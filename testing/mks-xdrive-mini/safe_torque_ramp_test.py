"""Safe ramped torque test for direct motor-to-trainer bring-up.

Use when velocity control saturates before trainer breakaway. This script
ramps torque explicitly in software so the drivetrain sees a gradual increase.
"""
from __future__ import annotations

import argparse
import sys
import time

import odrive
from odrive.enums import (
    AXIS_STATE_CLOSED_LOOP_CONTROL,
    AXIS_STATE_IDLE,
    CONTROL_MODE_TORQUE_CONTROL,
    INPUT_MODE_PASSTHROUGH,
)

KT_FALLBACK = 0.04


def safe_get(obj, attr, default=float("nan")):
    try:
        return getattr(obj, attr)
    except Exception:
        return default


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--target-torque", type=float, required=True,
                   help="Motor torque target in Nm. Sign sets direction.")
    p.add_argument("--ramp-seconds", type=float, default=20.0,
                   help="Seconds from 0 to target torque.")
    p.add_argument("--hold", type=float, default=3.0,
                   help="Hold seconds at target torque.")
    p.add_argument("--current-limit", type=float, default=10.0,
                   help="Motor current limit, A.")
    p.add_argument("--label", type=str, default="torque_ramp")
    p.add_argument("--dt", type=float, default=0.2,
                   help="Telemetry/sample period, seconds.")
    p.add_argument("--watchdog-timeout", type=float, default=2.0,
                   help="ODrive watchdog timeout, seconds.")
    p.add_argument("--stop-on-velocity", type=float, default=0.0,
                   help="If abs(encoder velocity) exceeds this turns/s, ramp down early.")
    p.add_argument("--rampdown-seconds", type=float, default=10.0,
                   help="Ramp-down duration after early movement detection.")
    p.add_argument("--stop-action", choices=["idle", "rampdown"], default="idle",
                   help="Action when stop-on-velocity trips. Default idle cuts torque immediately.")
    p.add_argument("--max-fet-temp-c", type=float, default=70.0,
                   help="Immediate idle if controller FET temp reaches this limit. Use 0 to disable.")
    p.add_argument("--max-runtime-seconds", type=float, default=0.0,
                   help="Immediate idle if elapsed runtime exceeds this value. Use 0 to disable.")
    a = p.parse_args()

    print(f"[{a.label}] Connecting...", flush=True)
    odrv = odrive.find_any(timeout=15.0)
    ax = odrv.axis0
    kt = getattr(ax.motor.config, "torque_constant", KT_FALLBACK) or KT_FALLBACK
    max_torque = abs(kt) * a.current_limit
    target = max(-max_torque, min(max_torque, a.target_torque))

    print(
        f"  vbus={odrv.vbus_voltage:.2f}V  state={ax.current_state}  "
        f"err axis={ax.error} motor={ax.motor.error} enc={ax.encoder.error}",
        flush=True,
    )
    print(
        f"  current_lim={a.current_limit}A  kt={kt:.4f}Nm/A  "
        f"target_torque={target:.4f}Nm  ramp={a.ramp_seconds}s  hold={a.hold}s",
        flush=True,
    )

    ax.requested_state = AXIS_STATE_IDLE
    time.sleep(0.3)
    try:
        ax.config.enable_watchdog = False
    except Exception:
        pass
    time.sleep(0.1)
    try:
        odrv.clear_errors()
    except Exception:
        pass
    for tgt in (ax, ax.motor, ax.encoder, ax.controller):
        try:
            tgt.error = 0
        except Exception:
            pass
    time.sleep(0.2)
    print(
        f"  after clear: err axis={ax.error} motor={ax.motor.error} "
        f"enc={ax.encoder.error} ctrl={ax.controller.error}",
        flush=True,
    )

    ax.motor.config.current_lim = a.current_limit
    ax.controller.config.control_mode = CONTROL_MODE_TORQUE_CONTROL
    ax.controller.config.input_mode = INPUT_MODE_PASSTHROUGH
    ax.controller.input_torque = 0.0
    ax.config.watchdog_timeout = a.watchdog_timeout
    ax.config.enable_watchdog = True
    try:
        ax.watchdog_feed()
    except Exception:
        pass
    try:
        odrv.clear_errors()
    except Exception:
        pass
    for tgt in (ax, ax.motor, ax.encoder, ax.controller):
        try:
            tgt.error = 0
        except Exception:
            pass

    ax.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    time.sleep(0.3)
    if ax.current_state != AXIS_STATE_CLOSED_LOOP_CONTROL:
        print(
            f"FAILED to enter closed loop, state={ax.current_state}  "
            f"err axis={ax.error} motor={ax.motor.error} enc={ax.encoder.error} "
            f"ctrl={ax.controller.error}",
            flush=True,
        )
        for attr in ("disarm_reason", "active_errors", "disarm_time"):
            try:
                print(f"  {attr}={getattr(ax, attr)}", flush=True)
            except Exception:
                pass
        ax.config.enable_watchdog = False
        ax.requested_state = AXIS_STATE_IDLE
        return 1

    total = max(0.0, a.ramp_seconds) + max(0.0, a.hold) + max(0.0, a.ramp_seconds)
    print(
        f"{'t_s':>6} {'torque':>8} {'vel':>8} {'iq_A':>7} {'fet_C':>7} "
        f"{'vbus_V':>7} {'ibus_A':>7} {'dc_W':>8} {'mech_W':>8} "
        f"{'cc_ibus_A':>10} {'id_A':>7} {'iq_sp_A':>8} {'id_sp_A':>8} "
        f"{'phB_A':>7} {'phC_A':>7} {'tq_sp':>8} {'vel_sp':>8} "
        f"{'eff_lim_A':>9} {'max_cc_A':>8}",
        flush=True,
    )

    try:
        t0 = time.time()
        early_rampdown_t0 = None
        early_rampdown_start = 0.0
        while True:
            t = time.time() - t0
            if early_rampdown_t0 is not None:
                down_t = t - early_rampdown_t0
                if down_t >= a.rampdown_seconds:
                    break
                frac = 1.0 if a.rampdown_seconds <= 0 else max(0.0, 1.0 - down_t / a.rampdown_seconds)
                cmd = early_rampdown_start * frac
            elif t <= a.ramp_seconds:
                frac = 1.0 if a.ramp_seconds <= 0 else t / a.ramp_seconds
                cmd = target * frac
            elif t <= a.ramp_seconds + a.hold:
                cmd = target
            elif t <= total:
                down_t = t - a.ramp_seconds - a.hold
                frac = 1.0 if a.ramp_seconds <= 0 else max(0.0, 1.0 - down_t / a.ramp_seconds)
                cmd = target * frac
            else:
                break

            ax.controller.input_torque = cmd
            try:
                ax.watchdog_feed()
            except Exception:
                pass
            state_now = safe_get(ax, "current_state", -1)
            if state_now != AXIS_STATE_CLOSED_LOOP_CONTROL:
                disarm_reason = safe_get(ax, "disarm_reason", "?")
                active_errors = safe_get(ax, "active_errors", "?")
                print(
                    f"  -> axis dropped out of CLOSED_LOOP at t={t:.2f}s "
                    f"(state={state_now}, disarm_reason={disarm_reason}, "
                    f"active_errors={active_errors}, "
                    f"axis_err={ax.error}, motor_err={ax.motor.error}, "
                    f"enc_err={ax.encoder.error}, ctrl_err={ax.controller.error}); "
                    f"aborting",
                    flush=True,
                )
                break
            vel = ax.encoder.vel_estimate
            iq = ax.motor.current_control.Iq_measured
            cc_ibus = safe_get(ax.motor.current_control, "Ibus")
            id_measured = safe_get(ax.motor.current_control, "Id_measured")
            iq_setpoint = safe_get(ax.motor.current_control, "Iq_setpoint")
            id_setpoint = safe_get(ax.motor.current_control, "Id_setpoint")
            phase_b = safe_get(ax.motor, "current_meas_phB")
            phase_c = safe_get(ax.motor, "current_meas_phC")
            torque_setpoint = safe_get(ax.controller, "torque_setpoint")
            vel_setpoint = safe_get(ax.controller, "vel_setpoint")
            effective_current_lim = safe_get(ax.motor, "effective_current_lim")
            max_allowed_current = safe_get(ax.motor.current_control, "max_allowed_current")
            try:
                fet_temp = ax.fet_thermistor.temperature
            except Exception:
                fet_temp = float("nan")
            vbus = safe_get(odrv, "vbus_voltage")
            ibus = safe_get(odrv, "ibus")
            dc_power = vbus * ibus if vbus == vbus and ibus == ibus else float("nan")
            mech_power = (kt * iq) * (vel * 2.0 * 3.141592653589793)
            print(
                f"{t:6.2f} {cmd:8.4f} {vel:8.3f} "
                f"{iq:7.2f} {fet_temp:7.2f} {vbus:7.2f} {ibus:7.2f} "
                f"{dc_power:8.2f} {mech_power:8.2f} "
                f"{cc_ibus:10.2f} {id_measured:7.2f} {iq_setpoint:8.2f} {id_setpoint:8.2f} "
                f"{phase_b:7.2f} {phase_c:7.2f} {torque_setpoint:8.4f} {vel_setpoint:8.3f} "
                f"{effective_current_lim:9.2f} {max_allowed_current:8.2f}",
                flush=True,
            )
            if a.max_runtime_seconds > 0 and t >= a.max_runtime_seconds:
                print("  -> max runtime reached; zero torque + IDLE", flush=True)
                ax.controller.input_torque = 0.0
                ax.requested_state = AXIS_STATE_IDLE
                break
            if a.max_fet_temp_c > 0 and fet_temp == fet_temp and fet_temp >= a.max_fet_temp_c:
                print(
                    f"  -> FET temp limit {a.max_fet_temp_c:.1f} C reached; zero torque + IDLE",
                    flush=True,
                )
                ax.controller.input_torque = 0.0
                ax.requested_state = AXIS_STATE_IDLE
                break
            if (
                early_rampdown_t0 is None
                and a.stop_on_velocity > 0
                and abs(vel) >= a.stop_on_velocity
            ):
                if a.stop_action == "idle":
                    print("  -> movement/overspeed detected; zero torque + IDLE", flush=True)
                    ax.controller.input_torque = 0.0
                    ax.requested_state = AXIS_STATE_IDLE
                    break
                early_rampdown_t0 = t
                early_rampdown_start = cmd
                print(
                    f"  -> movement detected; ramping torque down over {a.rampdown_seconds:.1f}s",
                    flush=True,
                )
            time.sleep(a.dt)
    finally:
        try:
            ax.controller.input_torque = 0.0
        except Exception:
            pass
        time.sleep(0.3)
        try:
            ax.config.enable_watchdog = False
        except Exception:
            pass
        try:
            ax.requested_state = AXIS_STATE_IDLE
        except Exception:
            pass
        time.sleep(0.3)
        print(
            f"final state={ax.current_state}  "
            f"err axis={ax.error} motor={ax.motor.error} enc={ax.encoder.error}",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
