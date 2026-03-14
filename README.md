# 🎵 Promptify

**YouTube URL → AI 음악 분석 → Suno AI 프롬프트 자동 생성**

레퍼런스 곡을 분석하고 Suno AI용 음악 프롬프트를 자동으로 만들어주는 서비스입니다.

## 기능

- YouTube URL 입력 → BPM · Key · Energy 분석
- 장르 히스토리 / 핵심 매력 포인트 / 시장 포지셔닝 등 구조화된 AI 분석 리포트 생성
- Suno AI 프롬프트 자동 생성 및 복사

## 프로젝트 구조

```
promptify/
├── backend/
│   ├── api.py              # FastAPI 서버
│   ├── analyzer.py         # librosa 음악 분석
│   ├── downloader.py       # yt-dlp YouTube 다운로드
│   ├── ai_generator.py     # Claude API 리포트 생성
│   └── requirements.txt
└── frontend/
    └── index.html          # 웹 UI
```

## 로컬 실행

```bash
# 1. 의존성 설치
cd backend
pip install -r requirements.txt

# 2. 환경변수 설정
# Windows: set ANTHROPIC_API_KEY=your_key
# Mac/Linux: export ANTHROPIC_API_KEY=your_key

# 3. ffmpeg 경로 설정 (downloader.py의 FFMPEG_LOCATION 수정)

# 4. 서버 실행
py -m uvicorn api:app --reload

# 5. frontend/index.html 을 브라우저로 열기
```

## 기술 스택

- **Backend**: Python · FastAPI · librosa · yt-dlp · ffmpeg
- **AI**: Claude API (Anthropic)
- **Frontend**: HTML / CSS / JavaScript

## 환경변수

| 변수 | 설명 |
|------|------|
| `ANTHROPIC_API_KEY` | Anthropic API 키 |
| `FFMPEG_LOCATION` | ffmpeg 설치 경로 |
