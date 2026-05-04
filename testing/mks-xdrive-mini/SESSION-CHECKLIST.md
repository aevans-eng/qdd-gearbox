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

## Synced Dyno Runs

For a synced motor + Hammer + temperature run, use the wrappers from `testing/`:

```powershell
cd ..\..\testing
.\run_official_requirement_test.ps1 -TestStage PreflightDirection
.\run_official_requirement_test.ps1 -TestStage BareBaseline -Series
.\run_official_requirement_test.ps1 -TestStage GearboxEfficiency -Series
```

These call `run_synced_motor_dyno_temp.ps1` which orchestrates `safe_ramp_test.py` / `safe_torque_ramp_test.py` (motor), `dyno.py` (Hammer BLE), and `log_thermistor.py` (Arduino). Output is one timestamped folder per run with motor.log, dyno.csv, temperature.csv, manifest.json.

Operating procedures, direction constraints, and recovery: [`testing/OFFICIAL-DYNO-TESTING.md`](../OFFICIAL-DYNO-TESTING.md).

## After A Failed Run

The synced scripts print diagnostic information that's the first place to look:

1. **`motor.log` post-clear printout** — `after clear: err axis=N motor=N enc=N ctrl=N`. If anything is nonzero here, the run will probably fail to enter `CLOSED_LOOP`.
2. **`motor.log` in-loop disarm message** — if the controller silently dropped to IDLE during the run, the script logs `disarm_reason`, `active_errors`, and per-subobject errors at the moment of disarm, then aborts cleanly.
3. **Manifest `motor_exit_code` and `dyno_exit_code`** — authoritative. Nonzero = real failure even if status reads "completed".

If sticky errors persist after the script's automatic clear sequence: **power-cycle the PSU** (off, count to 5, on). Sticky bits seen this session: axis `48`, `16`, `2048`; motor `32768`. Software clear can't always reset these without a controller power cycle.
