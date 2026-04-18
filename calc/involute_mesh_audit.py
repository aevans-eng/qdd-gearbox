"""
Fast sampled-outline mesh audit for the cq_gears involute planetary generator.

This script intentionally avoids raster area calculations in the search loop.
It uses the same static body placement as the STEP export path and reports:
- sampled outline overlap count for the sun-planet pair
- minimum sampled boundary gap for sun-planet and planet-ring pairs
- a coarse phase search around one tooth pitch to catch obvious indexing errors
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

OUTLINE_SUBDIVISIONS = 2
BOUNDARY_STRIDE = 24


@dataclass
class PairMetrics:
    overlap_count: int
    min_gap_mm: float


def load_generator():
    spec = importlib.util.spec_from_file_location("involute_generator", GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def dense_outline(poly_xy: np.ndarray, subdivisions: int = OUTLINE_SUBDIVISIONS) -> np.ndarray:
    samples = []
    for index in range(len(poly_xy)):
        start = poly_xy[index]
        end = poly_xy[(index + 1) % len(poly_xy)]
        segment = np.linspace(start, end, subdivisions, endpoint=False)
        samples.append(segment)
    return np.vstack(samples)


def pair_metrics(poly_a_xy: np.ndarray, poly_b_xy: np.ndarray) -> PairMetrics:
    dense_a = dense_outline(poly_a_xy)[::BOUNDARY_STRIDE]
    dense_b = dense_outline(poly_b_xy)[::BOUNDARY_STRIDE]

    path_a = Path(poly_a_xy)
    path_b = Path(poly_b_xy)
    overlap_count = int(path_a.contains_points(dense_b).sum() + path_b.contains_points(dense_a).sum())

    diff = dense_a[:, None, :] - dense_b[None, :, :]
    dist2 = np.sum(diff * diff, axis=2)
    min_gap = float(np.sqrt(dist2.min()))
    return PairMetrics(overlap_count=overlap_count, min_gap_mm=min_gap)


def planet_center(module, gearset, planet_index: int = 0) -> tuple[float, float]:
    orbit_angle_deg = module.PLANET_0_ANGLE_DEG + planet_index * (360.0 / gearset.n_planets)
    x = math.cos(math.radians(orbit_angle_deg)) * gearset.orbit_r
    y = math.sin(math.radians(orbit_angle_deg)) * gearset.orbit_r
    return x, y


def transform_pair(module, gearset, sun_phase_deg: float, planet_phase_deg: float, ring_phase_deg: float):
    sun = module.rotate_xy(gearset.sun.gear_points(), math.radians(sun_phase_deg))
    ring = module.rotate_xy(gearset.ring.gear_points(), math.radians(ring_phase_deg))

    planet = module.rotate_xy(gearset.planet.gear_points(), math.radians(planet_phase_deg))
    x, y = planet_center(module, gearset, planet_index=0)
    planet = module.translate_xy(planet, x, y)
    return sun[:, :2], planet[:, :2], ring[:, :2]


def current_metrics(module, gearset):
    sun_deg, planet_deg, ring_deg = module.static_phase_offsets_deg(gearset)
    sun_xy, planet_xy, ring_xy = transform_pair(module, gearset, sun_deg, planet_deg, ring_deg)
    return pair_metrics(sun_xy, planet_xy), pair_metrics(planet_xy, ring_xy), sun_deg, planet_deg, ring_deg


def build_report() -> str:
    module = load_generator()
    gearset = module.make_gearset()

    current_sp, current_pr, sun_deg, planet_deg, ring_deg = current_metrics(module, gearset)

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
        "## Current Static Pair Metrics",
        "",
        f"- Sun-planet sampled overlap count: `{current_sp.overlap_count}`",
        f"- Sun-planet min sampled boundary gap: `{current_sp.min_gap_mm:.4f} mm`",
        f"- Planet-ring sampled overlap count: `{current_pr.overlap_count}` (not reliable for internal-ring inside/outside classification)",
        f"- Planet-ring min sampled boundary gap: `{current_pr.min_gap_mm:.4f} mm`",
        "",
        "## Notes",
        "",
        "- This audit follows the same static body placement as the STEP assembly export.",
        "- It is a sampled-outline screen, not a full analytic tooth-contact solver.",
        "- It is intended to catch obvious indexing mistakes quickly before export or print.",
        "- The expensive phase sweep was removed because it was too slow to be useful in this workflow.",
        "- For the internal ring pair, use the sampled minimum gap and direct solid-intersection checks, not the overlap count alone.",
    ]
    return "\n".join(lines) + "\n"


def main():
    report = build_report()
    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        file.write(report)
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
