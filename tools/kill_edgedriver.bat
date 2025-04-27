:: 5. edgedriver.exe가 실행 중이면 종료
:: tasklist | findstr /I "edge"로 찾아진 모든 프로세스를 종료 (중복 방지)

setlocal enabledelayedexpansion
set "PROC_SET="

echo Checking for running Edge-related processes...
for /f "tokens=1" %%i in ('tasklist ^| findstr /I "edge"') do (
    set "PROC=%%i"
    set "PROC_LC=!PROC!"
    echo !PROC_SET! | findstr /I /C:"!PROC_LC!;" >nul
    if errorlevel 1 (
        echo Terminating process: !PROC!
        taskkill /F /IM !PROC!
        set "PROC_SET=!PROC_SET!!PROC_LC!;"
    )
)

echo Done.