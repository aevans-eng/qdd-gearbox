from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def as_float(row: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, "") or default)
    except ValueError:
        return default


def read_motor_log(path: Path) -> list[dict[str, float]]:
    if not path.exists():
        return []
    rows: list[dict[str, float]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip() or not line.lstrip()[0].isdigit():
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        try:
            iq = float(parts[3])
            vel = float(parts[2])
            torque = float(parts[1])
            rows.append(
                {
                    "t_s": float(parts[0]),
                    "torque_nm": torque,
                    "vel_tps": vel,
                    "iq_a": iq,
                    "fet_c": float(parts[4]) if len(parts) >= 5 else float("nan"),
                    "vbus_v": float(parts[5]) if len(parts) >= 6 else float("nan"),
                    "ibus_a": float(parts[6]) if len(parts) >= 7 else float("nan"),
                    "dc_w": float(parts[7]) if len(parts) >= 8 else float("nan"),
                    "motor_mech_w": float(parts[8]) if len(parts) >= 9 else (0.04 * iq) * (vel * 2.0 * 3.141592653589793),
                    "cc_ibus_a": float(parts[9]) if len(parts) >= 10 else float("nan"),
                    "id_a": float(parts[10]) if len(parts) >= 11 else float("nan"),
                    "iq_setpoint_a": float(parts[11]) if len(parts) >= 12 else float("nan"),
                    "phase_b_a": float(parts[13]) if len(parts) >= 14 else float("nan"),
                    "phase_c_a": float(parts[14]) if len(parts) >= 15 else float("nan"),
                }
            )
        except ValueError:
            continue
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot a synced QDD dyno run folder.")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    run_dir = args.run_dir
    output = args.output or run_dir / "synced-summary.png"

    temp_rows = read_csv(run_dir / "temperature.csv")
    dyno_rows = read_csv(run_dir / "dyno.csv")
    motor_rows = read_motor_log(run_dir / "motor.log")

    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=False)
    fig.suptitle(run_dir.name)

    ax = axes[0]
    if temp_rows:
        t = [as_float(row, "time_ms") / 1000.0 for row in temp_rows]
        temp = [as_float(row, "temp_c") for row in temp_rows]
        ax.plot(t, temp, label="Arduino temp C")
    if motor_rows:
        ax.plot([row["t_s"] for row in motor_rows], [row["fet_c"] for row in motor_rows], label="FET temp C")
    ax.axhline(50, color="tab:red", linestyle="--", linewidth=1, label="motor limit")
    ax.axhline(70, color="tab:purple", linestyle="--", linewidth=1, label="FET limit")
    ax.set_ylabel("Temp C")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.25)

    ax = axes[1]
    if motor_rows:
        ax.plot([row["t_s"] for row in motor_rows], [row["torque_nm"] for row in motor_rows], label="cmd torque Nm")
        ax.plot([row["t_s"] for row in motor_rows], [row["iq_a"] for row in motor_rows], label="Iq A")
        if any(row["cc_ibus_a"] == row["cc_ibus_a"] for row in motor_rows):
            ax.plot([row["t_s"] for row in motor_rows], [row["cc_ibus_a"] for row in motor_rows], label="current control Ibus A")
        if any(row["dc_w"] == row["dc_w"] for row in motor_rows):
            ax.plot([row["t_s"] for row in motor_rows], [row["dc_w"] for row in motor_rows], label="DC input W")
        ax.plot([row["t_s"] for row in motor_rows], [row["motor_mech_w"] for row in motor_rows], label="est motor mech W")
    ax.set_ylabel("Motor")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.25)

    ax = axes[2]
    if dyno_rows:
        t = [as_float(row, "elapsed_s") for row in dyno_rows]
        ax.plot(t, [as_float(row, "rpm") for row in dyno_rows], label="trainer rpm")
        ax.plot(t, [as_float(row, "power_w") for row in dyno_rows], label="trainer power W")
        ax.plot(t, [as_float(row, "inst_torque_nm") for row in dyno_rows], label="trainer torque Nm")
    ax.set_xlabel("Seconds")
    ax.set_ylabel("Trainer")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.25)

    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=150)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
