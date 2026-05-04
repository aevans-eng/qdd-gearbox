# Test Session Log

> Record every test session. What was done, what was observed, what was anomalous.

---

## Session 001 — 2026-03-22

**Goal:** First power-on, verify connection, calibrate motor, build control GUI
**Config:** Gearbox attached (5:1 planetary)
**Supply:** RD6030 @ 48V (originally set to 55V by buddy, reduced for safety)

### Setup
- [x] Wiring verified — DC polarity correct, motor phases (A=red, B=yellow, C=blue), brake resistor on AUX, encoder on J4
- [x] RD6030: V-set=48V, I-set=5A, OVP=52V, OCP=8A (originals: OVP=57, OCP=25)
- [x] Zadig driver installed (WinUSB on Interface 2)
- [x] USB connection confirmed (requires DC power on through dock)
- [x] odrive 0.5.4 Python package installed
- [x] Motor secured (mostly — needs proper clamping before sustained testing)

### Activities
1. **Onboarding guide received** from buddy, moved from dropbox to `testing/hardware/odrive-onboarding-guide.md`
2. **Spec verification** — independently verified all electrical limits:
   - ODrive 3.6 56V: MOSFETs rated 60V abs max, 56V nominal
   - D6374 150KV: rated 48V max (ODrive motor guide), 70A peak
   - **Supply voltage reduced from 55V to 48V** — only 5V regen headroom at 55V, 12V at 48V
   - Brake resistor (2 ohm 50W): adequate up to ~20A motor current
3. **First connection** — `odrive.find_any()` takes ~65s through USB dock (hardware bottleneck, not fixable in software)
4. **First calibration** — state 3, successful:
   - R = 43.8 mOhm (nominal ~39 line-to-line / ~19.5 phase-neutral)
   - L = 22.2 uH (nominal ~23)
   - All errors = 0, brake resistor armed
5. **First spin** — velocity mode, 1 t/s with gearbox gains:
   - Velocity fluctuated 0.53–1.28 t/s (gearbox friction causes uneven speed, normal for PLA)
   - Iq ranged 1.4–3.8A
   - Gearbox sounded "a little crunchy" during cal (normal gear mesh noise)
6. **Headless test** — all 9 control checks passed:
   - Velocity mode, position mode, torque mode
   - E-stop (IDLE), telemetry reads, calibration verification
7. **Control panel GUI built** — `testing/tools/odrive-control-panel.py`:
   - Velocity/position/torque modes in output shaft units
   - Two-tier limits (user adjustable + absolute max)
   - Trap trajectory for position moves with adjustable speed
   - E-stop on spacebar/Escape, auto-IDLE on window close
   - Desktop shortcut created (pythonw, no console window)

### Key Decisions
- **48V not 55V** — D6374 rated for 48V max, 55V leaves only 5V regen headroom to 60V MOSFET limit
- **Gearbox stays attached** for now — Phase 0 (motor-only baseline) would require disassembly
- **5:1 gear ratio conversions** in GUI — all user-facing values in output shaft units

### Hardware Notes
- USB connection requires DC power to enumerate through dock
- Direct laptop USB works but dock is only option (no USB-A ports on laptop)
- Micro USB cable is flaky — had intermittent connection issues
- RD6030 reads 46.0V bus (vs 48.0V set) — normal regulation + cable voltage drop

### Health Check

| Metric | Value |
|--------|-------|
| Bus voltage | 46.0V |
| Phase R | 43.8 mOhm |
| Phase L | 22.2 uH (first cal), 21.9 uH (second cal) |
| Errors | 0 |
| Brake resistor | Armed, 2.0 ohm |
| Gearbox sound | Normal gear mesh, slight crunch |

### Files Created/Modified
- `testing/hardware/odrive-onboarding-guide.md` (moved from dropbox)
- `testing/hardware/sop-odrive-session.md` (new — full SOP)
- `testing/data/session-log.md` (this file)
- `testing/tools/odrive-control-panel.py` (new — GUI)
- `Desktop/ODrive Control Panel.lnk` (shortcut)
- `STATE.md` (updated file map)

### Next Session Plan
- Properly clamp/bolt motor before sustained testing
- Run Phase 0 tests (T-009, T-010, T-011, T-014) — requires removing gearbox
- Or start Phase 1 (T-012, T-013) with gearbox attached — backlash + hand backdriving

---

## Session 002 — 2026-03-22

