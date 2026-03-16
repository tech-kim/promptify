from openai import OpenAI
import os
import json

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

MODELS = [
    "openrouter/auto",
    "meta-llama/llama-4-maverick:free",
    "meta-llama/llama-4-scout:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
    "mistralai/mistral-7b-instruct:free",
]

def chat(text: str) -> str:
    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": text}]
            )
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower() or "404" in str(e):
                continue
            raise e
    raise Exception("모든 모델이 rate limit에 걸렸습니다. 잠시 후 다시 시도해주세요.")


def extract_song_attributes(title: str, artist: str) -> dict:
    prompt = f"""
다음 곡의 정보를 JSON으로만 답하세요. 다른 텍스트 없이 JSON만 출력하세요.

곡: {title}
아티스트: {artist}

출력 형식:
{{
  "duration": "3:45",
  "timbre": "warm synth pad, bright pluck, punchy kick"
}}

duration은 실제 곡 길이를 mm:ss 형식으로,
timbre는 이 곡의 대표 음색/파형을 영어로 3가지 이내로 작성하세요.
"""
    try:
        raw = chat(prompt)
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        return {
            "duration": data.get("duration", ""),
            "timbre": data.get("timbre", "")
        }
    except:
        return {"duration": "", "timbre": ""}


def generate_analysis(song_info: dict) -> dict:
    title = song_info.get("title", "Unknown")
    artist = song_info.get("artist", "Unknown")
    bpm = song_info.get("bpm", "알 수 없음")
    key = song_info.get("key", "알 수 없음")
    energy = song_info.get("energy_label", "알 수 없음")
    genre = song_info.get("genre_guess", "알 수 없음")

    # 곡 길이 & 음색 추론
    attrs = extract_song_attributes(title, artist)
    duration = attrs.get("duration", "")
    timbre = attrs.get("timbre", "")

    prompt = f"""
당신은 전문 A&R 애널리스트입니다. 아래 곡을 분석해주세요.

곡 정보:
- 제목: {title}
- 아티스트: {artist}
- BPM: {bpm}
- 키: {key}
- 에너지: {energy}
- 장르 추정: {genre}

아래 형식으로 한국어 분석 리포트를 작성해주세요:

## 🎵 장르 히스토리
(이 장르의 역사와 이 곡의 위치)

## 🔥 3가지 핵심 매력 포인트
1. 
2. 
3. 

## 💫 이 곡만의 특별함
(이 곡만의 독특한 요소)

## 🎯 시장 포지셔닝 전략
(타겟 청중과 시장 전략)

## 📈 상업적 잠재력 및 마케팅 포인트
(상업적 가능성 분석)

## 🎛️ Suno AI 프롬프트
아래 규칙을 반드시 지켜서 Suno AI 프롬프트를 영어로 작성하세요:
- 코드블록(```) 없이 순수 텍스트 한 단락만 작성
- 반드시 950자(영문 공백 포함) 이내로 작성
- 아티스트 이름, 곡 제목, 앨범명을 절대 포함하지 말 것
- Hook-in-5 → Emotional overview → Instrumentation → Harmony → Vocal → Structure → Mix → Avoid 순서로 작성
- 특정 아티스트나 멜로디를 직접 복사하지 말고 영향을 묘사로만 표현할 것
"""

    report = chat(prompt)

    suno_prompt = ""
    if "🎛️ Suno AI 프롬프트" in report:
        raw = report.split("🎛️ Suno AI 프롬프트")[-1].strip()
        raw = raw.replace("```english", "").replace("```", "").strip()

        if len(raw) > 950:
            truncated = raw[:950]
            last_period = truncated.rfind(".")
            if last_period > 0:
                raw = truncated[:last_period + 1]
            else:
                raw = truncated

        words_to_remove = [title, artist]
        for word in words_to_remove:
            if word and word.lower() != "unknown":
                raw = raw.replace(word, "").replace(word.lower(), "")

        prefix = ""
        if duration:
            prefix += f"[Duration: {duration}] "
        if timbre:
            prefix += f"[Timbre: {timbre}] "

        suno_prompt = (prefix + raw).strip()

    return {
        "report": report,
        "suno_prompt": suno_prompt
    }