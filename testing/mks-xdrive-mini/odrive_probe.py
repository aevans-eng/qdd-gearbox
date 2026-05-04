"""
ODrive-compatible board probe for QDD bench bring-up.

Purpose:
- Confirm the USB/native protocol stack is alive
- Print the board identity and key electrical/config values
- Apply a safe profile if requested

Works with ODrive 3.6 and compatible 0.5.x-style boards such as
Makerbase / MKS ODrive-derived controllers, as long as they expose
the same native protocol object model through the `odrive` Python package.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


GAINS_BARE = {"pos": 5.0, "vel": 0.05, "int": 0.05, "ramp": 3.0}
GAINS_GEARBOX = {"pos": 15.0, "vel": 0.10, "int": 0.20, "ramp": 10.0}


def safe_get(obj, attr, default=None):
    try:
        return getattr(obj, attr)
    except Exception:
        return default


def summarize_device(odrv):
    ax = odrv.axis0
    motor_cfg = ax.motor.config
    ctrl_cfg = ax.controller.config
    axis_cfg = ax.config

    summary = {
        "serial_number": str(safe_get(odrv, "serial_number", "unknown")),
        "bus_voltage_v": safe_get(odrv, "vbus_voltage"),
        "fw_version": {
            "major": safe_get(odrv, "fw_version_major"),
            "minor": safe_get(odrv, "fw_version_minor"),
            "revision": safe_get(odrv, "fw_version_revision"),
            "unreleased": safe_get(odrv, "fw_version_unreleased"),
        },
        "hw_version": {
            "major": safe_get(odrv, "hw_version_major"),
            "minor": safe_get(odrv, "hw_version_minor"),
            "variant": safe_get(odrv, "hw_version_variant"),
        },
        "axis_state": safe_get(ax, "current_state"),
        "errors": {
            "axis": safe_get(ax, "error"),
            "motor": safe_get(ax.motor, "error"),
            "encoder": safe_get(ax.encoder, "error"),
        },
        "motor_config": {
            "current_lim_a": safe_get(motor_cfg, "current_lim"),
            "phase_resistance_ohm": safe_get(motor_cfg, "phase_resistance"),
            "phase_inductance_h": safe_get(motor_cfg, "phase_inductance"),
            "pole_pairs": safe_get(motor_cfg, "pole_pairs"),
            "pre_calibrated": safe_get(motor_cfg, "pre_calibrated"),
        },
        "encoder_config": {
            "cpr": safe_get(ax.encoder.config, "cpr"),
            "pre_calibrated": safe_get(ax.encoder.config, "pre_calibrated"),
        },
        "controller_config": {
            "control_mode": safe_get(ctrl_cfg, "control_mode"),
            "input_mode": safe_get(ctrl_cfg, "input_mode"),
            "pos_gain": safe_get(ctrl_cfg, "pos_gain"),
            "vel_gain": safe_get(ctrl_cfg, "vel_gain"),
            "vel_integrator_gain": safe_get(ctrl_cfg, "vel_integrator_gain"),
            "vel_ramp_rate": safe_get(ctrl_cfg, "vel_ramp_rate"),
        },
        "watchdog": {
            "enabled": safe_get(axis_cfg, "enable_watchdog"),
            "timeout_s": safe_get(axis_cfg, "watchdog_timeout"),
        },
    }
    return summary


def apply_profile(odrv, profile: str, current_lim: float, watchdog_timeout: float):
    ax = odrv.axis0
    gains = GAINS_GEARBOX if profile == "gearbox" else GAINS_BARE

    ax.motor.config.current_lim = current_lim
    ax.controller.config.pos_gain = gains["pos"]
    ax.controller.config.vel_gain = gains["vel"]
    ax.controller.config.vel_integrator_gain = gains["int"]
    ax.controller.config.vel_ramp_rate = gains["ramp"]

    # Best-effort watchdog enable. Older / clone firmware may differ.
    try:
        ax.config.watchdog_timeout = watchdog_timeout
        ax.config.enable_watchdog = True
    except Exception:
        pass


def format_version(version_dict):
    major = version_dict.get("major")
    minor = version_dict.get("minor")
    revision = version_dict.get("revision")
    if major is None or minor is None or revision is None:
        return "unknown"
    suffix = "-unreleased" if version_dict.get("unreleased") else ""
    return f"{major}.{minor}.{revision}{suffix}"


def main():
    parser = argparse.ArgumentParser(description="Probe an ODrive-compatible motor controller.")
    parser.add_argument("--timeout", type=float, default=20.0, help="USB discovery timeout in seconds")
    parser.add_argument(
        "--profile",
        choices=["none", "bare", "gearbox"],
        default="none",
        help="Apply a safe gain/current profile after connecting",
    )
    parser.add_argument("--current-limit", type=float, default=10.0, help="Motor current limit in amps")
    parser.add_argument("--watchdog-timeout", type=float, default=0.5, help="Watchdog timeout in seconds")
    parser.add_argument("--json-out", type=Path, help="Optional path to save the summary as JSON")
    args = parser.parse_args()

    try:
        import odrive
    except Exception as exc:
        print(f"Failed to import odrive package: {exc}", file=sys.stderr)
        return 2

    print(f"Scanning for ODrive-compatible device (timeout={args.timeout:.1f}s)...")
    try:
        odrv = odrive.find_any(timeout=args.timeout)
    except Exception as exc:
        print(f"Connection failed: {exc}", file=sys.stderr)
        return 1

    if args.profile != "none":
        apply_profile(odrv, args.profile, args.current_limit, args.watchdog_timeout)

    summary = summarize_device(odrv)

    print()
    print("Device summary")
    print("--------------")
    print(f"Serial:         {summary['serial_number']}")
    print(f"Bus voltage:    {summary['bus_voltage_v']:.2f} V" if summary["bus_voltage_v"] is not None else "Bus voltage:    unknown")
    print(f"FW version:     {format_version(summary['fw_version'])}")
    print(f"HW version:     {summary['hw_version']['major']}.{summary['hw_version']['minor']} variant {summary['hw_version']['variant']}")
    print(f"Axis state:     {summary['axis_state']}")
    print(
        "Errors:         "
        f"axis={summary['errors']['axis']} "
        f"motor={summary['errors']['motor']} "
        f"encoder={summary['errors']['encoder']}"
    )

    motor_cfg = summary["motor_config"]
    phase_r_mohm = None if motor_cfg["phase_resistance_ohm"] is None else motor_cfg["phase_resistance_ohm"] * 1000.0
    phase_l_uh = None if motor_cfg["phase_inductance_h"] is None else motor_cfg["phase_inductance_h"] * 1e6
    print(f"Current limit:  {motor_cfg['current_lim_a']} A")
    print(f"Phase R:        {phase_r_mohm:.2f} mOhm" if phase_r_mohm is not None else "Phase R:        unknown")
    print(f"Phase L:        {phase_l_uh:.2f} uH" if phase_l_uh is not None else "Phase L:        unknown")
    print(f"Pole pairs:     {motor_cfg['pole_pairs']}")
    print(f"Encoder CPR:    {summary['encoder_config']['cpr']}")
    print(
        "Watchdog:       "
        f"enabled={summary['watchdog']['enabled']} timeout={summary['watchdog']['timeout_s']}"
    )

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(summary, indent=2))
        print(f"\nSaved summary to: {args.json_out}")

    # Quick health readout for the D6374 setup.
    if phase_r_mohm is not None and not math.isnan(phase_r_mohm):
        if 10.0 <= phase_r_mohm <= 100.0:
            print("Phase resistance looks plausible for the D6374 stack.")
        else:
            print("Phase resistance looks suspicious. Re-check calibration and motor params.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
