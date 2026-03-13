from fastapi import FastAPI
from downloader import download_audio
from analyzer import analyze_song
from prompt_generator import generate_prompt

app = FastAPI()

@app.get("/")
def home():
    return {"service": "Promptify"}

@app.get("/analyze")
def analyze(url: str):

    path = download_audio(url)

    result = analyze_song(path)

    prompt = generate_prompt(result)

    return {
        "bpm": result["bpm"],
        "key": result["key"],
        "prompt": prompt
    }