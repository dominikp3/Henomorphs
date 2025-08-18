@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call .venv\Scripts\activate
python main.py
PAUSE
