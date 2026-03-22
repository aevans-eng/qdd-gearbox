# Smart Trainer Dynamometer — CycleOps Hammer H2

> Using a borrowed CycleOps (Saris) Hammer H2 direct-drive smart trainer as a budget dynamometer for QDD actuator testing.

---

## Why This Works

A direct-drive smart trainer is fundamentally a controllable brake with a calibrated power meter. It gives you something you don't otherwise have: **an independent torque measurement that doesn't depend on $K_t$**.

Right now, every torque number in the test campaign comes from $\tau = K_t \cdot I_q$ — which means if $K_t$ is wrong, everything downstream is wrong, and T-009 can only sanity-check $K_t$, not verify it (see testing-fundamentals.md). A trainer dyno closes that loop by measuring output torque directly.

---

## H2 Specifications (Relevant to Dyno Use)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Power accuracy | ±2% | PowerTap-derived measurement |
| Max power | 2000 W @ 40 kph | More than enough for QDD |
| Resistance type | Electromagnetic | Fast response, controllable |
| Flywheel | 9 kg (20 lb) | Adds inertia — affects transient tests |
| Protocols | ANT+ FE-C, BLE FTMS, ANT+ Power | Multiple data paths |
| Cadence broadcast | Integrated | No external sensor needed |
| Cassette compatibility | Shimano/SRAM 8–11 speed HG spline | Standard HG freehub body |
| Power supply | 110–240 V AC (mains required) | |
| Control modes | ERG (constant power), SIM (grade simulation) | ERG mode = constant load setpoints |

**Data update rate:** ANT+ power profile broadcasts at ~4 Hz (every 250 ms). This is fast enough for steady-state measurements but too slow for transient dynamics (step response, cogging). For transients, continue using ODrive's 8 kHz $I_q$ data.

---

## What This Enables

| Test | Without Trainer | With Trainer |
|------|----------------|--------------|
| **$K_t$ verification (T-009)** | Indirect sanity check only — can't confirm actual value | Direct: apply known torque via trainer resistance, read $I_q$, solve $K_t = \tau / I_q$ |
| **Efficiency (η)** | $P_{in} = V \cdot I$ is known, but $P_{out}$ requires trusting $K_t$ | $\eta = P_{trainer} / P_{electrical}$ — independent measurement on both sides |
| **Friction torque ($\tau_f$)** | Backdrive by hand, estimate from $I_q$ | Trainer drives the gearbox backwards at known torque — directly measures friction |
| **Torque capacity** | Load until something breaks, trust $K_t$ for the number | Calibrated torque at failure point |
| **Continuous torque / thermal** | Run at commanded $I_q$, trust $K_t$ for load | Verified load via trainer power reading |

