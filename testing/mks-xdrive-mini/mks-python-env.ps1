$ErrorActionPreference = "Stop"

$venvPython = Join-Path $PSScriptRoot ".venv-odrive051\Scripts\python.exe"
$fallbackPython = "C:\Users\aaron\miniconda3\python.exe"

if (Test-Path -LiteralPath $venvPython) {
    $script:MksPython = $venvPython

    $libusbDir = Join-Path $PSScriptRoot ".venv-odrive051\Lib\site-packages\libusb_package"
    if (Test-Path -LiteralPath $libusbDir) {
        $env:PATH = "$libusbDir;$env:PATH"
    }
}
elseif (Test-Path -LiteralPath $fallbackPython) {
    $script:MksPython = $fallbackPython
}
else {
    throw "Python not found at $venvPython or $fallbackPython"
}
