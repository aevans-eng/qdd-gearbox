"""
MKS XDrive Mini / ODrive-compatible first-spin helper.

Purpose:
- connect to an ODrive-compatible controller over USB
- optionally apply a conservative axis0 configuration
- calibrate with either incremental or SPI AMS encoder settings
- command a short, low-speed velocity spin

This is meant for first bench bring-up of the D6374 on the MKS XDrive Mini.
It avoids interactive shell editing and keeps the motion command conservative.
"""

from __future__ import annotations

import argparse
import sys
import time

import odrive
from odrive.enums import (
    AXIS_STATE_CLOSED_LOOP_CONTROL,
    AXIS_STATE_ENCODER_OFFSET_CALIBRATION,
    AXIS_STATE_FULL_CALIBRATION_SEQUENCE,
    AXIS_STATE_IDLE,
    AXIS_STATE_MOTOR_CALIBRATION,
    CONTROL_MODE_VELOCITY_CONTROL,
    ENCODER_MODE_INCREMENTAL,
    ENCODER_MODE_SPI_ABS_AMS,
    INPUT_MODE_PASSTHROUGH,
    MOTOR_TYPE_HIGH_CURRENT,
)


GAINS_BARE = {"pos": 5.0, "vel": 0.05, "int": 0.05, "ramp": 3.0}
GAINS_GEARBOX = {"pos": 15.0, "vel": 0.10, "int": 0.20, "ramp": 10.0}


def safe_get(obj, attr, default=None):
    try:
        return getattr(obj, attr)
    except Exception:
        return default


def safe_set(obj, attr, value):
    try:
        setattr(obj, attr, value)
        return True
    except Exception:
        return False


def axis_errors(ax) -> tuple[int, int, int]:
    return int(safe_get(ax, "error", 0) or 0), int(safe_get(ax.motor, "error", 0) or 0), int(
        safe_get(ax.encoder, "error", 0) or 0
    )


def print_status(odrv):
    ax = odrv.axis0
    bus = safe_get(odrv, "vbus_voltage")
    state = safe_get(ax, "current_state")
    axis_err, motor_err, encoder_err = axis_errors(ax)
    print(f"Bus voltage: {bus:.2f} V" if bus is not None else "Bus voltage: unknown")
    print(f"Axis state:  {state}")
    print(f"Errors:      axis={axis_err} motor={motor_err} encoder={encoder_err}")


def wait_for_idle(ax, timeout_s: float) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        if safe_get(ax, "current_state") == AXIS_STATE_IDLE:
            return True
        time.sleep(0.2)
    return False


def clear_errors(ax):
    for target in (ax, ax.motor, ax.encoder, ax.controller):
        safe_set(target, "error", 0)


def connect(timeout_s: float):
    print(f"Scanning for ODrive-compatible device (timeout={timeout_s:.1f}s)...")
    odrv = odrive.find_any(timeout=timeout_s)
    print("Connected.")
    print(f"Serial:      {safe_get(odrv, 'serial_number', 'unknown')}")
    print_status(odrv)
    return odrv


def configure_axis0(odrv, args):
    ax = odrv.axis0
    gains = GAINS_GEARBOX if args.profile == "gearbox" else GAINS_BARE

    print("Applying conservative axis0 configuration...")

    safe_set(odrv.config, "brake_resistance", args.brake_resistance)
    safe_set(odrv.config, "enable_brake_resistor", True)
    safe_set(odrv.config, "dc_bus_undervoltage_trip_level", args.uv_trip)
    safe_set(odrv.config, "dc_bus_overvoltage_trip_level", args.ov_trip)
    safe_set(odrv.config, "dc_max_positive_current", args.dc_max_positive_current)
    safe_set(odrv.config, "dc_max_negative_current", args.dc_max_negative_current)
    safe_set(odrv.config, "max_regen_current", args.max_regen_current)

    safe_set(ax.motor.config, "motor_type", MOTOR_TYPE_HIGH_CURRENT)
    safe_set(ax.motor.config, "pole_pairs", args.pole_pairs)
    safe_set(ax.motor.config, "current_lim", args.current_lim)
    safe_set(ax.motor.config, "requested_current_range", args.requested_current_range)
    safe_set(ax.motor.config, "calibration_current", args.calibration_current)
    safe_set(ax.motor.config, "resistance_calib_max_voltage", args.resistance_calib_max_voltage)

    if args.encoder == "incremental":
        safe_set(ax.encoder.config, "mode", ENCODER_MODE_INCREMENTAL)
    else:
        safe_set(ax.encoder.config, "mode", ENCODER_MODE_SPI_ABS_AMS)
        safe_set(ax.encoder.config, "abs_spi_cs_gpio_pin", args.abs_spi_cs_gpio_pin)

    safe_set(ax.encoder.config, "cpr", args.cpr)
    safe_set(ax.encoder.config, "bandwidth", args.encoder_bandwidth)
    safe_set(ax.encoder.config, "calib_range", args.encoder_calib_range)

    safe_set(ax.controller.config, "pos_gain", gains["pos"])
    safe_set(ax.controller.config, "vel_gain", gains["vel"])
    safe_set(ax.controller.config, "vel_integrator_gain", gains["int"])
    safe_set(ax.controller.config, "vel_ramp_rate", gains["ramp"])
    safe_set(ax.controller.config, "control_mode", CONTROL_MODE_VELOCITY_CONTROL)
    safe_set(ax.controller.config, "input_mode", INPUT_MODE_PASSTHROUGH)

    safe_set(ax.config, "watchdog_timeout", args.watchdog_timeout)
    safe_set(ax.config, "enable_watchdog", bool(args.enable_watchdog))

    print("Saving configuration and rebooting...")
    odrv.save_configuration()
    try:
        odrv.reboot()
    except Exception:
        pass
    time.sleep(3.0)


