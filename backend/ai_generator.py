import os
import json
import re
import google.generativeai as genai

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def chat(text: str) -> str:
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(
                text,
                generation_config=genai.GenerationConfig(
                    temperature=0,
                )
            )
            return response.text
        except Exception as e:
            print(f"Gemini 실패: {e}")

    from openai import OpenAI
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    MODELS = [
        "openrouter/auto",
        "meta-llama/llama-4-maverick:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "google/gemma-3-27b-it:free",
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


def get_tempo_override(tempo_user: str) -> dict:
    TEMPO_MAP = {
        "slow":      {"energy": "low",      "bpm": "70",  "feel": "slow, gentle, ballad-like"},
        "medium":    {"energy": "medium",    "bpm": "100", "feel": "moderate, mid-tempo, flowing"},
        "fast":      {"energy": "high",      "bpm": "130", "feel": "fast, energetic, driving"},
        "very_fast": {"energy": "very high", "bpm": "165", "feel": "very fast, intense, explosive"},
    }
    return TEMPO_MAP.get(tempo_user, {})


def analyze_song(title: str, artist: str, genre: str, tempo_override: dict, key_user: str, mood_user: str) -> dict:
    """곡의 음악적 속성을 깊이 있게 분석"""

    # 사용자 입력값 override 지시문 생성
    user_overrides = []
    if tempo_override:
        user_overrides.append(f"- BPM: approximately {tempo_override['bpm']} ({tempo_override['feel']})")
        user_overrides.append(f"- Energy: {tempo_override['energy']}")
    if key_user:
        user_overrides.append(f"- Key/Tonality: {key_user}")
    if mood_user:
        user_overrides.append(f"- Mood/Atmosphere: {mood_user}")

    override_block = ""
    if user_overrides:
        override_block = "CRITICAL USER OVERRIDES - use these values exactly, do not infer:\n" + "\n".join(user_overrides)

    prompt = f"""You are a professional music producer and analyst with deep knowledge of K-pop and global music.
Analyze this specific song in depth and return ONLY a JSON object.

Song: "{title}" by {artist}
Genre hint: {genre if genre else "unknown"}
{override_block}

Return exactly this JSON:
{{
  "duration": "3:45",
  "bpm": "120",
  "key": "G Minor",
  "energy": "high",
  "mood": "fierce, confident, dark",
  "genre_lineage": "K-Pop, Trap EDM, Dark Electropop",
  "chord_progression": "i-VI-III-VII (Gm-Eb-Bb-F)",
  "key_instruments": "aggressive synth bass, electronic drums, sharp synth leads, vocal chops",
  "timbre": "punchy, sharp, modern digital, subtle distortion",
  "vocal_style": "powerful female vocals, tight harmonies, aggressive delivery",
  "arrangement": "explosive chorus, tension-building pre-chorus, dynamic verse",
  "mix_character": "dense, layered, forward vocals, wide stereo, prominent kick and snare",
  "sonic_signature": "the most distinctive single sound element of THIS song",
  "avoid": "acoustic instruments, jazz harmony, breathy falsetto, lo-fi textures"
}}

Rules:
- Be SPECIFIC to this exact song
- If user overrides are provided, use them as absolute truth
- sonic_signature: the ONE most distinctive musical characteristic of THIS song
- avoid: what would ruin this song's character in AI generation
"""
    try:
        raw = chat(prompt)
        raw = raw.replace("```json", "").replace("```", "").strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]
        return json.loads(raw)
    except:
        return {}


