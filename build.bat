@echo off
echo ============================================
echo  Design Pattern PoC - EXE 빌드
echo ============================================
echo.

cd /d "%~dp0backend"

echo [1/2] pyinstaller 설치 확인...
pip install pyinstaller --quiet

echo [2/2] 빌드 시작...
pyinstaller pocPattern.spec --clean --noconfirm

echo.
if exist "dist\DesignPatternPoC.exe" (
    echo [완료] dist\DesignPatternPoC.exe 생성됨
    echo        파일 크기:
    for %%A in ("dist\DesignPatternPoC.exe") do echo        %%~zA bytes
) else (
    echo [실패] 빌드 중 오류가 발생했습니다.
)

echo.
pause
