@echo off
setlocal
cd /d "%~dp0"
title Duplicate - Local Website

where py >nul 2>nul
if %errorlevel%==0 (
    start "" /b cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8000"
    py -m http.server 8000 --bind 127.0.0.1
    goto :end
)

where python >nul 2>nul
if %errorlevel%==0 (
    start "" /b cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8000"
    python -m http.server 8000 --bind 127.0.0.1
    goto :end
)

echo Python was not found.
echo Install Python from https://www.python.org/downloads/windows/
echo During installation, enable "Add Python to PATH".
pause

:end
endlocal
