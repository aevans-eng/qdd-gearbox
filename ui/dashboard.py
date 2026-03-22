"""
QDD Gearbox Design Dashboard
=============================
Tkinter UI that takes gear parameters as input, runs all calculators,
and displays results with matplotlib plots.

Skills demonstrated: UI development, data visualization
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
import io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from calc.gear_geometry import design_planetary_set, compute_contact_ratio, tooth_profile
from calc.tooth_stress import analyze_stresses
from calc.bearing_life import analyze_bearings, gear_forces_to_bearing_loads
from calc.thermal import (
    motor_losses, heat_generation_vector, solve_steady_state,
    solve_transient, NODE_NAMES, WINDING, STATOR, HOUSING, GEARBOX, AMBIENT,
)
from calc.utils.data import PLA_PLUS, NYLON_PA6, PlanetarySet
from calc.utils.constants import (
    PRESSURE_ANGLE_DEG, NUM_PLANETS, OUTPUT_PEAK_TORQUE_NM,
    OUTPUT_CONT_TORQUE_NM, MOTOR_MAX_SPEED_RPM, GEAR_RATIO,
    WINDING_TEMP_LIMIT_C, HOUSING_TEMP_LIMIT_C,
)


class QDDDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("QDD Gearbox Design Dashboard")
        self.root.geometry("1200x800")

        self.gear_set = None
        self.results = {}

        self._build_ui()

    def _build_ui(self):
        # Main layout: left panel (inputs) + right panel (plots/results)
        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel — inputs
        left = ttk.Frame(main, width=300)
        main.add(left, weight=1)

        # Right panel — notebook with tabs
        right = ttk.Frame(main)
        main.add(right, weight=3)

        self._build_input_panel(left)
        self._build_output_panel(right)

    def _build_input_panel(self, parent):
        ttk.Label(parent, text="Gear Parameters", font=("", 12, "bold")).pack(pady=(10, 5))

        frame = ttk.LabelFrame(parent, text="Geometry")
        frame.pack(fill=tk.X, padx=5, pady=5)

        self.vars = {}
        params = [
            ("Module (mm):", "module", "1.5"),
            ("Sun Teeth:", "sun_teeth", "12"),
            ("Pressure Angle (deg):", "pressure_angle", "20"),
            ("Face Width (mm):", "face_width", "10"),
            ("Num Planets:", "num_planets", "3"),
        ]

        for i, (label, key, default) in enumerate(params):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            var = tk.StringVar(value=default)
            ttk.Entry(frame, textvariable=var, width=10).grid(row=i, column=1, padx=5, pady=2)
            self.vars[key] = var

        # Material selection
        mat_frame = ttk.LabelFrame(parent, text="Material")
        mat_frame.pack(fill=tk.X, padx=5, pady=5)
        self.material_var = tk.StringVar(value="PLA+")
        for mat in ["PLA+", "Nylon PA6"]:
            ttk.Radiobutton(mat_frame, text=mat, variable=self.material_var, value=mat).pack(anchor="w", padx=5)

        # Run button
        ttk.Button(parent, text="Run All Calculators", command=self._run_all).pack(pady=15, padx=5, fill=tk.X)

        # Export button
        ttk.Button(parent, text="Export Report", command=self._export_report).pack(pady=5, padx=5, fill=tk.X)

        # Status
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(parent, textvariable=self.status_var, foreground="gray").pack(pady=10)

    def _build_output_panel(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Summary tab
        self.summary_text = tk.Text(parent, wrap=tk.WORD, font=("Consolas", 9))
        self.notebook.add(self.summary_text, text="Summary")

        # Gear profile tab
        self.fig_gear = Figure(figsize=(6, 5), dpi=100)
        self.canvas_gear = FigureCanvasTkAgg(self.fig_gear, parent)
        self.notebook.add(self.canvas_gear.get_tk_widget(), text="Gear Profile")

        # Thermal tab
        self.fig_thermal = Figure(figsize=(6, 5), dpi=100)
        self.canvas_thermal = FigureCanvasTkAgg(self.fig_thermal, parent)
        self.notebook.add(self.canvas_thermal.get_tk_widget(), text="Thermal")

        # Stress tab
        self.fig_stress = Figure(figsize=(6, 5), dpi=100)
        self.canvas_stress = FigureCanvasTkAgg(self.fig_stress, parent)
        self.notebook.add(self.canvas_stress.get_tk_widget(), text="Stress")

    def _get_params(self):
        try:
            return {
                "module": float(self.vars["module"].get()),
                "sun_teeth": int(self.vars["sun_teeth"].get()),
                "pressure_angle": float(self.vars["pressure_angle"].get()),
                "face_width": float(self.vars["face_width"].get()),
                "num_planets": int(self.vars["num_planets"].get()),
            }
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")
            return None

    def _get_material(self):
        return PLA_PLUS if self.material_var.get() == "PLA+" else NYLON_PA6

    def _run_all(self):
        params = self._get_params()
        if not params:
            return

        self.status_var.set("Running calculators...")
        self.root.update()

        try:
            # Design gear set
            self.gear_set = design_planetary_set(
                params["module"], params["sun_teeth"],
                params["pressure_angle"], params["num_planets"],
                params["face_width"],
            )
            material = self._get_material()

            # Run stress analysis
            self.results["stress"] = analyze_stresses(self.gear_set, material)

            # Run thermal analysis
            losses_cont = motor_losses(OUTPUT_CONT_TORQUE_NM, MOTOR_MAX_SPEED_RPM / GEAR_RATIO)
            losses_peak = motor_losses(OUTPUT_PEAK_TORQUE_NM, MOTOR_MAX_SPEED_RPM / GEAR_RATIO)
            Q_cont = heat_generation_vector(losses_cont)
            Q_peak = heat_generation_vector(losses_peak)
            self.results["T_steady"] = solve_steady_state(Q_cont)
            time, T_hist = solve_transient(Q_peak, 300.0, dt=1.0)
            self.results["thermal_time"] = time
            self.results["thermal_hist"] = T_hist
            self.results["losses_cont"] = losses_cont
            self.results["losses_peak"] = losses_peak

            # Bearing forces
            self.results["forces_cont"] = gear_forces_to_bearing_loads(
                self.gear_set, OUTPUT_CONT_TORQUE_NM)

            # Contact ratio
            self.results["cr_sp"] = compute_contact_ratio(
                params["module"], params["sun_teeth"],
                self.gear_set.planet.num_teeth, params["pressure_angle"])

            # Update displays
            self._update_summary()
            self._plot_gear_profile()
            self._plot_thermal()
            self._plot_stress()

            self.status_var.set("Done")

        except Exception as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Calculation Error", str(e))

    def _update_summary(self):
        self.summary_text.delete("1.0", tk.END)
        gs = self.gear_set
        res = self.results["stress"]
        mat = self._get_material()

        lines = []
        lines.append("=" * 55)
        lines.append("  QDD GEARBOX DESIGN SUMMARY")
        lines.append("=" * 55)
        lines.append("")
        lines.append(f"  Gear Set: m={gs.sun.module_mm} mm, Zs={gs.sun.num_teeth}, "
                     f"Zp={gs.planet.num_teeth}, Zr={gs.ring_teeth}")
        lines.append(f"  Ratio: {gs.ratio:.2f}:1")
        lines.append(f"  Material: {mat.name}")
        lines.append(f"  Contact Ratio (sun-planet): {self.results['cr_sp']:.3f}")
        lines.append("")
        lines.append("--- Stress Results ---")
        lines.append(f"  Tangential Force/Planet: {res['tangential_force_n']:.1f} N")
        lines.append(f"  Bending Stress (Sun):    {res['bending_stress_sun_mpa']:.1f} MPa  "
                     f"SF={res['sf_bending_sun']:.2f}")
        lines.append(f"  Bending Stress (Planet): {res['bending_stress_planet_mpa']:.1f} MPa  "
                     f"SF={res['sf_bending_planet']:.2f}")
        lines.append(f"  Contact Stress:          {res['contact_stress_mpa']:.1f} MPa  "
                     f"SF={res['sf_contact']:.2f}")
        lines.append("")
        lines.append("--- Thermal (Steady-State, Continuous) ---")
        T_ss = self.results["T_steady"]
        for i in range(4):
            lines.append(f"  {NODE_NAMES[i]:>10s}: {T_ss[i]:.1f} C")
        lines.append("")
        lines.append("--- Bearing Forces (Continuous) ---")
        for loc, f in self.results["forces_cont"].items():
            lines.append(f"  {loc:>15s}: {f:.1f} N")

        self.summary_text.insert("1.0", "\n".join(lines))

    def _plot_gear_profile(self):
        self.fig_gear.clear()
        ax = self.fig_gear.add_subplot(111, aspect="equal")
        gs = self.gear_set

        # Plot sun gear teeth
        x, y = tooth_profile(gs.sun, num_points=80)
        num_teeth = gs.sun.num_teeth
        for i in range(num_teeth):
            angle = 2 * np.pi * i / num_teeth
            cos_a, sin_a = np.cos(angle), np.sin(angle)
            xr = x * cos_a - y * sin_a
            yr = x * sin_a + y * cos_a
            ax.plot(xr, yr, "b-", linewidth=0.8)

        # Draw pitch circle
        theta = np.linspace(0, 2 * np.pi, 100)
        r_pitch = gs.sun.pitch_diameter_mm / 2
        ax.plot(r_pitch * np.cos(theta), r_pitch * np.sin(theta), "g--", alpha=0.5, label="Pitch circle")

        ax.set_title(f"Sun Gear Profile (Z={gs.sun.num_teeth}, m={gs.sun.module_mm} mm)")
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        self.fig_gear.tight_layout()
        self.canvas_gear.draw()

    def _plot_thermal(self):
        self.fig_thermal.clear()
        ax = self.fig_thermal.add_subplot(111)

        time = self.results["thermal_time"]
        T_hist = self.results["thermal_hist"]

        colors = ["r", "orange", "b", "g"]
        for i in range(4):
            ax.plot(time, T_hist[:, i], color=colors[i], label=NODE_NAMES[i])

        ax.axhline(WINDING_TEMP_LIMIT_C, color="r", linestyle="--", alpha=0.5, label=f"Winding limit ({WINDING_TEMP_LIMIT_C} C)")
        ax.axhline(HOUSING_TEMP_LIMIT_C, color="b", linestyle="--", alpha=0.5, label=f"Housing limit ({HOUSING_TEMP_LIMIT_C} C)")

        ax.set_title("Transient Thermal Response (Peak Torque)")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Temperature (C)")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)
        self.fig_thermal.tight_layout()
        self.canvas_thermal.draw()

    def _plot_stress(self):
        self.fig_stress.clear()
        ax = self.fig_stress.add_subplot(111)
        res = self.results["stress"]
        mat = self._get_material()

        labels = ["Bending\n(Sun)", "Bending\n(Planet)", "Contact\n(Sun-Planet)"]
        stresses = [res["bending_stress_sun_mpa"], res["bending_stress_planet_mpa"],
                    res["contact_stress_mpa"]]
        sfs = [res["sf_bending_sun"], res["sf_bending_planet"], res["sf_contact"]]

        x_pos = range(len(labels))
        bars = ax.bar(x_pos, stresses, color=["steelblue", "steelblue", "coral"], alpha=0.8)
        ax.axhline(mat.yield_strength_mpa, color="red", linestyle="--",
                   label=f"Yield ({mat.yield_strength_mpa} MPa)")

        # Annotate safety factors
        for i, (bar, sf) in enumerate(zip(bars, sfs)):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f"SF={sf:.2f}", ha="center", va="bottom", fontsize=9)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels)
        ax.set_ylabel("Stress (MPa)")
        ax.set_title("Tooth Stress Analysis")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")
        self.fig_stress.tight_layout()
        self.canvas_stress.draw()

    def _export_report(self):
        if not self.gear_set:
            messagebox.showinfo("Export", "Run calculators first.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Report",
        )
        if not path:
            return

        # Capture summary text
        content = self.summary_text.get("1.0", tk.END)
        with open(path, "w") as f:
            f.write(content)

        self.status_var.set(f"Report exported to {os.path.basename(path)}")


def main():
    root = tk.Tk()
    app = QDDDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
