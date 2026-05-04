# MKS XDrive Mini Control Stack

> Canonical stack for motor bring-up and testing after the original ODrive 3.6 failed.

## Board Assumption

This document assumes the replacement controller is an **MKS XDrive / MKS ODrive Mini** class board derived from the legacy ODrive 3.6 ecosystem.

Why this is the working assumption:

- the provided listing matches the MKS XDrive Mini family
- Makerbase maintains an `ODrive-MKS` repository for these boards
- the board is commonly sold as an ODrive-style controller rather than as a new standalone software ecosystem

Implication:

- the safest control path is still the legacy `odrive` Python/native-protocol stack
- do not assume modern ODrive Pro / S1 docs apply directly
- do not assume the board behaves exactly like genuine ODrive hardware in every edge case

## Chosen Architecture

Use a **hybrid** workflow:

### 1. CLI probe and setup

Use CLI first for:

- first connection
- driver / protocol troubleshooting
- firmware / hardware summary
- safe profile application
- verifying motor parameters after calibration

Tool:

- `testing/mks-xdrive-mini/odrive_probe.py`

### 2. Compact GUI for manual control

Use a small GUI for:

- connect
- calibrate
- closed-loop entry
- idle / e-stop
- manual velocity / torque / position commands
- live telemetry

Tool:

- `testing/mks-xdrive-mini/odrive-session-panel.py`

### 2B. Agent-safe CLI for Codex / Claude control

Use the CLI for:

- status checks
- calibration
- short self-contained velocity / torque / position commands
- shell-driven control without relying on manual GUI interaction

Tool:

- `testing/mks-xdrive-mini/mks_agent_control.py`

### 3. Separate automation for scripted testing

Use standalone scripts, not the GUI, for:

- dyno capture
- repeatable sweeps
- logging-heavy tests

Relevant tools:

- `testing/dyno/ble-capture/`
- future dedicated scripted ODrive tests

## Why Hybrid Is Better Than GUI-Only

The older all-in-one GUI was too big and too stateful. That makes it fragile for a legacy ODrive-compatible board.

GUI-only is a bad fit because:

- first-connect failures are easier to diagnose in CLI
- firmware/USB issues need direct visibility
- one broken widget can make the whole session feel unreliable
- scripted dyno work should not depend on a manual GUI loop

CLI-only is also not ideal because:

- it is slower for repeated manual bench commands
- it increases operator friction during bring-up

So the best split is:

- CLI for truth and troubleshooting
- agent-safe CLI for shell-driven motion commands
- GUI for manual operation
- scripts for repeatable tests

## Local Software Stack

Current verified local stack:

- Python: `testing/mks-xdrive-mini/.venv-odrive051/Scripts/python.exe`
- `odrive`: `0.5.1.post0`
- `libusb-package`: required for PyUSB backend on Windows in this env
- `bleak`: installed
- `matplotlib`: installed
- Zadig driver utility present:
  - `testing/hardware/zadig-2.9.exe`

Important note:

- `odrive==0.5.5` is referenced in some older notes, but it is **not available on PyPI**
- `odrive==0.5.4` did not complete a reliable native-protocol handshake with the current MKS Mini firmware
- the practical pinned package for this workspace is therefore `odrive==0.5.1.post0`
- the local wrappers add the `libusb-package` DLL path automatically so PyUSB can open the native interface

Requirements file:

- `testing/mks-xdrive-mini/requirements.txt`

## Native USB / Driver Stack

Windows path:

1. connect controller over USB data cable
2. use Zadig
3. select the board's **native interface** if it enumerates as an ODrive-style device
4. install **WinUSB**
5. use `odrive.find_any()` from Python

If the device does not enumerate as an ODrive native interface:

- do not waste time fighting the GUI
- confirm USB cable is data-capable
- confirm board power is present
- confirm the board is actually exposing the legacy ODrive native protocol

## Bench Electronics Stack

Expected stack:

- controller: MKS XDrive Mini / ODrive-compatible board
- motor: D6374 150KV BLDC
- encoder: AMT-102 style incremental encoder
- brake resistor: required if the board supports / expects the same braking path
- DC supply: current-limited bring-up first
- optional dyno load: Saris H2 trainer

## Session Default Electrical Limits

Start conservative:

- supply voltage: `48 V`
- supply current limit: `5 A` first bring-up, then `10 A`
- motor `current_lim`: `10 A`
- watchdog timeout: `0.5 s`

These are default working limits, not claims about the absolute board capability.

## Default Control Profiles

### Bare motor

- `pos_gain = 5.0`
- `vel_gain = 0.05`
- `vel_integrator_gain = 0.05`
- `vel_ramp_rate = 3.0`

### 5:1 gearbox attached

- `pos_gain = 15.0`
- `vel_gain = 0.10`
- `vel_integrator_gain = 0.20`
- `vel_ramp_rate = 10.0`

These are session defaults, not universal truth. If the MKS clone behaves differently, tune from these, do not jump far.

## Units Convention

All operator-facing commands in the compact GUI are in **output shaft units**:

- velocity: RPM
- torque: Nm
- position: degrees

Internally the board still sees **motor-side units**:

- velocity: turns/s
- torque: motor Nm
- position: motor turns

For the 5:1 gearbox:

- `motor_torque = output_torque / 5`
- `motor_tps = output_rpm * 5 / 60`
- `motor_turns = output_deg * 5 / 360`

## Recommended Operating Flow

### First connection / board uncertainty

1. wire the system safely
2. run the probe
3. confirm bus voltage, errors, motor params, and watchdog support
4. apply the correct safe profile
5. only then open the GUI

Command:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\01-probe-board.ps1
```

### Manual bench operation

Open the compact session GUI:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\02-open-session-panel.ps1
```

### Dyno / scripted work

Do not depend on the GUI for repeatable dyno tests.

Use scripts instead:

- the controller side should be scripted from Python
- the trainer side should be handled by the Saris H2 tooling

Remember:

- only one ODrive USB/native-protocol connection at a time

## Known Clone-Specific Quirks

- For this board, set control mode before requesting `CLOSED_LOOP_CONTROL`
- Do not leave the watchdog enabled during probe/status/calibration-only flows
- Clear stale controller faults before diagnosing a fresh command result

## Tool Roles

### `odrive_probe.py`

Purpose:

- connect
- summarize board identity
- summarize motor config
- apply safe defaults
- save a JSON summary if needed

### `odrive-session-panel.py`

Purpose:

- compact manual session control
- explicit commands
- live telemetry
- less clunky than the old panel

### Legacy GUI

Legacy file:

- `testing/_archive/tool-overlap-cleanup-2026-05-03/odrive-control-panel.py`

Status:

- keep for reference
- do not treat as the primary bring-up tool anymore

## Settings Checklist To Record For The New Board

Once the MKS board is physically in hand and connected, record:

- exact product name from silkscreen
- USB device name
- firmware version reported by the `odrive` object
- hardware version fields, if exposed
- bus voltage limits actually used
- brake resistor config
- motor phase resistance / inductance after calibration
- working gains for bare motor
- working gains for gearbox
- any clone-specific quirks

Save the first successful probe JSON in:

- `testing/data/motor-controller-probe.json`

## Known Risk

The biggest risk is not missing Python packages.

The biggest risk is assuming full ODrive 3.6 behavior from a clone board without probing it first.

That is why the stack is probe-first, GUI-second.
