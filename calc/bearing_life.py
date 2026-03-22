"""
Bearing Life Calculator (ISO 281)
=================================
L10 basic rating life prediction for bearings in the QDD gearbox.
Supports variable-duty load spectrum analysis.

Skills demonstrated: data structure management, engineering analysis
"""

import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from calc.utils.data import (
    BearingData, LoadCase, PlanetarySet,
    BEARING_6805, BEARING_685, BEARING_683, BEARING_6710,
)
from calc.utils.constants import (
    OUTPUT_PEAK_TORQUE_NM, OUTPUT_CONT_TORQUE_NM,
    OUTPUT_MAX_SPEED_RPM, GEAR_RATIO, NUM_PLANETS,
)
from calc.gear_geometry import design_planetary_set
from calc.utils.constants import PRESSURE_ANGLE_DEG


# ── ISO 281 Basic Rating Life ─────────────────────────────────────────

def basic_life_revolutions(bearing: BearingData, equivalent_load_kn: float):
    """
    ISO 281 L10 basic rating life in millions of revolutions.

    L10 = (C / P)^p

    where:
        C = basic dynamic load rating (kN)
        P = equivalent dynamic bearing load (kN)
        p = life exponent (3 for ball bearings, 10/3 for roller)
    """
    if equivalent_load_kn <= 0:
        return float('inf')

    if bearing.bearing_type == "deep_groove":
        p = 3.0  # Ball bearing exponent
    else:
        p = 10.0 / 3.0  # Roller bearing exponent

    l10 = (bearing.dynamic_rating_kn / equivalent_load_kn) ** p
    return l10  # millions of revolutions


def life_hours(l10_mrev: float, speed_rpm: float):
    """Convert L10 from millions of revolutions to hours."""
    if speed_rpm <= 0 or l10_mrev == float('inf'):
        return float('inf')
    return (l10_mrev * 1e6) / (speed_rpm * 60.0)


# ── Equivalent Dynamic Load ──────────────────────────────────────────

def equivalent_dynamic_load(radial_kn: float, axial_kn: float,
                            bearing: BearingData):
    """
    Equivalent dynamic bearing load P (kN) per ISO 281.

    For deep groove ball bearings:
        If F_a/F_r <= e:  P = F_r + Y1 * F_a  (usually P = F_r)
        If F_a/F_r > e:   P = X * F_r + Y * F_a

    Simplified: for pure radial (axial = 0): P = F_r
    For combined loads with typical deep groove factors.
    """
    if radial_kn <= 0 and axial_kn <= 0:
        return 0.0

    if bearing.bearing_type == "deep_groove":
        # Simplified deep groove factors (typical values)
        e = 0.19  # Threshold ratio
        X = 0.56
        Y = 2.30

        if radial_kn <= 0:
            return Y * axial_kn

        ratio = axial_kn / radial_kn
        if ratio <= e:
            return radial_kn
        else:
            return X * radial_kn + Y * axial_kn
    else:
        # Default: pure radial
        return radial_kn


# ── Load Spectrum Life ────────────────────────────────────────────────

def spectrum_life(bearing: BearingData, load_cases: list):
    """
    Weighted bearing life for a variable-duty load spectrum.
    Uses Palmgren-Miner linear damage accumulation:

        1/L10_total = Σ (q_i / L10_i)

    where q_i is the fraction of time at load case i.
    """
    damage_sum = 0.0

    for lc in load_cases:
        p_eq = equivalent_dynamic_load(
            lc.radial_load_n / 1000.0,
            lc.axial_load_n / 1000.0,
            bearing,
        )
        l10_i = basic_life_revolutions(bearing, p_eq)
        if l10_i == float('inf') or l10_i <= 0:
            continue
        damage_sum += lc.duration_fraction / l10_i

    if damage_sum <= 0:
        return float('inf')
    return 1.0 / damage_sum  # millions of revolutions


# ── Gear Force to Bearing Loads ───────────────────────────────────────

def gear_forces_to_bearing_loads(gear_set: PlanetarySet, output_torque_nm: float):
    """
    Calculate bearing loads from gear mesh forces.

    Returns dict of bearing location -> radial load (N).
    """
    # Sun gear tangential force per planet
    sun_torque = output_torque_nm / gear_set.ratio
    sun_radius_m = gear_set.sun.pitch_diameter_mm / 2000.0
    ft_total = sun_torque / sun_radius_m
    ft_per_planet = ft_total / gear_set.num_planets

    alpha_rad = math.radians(gear_set.sun.pressure_angle_deg)
    fr_per_planet = ft_per_planet * math.tan(alpha_rad)  # Radial component

    # Resultant force on each planet pin
    planet_pin_force = math.sqrt(ft_per_planet**2 + fr_per_planet**2)

    # Main output bearing — carries full output torque reaction
    # Radial load on output bearing from carrier imbalance (ideally zero
    # with symmetric planets, but account for some misalignment)
    output_bearing_radial = ft_total * 0.1  # 10% imbalance factor

    # Input (motor side) bearing — carries sun gear reaction
    input_bearing_radial = ft_total

    return {
        "planet_pin": planet_pin_force,
        "output_main": output_bearing_radial,
        "input_main": input_bearing_radial,
        "carrier_pin": planet_pin_force,
    }


# ── Main Analysis ─────────────────────────────────────────────────────

