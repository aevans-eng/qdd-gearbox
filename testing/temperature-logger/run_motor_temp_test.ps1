param(
    [ValidateSet("velocity", "torque", "position", "status", "calibrate", "idle")]
    [string]$Command = "velocity",

    [ValidateSet("gearbox", "bare")]
    [string]$Profile = "gearbox",

    [double]$Ratio = 5.0,
    [double]$Rpm = 10.0,
    [double]$Nm = 0.5,
    [double]$Deg = 45.0,
    [double]$Seconds = 5.0,
    [switch]$Calibrate,

    [string]$TempPort = "COM6",
    [int]$Baud = 115200,
    [double]$PreLogSeconds = 3.0,
    [double]$PostLogSeconds = 5.0
)

$ErrorActionPreference = "Stop"

$toolRoot = $PSScriptRoot
$repoRoot = Resolve-Path (Join-Path $toolRoot "..\..")
$python = "C:\Users\aaron\miniconda3\python.exe"
$logger = Join-Path $toolRoot "log_thermistor.py"
$controller = Join-Path $repoRoot "testing\mks-xdrive-mini\10-agent-control.ps1"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$output = Join-Path $repoRoot "testing\data\thermistor-motor-test-$timestamp.csv"
$logSeconds = [Math]::Max(1.0, $PreLogSeconds + $Seconds + $PostLogSeconds)

if (-not (Test-Path -LiteralPath $python)) {
    throw "Python not found at $python"
}

if (-not (Test-Path -LiteralPath $logger)) {
    throw "Thermistor logger not found at $logger"
}

if (-not (Test-Path -LiteralPath $controller)) {
    throw "MKS control wrapper not found at $controller"
}

Write-Host "=== QDD Motor Temperature Test ==="
Write-Host "Temp logger: $TempPort at $Baud baud"
Write-Host "Temp CSV:    $output"
Write-Host "Motor cmd:   $Command"

$tempJob = Start-Job -ScriptBlock {
    param($Python, $Logger, $Port, $BaudRate, $OutputPath, $Duration)
    & $Python $Logger --port $Port --baud $BaudRate --output $OutputPath --seconds $Duration
} -ArgumentList $python, $logger, $TempPort, $Baud, $output, $logSeconds

try {
    Start-Sleep -Seconds $PreLogSeconds

    $controllerArgs = @("--profile", $Profile, "--ratio", "$Ratio", $Command)

    switch ($Command) {
        "velocity" {
            $controllerArgs += @("--rpm", "$Rpm", "--seconds", "$Seconds")
        }
        "torque" {
            $controllerArgs += @("--nm", "$Nm", "--seconds", "$Seconds")
        }
        "position" {
            $controllerArgs += @("--deg", "$Deg")
        }
    }

    if ($Calibrate -and $Command -in @("velocity", "torque", "position")) {
        $controllerArgs += "--calibrate"
    }

    PowerShell -ExecutionPolicy Bypass -File $controller @controllerArgs
}
finally {
    $remaining = [Math]::Max(0.0, $PostLogSeconds)
    if ($remaining -gt 0) {
        Start-Sleep -Seconds $remaining
    }

    if ((Get-Job -Id $tempJob.Id).State -eq "Running") {
        Stop-Job -Id $tempJob.Id
    }

    Receive-Job -Id $tempJob.Id
    Remove-Job -Id $tempJob.Id -Force

    Write-Host ""
    Write-Host "Temperature log written:"
    Write-Host $output
}
