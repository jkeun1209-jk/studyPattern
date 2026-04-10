import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import patterns


def _get_frontend_dir() -> Path:
    """PyInstaller 번들(.exe)과 일반 실행(uvicorn) 모두에서 올바른 frontend 경로 반환"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller --onefile: 임시 디렉토리에 번들된 frontend 참조
        return Path(sys._MEIPASS) / "frontend"
    # 일반 개발 실행: backend/../frontend
    return Path(__file__).parent.parent / "frontend"


FRONTEND_DIR = _get_frontend_dir()

app = FastAPI(title="Design Pattern PoC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patterns.router, prefix="/api")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def root():
    return FileResponse(FRONTEND_DIR / "index.html")
