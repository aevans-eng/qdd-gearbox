# MKS XDrive Mini Sprint Folder

This folder is the **single place to use during the test sprint** for the replacement motor controller.

It assumes the new board is an **MKS XDrive / MKS ODrive Mini** class controller that is broadly compatible with the legacy ODrive Python/native-protocol stack.

## Use Order

1. `00-verify-stack.ps1`
2. `01-probe-board.ps1`
3. `10-agent-control.ps1` for agent-driven commands
4. `02-open-session-panel.ps1` only if a human wants a GUI

Only use the old large GUI if you explicitly need something from it.

## Files

- `README.md`
  - quick sprint workflow
- `STACK.md`
  - detailed control-stack notes, electronics defaults, and architecture decisions
- `BARE-MOTOR-SETUP.md`
  - bare-motor bring-up workflow and first-spin helper notes
- `requirements.txt`
  - pinned local Python requirements for this sprint
- `odrive_probe.py`
  - CLI probe for USB/native-protocol bring-up
- `odrive-session-panel.py`
  - compact GUI for connect / calibrate / closed-loop / velocity / torque / position
- `mks_agent_control.py`
  - self-contained agent-safe CLI for Codex / Claude driven control
- `xdrive_first_spin.py`
  - lower-level first-spin helper retained for bare-motor bring-up
- `00-verify-stack.ps1`
  - checks Python path, imports, package versions, and key files
- `01-probe-board.ps1`
  - runs the probe with safe defaults and saves JSON output
- `02-open-session-panel.ps1`
  - launches the compact session GUI
- `03-open-zadig.ps1`
  - opens Zadig if the WinUSB/native driver still needs to be installed
- `10-agent-control.ps1`
  - passes arguments through to `mks_agent_control.py`
- `11-safe-smoke-test.ps1`
  - one-command minimal bring-up and tiny motion test
- `SESSION-CHECKLIST.md`
  - one-page session order and hard rules

## Sprint Defaults

- Python: local `.venv-odrive051\Scripts\python.exe` via `mks-python-env.ps1`
- ODrive package: `odrive==0.5.1.post0`
- USB backend: `libusb-package` DLL exposed automatically by the wrappers
- Board profile: `gearbox`
- Gear ratio: `5:1`
- Motor current limit: `10 A`
- Watchdog timeout: `0.5 s`

These are conservative defaults for bring-up. Tune later only after stable motion.

## First Session

### 1. Verify the software stack

Run:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\00-verify-stack.ps1
```

Expected:

- Python found
- `odrive` import works
- `bleak` import works
- `matplotlib` import works
- required files present

### 2. If the board is not recognized by Python yet

Run:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\03-open-zadig.ps1
```

Then install the WinUSB driver for the board's **native interface** if it enumerates as an ODrive-style USB device.

### 3. Probe the board first

Run:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\01-probe-board.ps1
```

This:

- looks for an ODrive-compatible device
- applies the safe gearbox profile
- prints the key board/motor values
- saves a JSON summary into:
  - `qdd-gearbox/testing/data/motor-controller-probe.json`

Do **not** skip this on the first successful connection.

### 4. Preferred: let Codex / Claude drive it through the agent CLI

Run:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 status
```

Examples:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 calibrate
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 velocity --rpm 30 --seconds 2
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 torque --nm 1.0 --seconds 1
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 position --deg 90
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 idle
```

Important:

- motion commands are self-contained and auto-safe
- they connect, apply the safe profile, enter closed loop, execute, zero, and return to idle
- that is the main reason this is safer for an AI-controlled sprint workflow
- only run one USB/native-protocol client at a time
- for bare-motor bring-up, override the gearbox defaults:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 --profile bare --ratio 1 status
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 --profile bare --ratio 1 calibrate
PowerShell -ExecutionPolicy Bypass -File .\10-agent-control.ps1 --profile bare --ratio 1 velocity --rpm 6 --seconds 1 --calibrate
```

### 4B. One-command smoke test

Run:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\11-safe-smoke-test.ps1
```

This is the fastest way to answer:

- does the board connect?
- can it calibrate?
- can it execute a tiny safe motion?
- does it return to idle?

### 5. Optional: open the session GUI

Run:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\02-open-session-panel.ps1
```

Use the GUI for:

- connect
- calibrate
- enter closed loop
- idle / e-stop
- manual velocity / torque / position commands

## Fast Rules

- Probe first, GUI second
- For AI-driven control, prefer `10-agent-control.ps1`
- One USB/native-protocol client at a time
- Stay on conservative current and voltage limits during bring-up
- If anything feels wrong, go idle and cut DC power
- Real hardware evidence matters more than fancy software during this sprint

## Notes About The Package Version

The docs in the repo sometimes mention `odrive==0.5.5`, but that version is not available on PyPI.

For this sprint, the working Python stack is:

- `odrive==0.5.1.post0`
- `libusb-package`

`odrive==0.5.4` enumerated the board in Windows but did not complete a reliable native-protocol handshake on this MKS Mini.
