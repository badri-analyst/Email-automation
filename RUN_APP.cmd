@echo off
setlocal
set "ROOT=%~dp0"
set "NODEBIN=C:\Users\ABC\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin"
set "NODE=%NODEBIN%\node.exe"

if not exist "%NODE%" (
  echo Node runtime not found:
  echo %NODE%
  echo.
  echo Install Node.js or update NODEBIN in this file.
  pause
  exit /b 1
)

if not exist "%ROOT%frontend\dist\index.html" (
  echo Frontend build not found at frontend\dist\index.html
  echo Run frontend dependency install/build first.
  pause
  exit /b 1
)

echo Starting backend on http://127.0.0.1:8080 ...
start "AI Outreach Backend" cmd /k call "%ROOT%start-backend.cmd"

echo Starting frontend on http://127.0.0.1:5173 ...
start "AI Outreach Frontend" cmd /k call "%ROOT%start-frontend.cmd"

timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:5173"

echo.
echo If the browser still says connection refused, keep this window open and check
echo the two server windows for the error message.
echo.
echo Frontend: http://127.0.0.1:5173
echo Backend:  http://127.0.0.1:8080
pause
