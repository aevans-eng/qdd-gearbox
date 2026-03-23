# SOP: ODrive Test Session

> **Purpose:** Step-by-step procedure for every ODrive test session. Follow in order. No shortcuts.
> **Hardware:** ODrive 3.6 (56V, FW 0.5.5) | D6374 150KV | AMT-102 encoder | Riden RD6030 | 2 ohm 50W brake resistor
> **Ref:** `testing/hardware/odrive-onboarding-guide.md` for troubleshooting

---

## Safe Operating Limits

| Parameter | Our Limit | Absolute Max | What Breaks |
|-----------|-----------|--------------|-------------|
| Supply voltage | **48V** | 56V rated, 60V MOSFET | ODrive board (MOSFETs) |
| Supply current limit | **5A** (initial), 10A (after cal verified) | 30A (RD6030 max) | Motor windings, ODrive |
| Motor current_lim | **10A** (initial), 15-20A (after verified) | 70A (motor peak) | Motor windings |
| Bus overvoltage trip | 59.92V (firmware default) | 60V (MOSFET Vds) | ODrive board |
| Motor Kt | 0.0551 Nm/A | — | — |
| Max velocity (PID stable) | ~5 turns/s (300 RPM) | — | Control instability |

---

## One-Time Setup (Do Once, Ever)

### 1. Zadig USB Driver

1. Plug ODrive into computer via micro USB data cable (with or without DC power)
2. Run `testing/hardware/zadig-2.9.exe`
3. **Options -> List All Devices** (checkbox)
4. Select **"ODrive 3.6 Native Interface (Interface 2)"** from dropdown
5. Set driver to **WinUSB** on the right side
6. Click **Install Driver** (or **Replace Driver**)
7. Wait for "Driver installed successfully"

> If "ODrive 3.6 Native Interface" doesn't appear, the cable is charge-only. Get a different micro USB cable.

### 2. Python Package

Already installed: `odrive==0.5.4` via miniconda.

Verify:
```
python -c "import odrive; print('OK')"
```

---

## Pre-Session Wiring Verification

> Do this EVERY session BEFORE turning on DC power. Read each item out loud.

- [ ] **DC polarity correct** — Red/positive wire to DC+ terminal, black/negative to DC-. **No reverse protection on this board.**
- [ ] **DC terminals tight** — wiggle each wire, must not move
- [ ] **Brake resistor connected** — both wires in AUX terminal, resistor body not touching bare contacts
- [ ] **Motor phases connected** — 3 wires into M0 terminals (A, B, C), tight
- [ ] **Motor bolted down** — clamped or mounted, cannot move
- [ ] **Encoder ribbon cable seated** — pushed into J4 until click
- [ ] **Encoder sleeve tight on shaft** — grab and twist by hand, must not rotate
- [ ] **Nothing touching rotor** — cables, zip ties, sleeves clear
- [ ] **Gearbox state noted** — bare motor OR gearbox attached (determines PID gains)
- [ ] **USB cable connected** — micro USB from ODrive to computer

---

## RD6030 Power Supply Setup

### Original Settings (Restore When Done With QDD Testing)

| Setting | Original Value |
|---------|---------------|
| OVP | 57V |
| OCP | 25A |

### Every Session Settings

| Setting | Value | How to Set |
|---------|-------|------------|
| **V-set** | **48.0V** | Rotate encoder to adjust voltage setpoint |
| **I-set** | **5.00A** (first session) / **10.0A** (after first successful cal) | Rotate encoder to adjust current limit |
| **OVP** | **52.0V** | Overvoltage protection — supply shuts off if output exceeds this |
| **OCP** | **8.0A** | Overcurrent protection — hard ceiling |

### Power On Sequence

> **Note:** The ODrive needs DC power to enumerate over USB through Aaron's dock. Turn on DC power BEFORE expecting USB connection.

1. Verify all wiring (checklist above)
2. Confirm V-set = 48.0V, I-set = 5.00A
3. Confirm OVP = 52.0V, OCP = 8.0A
4. **Turn output ON**
5. Display should show: ~48V output, ~0A current, ~0W power
6. If current jumps above 0.5A at idle — **turn OFF immediately**, something is wrong

---

## Software Startup

### Connect to ODrive

```python
import odrive
odrv0 = odrive.find_any(timeout=10)
print(f"Bus: {odrv0.vbus_voltage:.1f}V")
print(f"State: {odrv0.axis0.current_state}")  # Should be 1 (IDLE)
```

**Expected:** Bus voltage ~48V, state = 1.

If `find_any()` hangs: close any other `odrivetool` sessions (only one USB connection at a time).

### Calibration (Every Session)

The encoder loses reference on every power cycle. Must recalibrate.

```python
# ALWAYS use state 3 (full cal) — state 7 does NOT arm brake resistor
odrv0.axis0.requested_state = 3  # FULL_CALIBRATION_SEQUENCE
```

**What happens:**
1. Motor beeps (measuring phase resistance and inductance) — ~2 sec
2. Motor spins slowly (encoder offset calibration) — ~5 sec
3. Motor stops, state returns to 1 (IDLE)

