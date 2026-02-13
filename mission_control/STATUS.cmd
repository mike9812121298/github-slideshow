@echo off
setlocal
cd /d "%~dp0"

echo [Mission Control] Checking port 8080...
netstat -ano | findstr ":8080"
if errorlevel 1 (
  echo [Mission Control] No process listening on port 8080.
) else (
  echo [Mission Control] If needed, run STOP.cmd to terminate the process.
)
pause
