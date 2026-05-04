# Session 007 - Dyno Testing Handoff

Date: 2026-05-03

## Current State

The synchronized logging stack is working, but we do not yet have a valid efficiency baseline.

Working:
- Controller USB/API is reachable when powered.
- Arduino thermistor logger works on `COM6` at `115200`.
- Hammer BLE capture can connect when the trainer is awake.
- Synced run folders are created under `testing/data/`.
- Motor logs now include power-delivery fields: `vbus`, `ibus`, `dc_W`, current-control `Ibus`, `Iq/Id`, phase currents, FET temp, encoder velocity, and estimated motor mechanical power.
- Manifest files now include exit codes and fail if a subprocess fails.
- Dyno capture now fails if no samples are captured.

Important setup:
- PSU target: `24 V`, `10 A` current limit, `30 V` OVP, `10 A` OCP.
- Controller current range was raised and saved: `requested_current_range = 70 A`.
- Verified after reboot: `effective_current_lim = 40 A`, `max_allowed_current = 121.5 A`, errors clear.
- Conservative torque constant for requirement math: `Kt = 0.04 Nm/A`.
- Gear ratio: `5:1`.
- Thermal aborts: motor/gearbox temp `50 C`, FET temp `70 C`.

## Runs From This Session

### Valid Readiness / Logging Runs

- `synced-official-preflight-direction-20260503-211753`
  - Status: completed.
  - Motor/temp/dyno processes all exit code `0`.
  - Tiny `0.08 Nm` torque bump did not move the trainer, which is acceptable for preflight.
  - Temp stable: `27.87 C` to `27.89 C`.

### Not Valid For Efficiency

- `synced-official-bare-baseline-20a-20260503-210542`
  - Status: completed.
  - Motor/temp/dyno all logged.
  - Hammer captured rows but all `0 rpm / 0 W / 0 revs`.
  - Not useful for efficiency.

- `synced-official-bare-baseline-40a-20260503-211921`
  - Status: completed, but not valid for efficiency.
  - Motor/temp/dyno all logged.
  - Hammer captured rows but all `0 rpm / 0 W / 0 revs`.
  - Motor max Iq: `47.8 A`.
  - FET max: `46.49 C`.
  - Arduino temp: `27.65 C` to `33.69 C`.
  - Final motor log showed `axis=64`, `motor=4096` current-limit violation after the run.
  - Conclusion: positive torque ramp loaded/stalled the trainer but did not spin it enough for Hammer power data.

- `synced-official-bare-velocity-100rpm-20a-20260503-212506`
  - Status: failed.
  - Intended target: `-1.67 t/s`, roughly `100 rpm` direct-drive trainer speed.
  - Motor oversped in the freewheel/non-drive direction: encoder velocity spiked to `26.917 t/s`.
  - Triggered velocity limit and ended with `motor_error=4096`.
  - Hammer connected then dropped; no valid dyno data.
  - Conclusion: negative velocity is not valid for official baseline; it freewheels/overspeeds instead of loading the trainer.

## Main Conclusions

- The Hammer needs nonzero speed and wheel revolutions to produce useful power/torque data. Runs at `0-5 rpm` are not useful for efficiency.
- Negative motor direction appears to be the freewheel/overspeed direction in the bare-motor setup. Avoid it for official efficiency runs.
- Positive torque direction appears to load the trainer, but at 20 A and 40 A it stalled or moved too slowly for Hammer output.
- A usable efficiency method needs a controlled positive-direction speed/load point that produces stable Hammer rpm/power without current-limit trips.
- The gearbox will reduce output speed by `5:1`, so any motor-speed target for the gearbox-installed test must be 5x the motor-only direct-drive target if the same trainer rpm is desired.

## Recommended Next Testing Plan

1. Start every session with:
   - Controller status check: errors zero, encoder ready, state idle.
   - Hammer scan.
   - Arduino on `COM6`.
   - Tiny preflight: `.\run_official_requirement_test.ps1 -TestStage PreflightDirection`.

2. Do not run negative-direction velocity for official data.
   - It has already oversped and tripped current limit.

3. Find a positive-direction baseline that spins the Hammer:
   - Use a gradual positive velocity or torque-ramp strategy.
   - Target trainer speed should be at least `~100 rpm` for reliable Hammer data.
   - Direct bare motor target for `100 rpm` trainer speed is about `1.67 t/s`.
   - Gearbox-installed motor target for the same trainer speed is about `8.33 t/s`.
   - Use strict overspeed idle and thermal aborts.

4. Once a usable positive-direction baseline is found:
   - Record bare-motor baseline at the same target speed/load.
   - Assemble gearbox.
   - Repeat with gearbox installed at the same trainer speed.
   - Compare matched-speed windows using `testing/analyze_synced_efficiency.py`.

5. Requirement tests remain gearbox-installed:
   - `R-06` peak torque >= `16 Nm`: gearbox installed.
   - `R-07` continuous torque >= `12 Nm`: gearbox installed.
   - `R-08` thermal: gearbox installed.
   - `R-09` efficiency: compare bare motor vs gearbox installed at matched speed/load.
   - `R-11` speed >= `600 rpm` output: gearbox installed, separate from torque tests.

## Tooling Changed

- `testing/mks-xdrive-mini/safe_torque_ramp_test.py`
- `testing/mks-xdrive-mini/safe_ramp_test.py`
- `testing/run_synced_motor_dyno_temp.ps1`
- `testing/run_official_requirement_test.ps1`
- `testing/analyze_synced_efficiency.py`
- `testing/plot_synced_run.py`
- `testing/dyno/ble-capture/dyno.py`
- `testing/OFFICIAL-DYNO-TESTING.md`

## Resume Checklist

Before the next powered test:
- Controller powered and USB API reachable.
- Controller state `IDLE`.
- Axis/motor/encoder/controller errors all `0`.
- Encoder ready.
- Hammer found in BLE scan.
- Arduino temp logger visible on `COM6`.
- PSU at `24 V`, `10 A`, OVP `30 V`, OCP `10 A`.
- Fan cooling controller and motor.

Do not claim any efficiency result from today. The logs are useful diagnostics only.