**Goal:** Phase 1 mechanical tests — backlash and hand backdriving

### Activities
1. **Quick hand check** — spun output shaft, no significant lid drag after torquing lid. T-002 fix confirmed.
2. **T-012: Backlash measurement — PASS (0°)**
   - Motor phases shorted together for electromagnetic braking (locks input shaft)
   - Dial indicator clamped to housing, reading against screw threaded into output shaft
   - Wiggled output shaft back and forth — no measurable backlash
   - Photo of setup + video of measurement recorded
   - Result: 0° backlash (R-01 requirement: ≤ 0.5°) — clear pass
3. **Hockey stick adapter** — currently printing for T-013 hand backdriving torque measurement

### Key Observations
- Zero backlash suggests spur gear mesh is quite tight — good for precision, monitor for wear
- Lid drag fix (T-002) confirmed working — no parasitic drag with lid torqued

### Files Modified
- `testing/validation/test-tracker.md` (T-012 results)
- `testing/data/session-log.md` (this file)




DYNO DAY, PRE TESTING NOTES REV00B:

Coupling redesign notes:
- This coupling was a pain, the bore diameter was a tad small so it was a bit tight fitting onto the freehub, diameter could be a bit bigger
- The bolts are extremely anoying to get to, could possibly put them at an angle so its easier to access the bolts, and maybe only need 5
- Could also explore doing a transition fit coupling with a clamp connection, e.g transition fit with teeth and a band connection that goes over? Could design it like a blender tooth arrangement 
- I think a good option could just be to do a transition fit splines between the two pieces, and maybe have the fasteners going inwards radially? 
- Or maybe a transition fit splines, and each coupling has a groove which a clamp can go over to constrain the two together. 

 There is a noticeable backlash in the gearbox. Possibly due to it being taken apart and put back together as some of the plastic threads will wear out, and most likely the gears such as ring and planets being assembled in different directions (they likely slightly wore in). And although this shouldnt affect anything but the top of the sun gear, the teeth got chamfered and worn as it was contacting the top of the carrier as it was sitting a bit high. A thin coat of lithium grease was applied to the gears. Going to measure backlash before running the dyno, and measure after. Also going to measure the torque required to overcome friction. The coupling adapter isnt alligned great, it doesnt index with the output shaft or anything, and the holes are clearance, should be okay thouhg. Backlash could have also been worsened as the gearbox was ran without lubrication. It could also be due to a change in allignment of the carrier (the planets are slightly outwards or inwards from the center line they should be traveling on). 
Before testing: 
3 thou backlash (will need to be converted to angular backlash)
Coupler to trainer the cutout diam needs to be a tad bigger, its too tight.

During Testing:
- It spun, testing stand worked, coupling worked, although PIA, 
- During testing the motor eventually got to 60 degrees c (at coils) and later in testing it tried to spin but didnt end up spinning the coupling (the shaft likely rounded in the sun gear)
Next:
- Need better coupling desing, that is easier to remove, and faster to assemble
- Need to attatch sun gear better, or have better heat management?
- Design gearbox with better mounting solutions
- Design motor housing with better mounting solutions/cooling
- Sun gear:
	- Going to make a woodruff key version and a 3d printed woodruff key
- Coupling:
	- Going to create an indexing version, with radial screws to retain them, will be a transition fit
	- Needs a little more clearance on the bore for freehub interface

Post:
- Was indeed the sun gear rounding out, this will be a hard issue to overcome
- 

---

## Session 003 - 2026-04-18

**Goal:** Re-establish the current test stack around the `MKS XDrive Mini`, verify `Hammer H2` comms, and prepare the bare-motor first-spin workflow.
**Config:** Bare motor planning with `D6374 150KV`, `MKS XDrive Mini v1`, `AMT 102-V` incremental encoder

### Equipment Confirmed
- Controller: `MKS XDrive Mini v1`
- Motor: `D6374 150KV`
- Encoder: `CUI AMT 102-V`
- Trainer: `Saris / CycleOps Hammer H2`
- Local Python for tools: `C:\Users\aaron\miniconda3\python.exe`

### Activities
1. **Hammer H2 BLE discovery confirmed**
   - Scan found `Hammer 52942`
   - BLE address: `EE:51:A8:51:70:1A`
2. **Hammer H2 capture path confirmed**
   - `dyno.py capture` connected and logged notifications
   - Smoke-test files created under `saris-h2-dyno/runs/`
