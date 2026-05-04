$ErrorActionPreference = "Stop"

$root = $PSScriptRoot

Write-Host "=== MKS Sprint Smoke Test ==="
Write-Host "1. Status"
PowerShell -ExecutionPolicy Bypass -File (Join-Path $root "10-agent-control.ps1") status

Write-Host ""
Write-Host "2. Calibrate"
PowerShell -ExecutionPolicy Bypass -File (Join-Path $root "10-agent-control.ps1") calibrate

Write-Host ""
Write-Host "3. Very small velocity command (5 RPM, 1 second)"
PowerShell -ExecutionPolicy Bypass -File (Join-Path $root "10-agent-control.ps1") velocity --rpm 5 --seconds 1

Write-Host ""
Write-Host "4. Idle"
PowerShell -ExecutionPolicy Bypass -File (Join-Path $root "10-agent-control.ps1") idle

Write-Host ""
Write-Host "Smoke test complete."
