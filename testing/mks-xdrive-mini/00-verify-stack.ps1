$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
. (Join-Path $root "mks-python-env.ps1")
$python = $script:MksPython

if (-not (Test-Path -LiteralPath $python)) {
    throw "Python not found at $python"
}

$files = @(
    (Join-Path $root "odrive_probe.py"),
    (Join-Path $root "odrive-session-panel.py"),
    (Join-Path $root "mks_agent_control.py"),
    (Join-Path $root "requirements.txt"),
    (Join-Path $root "STACK.md"),
    (Join-Path $root "10-agent-control.ps1")
)

foreach ($file in $files) {
    if (-not (Test-Path -LiteralPath $file)) {
        throw "Missing required file: $file"
    }
}

Write-Host "Python:" $python
& $python -c "import sys; print(sys.version)"
Write-Host ""
Write-Host "Package check..."
& $python -c "import odrive, matplotlib; from importlib.metadata import version; print('odrive', odrive.__version__); print('bleak', version('bleak')); print('matplotlib', matplotlib.__version__)"
Write-Host ""
Write-Host "Probe help check..."
& $python (Join-Path $root "odrive_probe.py") --help | Out-Null
Write-Host "Agent CLI help check..."
& $python (Join-Path $root "mks_agent_control.py") --help | Out-Null
Write-Host "Session panel syntax check..."
& $python -m py_compile (Join-Path $root "odrive-session-panel.py")
Write-Host "Agent CLI syntax check..."
& $python -m py_compile (Join-Path $root "mks_agent_control.py")
Write-Host ""
Write-Host "Motor-control sprint stack looks ready."
