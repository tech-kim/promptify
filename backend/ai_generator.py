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
아래 규칙을 반드시 지켜서 Suno AI 프롬프트를 영어로 작성하세요:

규칙:
- 코드블록(```) 없이 순수 텍스트 한 단락만 작성
- 반드시 950자(영문 공백 포함) 이내로 작성
- 작성 후 Python으로 len()을 사용해 글자 수를 확인하고 950자 초과 시 줄일 것
- 글자 수 확인 코드와 결과는 출력하지 말 것, 최종 프롬프트 텍스트만 출력

구조 순서 (단락 안에서 이 순서로):
1. Hook-in-5: 첫 5초 안에 귀를 사로잡는 구체적인 음악적 순간 묘사 (오프닝 리프, 비트 드롭, 보컬 브레스 등)
2. Emotional overview: 전체적인 감성과 무드
3. Instrumentation: 악기 구성
4. Harmony: 화성 방향
5. Vocal: 보컬 스타일
6. Structure: 곡 구성
7. Mix: 믹스 질감
8. Avoid: 피해야 할 요소

특정 아티스트나 멜로디를 직접 복사하지 말고 영향을 묘사로만 표현할 것
아티스트 이름, 곡 제목, 앨범명을 프롬프트 안에 절대 포함하지 말 것
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
        raw = report.split("🎛️ Suno AI 프롬프트")[-1].strip()
        raw = raw.replace("```english", "").replace("```", "").strip()
        # 950자 초과 시 마지막 문장 단위로 자르기
        if len(raw) > 950:
            truncated = raw[:950]
            last_period = truncated.rfind(".")
            if last_period > 0:
                raw = truncated[:last_period + 1]
            else:
                raw = truncated
        # 아티스트명, 곡명 직접 언급 필터링
        words_to_remove = [title, artist]
        for word in words_to_remove:
            if word and word.lower() != "unknown":
                raw = raw.replace(word, "").replace(word.lower(), "")
        suno_prompt = raw.strip()

    return {
        "report": report,
        "suno_prompt": suno_prompt
    }