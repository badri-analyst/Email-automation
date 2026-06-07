@echo off
setlocal
set "ROOT=%~dp0"
set "NODEBIN=C:\Users\ABC\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin"
set "NODE=%NODEBIN%\node.exe"
set "NPM=%ROOT%.tools\package\bin\npm-cli.js"
set "PATH=%NODEBIN%;%PATH%"
cd /d "%ROOT%frontend"
if not exist "dist\index.html" (
  "%NODE%" "%NPM%" run build
)
"%NODE%" "serve-dist.js"
pause
