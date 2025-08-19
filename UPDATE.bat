@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
IF "%1" NEQ "--skip-pull" (
  echo Fetching latest version from git repository
  git pull
  IF !ERRORLEVEL! NEQ 0 (
    echo Failed to pull
    PAUSE
    exit
  )
)
echo Installing or updating dependencies
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
  echo Failed to install / update dependencies
  PAUSE
  exit
)
PAUSE