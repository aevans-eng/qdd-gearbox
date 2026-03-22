"""
Gear Tooth Stress Calculator with Iterative Solver
===================================================
Calculates Lewis bending stress and Hertzian contact stress for
the QDD planetary gear set. Includes an iterative solver that finds
minimum module/face-width to meet a target safety factor.

Skills demonstrated: iterative solvers, engineering analysis
"""

import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from calc.utils.data import GearParams, PlanetarySet, MaterialProps, PLA_PLUS, NYLON_PA6
from calc.utils.constants import (
    OUTPUT_PEAK_TORQUE_NM, GEAR_RATIO, NUM_PLANETS,
    PRESSURE_ANGLE_DEG, MIN_SAFETY_FACTOR_BENDING, MIN_SAFETY_FACTOR_CONTACT,
)
from calc.gear_geometry import design_planetary_set, compute_contact_ratio


# ── Lewis Form Factor ────────────────────────────────────────────────

def lewis_form_factor(num_teeth, pressure_angle_deg=20.0):
    """
    Approximate Lewis form factor Y for standard full-depth teeth.
    Uses the classic approximation: Y = 2/3 * (1 - 2.87/z) for 20° PA.
    More accurate values should come from AGMA tables.
    """
    z = num_teeth
    if pressure_angle_deg == 20.0:
        # Standard approximation (Shigley's)
        y = (2.0 / 3.0) * (1.0 - 2.87 / z)
    else:
        # Fallback for other pressure angles
        y = 0.154 - 0.912 / z
    return max(y, 0.05)  # Floor to avoid negative for very small z


# ── Lewis Bending Stress ─────────────────────────────────────────────

def lewis_bending_stress(tangential_force_n, module_mm, face_width_mm, num_teeth,
                         pressure_angle_deg=20.0):
    """
    Lewis bending stress at the tooth root (MPa).

    σ_b = F_t / (m * b * Y)

    where:
        F_t = tangential force (N)
        m   = module (mm)
        b   = face width (mm)
        Y   = Lewis form factor
    """
    y = lewis_form_factor(num_teeth, pressure_angle_deg)
    sigma_b = tangential_force_n / (module_mm * face_width_mm * y)
    return sigma_b


# ── Hertzian Contact Stress ──────────────────────────────────────────

def hertzian_contact_stress(tangential_force_n, gear1: GearParams, gear2: GearParams,
                            material: MaterialProps):
    """
    Hertzian contact stress at the pitch point (MPa).

    σ_c = sqrt( F_t / (b * d1) * (1/sin(α)cos(α)) * ((1/r1 + 1/r2) * E*) )

    Simplified AGMA-style:
        σ_c = Z_E * sqrt( F_t * K_H / (b * d1 * Z_I) )

    Using fundamental Hertz approach for two cylinders in contact.
    """
    alpha_rad = math.radians(gear1.pressure_angle_deg)
    r1 = gear1.pitch_diameter_mm / 2.0  # mm
    r2 = gear2.pitch_diameter_mm / 2.0  # mm
    b = gear1.face_width_mm             # mm

    # Radii of curvature at pitch point
    rho1 = r1 * math.sin(alpha_rad)  # mm
    rho2 = r2 * math.sin(alpha_rad)  # mm

    # Equivalent radius of curvature
    rho_eq = (rho1 * rho2) / (rho1 + rho2)  # mm

    # Effective elastic modulus (both gears same material)
    E_star = material.elastic_modulus_mpa / (2.0 * (1.0 - material.poisson_ratio**2))

    # Hertzian contact stress (cylinders)
    # σ_c = sqrt( F_t * E* / (π * b * ρ_eq) )
    sigma_c = math.sqrt(tangential_force_n * E_star / (math.pi * b * rho_eq))

    return sigma_c


# ── Force Analysis ────────────────────────────────────────────────────

