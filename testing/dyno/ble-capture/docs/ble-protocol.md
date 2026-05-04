# Saris Hammer H2 BLE Protocol Reference

## Overview

The Saris Hammer H2 (Model 320) uses the **Cycling Power Service (0x1818)**, not the more common FTMS (0x1826) used by newer trainers. Resistance control is via a Saris proprietary BLE characteristic.

## BLE Services

| Service | UUID | Type |
|---------|------|------|
| Cycling Power | `0x1818` | Standard BLE |
| Saris Proprietary | `c0f4013a-a837-4165-bab9-654ef70747c6` | Vendor |
| Device Information | `0x180A` | Standard BLE |

## Cycling Power Measurement (0x2A63)

Notifications arrive at ~1.1 Hz (firmware-locked, not adjustable from client side).

### Flags

The H2 reports flags `0x3418`, enabling:
- Accumulated Torque (bit 2)
- Wheel Revolution Data (bit 4)
- Crank Revolution Data (bit 5)

### Payload Format

```
Offset  Size    Field                   Resolution
0       uint16  Flags                   --
2       sint16  Instantaneous Power     1 W
4       uint16  Accumulated Torque      1/32 Nm (cumulative)
6       uint32  Cumulative Wheel Revs   1 revolution
10      uint16  Last Wheel Event Time   1/2048 s (rolls at 65536)
12      uint16  Cumulative Crank Revs   1 revolution
14      uint16  Last Crank Event Time   1/1024 s
```

### Derived Quantities

From consecutive notifications:

| Quantity | Formula |
|----------|---------|
| RPM | `d_revs / (d_wheel_time / 2048) * 60` |
| Angular velocity | `RPM * 2 * pi / 60` (rad/s) |
| Inst. torque | `d_acc_torque / d_revs * 2 * pi` (Nm) |
| Torque (cross-check) | `power / omega` (Nm) |
| Angular accel. | `d_omega / d_t` (rad/s^2) |

### Known Issues

- Wheel event time only updates when a new revolution completes, causing RPM to read 0 between events at low speeds
- Accumulated torque is energy/(2*pi), so the per-rev delta gives average torque over that revolution
- At ~1.1 Hz notification rate, fast transients are aliased

## Saris Proprietary Resistance Control

### Characteristic

```
Service:        c0f4013a-a837-4165-bab9-654ef70747c6
Characteristic: ca31a533-a858-4dc7-a650-fdeb6dad4c14
Properties:     Write + Indicate
```

### Command Format (10 bytes)

```
Byte  Value       Purpose
0     0x00        Header
1     0x10        Header
2     mode        Control mode (see below)
3     param_lo    Parameter low byte
4     param_hi    Parameter high byte
5-9   0x00        Padding
```

### Control Modes

| Mode | Byte | Parameter |
|------|------|-----------|
| ManualPower (ERG) | 0x01 | Target watts (uint16) |
| ManualSlope (SIM) | 0x02 | Grade * 100, e.g. 500 = 5.0% |

### Timing

- Minimum 3 seconds between write commands
- Allow 4-5 seconds for full brake engagement
- The trainer smoothly ramps between resistance levels

### Status

**NOT YET TESTED.** The command format is reverse-engineered from the [qdomyos-zwift](https://github.com/cagnulein/qdomyos-zwift/blob/master/src/devices/cycleopsphantombike/cycleopsphantombike.cpp) CycleOps Phantom Bike driver.

## CPS Vendor Characteristic (a026e005)

A secondary vendor characteristic under the Cycling Power Service. Accepts single-byte writes and responds with 4-byte indications (`01 XX 02 00`). Purpose unknown -- likely calibration or status queries.

## Alternative: ANT+ FE-C

The H2 also supports ANT+ FE-C at ~4 Hz (vs 1.1 Hz BLE). Requires a USB ANT+ stick (~$25). Not implemented in this project.

## Eddy Current Brake Physics

The trainer uses electromagnetic eddy currents for resistance:

- **Low speed**: Brake torque proportional to speed (`T = k * omega`)
- **High speed**: Brake power saturates, torque drops (`T = P_max / omega`)
- **Corner speed**: Crossover between linear-torque and constant-power regions (unknown for H2)
- **Field control**: Trainer varies `k` by adjusting coil current. Higher BLE resistance = higher `k`.

The actual brake torque curve is unknown. The 2000W @ 40 km/h spec is one data point.

## Sources

- [Bluetooth CPS 1.1 Spec](https://www.bluetooth.com/specifications/specs/cycling-power-service-1-1/)
- [qdomyos-zwift CycleOps driver](https://github.com/cagnulein/qdomyos-zwift/blob/master/src/devices/cycleopsphantombike/cycleopsphantombike.cpp)
- [pycycling](https://github.com/zacharyedwardbull/pycycling)
- [DC Rainmaker H2 Review](https://www.dcrainmaker.com/2019/01/cycleops-h2-hammer-2-trainer-in-depth-review.html)
- [pyftms](https://github.com/dudanov/python-pyftms)
