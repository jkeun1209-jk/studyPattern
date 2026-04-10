"""
실행 진입점 — PyInstaller .exe 빌드 및 직접 실행 모두 지원
  - uvicorn 서버를 프로그래밍 방식으로 시작
  - 서버 준비 후 기본 브라우저를 자동으로 열어줌
"""
import sys
import threading
import webbrowser
import uvicorn

HOST = "127.0.0.1"
PORT = 8000
URL  = f"http://{HOST}:{PORT}"


def _open_browser():
    webbrowser.open(URL)


if __name__ == "__main__":
    print(f"[DesignPattern PoC] 서버 시작 중... {URL}")

    # 1.8초 후 브라우저 자동 오픈 (uvicorn 기동 시간 확보)
    threading.Timer(1.8, _open_browser).start()

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        log_level="warning",   # INFO 로그 줄여 콘솔 깔끔하게
    )
