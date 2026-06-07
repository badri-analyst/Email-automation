$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$NodeBin = "C:\Users\ABC\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin"
$Node = Join-Path $NodeBin "node.exe"
$Npm = Join-Path $Root ".tools\package\bin\npm-cli.js"
$env:PATH = "$NodeBin;$env:PATH"
Set-Location (Join-Path $Root "frontend")
if (-not (Test-Path (Join-Path (Get-Location) "dist\index.html"))) {
  & $Node $Npm run build
}
& $Node "serve-dist.js"