def analyze_bearings(gear_set: PlanetarySet):
    """Full bearing life analysis for the QDD gearbox."""
    print("=" * 60)
    print("  QDD Gearbox — Bearing Life Analysis (ISO 281)")
    print("=" * 60)
    print()

    # Define load cases (duty cycle)
    # Continuous: 70% of time at rated continuous torque
    # Peak: 20% of time at peak torque
    # Light: 10% at half continuous torque
    load_cases_cont = [
        LoadCase(0, 0, OUTPUT_MAX_SPEED_RPM, 0.10, "Light load (50%)"),
        LoadCase(0, 0, OUTPUT_MAX_SPEED_RPM, 0.70, "Continuous (100%)"),
        LoadCase(0, 0, OUTPUT_MAX_SPEED_RPM, 0.20, "Peak (133%)"),
    ]

    forces_cont = gear_forces_to_bearing_loads(gear_set, OUTPUT_CONT_TORQUE_NM)
    forces_peak = gear_forces_to_bearing_loads(gear_set, OUTPUT_PEAK_TORQUE_NM)
    forces_light = gear_forces_to_bearing_loads(gear_set, OUTPUT_CONT_TORQUE_NM * 0.5)

    print("--- Gear Mesh Forces ---\n")
    print(f"  At continuous torque ({OUTPUT_CONT_TORQUE_NM} Nm output):")
    for loc, force in forces_cont.items():
        print(f"    {loc:>20s}: {force:.1f} N")
    print(f"\n  At peak torque ({OUTPUT_PEAK_TORQUE_NM} Nm output):")
    for loc, force in forces_peak.items():
        print(f"    {loc:>20s}: {force:.1f} N")
    print()

    # Bearing assignments
    bearing_map = {
        "Planet Pin Bearing (685ZZ)": (BEARING_685, "planet_pin"),
        "Carrier Pin Bearing (683ZZ)": (BEARING_683, "carrier_pin"),
        "Output Bearing (6710-2RS)": (BEARING_6710, "output_main"),
        "Input Bearing (6805-2RS)": (BEARING_6805, "input_main"),
    }

    speed_map = {
        "planet_pin": OUTPUT_MAX_SPEED_RPM * (GEAR_RATIO - 1),  # Planet spin speed
        "carrier_pin": OUTPUT_MAX_SPEED_RPM * (GEAR_RATIO - 1),
        "output_main": OUTPUT_MAX_SPEED_RPM,
        "input_main": OUTPUT_MAX_SPEED_RPM * GEAR_RATIO,
    }

    print("--- Bearing Life Predictions ---\n")
    print(f"  {'Bearing':>35s} {'Load(N)':>8} {'Speed':>7} {'L10(Mrev)':>10} {'L10(hrs)':>10} {'Status':>8}")
    print("  " + "-" * 82)

    all_pass = True
    for name, (bearing, loc) in bearing_map.items():
        # Build load spectrum for this bearing
        load_cases = [
            LoadCase(forces_light[loc], 0, speed_map[loc], 0.10),
            LoadCase(forces_cont[loc], 0, speed_map[loc], 0.70),
            LoadCase(forces_peak[loc], 0, speed_map[loc], 0.20),
        ]

        l10_mrev = spectrum_life(bearing, load_cases)
        l10_hrs = life_hours(l10_mrev, speed_map[loc])

        # Use continuous load for display
        load_n = forces_cont[loc]
        speed = speed_map[loc]
        status = "PASS" if l10_hrs > 5000 else "FAIL"
        if status == "FAIL":
            all_pass = False

        if l10_hrs == float('inf'):
            print(f"  {name:>35s} {load_n:>8.1f} {speed:>7.0f} {'inf':>10} {'inf':>10} {status:>8}")
        else:
            print(f"  {name:>35s} {load_n:>8.1f} {speed:>7.0f} {l10_mrev:>10.1f} {l10_hrs:>10.0f} {status:>8}")

    print()
    print(f"  Target: > 5000 hours at rated duty cycle")
    print(f"  Overall: {'ALL PASS' if all_pass else 'SOME BEARINGS FAIL — increase size or reduce load'}")
    print()

    return forces_cont, forces_peak


def main():
    # Use default gear set
    gear_set = design_planetary_set(1.5, 12, PRESSURE_ANGLE_DEG, NUM_PLANETS, 10.0)

    print(f"Gear set: m=1.5 mm, Z_sun=12, Z_planet={gear_set.planet.num_teeth}, "
          f"Z_ring={gear_set.ring_teeth}\n")

    analyze_bearings(gear_set)

    # Also show static safety check
    print("--- Static Load Safety Check ---\n")
    forces_peak = gear_forces_to_bearing_loads(gear_set, OUTPUT_PEAK_TORQUE_NM)
    bearing_map = {
        "685ZZ (planet pin)": (BEARING_685, "planet_pin"),
        "683ZZ (carrier pin)": (BEARING_683, "carrier_pin"),
        "6710-2RS (output)": (BEARING_6710, "output_main"),
        "6805-2RS (input)": (BEARING_6805, "input_main"),
    }

    print(f"  {'Bearing':>25s} {'Peak Load(N)':>12} {'C0(kN)':>8} {'S0':>6} {'Status':>8}")
    print("  " + "-" * 62)

    for name, (bearing, loc) in bearing_map.items():
        load_kn = forces_peak[loc] / 1000.0
        s0 = bearing.static_rating_kn / load_kn if load_kn > 0 else float('inf')
        status = "PASS" if s0 >= 1.0 else "FAIL"
        print(f"  {name:>25s} {forces_peak[loc]:>12.1f} {bearing.static_rating_kn:>8.2f} "
              f"{s0:>6.1f} {status:>8}")
    print()


if __name__ == "__main__":
    main()
