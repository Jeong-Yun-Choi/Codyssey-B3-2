def validate_commit(text):
    # 커밋 초안의 제목이 존재하고 길이 제한에 맞는지 검사합니다.
    lines = text.strip().splitlines()  # 앞뒤 빈 공간을 제거하고 줄로 나눔
    if not lines:
        return ["커밋 제목이 없습니다."]

    title = lines[0].strip()
    errors = []

    if not title:
        errors.append("커밋 제목이 없습니다.")
    if len(title) > 72:
        errors.append("커밋 제목이 72자를 초과했습니다.")

    return errors

# PR 제목과 필수 섹션 및 불릿을 검사합니다.
def validate_pr(text):
    lines = text.strip().splitlines()
    errors = []

    if not lines:
        return ["PR 초안이 비어 있습니다."]

    title = lines[0].strip()
    if title in ("## Why", "## What", "## How to Test") or not title.lstrip("# ").strip():
        errors.append("PR 제목이 없습니다.")
    if len(title) > 80:
        errors.append("PR 제목이 80자를 초과했습니다.")

    required_sections = ["## Why", "## What", "## How to Test"]

    for section in required_sections:
        if section not in lines:
            errors.append(f"{section} 섹션이 없습니다.")

    for section in required_sections:
        if section in lines:
            start = lines.index(section) + 1
            next_sections = [
                lines.index(other)
                for other in required_sections
                if other in lines and lines.index(other) > start
            ]
            end = min(next_sections) if next_sections else len(lines)

            bullets = [
                line for line in lines[start:end]
                if line.lstrip().startswith("- ") and line.lstrip()[2:].strip()
            ]

            if not bullets:
                errors.append(f"{section} 섹션에 불릿이 없습니다.")

    return errors


def postprocess_draft(text, draft_type):
    # AI 초안의 불필요한 머리말과 코드 블록을 제거합니다.
    cleaned_lines = []
    preambles = {
        "커밋 메시지",
        "# 커밋 메시지",
        "PR 초안",
        "# PR 초안",
    }

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            continue
        if not cleaned_lines and stripped in preambles:
            continue
        cleaned_lines.append(line.rstrip())

    cleaned_text = "\n".join(cleaned_lines).strip()

    if draft_type == "commit":
        for line in cleaned_text.splitlines():
            title = line.strip()
            if title:
                if title.startswith("# "):
                    title = title[2:].strip()
                return title
        return ""

    return cleaned_text
