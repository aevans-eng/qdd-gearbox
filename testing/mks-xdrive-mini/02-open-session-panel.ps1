$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
. (Join-Path $root "mks-python-env.ps1")
$python = $script:MksPython

if (-not (Test-Path -LiteralPath $python)) {
    throw "Python not found at $python"
}

& $python (Join-Path $root "odrive-session-panel.py")
