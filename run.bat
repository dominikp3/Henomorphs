@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call .venv\Scripts\activate
IF %ERRORLEVEL% NEQ 0 (
  echo Failed to activate venv
  PAUSE
  exit
)
python main.py
PAUSE
