def build_prompt(git_info, draft_type, convention=None):
    # Git 수집 결과와 출력 규칙을 합쳐 AI 요청용 프롬프트를 만듭니다.
    if draft_type == "commit":
         rules = (
            "변경 내용을 바탕으로 커밋 제목 한 줄만 작성하세요. "
            "제목은 최대 72자이며 50자 이내를 권장합니다. "
            "제목 외 설명, 대안, 마크다운과 코드 블록은 출력하지 마세요."
        )
    elif draft_type == "pr":
        rules = (
            "PR 초안을 정확히 7줄로 작성하세요. "
            "제목은 80자 이내입니다. "
            "각 불릿은 15자 이내의 짧은 한 문장입니다. "
            "설명, 대안, 코드 블록, 빈 줄을 추가하지 마세요."
        )
    else:
        raise ValueError("초안 종류는 commit 또는 pr이어야 합니다.")

    if convention == "docs":
        rules += (
            " 문서 변경을 전제로 제목은 docs: 접두사로 시작하고 "
            "한국어로 변경 내용을 구체적으로 작성하세요."
        )
    elif convention is not None:
        raise ValueError("지원하지 않는 컨벤션입니다.")

    # 새 파일 본문을 제한해 프롬프트 입력 토큰을 줄입니다.
    max_file_chars = 1_200
    max_total_chars = 6_000
    new_file_parts = []
    total_chars = 0

    for path, content in git_info["untracked_files"].items():
        remaining_chars = max_total_chars - total_chars
        if remaining_chars <= 0:
            new_file_parts.append(f"파일: {path}\n[본문 생략: 전체 프롬프트 한도 초과]")
            continue

        limit = min(max_file_chars, remaining_chars)
        excerpt = content[:limit]
        if len(content) > limit:
            excerpt += "\n[본문 일부 생략]"
        new_file_parts.append(f"파일: {path}\n{excerpt}")
        total_chars += len(content[:limit])

    new_files = "\n\n".join(new_file_parts)

    # 초안 종류에 맞는 출력 형식을 선택합니다.
    if draft_type == "commit":
        output_format = (
            "[출력 형식 재확인]\n"
            "커밋 제목 한 줄\n"
        )
    else:
        output_format = (
            "[출력 형식 재확인]\n"
            "PR 제목 한 줄\n"
            "## Why\n"
            "- 변경 이유\n"
            "## What\n"
            "- 변경 내용\n"
            "## How to Test\n"
            "- 확인 방법\n"
        )

    # Git 정보와 선택한 출력 형식을 하나의 프롬프트로 반환합니다.
    return (
        f"{rules}\n"
        "제공된 내용에 근거하고, 확인하지 않은 테스트는 실행했다고 쓰지 마세요.\n\n"
        f"[Git 상태]\n{git_info['status']}\n"
        f"[스테이징 전 변경]\n{git_info['diff']}\n"
        f"[스테이징된 변경]\n{git_info['staged_diff']}\n"
        f"[새 파일 내용]\n{new_files}\n\n"
        f"{output_format}"
    )