3. **Hand-spin data remained idle**
   - connection was real
   - notifications were real
   - captured power / RPM stayed at zero during hand-spin attempts
   - conclusion: trainer connectivity is proven, but hand-spin is not yet a reliable motion validation method
4. **XDrive Mini bring-up docs updated**
   - added bare-motor bring-up guide
   - corrected smart-trainer notes to match the local BLE CPS tooling
5. **First-spin helper created**
   - new tool: `testing/tools/xdrive_first_spin.py`
   - purpose: conservative configure + calibrate + short velocity spin from one command

### Key Decisions
- Active controller path is now `MKS XDrive Mini`, not the original ODrive 3.6
- Confirmed encoder for first spin is `AMT 102-V`, so the default path is **incremental encoder mode**
- H2 discovery and connection are good enough; do not spend more time re-proving BLE scan

### Notes
- In this PowerShell session, `python` and `py` were not on PATH
- Reliable interpreter path:
  - `C:\Users\aaron\miniconda3\python.exe`
- The next real blocker is XDrive Mini controller connection and calibration, not H2 communications

### Files Created / Modified
- `testing/hardware/xdrive-mini-bare-motor-setup.md`
- `testing/dyno/README.md`
- `testing/README.md`
- `testing/tools/xdrive_first_spin.py`
- `testing/data/session-log.md`

### Next Session Plan
- Power the XDrive Mini bench with a current-limited supply
- Connect USB and confirm `odrive.find_any()` sees the board
- Run `xdrive_first_spin.py` in incremental mode for the `AMT 102-V`
- If calibration fails, record exact axis / motor / encoder errors before changing settings

### Bring-Up Result Update
- USB probe succeeded on the XDrive Mini
- Confirmed board summary during first bring-up:
  - bus voltage about `24.0 V`
  - `current_lim = 5.0 A`
  - `pole_pairs = 7`
  - `encoder CPR = 8192`
  - watchdog disabled
- The previous board config had been set for a different encoder path (`CPR 16384`)
- After reconfiguring to incremental mode, calibration still failed due to encoder feedback issues
- Current blocking error:
  - `ENCODER_ERROR_NO_RESPONSE`
- Working conclusion:
  - controller comms are alive
  - motor config is at least partially applied
  - the next issue to solve is encoder wiring / signal / response, not USB discovery

---

## Session 004 - 2026-04-24

**Goal:** Recover reliable USB bring-up on the `MKS ODrive Mini v1.0` and continue toward first spin.
**Config:** Bare motor, `D6374 150KV`, `CUI AMT 102-V`, supply at about `24 V`

### Findings
1. **Windows USB enumeration was healthy**
   - device showed up as `ODrive 3.6 Native Interface`
   - Zadig native-interface driver was reinstalled with no change to the handshake problem
2. **Primary blocker was PC-side stack compatibility, not encoder response**
   - `odrive==0.5.4` consistently hung at `odrive.find_any()`
   - switching to `odrive==0.5.1.post0` changed the failure mode immediately, which matched the Makerbase `0.5.1` firmware family better
3. **Second blocker was missing PyUSB backend**
   - `odrive==0.5.1.post0` initially failed with `usb.core.NoBackendError: No backend available`
   - adding `libusb-package` and exposing its DLL path fixed the backend issue
4. **Controller comms are now working**
   - successful handshake in about `0.63 s`
   - serial: `62080355742261`
   - bus voltage: about `24.0 V`
   - axis state: `IDLE`
5. **No active encoder fault at idle**
   - first readback showed latched faults: `AXIS_ERROR_MOTOR_FAILED` and `MOTOR_ERROR_CURRENT_LIMIT_VIOLATION`
   - after clearing stale errors: axis=`0`, motor=`0`, encoder=`0`
6. **Bare-motor calibration and first spin succeeded**
   - re-applied conservative config for incremental encoder mode at `8192 CPR`
   - full calibration passed with:
     - phase resistance about `48.67 mOhm`
     - phase inductance about `22.23 uH`
   - first motion command succeeded at `0.1 turns/s` for `1.0 s`
   - returned to `IDLE` with axis=`0`, motor=`0`, encoder=`0`
7. **MKS wrapper path repaired**
   - sprint PowerShell wrappers now prefer the local `.venv-odrive051` env and expose the `libusb` DLL path automatically
   - `mks_agent_control.py` needed clone-specific fixes:
     - do not arm watchdog during probe/status/calibrate-only flows
     - clear stale controller faults
     - set control mode before requesting closed loop
   - after those fixes, `10-agent-control.ps1` could complete a self-contained velocity command with no reported errors
