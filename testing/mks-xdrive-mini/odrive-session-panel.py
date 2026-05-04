"""
Thin Tkinter bench panel for the MKS ODrive Mini sprint stack.

Design goals:
- use the proven CLI path instead of duplicating controller logic
- one USB/native-protocol client at a time
- explicit, self-contained actions for bench use
- clear status and command log with minimal hidden state
"""

from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk


ROOT = Path(__file__).resolve().parent
CLI = ROOT / "mks_agent_control.py"
PANEL_TITLE = "MKS Motor Bench Panel"
TEXT_WIDTH = 14


class BenchPanel:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(PANEL_TITLE)
        self.root.geometry("980x760")
        self.root.minsize(900, 680)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.python = Path(sys.executable)
        self.worker: threading.Thread | None = None
        self.command_queue: queue.Queue[tuple[str, list[str], bool]] = queue.Queue()
        self.busy = False
        self.alive = True

        self.profile_var = tk.StringVar(value="bare")
        self.ratio_var = tk.StringVar(value="1")
        self.current_limit_var = tk.StringVar(value="5")
        self.timeout_var = tk.StringVar(value="20")
        self.watchdog_var = tk.StringVar(value="0.5")
        self.auto_cal_var = tk.BooleanVar(value=True)

        self.velocity_var = tk.StringVar(value="6")
        self.velocity_seconds_var = tk.StringVar(value="1")
        self.torque_var = tk.StringVar(value="0.1")
        self.torque_seconds_var = tk.StringVar(value="1")
        self.position_var = tk.StringVar(value="45")
        self.position_timeout_var = tk.StringVar(value="8")

        self.connection_var = tk.StringVar(value=f"Python: {self.python}")
        self.status_var = tk.StringVar(value="Idle")
        self.summary_var = tk.StringVar(value="No controller data yet.")

        self.value_labels: dict[str, ttk.Label] = {}
        self.action_buttons: list[ttk.Button] = []

        self._build_ui()
        self._start_worker()
        self.log("Thin GUI ready. Commands run through mks_agent_control.py one at a time.")

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=10)
        outer.pack(fill="both", expand=True)

        top = ttk.Frame(outer)
        top.pack(fill="x")

        config = ttk.LabelFrame(top, text="Session Config", padding=10)
        config.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self._grid_labeled_entry(config, "Profile", 0, ttk.Combobox(config, textvariable=self.profile_var, values=["bare", "gearbox"], state="readonly", width=12))
        self._grid_labeled_entry(config, "Ratio", 1, ttk.Entry(config, textvariable=self.ratio_var, width=10))
        self._grid_labeled_entry(config, "Current Limit (A)", 2, ttk.Entry(config, textvariable=self.current_limit_var, width=10))
        self._grid_labeled_entry(config, "Connect Timeout (s)", 3, ttk.Entry(config, textvariable=self.timeout_var, width=10))
        self._grid_labeled_entry(config, "Watchdog (s)", 4, ttk.Entry(config, textvariable=self.watchdog_var, width=10))

        preset_row = ttk.Frame(config)
        preset_row.grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Checkbutton(preset_row, text="Auto-calibrate on motion", variable=self.auto_cal_var).pack(side="left")

        preset_buttons = ttk.Frame(config)
        preset_buttons.grid(row=6, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self._add_action_button(preset_buttons, "Bare Preset", self.use_bare_preset).pack(side="left", padx=(0, 6))
        self._add_action_button(preset_buttons, "Gearbox Preset", self.use_gearbox_preset).pack(side="left")

        session = ttk.LabelFrame(top, text="Controller", padding=10)
        session.pack(side="left", fill="both", expand=True)

        ttk.Label(session, textvariable=self.connection_var, wraplength=360, justify="left").pack(anchor="w")
        ttk.Label(session, textvariable=self.status_var, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 0))
        ttk.Label(session, textvariable=self.summary_var, wraplength=360, justify="left").pack(anchor="w", pady=(6, 0))

        session_buttons = ttk.Frame(session)
        session_buttons.pack(anchor="w", pady=(10, 0))
        self._add_action_button(session_buttons, "Refresh Status", self.refresh_status).pack(side="left", padx=(0, 6))
        self._add_action_button(session_buttons, "Calibrate", self.calibrate).pack(side="left", padx=(0, 6))
        self._add_action_button(session_buttons, "Idle", self.idle).pack(side="left", padx=(0, 6))
        self._add_action_button(session_buttons, "Smoke Test", self.smoke_test).pack(side="left", padx=(0, 6))

        mid = ttk.Frame(outer)
        mid.pack(fill="both", expand=True, pady=(10, 0))

        telemetry = ttk.LabelFrame(mid, text="Last Status Snapshot", padding=10)
        telemetry.pack(side="left", fill="both", expand=True, padx=(0, 6))

        fields = [
            "Bus V",
            "Axis State",
            "Errors",
            "Iq A",
            "Output RPM",
            "Output Deg",
            "Output Nm",
            "Current Limit",
            "Phase R mOhm",
            "Phase L uH",
        ]
        for row, label in enumerate(fields):
            ttk.Label(telemetry, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=4)
            value = ttk.Label(telemetry, text="--", anchor="center", relief="sunken", width=TEXT_WIDTH)
            value.grid(row=row, column=1, sticky="ew", pady=4)
            self.value_labels[label] = value
        telemetry.columnconfigure(1, weight=1)

        actions = ttk.LabelFrame(mid, text="Bench Actions", padding=10)
        actions.pack(side="left", fill="both", expand=True)

        vel_row = ttk.Frame(actions)
        vel_row.pack(fill="x", pady=4)
        ttk.Label(vel_row, text="Velocity RPM").pack(side="left")
        ttk.Entry(vel_row, textvariable=self.velocity_var, width=10).pack(side="left", padx=(8, 6))
        ttk.Label(vel_row, text="Seconds").pack(side="left")
        ttk.Entry(vel_row, textvariable=self.velocity_seconds_var, width=8).pack(side="left", padx=(8, 6))
        self._add_action_button(vel_row, "Run Velocity", self.run_velocity).pack(side="left", padx=(8, 0))

        tq_row = ttk.Frame(actions)
        tq_row.pack(fill="x", pady=4)
        ttk.Label(tq_row, text="Torque Nm").pack(side="left")
        ttk.Entry(tq_row, textvariable=self.torque_var, width=10).pack(side="left", padx=(18, 6))
        ttk.Label(tq_row, text="Seconds").pack(side="left")
        ttk.Entry(tq_row, textvariable=self.torque_seconds_var, width=8).pack(side="left", padx=(8, 6))
        self._add_action_button(tq_row, "Run Torque", self.run_torque).pack(side="left", padx=(8, 0))

        pos_row = ttk.Frame(actions)
        pos_row.pack(fill="x", pady=4)
        ttk.Label(pos_row, text="Position Deg").pack(side="left")
        ttk.Entry(pos_row, textvariable=self.position_var, width=10).pack(side="left", padx=(10, 6))
        ttk.Label(pos_row, text="Timeout").pack(side="left")
        ttk.Entry(pos_row, textvariable=self.position_timeout_var, width=8).pack(side="left", padx=(8, 6))
        self._add_action_button(pos_row, "Run Position", self.run_position).pack(side="left", padx=(8, 0))

        notes = ttk.Label(
            actions,
            text=(
                "Commands are self-contained: connect, apply profile, optional calibrate, "
                "run, then return to idle. Keep one GUI or CLI client only."
            ),
            wraplength=360,
            justify="left",
        )
        notes.pack(anchor="w", pady=(12, 0))

        log_frame = ttk.LabelFrame(outer, text="Command Log", padding=10)
        log_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.log_text = tk.Text(log_frame, height=16, wrap="word")
        self.log_text.pack(fill="both", expand=True)

    def _grid_labeled_entry(self, parent, text: str, row: int, widget):
        ttk.Label(parent, text=text).grid(row=row, column=0, sticky="e", padx=(0, 8), pady=4)
        widget.grid(row=row, column=1, sticky="w", pady=4)

    def _add_action_button(self, parent, text: str, command):
        button = ttk.Button(parent, text=text, command=command)
        self.action_buttons.append(button)
        return button

    def _start_worker(self):
        def worker():
            while self.alive:
                try:
                    label, args, expect_status = self.command_queue.get(timeout=0.2)
                except queue.Empty:
                    continue
                self.root.after(0, lambda: self._set_busy(True, label))
                self._run_cli(label, args, expect_status)
                self.command_queue.task_done()
                self.root.after(0, lambda: self._set_busy(False, "Idle"))

        self.worker = threading.Thread(target=worker, daemon=True)
        self.worker.start()

    def _base_args(self) -> list[str]:
        return [
            str(CLI),
            "--profile",
            self.profile_var.get(),
            "--ratio",
            self.ratio_var.get().strip(),
            "--current-limit",
            self.current_limit_var.get().strip(),
            "--connect-timeout",
            self.timeout_var.get().strip(),
            "--watchdog-timeout",
            self.watchdog_var.get().strip(),
        ]

    def _enqueue(self, label: str, extra_args: list[str], expect_status: bool = True):
        self.command_queue.put((label, self._base_args() + extra_args, expect_status))

    def _run_cli(self, label: str, args: list[str], expect_status: bool):
        started = time.time()
        self.log(f"{label}: running {' '.join(args[len(self._base_args()) - 1:])}")
        try:
            result = subprocess.run(
                [str(self.python)] + args,
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self.log(f"{label}: timed out"))
            return
        except Exception as exc:
            self.root.after(0, lambda: self.log(f"{label}: launch failed: {exc}"))
            return

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        payload = None

        if stdout:
            try:
                payload = json.loads(stdout)
            except json.JSONDecodeError:
                payload = None

        elapsed = time.time() - started
        if result.returncode == 0 and payload and payload.get("ok"):
            self.root.after(0, lambda: self.log(f"{label}: ok ({elapsed:.1f} s)"))
            if expect_status:
                self.root.after(0, lambda: self._update_from_payload(payload))
        else:
            detail = None
            if payload and isinstance(payload, dict):
                detail = payload.get("error")
            if not detail:
                detail = stderr or stdout or f"exit code {result.returncode}"
            self.root.after(0, lambda: self.log(f"{label}: failed - {detail}"))
            if stderr and stderr != detail:
                self.root.after(0, lambda: self.log(f"{label}: stderr - {stderr}"))

    def _set_busy(self, busy: bool, status_text: str):
        self.busy = busy
        self.status_var.set(status_text)
        new_state = "disabled" if busy else "normal"
        for button in self.action_buttons:
            button.configure(state=new_state)

    def _update_from_payload(self, payload: dict):
        status = payload.get("status")
        if status is None:
            status = payload.get("end") or payload.get("start")
        if not status:
            return

        telemetry = status.get("telemetry", {})
        errors = status.get("errors", {})
        motor_cfg = status.get("motor_config", {})
        axis_state = status.get("axis_state", {})
        bus = status.get("bus_voltage_v")
        phase_r = motor_cfg.get("phase_resistance_ohm")
        phase_l = motor_cfg.get("phase_inductance_h")

        self.value_labels["Bus V"].configure(text=self._fmt(bus, 2))
        self.value_labels["Axis State"].configure(text=axis_state.get("name", "--"))
        self.value_labels["Errors"].configure(text=str(errors.get("combined", "--")))
        self.value_labels["Iq A"].configure(text=self._fmt(telemetry.get("iq_a"), 3))
        self.value_labels["Output RPM"].configure(text=self._fmt(telemetry.get("output_rpm"), 2))
        self.value_labels["Output Deg"].configure(text=self._fmt(telemetry.get("output_deg"), 2))
        self.value_labels["Output Nm"].configure(text=self._fmt(telemetry.get("output_torque_nm"), 3))
        self.value_labels["Current Limit"].configure(text=self._fmt(motor_cfg.get("current_lim_a"), 1))
        self.value_labels["Phase R mOhm"].configure(text=self._fmt(None if phase_r is None else phase_r * 1000.0, 2))
        self.value_labels["Phase L uH"].configure(text=self._fmt(None if phase_l is None else phase_l * 1e6, 2))

        serial = status.get("serial_number", "unknown")
        profile = status.get("profile", self.profile_var.get())
        ratio = status.get("ratio", self.ratio_var.get())
        self.summary_var.set(
            f"Serial {serial} | Profile {profile} | Ratio {ratio} | "
            f"State {axis_state.get('name', '--')} | Errors {errors.get('combined', '--')}"
        )

    def _fmt(self, value, digits: int) -> str:
        if value is None:
            return "--"
        try:
            return f"{float(value):.{digits}f}"
        except Exception:
            return str(value)

    def log(self, message: str):
        stamp = time.strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{stamp}] {message}\n")
        self.log_text.see("end")

    def use_bare_preset(self):
        self.profile_var.set("bare")
        self.ratio_var.set("1")
        self.current_limit_var.set("5")
        self.velocity_var.set("6")
        self.torque_var.set("0.1")
        self.position_var.set("45")
        self.log("Applied bare-motor preset.")

    def use_gearbox_preset(self):
        self.profile_var.set("gearbox")
        self.ratio_var.set("5")
        self.current_limit_var.set("10")
        self.velocity_var.set("10")
        self.torque_var.set("0.5")
        self.position_var.set("45")
        self.log("Applied gearbox preset.")

    def refresh_status(self):
        self._enqueue("Status", ["status"])

    def calibrate(self):
        self._enqueue("Calibrate", ["calibrate"])

    def idle(self):
        self._enqueue("Idle", ["idle"], expect_status=False)

    def smoke_test(self):
        args = ["velocity", "--rpm", "5", "--seconds", "1", "--calibrate"]
        self._enqueue("Smoke Test", args)

    def run_velocity(self):
        args = [
            "velocity",
            "--rpm",
            self.velocity_var.get().strip(),
            "--seconds",
            self.velocity_seconds_var.get().strip(),
        ]
        if self.auto_cal_var.get():
            args.append("--calibrate")
        self._enqueue("Velocity", args)

    def run_torque(self):
        args = [
            "torque",
            "--nm",
            self.torque_var.get().strip(),
            "--seconds",
            self.torque_seconds_var.get().strip(),
        ]
        if self.auto_cal_var.get():
            args.append("--calibrate")
        self._enqueue("Torque", args)

    def run_position(self):
        args = [
            "position",
            "--deg",
            self.position_var.get().strip(),
            "--timeout-s",
            self.position_timeout_var.get().strip(),
        ]
        if self.auto_cal_var.get():
            args.append("--calibrate")
        self._enqueue("Position", args)

    def on_close(self):
        self.alive = False
        self.root.destroy()


def main():
    root = tk.Tk()
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    BenchPanel(root)
    root.mainloop()


if __name__ == "__main__":
    main()
