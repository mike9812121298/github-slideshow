@echo off
setlocal
cd /d "%~dp0"

echo [Mission Control] Stopping process on port 8080...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr "LISTENING"') do (
  echo [Mission Control] Terminating PID %%a
  taskkill /PID %%a /F
)

if errorlevel 1 (
  echo [Mission Control] No active listener found on port 8080.
)
pause
