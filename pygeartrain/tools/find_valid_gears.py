"""
Find valid gear configurations with proper meshing (no polygon overlap).

Design Rules Discovered:
1. Planet-to-Planet: Planets must not overlap each other
2. Sun-Planet: Planet polygons must not overlap sun polygon (>1% is invalid)
3. Planet-Ring: Planet polygons must not protrude outside ring

The key validation is Sun-Planet polygon intersection area.
"""

import numpy as np
from shapely.geometry import Polygon
from pygeartrain.planetary import Planetary, PlanetaryGeometry


def get_polygons(S, P, R, N, b, phase=0):
    """Extract Shapely polygons from a gear configuration."""
    kinematics = Planetary('s', 'c', 'r')
    gear = PlanetaryGeometry.create(kinematics, (R, P, S), N, b=b)

    profiles = gear.arrange(phase)
    ring_profile, planet_profiles, sun_profile, carrier_profile = profiles

    def to_polygon(profile):
        v = profile.vertices
        if len(v) < 3:
            return None
        if not np.allclose(v[0], v[-1]):
            v = np.vstack([v, v[0]])
        try:
            poly = Polygon(v)
            if not poly.is_valid:
                poly = poly.buffer(0)
            return poly
        except:
            return None

    sun_poly = to_polygon(sun_profile)
    planet_polys = [to_polygon(p) for p in planet_profiles]
    ring_poly = to_polygon(ring_profile)

    return sun_poly, planet_polys, ring_poly


def check_overlap(S, P, R, N, b=0.8, max_overlap_pct=1.0, phases=[0, 0.25, 0.5]):
    """
    Check if a configuration has acceptable overlap across multiple phases.

    Returns:
        dict with validation results
    """
    max_sun_planet_overlap = 0
    max_planet_planet_overlap = 0

    for phase in phases:
        try:
            sun_poly, planet_polys, ring_poly = get_polygons(S, P, R, N, b, phase)
        except Exception as e:
            return {'valid': False, 'error': str(e)}

        if sun_poly is None:
            return {'valid': False, 'error': 'Invalid sun polygon'}

        sun_area = sun_poly.area

        # Check sun-planet overlap
        for i, planet_poly in enumerate(planet_polys):
            if planet_poly is None:
                continue
            try:
                intersection = sun_poly.intersection(planet_poly)
                if not intersection.is_empty:
                    overlap_pct = (intersection.area / sun_area) * 100
                    max_sun_planet_overlap = max(max_sun_planet_overlap, overlap_pct)
            except:
                pass

        # Check planet-planet overlap
        for i in range(len(planet_polys)):
            for j in range(i + 1, len(planet_polys)):
                if planet_polys[i] is None or planet_polys[j] is None:
                    continue
                try:
                    intersection = planet_polys[i].intersection(planet_polys[j])
                    if not intersection.is_empty:
                        smaller_area = min(planet_polys[i].area, planet_polys[j].area)
                        overlap_pct = (intersection.area / smaller_area) * 100
                        max_planet_planet_overlap = max(max_planet_planet_overlap, overlap_pct)
                except:
                    pass

    valid = max_sun_planet_overlap <= max_overlap_pct and max_planet_planet_overlap <= max_overlap_pct

    return {
        'valid': valid,
        'sun_planet_overlap_pct': max_sun_planet_overlap,
        'planet_planet_overlap_pct': max_planet_planet_overlap,
        'S': S, 'P': P, 'R': R, 'N': N, 'b': b,
        'ratio': (R + S) / S,
    }


