@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
WHERE python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 goto nopy
WHERE pip >nul 2>nul
IF %ERRORLEVEL% NEQ 0 goto nopy

if exist .venv\ (
  set /p input=venv is already exist. Delete and reinstall? [y/n]: 
  if "!input!" NEQ "y" (exit) else (rmdir /S /Q .venv)
)

echo Creating venv
python -m venv .venv
IF %ERRORLEVEL% NEQ 0 (
  echo Failed to create venv
  PAUSE
  exit
)
echo Executing update script
call update.bat --skip-pull
exit
:nopy
echo Python not found. Ensure You have python and pip correctly installed and added to PATH
