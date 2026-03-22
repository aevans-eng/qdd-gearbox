"""
Symbolic Involute Gear Geometry Calculator
==========================================
Uses SymPy for parametric involute gear tooth profile generation.
Generates geometry for the QDD planetary gear set (sun, planet, ring).

Skills demonstrated: Python, symbolic equations, data structure management
"""

import math
import numpy as np
from sympy import symbols, cos, sin, tan, pi, sqrt, solve, simplify, Rational
from sympy import atan2, Piecewise, N

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from calc.utils.data import GearParams, PlanetarySet
from calc.utils.constants import GEAR_RATIO, NUM_PLANETS, PRESSURE_ANGLE_DEG


# ── Symbolic Definitions ──────────────────────────────────────────────

m, z, alpha = symbols('m z alpha', positive=True)  # module, teeth, pressure angle

# Symbolic gear equations
pitch_diameter = m * z
base_diameter = pitch_diameter * cos(alpha)
addendum = m
dedendum = Rational(5, 4) * m
outer_diameter = pitch_diameter + 2 * addendum
root_diameter = pitch_diameter - 2 * dedendum
circular_pitch = pi * m
tooth_thickness = circular_pitch / 2
base_pitch = pi * m * cos(alpha)


def print_symbolic_equations():
    """Print all symbolic gear equations."""
    print("=== Symbolic Gear Equations ===\n")
    equations = {
        "Pitch Diameter (d)": pitch_diameter,
        "Base Diameter (d_b)": base_diameter,
        "Addendum (a)": addendum,
        "Dedendum (b)": dedendum,
        "Outer Diameter (d_a)": outer_diameter,
        "Root Diameter (d_f)": root_diameter,
        "Circular Pitch (p)": circular_pitch,
        "Tooth Thickness (s)": tooth_thickness,
        "Base Pitch (p_b)": base_pitch,
    }
    for name, expr in equations.items():
        print(f"  {name} = {expr}")
    print()


# ── Contact Ratio ─────────────────────────────────────────────────────

def contact_ratio_symbolic():
    """Derive the contact ratio equation symbolically."""
    z1, z2 = symbols('z1 z2', positive=True, integer=True)

    r1 = m * z1 / 2       # pitch radius gear 1
    r2 = m * z2 / 2       # pitch radius gear 2
    ra1 = r1 + m           # addendum radius gear 1
    ra2 = r2 + m           # addendum radius gear 2
    rb1 = r1 * cos(alpha)  # base radius gear 1
    rb2 = r2 * cos(alpha)  # base radius gear 2

    # Center distance (standard, no profile shift)
    a_center = r1 + r2

    # Length of path of contact
    Za = sqrt(ra1**2 - rb1**2)
    Zf = sqrt(ra2**2 - rb2**2)
    Z_total = Za + Zf - a_center * sin(alpha)

    # Contact ratio
    cr = Z_total / (pi * m * cos(alpha))
    return simplify(cr), z1, z2


def compute_contact_ratio(module_mm, z1_val, z2_val, pressure_angle_deg=20.0):
    """Numerically compute contact ratio for a gear pair."""
    alpha_rad = math.radians(pressure_angle_deg)

    r1 = module_mm * z1_val / 2.0
    r2 = module_mm * z2_val / 2.0
    ra1 = r1 + module_mm
    ra2 = r2 + module_mm
    rb1 = r1 * math.cos(alpha_rad)
    rb2 = r2 * math.cos(alpha_rad)

    a_center = r1 + r2
    Za = math.sqrt(ra1**2 - rb1**2)
    Zf = math.sqrt(ra2**2 - rb2**2)
    Z_total = Za + Zf - a_center * math.sin(alpha_rad)

    pb = math.pi * module_mm * math.cos(alpha_rad)
    cr = Z_total / pb
    return cr


# ── Involute Profile Generation ──────────────────────────────────────

def involute_profile(base_radius_mm, num_points=50, max_angle_rad=None):
    """
    Generate involute curve coordinates from base circle.

    Returns arrays of (x, y) coordinates for one side of the tooth profile.
    The involute is parameterized by the roll angle t.
    """
    if max_angle_rad is None:
        max_angle_rad = math.pi / 4  # Default range

    t = np.linspace(0, max_angle_rad, num_points)
    rb = base_radius_mm

    x = rb * (np.cos(t) + t * np.sin(t))
    y = rb * (np.sin(t) - t * np.cos(t))

    return x, y


