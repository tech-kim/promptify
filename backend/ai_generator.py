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


def extract_song_attributes(title: str, artist: str, genre: str) -> dict:
    prompt = f"""You are a music expert. Analyze this song and return ONLY a JSON object with no explanation.

Song: "{title}" by {artist}
Genre hint: {genre if genre else "unknown"}

Return exactly this JSON format:
{{
  "duration": "3:45",
  "timbre": "distorted electric guitar, punchy 808 bass, crisp trap hi-hats",
  "tempo_feel": "aggressive and driving",
  "key_instruments": "trap drums, orchestral strings, brass stabs"
}}

Rules:
- duration: the ACTUAL real-world length of this specific song in mm:ss format
- timbre: 3 most distinctive sound textures of THIS specific song (not generic)
- tempo_feel: 2-3 words describing the rhythmic energy
- key_instruments: 3-4 most important instruments in THIS specific song
- Be specific to this song, not generic to the genre
"""
    try:
        raw = chat(prompt)
        raw = raw.replace("```json", "").replace("```", "").strip()
        # JSON 부분만 추출
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]
        data = json.loads(raw)
        return {
            "duration": data.get("duration", ""),
            "timbre": data.get("timbre", ""),
            "tempo_feel": data.get("tempo_feel", ""),
            "key_instruments": data.get("key_instruments", "")
        }
    except:
        return {"duration": "", "timbre": "", "tempo_feel": "", "key_instruments": ""}


def trim_to_limit(text: str, limit: int) -> str:
    """문장 단위로 limit 이하로 자르기"""
    if len(text) <= limit:
        return text
    # 마침표, 느낌표, 물음표 기준으로 문장 분리
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = ""
    for sentence in sentences:
        if len(result) + len(sentence) + 1 <= limit:
            result += ("" if not result else " ") + sentence
        else:
            break
    # 문장 분리 실패 시 단어 단위로 자르기
    if not result:
        words = text[:limit].split(" ")
        result = " ".join(words[:-1])
    return result.strip()


def generate_analysis(song_info: dict) -> dict:
    title = song_info.get("title", "Unknown")
    artist = song_info.get("artist", "Unknown")
    bpm = song_info.get("bpm", "알 수 없음")
    key = song_info.get("key", "알 수 없음")
    energy = song_info.get("energy_label", "알 수 없음")
    genre = song_info.get("genre_guess", "")

    # 곡 속성 추론
    attrs = extract_song_attributes(title, artist, genre)
    duration = attrs.get("duration", "")
    timbre = attrs.get("timbre", "")
    tempo_feel = attrs.get("tempo_feel", "")
    key_instruments = attrs.get("key_instruments", "")

    # 리포트 생성
    report_prompt = f"""당신은 전문 A&R 애널리스트입니다. 아래 곡을 분석해주세요.

곡 정보:
- 제목: {title}
- 아티스트: {artist}
- 장르 추정: {genre if genre else "알 수 없음"}

아래 형식으로 한국어 분석 리포트를 작성해주세요:

## 🎙️ 이 곡의 정체
(이 곡이 어떤 장르적 맥락에서 나왔는지, 한 문단으로 간결하게)

## ⚡ 왜 귀에 꽂히는가
(청자를 사로잡는 핵심 요소 3가지를 번호 없이, 각각 한 줄씩 핵심만)

## 🧬 이 곡의 DNA
(다른 곡과 구별되는 고유한 음악적 특성을 구체적으로)

## 👥 누가 이 곡을 찾는가
(타겟 청취자를 구체적인 상황과 감정으로 묘사)

## 💡 AI 작곡가를 위한 인사이트
(이 곡의 성공 요소를 AI 음악 제작에 활용하는 실용적 팁 2가지)

## 🎛️ Suno AI 프롬프트
아래 분석된 곡 속성을 반드시 반영하여 Suno AI 프롬프트를 영어로 작성하세요:

확인된 곡 속성:
- 실제 음색: {timbre if timbre else "분석 불가"}
- 핵심 악기: {key_instruments if key_instruments else "분석 불가"}
- 리듬 에너지: {tempo_feel if tempo_feel else "분석 불가"}

규칙:
- 코드블록(```) 없이 순수 텍스트 한 단락만 작성
- 반드시 900자(영문 공백 포함) 이내로 작성
- 아티스트 이름, 곡 제목, 앨범명을 절대 포함하지 말 것
- Hook-in-5 → Emotional overview → Instrumentation → Harmony → Vocal → Structure → Mix → Avoid 순서로 작성
- Hook-in-5는 반드시 완전한 문장으로 시작할 것
- 위에 제공된 실제 음색과 핵심 악기를 반드시 반영할 것
- 이 곡만의 장르적 독창성을 구체적으로 묘사할 것
- 특정 아티스트나 멜로디를 직접 복사하지 말고 영향을 묘사로만 표현할 것
"""

    report = chat(report_prompt)

    suno_prompt = ""
    if "🎛️ Suno AI 프롬프트" in report:
        raw = report.split("🎛️ Suno AI 프롬프트")[-1].strip()
        raw = raw.replace("```english", "").replace("```", "").strip()

        # 문장 단위로 900자 이내로 자르기
        raw = trim_to_limit(raw, 900)

        # 아티스트명, 곡명 필터링
        words_to_remove = [title, artist]
        for word in words_to_remove:
            if word and word.lower() != "unknown":
                raw = raw.replace(word, "").replace(word.lower(), "")

        # Duration, Timbre 강제 삽입
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