def search_valid_configs(target_ratio=5.0, tolerance=1.0, S_range=(4, 15), N_range=(2, 5),
                         b_values=[0.5, 0.6, 0.7, 0.8], max_overlap_pct=1.0):
    """
    Search for valid gear configurations.
    """
    valid_configs = []

    print("=" * 70)
    print(f"Searching for VALID configs: ratio {target_ratio}+/-{tolerance}, max_overlap={max_overlap_pct}%")
    print("=" * 70)

    for S in range(S_range[0], S_range[1] + 1):
        for ratio_offset in np.linspace(-tolerance, tolerance, 21):
            test_ratio = target_ratio + ratio_offset
            if test_ratio <= 1:
                continue

            R_ideal = S * (test_ratio - 1)
            R = round(R_ideal)

            P = (R - S) / 2
            if P != int(P) or P < 2:
                continue
            P = int(P)

            if R != S + 2 * P:
                continue

            actual_ratio = (R + S) / S
            if abs(actual_ratio - target_ratio) > tolerance:
                continue

            for N in range(N_range[0], N_range[1] + 1):
                for b in b_values:
                    result = check_overlap(S, P, R, N, b, max_overlap_pct)

                    if result['valid']:
                        valid_configs.append(result)
                        print(f"  VALID: S={S:2d}, P={P:2d}, R={R:2d}, N={N}, b={b}, "
                              f"ratio={actual_ratio:.2f}:1, "
                              f"overlap={result['sun_planet_overlap_pct']:.2f}%")

    # Remove duplicates and sort
    seen = set()
    unique = []
    for c in valid_configs:
        key = (c['S'], c['P'], c['R'], c['N'], c['b'])
        if key not in seen:
            seen.add(key)
            unique.append(c)

    unique.sort(key=lambda x: (abs(x['ratio'] - target_ratio), -x['N'], x['sun_planet_overlap_pct']))

    print("\n" + "=" * 70)
    print(f"Found {len(unique)} unique valid configurations")
    print("=" * 70)

    return unique


def print_best_configs(configs, top_n=20):
    """Print the best configurations."""
    print(f"\nTOP {top_n} CONFIGURATIONS (sorted by ratio closeness to 5:1, then by N):")
    print("-" * 80)
    print(f"{'S':>3} {'P':>3} {'R':>3} {'N':>2} {'b':>4} {'Ratio':>7} {'Sun-Planet%':>12} {'Planet-Planet%':>14}")
    print("-" * 80)

    for c in configs[:top_n]:
        print(f"{c['S']:>3} {c['P']:>3} {c['R']:>3} {c['N']:>2} {c['b']:>4.1f} {c['ratio']:>6.2f}:1 "
              f"{c['sun_planet_overlap_pct']:>11.2f}% {c['planet_planet_overlap_pct']:>13.2f}%")


if __name__ == "__main__":
    # Search with strict overlap requirement
    valid = search_valid_configs(
        target_ratio=5.0,
        tolerance=1.0,
        S_range=(4, 15),
        N_range=(2, 5),
        b_values=[0.3, 0.4, 0.5, 0.6, 0.7],  # Lower b values = shorter teeth
        max_overlap_pct=0.5  # Strict: less than 0.5% overlap
    )

    print_best_configs(valid, top_n=30)

    # Also specifically test S=4 to S=7 with various b values
    print("\n\n" + "=" * 70)
    print("SPECIFIC TEST: S=4 to S=7 with different b values")
    print("=" * 70)

    for S in [4, 5, 6, 7]:
        P = int(1.5 * S) if S % 2 == 0 else int(1.5 * S + 0.5)
        if S == 5:
            P = 8  # Round up for 5.2:1 ratio
        if S == 7:
            P = 10  # Round down for ~4.86:1 ratio

        R = S + 2 * P
        ratio = (R + S) / S

        print(f"\nS={S}, P={P}, R={R}, target_ratio={ratio:.2f}:1:")

        for b in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
            for N in [2, 3, 4]:
                result = check_overlap(S, P, R, N, b, max_overlap_pct=1.0)
                status = "VALID" if result['valid'] else "INVALID"
                print(f"  N={N}, b={b}: {status:8s} (sun-planet={result['sun_planet_overlap_pct']:.2f}%)")
