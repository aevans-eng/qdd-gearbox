# Official Dyno Requirement Testing

This is the operator guide for the QDD dyno bench:

- MKS XDrive Mini / ODrive-compatible motor controller
- Saris Hammer H2 trainer BLE dyno
- Arduino thermistor logger
- synchronized run folders and manifests

Use these wrappers for requirement runs. They create synced run folders under `testing/data/` with:

- `manifest.json`
- `motor.log`
- `temperature.csv`
- `dyno.csv`
- `emergency-idle.log`

Raw synced run folders are local bench artifacts and are ignored by git. Commit handoff summaries under `testing/data/session-*.md` when a test session needs to be preserved.

## Safety Defaults

- `Kt = 0.04 Nm/A`
- `gear_ratio = 5`
- `target_efficiency = 0.90`
- controller current envelope: `60 A continuous`, `90 A peak`
- abort at `50 C` Arduino motor/gearbox temp
- abort at `70 C` controller FET temp
- fan installed on controller by default

The wrapper emergency-idles the controller if the Arduino temperature log or FET telemetry crosses the configured limits.

## Bench Setup

Power:

```text
PSU voltage: 24 V
PSU current limit: 10 A
OVP: 30 V
OCP: 10 A
```

Connections:

- MKS controller powered and connected over USB.
- Arduino thermistor logger on `COM6` at `115200`.
- Hammer H2 awake and discoverable over BLE.
- Controller and motor fan cooling installed.

Controller current range:

```text
requested_current_range = 70 A
verified effective_current_lim = 40 A after reboot
```

Check this before any high-current run. If `effective_current_lim` is lower than the requested test current, reboot the controller after saving the new range.

## Official Sequence

Run from `C:\Users\aaron\Documents\c-projects\qdd-gearbox\testing`.

First verify that the trainer is awake:

```powershell
& C:\Users\aaron\miniconda3\python.exe .\dyno\ble-capture\dyno.py scan --timeout 10
```

Then run preflight:

```powershell
.\run_official_requirement_test.ps1 -TestStage PreflightDirection
```

Use this first after any wiring/controller reboot. It uses a tiny positive torque bump and a low velocity trip.

## Direction Notes From 2026-05-03

Two hard constraints established this date:

1. **Negative-velocity at high targets oversped to ~+27 t/s** in the freewheel direction and tripped current limit (session 007, target -1.67 t/s @ 20 A). Do not use targets ≤ -1 t/s for official runs.
2. **Positive (loaded) direction cannot be driven bare-motor at this controller's ~70 A Iq cap** (≈ 2.8 Nm motor torque, session 008). Multiple runs at 20 A, 40 A, 60 A, 70 A torque mode and 20 A, 60 A, 90 A velocity mode → motor stalled in the loaded direction. After 150 s pinned at 70 A Iq, motor heated +9 °C, all 232 W dissipated as heat, no rotation. **The 5:1 gearbox exists because the bare motor cannot drive these loads directly — this is consistent with the design rationale.**

For a matched-load (Hammer-recording) bare-motor baseline, three options remain:

- **Hand-spin start.** Apply ~2.8 Nm at 70 A, hand-spin the wheel during the hold to break stiction, motor maintains at lower steady-state torque. Hacky but produces matched-load data.
- **Higher current burst.** Try 100–120 A peak for ≤ 10 s with strict thermal abort. Risk: FET thermal trip, motor windings stress.
- **Change methodology for R-09.** Characterize bare motor in freewheel direction at low load (motor input W vs estimated motor mech W). Characterize gearbox-installed in loaded direction at trainer (full-system input W vs Hammer output W). Compute gearbox-only efficiency by inferring motor losses from the bare curve at matched motor torque/speed. Most methodologically rigorous; avoids the bare-motor torque wall entirely.

Target speed guidance (if a valid bare-motor matched-load run is achieved):

```text
Minimum useful trainer speed target: about 100 rpm
Bare direct-drive motor target: 100 rpm / 60 = 1.67 turns/s
Gearbox-installed motor target for same trainer speed: 1.67 * 5 = 8.33 turns/s
```

For the gearbox-installed runs (where bare-motor torque is not the limit), use a gradual positive-direction ramp and strict velocity/temp aborts.

## Recovery After a Failed Run

The 2026-05-03 evening session uncovered a chain of silent-failure modes in the harness; all are now fixed in code (`safe_ramp_test.py`, `safe_torque_ramp_test.py`, `run_synced_motor_dyno_temp.ps1`). When a run still fails:

1. **Read the new state-watch printout in `motor.log`** — on a silent disarm during a run, the script now prints `disarm_reason`, `active_errors`, and per-subobject error codes at the moment of disarm.
2. **Read the post-clear printout at the start of every run.** The script prints axis/motor/encoder/controller errors after attempting to clear them. If anything is nonzero after the clear, the run will likely fail to enter CLOSED_LOOP.
3. **If sticky errors remain after a software clear: power-cycle PSU.** Off, count to 5, on. This is the only reliable reset for some sticky bits. Sticky values seen: axis `48`, `16`, `2048`; motor `32768`.
4. **Manifest summary `motor_exit_code` and `dyno_exit_code` are authoritative.** Nonzero = real failure even if the parent script reported "completed" status.

## Bare Motor Baseline

The baseline is not a torque requirement proof. It is a repeatable motor/controller/trainer operating point used later for gearbox efficiency comparison.

Required for a valid baseline:

- nonzero Hammer `rpm`
- nonzero Hammer `wheel_revs`
- nonzero Hammer `power_w`, or a clearly stable nonzero torque channel
- controller logs with `vbus`, `ibus`, `dc_W`, `Iq`, encoder velocity, FET temp
- Arduino temperature log
- manifest status `completed` and all process exit codes `0`

The 2026-05-03 attempts with zero Hammer rpm/power are diagnostics only, not efficiency data.

```powershell
.\run_official_requirement_test.ps1 -TestStage BareBaseline -Series
```

Bare motor baseline at `20 A`, `40 A`, and `60 A`.

```powershell
.\run_official_requirement_test.ps1 -TestStage GearboxEfficiency -Series
```

Gearbox-installed efficiency runs at the same current points.

```powershell
.\run_official_requirement_test.ps1 -TestStage ContinuousTorque
```

Gearbox-installed continuous torque run capped at `60 A`.

```powershell
.\run_official_requirement_test.ps1 -TestStage PeakTorque
```

Gearbox-installed peak torque ramp capped at `90 A`.

```powershell
.\run_official_requirement_test.ps1 -TestStage Speed
```

Gearbox-installed `600 RPM` output speed run.

## Efficiency Analysis

Compare one bare run folder against the matching gearbox run folder:

```powershell
& C:\Users\aaron\miniconda3\python.exe .\analyze_synced_efficiency.py `
  --bare-run .\data\synced-official-bare-baseline-40a-YYYYMMDD-HHMMSS `
  --gearbox-run .\data\synced-official-gearbox-efficiency-40a-YYYYMMDD-HHMMSS `
  --rpm-tolerance 3 `
  --output .\data\efficiency-40a.json
```

Only claim `R-09` from matched-speed pairs with enough samples. Do not use startup spikes or zero-rpm power artifacts.
