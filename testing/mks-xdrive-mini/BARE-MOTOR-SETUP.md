# MKS XDrive Mini + D6374 Bare-Motor Bring-Up

> Purpose: get the `D6374 150KV` spinning safely on the `MKS XDrive Mini v1`, then connect that bench setup to the `Hammer H2` trainer for dyno work.

## What Changed

The old QDD hardware notes were written around the larger ODrive 3.6 board. The current controller is the smaller `MKS XDrive Mini v1`, which is ODrive-like but not a drop-in "upgrade firmware and forget it" board.

Key implications:

- Treat the board as legacy ODrive `v0.5.1` hardware
- Do not use generic `odrivetool upgrade`
- Do first bring-up over USB, not CAN
- Ignore multi-axis CAN quirks until the motor spins reliably on `axis0`

## Bench Plan

1. Bring up the XDrive Mini on USB only
2. Confirm encoder feedback is sane
3. Spin the bare motor at low speed
4. Add the H2 data path separately
5. Couple motor to trainer only after both sides work independently

## Hardware Needed

- `MKS XDrive Mini v1`
- `D6374 150KV` motor
- encoder path:
  - preferred: AS5047 SPI encoder path if you have the Makerbase-compatible encoder board and magnet setup
  - fallback: incremental A/B/Z encoder with known CPR
- current-limited DC supply
- brake resistor
- USB-C data cable for the XDrive Mini
- rigid motor fixture
- emergency power kill within arm's reach

## Encoder Reality Check

You need a real encoder before this becomes a servo test.

Current confirmed encoder for this bench:

- `CUI AMT 102-V`
- treat it as an incremental encoder path
- default working assumption: `8192 CPR`

- The XDrive Mini schematic shows support for an `AS5047` SPI encoder path and also an incremental encoder header.
- The community config you linked assumes:
  - `ENCODER_MODE_SPI_ABS_AMS`
  - `abs_spi_cs_gpio_pin = 7`
  - `cpr = 16384`
- If your D6374 does not currently have a mounted encoder and magnet, stop there first. No encoder means no normal ODrive-style closed-loop bring-up.

## Software Recommendation

Use a dedicated Python environment for the XDrive Mini so you do not mix it with the older ODrive 3.6 tooling.

```powershell
Set-Location C:\Users\aaron\Documents\c-projects\qdd-gearbox\testing\mks-xdrive-mini
C:\Users\aaron\miniconda3\python.exe -m venv .venv-odrive051
.venv-odrive051\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install odrive==0.5.1.post0 libusb-package bleak matplotlib
```

Reason:

- the community guide explicitly targets `odrive==0.5.1.post0`
- the XDrive Mini ships with Makerbase-modified `v0.5.1` firmware
- newer generic firmware and tooling may connect poorly or brick the board if you start "upgrading"
- on Windows, `libusb-package` is needed so PyUSB has a backend for the native interface

In this workspace, the sprint wrappers already handle this through:

- `testing/mks-xdrive-mini/mks-python-env.ps1`

## Firmware Rules

- Keep the board on the Makerbase `v0.5.1` family firmware unless you intentionally reflash with `ST-Link`
- Do not run `odrivetool dfu`, `upgrade`, or generic ODrive firmware update flow
- If the board gets bricked, recover with `ST-Link V2` and the Makerbase dump, not stock ODrive binaries

Makerbase's own repo currently includes:

- `MKS_ODrive_MINI_0_5_1_20250326.bin`
- `MKS ODRIVE MINI V1.0 Schematic.pdf`
- a note stating the Mini needs source modifications beyond plain ODrive v3.6 code

## Wiring Notes

Minimum bench wiring:

- DC supply to board power input
- brake resistor connected
- three motor phases connected to `axis0` motor output
- encoder connected and secured
- USB connected to laptop

Treat the board like classic ODrive hardware here:

- correct polarity matters
- loose motor leads will create garbage behavior fast
- bench supplies usually do not safely absorb regen, so keep the brake resistor installed

## First Bring-Up

### 1. Confirm USB connection

```powershell
.venvs\xdrive-mini\Scripts\Activate.ps1
python -c "import odrive; odrv0 = odrive.find_any(timeout=10); print(odrv0.serial_number)"
```

If this does not enumerate, solve USB/driver issues before touching motor config.

### 2. Read current firmware/config state

```python
import odrive
odrv0 = odrive.find_any(timeout=10)

print(odrv0.vbus_voltage)
print(odrv0.axis0.current_state)
print(odrv0.axis0.error)
print(odrv0.axis0.motor.error)
print(odrv0.axis0.encoder.error)
```

### 3. Only erase config if you intentionally want a clean start

The community config begins with `erase_configuration()`. That is fine for a deliberate fresh setup, but it is not a casual first command.

### 4. Set the bare minimum motor parameters

Start from the linked community flow, but replace the motor-specific values with your hardware:

```python
odrv0.config.brake_resistance = 2.0
odrv0.config.dc_bus_undervoltage_trip_level = 8.0
odrv0.config.dc_bus_overvoltage_trip_level = 56.0
odrv0.config.dc_max_positive_current = 20.0
odrv0.config.dc_max_negative_current = -3.0
odrv0.config.max_regen_current = 0

odrv0.axis0.motor.config.pole_pairs = 7
odrv0.axis0.motor.config.calibration_current = 5
odrv0.axis0.motor.config.resistance_calib_max_voltage = 2
odrv0.axis0.motor.config.motor_type = MOTOR_TYPE_HIGH_CURRENT
odrv0.axis0.motor.config.current_lim = 10
odrv0.axis0.motor.config.requested_current_range = 20
```

