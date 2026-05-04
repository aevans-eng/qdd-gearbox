$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
. (Join-Path $root "mks-python-env.ps1")
$python = $script:MksPython
$repoRoot = Split-Path (Split-Path (Split-Path $root -Parent) -Parent) -Parent
$jsonOut = Join-Path $repoRoot "qdd-gearbox\testing\data\motor-controller-probe.json"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Python not found at $python"
}

New-Item -ItemType Directory -Force -Path (Split-Path $jsonOut -Parent) | Out-Null

& $python `
    (Join-Path $root "odrive_probe.py") `
    --profile gearbox `
    --current-limit 10.0 `
    --watchdog-timeout 0.5 `
    --json-out $jsonOut
