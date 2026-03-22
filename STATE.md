# STATE — QDD Gearbox
> Last updated: 2026-03-20 (learning system created)

## Status
Rev 00B printed and assembled. RTM created. **Learning system built:** 13 workbooks covering motor physics through FEA literacy, with grading workflow and progress tracker. Ready to start Phase 0 testing and workbook study in parallel.

## What Changed Last Session
- Created **QDD Learning System** — 13 graded workbooks (`testing/learn/workbooks/01-*.md` through `13-*.md`)
  - 141 total questions across concept checks, applied problems, design judgment, and teach-it sections
  - Progress tracker at `testing/learn/workbooks/_progress.md`
  - Spec: `docs/specs/2026-03-20-qdd-learning-system-design.md`
  - Plan: `docs/specs/2026-03-20-qdd-learning-system-plan.md`
- All workbooks formatted with checkbox confidence ratings, response areas, and "How to use" instructions

## What's Next (Priority Order)
1. **Start workbook 01** (Motor Fundamentals) — work through open-book, bring to Claude for grading
2. **Execute test campaign** — `testing/test-campaign-rev00b.md` (5 phases). Track in `testing/qdd-rtm.xlsx`.
3. Take hero photo of assembled Rev 00B (clean background, good lighting)
4. Update portfolio page with test data, plots, and impedance control demo
5. Phase 2: first-principles explainers on aaronevans.ca (after topics 1-5 complete)

## File Map
| What you need | Read this |
|--------------|-----------|
| Project rules & conventions | CLAUDE.md |
| **RTM — requirements, tests, traceability** | **testing/qdd-rtm.xlsx** |
| **Test campaign procedures** | **testing/test-campaign-rev00b.md** |
| **Learning workbooks (13)** | **testing/learn/workbooks/** (progress: `_progress.md`) |
| Rev 00B scoped changes | prototypes/rev00b/changes.md |
| Rev 00B photos | prototypes/rev00b/photos/ |
| Official docs (content bank, media plan) | docs/official/ |
| Research (ODrive, impedance, PLA gears) | research/gemini-deep-research/01-actuator-testing-methodology/ |
| Test bench design | testing/test-bench-design.md |
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
