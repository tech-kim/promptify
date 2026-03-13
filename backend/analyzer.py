import librosa
import numpy as np

def analyze_song(path):

    y, sr = librosa.load(path)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    tempo = float(np.atleast_1d(tempo)[0])

    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)

    notes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    key = notes[chroma_mean.argmax()]

    return {
        "bpm": round(tempo),
        "key": key
    }