**What the trainer does NOT help with** (continue using ODrive data):
- Step response / transient dynamics (trainer data too slow)
- Cogging profile (need position-resolved $I_q$ at 8 kHz)
- Backlash measurement (need encoder counts, not power)
- High-speed testing >200 RPM (outside trainer's accurate range — see limitations)

---

## Mechanical Interface — The Adapter

### The Problem

The QDD gearbox output shaft needs to couple to the H2's Shimano HG freehub body. These are completely different interfaces.

### Shimano HG Freehub Spline Profile

The HG freehub is the industry standard cassette interface. Key characteristics:

| Feature | Value |
|---------|-------|
| Spline count | 9 splines + 1 wide key slot |
| Approximate OD across splines | ~34–35 mm |
| Body length (8/9/10-speed) | 34.9 mm |
| Smallest compatible cog | 11T |
| Spline profile | Shallow, parallel-sided, non-involute |

> **Shimano does not publish exact spline geometry.** The best approach is to **measure the actual freehub body on the H2** with calipers, or find/download a community HG spline CAD model (GrabCAD, Thingiverse — multiple exist) and verify against the physical part.

### Adapter Concept

```
QDD Output Shaft ──→ [ADAPTER] ──→ H2 Freehub Splines
     (your design)     (new part)     (standard HG interface)
```

The adapter needs:

1. **Input side (QDD):** Matches your gearbox output shaft geometry — whatever the current output interface is (D-shaft, keyed shaft, bolt pattern, etc.)
2. **Output side (trainer):** Female HG spline profile that slides onto the freehub body, same as a cassette cog
3. **Retention:** The freehub has a threaded end for a cassette lockring — you can use a standard lockring to hold the adapter in place
4. **Concentricity:** Both interfaces must be concentric to avoid runout and bearing side-loads

### Design Considerations

| Consideration | Notes |
|---------------|-------|
| **Material** | 3D print is likely fine at 16 Nm — HG splines are shallow and the contact area is large. Print in PLA+ or nylon. If splines deform under load, machine from aluminum. |
| **Fit tolerance** | HG splines have a loose fit by design (cassette cogs slide on by hand). This is fine — torque is transmitted through the spline faces, not interference fit. |
| **Axial retention** | Use the existing cassette lockring (standard tool: FR-5.2 or similar). Thread onto freehub end, clamps adapter axially. |
| **Length** | Keep adapter short — you only need one "cog" worth of engagement (~3–5 mm spline contact minimum). Longer = more contact area but more overhang from gearbox. |
| **Alignment** | The trainer sits on the floor. The gearbox needs to be at the same height and axially aligned. You'll need some kind of mounting bracket or stand — even a simple plywood jig. |
| **Freehub ratchet direction** | The freehub has a one-way clutch (freewheel). It only transmits torque in one direction (forward pedaling). This means you can only load the gearbox in one rotation direction via the trainer's resistance. To test both directions, you'd need to reverse the setup or accept single-direction testing. |

### Steps to Build

1. **Measure the freehub body** — calipers on the actual H2. Get: OD across splines, root diameter between splines, key slot width, body length. Alternatively, pull a cassette cog off a bike and use that as your template.
2. **Measure QDD output** — whatever your current output shaft/interface is.
3. **CAD the adapter** — disc with female HG splines (ID) and QDD shaft interface (center bore or bolt pattern).
4. **Print and test fit** — slide onto freehub, check for slop, check lockring threads.
5. **Iterate** — if splines are too tight/loose, adjust by 0.1 mm and reprint.

> **Shortcut:** Pull an old cassette cog (any single cog from an 8–11 speed cassette) and use it as a known-good spline reference. Bore out the center to accept your output shaft. This skips the spline modeling entirely.

---

## Data Acquisition

### Option A: Cycling App + ANT+ Dongle (Simplest)

- Use any ANT+ USB dongle on a laptop
- Software: Zwift, TrainerRoad, or free options like GoldenCheetah
- Logs power (W), cadence (RPM) at ~1 Hz
- Good enough for steady-state efficiency sweeps

### Option B: ANT+ Python Library (Best for Automation)

- `openant` or `python-ant` library to read ANT+ data directly
- Sync with ODrive Python logging — timestamp both streams
- Get power and cadence from trainer + $I_q$, $\omega$, $\theta$ from ODrive in one script
- This is the ideal setup — single Python script runs both instruments

### Option C: Bluetooth FTMS (Alternative)

- `bleak` Python library for BLE
- FTMS (Fitness Machine Service) profile exposes power, cadence, resistance control
- Can programmatically set trainer resistance from Python — fully automated test sweeps

### Recommended Approach

Option B or C — whichever protocol is easier to get working. The key advantage is **synchronized logging**: one Python script that simultaneously:
1. Commands motor current via ODrive
2. Reads $I_q$, $\omega$, $V_{bus}$ from ODrive
3. Reads power and cadence from trainer
4. Logs everything to a single CSV with aligned timestamps

---

## Test Procedures (Trainer-Based)

### Steady-State Efficiency Sweep

1. Set trainer to ERG mode at a target power (e.g., 10 W)
2. Command motor to constant velocity via ODrive
3. Wait for steady state (~5 s)
4. Log: ODrive $I_q$, $V_{bus}$, $\omega$ and trainer power, cadence for 10 s
5. $\eta = P_{trainer} / (V_{bus} \cdot I_q)$
6. Repeat at 10, 20, 30, 50, 75, 100 W (or whatever the gearbox can handle)
7. Plot $\eta$ vs load — this is the efficiency curve

### $K_t$ Calibration

1. Set trainer to ERG mode at a known power setpoint
2. Command motor at constant speed — trainer provides the resistive load
3. Compute trainer torque: $\tau_{trainer} = P_{trainer} / \omega_{output}$
4. Read $I_q$ from ODrive
5. $K_t = \tau_{trainer} / (I_q \cdot N \cdot \eta_{est})$ — iterate if needed, or test motor alone (no gearbox) for cleaner measurement
6. Compare to theoretical $K_t = 0.0551$ Nm/A

> **Cleaner $K_t$ calibration:** Remove the gearbox, couple motor shaft directly to trainer. Then $K_t = \tau_{trainer} / I_q$ with no gearbox losses in the loop. This requires a second adapter (motor shaft → freehub) but gives the cleanest number.

### Friction Torque (Backdriving)

1. Disconnect motor power (ODrive idle or disabled)
2. Use trainer in SIM mode to slowly drive the gearbox backwards
3. Read trainer power at the speed where the gearbox just barely turns
4. $\tau_f = P_{trainer} / \omega$ at that threshold
5. Sweep across several speeds to get the $\tau_f = \tau_c + b\omega$ curve

> **Note:** The freehub ratchet may complicate this — it freewheels in one direction. You may need to flip which device is driving vs. resisting, or accept testing friction in one direction only.

### Torque Capacity / Stall Test

1. Lock gearbox output (clamp adapter or use trainer at max resistance)
2. Slowly ramp motor current via ODrive
3. Monitor trainer torque (or use the stall condition where speed = 0 and $\tau = K_t \cdot I_q$)
4. Record max torque before: structural failure, gear skip, or current limit

---

## Limitations & Watch-Outs

| Issue | Impact | Mitigation |
|-------|--------|------------|
| **Freehub is one-way** | Can only resist torque in one direction | Test both directions by swapping which device drives |
| **4 Hz power data** | Too slow for transient tests | Use for steady-state only; ODrive data for dynamics |
| **±2% accuracy** | At 10 W that's ±0.2 W — fine. At 1 W it's ±0.02 W — might hit noise floor | Test at higher power levels for better accuracy |
| **Speed range** | Trainer designed for 60–100 RPM cycling cadence | QDD at 600 RPM output is outside normal range — stay below ~200 RPM for reliable trainer data |
| **Flywheel inertia** | 9 kg flywheel smooths out torque ripple | Good for steady-state, masks cogging. Not a problem — cogging is measured with ODrive anyway |
| **Not the gearbox output RPM** | Trainer reads its own internal cadence, not your shaft speed | Use ODrive encoder for speed; trainer for torque/power only |
| **Mounting alignment** | Gearbox + trainer must be coaxial | Build a jig — even rough alignment is fine if adapter has some float |

---

## Bill of Materials (Adapter)

| Item | Source | Est. Cost |
|------|--------|-----------|
| 3D printed adapter (PLA+/nylon) | Print | ~$1 material |
| Cassette lockring (Shimano compatible) | Bike shop / Amazon | ~$5 |
| Lockring tool (FR-5.2 or equivalent) | Bike shop / Amazon | ~$10 (or borrow) |
| ANT+ USB dongle (if using Option B) | Amazon | ~$25 |
| Mounting jig materials (plywood, bolts) | Hardware store | ~$10 |
| **Total** | | **~$50 or less** |

> **Shortcut option:** Scavenge a single cog from an old cassette (free if your friend has one), bore out the center, and bolt/epoxy to your output shaft adapter. Total cost: $0 + a lockring.

---

## Relationship to Test Campaign

This dyno setup augments the existing test campaign (test-campaign-rev00b.md) but doesn't replace it:

| Phase | Role of Trainer |
|-------|----------------|
| **Phase 0 (motor baseline)** | Optional — could do $K_t$ calibration here instead of T-009 sanity check |
| **Phase 1 (gearbox assembly)** | Not needed — these are fit/function checks |
| **Phase 2 (gearbox quantitative)** | **Primary use** — efficiency sweeps, friction measurement, torque capacity with calibrated load |
| **Phase 3 (controls)** | Not needed for step response / Bode (too slow). Could verify impedance controller output torque at steady state |
| **Phase 4 (endurance)** | Could provide sustained calibrated load for extended run tests |

---

## Next Steps

- [ ] Confirm access to the H2 — when can you borrow it?
- [ ] Measure the freehub body dimensions (calipers on the actual unit)
- [ ] Decide on adapter approach: CAD splines from scratch vs. repurpose a cassette cog
- [ ] Prototype adapter and test fit
- [ ] Set up data acquisition (ANT+ or BLE Python script)
- [ ] Run first calibration test: motor-only $K_t$ verification

---

## Sources

- [CycleOps H2 In-Depth Review — DC Rainmaker](https://www.dcrainmaker.com/2019/01/cycleops-h2-hammer-2-trainer-in-depth-review.html)
- [Saris Direct Drive Shimano/SRAM Freehub](https://saris.com/products/direct-drive-shimano-sram-trainer-freehub)
- [Shimano Cassette Bodies — Sheldon Brown](https://www.sheldonbrown.com/shimano-cassette-bodies.html)
- [Freehub & Cassette Compatibility — Shimano](https://productinfo.shimano.com/en/compatibility/C-731)
- [Freehub Compatibility Guide — Outside](https://velo.outsideonline.com/road/road-racing/a-guide-to-freehub-body-and-cassette-compatibility/)
