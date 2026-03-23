---
created: 2026-03-22
tags: [motor-control, odrive, onboarding, safety]
---

# ODrive 3.6 + D6374 Onboarding Guide

Everything you need to get the motor spinning from a cold start. Written from hard-won troubleshooting — read this before powering anything on.

## Safety First

> [!danger] Mandatory Safety Rules
> - **Never touch motor leads or encoder wires while powered on.** 55V DC can kill. Motor phase voltages spike during braking.
> - **Secure the motor before spinning.** The D6374 generates over 1 Nm of torque and can throw itself off a bench. Clamp or bolt it down.
> - **Keep hands and cables clear of the rotor.** At 5 t/s (300 RPM) the exposed shaft is a finger-catching hazard. At high speed (6000+ RPM in torque mode) it's genuinely dangerous.
> - **The brake resistor gets hot.** 50W dissipation during hard stops. Don't touch it during or after decel tests.
> - **The power supply can source dangerous current.** Our supply runs ~55V and can push well beyond 19A at the wall. Treat it like a welding source.
> - **If anything sounds wrong, cut power at the supply.** Don't try to software-stop a desync'd motor — it may spike current instead.

### Electrical Limits

| Parameter | Limit | What Happens If Exceeded |
|-----------|-------|--------------------------|
| Bus voltage | 59V trip | ODrive shuts down (overvoltage fault) |
| Motor current | 19A (software limit) | ODrive current-limits or faults |
| Motor phase R | ~50 mOhm | If reads <10 mOhm or NaN → corrupted, motor won't respond correctly |
| Motor phase L | ~23 uH | Same — corruption check |
| Max stable velocity (PID) | ~5 t/s (300 RPM) | Above this, velocity PID oscillates and loses control |
| FOC desync limit | ~50 t/s (3000 RPM) | Commutation fails, motor stalls violently, high current spike |
| Cogging breakaway | ~1.9A (~0.105 Nm) | Below this current the motor just sits in a detent and vibrates |

---

## Hardware Wiring & Pre-Power Checklist

> [!danger] The ODrive 3.6 has NO reverse polarity protection. Wiring DC power backwards will fry the board instantly.

### Connection Diagram

```
                    ┌──────────────────────────────────┐
   DC SUPPLY        │         ODrive 3.6               │
   (+) ────────────►│ DC+ (thick screw terminal)       │
   (-) ────────────►│ DC- (thick screw terminal)       │
                    │                                  │
   BRAKE RESISTOR   │ AUX (2-pin screw terminal)       │
   (2Ω 50W) ◄─────►│ Polarity doesn't matter           │
                    │                                  │
   D6374 MOTOR      │ M0 (3x screw terminal)           │
   Phase A ────────►│ A                                │
   Phase B ────────►│ B                                │
   Phase C ────────►│ C                                │
                    │                                  │
   AMT-102 ENCODER  │ J4 encoder port (JST-SH)        │
   (ribbon cable)──►│ Keyed connector, one way only    │
                    │                                  │
   USB ────────────►│ Micro-USB                        │
                    └──────────────────────────────────┘
```

### Pre-Power Checklist

Run through this **every time** before turning on the power supply:

> [!warning] Hardware Checklist
> - [ ] **DC polarity correct.** Red/positive to DC+, black/negative to DC-. Triple-check. No reverse protection on this board.
> - [ ] **Screw terminals tight.** Loose DC connections arc and melt. Loose motor phase wires cause intermittent faults. Wiggle each wire — it shouldn't move.
> - [ ] **Brake resistor connected and not shorting anything.** Both wires into the AUX terminal. If disconnected, regen energy has nowhere to go → overvoltage fault → ODrive shuts down mid-decel. The resistor body is metal — make sure it's not bridging exposed contacts or bare wires. It only gets hot during hard decel at high speeds.
> - [ ] **Motor bolted down.** Clamped or mounted. Not sitting loose on the bench.
> - [ ] **Encoder sleeve tight on shaft.** Grab it and twist by hand. If it rotates, press it back on. Slip = garbage position data = failed cal or mid-run faults.
> - [ ] **Encoder cable seated.** Push the JST connector into J4 until it clicks. It's keyed — only goes one way.
> - [ ] **Gearbox state matches your PID gains.** If gearbox is attached, you need gearbox gains. If bare motor, you need bare motor gains. Wrong gains = oscillation or stall. See [[#PID Gains — Which Config Are You Running?]].
> - [ ] **Nothing touching the rotor.** Cables, zip ties, fingers, sleeves — clear of the spinning parts.
> - [ ] **Power supply current limit set.** If your supply has an adjustable current limit, set it to ~5A for initial bring-up. You can raise it once things are working.
> - [ ] **USB connected.** Plug in before or after DC power — order doesn't matter for ODrive 3.6.

### Motor Phase Order

The 3 motor wires (A, B, C) can go into the 3 ODrive terminals in any order. Wrong order just reverses rotation direction — it won't damage anything. If the motor spins the wrong way after calibration:

1. Power off
2. Swap any two of the three motor wires
3. Recalibrate (state 3)

### AMT-102 Encoder DIP Switches

The encoder ships at 2048 PPR (x4 = 8192 CPR). **Leave all DIP switches at factory default.** The ODrive config expects `cpr = 8192`. If someone has changed the DIP switches, the encoder CPR won't match and calibration will fail or give wrong velocity readings.

---

## Hardware on the Bench

| Component | Spec | Notes |
|-----------|------|-------|
| ESC | ODrive 3.6 (FW 0.5.5, HW 3.6.56) | **End-of-life hardware** — no firmware updates coming |
| Motor | D6374 150kv, 7 pole pairs | Star-wound, exposed shaft |
| Encoder | CUI AMT-102 (8192 CPR) | Press-fit sleeve on shaft — check tightness before every session |
| Gearbox | 5:1 planetary (removable) | Adds friction/damping, changes PID gains needed |
| Brake resistor | 50W, 2 ohm | Must be armed via full calibration (state 3) |
| Power supply | ~55V DC | Current draw at the supply is much lower than motor phase current (the ESC trades voltage for current) |

---

## First-Time Setup (One-Time)

### 1. Install USB Driver (Zadig)

The ODrive 3.6 won't show up in Python without the right driver.

1. Download and open [Zadig](https://zadig.akeo.ie/)
2. Options → List All Devices
3. Select **"ODrive 3.6 Native Interface (Interface 2)"**
4. Set driver to **WinUSB** → Install
5. Reboot if needed

> [!warning] After a factory reset (`erase_configuration()`), you'll need to redo this step.

### 2. Install Python Packages

```bash
pip install odrive==0.5.5
```

That's it. The `odrive` package includes `odrivetool` (interactive shell) and the Python API.

### 3. Verify Connection

```python
import odrive
odrv0 = odrive.find_any(timeout=10)
print(f"Bus voltage: {odrv0.vbus_voltage:.1f}V")
print(f"Serial: {odrv0.serial_number}")
```

Should print ~55V and the serial `59962984378673`. If it hangs, check Zadig driver.

> [!warning] Only one process can hold the USB connection at a time.
> Close `odrivetool` before running Python scripts, and vice versa.

---

## Every-Session Startup

The encoder loses its reference on every power cycle. You must recalibrate.

### Step 1: Power on and connect

```python
import odrive
odrv0 = odrive.find_any()
print(f"Bus: {odrv0.vbus_voltage:.1f}V, State: {odrv0.axis0.current_state}")
# State should be 1 (IDLE)
```

### Step 2: Full calibration (state 3)

```python
odrv0.axis0.requested_state = 3   # FULL_CALIBRATION_SEQUENCE
```

The motor will beep (measuring R and L), then spin slowly (encoder offset search). Wait until state returns to 1 (IDLE).

> [!danger] Use state 3 (full cal), NOT state 7 (encoder-only)
> Encoder-only calibration (state 7) does **not** arm the brake resistor. If you skip the brake resistor arming and then decelerate hard, the bus voltage spikes and the ODrive faults with overvoltage. This is an undocumented FW 0.5.5 behavior. **Always use state 3.**

### Step 3: Check for motor parameter corruption

```python
R = odrv0.axis0.motor.config.phase_resistance
L = odrv0.axis0.motor.config.phase_inductance
print(f"R = {R*1000:.1f} mOhm, L = {L*1e6:.1f} uH")
```

**Expected:** R ≈ 48-52 mOhm, L ≈ 22-24 uH

If R < 10 mOhm or L shows NaN → params are corrupted. See [[#Motor Parameter Corruption Fix]] below.

### Step 4: Enter closed-loop control

```python
odrv0.axis0.requested_state = 8   # CLOSED_LOOP_CONTROL
```

Motor is now holding position. You can command it.

### Step 5: Command motion

```python
# Velocity mode
odrv0.axis0.controller.config.control_mode = 2  # VEL_CONTROL
odrv0.axis0.controller.input_vel = 2.0  # turns/sec

# Stop
odrv0.axis0.controller.input_vel = 0

# Position mode
odrv0.axis0.controller.config.control_mode = 3  # POS_CONTROL
odrv0.axis0.controller.input_pos = 10.0  # turns

# Torque mode (be careful)
odrv0.axis0.controller.config.control_mode = 1  # TORQUE_CONTROL
odrv0.axis0.controller.input_torque = 0.1  # Nm
```

### Step 6: Shut down safely

```python
odrv0.axis0.requested_state = 1   # IDLE
```

Then power off the supply.

---

## PID Gains — Which Config Are You Running?

**You must switch gains when adding/removing the gearbox.** Using gearbox gains on a bare motor causes violent oscillation.

| Config | pos_gain | vel_gain | vel_integrator_gain | vel_ramp_rate |
|--------|----------|----------|---------------------|---------------|
| Bare motor (no gearbox) | 5.0 | 0.05 | 0.05 | 3.0 |
| 5:1 gearbox | 15.0 | 0.1 | 0.2 | 10.0 |

```python
# Example: set bare motor gains
ax = odrv0.axis0
ax.controller.config.pos_gain = 5.0
ax.controller.config.vel_gain = 0.05
ax.controller.config.vel_integrator_gain = 0.05
ax.controller.config.vel_ramp_rate = 3.0
```

> [!warning] Gearbox needs vel_ramp_rate ≥ 10
> At 3 t/s/s (bare motor default), the integrator saturates at current limit before the gearbox breaks through stiction. The motor just buzzes and doesn't move.

---

## Troubleshooting

### Motor Parameter Corruption Fix

Full cal (state 3) sometimes corrupts R and L even with `pre_calibrated=True`. Symptoms: motor doesn't respond to commands, or current controller behaves erratically.

```python
# 1. Disable pre_calibrated
odrv0.axis0.motor.config.pre_calibrated = False

# 2. Run motor-only cal (state 4) — NOT full cal
odrv0.axis0.requested_state = 4
# Wait for IDLE

# 3. Verify
R = odrv0.axis0.motor.config.phase_resistance
L = odrv0.axis0.motor.config.phase_inductance
print(f"R = {R*1000:.1f} mOhm, L = {L*1e6:.1f} uH")
# Should be R ≈ 48-52, L ≈ 22-24

# 4. Re-enable and save
odrv0.axis0.motor.config.pre_calibrated = True
odrv0.save_configuration()
# ODrive reboots here (DeviceLostException is normal)
```

### Brake Resistor Not Armed

If you get overvoltage faults during decel, the brake resistor probably isn't armed.

```python
print(odrv0.config.enable_brake_resistor)   # Should be True
print(odrv0.config.brake_resistance)         # Should be 2.0
```

`enable_brake_resistor` can silently reset after `save_configuration()`. Verify after every reboot. Fix: set it True and save again.

### Motor Won't Move / Buzzes in Place

Check in this order:
1. **State check:** `odrv0.axis0.current_state` — must be 8 (closed-loop). If 1, you forgot to enter closed-loop.
2. **Error check:** `odrv0.axis0.error`, `odrv0.axis0.motor.error`, `odrv0.axis0.encoder.error` — any non-zero means something faulted.
3. **R/L corruption:** Check phase_resistance and phase_inductance (see above).
4. **Cogging detent:** At currents below ~1.9A (0.105 Nm), the motor just sits in a magnet detent. Command more torque.
5. **Wrong gains:** If you have gearbox gains on a bare motor, it will oscillate and fault.

### Clear All Errors

```python
odrv0.axis0.error = 0
odrv0.axis0.motor.error = 0
odrv0.axis0.encoder.error = 0
odrv0.axis0.controller.error = 0
```

### save_configuration() Reboots the ODrive

This is normal. You'll get a `DeviceLostException`. Reconnect:

```python
odrv0 = odrive.find_any()
```

### Factory Reset

Nuclear option. Erases everything.

```python
odrv0.erase_configuration()
# ODrive reboots. You'll need to:
# 1. Redo Zadig driver install
# 2. Reconfigure all parameters from scratch
```

### Encoder Slip

The AMT-102 press-fit sleeve can slip on the shaft during high-accel tests. Symptoms: position drifts, calibration fails, or motor faults mid-run. **Check the sleeve tightness before every session** — twist it by hand and make sure it doesn't rotate.

---

## Saved Configuration Reference

These are the values currently saved to the ODrive. If you factory reset, re-enter all of these:

```python
odrv0.config.dc_bus_overvoltage_trip_level = 59.0
odrv0.axis0.motor.config.current_lim = 19.0
odrv0.axis0.motor.config.calibration_current = 10.0
odrv0.axis0.motor.config.pole_pairs = 7
odrv0.axis0.motor.config.phase_resistance = 0.05022
odrv0.axis0.motor.config.phase_inductance = 23.14e-6
odrv0.axis0.motor.config.pre_calibrated = True
odrv0.axis0.encoder.config.cpr = 8192
odrv0.axis0.encoder.config.mode = 0  # INCREMENTAL
odrv0.config.enable_brake_resistor = True
odrv0.config.brake_resistance = 2.0
odrv0.axis0.trap_traj.config.vel_limit = 5.0
odrv0.axis0.trap_traj.config.accel_limit = 10.0
odrv0.axis0.trap_traj.config.decel_limit = 10.0
odrv0.save_configuration()
```

---

## Tools & Scripts

| What | Command | Notes |
|------|---------|-------|
| Interactive shell | `odrivetool` | Tab-complete, live object model. Good for poking around. |
| Live dashboard | `python _dev/odrive_dashboard.py` | Tkinter GUI: voltage, current, velocity, position at 20Hz |
| Characterization sweep | `python _dev/odrive_sweep.py "no_gearbox"` | Runs 6 automated tests, saves JSON results |
| Compare sweeps | `python _dev/odrive_compare.py` | Plots side-by-side comparison from saved JSONs |

---

## Things That Will Bite You (Lessons Learned)

1. **State 7 doesn't arm the brake resistor.** Use state 3. Always.
2. **Full cal corrupts motor params randomly.** Check R and L after every calibration. The sweep script does this automatically with retries.
3. **PID gains are config-specific.** Gearbox gains on bare motor = violent oscillation. Bare motor gains on gearbox = motor buzzes and doesn't move.
4. **Ramp rate matters more than you think.** Too slow and the integrator saturates. Too fast and the motor can't track. Bare motor sweet spot: ~6.7 t/s/s. Gearbox needs ≥ 10 t/s/s.
5. **Velocity PID tops out at ~5 t/s on this firmware.** The motor can go way faster (6000+ RPM in torque mode), but the velocity controller can't track above ~300 RPM. This is a FW 0.5.5 limitation.
6. **Power supply current ≠ motor current.** The ESC is a DC-AC converter. You might see 2A at the supply but 15A in the motor phases. Don't be surprised.
7. **Only one USB connection at a time.** Close odrivetool before running scripts. Close scripts before opening odrivetool.
8. **save_configuration() reboots.** DeviceLostException after save is normal.
9. **The gearbox clicks at high accel.** Not broken, just gear mesh noise.
10. **The encoder sleeve slips.** Check it before every session. If position drifts randomly, this is probably why.

---

## Quick Reference Card

```
CALIBRATE:    odrv0.axis0.requested_state = 3
CLOSED LOOP:  odrv0.axis0.requested_state = 8
IDLE:         odrv0.axis0.requested_state = 1
VELOCITY:     .controller.config.control_mode = 2 → .controller.input_vel = X
POSITION:     .controller.config.control_mode = 3 → .controller.input_pos = X
TORQUE:       .controller.config.control_mode = 1 → .controller.input_torque = X
CHECK ERRORS: .axis0.error, .motor.error, .encoder.error
CHECK PARAMS: .motor.config.phase_resistance, .phase_inductance
BUS VOLTAGE:  odrv0.vbus_voltage
```

---

## Where to Find More

- **Full hardware spec, sweep data, VESC transition notes:** [[odrive-motor-control|README]]
- **Structured test plan and characterization framework:** [[Motor Test Matrix]]
- **ODrive docs (FW 0.5.5):** [docs.odriverobotics.com](https://docs.odriverobotics.com/v/0.5.5/)
