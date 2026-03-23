"""
ODrive Control Panel — QDD Test Sessions
Tkinter GUI for safe motor control and live telemetry.

All values shown in OUTPUT SHAFT units (after gear ratio).
ODrive commands are in motor shaft units — conversions happen internally.

Two-tier limits:
  ABSOLUTE MAX — hardcoded safety ceiling, cannot be exceeded
  USER MAX     — adjustable in GUI, sets slider range

Safety features:
- E-stop button (spacebar / Escape) -> immediate IDLE
- Closing window -> automatic IDLE
- All sliders default to zero
- Must explicitly enter closed-loop before any motion
- Current limit enforced on ODrive at connect and on change

Equations (motor -> output):
  Motor Torque (Nm) = Kt * Iq      (Kt = 8.27 / 150KV = 0.0551 Nm/A)
  Output Torque     = Motor Torque * gear_ratio
  Output Speed      = Motor t/s * 60 / gear_ratio  (RPM)
  Output Position   = Motor turns * 360 / gear_ratio  (deg)
"""

import tkinter as tk
from tkinter import ttk
import threading
import time

# --- Absolute Limits (hardcoded safety ceiling) ---
ABS_MAX_MOTOR_VEL = 5.0    # motor t/s — PID stability limit (FW 0.5.5)
ABS_MAX_CURRENT = 19.0     # A — ODrive software limit for D6374
ABS_MAX_GEAR_RATIO = 20.0  # sanity cap

# --- Defaults ---
DEFAULT_GEAR_RATIO = 5.0
DEFAULT_CURRENT_LIM = 10.0        # A
DEFAULT_MAX_OUTPUT_RPM = 60.0     # RPM at output
DEFAULT_MOVE_SPEED_RPM = 30.0     # RPM for position moves
ABS_MAX_MOVE_RPM = 300.0          # Position mode can go faster than vel PID limit
KT = 0.0551                       # Nm/A (8.27 / 150KV)
POLL_RATE_MS = 100

# PID gains
GAINS_GEARBOX = {"pos": 15.0, "vel": 0.1, "int": 0.2, "ramp": 10.0}
GAINS_BARE = {"pos": 5.0, "vel": 0.05, "int": 0.05, "ramp": 3.0}

# State names
STATE_NAMES = {
    0: "UNDEFINED", 1: "IDLE", 2: "STARTUP", 3: "FULL_CAL",
    4: "MOTOR_CAL", 6: "ENC_INDEX", 7: "ENC_OFFSET",
    8: "CLOSED_LOOP", 9: "LOCKIN_SPIN", 10: "LOCKIN_RAMP",
}


class ODriveControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("ODrive Control Panel — QDD Testing")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<space>", lambda e: self.estop())
        self.root.bind("<Escape>", lambda e: self.estop())

        self.odrv = None
        self.connected = False
        self.in_closed_loop = False
        self.polling = False

        self.build_ui()

    # --- Helpers ---
    def gear_ratio(self):
        try:
            r = float(self.gear_ratio_var.get())
            return max(1.0, min(ABS_MAX_GEAR_RATIO, r))
        except (ValueError, tk.TclError):
            return DEFAULT_GEAR_RATIO

    def is_gearbox(self):
        return self.config_var.get() == "gearbox"

    def ratio(self):
        return self.gear_ratio() if self.is_gearbox() else 1.0

    def current_limit(self):
        try:
            return max(1.0, min(ABS_MAX_CURRENT, float(self.current_lim_var.get())))
        except (ValueError, tk.TclError):
            return DEFAULT_CURRENT_LIM

    def max_output_rpm(self):
        try:
            user_rpm = max(1.0, float(self.max_rpm_var.get()))
        except (ValueError, tk.TclError):
            user_rpm = DEFAULT_MAX_OUTPUT_RPM
        # Clamp to absolute max
        abs_max_rpm = ABS_MAX_MOTOR_VEL * 60.0 / self.ratio()
        return min(user_rpm, abs_max_rpm)

    def max_output_torque(self):
        return KT * self.current_limit() * self.ratio()

    def move_speed_motor_tps(self):
        try:
            rpm = max(1.0, float(self.move_speed_var.get()))
        except (ValueError, tk.TclError):
            rpm = DEFAULT_MOVE_SPEED_RPM
        rpm = min(rpm, ABS_MAX_MOVE_RPM)
        return rpm * self.ratio() / 60.0  # convert output RPM to motor t/s

    # --- UI ---
    def build_ui(self):
        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=5)

        # --- Connection ---
        conn = ttk.LabelFrame(top, text="Connection", padding=8)
        conn.pack(side="left", fill="both", expand=True, padx=(0, 5))

        row0 = ttk.Frame(conn)
        row0.pack(fill="x")
        self.btn_connect = ttk.Button(row0, text="Connect", command=self.connect)
        self.btn_connect.pack(side="left", padx=5)
        self.lbl_status = ttk.Label(row0, text="Disconnected", foreground="red")
        self.lbl_status.pack(side="left", padx=10)

        row1 = ttk.Frame(conn)
        row1.pack(fill="x", pady=(5, 0))
        self.config_var = tk.StringVar(value="gearbox")
        ttk.Radiobutton(row1, text="Gearbox", variable=self.config_var, value="gearbox").pack(side="left", padx=5)
        ttk.Radiobutton(row1, text="Bare Motor", variable=self.config_var, value="bare").pack(side="left", padx=5)
        ttk.Label(row1, text="Ratio:").pack(side="left", padx=(15, 2))
        self.gear_ratio_var = tk.StringVar(value=str(DEFAULT_GEAR_RATIO))
        ttk.Entry(row1, textvariable=self.gear_ratio_var, width=5).pack(side="left")
        ttk.Label(row1, text=":1").pack(side="left")

        # --- Limits ---
        lim = ttk.LabelFrame(top, text="Limits (adjustable)", padding=8)
        lim.pack(side="left", fill="both", expand=True, padx=(5, 0))

        def lim_row(parent, label, var, unit, abs_max_text, row):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky="e", padx=2)
            ttk.Entry(parent, textvariable=var, width=7).grid(row=row, column=1, padx=2)
            ttk.Label(parent, text=unit).grid(row=row, column=2, sticky="w", padx=2)
            ttk.Label(parent, text=f"(abs max: {abs_max_text})", font=("Arial", 7), foreground="gray").grid(row=row, column=3, sticky="w", padx=5)

        abs_max_vel_rpm = ABS_MAX_MOTOR_VEL * 60.0 / DEFAULT_GEAR_RATIO
        self.max_rpm_var = tk.StringVar(value=str(int(DEFAULT_MAX_OUTPUT_RPM)))
        self.current_lim_var = tk.StringVar(value=str(DEFAULT_CURRENT_LIM))
        self.move_speed_var = tk.StringVar(value=str(int(DEFAULT_MOVE_SPEED_RPM)))

        lim_row(lim, "Vel Max:", self.max_rpm_var, "RPM", f"{abs_max_vel_rpm:.0f} RPM (vel PID limit)", 0)
        lim_row(lim, "Current Limit:", self.current_lim_var, "A", f"{ABS_MAX_CURRENT:.0f}A", 1)
        lim_row(lim, "Move Speed:", self.move_speed_var, "RPM", f"for position Go (up to {ABS_MAX_MOVE_RPM:.0f})", 2)

        self.btn_apply_limits = ttk.Button(lim, text="Apply", command=self.apply_limits)
        self.btn_apply_limits.grid(row=0, column=4, rowspan=3, padx=10, sticky="ns")

        # --- Telemetry ---
        telem = ttk.LabelFrame(self.root, text="Telemetry (live from ODrive)", padding=8)
        telem.pack(fill="x", padx=10, pady=3)

        telem_items = [
            ("Bus", "V"), ("Iq", "A"), ("Motor Torque", "Nm"),
            ("Output Torque", "Nm"), ("Output Speed", "RPM"),
            ("Output Pos", "deg"), ("State", ""), ("Status", ""),
        ]
        self.telem_labels = {}
        for i, (key, unit) in enumerate(telem_items):
            label_text = f"{key} ({unit})" if unit else key
            ttk.Label(telem, text=label_text, font=("Arial", 8)).grid(row=0, column=i, padx=3, sticky="s")
            lbl = ttk.Label(telem, text="--", width=11, relief="sunken", anchor="center", font=("Consolas", 10))
            lbl.grid(row=1, column=i, padx=3, pady=2)
            self.telem_labels[key] = lbl

        # --- Equations ---
        eq = ttk.LabelFrame(self.root, text="How values are calculated", padding=4)
        eq.pack(fill="x", padx=10, pady=1)
        eq_text = (
            "Motor Torque = Kt x Iq  (Kt = 0.0551 Nm/A)  |  "
            "Output Torque = Motor Torque x ratio  |  "
            "Output Speed = Motor t/s x 60 / ratio  |  "
            "Output Pos = Motor turns x 360 / ratio"
        )
        ttk.Label(eq, text=eq_text, font=("Arial", 8), foreground="gray").pack()

        # --- Control ---
        ctrl = ttk.LabelFrame(self.root, text="Control (output shaft units)", padding=8)
        ctrl.pack(fill="x", padx=10, pady=3)

        btn_row = ttk.Frame(ctrl)
        btn_row.pack(fill="x", pady=3)
        self.btn_calibrate = ttk.Button(btn_row, text="Calibrate", command=self.calibrate, state="disabled")
        self.btn_calibrate.pack(side="left", padx=5)
        self.btn_closed_loop = ttk.Button(btn_row, text="Enter Closed Loop", command=self.enter_closed_loop, state="disabled")
        self.btn_closed_loop.pack(side="left", padx=5)
        self.btn_idle = ttk.Button(btn_row, text="IDLE (motor off, spins free)", command=self.go_idle, state="disabled")
        self.btn_idle.pack(side="left", padx=5)

        mode_row = ttk.Frame(ctrl)
        mode_row.pack(fill="x", pady=3)
        ttk.Label(mode_row, text="Mode:").pack(side="left", padx=5)
        self.mode_var = tk.StringVar(value="velocity")
        for text, val in [("Velocity", "velocity"), ("Position", "position"), ("Torque", "torque")]:
            ttk.Radiobutton(mode_row, text=text, variable=self.mode_var, value=val, command=self.on_mode_change).pack(side="left", padx=5)

        # Velocity
        self.vel_frame = ttk.Frame(ctrl)
        ttk.Label(self.vel_frame, text="Speed (RPM):").pack(side="left", padx=5)
        self.vel_slider = tk.Scale(self.vel_frame, from_=-DEFAULT_MAX_OUTPUT_RPM, to=DEFAULT_MAX_OUTPUT_RPM,
                                   resolution=1, orient="horizontal", length=400,
                                   command=self.on_vel_change)
        self.vel_slider.set(0)
        self.vel_slider.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(self.vel_frame, text="Zero", command=lambda: self.vel_slider.set(0)).pack(side="left", padx=5)
        self.vel_frame.pack(fill="x", pady=3)

        # Position
        self.pos_frame = ttk.Frame(ctrl)
        ttk.Label(self.pos_frame, text="Position (deg):").pack(side="left", padx=5)
        self.pos_entry = ttk.Entry(self.pos_frame, width=10)
        self.pos_entry.insert(0, "0")
        self.pos_entry.pack(side="left", padx=5)
        ttk.Button(self.pos_frame, text="Go", command=self.go_to_position).pack(side="left", padx=5)
        self.lbl_move_speed = ttk.Label(self.pos_frame, text=f"(at {int(DEFAULT_MOVE_SPEED_RPM)} RPM)", font=("Arial", 8), foreground="gray")
        self.lbl_move_speed.pack(side="left", padx=5)

        # Torque
        self.torque_frame = ttk.Frame(ctrl)
        ttk.Label(self.torque_frame, text="Torque (Nm):").pack(side="left", padx=5)
        max_t = KT * DEFAULT_CURRENT_LIM * DEFAULT_GEAR_RATIO
        self.torque_slider = tk.Scale(self.torque_frame, from_=-max_t, to=max_t,
                                      resolution=0.05, orient="horizontal", length=400,
                                      command=self.on_torque_change)
        self.torque_slider.set(0)
        self.torque_slider.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(self.torque_frame, text="Zero", command=lambda: self.torque_slider.set(0)).pack(side="left", padx=5)

        # --- E-STOP ---
        estop_frame = ttk.Frame(self.root, padding=5)
        estop_frame.pack(fill="x", padx=10, pady=3)
        self.btn_estop = tk.Button(estop_frame, text="E-STOP (spacebar)",
                                   command=self.estop, bg="red", fg="white",
                                   font=("Arial", 14, "bold"), height=2)
        self.btn_estop.pack(fill="x")

        # --- Status bar ---
        self.status_bar = ttk.Label(self.root, text="Press Connect. IDLE = motor off, spins freely. E-STOP: spacebar/Escape.",
                                     relief="sunken", anchor="w", padding=4)
        self.status_bar.pack(fill="x", padx=10, pady=(0, 5))

    def log(self, msg):
        self.status_bar.config(text=msg)

    def apply_limits(self):
        """Apply user limits — update slider ranges and ODrive current limit."""
        # Update velocity slider range
        rpm = self.max_output_rpm()
        self.vel_slider.config(from_=-rpm, to=rpm)
        if abs(self.vel_slider.get()) > rpm:
            self.vel_slider.set(0)
            if self.connected and self.in_closed_loop:
                self.odrv.axis0.controller.input_vel = 0

        # Update torque slider range
        max_t = self.max_output_torque()
        self.torque_slider.config(from_=-max_t, to=max_t)
        if abs(self.torque_slider.get()) > max_t:
            self.torque_slider.set(0)
            if self.connected and self.in_closed_loop:
                self.odrv.axis0.controller.input_torque = 0

        # Update move speed label
        try:
            ms = float(self.move_speed_var.get())
        except ValueError:
            ms = DEFAULT_MOVE_SPEED_RPM
        self.lbl_move_speed.config(text=f"(at {int(ms)} RPM)")

        # Push current limit to ODrive
        if self.connected:
            cl = self.current_limit()
            self.odrv.axis0.motor.config.current_lim = cl
            self.log(f"Limits applied. Speed: ±{rpm:.0f} RPM, Current: {cl:.1f}A, Torque: ±{max_t:.2f} Nm, Move: {int(ms)} RPM")
        else:
            self.log(f"Limits updated. Speed: ±{rpm:.0f} RPM, Current: {self.current_limit():.1f}A. Connect to apply to ODrive.")

    # --- Connection ---
    def connect(self):
        if self.connected:
            return
        self.log("Connecting... please wait (can take up to 60s)")
        self.btn_connect.config(state="disabled")

        def do_connect():
            try:
                import odrive
                self.root.after(0, lambda: self.lbl_status.config(text="Scanning USB...", foreground="orange"))
                self.odrv = odrive.find_any(timeout=90)

                # Enforce current limit
                self.odrv.axis0.motor.config.current_lim = self.current_limit()

                # Set gains
                gains = GAINS_GEARBOX if self.is_gearbox() else GAINS_BARE
                ax = self.odrv.axis0
                ax.controller.config.pos_gain = gains["pos"]
                ax.controller.config.vel_gain = gains["vel"]
                ax.controller.config.vel_integrator_gain = gains["int"]
                ax.controller.config.vel_ramp_rate = gains["ramp"]

                # Set trap trajectory limits for position mode
                ax.trap_traj.config.vel_limit = self.move_speed_motor_tps()
                ax.trap_traj.config.accel_limit = 10.0
                ax.trap_traj.config.decel_limit = 10.0

                self.connected = True
                self.root.after(0, self._on_connected)
            except Exception as e:
                self.root.after(0, lambda: self._on_connect_fail(str(e)))

        threading.Thread(target=do_connect, daemon=True).start()

    def _on_connected(self):
        bus = self.odrv.vbus_voltage
        config = f"gearbox {self.gear_ratio():.0f}:1" if self.is_gearbox() else "bare motor"
        self.lbl_status.config(text=f"Connected ({config}) — {bus:.1f}V", foreground="green")
        self.btn_connect.config(state="disabled")
        self.btn_calibrate.config(state="normal")
        self.btn_closed_loop.config(state="normal")
        self.btn_idle.config(state="normal")
        self.apply_limits()
        self.start_polling()

    def _on_connect_fail(self, err):
        self.lbl_status.config(text="Connection failed", foreground="red")
        self.btn_connect.config(state="normal")
        self.log(f"Connection failed: {err}")

    # --- Telemetry ---
    def start_polling(self):
        if self.polling:
            return
        self.polling = True
        self._poll()

    def _poll(self):
        if not self.polling or not self.connected:
            return
        try:
            ax = self.odrv.axis0
            iq = ax.motor.current_control.Iq_measured
            motor_vel = ax.encoder.vel_estimate
            motor_pos = ax.encoder.pos_estimate

            r = self.ratio()
            motor_torque = KT * iq
            output_torque = motor_torque * r
            output_rpm = motor_vel * 60.0 / r
            output_deg = motor_pos * 360.0 / r

            state_num = ax.current_state
            state_name = STATE_NAMES.get(state_num, f"?{state_num}")

            self.telem_labels["Bus"].config(text=f"{self.odrv.vbus_voltage:.1f}")
            self.telem_labels["Iq"].config(text=f"{iq:.2f}")
            self.telem_labels["Motor Torque"].config(text=f"{motor_torque:.3f}")
            self.telem_labels["Output Torque"].config(text=f"{output_torque:.3f}")
            self.telem_labels["Output Speed"].config(text=f"{output_rpm:.1f}")
            self.telem_labels["Output Pos"].config(text=f"{output_deg:.1f}")
            self.telem_labels["State"].config(text=state_name)

            errs = ax.error | ax.motor.error | ax.encoder.error
            if errs:
                self.telem_labels["Status"].config(text=f"ERR:{errs}", foreground="red")
            else:
                self.telem_labels["Status"].config(text="OK", foreground="green")
        except Exception:
            self.telem_labels["Status"].config(text="COMM ERR", foreground="red")

        self.root.after(POLL_RATE_MS, self._poll)

    # --- Calibration ---
    def calibrate(self):
        if not self.connected:
            return
        self.log("Calibrating... motor will beep then spin slowly.")
        self.btn_calibrate.config(state="disabled")

        def do_cal():
            try:
                self.odrv.axis0.requested_state = 3
                while self.odrv.axis0.current_state != 1:
                    time.sleep(0.5)
                errs = self.odrv.axis0.error | self.odrv.axis0.motor.error | self.odrv.axis0.encoder.error
                R = self.odrv.axis0.motor.config.phase_resistance * 1000
                L = self.odrv.axis0.motor.config.phase_inductance * 1e6
                if errs:
                    self.root.after(0, lambda: self.log(f"Calibration FAILED. Errors present. R={R:.1f}mOhm L={L:.1f}uH"))
                else:
                    self.root.after(0, lambda: self.log(f"Calibration OK. R={R:.1f}mOhm L={L:.1f}uH. Ready for closed loop."))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Calibration error: {e}"))
            finally:
                self.root.after(0, lambda: self.btn_calibrate.config(state="normal"))

        threading.Thread(target=do_cal, daemon=True).start()

    # --- Control State ---
    def enter_closed_loop(self):
        if not self.connected:
            return
        try:
            ax = self.odrv.axis0
            ax.controller.input_vel = 0
            ax.controller.input_torque = 0
            ax.controller.config.control_mode = 2  # velocity
            ax.controller.config.input_mode = 1     # passthrough
            self.vel_slider.set(0)
            self.torque_slider.set(0)
            self.mode_var.set("velocity")
            self.on_mode_change()

            ax.requested_state = 8
            time.sleep(0.3)
            if ax.current_state == 8:
                self.in_closed_loop = True
                self.log("Closed loop active. Motor holding position.")
            else:
                self.log(f"Failed to enter closed loop. State: {ax.current_state}")
        except Exception as e:
            self.log(f"Error: {e}")

    def go_idle(self):
        if not self.connected:
            return
        try:
            self.odrv.axis0.controller.input_vel = 0
            self.odrv.axis0.controller.input_torque = 0
            self.odrv.axis0.requested_state = 1
            self.in_closed_loop = False
            self.vel_slider.set(0)
            self.torque_slider.set(0)
            self.log("IDLE — motor off, spins freely.")
        except Exception as e:
            self.log(f"Error going idle: {e}")

    def estop(self):
        try:
            if self.odrv:
                self.odrv.axis0.controller.input_vel = 0
                self.odrv.axis0.controller.input_torque = 0
                self.odrv.axis0.requested_state = 1
                self.in_closed_loop = False
                self.vel_slider.set(0)
                self.torque_slider.set(0)
                self.log("E-STOP — motor off.")
        except Exception:
            self.log("E-STOP — comm error, kill DC power manually!")

    # --- Mode switching ---
    def on_mode_change(self):
        mode = self.mode_var.get()
        self.vel_frame.pack_forget()
        self.pos_frame.pack_forget()
        self.torque_frame.pack_forget()

        if mode == "velocity":
            self.vel_frame.pack(fill="x", pady=3)
            if self.connected and self.in_closed_loop:
                self.odrv.axis0.controller.input_vel = 0
                self.vel_slider.set(0)
                self.odrv.axis0.controller.config.control_mode = 2
                self.odrv.axis0.controller.config.input_mode = 1  # passthrough
        elif mode == "position":
            self.pos_frame.pack(fill="x", pady=3)
            if self.connected and self.in_closed_loop:
                self.odrv.axis0.controller.config.control_mode = 3
                self.odrv.axis0.controller.config.input_mode = 5  # trap trajectory
                # Update trap traj speed
                self.odrv.axis0.trap_traj.config.vel_limit = self.move_speed_motor_tps()
        elif mode == "torque":
            self.torque_frame.pack(fill="x", pady=3)
            if self.connected and self.in_closed_loop:
                self.odrv.axis0.controller.input_torque = 0
                self.torque_slider.set(0)
                self.odrv.axis0.controller.config.control_mode = 1
                self.odrv.axis0.controller.config.input_mode = 1  # passthrough
        self.log(f"Mode: {mode}")

    # --- Command handlers ---
    def on_vel_change(self, val):
        if not self.connected or not self.in_closed_loop:
            return
        try:
            output_rpm = float(val)
            motor_vel = output_rpm * self.ratio() / 60.0
            motor_vel = max(-ABS_MAX_MOTOR_VEL, min(ABS_MAX_MOTOR_VEL, motor_vel))
            self.odrv.axis0.controller.input_vel = motor_vel
        except Exception:
            pass

    def on_torque_change(self, val):
        if not self.connected or not self.in_closed_loop:
            return
        try:
            output_torque = float(val)
            motor_torque = output_torque / self.ratio()
            max_motor_torque = KT * self.current_limit()
            motor_torque = max(-max_motor_torque, min(max_motor_torque, motor_torque))
            self.odrv.axis0.controller.input_torque = motor_torque
        except Exception:
            pass

    def go_to_position(self):
        if not self.connected or not self.in_closed_loop:
            self.log("Enter closed loop first.")
            return
        try:
            output_deg = float(self.pos_entry.get())
            r = self.ratio()
            motor_turns = output_deg * r / 360.0
            # Ensure trap traj mode and speed
            self.odrv.axis0.controller.config.control_mode = 3
            self.odrv.axis0.controller.config.input_mode = 5  # trap trajectory
            self.odrv.axis0.trap_traj.config.vel_limit = self.move_speed_motor_tps()
            self.odrv.axis0.controller.input_pos = motor_turns
            move_rpm = float(self.move_speed_var.get())
            self.log(f"Moving to {output_deg} deg at {move_rpm:.0f} RPM ({motor_turns:.2f} motor turns)")
        except ValueError:
            self.log("Invalid position value.")

    def on_close(self):
        self.polling = False
        try:
            if self.odrv:
                self.odrv.axis0.controller.input_vel = 0
                self.odrv.axis0.controller.input_torque = 0
                self.odrv.axis0.requested_state = 1
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(950, 550)
    app = ODriveControlPanel(root)
    root.mainloop()