**Wait until state returns to 1 before proceeding.**

```python
# Poll state (or just wait ~10 seconds)
import time
while odrv0.axis0.current_state != 1:
    time.sleep(0.5)
print("Calibration complete")
```

### Post-Calibration Verification (MANDATORY)

```python
# 1. Check for errors
print(f"Axis error:    {odrv0.axis0.error}")      # Must be 0
print(f"Motor error:   {odrv0.axis0.motor.error}")  # Must be 0
print(f"Encoder error: {odrv0.axis0.encoder.error}") # Must be 0

# 2. Check motor parameters aren't corrupted
R = odrv0.axis0.motor.config.phase_resistance
L = odrv0.axis0.motor.config.phase_inductance
print(f"R = {R*1000:.1f} mOhm (expect ~50)")
print(f"L = {L*1e6:.1f} uH (expect ~23)")

# 3. Check brake resistor is armed
print(f"Brake enabled: {odrv0.config.enable_brake_resistor}")  # Must be True
print(f"Brake R: {odrv0.config.brake_resistance}")              # Must be 2.0
```

**If any error is non-zero:** Do NOT proceed. See troubleshooting in onboarding guide.
**If R < 10 mOhm or L is NaN:** Motor params corrupted. See "Motor Parameter Corruption Fix" in onboarding guide.
**If brake not enabled:** Set it True and save before continuing.

---

## Entering Control Modes

### Set PID Gains First

```python
ax = odrv0.axis0

# BARE MOTOR (no gearbox)
ax.controller.config.pos_gain = 5.0
ax.controller.config.vel_gain = 0.05
ax.controller.config.vel_integrator_gain = 0.05
ax.controller.config.vel_ramp_rate = 3.0

# 5:1 GEARBOX
# ax.controller.config.pos_gain = 15.0
# ax.controller.config.vel_gain = 0.1
# ax.controller.config.vel_integrator_gain = 0.2
# ax.controller.config.vel_ramp_rate = 10.0
```

> Using wrong gains for your config = violent oscillation or motor that won't move. Get this right.

### Enter Closed-Loop Control

```python
odrv0.axis0.requested_state = 8  # CLOSED_LOOP_CONTROL
# Motor is now actively holding position
```

### Velocity Mode

```python
odrv0.axis0.controller.config.control_mode = 2  # VEL_CONTROL
odrv0.axis0.controller.input_vel = 1.0  # turns/sec (START SLOW)

# To stop:
odrv0.axis0.controller.input_vel = 0
```

### Position Mode

```python
odrv0.axis0.controller.config.control_mode = 3  # POS_CONTROL
odrv0.axis0.controller.input_pos = 1.0  # turns from current zero
```

### Torque Mode (Use with Caution)

```python
odrv0.axis0.controller.config.control_mode = 1  # TORQUE_CONTROL
odrv0.axis0.controller.input_torque = 0.1  # Nm (START VERY LOW)

# Minimum to overcome cogging: ~0.105 Nm (1.9A)
# At current_lim = 10A, max torque = 0.551 Nm
```

---

## Health Check (Start and End of Every Session)

Record in `testing/data/health-log.csv`:

```python
# Run this and log the values:
print(f"Bus voltage: {odrv0.vbus_voltage:.1f}V")

# If gearbox attached, also check:
# - Backlash (T-012 method)
# - No-load friction Iq at reference speed
# - Housing temperature (hand feel or IR thermometer)
# - Visual tooth inspection
```

---

## Shutdown Procedure

1. **Stop all motion:**
   ```python
   odrv0.axis0.controller.input_vel = 0
   odrv0.axis0.controller.input_torque = 0
   ```

2. **Return to idle:**
   ```python
   odrv0.axis0.requested_state = 1  # IDLE
   ```

3. **Verify motor stopped** — physically confirm no movement

4. **Turn off RD6030 output** — press output button

5. **Log session** — record what you did, any anomalies, health check values

---

## Emergency Stop

**If anything goes wrong — sound, smell, vibration, unexpected motion:**

1. **Kill DC power** — RD6030 output OFF (fastest option: hit the output button or unplug DC input)
2. Software backup: `odrv0.axis0.requested_state = 1` (only if safe to reach keyboard)
3. Do NOT touch the motor, brake resistor, or DC wires until power is confirmed off
4. Investigate before re-powering

---

## Quick Reference

```
States:  1 = IDLE    3 = FULL_CAL    8 = CLOSED_LOOP
Modes:   1 = TORQUE  2 = VELOCITY    3 = POSITION
Gains:   Bare motor → pos=5, vel=0.05, int=0.05, ramp=3
         Gearbox    → pos=15, vel=0.1, int=0.2, ramp=10
Limits:  48V supply, 5-10A supply limit, 10A motor current_lim
Kt:      0.0551 Nm/A  →  10A = 0.551 Nm max
```

---

## Revision History

| Date | Change |
|------|--------|
| 2026-03-22 | Initial SOP created. Supply voltage set to 48V (not 55V) based on independent spec verification. |
