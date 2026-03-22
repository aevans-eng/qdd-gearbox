"""
Gear Design Rules - Planet Overlap Check

This module provides functions to check if planet gears will overlap
and to calculate the maximum number of planets for a given configuration.

GEOMETRY:
- Gears are scaled so ring gear outer profile fits on ~unit circle
- Scale factor: f = (S + P) where S=sun teeth, P=planet teeth
- Planet pitch radius: P/f = P/(S+P)
- Carrier radius (planet centers): 1.0 (normalized)
- Planet outer radius (with teeth): approximately (P + tooth_addendum)/f

OVERLAP CONDITION:
- N planets are evenly spaced at angles 2*pi*k/N for k=0,1,...,N-1
- Distance between adjacent planet centers: 2 * sin(pi/N) (on unit carrier)
- Planets overlap if: 2*sin(pi/N) < 2*r_planet_outer
- Non-overlap requires: sin(pi/N) > r_planet_outer

LOCKED GEAR CONFIGURATIONS (for reference):
- Lock SUN, input CARRIER, output RING: ratio = R/(R+S) [always < 1, speed increase on ring]
- Lock SUN, input RING, output CARRIER: ratio = (R+S)/R [always > 1, reduction]
- Lock RING, input SUN, output CARRIER: ratio = (R+S)/S = 1 + R/S [reduction, used for high ratios]
- Lock RING, input CARRIER, output SUN: ratio = S/(R+S) [always < 1, speed increase on sun]
- Lock CARRIER, input SUN, output RING: ratio = -R/S [reverses direction]
- Lock CARRIER, input RING, output SUN: ratio = -S/R [reverses direction]
"""

import numpy as np


def planet_outer_radius(S, P, tooth_addendum=1.2, b=0.8):
    """
    Calculate the approximate outer radius of a planet gear (normalized).

    The tooth_addendum accounts for how far teeth extend beyond the pitch circle.
    For epicycloidal profiles with b=0.8, teeth extend further than standard involute.

    Args:
        S: Sun gear teeth
        P: Planet gear teeth
        tooth_addendum: Extra radius for teeth (in tooth units). Default 1.2 for epicycloidal.
        b: Tooth profile parameter (higher = more epicycloidal = taller teeth)

    Returns:
        Outer radius of planet gear on normalized (unit carrier) scale
    """
    f = S + P  # scale factor
    # Pitch radius plus tooth height, scaled
    r_outer = (P + tooth_addendum * (0.5 + b)) / f
    return r_outer


def min_planet_spacing(N):
    """
    Calculate the minimum distance between adjacent planet centers.

    Args:
        N: Number of planets

    Returns:
        Chord distance between adjacent planet centers (on unit carrier radius)
    """
    return 2 * np.sin(np.pi / N)


def check_planet_overlap(S, P, N, safety_margin=1.1, b=0.8):
    """
    Check if planet gears will overlap.

    Args:
        S: Sun gear teeth
        P: Planet gear teeth
        N: Number of planets
        safety_margin: Multiplier for clearance (1.0 = touching, 1.1 = 10% gap)
        b: Tooth profile parameter

    Returns:
        dict with:
            - valid: True if planets don't overlap
            - spacing: Distance between planet centers
            - planet_diameter: Diameter of planet gear (with teeth)
            - clearance: Gap between adjacent planets (negative = overlap)
            - clearance_pct: Clearance as percentage of planet diameter
    """
    r_planet = planet_outer_radius(S, P, b=b)
    planet_diameter = 2 * r_planet
    spacing = min_planet_spacing(N)
    clearance = spacing - planet_diameter * safety_margin

    return {
        'valid': clearance > 0,
        'spacing': spacing,
        'planet_diameter': planet_diameter,
        'clearance': clearance,
        'clearance_pct': (clearance / planet_diameter) * 100 if planet_diameter > 0 else 0,
        'N': N,
        'S': S,
        'P': P,
    }


def max_planets(S, P, safety_margin=1.1, b=0.8, max_N=12):
    """
    Calculate the maximum number of planets that fit without overlap.

    Args:
        S: Sun gear teeth
        P: Planet gear teeth
        safety_margin: Clearance multiplier
        b: Tooth profile parameter
        max_N: Maximum N to check

    Returns:
        Maximum valid N, or 0 if even N=2 doesn't work
    """
    for N in range(max_N, 1, -1):
        result = check_planet_overlap(S, P, N, safety_margin, b)
        if result['valid']:
            return N
    return 0