def tangential_force_on_sun(output_torque_nm, gear_set: PlanetarySet):
    """
    Tangential force on the sun gear from the mesh with planets.

    For planetary with fixed ring, carrier output:
        T_sun = T_output / ratio
        F_t = T_sun / (r_sun / 1000)  (convert mm to m)
        Force per planet = F_t / num_planets
    """
    sun_torque_nm = output_torque_nm / gear_set.ratio
    sun_radius_m = gear_set.sun.pitch_diameter_mm / 2000.0
    total_tangential = sun_torque_nm / sun_radius_m  # N
    force_per_planet = total_tangential / gear_set.num_planets
    return force_per_planet


# ── Stress Analysis ──────────────────────────────────────────────────

def analyze_stresses(gear_set: PlanetarySet, material: MaterialProps,
                     output_torque_nm=OUTPUT_PEAK_TORQUE_NM):
    """Run full stress analysis on the planetary gear set."""
    ft = tangential_force_on_sun(output_torque_nm, gear_set)

    # Sun gear bending
    sigma_b_sun = lewis_bending_stress(
        ft, gear_set.sun.module_mm, gear_set.sun.face_width_mm,
        gear_set.sun.num_teeth, gear_set.sun.pressure_angle_deg
    )

    # Planet gear bending
    sigma_b_planet = lewis_bending_stress(
        ft, gear_set.planet.module_mm, gear_set.planet.face_width_mm,
        gear_set.planet.num_teeth, gear_set.planet.pressure_angle_deg
    )

    # Sun-planet contact stress
    sigma_c_sp = hertzian_contact_stress(ft, gear_set.sun, gear_set.planet, material)

    # Safety factors
    sf_bend_sun = material.yield_strength_mpa / sigma_b_sun
    sf_bend_planet = material.yield_strength_mpa / sigma_b_planet
    sf_contact = material.yield_strength_mpa / sigma_c_sp

    results = {
        "tangential_force_n": ft,
        "bending_stress_sun_mpa": sigma_b_sun,
        "bending_stress_planet_mpa": sigma_b_planet,
        "contact_stress_mpa": sigma_c_sp,
        "sf_bending_sun": sf_bend_sun,
        "sf_bending_planet": sf_bend_planet,
        "sf_contact": sf_contact,
    }
    return results


def print_stress_results(results, material_name=""):
    """Print stress analysis results."""
    print(f"=== Tooth Stress Analysis{' (' + material_name + ')' if material_name else ''} ===\n")
    print(f"  Tangential Force per Planet:  {results['tangential_force_n']:.1f} N")
    print()
    print(f"  Bending Stress (Sun):         {results['bending_stress_sun_mpa']:.1f} MPa")
    print(f"  Bending Stress (Planet):      {results['bending_stress_planet_mpa']:.1f} MPa")
    print(f"  Contact Stress (Sun-Planet):  {results['contact_stress_mpa']:.1f} MPa")
    print()
    print(f"  Safety Factor — Bending (Sun):    {results['sf_bending_sun']:.2f}"
          f"  {'PASS' if results['sf_bending_sun'] >= MIN_SAFETY_FACTOR_BENDING else 'FAIL'}")
    print(f"  Safety Factor — Bending (Planet): {results['sf_bending_planet']:.2f}"
          f"  {'PASS' if results['sf_bending_planet'] >= MIN_SAFETY_FACTOR_BENDING else 'FAIL'}")
    print(f"  Safety Factor — Contact:          {results['sf_contact']:.2f}"
          f"  {'PASS' if results['sf_contact'] >= MIN_SAFETY_FACTOR_CONTACT else 'FAIL'}")
    print()


# ── Iterative Solver ──────────────────────────────────────────────────

