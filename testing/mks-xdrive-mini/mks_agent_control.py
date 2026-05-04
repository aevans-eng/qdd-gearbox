"""
Agent-safe control CLI for the MKS XDrive Mini / ODrive-compatible sprint stack.

Design intent:
- Be usable by Codex / Claude directly from the shell
- Minimize dangerous persistent controller state
- Default motion commands are self-contained:
  connect -> apply safe profile -> closed loop -> execute -> zero -> idle -> exit
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path


KT = 0.0551
GAINS_BARE = {"pos": 5.0, "vel": 0.05, "int": 0.05, "ramp": 3.0}
GAINS_GEARBOX = {"pos": 15.0, "vel": 0.10, "int": 0.20, "ramp": 10.0}
STATE_NAMES = {
    0: "UNDEFINED",
    1: "IDLE",
    2: "STARTUP",
    3: "FULL_CALIBRATION_SEQUENCE",
    8: "CLOSED_LOOP_CONTROL",
}


def safe_get(obj, attr, default=None):
    try:
        return getattr(obj, attr)
    except Exception:
        return default


def state_name(num):
    return STATE_NAMES.get(num, str(num))


class ControllerSession:
    def __init__(self, timeout: float, profile: str, ratio: float, current_limit: float, watchdog_timeout: float):
        self.timeout = timeout
        self.profile = profile
        self.ratio = max(1.0, ratio)
        self.current_limit = current_limit
        self.watchdog_timeout = watchdog_timeout
        self.odrv = None

    def connect(self):
        import odrive

        self.odrv = odrive.find_any(timeout=self.timeout)
        self.apply_profile()
        self.clear_errors()
        return self.odrv

    def gains(self):
        return GAINS_GEARBOX if self.profile == "gearbox" else GAINS_BARE

    def apply_profile(self):
        ax = self.odrv.axis0
        gains = self.gains()

        ax.motor.config.current_lim = self.current_limit
        ax.controller.config.pos_gain = gains["pos"]
        ax.controller.config.vel_gain = gains["vel"]
        ax.controller.config.vel_integrator_gain = gains["int"]
        ax.controller.config.vel_ramp_rate = gains["ramp"]

        try:
            ax.config.watchdog_timeout = self.watchdog_timeout
            ax.config.enable_watchdog = False
        except Exception:
            pass

    def set_watchdog_enabled(self, enabled: bool):
        if self.odrv is None:
            return
        try:
            self.odrv.axis0.config.enable_watchdog = enabled
        except Exception:
            pass

    def feed_watchdog(self):
        try:
            self.odrv.axis0.watchdog_feed()
        except Exception:
            pass

    def clear_errors(self):
        if self.odrv is None:
            return
        ax = self.odrv.axis0
        for target in (ax, ax.motor, ax.encoder, ax.controller):
            try:
                target.error = 0
            except Exception:
                pass

    def calibrate(self):
        ax = self.odrv.axis0
        watchdog_enabled = safe_get(ax.config, "enable_watchdog")
        try:
            ax.config.enable_watchdog = False
        except Exception:
            watchdog_enabled = None

        try:
            ax.requested_state = 3
            deadline = time.time() + 25.0
            while time.time() < deadline:
                if ax.current_state == 1:
                    return
                time.sleep(0.25)
            raise TimeoutError("Calibration timed out before returning to IDLE")
        finally:
            if watchdog_enabled is not None:
                try:
                    ax.config.enable_watchdog = watchdog_enabled
                except Exception:
                    pass

    def enter_closed_loop(self):
        ax = self.odrv.axis0
        ax.controller.input_vel = 0
        ax.controller.input_torque = 0
        ax.requested_state = 8
        time.sleep(0.25)
        if ax.current_state != 8:
            raise RuntimeError(f"Failed to enter closed loop, state={ax.current_state}")

    def zero_and_idle(self):
        if self.odrv is None:
            return
        ax = self.odrv.axis0
        self.set_watchdog_enabled(False)
        try:
            ax.controller.input_vel = 0
        except Exception:
            pass
        try:
            ax.controller.input_torque = 0
        except Exception:
            pass
        try:
            ax.requested_state = 1
        except Exception:
            pass

    def status(self):
        ax = self.odrv.axis0
        iq = safe_get(ax.motor.current_control, "Iq_measured")
        motor_vel = safe_get(ax.encoder, "vel_estimate")
        motor_pos = safe_get(ax.encoder, "pos_estimate")
        errors = safe_get(ax, "error", 0) | safe_get(ax.motor, "error", 0) | safe_get(ax.encoder, "error", 0)

        output_rpm = None if motor_vel is None else motor_vel * 60.0 / self.ratio
        output_deg = None if motor_pos is None else motor_pos * 360.0 / self.ratio
        motor_nm = None if iq is None else KT * iq
        output_nm = None if motor_nm is None else motor_nm * self.ratio

        return {
            "bus_voltage_v": safe_get(self.odrv, "vbus_voltage"),
            "serial_number": str(safe_get(self.odrv, "serial_number", "unknown")),
            "fw_version": {
                "major": safe_get(self.odrv, "fw_version_major"),
                "minor": safe_get(self.odrv, "fw_version_minor"),
                "revision": safe_get(self.odrv, "fw_version_revision"),
            },
            "axis_state": {
                "code": safe_get(ax, "current_state"),
                "name": state_name(safe_get(ax, "current_state")),
            },
            "errors": {
                "axis": safe_get(ax, "error"),
                "motor": safe_get(ax.motor, "error"),
                "encoder": safe_get(ax.encoder, "error"),
                "combined": errors,
            },
            "telemetry": {
                "iq_a": iq,
                "motor_torque_nm": motor_nm,
                "output_torque_nm": output_nm,
                "output_rpm": output_rpm,
                "output_deg": output_deg,
            },
            "motor_config": {
                "current_lim_a": safe_get(ax.motor.config, "current_lim"),
                "phase_resistance_ohm": safe_get(ax.motor.config, "phase_resistance"),
                "phase_inductance_h": safe_get(ax.motor.config, "phase_inductance"),
            },
            "profile": self.profile,
            "ratio": self.ratio,
        }

    def set_velocity(self, output_rpm: float):
        ax = self.odrv.axis0
        motor_tps = output_rpm * self.ratio / 60.0
        ax.controller.config.control_mode = 2
        ax.controller.config.input_mode = 1
        ax.controller.input_vel = motor_tps

    def prepare_mode(self, mode: str):
        ax = self.odrv.axis0
        if mode == "velocity":
            ax.controller.config.control_mode = 2
            ax.controller.config.input_mode = 1
            ax.controller.input_vel = 0
        elif mode == "torque":
            ax.controller.config.control_mode = 1
            ax.controller.config.input_mode = 1
            ax.controller.input_torque = 0
        elif mode == "position":
            ax.controller.config.control_mode = 3
            ax.controller.config.input_mode = 5

    def set_torque(self, output_nm: float):
        ax = self.odrv.axis0
        motor_nm = output_nm / self.ratio
        max_motor_nm = KT * self.current_limit
        motor_nm = max(-max_motor_nm, min(max_motor_nm, motor_nm))
        ax.controller.config.control_mode = 1
        ax.controller.config.input_mode = 1
        ax.controller.input_torque = motor_nm

    def move_position(self, output_deg: float, timeout_s: float = 8.0, tolerance_deg: float = 3.0):
        ax = self.odrv.axis0
        motor_turns = output_deg * self.ratio / 360.0
        ax.controller.config.control_mode = 3
        ax.controller.config.input_mode = 5
        ax.trap_traj.config.vel_limit = max(1.0, 30.0 * self.ratio / 60.0)
        ax.trap_traj.config.accel_limit = 10.0
        ax.trap_traj.config.decel_limit = 10.0
        ax.controller.input_pos = motor_turns

        deadline = time.time() + timeout_s
        while time.time() < deadline:
            current_motor_pos = safe_get(ax.encoder, "pos_estimate")
            if current_motor_pos is not None:
                current_output_deg = current_motor_pos * 360.0 / self.ratio
                if abs(current_output_deg - output_deg) <= tolerance_deg:
                    return
            self.feed_watchdog()
            time.sleep(0.15)
        raise TimeoutError("Position move timed out")


def print_json(payload):
    print(json.dumps(payload, indent=2))


def run_self_contained_motion(session: ControllerSession, args, mode: str):
    session.connect()
    if args.calibrate:
        session.calibrate()
    session.clear_errors()
    session.prepare_mode(mode)
    session.set_watchdog_enabled(True)
    session.feed_watchdog()
    session.enter_closed_loop()

    started = session.status()
    started["phase"] = "start"

    try:
        if mode == "velocity":
            session.set_velocity(args.rpm)
            deadline = time.time() + args.seconds
            while time.time() < deadline:
                session.feed_watchdog()
                time.sleep(0.1)
        elif mode == "torque":
            session.set_torque(args.nm)
            deadline = time.time() + args.seconds
            while time.time() < deadline:
                session.feed_watchdog()
                time.sleep(0.1)
        elif mode == "position":
            session.move_position(args.deg, timeout_s=args.timeout_s)
        else:
            raise ValueError(f"Unsupported motion mode: {mode}")

        ended = session.status()
        ended["phase"] = "end"
        print_json({"ok": True, "command": mode, "start": started, "end": ended})
    finally:
        session.zero_and_idle()


def main():
    parser = argparse.ArgumentParser(description="Agent-safe CLI for MKS XDrive Mini / ODrive-compatible control.")
    parser.add_argument("--connect-timeout", type=float, default=20.0)
    parser.add_argument("--profile", choices=["gearbox", "bare"], default="gearbox")
    parser.add_argument("--ratio", type=float, default=5.0)
    parser.add_argument("--current-limit", type=float, default=10.0)
    parser.add_argument("--watchdog-timeout", type=float, default=0.5)

    sub = parser.add_subparsers(dest="command", required=True)

    probe = sub.add_parser("probe")
    probe.add_argument("--json-out", type=Path)

    sub.add_parser("status")
    cal = sub.add_parser("calibrate")
    cal.add_argument("--json-out", type=Path)

    vel = sub.add_parser("velocity")
    vel.add_argument("--rpm", type=float, required=True)
    vel.add_argument("--seconds", type=float, default=2.0)
    vel.add_argument("--calibrate", action="store_true")

    tq = sub.add_parser("torque")
    tq.add_argument("--nm", type=float, required=True)
    tq.add_argument("--seconds", type=float, default=2.0)
    tq.add_argument("--calibrate", action="store_true")

    pos = sub.add_parser("position")
    pos.add_argument("--deg", type=float, required=True)
    pos.add_argument("--timeout-s", type=float, default=8.0)
    pos.add_argument("--calibrate", action="store_true")

    sub.add_parser("idle")

    args = parser.parse_args()

    try:
        session = ControllerSession(
            timeout=args.connect_timeout,
            profile=args.profile,
            ratio=args.ratio,
            current_limit=args.current_limit,
            watchdog_timeout=args.watchdog_timeout,
        )

        if args.command == "probe":
            session.connect()
            payload = {"ok": True, "command": "probe", "status": session.status()}
            if args.json_out:
                args.json_out.parent.mkdir(parents=True, exist_ok=True)
                args.json_out.write_text(json.dumps(payload, indent=2))
            print_json(payload)
            session.zero_and_idle()
            return 0

        if args.command == "status":
            session.connect()
            print_json({"ok": True, "command": "status", "status": session.status()})
            session.zero_and_idle()
            return 0

        if args.command == "calibrate":
            session.connect()
            session.calibrate()
            payload = {"ok": True, "command": "calibrate", "status": session.status()}
            if args.json_out:
                args.json_out.parent.mkdir(parents=True, exist_ok=True)
                args.json_out.write_text(json.dumps(payload, indent=2))
            print_json(payload)
            session.zero_and_idle()
            return 0

        if args.command == "velocity":
            run_self_contained_motion(session, args, "velocity")
            return 0

        if args.command == "torque":
            run_self_contained_motion(session, args, "torque")
            return 0

        if args.command == "position":
            run_self_contained_motion(session, args, "position")
            return 0

        if args.command == "idle":
            session.connect()
            session.zero_and_idle()
            print_json({"ok": True, "command": "idle"})
            return 0

        raise ValueError(f"Unknown command: {args.command}")

    except Exception as exc:
        print_json({"ok": False, "error": str(exc), "command": args.command})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
