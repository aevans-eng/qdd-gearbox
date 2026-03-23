# STATE — QDD Gearbox
> Last updated: 2026-03-22 (first power-on + control panel built)

## Status
Rev 00B printed and assembled. **First power-on complete** — motor calibrated, all control modes verified (velocity, position, torque), control panel GUI built. Supply voltage set to 48V (not 55V) after independent spec verification. Ready for Phase 0/1 testing.

## What Changed Last Session
- **First power-on and motor bring-up** — ODrive connected, calibrated, spun under all 3 control modes
- **Onboarding guide** from buddy moved to `testing/hardware/odrive-onboarding-guide.md`
- **SOP created** — `testing/campaign/sop-odrive-session.md` (safety checklists, startup sequence, emergency procedures)
- **Control panel GUI** — `testing/tools/odrive-control-panel.py` with desktop shortcut
  - Output shaft units, adjustable limits, trap trajectory position control, E-stop
- **Supply voltage reduced to 48V** — D6374 rated 48V max, 55V left only 5V regen headroom to 60V MOSFET limit
- **Session log started** — `testing/data/session-log.md`
- Zadig driver installed, odrive 0.5.4 Python package installed

## What's Next (Priority Order)
1. **Properly clamp motor** before sustained testing
2. **Phase 1 tests** (gearbox attached): T-012 backlash, T-013 hand backdriving
3. **Phase 0 tests** (motor only, requires gearbox removal): T-009 Kt verify, T-010 cogging, T-011 friction, T-014 step response
4. **Start workbook 01** (Motor Fundamentals) — work through open-book, bring to Claude for grading
5. Take hero photo of assembled Rev 00B
6. Update portfolio page with test data

## File Map
| What you need | Read this |
|--------------|-----------|
| Project rules & conventions | CLAUDE.md |
| **RTM — requirements, tests, traceability** | **testing/qdd-rtm.xlsx** |
| **Test campaign procedures** | **testing/campaign/test-campaign-rev00b.md** |
| **Session SOP (follow every time)** | **testing/campaign/sop-odrive-session.md** |
| **Session log** | **testing/data/session-log.md** |
| **Learning workbooks (13)** | **testing/learn/workbooks/** (progress: `_progress.md`) |
| Rev 00B scoped changes | prototypes/rev00b/changes.md |
| Rev 00B photos | prototypes/rev00b/photos/ |
| Official docs (content bank, media plan) | docs/official/ |
| Research (ODrive, impedance, PLA gears) | research/gemini-deep-research/01-actuator-testing-methodology/ |
| **ODrive onboarding guide** (setup, safety, gains, troubleshooting) | **testing/hardware/odrive-onboarding-guide.md** |
| Test bench design | testing/hardware/test-bench-design.md |
| Documentation index | docs/README.md |
| Design docs (tolerances, assembly, gear params) | docs/design/ |
| Future design ideas (bearing, housing, integration) | docs/design/future-ideas.md |
| CATIA workflows | docs/catia/ |
| Python calculators | calc/ (gear_geometry, tooth_stress, bearing_life, thermal) |
| Work logs | docs/log/ |
| Rev 00A fitment notes | prototypes/rev00a/notes.md |
| Old test tracker (archived) | testing/_archive/test-tracker-pre-rtm.md |

## Open Questions / Blockers
- Need quantitative test data for Rev 00B (backlash, friction torque)
- U-06 through U-10 not started (need Rev 00B test results first)
- Hero photo needed for portfolio thumbnail and LinkedIn

<!-- After updating this file, sync status to discovery-protocol.md registry -->
