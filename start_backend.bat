@echo off
title AyurVoice SaaS - Backend Server
echo ===================================================
echo 🌿 Starting AyurVoice SaaS FastAPI Backend...
echo ===================================================
cd backend
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)
python run.py
pause

