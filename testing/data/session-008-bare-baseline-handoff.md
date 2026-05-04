# Session 008 — Bare Motor Baseline Handoff

Date: 2026-05-03 (evening, follows session 007 same day)

## Summary

We did **not** capture a valid bare-motor efficiency baseline. We did:

- Find and fix five real bugs in the synced test harness.
- Confirm a hard physical limit: bare motor at `~70 A` Iq (≈ `2.8 Nm`) cannot break the trainer's static load in the positive (loaded) direction in this configuration.
- Re-confirm that the negative ("freewheel") direction can be driven slowly with low current — that's the only direction that has ever moved the trainer bare-motor in any logged session today.

Do not claim any efficiency result from this session. Logs are diagnostic only.

## Important Context — What "Worked Before" Was Negative Direction

Earlier session-006 runs that Aaron remembered as "working":

| Run | Mode | Target | Max abs vel | Notes |
|---|---|---|---|---|
| `synced-bare-driven-30a-…-191239` | torque | **−1.2 Nm** | 0.687 t/s | clean |
| `synced-bare-driven-30a-hold-…-192037` | torque | **−1.2 Nm** | 0.687 t/s | clean |
| `synced-bare-driven-velocity-30a-…-192638` | velocity | **−2.0 t/s** | 0.549 t/s | clean |
| `synced-bare-baseline-efficiency-…-195612` | torque | **−1.2 Nm** | spiked to 44.9 t/s | overspeed event |

**All four were negative direction.** No prior session has ever driven the trainer in the positive (loaded) direction with the bare motor. Session 007's "don't run negative" rule was specifically about the overspeed/runaway risk at higher negative targets, not about positive being viable bare-motor.

## Harness Bugs Found and Fixed (2026-05-03 PM)

All of these were silent failure modes that wasted runs and produced misleading "completed" status. Each is fixed in code now.

| # | Bug | Fix | Files |
|---|---|---|---|
| 1 | The velocity-mode loop never checked `ax.current_state`. If the controller silently dropped to IDLE, the script logged stale Iq values for the rest of the run and reported "completed". | Added in-loop `current_state` check that prints `disarm_reason`, `active_errors`, all per-subobject errors, and aborts the run cleanly. | `safe_ramp_test.py`, `safe_torque_ramp_test.py` |
| 2 | Sticky axis errors (e.g. `axis=48`) didn't clear with `target.error = 0` per-subobject — needed device-level `odrv.clear_errors()` and even that couldn't always clear watchdog-related bits while watchdog was enabled. | Sequence is now: `requested_state=IDLE` → `enable_watchdog=False` → `odrv.clear_errors()` → per-target `error=0` → print post-clear state. | both scripts |
| 3 | After enabling watchdog and before transitioning to CLOSED_LOOP, watchdog tripped instantly (firmware sees stale "last fed" time). Result: `axis=2048` (WATCHDOG_TIMER_EXPIRED) sticky on every retry. | Added `watchdog_feed()` immediately after `enable_watchdog=True`, then a second `clear_errors()` pass, then transition. | both scripts |
| 4 | `run_synced_motor_dyno_temp.ps1`'s manifest write had only 5 retries × 150 ms backoff (~2 s total). When AV/file-indexer locked the brand-new `manifest.json`, the parent script threw — orphaning the Python jobs, which then watchdog-timed-out and left the controller with sticky errors. | Bumped to 20 retries × 500 ms (10 s total); warns instead of throwing. Parent stays alive even on a locked manifest. | `run_synced_motor_dyno_temp.ps1` |
| 5 | Manifest summary stats parser couldn't tell torque-mode vs velocity-mode column meaning — "motor_max_torque_nm" in summary actually reports the velocity setpoint when run in velocity mode. | Not fixed — just be aware: when reading a summary from a velocity-mode run, ignore the `motor_*_torque_nm` fields. | n/a |

## Recovery Procedure (Sticky Axis Errors)

When a run fails to enter CLOSED_LOOP and prints `err axis=<nonzero>`:

1. Try one more launch — the new clear sequence may unstick certain bits.
2. If still sticky: **power-cycle the PSU** (off, count to 5, on). This is the only reliable reset for some sticky bits.
3. Verify clean state: `vbus≈24 V`, `state=1` (IDLE), `err axis=0 motor=0 enc=0`.
4. Re-run.

Common sticky axis-error values seen this session:
- `48` = `0x30` — combination, includes WATCHDOG-related bits
- `16` = `0x10` — typically ESTOP/under-voltage area
- `2048` = `0x800` — WATCHDOG_TIMER_EXPIRED
- Motor `32768` = `0x8000` — current-sense saturation area

## Physical Findings

### Bare motor positive (loaded) direction

Tested this session at progressively higher targets:

