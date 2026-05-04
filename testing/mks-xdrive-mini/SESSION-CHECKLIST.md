# MKS Session Checklist

Use this in order during the sprint.

## Before Power

- DC polarity confirmed
- brake resistor connected
- motor phases tight
- motor physically secured
- encoder coupling tight
- USB data cable connected
- nothing can catch the rotor
- supply current limit set conservative

## Software Bring-Up

1. Run `00-verify-stack.ps1`
2. If driver issue: run `03-open-zadig.ps1`
3. Run `01-probe-board.ps1`
4. Check:
   - bus voltage is sane
   - no errors
   - phase resistance / inductance look sane
   - watchdog did not throw errors

## First Motion

1. Run `11-safe-smoke-test.ps1`
2. Confirm:
   - calibration completes
   - small motion is clean
   - command returns to idle

If anything is odd:

- stop using motion commands
- rerun probe
- inspect wiring / encoder / board USB path

## During Testing

- prefer `10-agent-control.ps1` for shell-driven commands
- use the GUI only if a human wants manual operation
- keep only one ODrive-compatible USB client open at a time
- after each risky step, return to `idle`

## Suggested Safe Command Set

```powershell
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 status
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 calibrate
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 velocity --rpm 10 --seconds 1
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 position --deg 45
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 torque --nm 0.5 --seconds 1
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 idle
```

## Hard Rules

- do not jump straight to large torque or speed
- do not leave the axis in closed loop unattended
- do not assume the clone board behaves exactly like the old ODrive
- if communication goes weird, go electrical-safe first, software second
