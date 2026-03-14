from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from downloader import download_audio, get_song_info_from_url
from analyzer import analyze_song
from ai_generator import generate_analysis

app = FastAPI(title="Promptify API", version="1.0.0")

# CORS 설정 (프론트엔드에서 API 호출 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    url: str
    title: str = ""   # 선택: 유튜브 외 곡 제목 직접 입력
    artist: str = ""  # 선택: 아티스트명 직접 입력


@app.get("/")
def root():
    return {"service": "Promptify", "version": "1.0.0", "status": "running"}


@app.get("/info")
def get_info(url: str):
    """YouTube 메타데이터만 미리 가져오기 (다운로드 없음)"""
    try:
        info = get_song_info_from_url(url)
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    """
    유튜브 URL → 오디오 분석 → AI 리포트 생성
    """
    try:
        # 1. 오디오 다운로드
        mp3_path, yt_title, yt_artist = download_audio(req.url)
        
        title = req.title or yt_title
        artist = req.artist or yt_artist
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"다운로드 실패: {str(e)}")

    try:
        # 2. 음악 분석
        audio_features = analyze_song(mp3_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")

    try:
        # 3. AI 리포트 생성
        song_info = {
            "title": title,
            "artist": artist,
            "youtube_url": req.url,
            **audio_features
        }
        
        result = generate_analysis(song_info)
        
        return {
            "success": True,
            "title": title,
            "artist": artist,
            "features": audio_features,
            "report": result["report"],
            "suno_prompt": result["suno_prompt"],
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 분석 실패: {str(e)}")


@app.get("/health")
def health():
    return {"status": "ok"}
