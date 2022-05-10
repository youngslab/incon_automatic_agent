@ECHO off

set "params=%*"
cd /d "%~dp0" && ( if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs" ) ^
              && fsutil dirty query %systemdrive% 1>nul 2>nul ^
              || ( echo Set UAC = CreateObject^("Shell.Application"^) : UAC.ShellExecute "cmd.exe", "/k cd ""%~sdp0"" && %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs" && "%temp%\getadmin.vbs" && exit /B )

@SET PYTHON_EXE=
FOR /F %%I IN ('where python') DO @SET "PYTHON_EXE=%%I"

schtasks /CREATE /SC DAILY /ST 10:00:00 /RL HIGHEST ^
    /TN "youngs\Incon Automatic Service" ^
    /TR "%PYTHON_EXE% %~dp0\agent.py"

pause
exit