| Target | Current limit | Outcome |
|---|---|---|
| velocity +1.67 t/s | 20 A | Iq saturated 20 A, vel = 0, motor stalled |
| velocity +1.67 t/s | 60 A | Iq peaked 68.7 A, vel = 0.275 t/s briefly, controller silently disarmed |
| velocity +8.33 t/s | 90 A | Iq saturated 70 A, vel = -0.137 t/s briefly, **silent disarm at t=21 s** (this is what triggered the diagnostic-bug hunt) |
| **torque +2.8 Nm** | **70 A** | **Clean 150 s run.** Iq pinned 69.8 A, vel = **0** entire run, motor temp +9.07 °C, FET 54 °C, DC power 232 W (all dissipated as heat). |
| torque +4.0 Nm | 100 A | sticky-error chain, never executed cleanly |

Conclusion: **bare motor at this controller's effective ~70 A Iq cap (≈ 2.8 Nm) cannot break the trainer's loaded-direction static load in this setup.** Possible exceptions:
- Hand-spinning the wheel to break stiction, then motor maintains at lower steady-state torque.
- Higher current limit (>90 A peak), accepting thermal risk; never confirmed working.
- Different mechanical setup that we haven't characterized.

### Negative (freewheel) direction

Confirmed working from session-006 logs at 30 A → 0.5–0.7 t/s. Hammer rarely produces useful power data in this direction because the resistance unit isn't loaded.

### Encoder vs. visible motion

At one point Aaron observed the dyno wheel spinning while logged motor encoder velocity stayed at 0. Possible causes (not isolated):
- Shaft coupling slipping under load
- Encoder resolution at very low rpm
- Brief motion below sampling resolution

Not chased this session.

## Hammer (BLE) Notes

- Hammer is named in the BLE config by address. If the trainer is asleep, direct connect by address fails and the script falls back to a 5 s scan. If it's powered off or out of range, the dyno script exits with "No Hammer trainer found" and the run produces zero dyno samples.
- One run this session failed BLE because the trainer wasn't awake. Always verify Hammer is awake (and ideally already showing in a fresh BLE scan) before launching a synced run.

## Tooling Changed This Session

- `testing/mks-xdrive-mini/safe_ramp_test.py` — bug 1, 2, 3 fixes.
- `testing/mks-xdrive-mini/safe_torque_ramp_test.py` — bug 1, 2, 3 fixes.
- `testing/run_synced_motor_dyno_temp.ps1` — bug 4 fix (manifest-write robustness).
- `testing/OFFICIAL-DYNO-TESTING.md` — direction notes updated to reflect the bare-motor torque limit.
- `testing/data/session-log.md` — session-008 entry appended.

No physics or test-methodology changes; just diagnostic visibility and recovery robustness.

## Recommended Next Session

The bare-motor matched-load baseline against the loaded direction is blocked by torque. Three real options to discuss with Russell / before next dyno time:

1. **Hand-spin start.** Apply 2.8 Nm at 70 A, hand-spin the wheel during the hold to break stiction, motor maintains. Hacky but produces matched-load data.
2. **Higher current burst.** Try 100–120 A peak for ≤ 10 s with strict thermal abort. If it breaks free, current naturally drops as the flywheel accelerates. If not, FET trips and we abort cleanly.
3. **Change the methodology for R-09.** Characterize bare motor in freewheel direction at low load (motor input W vs estimated motor mech W). Characterize gearbox-installed in loaded direction (full-system input W vs Hammer output W). Compute gearbox-only efficiency by inferring motor losses from the bare curve at matched motor torque/speed. More rigorous than matched-trainer-speed comparison and avoids the bare-motor torque wall entirely.

The 5:1 gearbox exists *because* the bare motor can't drive these loads directly. Hitting this wall is consistent with the design rationale.

## Resume Checklist (Updated)

Before any powered run:

- Controller powered, USB API reachable.
- Controller state `IDLE`, all errors `0` (axis, motor, encoder, controller). If anything nonzero, **power-cycle PSU first**.
- Encoder ready.
- **Hammer awake and visible in a fresh BLE scan** (run a quick scan; do not rely on cached connection).
- Arduino temp logger visible on `COM6`.
- PSU at `24 V`, `10 A`, OVP `30 V`, OCP `10 A`.
- Fan cooling controller and motor.
- Tiny preflight: `.\run_official_requirement_test.ps1 -TestStage PreflightDirection`.

When a run fails:

- Read the new state-watch printout in `motor.log` — it will tell you `disarm_reason`, `active_errors`, and per-subobject error codes at the moment of disarm. This is your first-line diagnostic.
- Read manifest summary `motor_exit_code` and `dyno_exit_code`. Nonzero = real failure.
- If sticky errors after a software clear: **power-cycle PSU**.