def run_calibration(odrv, calibration: str, timeout_s: float):
    ax = odrv.axis0

    if calibration == "none":
        return

    clear_errors(ax)

    if calibration == "motor":
        state = AXIS_STATE_MOTOR_CALIBRATION
        label = "motor calibration"
    elif calibration == "encoder":
        state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
        label = "encoder offset calibration"
    else:
        state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
        label = "full calibration"

    print(f"Starting {label}...")
    ax.requested_state = state

    if not wait_for_idle(ax, timeout_s):
        print("Calibration timed out waiting for IDLE.", file=sys.stderr)
        sys.exit(1)

    axis_err, motor_err, encoder_err = axis_errors(ax)
    if axis_err or motor_err or encoder_err:
        print(
            f"Calibration finished with errors: axis={axis_err} motor={motor_err} encoder={encoder_err}",
            file=sys.stderr,
        )
        sys.exit(1)

    phase_r = safe_get(ax.motor.config, "phase_resistance")
    phase_l = safe_get(ax.motor.config, "phase_inductance")
    if phase_r is not None:
        print(f"Phase R:     {phase_r * 1000.0:.2f} mOhm")
    if phase_l is not None:
        print(f"Phase L:     {phase_l * 1e6:.2f} uH")

    print("Calibration OK.")


def spin_velocity(odrv, velocity_tps: float, duration_s: float):
    ax = odrv.axis0
    clear_errors(ax)
    safe_set(ax.controller.config, "control_mode", CONTROL_MODE_VELOCITY_CONTROL)
    safe_set(ax.controller.config, "input_mode", INPUT_MODE_PASSTHROUGH)

    print("Entering closed loop...")
    ax.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    time.sleep(0.5)
    if safe_get(ax, "current_state") != AXIS_STATE_CLOSED_LOOP_CONTROL:
        print(f"Failed to enter closed loop. Current state: {safe_get(ax, 'current_state')}", file=sys.stderr)
        sys.exit(1)

    print(f"Commanding velocity: {velocity_tps:.3f} turns/s for {duration_s:.1f} s")
    ax.controller.input_vel = velocity_tps
    time.sleep(duration_s)
    ax.controller.input_vel = 0.0
    time.sleep(0.5)
    ax.requested_state = AXIS_STATE_IDLE
    print("Returned to IDLE.")


def parse_args():
    parser = argparse.ArgumentParser(description="Configure/calibrate/spin an MKS XDrive Mini conservatively.")
    parser.add_argument("--timeout", type=float, default=20.0, help="USB discovery timeout in seconds")
    parser.add_argument("--configure", action="store_true", help="Apply conservative config to axis0 and save it")
    parser.add_argument(
        "--profile",
        choices=["bare", "gearbox"],
        default="bare",
        help="Use bare-motor or gearbox gain defaults",
    )
    parser.add_argument(
        "--encoder",
        choices=["incremental", "spi_ams"],
        default="incremental",
        help="Encoder path for axis0",
    )
    parser.add_argument("--cpr", type=int, default=8192, help="Encoder CPR (8192 for AMT-102 default)")
    parser.add_argument("--abs-spi-cs-gpio-pin", type=int, default=7, help="CS GPIO for SPI AMS encoder mode")
    parser.add_argument("--encoder-bandwidth", type=float, default=3000.0)
    parser.add_argument("--encoder-calib-range", type=float, default=10.0)
    parser.add_argument("--pole-pairs", type=int, default=7)
    parser.add_argument("--current-lim", type=float, default=10.0)
    parser.add_argument("--requested-current-range", type=float, default=20.0)
    parser.add_argument("--calibration-current", type=float, default=5.0)
    parser.add_argument("--resistance-calib-max-voltage", type=float, default=2.0)
    parser.add_argument("--brake-resistance", type=float, default=2.0)
    parser.add_argument("--uv-trip", type=float, default=8.0)
    parser.add_argument("--ov-trip", type=float, default=56.0)
    parser.add_argument("--dc-max-positive-current", type=float, default=20.0)
    parser.add_argument("--dc-max-negative-current", type=float, default=-3.0)
    parser.add_argument("--max-regen-current", type=float, default=0.0)
    parser.add_argument("--watchdog-timeout", type=float, default=0.5)
    parser.add_argument(
        "--enable-watchdog",
        action="store_true",
        help="Enable axis watchdog after configuring (disabled by default for first bring-up)",
    )
    parser.add_argument(
        "--calibrate",
        choices=["none", "motor", "encoder", "full"],
        default="full",
        help="Calibration stage to run after connecting/configuring",
    )
    parser.add_argument("--spin", action="store_true", help="Command a short low-speed velocity spin after calibration")
    parser.add_argument("--velocity-tps", type=float, default=0.5, help="Velocity command in motor turns/s")
    parser.add_argument("--spin-duration", type=float, default=3.0, help="Spin duration in seconds")
    return parser.parse_args()


def main():
    args = parse_args()

    odrv = connect(args.timeout)

    if args.configure:
        configure_axis0(odrv, args)
        odrv = connect(args.timeout)

    print_status(odrv)
    run_calibration(odrv, args.calibrate, timeout_s=20.0)

    if args.spin:
        spin_velocity(odrv, velocity_tps=args.velocity_tps, duration_s=args.spin_duration)
        print_status(odrv)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
