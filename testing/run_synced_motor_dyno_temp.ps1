param(
    [string]$Label = "synced-run",
    [ValidateSet("torque", "velocity")]
    [string]$Mode = "torque",
    [double]$TargetTorqueNm = -1.2,
    [double]$TargetVelocityTps = -2.0,
    [double]$VelocityRampRateTps2 = 0.05,
    [double]$RampSeconds = 100.0,
    [double]$HoldSeconds = 3.0,
    [double]$CurrentLimitA = 30.0,
    [double]$StopOnVelocityTps = 1.0,
    [double]$RampdownSeconds = 25.0,
    [double]$MotorDtSeconds = 0.5,
    [double]$CaptureSeconds = 220.0,
    [double]$MaxMotorTempC = 50.0,
    [double]$MaxFetTempC = 70.0,
    [double]$GearRatio = 5.0,
    [double]$TorqueConstantNmPerA = 0.04,
    [double]$TargetEfficiency = 0.90,
    [double]$ContinuousCurrentCapA = 60.0,
    [double]$PeakCurrentCapA = 90.0,
    [string]$TestStage = "development",
    [ValidateSet("bare_motor", "gearbox_installed", "unknown")]
    [string]$HardwareSetup = "unknown",
    [bool]$FanInstalled = $true,
    [double]$PsuVoltageV = 24.0,
    [double]$PsuCurrentLimitA = 10.0,
    [double]$PsuOvpV = 30.0,
    [double]$PsuOcpA = 10.0,
    [string]$TempPort = "COM6",
    [int]$TempBaud = 115200
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$dataRoot = Join-Path $repoRoot "testing\data"
$dynoRoot = Join-Path $repoRoot "testing\dyno\ble-capture"
$mksRoot = Join-Path $repoRoot "testing\mks-xdrive-mini"
$tempRoot = Join-Path $repoRoot "testing\temperature-logger"
$python = "C:\Users\aaron\miniconda3\python.exe"

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$safeLabel = ($Label -replace '[^A-Za-z0-9_.-]', '_')
$runDir = Join-Path $dataRoot "synced-$safeLabel-$stamp"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$motorLog = Join-Path $runDir "motor.log"
$tempCsv = Join-Path $runDir "temperature.csv"
$tempStdout = Join-Path $runDir "temperature.stdout.log"
$dynoCsv = Join-Path $runDir "dyno.csv"
$dynoStdout = Join-Path $runDir "dyno.stdout.log"
$emergencyLog = Join-Path $runDir "emergency-idle.log"
$tempExitCodePath = Join-Path $runDir "temperature.exitcode"
$dynoExitCodePath = Join-Path $runDir "dyno.exitcode"
$motorExitCodePath = Join-Path $runDir "motor.exitcode"
$manifestPath = Join-Path $runDir "manifest.json"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Python not found at $python"
}

