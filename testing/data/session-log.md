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
- `testing/campaign/sop-odrive-session.md` (new — full SOP)
- `testing/data/session-log.md` (this file)
- `testing/tools/odrive-control-panel.py` (new — GUI)
- `Desktop/ODrive Control Panel.lnk` (shortcut)
- `STATE.md` (updated file map)

### Next Session Plan
- Properly clamp/bolt motor before sustained testing
- Run Phase 0 tests (T-009, T-010, T-011, T-014) — requires removing gearbox
- Or start Phase 1 (T-012, T-013) with gearbox attached — backlash + hand backdriving
