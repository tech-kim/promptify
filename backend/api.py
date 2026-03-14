from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_generator import generate_analysis

app = FastAPI(title="Promptify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    title: str
    artist: str = ""
    genre: str = ""

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        song_info = {
            "title": req.title,
            "artist": req.artist,
            "genre_guess": req.genre,
            "bpm": "알 수 없음",
            "key": "알 수 없음",
            "energy_label": "알 수 없음",
        }
        result = generate_analysis(song_info)
        return {
            "success": True,
            "title": req.title,
            "artist": req.artist,
            "report": result["report"],
            "suno_prompt": result["suno_prompt"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def root():
    return {"status": "Promptify API is running"}