from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean


def load_manifest(run_dir: Path) -> dict:
    with (run_dir / "manifest.json").open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def load_dyno_rows(run_dir: Path) -> list[dict[str, float]]:
    path = run_dir / "dyno.csv"
    rows: list[dict[str, float]] = []
    with path.open("r", newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            try:
                rpm = float(row.get("rpm", 0) or 0)
                power = float(row.get("power_w", 0) or 0)
                torque = float(row.get("inst_torque_nm", 0) or 0)
                elapsed = float(row.get("elapsed_s", 0) or 0)
            except ValueError:
                continue
            if elapsed >= 5.0 and rpm > 1.0 and power > 0.0:
                rows.append({"elapsed_s": elapsed, "rpm": rpm, "power_w": power, "inst_torque_nm": torque})
    return rows


def summarize(rows: list[dict[str, float]]) -> dict[str, float | int | None]:
    if not rows:
        return {
            "samples": 0,
            "avg_rpm": None,
            "avg_power_w": None,
            "max_power_w": None,
            "avg_inst_torque_nm": None,
            "max_inst_torque_nm": None,
        }
    return {
        "samples": len(rows),
        "avg_rpm": round(mean(row["rpm"] for row in rows), 3),
        "avg_power_w": round(mean(row["power_w"] for row in rows), 3),
        "max_power_w": round(max(row["power_w"] for row in rows), 3),
        "avg_inst_torque_nm": round(mean(row["inst_torque_nm"] for row in rows), 3),
        "max_inst_torque_nm": round(max(row["inst_torque_nm"] for row in rows), 3),
    }


def matched_efficiency(
    bare_rows: list[dict[str, float]],
    gearbox_rows: list[dict[str, float]],
    rpm_tolerance: float,
) -> dict[str, float | int | None]:
    pairs: list[float] = []
    for gear in gearbox_rows:
        candidates = [
            bare for bare in bare_rows
            if abs(bare["rpm"] - gear["rpm"]) <= rpm_tolerance and bare["power_w"] > 0
        ]
        if not candidates:
            continue
        nearest = min(candidates, key=lambda row: abs(row["rpm"] - gear["rpm"]))
        pairs.append(gear["power_w"] / nearest["power_w"])

    if not pairs:
        return {"matched_pairs": 0, "avg_efficiency": None, "min_efficiency": None, "max_efficiency": None}
    return {
        "matched_pairs": len(pairs),
        "avg_efficiency": round(mean(pairs), 4),
        "min_efficiency": round(min(pairs), 4),
        "max_efficiency": round(max(pairs), 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare bare motor and gearbox dyno runs.")
    parser.add_argument("--bare-run", type=Path, required=True, help="Synced bare-motor run directory.")
    parser.add_argument("--gearbox-run", type=Path, required=True, help="Synced gearbox-installed run directory.")
    parser.add_argument("--rpm-tolerance", type=float, default=3.0)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    bare_manifest = load_manifest(args.bare_run)
    gearbox_manifest = load_manifest(args.gearbox_run)
    bare_rows = load_dyno_rows(args.bare_run)
    gearbox_rows = load_dyno_rows(args.gearbox_run)

    result = {
        "bare_run": str(args.bare_run),
        "gearbox_run": str(args.gearbox_run),
        "rpm_tolerance": args.rpm_tolerance,
        "bare_label": bare_manifest.get("label"),
        "gearbox_label": gearbox_manifest.get("label"),
        "bare_summary": summarize(bare_rows),
        "gearbox_summary": summarize(gearbox_rows),
        "matched_speed_efficiency": matched_efficiency(bare_rows, gearbox_rows, args.rpm_tolerance),
        "passes_90pct_soft_target": None,
    }

    avg_eff = result["matched_speed_efficiency"]["avg_efficiency"]
    if avg_eff is not None:
        result["passes_90pct_soft_target"] = avg_eff >= 0.90

    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