def min_planets(S, P, R):
    """
    Calculate minimum planets needed for assembly/timing constraints.

    For a planetary gear to assemble properly, (R + S) must be divisible by N,
    or the planets won't mesh correctly with both sun and ring simultaneously.

    Args:
        S: Sun gear teeth
        P: Planet gear teeth
        R: Ring gear teeth

    Returns:
        Minimum N that satisfies assembly constraint (typically 2 or 3)
    """
    # Assembly constraint: (R + S) mod N == 0 for symmetric assembly
    # But asymmetric assembly is possible, so minimum is usually 2
    return 2


def valid_planet_counts(S, P, R, safety_margin=1.1, b=0.8, max_N=12):
    """
    Get list of valid planet counts for a configuration.

    Args:
        S, P, R: Gear teeth counts
        safety_margin: Clearance multiplier
        b: Tooth profile parameter
        max_N: Maximum N to check

    Returns:
        List of valid N values (that don't cause overlap)
    """
    valid = []
    for N in range(2, max_N + 1):
        result = check_planet_overlap(S, P, N, safety_margin, b)
        if result['valid']:
            valid.append(N)
    return valid


def calculate_ratio(S, P, R, config):
    """
    Calculate gear ratio for a given locked gear configuration.

    Args:
        S: Sun teeth
        P: Planet teeth (not used in ratio, but included for completeness)
        R: Ring teeth
        config: Tuple of (input, output, locked) e.g., ('s', 'c', 'r')

    Returns:
        Gear ratio (input rotations per output rotation)
    """
    input_gear, output_gear, locked_gear = config

    # Planetary gear fundamental equation: R*ωr + S*ωs = (R+S)*ωc
    # With one gear locked (ω=0), solve for input/output ratio

    if locked_gear == 'r':  # Ring locked
        if input_gear == 's' and output_gear == 'c':
            return (R + S) / S  # Reduction (sun faster than carrier)
        elif input_gear == 'c' and output_gear == 's':
            return S / (R + S)  # Speed increase (carrier slower than sun)

    elif locked_gear == 's':  # Sun locked
        if input_gear == 'c' and output_gear == 'r':
            return R / (R + S)  # Speed increase (ring faster than carrier)
        elif input_gear == 'r' and output_gear == 'c':
            return (R + S) / R  # Reduction

    elif locked_gear == 'c':  # Carrier locked
        if input_gear == 's' and output_gear == 'r':
            return -R / S  # Reversal + ratio change
        elif input_gear == 'r' and output_gear == 's':
            return -S / R  # Reversal + ratio change

    raise ValueError(f"Unknown config: {config}")


def print_all_ratios(S, P, R):
    """Print all possible gear ratios for a configuration."""
    print(f"\nGear ratios for S={S}, P={P}, R={R}:")
    print("-" * 60)

    configs = [
        (('s', 'c', 'r'), "Ring locked, Sun->Carrier"),
        (('c', 's', 'r'), "Ring locked, Carrier->Sun"),
        (('c', 'r', 's'), "Sun locked, Carrier->Ring"),
        (('r', 'c', 's'), "Sun locked, Ring->Carrier"),
        (('s', 'r', 'c'), "Carrier locked, Sun->Ring"),
        (('r', 's', 'c'), "Carrier locked, Ring->Sun"),
    ]

    for config, desc in configs:
        try:
            ratio = calculate_ratio(S, P, R, config)
            if ratio > 0:
                print(f"  {desc}: {ratio:.3f}:1")
            else:
                print(f"  {desc}: {ratio:.3f}:1 (REVERSES DIRECTION)")
        except Exception as e:
            print(f"  {desc}: ERROR - {e}")


