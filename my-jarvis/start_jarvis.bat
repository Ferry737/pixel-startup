@echo off
REM Jarvis P01 launcher: server + Opera GX pinned-tab workflow
cd /d "%~dp0"
start "jarvis-4700" python server.py
timeout /t 3 /nobreak >nul
start "" "%LOCALAPPDATA%\Programs\Opera GX\opera.exe" http://127.0.0.1:4700/
echo Opened Jarvis galaxy in Opera GX. Pin the tab to keep it docked.