Notes:

- `pole_pairs = 7` matches the existing QDD D6374 notes
- keep `current_lim` conservative at first
- if the motor fails to calibrate, do not just keep increasing current blindly

### 5. Set encoder mode correctly

If using the AS5047 SPI path:

```python
odrv0.axis0.encoder.config.mode = ENCODER_MODE_SPI_ABS_AMS
odrv0.axis0.encoder.config.abs_spi_cs_gpio_pin = 7
odrv0.axis0.encoder.config.cpr = 16384
odrv0.axis0.encoder.config.bandwidth = 3000
odrv0.axis0.encoder.config.calib_range = 10
```

If using an incremental encoder instead, do not copy the SPI settings. Set:

- incremental mode
- correct CPR for the encoder you actually mounted

### 6. Save, reboot, calibrate

```python
odrv0.save_configuration()
odrv0.reboot()
```

Reconnect, then:

```python
odrv0.axis0.requested_state = AXIS_STATE_MOTOR_CALIBRATION
```

After that passes cleanly, run the encoder calibration path appropriate to your encoder setup.

### 7. First motion command

Do not jump straight to aggressive position control. Start in velocity mode at a very low speed.

```python
odrv0.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
odrv0.axis0.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL
odrv0.axis0.controller.input_vel = 0.5
```

If the motor behaves correctly:

- stop
- inspect temperatures, sounds, and errors
- then increase speed in small steps

## CAN Notes

Ignore CAN until USB bring-up is done.

When you do move to CAN:

- set `axis0` to the node ID you want
- move the ghost `axis1` to `63`

```python
odrv0.axis0.config.can_node_id = 0
odrv0.axis1.config.can_node_id = 63
odrv0.can.set_baud_rate(500000)
```

This only matters for CAN. It is not needed for simple USB bench testing.

## Hammer H2 Data Path

The H2 should be treated as a second subsystem. Keep the split clear:

- hardware/test concept: `testing/dyno/README.md`
- executable BLE capture tool: `testing/dyno/ble-capture/`

Validate it independently first:

```powershell
Set-Location C:\Users\aaron\Documents\c-projects\qdd-gearbox\testing\\dyno\\ble-capture
C:\Users\aaron\miniconda3\python.exe dyno.py scan
C:\Users\aaron\miniconda3\python.exe dyno.py capture --duration 20 --output runs\smoke_h2.csv
```

Important:

- your local H2 tooling uses BLE Cycling Power Service, not FTMS
- BLE notifications are about `~1.1 Hz`, so use trainer data for steady-state dyno work, not fast transients
- the trainer freehub is one-way, so the loaded dyno direction matters

## Recommended Bench Sequence

1. XDrive Mini + motor + encoder only
2. H2 BLE scan/capture only
3. print/test freehub adapter
4. couple bare motor to trainer
5. run a no-load spin with the trainer mechanically connected but electrically passive
6. run low-speed, low-current dyno capture

## Helper Script

There is now a dedicated first-spin helper at:

- `testing/mks-xdrive-mini/xdrive_first_spin.py`

Example for an AMT-102 style incremental encoder:

```powershell
& "C:\Users\aaron\Documents\c-projects\qdd-gearbox\testing\mks-xdrive-mini\.venv-odrive051\Scripts\python.exe" `
  "C:\Users\aaron\Documents\c-projects\qdd-gearbox\testing\mks-xdrive-mini\xdrive_first_spin.py" `
  --configure `
  --profile bare `
  --encoder incremental `
  --cpr 8192 `
  --calibrate full `
  --spin `
  --velocity-tps 0.5 `
  --spin-duration 3
```

Example for an AS5047 SPI encoder path:

```powershell
& "C:\Users\aaron\Documents\c-projects\qdd-gearbox\testing\mks-xdrive-mini\.venv-odrive051\Scripts\python.exe" `
  "C:\Users\aaron\Documents\c-projects\qdd-gearbox\testing\mks-xdrive-mini\xdrive_first_spin.py" `
  --configure `
  --profile bare `
  --encoder spi_ams `
  --cpr 16384 `
  --abs-spi-cs-gpio-pin 7 `
  --calibrate full `
  --spin `
  --velocity-tps 0.5 `
  --spin-duration 3
```

## Immediate Unknowns To Close

- Do you already have the Makerbase-compatible AS5047 board and magnet, or are you using another encoder?
- What DC supply and brake resistor are you using with the XDrive Mini?
- Do you want USB-only bench control first, or are you planning to go straight to CAN + Arduino/ESP32?

## Sources

- Hackaday project: [MKS XDrive Mini Guide: Set up, Tuning & Arduino](https://hackaday.io/project/204985-mks-xdrive-mini-guide-set-up-tuning-arduino)
- Community repo: [justlovescience/MKS-XDRIVE-MINI](https://github.com/justlovescience/MKS-XDRIVE-MINI)
- Makerbase firmware/schematic repo: `C:\Users\aaron\Documents\c-projects\.tmp\mks-odrive`
- H2 local tooling: `C:\Users\aaron\Documents\c-projects\saris-h2-dyno`
