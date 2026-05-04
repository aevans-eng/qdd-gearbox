# QDD Gearbox

A quasi-direct-drive actuator built around a D6374-150KV BLDC motor, a 5:1 3D-printed planetary gearbox, and an MKS xDrive Mini ODrive-compatible controller. Designed for backdrivability and impedance-control experiments. Total build cost under $120 CAD.

This is a personal engineering project tracked end-to-end with a real V&V framework: requirements, traceability matrix, test plans, and a documented test campaign. The goal is to learn actuator design from the physics up — and to produce something interview-grade for actuator-engineering roles.

## Status

**Rev 00B printed, assembled, and partially validated.**

| Test | Requirement | Status |
|---|---|---|
| T-012 backlash | R-01 | **Pass** — 0° measured |
| T-013 backdrivability | R-04 | Pending hockey-stick adapter |
| BOM weight | R-10 | Pending inspection |
| BOM cost | R-02 | Pending sum |
| T-020 peak torque | R-06 | Pending dyno day |
| T-021 continuous torque | R-07 | Pending dyno day |
| T-022 efficiency | R-09 | Pending — bare-motor baseline blocked, see [`testing/OFFICIAL-DYNO-TESTING.md`](testing/OFFICIAL-DYNO-TESTING.md) |
| T-023 speed | R-11 | Pending dyno day |
| T-024 thermal | R-08 | Pending dyno day |
| Health check (pre/post dyno) | R-05 | Pending |

Active blocker: bare-motor matched-load baseline against the trainer's loaded direction is torque-limited bare-motor. See [session-008 handoff](testing/data/session-008-bare-baseline-handoff.md) for the diagnosis and three options to unblock R-09.

## Hardware

| Component | Spec |
|---|---|
| Motor | D6374-150KV BLDC (7 pole pairs) |
| Torque constant | 0.04 Nm/A (conservative — used for all requirement math; nominal 0.0551 Nm/A documented but not yet re-validated) |
| Controller | MKS xDrive Mini (ODrive-compatible firmware), 8 kHz FOC |
| Gearbox | 5:1 planetary, 3D printed PLA, custom design |
| Supply | 24 V nominal, 10 A current limit, OVP 30 V, OCP 10 A |
| Encoder | Magnetic (integrated with controller) |
| Dyno | Saris H2 / Hammer trainer (BLE power + rpm) |
| Thermal monitoring | Arduino + thermistor on motor body, FET temp from controller |

Direction note: positive motor velocity drives the trainer's *loaded* (resistance-engaged) direction. Negative is freewheel. The bare motor at this controller's effective ~70 A Iq cap (≈ 2.8 Nm) cannot break the trainer's loaded-direction static drag — that's why the gearbox exists.

## How the Test System Works

The dyno runs are *synchronized*: motor controller, BLE dyno, and Arduino temperature logger all start within a second of each other and run for a fixed capture window. Output is one timestamped folder per run with:

- `motor.log` — controller telemetry (vbus, ibus, dc_W, Iq, encoder velocity, FET temp, phase currents)
- `dyno.csv` — Hammer rpm/power/torque from BLE
- `temperature.csv` — Arduino motor-body thermistor
- `manifest.json` — run metadata, parameters, summary stats, exit codes

Run a synced test:

```powershell
cd testing
.\run_official_requirement_test.ps1 -TestStage PreflightDirection
.\run_official_requirement_test.ps1 -TestStage BareBaseline -Series
.\run_official_requirement_test.ps1 -TestStage GearboxEfficiency -Series
```

See [`testing/OFFICIAL-DYNO-TESTING.md`](testing/OFFICIAL-DYNO-TESTING.md) for the full sequence, safety defaults, recovery procedures, and the bare-motor torque-limit constraint.

Compare a bare run against a gearbox-installed run:

```powershell
& C:\Users\aaron\miniconda3\python.exe .\analyze_synced_efficiency.py `
  --bare-run    .\data\synced-official-bare-baseline-40a-YYYYMMDD-HHMMSS `
  --gearbox-run .\data\synced-official-gearbox-efficiency-40a-YYYYMMDD-HHMMSS `
  --rpm-tolerance 3
```

## V&V Framework

11 requirements drive 7 tests + 3 inspections:

- **Source of truth:** [`testing/qdd-rtm.xlsx`](testing/qdd-rtm.xlsx) — full requirements traceability matrix.
- **Test log:** [`testing/validation/test-log.md`](testing/validation/test-log.md) — every test entry with date, config, result, anomalies.
- **Test plans:** [`testing/validation/`](testing/validation/) — per-test procedures, acceptance criteria.
- **Methodology:** test plan was redesigned around a V-model approach in March 2026.

Every test session also gets a journal entry in [`testing/data/session-log.md`](testing/data/session-log.md) and, for major sessions, a handoff doc (`session-NNN-*-handoff.md`) capturing what worked, what didn't, and what the next session needs to know.

## Repo Structure

```
calc/                 Python design calculators (gear geometry, tooth stress, bearing life, thermal)
docs/
  design/             Tolerances, assembly profile, gear parameters
  catia/              CATIA modeling guide and skeleton workflow
  log/                Session work logs
drawings/             GD&T annotation notes
prototypes/
  rev00a/             First print — superseded
  rev00b/             Current revision (assembled, partial validation passed)
testing/
  OFFICIAL-DYNO-TESTING.md     Operating procedures for the dyno campaign
  qdd-rtm.xlsx                 Requirements traceability matrix
  run_official_requirement_test.ps1   Wrapper for each requirement test stage
  run_synced_motor_dyno_temp.ps1      Underlying synced-capture orchestrator
  analyze_synced_efficiency.py        Match bare vs gearbox runs at common rpm windows
  plot_synced_run.py                  Per-run timeseries plots
  mks-xdrive-mini/                    Controller-side scripts and session checklist
  temperature-logger/                 Arduino + Python thermistor logger
  dyno/ble-capture/                   BLE Hammer capture
  validation/                         Per-test plans, test log, methodology docs
  hardware/                           Safety checklist, SOP, mounting notes
  data/                               Run folders + session-log.md + handoff docs
  future-work.md                      Characterization and controls ideas
STATE.md              Current project state — start here for any new session
CLAUDE.md             Project rules and conventions
```

## Active Files to Read First

- **[STATE.md](STATE.md)** — current status, remaining tests, file map, blockers.
- **[testing/data/session-008-bare-baseline-handoff.md](testing/data/session-008-bare-baseline-handoff.md)** — most recent test session, harness bug fixes, R-09 unblock options.
- **[testing/OFFICIAL-DYNO-TESTING.md](testing/OFFICIAL-DYNO-TESTING.md)** — dyno operating procedures.
- **[testing/qdd-rtm.xlsx](testing/qdd-rtm.xlsx)** — requirements ↔ tests matrix.

## License

Personal learning project. Not intended for redistribution.
