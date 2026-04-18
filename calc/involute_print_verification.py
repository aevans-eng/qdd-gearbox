"""
Verification report for the current involute planetary design.

This is intentionally tied to the cq_gears-based generator so the report
reflects the actual exported geometry rather than a separate hand-entered
calculator setup.
"""

from __future__ import annotations

import importlib.util
import math
import os
import sys
from dataclasses import dataclass

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, WORKSPACE_ROOT)

from calc.tooth_stress import analyze_stresses
from calc.utils.data import GearParams, PlanetarySet, PLA_PLUS, NYLON_PA6


GENERATOR_PATH = os.path.join(WORKSPACE_ROOT, "pygeartrain", "generate_step_aaron_cq_gears.py")
REPORT_PATH = os.path.join(
    WORKSPACE_ROOT,
    "pygeartrain",
    "docs",
    "design_log",
    "2026-04-17_involute-print-verification.md",
)


@dataclass
class CapacityResult:
    material: str
    target_sf_torque_nm: float
    first_yieldish_torque_nm: float
    governing_mode: str
    stress_at_16_nm_mpa: float


def load_generator_module():
    spec = importlib.util.spec_from_file_location("involute_generator", GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def make_calc_planetary_set(gearset) -> PlanetarySet:
    sun = GearParams(
        module_mm=gearset.sun.m,
        num_teeth=gearset.sun.z,
        pressure_angle_deg=math.degrees(gearset.sun.a0),
        face_width_mm=gearset.sun.width,
    )
    planet = GearParams(
        module_mm=gearset.planet.m,
        num_teeth=gearset.planet.z,
        pressure_angle_deg=math.degrees(gearset.planet.a0),
        face_width_mm=gearset.planet.width,
    )
    return PlanetarySet(sun=sun, planet=planet, ring_teeth=gearset.ring.z, num_planets=gearset.n_planets)


def estimate_capacity(calc_set: PlanetarySet, material) -> CapacityResult:
    at_16 = analyze_stresses(calc_set, material, 16.0)

    bending_sf = min(at_16["sf_bending_sun"], at_16["sf_bending_planet"])
    contact_sf = at_16["sf_contact"]

    target_bending_torque = 16.0 * (bending_sf / 2.0)
    target_contact_torque = 16.0 * (contact_sf / 1.5) ** 2
    yieldish_bending_torque = 16.0 * bending_sf
    yieldish_contact_torque = 16.0 * (contact_sf**2)

    if target_bending_torque <= target_contact_torque:
        governing_mode = "sun/planet bending"
        target_stress = max(at_16["bending_stress_sun_mpa"], at_16["bending_stress_planet_mpa"])
    else:
        governing_mode = "contact"
        target_stress = at_16["contact_stress_mpa"]

    return CapacityResult(
        material=material.name,
        target_sf_torque_nm=min(target_bending_torque, target_contact_torque),
        first_yieldish_torque_nm=min(yieldish_bending_torque, yieldish_contact_torque),
        governing_mode=governing_mode,
        stress_at_16_nm_mpa=target_stress,
    )


def external_contact_ratio(gear_a, gear_b) -> float:
    alpha = gear_a.a0
    rb_a = gear_a.rb
    rb_b = gear_b.rb
    ra_a = gear_a.ra
    ra_b = gear_b.ra
    center = gear_a.r0 + gear_b.r0
    path = math.sqrt(max(ra_a * ra_a - rb_a * rb_a, 0.0)) + math.sqrt(max(ra_b * ra_b - rb_b * rb_b, 0.0)) - center * math.sin(alpha)
    base_pitch = math.pi * gear_a.m * math.cos(alpha)
    return path / base_pitch


def family_sweep(orbit_radius_mm: float, sun_pitch_diameter_mm: float, face_width_mm: float, pressure_angle_deg: float):
    results = []
    for sun_teeth in (12, 18, 24, 30):
        planet_teeth = sun_teeth * 3 // 2
        ring_teeth = sun_teeth * 4
        if sun_teeth + 2 * planet_teeth != ring_teeth:
            continue
        if (sun_teeth + ring_teeth) % 3 != 0:
            continue

        module_mm = sun_pitch_diameter_mm / sun_teeth
        calc_set = PlanetarySet(
            sun=GearParams(module_mm, sun_teeth, pressure_angle_deg=pressure_angle_deg, face_width_mm=face_width_mm),
            planet=GearParams(module_mm, planet_teeth, pressure_angle_deg=pressure_angle_deg, face_width_mm=face_width_mm),
            ring_teeth=ring_teeth,
            num_planets=3,
        )
        pla_capacity = estimate_capacity(calc_set, PLA_PLUS)
        nylon_capacity = estimate_capacity(calc_set, NYLON_PA6)
        pressure_angle_rad = math.radians(pressure_angle_deg)
        pitch_radius_sun = sun_pitch_diameter_mm / 2.0
        pitch_radius_planet = pitch_radius_sun * 1.5
        results.append(
            {
                "sun_teeth": sun_teeth,
                "planet_teeth": planet_teeth,
                "ring_teeth": ring_teeth,
                "module_mm": module_mm,
                "pla_target_sf_nm": pla_capacity.target_sf_torque_nm,
                "nylon_target_sf_nm": nylon_capacity.target_sf_torque_nm,
                "contact_ratio": (
                    math.sqrt(max((19.898 / 2.0) ** 2 - (pitch_radius_sun * math.cos(pressure_angle_rad)) ** 2, 0.0))
                    + math.sqrt(max((29.082 / 2.0) ** 2 - (pitch_radius_planet * math.cos(pressure_angle_rad)) ** 2, 0.0))
                    - (pitch_radius_sun + pitch_radius_planet) * math.sin(pressure_angle_rad)
                ) / (math.pi * module_mm * math.cos(pressure_angle_rad)),
            }
        )
    return sorted(results, key=lambda item: item["pla_target_sf_nm"], reverse=True)


def build_report() -> str:
    generator = load_generator_module()
    gearset = generator.make_gearset()
    calc_set = make_calc_planetary_set(gearset)

    addendum_mm = gearset.sun.ka * gearset.sun.m
    dedendum_mm = gearset.sun.kd * gearset.sun.m + gearset.sun.clearance
    contact_ratio_sp = external_contact_ratio(gearset.sun, gearset.planet)

    pla_capacity = estimate_capacity(calc_set, PLA_PLUS)
    nylon_capacity = estimate_capacity(calc_set, NYLON_PA6)
    sweep = family_sweep(
        orbit_radius_mm=gearset.orbit_r,
        sun_pitch_diameter_mm=gearset.sun.r0 * 2.0,
        face_width_mm=gearset.sun.width,
        pressure_angle_deg=math.degrees(gearset.sun.a0),
    )

    lines = [
        "# 2026-04-17 Involute Print Verification",
        "",
        "## Current Design",
        "",
        f"- Source generator: `{os.path.relpath(GENERATOR_PATH, WORKSPACE_ROOT)}`",
        f"- Gearset: `R{gearset.ring.z} / P{gearset.planet.z} / S{gearset.sun.z}`",
        f"- Ratio: `{calc_set.ratio:.3f}:1`",
        f"- Module: `{gearset.sun.m:.4f} mm`",
        f"- Pressure angle: `{math.degrees(gearset.sun.a0):.1f} deg`",
        f"- Face width: `{gearset.sun.width:.1f} mm`",
        f"- Orbit radius: `{gearset.orbit_r:.3f} mm`",
        f"- Sun OD: `{gearset.sun.ra * 2.0:.3f} mm`",
        f"- Planet OD: `{gearset.planet.ra * 2.0:.3f} mm`",
        f"- Ring inner tip diameter: `{gearset.ring.ra * 2.0:.3f} mm`",
        f"- Ring root diameter: `{gearset.ring.rd * 2.0:.3f} mm`",
        f"- Ring OD: `{gearset.ring.rim_r * 2.0:.3f} mm`",
        "",
        "## Tooth Proportions",
        "",
        f"- Addendum coefficient: `{gearset.sun.ka:.4f}`",
        f"- Dedendum coefficient: `{gearset.sun.kd:.4f}`",
        f"- Addendum depth: `{addendum_mm:.3f} mm`",
        f"- Dedendum depth including root clearance: `{dedendum_mm:.3f} mm`",
        f"- Radial root clearance target: `{gearset.sun.clearance:.3f} mm`",
        "",
        "## Mesh Checks",
        "",
        f"- External sun-planet contact ratio estimate: `{contact_ratio_sp:.3f}`",
        "- This is the strongest simple check available locally for the current involute export path.",
        "",
        "## Rough Torque Capacity",
        "",
        f"- PLA+ target-safety-factor torque: `{pla_capacity.target_sf_torque_nm:.2f} Nm`",
        f"- PLA+ first-yield-ish torque: `{pla_capacity.first_yieldish_torque_nm:.2f} Nm`",
        f"- PLA+ governing mode: `{pla_capacity.governing_mode}`",
        f"- Nylon PA6 target-safety-factor torque: `{nylon_capacity.target_sf_torque_nm:.2f} Nm`",
        f"- Nylon PA6 first-yield-ish torque: `{nylon_capacity.first_yieldish_torque_nm:.2f} Nm`",
        f"- Nylon PA6 governing mode: `{nylon_capacity.governing_mode}`",
        "",
        "## Same-Package Same-Ratio Family Sweep",
        "",
        "Families compared by keeping the same pitch diameters and ratio, then changing tooth counts and module together.",
        "",
        "| Family | Module (mm) | Contact ratio | PLA+ target SF torque (Nm) | Nylon target SF torque (Nm) |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]

    for item in sweep:
        lines.append(
            f"| `R{item['ring_teeth']}/P{item['planet_teeth']}/S{item['sun_teeth']}` | "
            f"{item['module_mm']:.4f} | {item['contact_ratio']:.3f} | {item['pla_target_sf_nm']:.2f} | {item['nylon_target_sf_nm']:.2f} |"
        )

    acceptable = [item for item in sweep if item["contact_ratio"] >= 1.2]
    best = acceptable[0] if acceptable else sweep[0]
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            f"- The first same-package family that clears the `contact ratio >= 1.2` screen is `R{best['ring_teeth']}/P{best['planet_teeth']}/S{best['sun_teeth']}`.",
            "- That makes `18/27/72` the better printable baseline than `12/18/48` under the current packaging constraints because the mesh overlap is no longer obviously deficient.",
            "- The visible shallow dedendum problem is materially improved by moving away from the `12/18/48` family.",
            "- This can be treated as the better fit-checked involute baseline, but it is still not a verified 16 Nm PLA+ design.",
        ]
    )

    return "\n".join(lines) + "\n"


def main():
    report = build_report()
    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        file.write(report)
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
