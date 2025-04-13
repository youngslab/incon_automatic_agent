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