8. **Motion is electrically clean but still needs operator confirmation**
   - helper and wrapper commands both complete with zero reported faults
   - telemetry shows only modest encoder position change during low-speed commands, so visual confirmation of actual rotor spin still matters
   - likely next bench checks if motion is weak or partial:
     - confirm AMT-102 resolution setting really matches `8192 CPR` assumption
     - increase command in small steps only after visual confirmation
9. **First motor-plus-coupling inertia estimate captured**
   - logged a low-torque spin-up / coast-down dataset to:
     - `testing/data/motor-inertia-log-20260424-143504.csv`
   - simple fit of `tau = J*alpha + B*omega + Tc*sign(omega)` gave:
     - `J ~= 1.67e-4 kg*m^2`
     - `B ~= 2.77e-4 N*m*s/rad`
     - `Tc ~= 2.35e-2 N*m`
   - fit quality was only moderate (`R^2 ~= 0.43`), so treat this as a first-order estimate for the **bare motor + attached coupling**, not a final characterization value

### Files Modified
- `testing/mks-xdrive-mini/requirements.txt`
- `testing/mks-xdrive-mini/*.ps1` wrappers updated to prefer the working `0.5.1.post0` env
- `testing/mks-xdrive-mini/mks_agent_control.py`
- `testing/data/session-log.md`

### Next Session Plan
- Keep the MKS stack on the `0.5.1.post0` env
- Repeat tiny motion with operator observation, then step speed up gradually
- If motion remains clean, move to the agent CLI / smoke-test wrappers for normal sessions

---

## Session 005 - 2026-05-03

**Goal:** Bring up basic thermistor temperature logging for gearbox thermal tests.

### Setup
- Arduino Uno on `COM6`
- Serial baud `115200`
- Thermistor: `10k NTC`, `Beta 3435`
- Measured Arduino 5V rail: `4.35 V`
- Divider assumption in sketch: `5V -> 10k fixed resistor -> A0 -> thermistor -> GND`

### Activities
1. Created Arduino sketch for thermistor voltage-divider logging:
   - `testing/temperature-logger/arduino/qdd_thermistor_logger/qdd_thermistor_logger.ino`
   - CSV output: `time_ms,adc_counts,voltage_v,resistance_ohm,temp_c,temp_f`
   - optional Arduino Serial Plotter mode
   - optional I2C LCD hook
2. Corrected thermistor calibration from generic `Beta 3950` to actual `Beta 3435`.
3. Updated voltage reference assumption to the measured Arduino rail value: `4.35 V`.
4. Compiled and uploaded the sketch to the Arduino Uno.
5. Created Python serial logger:
   - `testing/temperature-logger/log_thermistor.py`
   - writes timestamped CSV files into `testing/data/`
   - adds PC timestamp column for test correlation
6. Added motor-test wrapper:
   - `testing/temperature-logger/run_motor_temp_test.ps1`
   - starts temp logging, runs one MKS command, then keeps logging briefly after motion
   - leaves the existing MKS motor-control code unchanged
7. Captured powered-test synchronization concept:
   - `testing/validation/motor-dyno-temp-conops.md`
   - defines PC timestamps, event markers, sync step, steady-state analysis windows, and run manifests
8. Cleaned up the active testing folder:
   - summarized `GEAR TESTING BRAINSTORM.md` into `testing/future-work.md`
   - archived the raw brainstorm and old sprint plan under `testing/_archive/`
   - moved `testing/01 stuff/` to `testing/_archive/unsorted-hardware-2026-05-03/`
   - moved short thermistor sanity captures to `testing/data/scratch/`
   - consolidated MKS controller scripts/docs under `testing/mks-xdrive-mini/`
   - archived duplicate/legacy motor-control files under `testing/_archive/tool-overlap-cleanup-2026-05-03/`
   - moved Ishikawa/root-cause files from `testing/tools/` to `testing/validation/`
   - removed the generic `testing/tools/` layer:
     - thermistor logger moved to `testing/temperature-logger/`
     - Hammer H2 docs and BLE tool consolidated under `testing/dyno/`
