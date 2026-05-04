"""Safe ramped velocity test for first powered run on Saris H2 dyno.

Enforces INPUT_MODE_VEL_RAMP per shock-loading rule. Watchdog enabled.
Streams encoder velocity + Iq + commanded velocity to stdout.

Single-run, self-contained: connect -> configure -> closed loop ->
ramp up -> hold -> ramp down -> idle.
"""
from __future__ import annotations

import argparse
import sys
import time

import odrive
from odrive.enums import (
    AXIS_STATE_CLOSED_LOOP_CONTROL,
    AXIS_STATE_IDLE,
    CONTROL_MODE_VELOCITY_CONTROL,
    INPUT_MODE_VEL_RAMP,
)

GAINS = {
    "bare": {"pos": 5.0, "vel": 0.05, "int": 0.05, "ramp": 3.0},
    "gearbox": {"pos": 15.0, "vel": 0.10, "int": 0.20, "ramp": 10.0},
}


def safe_get(obj, attr, default=float("nan")):
    try:
        return getattr(obj, attr)
    except Exception:
        return default


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--target", type=float, required=True,
                   help="Motor turns/s target. Sign sets direction.")
    p.add_argument("--profile", choices=["bare", "gearbox"], default="bare",
                   help="Apply known profile gains before motion (default bare).")
    p.add_argument("--ramp-rate", type=float, default=2.0,
                   help="Motor turns/s^2 (default 2.0)")
    p.add_argument("--hold", type=float, default=5.0,
                   help="Hold seconds at target")
    p.add_argument("--current-limit", type=float, default=5.0,
                   help="Motor current limit, A (default 5.0)")
    p.add_argument("--label", type=str, default="run")
    p.add_argument("--watchdog-timeout", type=float, default=2.0,
                   help="ODrive watchdog timeout, seconds.")
    p.add_argument("--stop-on-velocity", type=float, default=0.0,
                   help="Immediate idle if abs(encoder velocity) exceeds this turns/s. Use 0 to disable.")
    p.add_argument("--max-fet-temp-c", type=float, default=70.0,
                   help="Immediate idle if controller FET temp reaches this limit. Use 0 to disable.")
    p.add_argument("--max-runtime-seconds", type=float, default=0.0,
                   help="Immediate idle if elapsed runtime exceeds this value. Use 0 to disable.")
    a = p.parse_args()

    print(f"[{a.label}] Connecting...", flush=True)
    odrv = odrive.find_any(timeout=15.0)
    ax = odrv.axis0
    print(
        f"  vbus={odrv.vbus_voltage:.2f}V  state={ax.current_state}  "
        f"err axis={ax.error} motor={ax.motor.error} enc={ax.encoder.error}",
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

    gains = GAINS[a.profile]
    ax.motor.config.current_lim = a.current_limit
    ax.controller.config.pos_gain = gains["pos"]
    ax.controller.config.vel_gain = gains["vel"]
    ax.controller.config.vel_integrator_gain = gains["int"]
    ax.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL
    ax.controller.config.input_mode = INPUT_MODE_VEL_RAMP
    ax.controller.config.vel_ramp_rate = a.ramp_rate
    ax.controller.input_vel = 0.0
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
    print(
        f"  profile={a.profile}  current_lim={a.current_limit}A  "
        f"vel_gain={gains['vel']}  vel_int={gains['int']}  "
        f"ramp_rate={a.ramp_rate}t/s^2  "
        f"target={a.target}t/s  hold={a.hold}s",
        flush=True,
    )

    ax.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    time.sleep(0.3)
    if ax.current_state != 8:
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

    ramp_t = abs(a.target) / a.ramp_rate if a.ramp_rate > 0 else 0.0
    total = ramp_t + a.hold + ramp_t + 0.5

    try:
        ax.controller.input_vel = a.target
        t0 = time.time()
        ramp_down_sent = False
        print(
            f"{'t_s':>5} {'cmd':>7} {'vel':>7} {'iq_A':>6} {'fet_C':>7} "
            f"{'vbus_V':>7} {'ibus_A':>7} {'dc_W':>8} {'mech_W':>8} "
            f"{'cc_ibus_A':>10} {'id_A':>7} {'iq_sp_A':>8} {'id_sp_A':>8} "
            f"{'phB_A':>7} {'phC_A':>7} {'tq_sp':>8} {'vel_sp':>8} "
            f"{'eff_lim_A':>9} {'max_cc_A':>8}",
            flush=True,
        )
        while True:
            t = time.time() - t0
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
            cmd = ax.controller.input_vel
            vel = ax.encoder.vel_estimate
            iq = ax.motor.current_control.Iq_measured
            try:
                fet_temp = ax.fet_thermistor.temperature
            except Exception:
                fet_temp = float("nan")
            vbus = safe_get(odrv, "vbus_voltage")
            ibus = safe_get(odrv, "ibus")
            dc_power = vbus * ibus if vbus == vbus and ibus == ibus else float("nan")
            kt = safe_get(ax.motor.config, "torque_constant", 0.04) or 0.04
            mech_power = (kt * iq) * (vel * 2.0 * 3.141592653589793)
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
            print(
                f"{t:5.2f} {cmd:7.3f} {vel:7.3f} {iq:6.2f} {fet_temp:7.2f} "
                f"{vbus:7.2f} {ibus:7.2f} {dc_power:8.2f} {mech_power:8.2f} "
                f"{cc_ibus:10.2f} {id_measured:7.2f} {iq_setpoint:8.2f} {id_setpoint:8.2f} "
                f"{phase_b:7.2f} {phase_c:7.2f} {torque_setpoint:8.4f} {vel_setpoint:8.3f} "
                f"{effective_current_lim:9.2f} {max_allowed_current:8.2f}",
                flush=True,
            )
            if a.max_runtime_seconds > 0 and t >= a.max_runtime_seconds:
                print("  -> max runtime reached; zero velocity + IDLE", flush=True)
                ax.controller.input_vel = 0.0
                ax.requested_state = AXIS_STATE_IDLE
                break
            if a.max_fet_temp_c > 0 and fet_temp == fet_temp and fet_temp >= a.max_fet_temp_c:
                print(
                    f"  -> FET temp limit {a.max_fet_temp_c:.1f} C reached; zero velocity + IDLE",
                    flush=True,
                )
                ax.controller.input_vel = 0.0
                ax.requested_state = AXIS_STATE_IDLE
                break
            if a.stop_on_velocity > 0 and abs(vel) >= a.stop_on_velocity:
                print("  -> velocity limit reached; zero velocity + IDLE", flush=True)
                ax.controller.input_vel = 0.0
                ax.requested_state = AXIS_STATE_IDLE
                break
            if not ramp_down_sent and t >= ramp_t + a.hold:
                ax.controller.input_vel = 0.0
                ramp_down_sent = True
                print("  -> ramping to 0", flush=True)
            if t >= total:
                break
            time.sleep(0.2)
    finally:
        try:
            ax.controller.input_vel = 0.0
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