function Write-Manifest($status, $extra = @{}) {
    $manifest = [ordered]@{
        status = $status
        label = $Label
        created_at = (Get-Date).ToString("o")
        run_dir = $runDir
        files = [ordered]@{
            motor_log = $motorLog
            temperature_csv = $tempCsv
            temperature_stdout = $tempStdout
            dyno_csv = $dynoCsv
            dyno_stdout = $dynoStdout
            emergency_idle_log = $emergencyLog
            temperature_exitcode = $tempExitCodePath
            dyno_exitcode = $dynoExitCodePath
            motor_exitcode = $motorExitCodePath
        }
        settings = [ordered]@{
            test_stage = $TestStage
            hardware_setup = $HardwareSetup
            fan_installed = $FanInstalled
            mode = $Mode
            target_torque_nm = $TargetTorqueNm
            target_velocity_tps = $TargetVelocityTps
            velocity_ramp_rate_tps2 = $VelocityRampRateTps2
            ramp_seconds = $RampSeconds
            hold_seconds = $HoldSeconds
            current_limit_a = $CurrentLimitA
            stop_on_velocity_tps = $StopOnVelocityTps
            rampdown_seconds = $RampdownSeconds
            motor_dt_seconds = $MotorDtSeconds
            capture_seconds = $CaptureSeconds
            max_motor_temp_c = $MaxMotorTempC
            max_fet_temp_c = $MaxFetTempC
            gear_ratio = $GearRatio
            torque_constant_nm_per_a = $TorqueConstantNmPerA
            target_efficiency = $TargetEfficiency
            continuous_current_cap_a = $ContinuousCurrentCapA
            peak_current_cap_a = $PeakCurrentCapA
            psu_voltage_v = $PsuVoltageV
            psu_current_limit_a = $PsuCurrentLimitA
            psu_ovp_v = $PsuOvpV
            psu_ocp_a = $PsuOcpA
            temp_port = $TempPort
            temp_baud = $TempBaud
        }
        requirement_math = [ordered]@{
            continuous_output_torque_nm = 12.0
            peak_output_torque_nm = 16.0
            speed_output_rpm = 600.0
            current_for_12nm_at_target_eff_a = [Math]::Round(12.0 / ($GearRatio * $TargetEfficiency * $TorqueConstantNmPerA), 2)
            current_for_16nm_at_target_eff_a = [Math]::Round(16.0 / ($GearRatio * $TargetEfficiency * $TorqueConstantNmPerA), 2)
            est_output_torque_at_current_limit_nm = [Math]::Round($CurrentLimitA * $TorqueConstantNmPerA * $GearRatio * $TargetEfficiency, 2)
        }
    }

    foreach ($key in $extra.Keys) {
        $manifest[$key] = $extra[$key]
    }

    $json = $manifest | ConvertTo-Json -Depth 8
    $written = $false
    for ($attempt = 1; $attempt -le 20; $attempt++) {
        try {
            Set-Content -LiteralPath $manifestPath -Value $json -Encoding UTF8
            $written = $true
            break
        }
        catch {
            Start-Sleep -Milliseconds 500
        }
    }
    if (-not $written) {
        Write-Warning "Manifest write to $manifestPath failed after 20 retries; continuing without manifest update."
    }
}

Write-Manifest "starting"

$tempStart = Get-Date
$tempJob = Start-Job -ScriptBlock {
    param($Python, $TempRoot, $Port, $Baud, $OutPath, $Seconds, $StdoutPath, $ExitCodePath)
    & $Python (Join-Path $TempRoot "log_thermistor.py") --port $Port --baud $Baud --output $OutPath --seconds $Seconds *> $StdoutPath
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = 0 }
    Set-Content -LiteralPath $ExitCodePath -Value $code -Encoding ASCII
    exit $code
} -ArgumentList $python, $tempRoot, $TempPort, $TempBaud, $tempCsv, $CaptureSeconds, $tempStdout, $tempExitCodePath

Start-Sleep -Seconds 3

$dynoStart = Get-Date
$dynoJob = Start-Job -ScriptBlock {
    param($Python, $DynoRoot, $OutPath, $Seconds, $StdoutPath, $ExitCodePath)
    Set-Location -LiteralPath $DynoRoot
    & $Python "dyno.py" capture --duration $Seconds --output $OutPath --no-plot -q *> $StdoutPath
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = 0 }
    Set-Content -LiteralPath $ExitCodePath -Value $code -Encoding ASCII
    exit $code
} -ArgumentList $python, $dynoRoot, $dynoCsv, $CaptureSeconds, $dynoStdout, $dynoExitCodePath

Start-Sleep -Seconds 3

