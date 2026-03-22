# Testing — QDD Actuator

## Tracking Hub

**`qdd-rtm.xlsx`** — Requirements Traceability Matrix. This is the single source of truth for:
- All 13 design requirements (status, verification method, coverage)
- Traceability matrix (which tests verify which requirements)
- Test log (all 19 tests, status, results, acceptance criteria)
- Unknowns register (U-01 through U-10)
- Health log (degradation tracking over time)

## Reading Order

If you're starting from scratch, read in this order:

1. **`learn/motor-physics-primer.md`** — First-principles physics: current, torque, speed, heat, and how they connect. Start here if the equations don't make sense yet.
2. **`learn/campaign-walkthrough.md`** — What each test does and why, explained intuitively. Connects physics to the specific tests.
3. **`methodology/testing-fundamentals.md`** — How to think about testing: requirements traceability, unknowns, prioritization, test levels. Also has the variables/nomenclature table.
4. **`campaign/test-campaign-rev00b.md`** — The actual test procedures. Step-by-step instructions for each phase.
5. **`qdd-rtm.xlsx`** — Track progress, results, and traceability as you run tests.

## Folder Structure

```
testing/
├── qdd-rtm.xlsx           ★ tracking hub — requirements, tests, traceability
├── learn/                 "understand before you test"
│   ├── motor-physics-primer.md    — physics fundamentals
│   └── campaign-walkthrough.md    — intuitive test explanations
├── methodology/           "how to think about testing"
│   └── testing-fundamentals.md    — framework, variables table
├── campaign/              "the actual tests"
│   └── test-campaign-rev00b.md    — procedures (Phase 0–5)
├── hardware/              "physical test setup"
│   ├── test-bench-design.md       — portable bench design
│   └── dyno-smart-trainer.md      — CycleOps H2 as budget dyno
├── data/                  raw test results (CSVs, logs)
└── _archive/              superseded docs
    └── test-tracker-pre-rtm.md    — old markdown tracker (pre-RTM)
```
