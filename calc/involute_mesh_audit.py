"""
Numerical mesh audit for the cq_gears involute planetary generator.

This script works directly on sampled 2D tooth outlines. It estimates:
- overlap area between meshing profiles using rasterized point-in-polygon tests
- approximate boundary gap using a downsampled nearest-point search
- phase offsets that minimize overlap for sun/planet and planet/ring pairs

The goal is to catch indexing and static-meshing issues before printing.
"""

from __future__ import annotations

import importlib.util
import math
import os
from dataclasses import dataclass

import numpy as np
from matplotlib.path import Path


WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GENERATOR_PATH = os.path.join(WORKSPACE_ROOT, "pygeartrain", "generate_step_aaron_cq_gears.py")
REPORT_PATH = os.path.join(
    WORKSPACE_ROOT,
    "pygeartrain",
    "docs",
    "design_log",
    "2026-04-17_involute-mesh-audit.md",
)


RASTER_STEP_MM = 0.08
BOUNDARY_STRIDE = 24


@dataclass
class PairMetrics:
    overlap_area_mm2: float
    min_gap_mm: float


def load_generator():
    spec = importlib.util.spec_from_file_location("involute_generator", GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def poly_metrics(poly_a_xy: np.ndarray, poly_b_xy: np.ndarray) -> PairMetrics:
    path_a = Path(poly_a_xy)
    path_b = Path(poly_b_xy)

    min_x = max(poly_a_xy[:, 0].min(), poly_b_xy[:, 0].min())
    max_x = min(poly_a_xy[:, 0].max(), poly_b_xy[:, 0].max())
    min_y = max(poly_a_xy[:, 1].min(), poly_b_xy[:, 1].min())
    max_y = min(poly_a_xy[:, 1].max(), poly_b_xy[:, 1].max())

    overlap_area = 0.0
    if max_x > min_x and max_y > min_y:
        xs = np.arange(min_x, max_x + RASTER_STEP_MM, RASTER_STEP_MM)
        ys = np.arange(min_y, max_y + RASTER_STEP_MM, RASTER_STEP_MM)
        grid = np.stack(np.meshgrid(xs, ys), axis=-1).reshape(-1, 2)
        inside = path_a.contains_points(grid) & path_b.contains_points(grid)
        overlap_area = inside.sum() * (RASTER_STEP_MM ** 2)

    a = poly_a_xy[::BOUNDARY_STRIDE]
    b = poly_b_xy[::BOUNDARY_STRIDE]
    diff = a[:, None, :] - b[None, :, :]
    dist2 = np.sum(diff * diff, axis=2)
    min_gap = float(np.sqrt(dist2.min()))
    return PairMetrics(overlap_area_mm2=overlap_area, min_gap_mm=min_gap)


def transform_pair(module, gearset, sun_phase_deg: float, planet_phase_deg: float, ring_phase_deg: float):
    sun = module.rotate_xy(gearset.sun.gear_points(), math.radians(sun_phase_deg))
    ring = module.rotate_xy(gearset.ring.gear_points(), math.radians(ring_phase_deg))

    planet = module.rotate_xy(gearset.planet.gear_points(), math.radians(planet_phase_deg))
    planet = module.translate_xy(planet, gearset.orbit_r, 0.0)
    planet = module.rotate_xy(planet, math.radians(module.PLANET_0_ANGLE_DEG))
    return sun[:, :2], planet[:, :2], ring[:, :2]


def search_pair_offsets(module, gearset):
    sun_span_deg = 360.0 / gearset.sun.z
    planet_span_deg = 360.0 / gearset.planet.z
    ring_span_deg = 360.0 / gearset.ring.z

    best_sp = None
    for sun_deg in np.linspace(0.0, sun_span_deg, 13):
        for planet_deg in np.linspace(0.0, planet_span_deg, 19):
            sun_xy, planet_xy, _ = transform_pair(module, gearset, float(sun_deg), float(planet_deg), 0.0)
            metrics = poly_metrics(sun_xy, planet_xy)
            score = (metrics.overlap_area_mm2, abs(metrics.min_gap_mm - module.CLEARANCE_MM))
            if best_sp is None or score < best_sp["score"]:
                best_sp = {
                    "score": score,
                    "sun_deg": float(sun_deg),
                    "planet_deg": float(planet_deg),
                    "metrics": metrics,
                }

    best_pr = None
    for ring_deg in np.linspace(0.0, ring_span_deg, 13):
        sun_xy, planet_xy, ring_xy = transform_pair(
            module,
            gearset,
            best_sp["sun_deg"],
            best_sp["planet_deg"],
            float(ring_deg),
        )
        metrics = poly_metrics(planet_xy, ring_xy)
        score = (metrics.overlap_area_mm2, abs(metrics.min_gap_mm - module.CLEARANCE_MM))
        if best_pr is None or score < best_pr["score"]:
            best_pr = {
                "score": score,
                "ring_deg": float(ring_deg),
                "metrics": metrics,
            }

    return best_sp, best_pr


def current_metrics(module, gearset):
    sun_deg, planet_deg, ring_deg = module.static_phase_offsets_deg(gearset)
    sun_xy, planet_xy, ring_xy = transform_pair(module, gearset, sun_deg, planet_deg, ring_deg)
    return (
        PairMetrics(*poly_metrics(sun_xy, planet_xy).__dict__.values()),
        PairMetrics(*poly_metrics(planet_xy, ring_xy).__dict__.values()),
        sun_deg,
        planet_deg,
        ring_deg,
    )


def build_report() -> str:
    module = load_generator()
    gearset = module.make_gearset()

    current_sp, current_pr, sun_deg, planet_deg, ring_deg = current_metrics(module, gearset)
    best_sp, best_pr = search_pair_offsets(module, gearset)

    lines = [
        "# 2026-04-17 Involute Mesh Audit",
        "",
        "## Current Generator State",
        "",
        f"- Family: `R{gearset.ring.z} / P{gearset.planet.z} / S{gearset.sun.z}`",
        f"- Pressure angle: `{math.degrees(gearset.sun.a0):.1f} deg`",
        f"- Module: `{gearset.sun.m:.4f} mm`",
        f"- Current static phases (deg): sun `{sun_deg:.4f}`, planet `{planet_deg:.4f}`, ring `{ring_deg:.4f}`",
        "",
        "## Current Pair Metrics",
        "",
        f"- Sun-planet overlap area estimate: `{current_sp.overlap_area_mm2:.4f} mm^2`",
        f"- Sun-planet min boundary gap estimate: `{current_sp.min_gap_mm:.4f} mm`",
        f"- Planet-ring overlap area estimate: `{current_pr.overlap_area_mm2:.4f} mm^2`",
        f"- Planet-ring min boundary gap estimate: `{current_pr.min_gap_mm:.4f} mm`",
        "",
        "## Best Offsets From 2D Search",
        "",
        f"- Sun-planet best phase pair (deg): sun `{best_sp['sun_deg']:.4f}`, planet `{best_sp['planet_deg']:.4f}`",
        f"- Sun-planet best overlap area estimate: `{best_sp['metrics'].overlap_area_mm2:.4f} mm^2`",
        f"- Sun-planet best min gap estimate: `{best_sp['metrics'].min_gap_mm:.4f} mm`",
        f"- Planet-ring best ring phase (deg): ring `{best_pr['ring_deg']:.4f}`",
        f"- Planet-ring best overlap area estimate: `{best_pr['metrics'].overlap_area_mm2:.4f} mm^2`",
        f"- Planet-ring best min gap estimate: `{best_pr['metrics'].min_gap_mm:.4f} mm`",
        "",
        "## Notes",
        "",
        "- This is a sampled 2D audit, not an analytic gear solver.",
        "- It is still useful for catching obvious indexing errors and static overlap before printing.",
        "- If overlap area is near zero and boundary gap is small positive, the static mesh is at least numerically plausible.",
    ]
    return "\n".join(lines) + "\n"


def main():
    report = build_report()
    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        file.write(report)
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