9. Installed `pyserial` into `C:\Users\aaron\miniconda3\python.exe`.
10. Ran logger sanity captures:
   - `testing/data/scratch/thermistor-log-20260503-135211.csv`
   - `testing/data/scratch/thermistor-log-20260503-141543.csv`
   - reading stable around `23.8 C`

### Key Decisions
- Keep the Arduino output as plain CSV by default for logging.
- Use Python for actual test capture instead of copying from Serial Monitor.
- Integrate motor testing with a wrapper script rather than modifying the MKS control path.
- Synchronize motor/dyno/temp streams using PC timestamps plus event markers and a deliberate step input, then analyze steady-state windows.
- Store raw logs in `testing/data/` and reference them from formal test logs.

### Next Session Plan
- Before thermal testing, measure Arduino `5V` and fixed resistor value, then update `VREF_VOLTS` and `FIXED_RESISTOR_OHMS` if needed.
- During T-021/T-023, use `run_motor_temp_test.ps1` for synchronized motor command plus temperature capture, then record the generated CSV filename in `testing/validation/test-log.md`.

---

## Session 006 - 2026-05-03

**Goal:** First powered run on Saris H2 dyno — verify motor + dyno + temp logging integration end-to-end. Pre-Phase-2 bring-up, NOT a formal characterization run.

**Config:**
- Motor: MKS XDrive Mini (ODrive-clone), motor coupled directly to dyno trainer
- Gearbox: not installed in this drivetrain for this session
- Dyno: Saris H2, mechanically coupled to motor through the trainer/cassette-side adapter
- PSU: 24 V, 3 A current limit
- Arduino temp logger active on COM6, writing to `thermistor-log-20260503-164329.csv`

### Confirmed Working
- Dyno BLE link alive (`Hammer 52942 at EE:51:A8:51:70:1A`); `dyno.py scan` and `capture` both functional once trainer is awake.
- Temp logger continues to stream correctly to CSV with `pc_timestamp` column.
- ODrive USB connection works through `.venv-odrive051` once `libusb_package` directory is on `PATH` (handled by `mks-python-env.ps1`).
- Encoder + motor errors stayed at 0 across all attempts.

### Observations (verified, not interpreted)

1. **Motor was found in `CLOSED_LOOP_CONTROL` (state=8) at session start**, holding 1.14 A Iq with vel=0. Origin unknown — predates this session. Idled to state=1 before any further action. Worth flagging: violates the "do not leave axis in closed loop unattended" rule from `safety-checklist.md`.

