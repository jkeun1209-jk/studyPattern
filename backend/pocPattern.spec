# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 빌드 설정 — Design Pattern PoC
# 실행: cd backend && pyinstaller pocPattern.spec

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # frontend 정적 파일 번들 (HTML/CSS/JS)
        ('../frontend', 'frontend'),
    ],
    hiddenimports=[
        # uvicorn 동적 임포트 모듈 (자동 감지 안 됨)
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        # anyio 백엔드
        'anyio._backends._asyncio',
        'anyio._backends._trio',
        # FastAPI / Starlette
        'fastapi',
        'starlette',
        'starlette.routing',
        'starlette.staticfiles',
        # 기타
        'multipart',
        'email.mime.text',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DesignPatternPoC',   # 출력 파일명: DesignPatternPoC.exe
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,              # False 로 바꾸면 콘솔 창 없이 실행
    icon=None,                 # 아이콘 경로 지정 가능: 'icon.ico'
)