def design_planetary(target_ratio, ratio_tolerance=1.0, S_range=(4, 10), b=0.8, safety_margin=1.1):
    """
    Design a planetary gear set for a target ratio.

    Args:
        target_ratio: Desired gear ratio (e.g., 5.0 for 5:1)
        ratio_tolerance: Acceptable deviation from target (e.g., 1.0 means 4:1 to 6:1)
        S_range: Range of sun teeth to try
        b: Tooth profile parameter
        safety_margin: Clearance multiplier for overlap check

    Returns:
        List of valid configurations sorted by ratio closeness to target
    """
    configs = []

    for S in range(S_range[0], S_range[1] + 1):
        # For ring-locked config (best for high ratios): ratio = (R+S)/S = 1 + R/S
        # So R = S * (ratio - 1)

        for ratio_adj in np.linspace(-ratio_tolerance, ratio_tolerance, 21):
            test_ratio = target_ratio + ratio_adj
            if test_ratio <= 1:
                continue

            R_float = S * (test_ratio - 1)
            R = round(R_float)

            # Meshing constraint: R = S + 2*P
            P_float = (R - S) / 2
            if P_float != int(P_float) or P_float < 2:
                continue
            P = int(P_float)

            # Verify meshing
            if R != S + 2 * P:
                continue

            # Calculate actual ratio
            actual_ratio = (R + S) / S

            # Check if within tolerance
            if abs(actual_ratio - target_ratio) > ratio_tolerance:
                continue

            # Find valid planet counts
            valid_N = valid_planet_counts(S, P, R, safety_margin, b)

            if len(valid_N) > 0:
                configs.append({
                    'S': S,
                    'P': P,
                    'R': R,
                    'ratio': actual_ratio,
                    'ratio_error': abs(actual_ratio - target_ratio),
                    'valid_N': valid_N,
                    'max_N': max(valid_N),
                    'config': ('s', 'c', 'r'),  # Ring locked
                    'config_desc': 'Ring locked, Sun input, Carrier output',
                })

    # Sort by ratio error, then by max_N (prefer more planets)
    configs.sort(key=lambda x: (x['ratio_error'], -x['max_N']))

    # Remove duplicates
    seen = set()
    unique = []
    for c in configs:
        key = (c['S'], c['P'], c['R'])
        if key not in seen:
            seen.add(key)
            unique.append(c)

    return unique


if __name__ == "__main__":
    print("=" * 60)
    print("GEAR DESIGN RULES - Analysis")
    print("=" * 60)

    # Analyze the problematic configurations from the sweep
    print("\n\nANALYSIS OF PREVIOUS SWEEP CONFIGURATIONS:")
    print("-" * 60)

    test_configs = [
        (4, 6, 16, 4),   # S=4, P=6, R=16, N=4 (reported overlap)
        (5, 8, 21, 3),   # S=5, P=8, R=21, N=3
        (6, 9, 24, 3),   # S=6, P=9, R=24, N=3
        (7, 10, 27, 3),  # S=7, P=10, R=27, N=3 (reported too sparse?)
    ]

    for S, P, R, N in test_configs:
        result = check_planet_overlap(S, P, N, safety_margin=1.1, b=0.8)
        max_N = max_planets(S, P, safety_margin=1.1, b=0.8)
        valid_N = valid_planet_counts(S, P, R, safety_margin=1.1, b=0.8)
        ratio = (R + S) / S

        status = "OK" if result['valid'] else "OVERLAP"
        print(f"\nS={S}, P={P}, R={R}, N={N}:")
        print(f"  Ratio: {ratio:.2f}:1")
        print(f"  Status: {status}")
        print(f"  Planet diameter: {result['planet_diameter']:.3f}")
        print(f"  Planet spacing:  {result['spacing']:.3f}")
        print(f"  Clearance: {result['clearance']:.3f} ({result['clearance_pct']:.1f}%)")
        print(f"  Max planets: {max_N}")
        print(f"  Valid N values: {valid_N}")

    # Show all ratio options for one config
    print_all_ratios(6, 9, 24)

    # Design new configurations
    print("\n\n" + "=" * 60)
    print("RECOMMENDED CONFIGURATIONS FOR ~5:1 RATIO (±1)")
    print("Ring locked, Sun input, Carrier output")
    print("=" * 60)

    recommendations = design_planetary(
        target_ratio=5.0,
        ratio_tolerance=1.0,
        S_range=(4, 10),
        b=0.8,
        safety_margin=1.1
    )

    print(f"\nFound {len(recommendations)} valid configurations:\n")
    print(f"{'S':>3} {'P':>3} {'R':>3} {'Ratio':>7} {'Valid N':>12} {'Max N':>6}")
    print("-" * 42)

    for cfg in recommendations[:15]:  # Show top 15
        valid_n_str = ','.join(map(str, cfg['valid_N'][:5]))
        if len(cfg['valid_N']) > 5:
            valid_n_str += '...'
        print(f"{cfg['S']:>3} {cfg['P']:>3} {cfg['R']:>3} {cfg['ratio']:>7.2f}:1 {valid_n_str:>12} {cfg['max_N']:>6}")
