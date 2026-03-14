from openai import OpenAI
import os

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


def generate_analysis(song_info: dict) -> dict:
    title = song_info.get("title", "Unknown")
    artist = song_info.get("artist", "Unknown")
    bpm = song_info.get("bpm", "?")
    key = song_info.get("key", "?")
    energy = song_info.get("energy_label", "?")
    genre = song_info.get("genre_guess", "?")

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
(Suno AI로 비슷한 곡을 만들기 위한 영어 프롬프트. 장르, 분위기, 악기, 보컬 스타일 등을 포함)
"""

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    report = response.choices[0].message.content

    suno_prompt = ""
    if "🎛️ Suno AI 프롬프트" in report:
        suno_prompt = report.split("🎛️ Suno AI 프롬프트")[-1].strip()

    return {
        "report": report,
        "suno_prompt": suno_prompt
    }