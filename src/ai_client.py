import os
import requests


# 교육기관 API에서 사용할 가상 키를 환경변수에서 가져옵니다.
def get_api_key():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
    return api_key


# 교육기관의 Claude 호환 API를 호출하고 응답 텍스트를 반환합니다.
def generate_text(prompt, model, temperature, max_tokens):
    response = requests.post(
        "https://copa.codyssey.kr/v1/messages",
        headers={
            "x-api-key": get_api_key(),
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    texts = [item.get("text", "") for item in data.get("content", []) if item.get("type") == "text"]
    text = "\n".join(texts).strip()
    if not text:
        raise RuntimeError("Claude가 텍스트 응답을 반환하지 않았습니다.")

    usage = data.get("usage")
    if isinstance(usage, dict):
        print(f"토큰 사용량: 입력 {usage.get('input_tokens', '?')}, 출력 {usage.get('output_tokens', '?')}")
    else:
        print("토큰 사용량: 응답에 사용량 정보가 없습니다.")
    if data.get("stop_reason") == "max_tokens":
        raise RuntimeError("출력 토큰 한도에 도달해 초안이 잘렸을 수 있습니다. --max-tokens 값을 조정해 다시 실행하세요.")
    return text
