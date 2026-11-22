import argparse
from git_info import collect_git_info
from prompt_builder import build_prompt
from safety import mask_git_info, mask_sensitive_text
from ai_client import generate_text
from output import postprocess_draft, validate_commit, validate_pr


# 하위 명령과 AI 설정 옵션을 읽어 반환합니다.
def parse_arguments():
    parser = argparse.ArgumentParser(description="Git 변경사항 초안 생성기")
    commands = parser.add_subparsers(dest="command", required=True)

    for command in ("commit", "pr"):
        command_parser = commands.add_parser(command)
        command_parser.add_argument(
            "--model", default=None, metavar="모델명",
            help="사용할 AI 모델"
        )
        command_parser.add_argument(
            "--temperature", type=float, default=0.2, metavar="값",
            help="응답 다양성 설정 (기본값: 0.2)"
        )
        command_parser.add_argument(
            "--max-tokens", type=int, default=256, metavar="개수",
            help="최대 출력 토큰 수 (기본값: 256)"
        )
        command_parser.add_argument(
            "--safe-mode", action="store_true",
            help="민감정보 패턴 마스킹 사용"
        )
        command_parser.add_argument(
            "--safe-max-diff-lines", type=int, default=None, metavar="줄수",
            help="안전 모드에서 각 diff의 최대 전송 줄 수"
        )
        command_parser.add_argument(
            "--convention", choices=["b3-1-docs"], default=None,
            help="문서 변경용 B3-1 커밋 스타일 적용"
        )

    args = parser.parse_args()
    if args.safe_max_diff_lines is not None:
        if not args.safe_mode:
            parser.error("--safe-max-diff-lines에는 --safe-mode가 필요합니다.")
        if args.safe_max_diff_lines < 1:
            parser.error("--safe-max-diff-lines는 1 이상이어야 합니다.")
    return args

# Git 변경 내용을 수집하고 AI가 생성한 초안을 출력합니다.
def main():
    args = parse_arguments()

    try:
        git_info = collect_git_info()  # Git 상태와 변경 내용 수집
    except RuntimeError as error:
        print("오류:", error)
        return

    if not git_info["status"].strip():
        print("변경 사항이 없습니다.")
        return

    if not git_info["diff"].strip() and not git_info["staged_diff"].strip() and not git_info["untracked_files"]:
        print("수집 가능한 변경 내용이 없습니다.")
        if git_info["skipped_files"]:
            print("제외한 파일:", git_info["skipped_files"])
        return
    
    if args.safe_mode:
        git_info = mask_git_info(git_info, args.safe_max_diff_lines)  # 마스킹 및 선택적 diff 줄 제한

    prompt = build_prompt(git_info, args.command, args.convention)  # 초안 종류와 컨벤션 적용

    if args.safe_mode:
        prompt = mask_sensitive_text(prompt)  # 파일 경로 등에 남은 이메일 마스킹
    
    if git_info["skipped_files"]:
        print("제외한 파일:", git_info["skipped_files"])

    try:
        # 지정된 모델과 설정을 사용해 Claude 초안을 생성합니다.
        draft = generate_text(
            prompt, args.model or "claude-sonnet-4",
            args.temperature, args.max_tokens,
        )
    except Exception as error:
        print(f"AI 요청 오류 ({type(error).__name__}): {error}")
        return
    
    draft = postprocess_draft(draft, args.command)  # 불필요한 머리말과 코드 블록 제거

    # AI가 생성한 초안의 형식을 검사합니다.
    if args.command == "commit":
        validation_errors = validate_commit(draft)
    else:
        validation_errors = validate_pr(draft)
    if validation_errors:
        print("초안 형식 검증 오류:")
        for error in validation_errors:
            print("-", error)
        return
    
    print(f"--- {args.command.upper()} 초안 ---")
    print(draft)

if __name__ == "__main__":
    main()
