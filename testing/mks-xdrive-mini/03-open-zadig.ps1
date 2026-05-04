$ErrorActionPreference = "Stop"

$zadig = "C:\Users\aaron\Documents\c-projects\qdd-gearbox\testing\hardware\zadig-2.9.exe"

if (-not (Test-Path -LiteralPath $zadig)) {
    throw "Zadig not found at $zadig"
}

Start-Process -FilePath $zadig
Write-Host "Opened Zadig."
