param(
    [ValidateSet("PreflightDirection", "BareBaseline", "GearboxEfficiency", "ContinuousTorque", "PeakTorque", "Speed")]
    [string]$TestStage,
    [double]$DriveSign = 1.0,
    [switch]$Series,
    [double]$CurrentLimitA = 0.0,
    [double]$TargetTorqueNm = 0.0,
    [double]$TargetVelocityTps = 0.0,
    [string]$TempPort = "COM6",
    [int]$TempBaud = 115200,
    [bool]$FanInstalled = $true,
    [double]$PsuVoltageV = 24.0,
    [double]$PsuCurrentLimitA = 10.0,
    [double]$PsuOvpV = 30.0,
    [double]$PsuOcpA = 10.0
)

$ErrorActionPreference = "Stop"

$synced = Join-Path $PSScriptRoot "run_synced_motor_dyno_temp.ps1"
$kt = 0.04
$gearRatio = 5.0
$targetEfficiency = 0.90
$continuousCap = 60.0
$peakCap = 90.0

function Invoke-SyncedRun($ArgsTable) {
    & $synced @ArgsTable
}

function CommonArgs($Stage, $Setup, $Label) {
    return @{
        Label = $Label
        TestStage = $Stage
        HardwareSetup = $Setup
        FanInstalled = $FanInstalled
        TempPort = $TempPort
        TempBaud = $TempBaud
        MaxMotorTempC = 50.0
        MaxFetTempC = 70.0
        GearRatio = $gearRatio
        TorqueConstantNmPerA = $kt
        TargetEfficiency = $targetEfficiency
        ContinuousCurrentCapA = $continuousCap
        PeakCurrentCapA = $peakCap
        PsuVoltageV = $PsuVoltageV
        PsuCurrentLimitA = $PsuCurrentLimitA
        PsuOvpV = $PsuOvpV
        PsuOcpA = $PsuOcpA
    }
}

$sign = if ($DriveSign -lt 0) { -1.0 } else { 1.0 }

switch ($TestStage) {
    "PreflightDirection" {
        $current = if ($CurrentLimitA -gt 0) { $CurrentLimitA } else { 5.0 }
        $torque = if ($TargetTorqueNm -ne 0) { $TargetTorqueNm } else { $sign * 0.08 }
        $args = CommonArgs "preflight_direction" "unknown" "official-preflight-direction"
        $args += @{
            Mode = "torque"
            TargetTorqueNm = $torque
            RampSeconds = 30.0
            HoldSeconds = 1.5
            CurrentLimitA = $current
            StopOnVelocityTps = 0.25
            RampdownSeconds = 0.0
            MotorDtSeconds = 0.25
            CaptureSeconds = 75.0
        }
        Invoke-SyncedRun $args
    }
    "BareBaseline" {
        $points = if ($Series) { @(20.0, 40.0, 60.0) } elseif ($CurrentLimitA -gt 0) { @($CurrentLimitA) } else { @(30.0) }
        foreach ($current in $points) {
            $torque = if ($TargetTorqueNm -ne 0) { $TargetTorqueNm } else { $sign * $current * $kt }
            $args = CommonArgs "bare_baseline" "bare_motor" "official-bare-baseline-${current}a"
            $args += @{
                Mode = "torque"
                TargetTorqueNm = $torque
                RampSeconds = 120.0
                HoldSeconds = 8.0
                CurrentLimitA = $current
                StopOnVelocityTps = 8.0
                RampdownSeconds = 0.0
                MotorDtSeconds = 0.5
                CaptureSeconds = 180.0
            }
            Invoke-SyncedRun $args
        }
    }
    "GearboxEfficiency" {
        $points = if ($Series) { @(20.0, 40.0, 60.0) } elseif ($CurrentLimitA -gt 0) { @($CurrentLimitA) } else { @(30.0) }
        foreach ($current in $points) {
            $torque = if ($TargetTorqueNm -ne 0) { $TargetTorqueNm } else { $sign * $current * $kt }
            $args = CommonArgs "gearbox_efficiency" "gearbox_installed" "official-gearbox-efficiency-${current}a"
            $args += @{
                Mode = "torque"
                TargetTorqueNm = $torque
                RampSeconds = 120.0
                HoldSeconds = 8.0
                CurrentLimitA = $current
                StopOnVelocityTps = 8.0
                RampdownSeconds = 0.0
                MotorDtSeconds = 0.5
                CaptureSeconds = 180.0
            }
            Invoke-SyncedRun $args
        }
    }
    "ContinuousTorque" {
        $current = if ($CurrentLimitA -gt 0) { [Math]::Min($CurrentLimitA, $continuousCap) } else { $continuousCap }
        $torque = if ($TargetTorqueNm -ne 0) { $TargetTorqueNm } else { $sign * $current * $kt }
        $args = CommonArgs "continuous_torque" "gearbox_installed" "official-continuous-torque-${current}a"
        $args += @{
            Mode = "torque"
            TargetTorqueNm = $torque
            RampSeconds = 180.0
            HoldSeconds = 300.0
            CurrentLimitA = $current
            StopOnVelocityTps = 20.0
            RampdownSeconds = 0.0
            MotorDtSeconds = 0.5
            CaptureSeconds = 540.0
        }
        Invoke-SyncedRun $args
    }
    "PeakTorque" {
        $current = if ($CurrentLimitA -gt 0) { [Math]::Min($CurrentLimitA, $peakCap) } else { $peakCap }
        $requiredPeakMotorTorque = 16.0 / ($gearRatio * $targetEfficiency)
        $torque = if ($TargetTorqueNm -ne 0) { $TargetTorqueNm } else { $sign * [Math]::Min($current * $kt, $requiredPeakMotorTorque) }
        $args = CommonArgs "peak_torque" "gearbox_installed" "official-peak-torque-${current}a"
        $args += @{
            Mode = "torque"
            TargetTorqueNm = $torque
            RampSeconds = 150.0
            HoldSeconds = 2.0
            CurrentLimitA = $current
            StopOnVelocityTps = 20.0
            RampdownSeconds = 0.0
            MotorDtSeconds = 0.25
            CaptureSeconds = 210.0
        }
        Invoke-SyncedRun $args
    }
    "Speed" {
        $current = if ($CurrentLimitA -gt 0) { $CurrentLimitA } else { 30.0 }
        $target = if ($TargetVelocityTps -ne 0) { $TargetVelocityTps } else { $sign * (600.0 * $gearRatio / 60.0) }
        $args = CommonArgs "speed" "gearbox_installed" "official-speed-600rpm"
        $args += @{
            Mode = "velocity"
            TargetVelocityTps = $target
            VelocityRampRateTps2 = 0.5
            HoldSeconds = 60.0
            CurrentLimitA = $current
            StopOnVelocityTps = 55.0
            MotorDtSeconds = 0.5
            CaptureSeconds = 180.0
        }
        Invoke-SyncedRun $args
    }
}
