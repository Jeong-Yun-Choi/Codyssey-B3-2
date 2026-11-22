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
- 프로그램은 초안만 출력하며 커밋이나 PR을 자동으로 생성하지 않습니다.

## 검증 현황

- 실제 API로 커밋과 PR 초안을 생성했고, PR의 제목과 Why·What·How to Test 섹션을 확인했습니다.
- 커밋 제목의 72자 경계, PR 제목의 80자 경계와 필수 섹션·불릿 누락을 확인했습니다.
- 가짜 민감정보로 안전 모드의 이메일·일부 키 마스킹을 확인했고, 키 누락·연결 오류·변경사항 없음과 Git 저장소 오류를 시험했습니다.
- 모델·temperature·max-tokens가 요청에 전달되는 것을 확인했습니다. 모델에 따른 실제 출력 차이는 별도 확인이 필요합니다.
- 새 파일 본문의 전체 길이는 실제로 포함한 글자 수로 누적하며, 파일당 1,200자와 전체 6,000자를 제한합니다.

## 선택 기능: B3-1 문서 컨벤션과 안전 모드

B3-1 저장소의 최근 문서 커밋은 `docs: README 디렉터리 구조 추가`처럼 `docs:` 접두사와 한국어 변경 설명을 사용합니다. 문서 변경에 이 스타일을 요청하려면 다음 옵션을 추가합니다. 일반 변경에는 적용하지 마세요.

```bash
python3 src/main.py commit --safe-mode --convention b3-1-docs
```

컨벤션 옵션을 사용하지 않으면 기본 커밋 형식을 요청하고, 사용하면 `docs:` 접두사와 한국어 설명을 추가로 요청합니다. 이는 AI에 전달하는 지시이며 모델이 항상 따르는 것은 아니므로 결과를 확인해야 합니다.

안전 모드에서는 이메일과 일부 키·토큰 패턴을 가립니다. 선택적으로 각 diff에 전송할 줄 수를 지정할 수 있습니다.

```bash
python3 src/main.py pr --safe-mode --safe-max-diff-lines 200
```

위 설정은 스테이징 전 diff와 스테이징된 diff **각각** 최대 200줄을 전송하고, 생략된 경우 표시를 추가합니다. 이 제한은 파일 경로, 새 파일 본문이나 전체 요청 크기의 상한이 아닙니다. `--safe-max-diff-lines`는 `--safe-mode`와 함께 사용하고 1 이상의 정수를 입력합니다. 줄 수 옵션이 없으면 diff 줄 수를 제한하지 않습니다.

가짜 데이터로 확인한 예: 안전 모드가 꺼지면 `dev@example.com`이 전달 대상에 남고, 켜지면 `[이메일 가림]`으로 바뀝니다. 두 diff에 각각 1줄 제한을 적용하면 첫 줄만 남고 `[나머지 diff 생략]`이 붙습니다. AI 요청 없이 검증하려면 프로젝트 루트에서 다음을 실행합니다.

```bash
python3 -m unittest discover -s tests -v
```

실제 AI 생성 결과의 컨벤션 적용 전후 비교는 아직 수행하지 않았습니다.
