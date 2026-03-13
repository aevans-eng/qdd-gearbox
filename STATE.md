# STATE — QDD Gearbox
> Last updated: 2026-03-13 (test review complete, Rev 00B changes scoped)

## Status
Testing Rev 00A complete → Rev 00B design changes scoped, ready for CATIA.

## What Changed Last Session
- Completed review of all 5 tests (T-001 through T-005)
- Identified root causes for 4 major issues
- Created Rev 00B changes consolidation doc
- T-004 (carrier indexing) resolved — deprioritized
- T-005 (bolt torque sensitivity) confirmed shoulder redesign needed

## What's Next (Priority Order)
1. Implement Rev 00B must-have changes in CATIA (5 changes — see prototypes/rev00b/changes.md)
2. Print Rev 00B prototype
3. Re-run validation tests on Rev 00B
4. Quantitative shoulder deformation measurement (T-003 follow-up)

## File Map
| What you need | Read this |
|--------------|-----------|
| Project rules & conventions | CLAUDE.md |
| Test tracker & unknowns registry | testing/test-tracker.md |
| Rev 00B scoped changes | prototypes/rev00b/changes.md |
| Test bench design | testing/test-bench-design.md |
| Documentation index | docs/README.md |
| Design docs (tolerances, assembly, gear params) | docs/design/ |
| CATIA workflows | docs/catia/ |
| Python calculators | calc/ (gear_geometry, tooth_stress, bearing_life, thermal) |
| Work logs | docs/log/ |
| Rev 00A fitment notes | prototypes/rev00a/notes.md |

## Open Questions / Blockers
- Quantitative shoulder deformation data needed (visual assessment only so far)
- 3D printer dimensional bias on sun-planet clearance unknown
- U-06 through U-10 not started (future gates — need Rev 00B first)

<!-- After updating this file, sync status to discovery-protocol.md registry -->
