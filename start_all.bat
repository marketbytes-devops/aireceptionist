@echo off
title AyurVoice SaaS Launcher
echo ===================================================
echo 🌿 Launching AyurVoice SaaS (Backend + Frontend)...
echo ===================================================

start "AyurVoice Backend (Port 8000)" cmd /k "start_backend.bat"
timeout /t 3 /nobreak >nul
start "AyurVoice Frontend (Port 3000)" cmd /k "start_frontend.bat"

echo.
echo Both servers are starting up!
echo - Backend API:  http://localhost:8000/docs
echo - Frontend App: http://localhost:3000
echo ===================================================
pause

