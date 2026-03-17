import os
import json
import re
import google.generativeai as genai

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Gemini 설정
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def chat(text: str) -> str:
    """Gemini 우선, 실패시 OpenRouter fallback"""
    # 1. Gemini 시도
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(text)
            return response.text
        except Exception as e:
            print(f"Gemini 실패: {e}")

    # 2. OpenRouter fallback
    from openai import OpenAI
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
    prompt = f"""You are a music expert with deep knowledge of Korean and international pop music.
Analyze this specific song and return ONLY a JSON object.

Song: "{title}" by {artist}
Genre hint: {genre if genre else "unknown"}

Return exactly this JSON format:
{{
  "duration": "3:45",
  "timbre": "soft piano, warm synth pads, gentle acoustic guitar",
  "tempo_feel": "slow and melancholic",
  "energy_level": "low",
  "mood": "bittersweet, nostalgic, emotional",
  "key_instruments": "piano, synth pad, light percussion",
  "vocal_style": "soft female vocals, emotional delivery, harmonized chorus",
  "tempo_bpm": "75"
}}

Definitions:
- duration: ACTUAL real length of this specific song in mm:ss
- timbre: 3 most distinctive sound textures specific to THIS song
- tempo_feel: 3-4 words describing the rhythmic energy
- energy_level: must be one of: "very low" / "low" / "medium" / "high" / "very high"
- mood: 3 emotional adjectives specific to THIS song
- key_instruments: 3-4 most prominent instruments in THIS song
- vocal_style: vocal characteristics specific to this song
- tempo_bpm: estimated BPM as a number string

Be SPECIFIC to this exact song. Do not generalize by genre.
If this is a ballad, say ballad. If it's slow, say slow. Do not over-energize.
"""
    try:
        raw = chat(prompt)
        raw = raw.replace("```json", "").replace("```", "").strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]
        data = json.loads(raw)
        return {
            "duration": data.get("duration", ""),
            "timbre": data.get("timbre", ""),
            "tempo_feel": data.get("tempo_feel", ""),
            "energy_level": data.get("energy_level", "medium"),
            "mood": data.get("mood", ""),
            "key_instruments": data.get("key_instruments", ""),
            "vocal_style": data.get("vocal_style", ""),
            "tempo_bpm": data.get("tempo_bpm", "")
        }
    except:
        return {
            "duration": "", "timbre": "", "tempo_feel": "",
            "energy_level": "medium", "mood": "",
            "key_instruments": "", "vocal_style": "", "tempo_bpm": ""
        }


def trim_to_limit(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = ""
    for sentence in sentences:
        if len(result) + len(sentence) + 1 <= limit:
            result += ("" if not result else " ") + sentence
        else:
            break
    if not result:
        words = text[:limit].split(" ")
        result = " ".join(words[:-1])
    return result.strip()


def generate_suno_prompt(title: str, artist: str, attrs: dict) -> str:
    timbre = attrs.get("timbre", "")
    key_instruments = attrs.get("key_instruments", "")
    tempo_feel = attrs.get("tempo_feel", "")
    energy_level = attrs.get("energy_level", "medium")
    mood = attrs.get("mood", "")
    vocal_style = attrs.get("vocal_style", "")
    tempo_bpm = attrs.get("tempo_bpm", "")
    duration = attrs.get("duration", "")

    dur_text = ""
    if duration:
        parts = duration.split(":")
        if len(parts) == 2:
            dur_text = f"a {parts[0]} minute {parts[1]} second track"

    prompt = f"""Write a Suno AI music generation prompt based on these EXACT song attributes.
You must faithfully reflect the energy and mood - do not make it more energetic than specified.

Song attributes:
- Energy level: {energy_level} (CRITICAL: reflect this accurately)
- Mood: {mood}
- Tempo feel: {tempo_feel}
- Estimated BPM: {tempo_bpm}
- Timbre: {timbre}
- Key instruments: {key_instruments}
- Vocal style: {vocal_style}
- Length: {dur_text}

Strict rules:
1. Write ONE complete paragraph only
2. Maximum 700 characters including spaces
3. Never mention any artist name or song title
4. Start with a COMPLETE sentence describing the opening 5 seconds
5. Follow this exact order: opening hook → overall mood → instruments → harmony → vocals → structure → mix → what to avoid
6. Energy level "{energy_level}" must be clearly reflected throughout
7. If energy is low/very low: use words like gentle, soft, subtle, delicate
8. If energy is high/very high: use words like driving, powerful, explosive, intense
9. No tags or brackets - natural flowing prose only
10. Every sentence must be grammatically complete

Output the prompt text only. Nothing else."""

    raw = chat(prompt)
    raw = raw.strip().replace("```", "")
    raw = trim_to_limit(raw, 700)

    for word in [title, artist]:
        if word and word.lower() != "unknown":
            raw = raw.replace(word, "").replace(word.lower(), "")

    return raw.strip()


def generate_analysis(song_info: dict) -> dict:
    title = song_info.get("title", "Unknown")
    artist = song_info.get("artist", "Unknown")
    genre = song_info.get("genre_guess", "")

    # 1. 곡 속성 추론
    attrs = extract_song_attributes(title, artist, genre)

    # 2. 리포트 생성
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
(이 곡의 성공 요소를 AI 음악 제작에 활용하는 실용적 팁 2가지)"""

    report = chat(report_prompt)

    # 3. Suno 프롬프트 별도 생성
    suno_prompt = generate_suno_prompt(title, artist, attrs)

    return {
        "report": report,
        "suno_prompt": suno_prompt
    }