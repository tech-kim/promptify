def analyze_song(title: str, artist: str, genre: str, tempo_override: dict) -> dict:
    """곡의 음악적 속성을 안정적으로 분석 (결정형 JSON)"""

    tempo_instruction = ""
    if tempo_override:
        tempo_instruction = f"""
CRITICAL OVERRIDE by user:
- BPM: approximately {tempo_override['bpm']}
- Energy: {tempo_override['energy']}
Use these values. Do NOT infer BPM or energy yourself.
"""

    prompt = f"""
You are a deterministic music analysis engine.

Return ONLY JSON. No explanation. No extra text.

Song: "{title}" by {artist}
Genre hint: {genre if genre else "unknown"}
{tempo_instruction}

JSON schema:
{{
  "bpm": 0,
  "key": "",
  "energy": "",
  "mood": [],
  "genre": "",
  "vocal_type": "",
  "structure": [],
  "instrument_main": []
}}

Allowed values:
- energy: low, medium, high
- mood: nostalgic, dark, bright, dreamy, emotional, aggressive
- genre: synthpop, rock, hiphop, edm, ballad, rnb, jazz, kpop, pop
- vocal_type: male, female, mixed, instrumental
- structure: intro, verse, chorus, bridge, outro
- instrument_main: synth, guitar, piano, bass, drums

Rules:
- Choose ONLY from allowed values
- mood must be 1~3 items
- structure must be ordered list
- instrument_main must be 2~4 items
- bpm must be an integer
- key must be like "C Major", "A minor"
"""

    try:
        raw = chat(prompt)

        # 코드블럭 제거
        raw = raw.replace("```json", "").replace("```", "").strip()

        # JSON 부분만 추출
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]

        data = json.loads(raw)

        # 최소 검증 + 보정
        if not isinstance(data.get("mood"), list):
            data["mood"] = ["emotional"]

        if not isinstance(data.get("structure"), list):
            data["structure"] = ["intro", "verse", "chorus", "bridge", "outro"]

        if not isinstance(data.get("instrument_main"), list):
            data["instrument_main"] = ["synth", "drums"]

        return data

    except Exception as e:
        print(f"analyze_song 실패: {e}")

        # fallback (절대 빈값 방지)
        return {
            "bpm": int(tempo_override.get("bpm", 100)) if tempo_override else 100,
            "key": "C Major",
            "energy": tempo_override.get("energy", "medium") if tempo_override else "medium",
            "mood": ["emotional"],
            "genre": genre if genre else "pop",
            "vocal_type": "mixed",
            "structure": ["intro", "verse", "chorus", "bridge", "outro"],
            "instrument_main": ["synth", "drums"]
        }
    def generate_analysis(song_info: dict) -> dict:
    title = song_info.get("title", "Unknown")
    artist = song_info.get("artist", "Unknown")
    genre = song_info.get("genre_guess", "")
    tempo_user = song_info.get("tempo_user", "")

    # 1. 템포 오버라이드
    tempo_override = get_tempo_override(tempo_user)

    # 2. 곡 분석
    attrs = analyze_song(title, artist, genre, tempo_override)

    # 템포 강제 반영
    if tempo_override:
        attrs["energy"] = tempo_override["energy"]
        attrs["bpm"] = tempo_override["bpm"]

    # 3. 출력 생성
    report = generate_report(title, artist, genre, attrs)
    outputs = generate_all_outputs(title, artist, attrs)

    return {
        "report": report,
        "suno_prompt": outputs.get("suno_prompt", ""),
        "style_keywords": outputs.get("style_keywords", ""),
        "song_structure": outputs.get("song_structure", ""),
        "pro_tips": outputs.get("pro_tips", ""),
    }
    