def tooth_profile(gear: GearParams, num_points=100):
    """
    Generate a full tooth profile (both flanks + tip arc + root fillet).

    Returns x, y arrays tracing one complete tooth.
    """
    r_pitch = gear.pitch_diameter_mm / 2.0
    r_base = gear.base_diameter_mm / 2.0
    r_outer = gear.outer_diameter_mm / 2.0
    r_root = gear.root_diameter_mm / 2.0
    alpha_rad = math.radians(gear.pressure_angle_deg)

    # Involute from base circle to addendum circle
    # Find max roll angle where involute reaches addendum
    # r = r_base * sqrt(1 + t^2), so t_max = sqrt((r_outer/r_base)^2 - 1)
    t_max = math.sqrt((r_outer / r_base) ** 2 - 1)

    t = np.linspace(0, t_max, num_points // 2)

    # Right flank involute
    x_inv = r_base * (np.cos(t) + t * np.sin(t))
    y_inv = r_base * (np.sin(t) - t * np.cos(t))

    # Angular tooth thickness at pitch circle
    inv_alpha = math.tan(alpha_rad) - alpha_rad  # involute function at pressure angle
    tooth_half_angle = math.pi / (2 * gear.num_teeth) + inv_alpha

    # Rotate right flank to center the tooth on the x-axis
    cos_rot = math.cos(tooth_half_angle)
    sin_rot = math.sin(tooth_half_angle)
    x_right = x_inv * cos_rot - y_inv * sin_rot
    y_right = x_inv * sin_rot + y_inv * cos_rot

    # Left flank is mirror of right flank about x-axis
    x_left = x_right[::-1]
    y_left = -y_right[::-1]

    # Tip arc (connect right to left at addendum)
    tip_angle_start = math.atan2(y_right[-1], x_right[-1])
    tip_angle_end = math.atan2(y_left[0], x_left[0])
    tip_angles = np.linspace(tip_angle_start, tip_angle_end, 10)
    x_tip = r_outer * np.cos(tip_angles)
    y_tip = r_outer * np.sin(tip_angles)

    # Combine: left flank -> root -> right flank -> tip
    x_profile = np.concatenate([x_left, x_right, x_tip])
    y_profile = np.concatenate([y_left, y_right, y_tip])

    return x_profile, y_profile


# ── Planetary Gear Set Design ────────────────────────────────────────

def design_planetary_set(module_mm, sun_teeth, pressure_angle_deg=20.0,
                         num_planets=3, face_width_mm=10.0):
    """
    Design a complete planetary gear set for the given parameters.

    For a planetary with fixed ring and carrier output:
        ratio = 1 + Z_ring / Z_sun
        Z_ring = Z_sun + 2 * Z_planet

    Assembly condition: (Z_sun + Z_ring) must be divisible by num_planets.
    """
    # Ring teeth from ratio
    ring_teeth = int(sun_teeth * (GEAR_RATIO - 1))

    # Planet teeth
    planet_teeth = (ring_teeth - sun_teeth) // 2

    # Verify assembly condition
    if (sun_teeth + ring_teeth) % num_planets != 0:
        print(f"  WARNING: Assembly condition not met. "
              f"(Z_sun + Z_ring) = {sun_teeth + ring_teeth} "
              f"is not divisible by {num_planets}.")
        # Find nearest valid sun_teeth
        for offset in range(1, 10):
            for trial in [sun_teeth + offset, sun_teeth - offset]:
                if trial < 8:
                    continue
                rt = int(trial * (GEAR_RATIO - 1))
                pt = (rt - trial) // 2
                if (trial + rt) % num_planets == 0 and pt > 0 and (rt - trial) % 2 == 0:
                    print(f"  Suggestion: Z_sun={trial}, Z_planet={pt}, Z_ring={rt}")
                    break

    # Verify mesh
    actual_ratio = 1.0 + ring_teeth / sun_teeth
    assert ring_teeth == sun_teeth + 2 * planet_teeth, \
        f"Geometry error: Z_ring ({ring_teeth}) != Z_sun ({sun_teeth}) + 2*Z_planet ({planet_teeth})"

    sun = GearParams(module_mm, sun_teeth, pressure_angle_deg, face_width_mm)
    planet = GearParams(module_mm, planet_teeth, pressure_angle_deg, face_width_mm)
    gear_set = PlanetarySet(sun, planet, ring_teeth, num_planets)

    return gear_set


def print_gear_set(gs: PlanetarySet):
    """Print a summary of the planetary gear set."""
    print(f"=== Planetary Gear Set (ratio = {gs.ratio:.2f}:1) ===\n")
    print(f"  Module:          {gs.sun.module_mm:.2f} mm")
    print(f"  Pressure Angle:  {gs.sun.pressure_angle_deg:.1f}°")
    print(f"  Face Width:      {gs.sun.face_width_mm:.1f} mm")
    print(f"  Num Planets:     {gs.num_planets}")
    print()

    for name, g in [("Sun", gs.sun), ("Planet", gs.planet)]:
        print(f"  {name} Gear:")
        print(f"    Teeth:           {g.num_teeth}")
        print(f"    Pitch Diameter:  {g.pitch_diameter_mm:.2f} mm")
        print(f"    Base Diameter:   {g.base_diameter_mm:.2f} mm")
        print(f"    Outer Diameter:  {g.outer_diameter_mm:.2f} mm")
        print(f"    Root Diameter:   {g.root_diameter_mm:.2f} mm")
        print()

    print(f"  Ring Gear:")
    print(f"    Teeth:           {gs.ring_teeth}")
    print(f"    Pitch Diameter:  {gs.ring_pitch_diameter_mm:.2f} mm")
    print()

    # Contact ratios
    cr_sp = compute_contact_ratio(gs.sun.module_mm, gs.sun.num_teeth,
                                  gs.planet.num_teeth, gs.sun.pressure_angle_deg)
    cr_pr = compute_contact_ratio(gs.sun.module_mm, gs.planet.num_teeth,
                                  gs.ring_teeth, gs.sun.pressure_angle_deg)
    print(f"  Contact Ratio (sun-planet):    {cr_sp:.3f}")
    print(f"  Contact Ratio (planet-ring):   {cr_pr:.3f}")
    cr_ok = "PASS" if cr_sp > 1.2 and cr_pr > 1.2 else "FAIL (< 1.2)"
    print(f"  Contact Ratio Check:           {cr_ok}")
    print()


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print_symbolic_equations()

    # Design the QDD planetary set
    # Try module = 1.5 mm, sun = 12 teeth as starting point
    module_mm = 1.5
    sun_teeth = 12

    print(f"--- Designing planetary set: m={module_mm} mm, Z_sun={sun_teeth} ---\n")
    gear_set = design_planetary_set(
        module_mm=module_mm,
        sun_teeth=sun_teeth,
        pressure_angle_deg=PRESSURE_ANGLE_DEG,
        num_planets=NUM_PLANETS,
        face_width_mm=10.0,
    )

    print_gear_set(gear_set)

    # Generate and display tooth profile coordinates
    print("--- Involute Profile (Sun Gear) ---")
    x, y = tooth_profile(gear_set.sun, num_points=80)
    print(f"  Generated {len(x)} profile points")
    print(f"  X range: [{x.min():.2f}, {x.max():.2f}] mm")
    print(f"  Y range: [{y.min():.2f}, {y.max():.2f}] mm")
    print()

    # Try a few module/teeth combos for comparison
    print("=== Parameter Sweep: Valid Configurations ===\n")
    print(f"  {'Module':>8} {'Z_sun':>6} {'Z_planet':>9} {'Z_ring':>7} {'d_sun':>7} {'d_ring':>8} {'CR_sp':>6} {'Assembly':>9}")
    print(f"  {'(mm)':>8} {'':>6} {'':>9} {'':>7} {'(mm)':>7} {'(mm)':>8} {'':>6} {'':>9}")
    print("  " + "-" * 70)

    for mod in [1.0, 1.25, 1.5, 2.0]:
        for zs in range(10, 25):
            zr = int(zs * (GEAR_RATIO - 1))
            zp = (zr - zs) // 2
            if (zr - zs) % 2 != 0 or zp < 5:
                continue
            if (zs + zr) % NUM_PLANETS != 0:
                continue
            cr = compute_contact_ratio(mod, zs, zp)
            d_sun = mod * zs
            d_ring = mod * zr
            asm = "OK" if (zs + zr) % NUM_PLANETS == 0 else "FAIL"
            print(f"  {mod:>8.2f} {zs:>6} {zp:>9} {zr:>7} {d_sun:>7.1f} {d_ring:>8.1f} {cr:>6.3f} {asm:>9}")


if __name__ == "__main__":
    main()
