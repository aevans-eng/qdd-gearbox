"""Visualization for dyno capture data.

Generates a 6-panel plot: power, RPM, torque (two methods), dyno curve
(torque & power vs RPM), angular acceleration, and accumulated torque.
"""

import csv
from pathlib import Path


def load_csv(path: Path) -> list[dict]:
    """Load a dyno capture CSV into a list of dicts with proper types."""
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append({
                "elapsed_s": float(row["elapsed_s"]),
                "power_w": int(row["power_w"]),
                "acc_torque_nm": float(row["acc_torque_nm"]),
                "wheel_revs": int(row["wheel_revs"]),
                "wheel_event_time": int(row["wheel_event_time"]),
                "crank_revs": int(row["crank_revs"]),
                "crank_event_time": int(row["crank_event_time"]),
                "rpm": float(row["rpm"]),
                "omega_rad_s": float(row["omega_rad_s"]),
                "inst_torque_nm": float(row["inst_torque_nm"]),
                "torque_from_power_nm": float(row["torque_from_power_nm"]),
                "alpha_rad_s2": float(row["alpha_rad_s2"]),
            })
    return rows


def plot_dyno(
    rows: list[dict],
    title: str = "Dyno Capture",
    save_path: Path | None = None,
    show: bool = True,
):
    """Generate the 6-panel dyno plot.

    Args:
        rows: List of sample dicts (from load_csv or DynoSample.to_dict)
        title: Plot title
        save_path: If set, save PNG here
        show: If True, display interactive window
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed -- pip install matplotlib")
        return

    t = [r["elapsed_s"] for r in rows]
    power = [r["power_w"] for r in rows]
    rpm = [r["rpm"] for r in rows]
    inst_torque = [r["inst_torque_nm"] for r in rows]
    torque_pw = [r["torque_from_power_nm"] for r in rows]
    alpha = [r["alpha_rad_s2"] for r in rows]
    acc_torque = [r["acc_torque_nm"] for r in rows]
    revs = [r["wheel_revs"] for r in rows]

    fig, axes = plt.subplots(3, 2, figsize=(14, 10), constrained_layout=True)
    fig.suptitle(f"Saris H2 Dyno -- {title}", fontsize=14)

    # 1. Power vs Time
    ax = axes[0, 0]
    ax.plot(t, power, "b-", linewidth=0.8)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Power (W)")
    ax.set_title("Power vs Time")
    ax.grid(True, alpha=0.3)

    # 2. RPM vs Time
    ax = axes[0, 1]
    ax.plot(t, rpm, "r-", linewidth=0.8)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("RPM")
    ax.set_title("Flywheel RPM vs Time")
    ax.grid(True, alpha=0.3)

    # 3. Torque vs Time (both derivation methods)
    ax = axes[1, 0]
    ax.plot(t, inst_torque, "g-", linewidth=0.8, label="From acc. torque")
    ax.plot(t, torque_pw, "m--", linewidth=0.8, alpha=0.7, label="From P/w")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Torque (Nm)")
    ax.set_title("Instantaneous Torque vs Time")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 4. Dyno curve: Torque & Power vs RPM
    ax = axes[1, 1]
    rpm_vals = [rp for rp in rpm if rp > 1]
    torque_vals = [tq for tq, rp in zip(inst_torque, rpm) if rp > 1]
    if rpm_vals:
        ax.scatter(rpm_vals, torque_vals, c="green", s=8, alpha=0.6, label="Torque")
        ax2 = ax.twinx()
        power_vals = [p for p, rp in zip(power, rpm) if rp > 1]
        ax2.scatter(rpm_vals, power_vals, c="blue", s=8, alpha=0.4, label="Power")
        ax2.set_ylabel("Power (W)", color="blue")
    ax.set_xlabel("RPM")
    ax.set_ylabel("Torque (Nm)", color="green")
    ax.set_title("Torque & Power vs RPM (Dyno Curve)")
    ax.grid(True, alpha=0.3)

    # 5. Angular acceleration vs Time
    ax = axes[2, 0]
    ax.plot(t, alpha, "k-", linewidth=0.8)
    ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.5)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("alpha (rad/s^2)")
    ax.set_title("Angular Acceleration vs Time")
    ax.grid(True, alpha=0.3)

    # 6. Accumulated torque vs Wheel revs
    ax = axes[2, 1]
    ax.plot(revs, acc_torque, "c-", linewidth=0.8)
    ax.set_xlabel("Wheel Revolutions")
    ax.set_ylabel("Accumulated Torque (Nm)")
    ax.set_title("Accumulated Torque vs Revolutions")
    ax.grid(True, alpha=0.3)

    if save_path:
        fig.savefig(save_path, dpi=150)
        print(f"Plot saved to {save_path}")
    if show:
        plt.show()
