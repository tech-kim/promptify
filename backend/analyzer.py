import librosa
import numpy as np


def analyze_song(path: str) -> dict:
    """
    오디오 파일을 분석하여 음악적 특징을 추출합니다.
    Returns: { bpm, key, energy, energy_label, genre_guess }
    """
    try:
        y, sr = librosa.load(path, duration=120)  # 최대 2분만 분석 (속도)
    except Exception as e:
        raise RuntimeError(f"오디오 로드 실패: {e}")

    # BPM
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(np.atleast_1d(tempo)[0])
    if tempo > 160:
        tempo = tempo / 2
    bpm = round(tempo)

    # Key (chromagram)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    key = notes[int(chroma_mean.argmax())]

    # Energy (RMS)
    rms = librosa.feature.rms(y=y)
    energy = float(np.mean(rms))
    # 정규화 (대략적)
    energy_norm = min(energy * 20, 1.0)

    if energy_norm > 0.7:
        energy_label = "High Energy"
    elif energy_norm > 0.4:
        energy_label = "Medium Energy"
    else:
        energy_label = "Low Energy / Mellow"

    # Spectral centroid (음색 밝기)
    spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    brightness = float(np.mean(spec_cent))

    # 장르 추정 (rule-based 간단 버전)
    genre_guess = estimate_genre(bpm, energy_norm, brightness)

    return {
        "bpm": bpm,
        "key": key,
        "energy": round(energy_norm, 2),
        "energy_label": energy_label,
        "genre_guess": genre_guess,
        "brightness": round(brightness, 1)
    }


def estimate_genre(bpm: float, energy: float, brightness: float) -> str:
    """BPM, 에너지, 밝기로 장르를 추정합니다 (단순 rule-based)."""
    
    if bpm >= 128 and energy > 0.6:
        return "EDM / Dance Pop"
    elif bpm >= 120 and energy > 0.5 and brightness > 2000:
        return "Upbeat K-Pop"
    elif bpm >= 100 and energy > 0.4:
        return "Pop / K-Pop"
    elif bpm >= 90 and energy < 0.4:
        return "R&B / Soul"
    elif bpm < 90 and energy < 0.35:
        return "Ballad / Slow Pop"
    elif bpm >= 80 and brightness < 1500:
        return "R&B Ballad"
    else:
        return "Contemporary Pop"