$motorStart = Get-Date
$motorJob = Start-Job -ScriptBlock {
    param($MksRoot, $LogPath, $Mode, $TargetTorque, $TargetVelocity, $VelocityRampRate, $RampSeconds, $HoldSeconds, $CurrentLimit, $StopOnVelocity, $RampdownSeconds, $DtSeconds, $MaxFetTemp, $CaptureSeconds, $Label, $ExitCodePath)
    . (Join-Path $MksRoot "mks-python-env.ps1")

    if ($Mode -eq "velocity") {
        & $script:MksPython (Join-Path $MksRoot "safe_ramp_test.py") `
            --profile bare `
            --target $TargetVelocity `
            --ramp-rate $VelocityRampRate `
            --hold $HoldSeconds `
            --current-limit $CurrentLimit `
            --watchdog-timeout 2 `
            --stop-on-velocity $StopOnVelocity `
            --max-fet-temp-c $MaxFetTemp `
            --max-runtime-seconds $CaptureSeconds `
            --label $Label *> $LogPath
    }
    else {
        & $script:MksPython (Join-Path $MksRoot "safe_torque_ramp_test.py") `
            --target-torque $TargetTorque `
            --ramp-seconds $RampSeconds `
            --hold $HoldSeconds `
            --current-limit $CurrentLimit `
            --watchdog-timeout 2 `
            --stop-on-velocity $StopOnVelocity `
            --rampdown-seconds $RampdownSeconds `
            --dt $DtSeconds `
            --max-fet-temp-c $MaxFetTemp `
            --max-runtime-seconds $CaptureSeconds `
            --label $Label *> $LogPath
    }
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = 0 }
    Set-Content -LiteralPath $ExitCodePath -Value $code -Encoding ASCII
    exit $code
} -ArgumentList $mksRoot, $motorLog, $Mode, $TargetTorqueNm, $TargetVelocityTps, $VelocityRampRateTps2, $RampSeconds, $HoldSeconds, $CurrentLimitA, $StopOnVelocityTps, $RampdownSeconds, $MotorDtSeconds, $MaxFetTempC, $CaptureSeconds, $Label, $motorExitCodePath

Write-Manifest "running" @{
    starts = [ordered]@{
        temperature = $tempStart.ToString("o")
        dyno = $dynoStart.ToString("o")
        motor = $motorStart.ToString("o")
    }
}

function Invoke-EmergencyIdle($Reason) {
    "Emergency idle: $Reason" | Set-Content -LiteralPath $emergencyLog -Encoding UTF8
    try {
        & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $mksRoot "10-agent-control.ps1") idle *>> $emergencyLog
    }
    catch {
        "Emergency idle command failed: $($_.Exception.Message)" | Add-Content -LiteralPath $emergencyLog -Encoding UTF8
    }
}

function Read-LatestMotorTempC {
    if (-not (Test-Path -LiteralPath $tempCsv)) {
        return $null
    }
    $line = Get-Content -LiteralPath $tempCsv -Tail 1 -ErrorAction SilentlyContinue
    if (-not $line -or $line -match '^pc_timestamp,') {
        return $null
    }
    $parts = $line -split ','
    if ($parts.Count -lt 6) {
        return $null
    }
    try {
        return [double]$parts[5]
    }
    catch {
        return $null
    }
}

function Read-LatestFetTempC {
    if (-not (Test-Path -LiteralPath $motorLog)) {
        return $null
    }
    $lines = @(Get-Content -LiteralPath $motorLog -Tail 12 -ErrorAction SilentlyContinue)
    [array]::Reverse($lines)
    foreach ($line in $lines) {
        if ($line -notmatch '^\s*\d') {
            continue
        }
        $parts = ($line -split '\s+') | Where-Object { $_ -ne '' }
        if ($parts.Count -lt 5) {
            continue
        }
        try {
            return [double]$parts[4]
        }
        catch {
            continue
        }
    }
    return $null
}

$abortReason = $null
while ((Get-Job -Id $motorJob.Id).State -eq "Running") {
    Start-Sleep -Seconds 1

    $latestMotorTemp = Read-LatestMotorTempC
    if ($null -ne $latestMotorTemp -and $latestMotorTemp -ge $MaxMotorTempC) {
        $abortReason = "motor temp $latestMotorTemp C >= $MaxMotorTempC C"
        break
    }

    $latestFetTemp = Read-LatestFetTempC
    if ($null -ne $latestFetTemp -and $latestFetTemp -ge $MaxFetTempC) {
        $abortReason = "FET temp $latestFetTemp C >= $MaxFetTempC C"
        break
    }
}

if ($abortReason) {
    Invoke-EmergencyIdle $abortReason
    foreach ($job in @($motorJob, $dynoJob, $tempJob)) {
        if ((Get-Job -Id $job.Id).State -eq "Running") {
            Stop-Job -Id $job.Id
        }
    }
}

Wait-Job -Id $motorJob.Id | Out-Null
$motorState = (Get-Job -Id $motorJob.Id).State
Receive-Job -Id $motorJob.Id | Out-Null
Remove-Job -Id $motorJob.Id -Force

Wait-Job -Id $dynoJob.Id | Out-Null
$dynoState = (Get-Job -Id $dynoJob.Id).State
Receive-Job -Id $dynoJob.Id | Out-Null
Remove-Job -Id $dynoJob.Id -Force

Wait-Job -Id $tempJob.Id | Out-Null
$tempState = (Get-Job -Id $tempJob.Id).State
Receive-Job -Id $tempJob.Id | Out-Null
Remove-Job -Id $tempJob.Id -Force

function Read-ExitCode($Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }
    try {
        return [int](Get-Content -LiteralPath $Path -TotalCount 1)
    }
    catch {
        return $null
    }
}

$motorExitCode = Read-ExitCode $motorExitCodePath
$dynoExitCode = Read-ExitCode $dynoExitCodePath
$tempExitCode = Read-ExitCode $tempExitCodePath

$summary = [ordered]@{
    motor_state = $motorState
    dyno_state = $dynoState
    temperature_state = $tempState
    motor_exit_code = $motorExitCode
    dyno_exit_code = $dynoExitCode
    temperature_exit_code = $tempExitCode
    abort_reason = $abortReason
}

if (Test-Path -LiteralPath $motorLog) {
    $motorRows = Get-Content -LiteralPath $motorLog | Where-Object { $_ -match '^\s*\d' } | ForEach-Object {
        $parts = ($_ -split '\s+') | Where-Object { $_ -ne '' }
        $fet = $null
        $dcPower = $null
        $motorMechPower = $null
        $ccIbus = $null
        if ($parts.Count -ge 5) {
            try {
                $fet = [double]$parts[4]
            }
            catch {
                $fet = $null
            }
        }
        if ($parts.Count -ge 8) {
            try {
                $dcPower = [double]$parts[7]
            }
            catch {
                $dcPower = $null
            }
        }
        if ($parts.Count -ge 9) {
            try {
                $motorMechPower = [double]$parts[8]
            }
            catch {
                $motorMechPower = $null
            }
        }
        if ($parts.Count -ge 10) {
            try {
                $ccIbus = [double]$parts[9]
            }
            catch {
                $ccIbus = $null
            }
        }
        [pscustomobject]@{
            t=[double]$parts[0]
            torque=[double]$parts[1]
            vel=[double]$parts[2]
            iq=[double]$parts[3]
            fet=$fet
            dc_power=$dcPower
            motor_mech_power=$motorMechPower
            cc_ibus=$ccIbus
        }
    }
    if ($motorRows) {
        $summary.motor_rows = $motorRows.Count
        $summary.motor_min_torque_nm = ($motorRows | Measure-Object torque -Minimum).Minimum
        $summary.motor_max_torque_nm = ($motorRows | Measure-Object torque -Maximum).Maximum
        $summary.motor_max_abs_vel_tps = ($motorRows | ForEach-Object { [Math]::Abs($_.vel) } | Measure-Object -Maximum).Maximum
        $summary.motor_max_abs_iq_a = ($motorRows | ForEach-Object { [Math]::Abs($_.iq) } | Measure-Object -Maximum).Maximum
        $summary.motor_max_fet_c = ($motorRows | Where-Object { $null -ne $_.fet } | Measure-Object fet -Maximum).Maximum
        $summary.motor_max_abs_dc_power_w = ($motorRows | Where-Object { $null -ne $_.dc_power } | ForEach-Object { [Math]::Abs($_.dc_power) } | Measure-Object -Maximum).Maximum
        $summary.motor_max_abs_est_mech_power_w = ($motorRows | Where-Object { $null -ne $_.motor_mech_power } | ForEach-Object { [Math]::Abs($_.motor_mech_power) } | Measure-Object -Maximum).Maximum
        $summary.motor_max_abs_current_control_ibus_a = ($motorRows | Where-Object { $null -ne $_.cc_ibus } | ForEach-Object { [Math]::Abs($_.cc_ibus) } | Measure-Object -Maximum).Maximum
        $summary.est_output_torque_at_max_iq_nm = [Math]::Round($summary.motor_max_abs_iq_a * $TorqueConstantNmPerA * $GearRatio * $TargetEfficiency, 2)
        $summary.est_output_rpm_at_max_encoder_vel = [Math]::Round($summary.motor_max_abs_vel_tps * 60.0 / $GearRatio, 2)
    }
}

if (Test-Path -LiteralPath $tempCsv) {
    $temps = Import-Csv -LiteralPath $tempCsv
    if ($temps.Count -gt 0) {
        $firstTemp = [double]$temps[0].temp_c
        $maxTemp = [double](($temps | Measure-Object -Property temp_c -Maximum).Maximum)
        $summary.temperature_rows = $temps.Count
        $summary.temperature_first_c = $firstTemp
        $summary.temperature_max_c = $maxTemp
        $summary.temperature_rise_c = [Math]::Round($maxTemp - $firstTemp, 2)
    }
}

if (Test-Path -LiteralPath $dynoCsv) {
    $dynoRows = Import-Csv -LiteralPath $dynoCsv
    if ($dynoRows.Count -gt 0) {
        $summary.dyno_rows = $dynoRows.Count
        $summary.dyno_max_rpm = ($dynoRows | Measure-Object -Property rpm -Maximum).Maximum
        $summary.dyno_max_power_w = ($dynoRows | Measure-Object -Property power_w -Maximum).Maximum
        $summary.dyno_max_inst_torque_nm = ($dynoRows | Measure-Object -Property inst_torque_nm -Maximum).Maximum
        $summary.dyno_max_torque_from_power_nm = ($dynoRows | Measure-Object -Property torque_from_power_nm -Maximum).Maximum
        $summary.dyno_max_wheel_revs = ($dynoRows | Measure-Object -Property wheel_revs -Maximum).Maximum
    }
}

$summary.requirement_checks = [ordered]@{
    r06_peak_torque_possible_from_current = ($summary.est_output_torque_at_max_iq_nm -ge 16.0)
    r07_continuous_current_cap_below_90pct_math = ($ContinuousCurrentCapA -lt (12.0 / ($GearRatio * $TargetEfficiency * $TorqueConstantNmPerA)))
    r08_thermal_motor_temp_ok = ($null -eq $summary.temperature_max_c -or $summary.temperature_max_c -lt $MaxMotorTempC)
    r08_thermal_fet_temp_ok = ($null -eq $summary.motor_max_fet_c -or $summary.motor_max_fet_c -lt $MaxFetTempC)
    r11_speed_met_from_encoder = ($summary.est_output_rpm_at_max_encoder_vel -ge 600.0)
}

$finalStatus = "completed"
if (
    ($null -ne $motorExitCode -and $motorExitCode -ne 0) -or
    ($null -ne $dynoExitCode -and $dynoExitCode -ne 0) -or
    ($null -ne $tempExitCode -and $tempExitCode -ne 0) -or
    $abortReason
) {
    $finalStatus = "failed"
}

Write-Manifest $finalStatus @{
    starts = [ordered]@{
        temperature = $tempStart.ToString("o")
        dyno = $dynoStart.ToString("o")
        motor = $motorStart.ToString("o")
    }
    summary = $summary
}

Write-Output "RUN_DIR=$runDir"
Write-Output "MANIFEST=$manifestPath"
$summary.GetEnumerator() | ForEach-Object { Write-Output "$($_.Key)=$($_.Value)" }
