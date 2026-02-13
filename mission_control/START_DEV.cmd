@echo off
setlocal
cd /d "%~dp0"

set "VENV_PY=%~dp0.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
  echo [Mission Control] Creating local virtual environment at %~dp0.venv
  python -m venv "%~dp0.venv"
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
  )
)

"%VENV_PY%" -c "import fastapi" >nul 2>&1
if errorlevel 1 (
  echo [Mission Control] Installing requirements...
  "%VENV_PY%" -m pip install --upgrade pip
  if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip.
    pause
    exit /b 1
  )
  "%VENV_PY%" -m pip install -r "%~dp0requirements.txt"
  if errorlevel 1 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
  )
)

echo [Mission Control] Starting development server on http://127.0.0.1:8080/ui
"%VENV_PY%" -m uvicorn app:app --host 127.0.0.1 --port 8080 --reload --log-level debug
if errorlevel 1 (
  echo [ERROR] Server exited with an error.
)
pause
