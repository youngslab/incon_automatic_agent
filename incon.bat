@echo off
setlocal enabledelayedexpansion

:: 현재 스크립트가 있는 디렉토리로 이동
cd /d %~dp0

:: Git repository 루트 디렉토리 찾기
for /f "delims=" %%i in ('git rev-parse --show-toplevel 2^>nul') do set GIT_ROOT=%%i

if "%GIT_ROOT%"=="" (
    echo Error: This script must be run inside a Git repository.
    pause
    exit /b 1
)

cd /d %GIT_ROOT%
echo Git repository found at: %GIT_ROOT%

:: 1. Git 저장소 업데이트
echo Updating git repository...
git pull

:: 2. 가상 환경 설정 (venv)
set VENV_PATH=%GIT_ROOT%\env
if not exist "%VENV_PATH%" (
    echo Creating virtual environment...
    python -m venv "%VENV_PATH%"
)

:: 3. 가상 환경 활성화
echo Activating virtual environment...
call "%VENV_PATH%\Scripts\activate.bat"

:: 4. Python 의존성 설치
if exist "%GIT_ROOT%\requirements.txt" (
    echo Installing dependencies...
    pip install -r "%GIT_ROOT%\requirements.txt" >nul 2>&1
) else (
    echo No requirements.txt found.
)

:: 5. edgedriver.exe가 실행 중이면 종료
echo Checking for running EdgeDriver instances...
tasklist | findstr /I "msedgedriver.exe" >nul
if %ERRORLEVEL%==0 (
    echo Found running msedgedriver.exe, terminating process...
    taskkill /F /IM msedgedriver.exe
    timeout /t 3 >nul
) else (
    echo No running msedgedriver.exe found.
)

:: 6. agent.py 실행
set AGENT_PATH=%GIT_ROOT%\agent.py
if exist "%AGENT_PATH%" (
    echo Running agent.py...
    python "%AGENT_PATH%"
) else (
    echo Error: agent.py not found.
)

