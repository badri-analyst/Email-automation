@echo off
setlocal
set "ROOT=%~dp0"
start "AI Outreach Backend" cmd /k call "%ROOT%start-backend.cmd"
start "AI Outreach Frontend" cmd /k call "%ROOT%start-frontend.cmd"
echo Backend:  http://localhost:8080
echo Frontend: http://localhost:5173
pause
