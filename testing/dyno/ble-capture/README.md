# saris-h2-dyno

BLE-based dynamometer capture tool for the **Saris Hammer H2** bike trainer. Connects via Bluetooth, logs power/torque/RPM at ~1.1 Hz, and generates dyno curves.

Built to repurpose the H2 as a motor dynamometer for small-medium electric motors (e.g., ODrive D6374).

**Folder boundary:** this folder is only the executable BLE capture/control tool. Hardware assumptions, trainer limitations, adapter design notes, and test interpretation live in `testing/dyno/README.md`.

## Features

- **BLE data capture** via Cycling Power Service (0x1818) with live terminal output
- **12 data channels**: power, torque (2 derivation methods), RPM, angular velocity, angular acceleration, wheel/crank revolutions
- **6-panel dyno plots**: power, RPM, torque time history, classic dyno curve (T & P vs RPM), angular acceleration, accumulated torque
- **CSV output** for post-processing
- **Resistance control** (experimental, untested): ERG mode (constant watts) and SIM mode (simulated grade)

## Quick Start

```bash
pip install bleak matplotlib

# Capture 60 seconds of data
python dyno.py capture --duration 60 --output runs/my_run.csv

# Plot an existing capture
python dyno.py plot runs/run_001.csv --save

# Scan for the trainer
python dyno.py scan
```

## CLI Reference

```
python dyno.py capture [-d DURATION] [-o OUTPUT] [--addr ADDR] [--no-plot] [-q]
python dyno.py plot <csv_path> [--save]
python dyno.py scan [-t TIMEOUT]
```

| Flag | Description |
|------|-------------|
| `-d`, `--duration` | Capture time in seconds (default: 60) |
| `-o`, `--output` | Output CSV path (default: `runs/run_001.csv`) |
| `--addr` | BLE address override (default: auto-detect known H2) |
| `--no-plot` | Skip plot generation after capture |
| `-q`, `--quiet` | Suppress live sample output |
| `-s`, `--save` | Save plot as PNG alongside CSV |
| `-t`, `--timeout` | BLE scan timeout in seconds (default: 5) |

## Data Channels

| Channel | Source | Notes |
|---------|--------|-------|
| `power_w` | CPS direct | Instantaneous power (W) |
| `acc_torque_nm` | CPS direct | Cumulative torque at 1/32 Nm resolution |
| `wheel_revs` | CPS direct | Cumulative flywheel revolution count |
| `wheel_event_time` | CPS direct | High-res timing at 1/2048 s |
| `crank_revs` | CPS direct | Cumulative crank count (0 when not pedaling) |
| `crank_event_time` | CPS direct | Crank timing at 1/1024 s |
| `rpm` | Derived | delta(revs) / delta(time) * 60 |
| `omega_rad_s` | Derived | RPM * 2pi/60 |
| `inst_torque_nm` | Derived | delta(acc_torque) / delta(revs) * 2pi |
| `torque_from_power_nm` | Derived | P / omega (cross-check) |
| `alpha_rad_s2` | Derived | delta(omega) / delta(t) |

## Device Info

| Field | Value |
|-------|-------|
| Model | Saris Hammer H2 (Model 320) |
| MAC | `EE:51:A8:51:70:1A` |
| Protocol | Cycling Power Service (0x1818), **not** FTMS |
| Notification rate | ~1.1 Hz (firmware-locked) |
| Max power | 2000W @ 40 km/h |
| Accuracy | +/- 2% |
| Brake type | Electromagnetic eddy current |
| Flywheel | 20 lbs (9 kg) |

## BLE Protocol Notes

The H2 does **not** use the standard FTMS (0x1826) profile. It exposes:

| Service | UUID | Purpose |
|---------|------|---------|
| Cycling Power | `0x1818` | Power, torque, revs (read) |
| Saris Proprietary | `c0f4013a-...` | Resistance control (write) |
| Device Information | `0x180A` | Model, firmware, serial |

### Resistance Control (Untested)

Write 10-byte commands to characteristic `ca31a533-a858-4dc7-a650-fdeb6dad4c14`:

```
[0x00] [0x10] [mode] [param_lo] [param_hi] [0x00] [0x00] [0x00] [0x00] [0x00]

Modes:
  0x01 = ManualPower (ERG) -- target watts
  0x02 = ManualSlope (SIM) -- grade * 100 (500 = 5.0%)

Timing: 3s between commands, 4-5s for brake engagement
```

Protocol source: [qdomyos-zwift](https://github.com/cagnulein/qdomyos-zwift/blob/master/src/devices/cycleopsphantombike/cycleopsphantombike.cpp)

## Project Structure

```
saris-h2-dyno/
├── dyno.py              # CLI entry point
├── saris_h2/
│   ├── __init__.py
│   ├── protocol.py      # BLE constants, CPS parser, resistance commands
│   ├── capture.py       # Async BLE session + CSV output
│   ├── control.py       # Resistance control (untested)
│   └── plot.py          # 6-panel matplotlib visualization
├── runs/                # Captured data
│   └── run_001.csv      # First test (hand spin, 2026-03-16)
└── docs/
    └── ble-protocol.md  # Detailed protocol reference
```

## Requirements

- Python 3.11+
- Windows 10+ with Bluetooth (tested on Windows 11)
- `bleak` for BLE
- `matplotlib` for plotting

## Motor Dyno Integration

The original goal is to drive the trainer flywheel with an ODrive D6374 motor:

- **Direct drive preferred**: The eddy current brake needs speed to produce torque. A 5:1 gearbox is counterproductive (gives torque the trainer doesn't need, removes speed it does).
- **ODrive USB gives 20+ Hz motor telemetry**, BLE gives ~1 Hz trainer telemetry
- **Gearbox efficiency test**: Run motor through gearbox into free-spinning trainer. Compare ODrive-side power to trainer-side power = gearbox efficiency map.

## References

- [Bluetooth CPS Spec](https://www.bluetooth.com/specifications/specs/cycling-power-service-1-1/)
- [qdomyos-zwift](https://github.com/cagnulein/qdomyos-zwift) -- Saris resistance protocol
- [pycycling](https://github.com/zacharyedwardbull/pycycling) -- Python BLE trainer library
- [DC Rainmaker H2 Review](https://www.dcrainmaker.com/2019/01/cycleops-h2-hammer-2-trainer-in-depth-review.html)