def find_minimum_geometry(material: MaterialProps, output_torque_nm=OUTPUT_PEAK_TORQUE_NM,
                          target_sf_bending=MIN_SAFETY_FACTOR_BENDING,
                          target_sf_contact=MIN_SAFETY_FACTOR_CONTACT,
                          module_range=(0.5, 3.0), module_step=0.25,
                          fw_range=(5.0, 25.0), fw_step=1.0,
                          sun_teeth_range=(10, 24)):
    """
    Iterative solver: sweep module, face width, and sun teeth to find the
    minimum geometry that meets target safety factors.

    Returns list of valid configurations sorted by compactness (ring OD).
    """
    valid = []

    mod = module_range[0]
    while mod <= module_range[1]:
        for zs in range(sun_teeth_range[0], sun_teeth_range[1] + 1):
            zr = int(zs * (GEAR_RATIO - 1))
            zp = (zr - zs) // 2
            if (zr - zs) % 2 != 0 or zp < 5:
                continue
            if (zs + zr) % NUM_PLANETS != 0:
                continue

            # Check contact ratio
            cr = compute_contact_ratio(mod, zs, zp)
            if cr < 1.2:
                continue

            fw = fw_range[0]
            while fw <= fw_range[1]:
                gs = design_planetary_set(mod, zs, PRESSURE_ANGLE_DEG, NUM_PLANETS, fw)
                res = analyze_stresses(gs, material, output_torque_nm)

                if (res["sf_bending_sun"] >= target_sf_bending and
                        res["sf_bending_planet"] >= target_sf_bending and
                        res["sf_contact"] >= target_sf_contact):
                    ring_od = mod * zr + 2 * mod  # approximate ring OD
                    valid.append({
                        "module_mm": mod,
                        "sun_teeth": zs,
                        "planet_teeth": zp,
                        "ring_teeth": zr,
                        "face_width_mm": fw,
                        "ring_od_mm": ring_od,
                        "sf_bending_sun": res["sf_bending_sun"],
                        "sf_bending_planet": res["sf_bending_planet"],
                        "sf_contact": res["sf_contact"],
                        "contact_ratio": cr,
                    })
                    break  # Found min face width for this module/teeth combo
                fw += fw_step
        mod += module_step

    # Sort by ring OD (most compact first)
    valid.sort(key=lambda x: x["ring_od_mm"])
    return valid


# ── Main ──────────────────────────────────────────────────────────────

def main():
    # Baseline analysis with PLA+ and starting geometry
    print("=" * 60)
    print("  QDD Gearbox — Tooth Stress Calculator")
    print("=" * 60)
    print()

    module_mm = 1.5
    sun_teeth = 12
    face_width = 10.0

    gear_set = design_planetary_set(module_mm, sun_teeth, PRESSURE_ANGLE_DEG,
                                    NUM_PLANETS, face_width)

    print(f"Baseline: m={module_mm} mm, Z_sun={sun_teeth}, b={face_width} mm\n")

    for mat in [PLA_PLUS, NYLON_PA6]:
        results = analyze_stresses(gear_set, mat)
        print_stress_results(results, mat.name)

    # Run iterative solver
    print("=" * 60)
    print("  Iterative Solver — Finding Minimum Geometry")
    print("=" * 60)
    print()

    for mat in [PLA_PLUS, NYLON_PA6]:
        print(f"--- Material: {mat.name} (Sy = {mat.yield_strength_mpa} MPa) ---\n")
        configs = find_minimum_geometry(mat)

        if not configs:
            print("  No valid configuration found in search range.\n")
            continue

        print(f"  Found {len(configs)} valid configurations. Top 5 most compact:\n")
        print(f"  {'m':>5} {'Zs':>4} {'Zp':>4} {'Zr':>4} {'b':>6} {'Ring OD':>8} "
              f"{'SF_b(s)':>8} {'SF_b(p)':>8} {'SF_c':>6} {'CR':>5}")
        print("  " + "-" * 65)

        for cfg in configs[:5]:
            print(f"  {cfg['module_mm']:>5.2f} {cfg['sun_teeth']:>4} "
                  f"{cfg['planet_teeth']:>4} {cfg['ring_teeth']:>4} "
                  f"{cfg['face_width_mm']:>6.1f} {cfg['ring_od_mm']:>8.1f} "
                  f"{cfg['sf_bending_sun']:>8.2f} {cfg['sf_bending_planet']:>8.2f} "
                  f"{cfg['sf_contact']:>6.2f} {cfg['contact_ratio']:>5.2f}")
        print()

        best = configs[0]
        print(f"  >> Recommended: m={best['module_mm']} mm, Z_sun={best['sun_teeth']}, "
              f"b={best['face_width_mm']} mm, Ring OD={best['ring_od_mm']:.1f} mm\n")


if __name__ == "__main__":
    main()
