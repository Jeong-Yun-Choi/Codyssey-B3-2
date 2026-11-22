import subprocess
from pathlib import Path

MAX_UNTRACKED_FILE_BYTES = 100_000   # 새 파일 하나의 최대 크기
MAX_UNTRACKED_TOTAL_BYTES = 500_000  # 새 파일 내용 전체의 최대 크기

# 전달받은 Git 명령을 실행하고 출력 결과를 가져옵니다.
def run_git_command(command):
    try:
        result = subprocess.run(
            command,              # 실행할 Git 명령 리스트
            capture_output=True,  # 출력과 오류 보관
            text=True,            # 결과를 문자열로 받기
        )
    except FileNotFoundError as error:
        raise RuntimeError("Git 실행 파일을 찾을 수 없습니다.") from error

    if result.returncode != 0:  # 명령이 실패했는지 확인
        raise RuntimeError(f"Git 명령 실행 실패: {result.stderr.strip()}")
    return result.stdout      # 일반 출력을 호출한 곳에 반환

# Git 상태 출력에서 추적되지 않는 새 파일의 경로를 골라냅니다.
def get_untracked_paths(status_output):
    entries = status_output.split("\0")  # NUL을 기준으로 항목 분리
    paths = []                           # 새 파일 경로를 담을 리스트
    index = 0                            # 현재 확인할 항목의 위치

    while index < len(entries):          # 마지막 항목까지 확인
        entry = entries[index]
        if not entry:                    # 마지막 빈 항목이면 종료
            break

        status = entry[:2]               # 앞의 두 글자가 Git 상태
        if status == "??":
            paths.append(entry[3:])      # 새 파일이면 경로 저장

        if "R" in status or "C" in status:
            index += 1                   # 이름 변경·복사의 추가 경로 건너뛰기

        index += 1                       # 다음 상태 항목으로 이동

    return paths                         # 새 파일 경로 리스트 반환

# 파일을 읽고 한도를 초과하면 오류를 알립니다.
def read_limited_file_bytes(file_path):
    path = Path(file_path)
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError("심볼릭 링크가 포함된 경로는 수집할 수 없습니다.")
    
    with open(file_path, "rb") as file:
        content = file.read(MAX_UNTRACKED_FILE_BYTES + 1)

    if len(content) > MAX_UNTRACKED_FILE_BYTES:
        raise ValueError("파일이 크기 한도를 초과했습니다.")

    return content

# 파일 바이트를 UTF-8 텍스트로 변환하고 형식을 확인합니다.
def decode_untracked_text(content):
    if b"\0" in content:
        raise ValueError("NUL 문자가 포함된 파일은 수집할 수 없습니다.")

    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("UTF-8 텍스트로 읽을 수 없는 파일입니다.") from error

# 저장소 기준으로 사용할 수 있는 상대 경로인지 확인합니다.
def validate_untracked_path(file_path):
    path = Path(file_path)

    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError("저장소 기준의 파일 경로가 아닙니다.")

    return path

# 새 파일의 경로를 검사하고 파일 내용을 텍스트로 가져옵니다.
def read_untracked_file(file_path):
    path = validate_untracked_path(file_path)  # 저장소 기준 상대 경로 검사
    content = read_limited_file_bytes(path)    # 링크와 파일별 크기를 확인하며 읽기
    return decode_untracked_text(content)      # UTF-8 텍스트로 변환해 반환

# 새 파일의 전체 크기를 제한하고 수집 결과와 제외 이유를 반환합니다.
def collect_untracked_files(paths):
    files = {}        # 수집한 파일 경로와 텍스트
    skipped = {}      # 제외한 파일 경로와 이유
    total_bytes = 0   # 지금까지 수집한 파일의 바이트 합계

    for file_path in paths:
        try:
            content = read_untracked_file(file_path)
            file_bytes = len(content.encode("utf-8"))  # UTF-8 기준 바이트 수

            if total_bytes + file_bytes > MAX_UNTRACKED_TOTAL_BYTES:
                skipped[file_path] = "새 파일 전체 크기 한도를 초과했습니다."
                continue  # 이 파일을 제외하고 다음 파일 검사

            files[file_path] = content
            total_bytes += file_bytes  # 수집한 파일의 크기만 합산
        except (ValueError, OSError) as error:
            skipped[file_path] = str(error)

    return files, skipped

# Git 상태와 변경 내용, 새 파일 수집 결과를 한데 모읍니다.
def collect_git_info():
    status = run_git_command(["git", "status", "--short"])
    diff = run_git_command(["git", "diff"])
    staged_diff = run_git_command(["git", "diff", "--staged"])

    # 새 파일 경로를 정확히 구분할 수 있는 Git 상태를 가져옵니다.
    raw_status = run_git_command(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"]
    )
    paths = get_untracked_paths(raw_status)
    files, skipped = collect_untracked_files(paths)

    return {
        "status": status,              # 파일 상태
        "diff": diff,                  # 스테이징 전 변경 내용
        "staged_diff": staged_diff,    # 스테이징된 변경 내용
        "untracked_files": files,      # 새 파일 경로와 텍스트
        "skipped_files": skipped,      # 제외한 파일 경로와 이유
    }