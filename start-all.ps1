$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$Root\start-backend.ps1`""
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$Root\start-frontend.ps1`""
Write-Host "Backend:  http://localhost:8080"
Write-Host "Frontend: http://localhost:5173"