2. **Velocity-loop gains differ from `mks_agent_control.py` gearbox profile.** Live values dumped from controller:
   - `vel_gain = 0.05` (gearbox profile expects 0.10)
   - `vel_integrator_gain = 0.05` (gearbox profile expects 0.20)
   - `pos_gain = 5.0` (gearbox profile expects 15.0)
   - These never persisted; cause not investigated this session. (Possibly because `mks_agent_control.py` only applies them inside its self-contained motion path, and the standalone safe_ramp_test.py script doesn't.)

3. **`motor.config.torque_constant = 0.04 Nm/A`** — differs from documented `Kt = 0.0551 Nm/A` used elsewhere in the project. Source of the 0.04 not investigated. ODrive uses this internally to convert torque-loop output to Iq command, so it affects velocity-loop response.

4. **First powered ramp attempts (both directions) stalled.** Test parameters:
   - Script: `testing/mks-xdrive-mini/safe_ramp_test.py` (new — see below)
   - control_mode = VELOCITY, input_mode = VEL_RAMP, vel_ramp_rate = 2.0 turns/s² (motor)
   - Targets attempted: +0.5, then -0.5 motor turns/s, hold 3 s
   - current_lim = 5 A
   - Result: encoder vel_estimate stayed at 0.000 throughout. Iq integrator wound up monotonically to ±2.55 A and held until ramp-down. Dyno CSV (`probe_v4_2026-05-03.csv`) recorded `wheel_revs = 0` for the entire 30-second window. No errors raised.

5. **Iq plateau matches predicted output of the soft gains.** With `vel_gain=0.05 Nm/(turn/s)` and `vel_integrator_gain=0.05 Nm/(turn × s)` integrated over 3 s × 0.5 turn/s vel-error: predicted torque ~0.1 Nm motor / Iq ~2.5 A. Matches observed 2.5 A. So: the controller did exactly what its gains commanded; it simply never asked for more current than that within the test window.

6. **Hand-rotation check (Aaron, motor IDLE):** looking at the cassette side, **CCW is the non-engagement/freewheel direction**. In that direction the coupled drivetrain spins freely by hand, and everything visible spins together. Engagement direction not separately characterized by hand this session.

7. **Separate bench-panel check (Aaron):** using the MKS motor bench panel tester on the desktop, Aaron was able to spin the motor. This suggests the motor/controller/hardware path can produce motion; the stalled `safe_ramp_test.py` attempts may be specific to script configuration, gains, command sign, applied torque/current, or test setup state. Exact bench-panel command mode, speed/torque/current, and direction were not recorded.

### Not Confirmed (open questions)

- **Which sign of motor velocity = freewheel direction.** Both signs stalled with the same magnitude of integrator wind-up; we cannot infer direction mapping from a stall.
- **Cause of stall in `safe_ramp_test.py`.** With only ~0.1 Nm motor torque applied by the soft velocity-loop gains, we don't know whether the wheel didn't move because of (a) command sign not mapped to the freewheel direction, (b) freehub/clutch breakaway or trainer inertia, (c) under-torqued by soft gains, (d) script/profile mismatch relative to the bench panel, or (e) Kt mismatch shrinking actual delivered torque relative to expected. Nothing in the logged data isolates these.
- **Whether torque_constant=0.04 is correct, or stale calibration data overriding the documented 0.0551.**

### PSU Math (for the record)

PSU is 24 V / 3 A max. At stall, bus current ≈ 1.5 × R × Iq² / V_bus = 1.5 × 0.049 × Iq² / 24. Even at Iq = 10 A stalled, bus current ≈ 0.31 A — well under the PSU limit. The 3 A constraint will become relevant once the motor is *moving under load* (back-EMF + mechanical work raise bus current). Not a constraint at the breakaway-search stage.

### Files Created/Modified
- `testing/mks-xdrive-mini/safe_ramp_test.py` (new) — single-shot ramped velocity test. Self-contained: connect → idle → set INPUT_MODE_VEL_RAMP + watchdog → closed loop → ramp to target → hold → ramp down → idle. Streams `t/cmd/vel/iq` to stdout each 0.2 s. Exists to enforce the "no step inputs on dyno" rule, which `mks_agent_control.py` does not (it sets `input_mode=1` PASSTHROUGH in `set_velocity`).
- Dyno captures: `runs/probe_2026-05-03.csv`, `probe_v2_2026-05-03.csv`, `probe_v3_2026-05-03.csv`, `probe_v4_2026-05-03.csv`, `probe_neg_2026-05-03.csv` (most are baseline-only — see Tooling Note below).
- Temp log: `testing/data/thermistor-log-20260503-164329.csv` (continuous across session).

### Tooling Note — Synchronization Friction

Dyno BLE connect is faster than expected (~1-2 s once trainer is awake). When launching dyno capture as a background task and motor command after a sleep, the capture window can elapse before motor activity. Working approach: launch dyno capture (background) and motor probe (foreground via PowerShell with the venv env) back-to-back; the motor's USB connect (~3-5 s) gives the dyno enough lead time. A more robust approach for future runs: have the motor script signal "ready" before issuing motion, and have the dyno capture start triggered by that signal — or simply use a longer dyno capture (45-60 s) so timing slop doesn't matter.

### Open Bug — `mks_agent_control.py` velocity command is a step

`set_velocity()` and `prepare_mode("velocity")` both write `controller.config.input_mode = 1` (PASSTHROUGH) before issuing `input_vel`. The `vel_ramp_rate` configured in the gearbox profile is therefore inactive during velocity commands — every velocity command is a hard step. This contradicts the "ramp only for dyno runs" operating rule. Not patched this session (Aaron preferred manual control first); flagged for follow-up.

### Next Session Plan

- **Before commanding more torque, compare the bench panel path to `safe_ramp_test.py`:** record panel command mode, direction, speed/torque/current settings, and whether CCW-looking-from-cassette corresponds to positive or negative motor velocity in ODrive units.
- **Repeat hand-rotation check only as needed:** confirm freewheel direction is still CCW looking at the cassette, and confirm engagement direction loads the flywheel. The gearbox is not installed in this setup, so do not attribute this session's stall to gearbox friction.
- **Investigate why `vel_gain/vel_integrator_gain` reverted to 0.05/0.05** — likely the gearbox profile is only applied within `mks_agent_control.py`'s session; standalone scripts inherit whatever was last saved/persisted. Decide whether to apply the profile in `safe_ramp_test.py` or write to ODrive nonvolatile config once.
- **Investigate `torque_constant = 0.04` vs documented `0.0551`.** May be from an old cal. Re-running motor cal off-dyno (motor only, freed) would give a clean number. Until resolved, treat ODrive torque numbers with skepticism.
- **Then retry powered ramp** with: (a) gearbox-profile gains applied, (b) current_lim raised to ~8 A, (c) target ~1.0 motor turns/s, (d) ramp_rate kept at 2.0. If breakaway still doesn't happen, switch to torque-control mode and ramp torque manually to find breakaway, which is more diagnostic than velocity-loop wind-up.
- **Patch `mks_agent_control.py` velocity-mode bug** (input_mode 1 → 2) so the documented "ramp only" rule actually holds when that path is used in the future.

---

## Session 007 — 2026-05-03 (afternoon)

**Goal:** Get a valid bare-motor efficiency baseline.
**Config:** Bare motor (no gearbox) on Hammer trainer, MKS xDrive Mini, PSU 24 V / 10 A.

**Outcome:** No valid efficiency data. Multiple attempts at positive torque (20 A, 40 A) stalled the trainer. Negative-velocity (-1.67 t/s @ 20 A) oversped to +27 t/s and tripped current limit. Established preflight + safety procedures.

Full handoff: [`session-007-dyno-testing-handoff.md`](session-007-dyno-testing-handoff.md)

---

## Session 008 — 2026-05-03 (evening)

**Goal:** Bare-motor efficiency baseline, retry with diagnostics.
**Config:** Bare motor, Hammer trainer, MKS xDrive Mini, PSU 24 V / 10 A.

**Outcome:** No valid efficiency data, but found and fixed five real bugs in the synced harness, and confirmed a hard physical limit: bare motor at this controller's effective ~70 A Iq cap (≈ 2.8 Nm) cannot break the trainer's loaded-direction static load in this setup. After 150 s pinned at 70 A Iq with `vel = 0`, motor heated +9.07 °C, FET 54 °C, 232 W dissipated as heat, no rotation. Hammer logged zero rpm/power.

**Key realization:** every session-006 run that previously "worked" was negative-direction (freewheel) at low speed — there is no precedent for the bare motor driving the trainer's loaded direction in any logged session. Session 007's "don't run negative" rule was specifically about overspeed at higher negative targets, not about positive being viable bare-motor.

**Harness bugs fixed (all silent failure modes that wasted runs):**
1. `safe_ramp_test.py` velocity loop never checked `ax.current_state` — silent disarms went undetected, script logged stale Iq for 90+ s and reported "completed".
2. Sticky axis errors didn't clear with per-subobject `target.error = 0`; needed device-level `odrv.clear_errors()` and watchdog-disable-before-clear.
3. Enabling watchdog without immediate `watchdog_feed()` instantly tripped `axis=2048` (WATCHDOG_TIMER_EXPIRED) on every retry.
4. `run_synced_motor_dyno_temp.ps1` manifest write had only 5×150 ms retries; AV/file-indexer locked the new file → parent script threw → orphaned Python jobs → orphaned watchdog timeout → sticky errors. Bumped to 20×500 ms with warn-not-throw.
5. Manifest summary's `motor_max_torque_nm` reports the velocity setpoint when run in velocity mode (column-position confusion). Not fixed; just be aware.

**Tooling changed:** `safe_ramp_test.py`, `safe_torque_ramp_test.py`, `run_synced_motor_dyno_temp.ps1`. See full handoff: [`session-008-bare-baseline-handoff.md`](session-008-bare-baseline-handoff.md).

**Recovery procedure for sticky axis errors:** software clear sometimes works with the new sequence; if not, **power-cycle PSU** (only reliable reset for some sticky bits — observed `axis=48`, `16`, `2048`).

**Next session — three options for R-09:**
1. Hand-spin start to break stiction, motor maintains.
2. Higher current burst (100–120 A peak, ≤ 10 s, strict thermal abort).
3. Change methodology — characterize bare motor in freewheel direction at low load, gearbox-installed in loaded direction, infer gearbox-only efficiency from motor losses. Most rigorous; avoids the bare-motor-can't-drive-trainer wall.

The 5:1 gearbox exists *because* the bare motor doesn't have enough torque to drive these loads. Hitting this wall is consistent with the design rationale.
