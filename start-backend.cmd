@echo off
setlocal
set "ROOT=%~dp0"
set "NODEBIN=C:\Users\ABC\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin"
set "NODE=%NODEBIN%\node.exe"
set "PATH=%NODEBIN%;%PATH%"
cd /d "%ROOT%backend"
if not exist "%NODE%" (
  echo Node runtime not found:
  echo %NODE%
  pause
  exit /b 1
)
"%NODE%" "server.js"
pause
