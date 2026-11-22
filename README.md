# AI Git 초안 생성기

Git 저장소의 변경 사항을 수집해 커밋 메시지와 PR 설명 초안을 만드는 Python CLI입니다. 교육기관의 Anthropic 호환 API를 사용합니다.

## 설치 및 설정

Python 3.10 이상과 Git이 필요합니다. 이 저장소를 내려받은 후 프로젝트 루트에서 실행하세요.

```bash
git clone https://github.com/Jeong-Yun-Choi/Codyssey-B3-2.git
cd Codyssey-B3-2
python3 -m pip install requests
```

발급받은 교육기관 가상 키를 현재 터미널의 환경변수에 설정합니다.

```bash
export ANTHROPIC_API_KEY="발급받은_가상_키"
```

키를 소스코드나 저장소에 기록하지 마세요. 설치와 실행에는 같은 Python 환경을 사용합니다.

## 실행

Git 저장소의 프로젝트 루트에서 실행합니다.

```bash
# 커밋 메시지 생성
python3 src/main.py commit --safe-mode

# PR 초안 생성
python3 src/main.py pr --safe-mode
```

`--model`, `--temperature`, `--max-tokens`로 모델과 생성 설정을 변경할 수 있습니다. 기본값은 각각 `claude-sonnet-4`, `0.2`, `256`입니다.

```bash
python3 src/main.py pr --model claude-sonnet-4 --temperature 0.2 --max-tokens 256 --safe-mode
python3 src/main.py pr --help
```

## 출력 예시

```text
--- COMMIT 초안 ---
Git 초안 생성기 프로젝트 구조 및 문서 추가
```

```text
--- PR 초안 ---
# Git 변경사항 기반 AI 커밋 메시지 및 PR 초안 생성 CLI 완성

## Why
- Git 변경사항을 수동으로 정리하는 번거로움을 자동화합니다.

## What
- Python CLI가 Git diff와 새 파일을 수집해 AI로 커밋 메시지와 PR 초안을 생성합니다.

## How to Test
- 변경된 기능을 실행해 결과를 확인합니다.
```

## 사용 시 주의

- `--safe-mode`는 이메일과 일부 키·토큰 형태를 가립니다. 모든 민감정보를 탐지하지는 못하므로 전송할 변경 내용을 미리 확인하세요.
- 요청에는 Git 상태, diff와 수집된 새 파일의 일부가 포함됩니다. 입력과 출력 모두 토큰을 사용합니다.
- 출력 토큰 한도에 도달하면 문장이 잘릴 수 있습니다. 초안은 사용자가 검토하고 수정한 후 적용하세요.
- 현재 출력 검증과 후처리는 보완 중입니다. 프로그램은 초안만 출력하며 커밋이나 PR을 자동으로 생성하지 않습니다.