def generate_all_outputs(title: str, artist: str, attrs: dict) -> dict:
    """4개 섹션 동시 생성"""

    prompt = f"""You are a Suno AI prompt architect and professional music producer.
Based on the deep musical analysis below, generate 4 outputs for Suno AI.

Song: "{title}" by {artist}
Musical Analysis:
- BPM: {attrs.get('bpm', '?')}
- Key: {attrs.get('key', '?')}
- Energy: {attrs.get('energy', '?')}
- Mood: {attrs.get('mood', '?')}
- Genre lineage: {attrs.get('genre_lineage', '?')}
- Chord progression: {attrs.get('chord_progression', '?')}
- Key instruments: {attrs.get('key_instruments', '?')}
- Timbre: {attrs.get('timbre', '?')}
- Vocal style: {attrs.get('vocal_style', '?')}
- Arrangement: {attrs.get('arrangement', '?')}
- Mix character: {attrs.get('mix_character', '?')}
- Sonic signature: {attrs.get('sonic_signature', '?')}
- Avoid: {attrs.get('avoid', '?')}
- Duration: {attrs.get('duration', '?')}

Generate ALL 4 outputs below. Use ONLY English. Never mention artist name or song title.

---OUTPUT 1: SUNO OPTIMIZED PROMPT---
Write a single flowing paragraph (max 900 characters).
This goes into Suno's "Style of Music" box.
Structure: Opening sonic hook (first 5 seconds) → overall mood → chord/harmony → key instruments → vocal style → arrangement arc → mix texture → what to avoid.
Make it read like a professional producer briefing. Dense with musical information.
Every sentence must be complete. No truncation.

---OUTPUT 2: STYLE KEYWORDS---
Max 120 characters. Comma-separated keywords only.
Priority order: genre, sub-genre, key instruments, mood, tempo, production style, vocal type.
Example format: K-Pop, Trap EDM, aggressive synth bass, dark, 165 BPM, powerful female vocals

---OUTPUT 3: SONG STRUCTURE---
Generate song structure using ONLY bracket tags for Suno's lyrics box.

CRITICAL RULES:
- Every single piece of text MUST be inside brackets [ ]
- Text outside brackets = Suno will SING it as lyrics
- Section tag on its own line: [Intro], [Verse 1], [Pre-Chorus], [Chorus], [Bridge], [Outro]
- Instrument/mood on next line in own brackets: [sharp synths, no vocals]
- Energy changes in own brackets: [full drop, all instruments]
- Max 6 words inside each descriptor bracket

Example format:
[Intro]
[dark synth build, no vocals]

[Verse 1]
[minimal beat, driving bass]

[Pre-Chorus]
[synth build-up, rising energy]

[Chorus]
[massive drop, all instruments, powerful vocals]

[Bridge]
[rhythmic shift, stripped back]

[Outro]
[driving synths fade out]

Follow this exact format. Base sections on the arrangement analysis.

---OUTPUT 4: PRO TIPS---
3-5 bullet points. Each tip should be specific to THIS song's sonic character.
Focus on: key Suno trigger words, how to achieve the sonic signature, common mistakes to avoid.
"""

    raw = chat(prompt)

    result = {
        "suno_prompt": "",
        "style_keywords": "",
        "song_structure": "",
        "pro_tips": ""
    }

    sections = {
        "suno_prompt": "OUTPUT 1: SUNO OPTIMIZED PROMPT",
        "style_keywords": "OUTPUT 2: STYLE KEYWORDS",
        "song_structure": "OUTPUT 3: SONG STRUCTURE",
        "pro_tips": "OUTPUT 4: PRO TIPS"
    }

    for key, marker in sections.items():
        if marker in raw:
            start = raw.find(marker) + len(marker)
            next_markers = [m for m in sections.values() if m != marker and m in raw]
            end = len(raw)
            for nm in next_markers:
                pos = raw.find(nm, start)
                if pos > start:
                    end = min(end, pos)
            content = raw[start:end].strip()
            content = content.replace("---", "").strip()
            result[key] = content

    # suno_prompt 글자수 보장
    if len(result["suno_prompt"]) > 950:
        sentences = re.split(r'(?<=[.!?])\s+', result["suno_prompt"])
        trimmed = ""
        for s in sentences:
            if len(trimmed) + len(s) + 1 <= 950:
                trimmed += ("" if not trimmed else " ") + s
            else:
                break
        result["suno_prompt"] = trimmed

    # 아티스트명/곡명 필터링
    for word in [title, artist]:
        if word and word.lower() != "unknown":
            for key in result:
                result[key] = result[key].replace(word, "").replace(word.lower(), "")

    return result


def generate_report(title: str, artist: str, genre: str, attrs: dict) -> str:
    """프로듀서 시점 한국어 리포트"""
    prompt = f"""당신은 전문 A&R 애널리스트이자 음악 프로듀서입니다.
아래 곡을 프로듀서 시점에서 깊이 있게 분석해주세요.

곡 정보:
- 제목: {title}
- 아티스트: {artist}
- 장르: {genre if genre else "알 수 없음"}
- BPM: {attrs.get('bpm', '?')}
- 조성: {attrs.get('key', '?')}
- 화성 진행: {attrs.get('chord_progression', '?')}
- 핵심 악기: {attrs.get('key_instruments', '?')}
- 음색: {attrs.get('timbre', '?')}
- 편곡 구조: {attrs.get('arrangement', '?')}
- 무드: {attrs.get('mood', '?')}

아래 형식으로 한국어 리포트를 작성하세요:

## 🎵 장르 계보
(이 곡의 장르적 뿌리와 영향받은 아티스트/시대를 구체적으로)

## 🎹 화성 & 사운드 분석
(코드 진행, 조성, 핵심 악기의 톤과 역할을 프로듀서 시점에서 구체적으로)

## 🎚️ 편곡 & 믹스 특성
(곡의 구조적 흐름, 악기 배치, 믹싱 특성을 구체적으로)

## ⚡ 이 곡의 소닉 시그니처
(다른 곡과 절대적으로 구별되는 핵심 사운드 요소 한 가지를 구체적으로)

## 💡 AI 재현 핵심 포인트
(Suno로 이 곡과 유사한 결과를 얻기 위한 실용적 팁 3가지)"""

    return chat(prompt)


def generate_analysis(song_info: dict) -> dict:
    title = song_info.get("title", "Unknown")
    artist = song_info.get("artist", "Unknown")
    genre = song_info.get("genre_guess", "")
    tempo_user = song_info.get("tempo_user", "")
    key_user = song_info.get("key_user", "")
    mood_user = song_info.get("mood_user", "")

    # 1. 템포 오버라이드
    tempo_override = get_tempo_override(tempo_user)

    # 2. 곡 속성 분석 (사용자 입력값 우선 반영)
    attrs = analyze_song(title, artist, genre, tempo_override, key_user, mood_user)

    # 템포 강제 반영
    if tempo_override:
        attrs["energy"] = tempo_override["energy"]
        attrs["bpm"] = tempo_override["bpm"]

    # 조성/무드 강제 반영
    if key_user:
        attrs["key"] = key_user
    if mood_user:
        attrs["mood"] = mood_user

    # 3. 리포트 + Suno 4개 출력 생성
    report = generate_report(title, artist, genre, attrs)
    outputs = generate_all_outputs(title, artist, attrs)

    return {
        "report": report,
        "suno_prompt": outputs.get("suno_prompt", ""),
        "style_keywords": outputs.get("style_keywords", ""),
        "song_structure": outputs.get("song_structure", ""),
        "pro_tips": outputs.get("pro_tips", ""),
    }