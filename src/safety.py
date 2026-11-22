import re

# 텍스트에서 이메일과 일부 비밀값 표기를 찾아 가립니다.
def mask_sensitive_text(text):
    email_pattern = r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}"
    secret_pattern = r"""(?i)(\b(?:api[_-]?key|token|secret)\s*[:=]\s*["']?)([^\s"',;]+)"""

    text = re.sub(email_pattern, "[이메일 가림]", text)
    return re.sub(secret_pattern, r"\1[비밀값 가림]", text)

# 수집한 Git 정보의 텍스트를 가린 새 딕셔너리를 만듭니다.
def mask_git_info(git_info, max_diff_lines=None):
    masked = git_info.copy()  # 원본 딕셔너리 유지

    for key in ("status", "diff", "staged_diff"):
        masked[key] = mask_sensitive_text(git_info[key])

    if max_diff_lines is not None:
        if max_diff_lines < 1:
            raise ValueError("diff 줄 제한은 1 이상이어야 합니다.")
        for key in ("diff", "staged_diff"):
            lines = masked[key].splitlines(keepends=True)
            if len(lines) > max_diff_lines:
                masked[key] = "".join(lines[:max_diff_lines]).rstrip("\n") + "\n[나머지 diff 생략]"

    masked["untracked_files"] = {
        path: mask_sensitive_text(content)
        for path, content in git_info["untracked_files"].items()
    }
    return masked
