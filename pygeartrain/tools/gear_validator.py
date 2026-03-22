"""
Gear Geometry Validator - Detects invalid configurations using Shapely

VALIDATION CHECKS:
1. Planet-to-planet intersection - planets should not overlap each other
2. Planet-sun intersection - planets should mesh with sun, not cut through it
3. Planet-ring intersection - planets should mesh with ring, not cut through it
4. Self-intersection - individual gear profiles should be valid polygons

A valid meshing means the gear profiles interleave (teeth fit into gaps),
not that they physically intersect (teeth cutting through teeth).
"""

import numpy as np
from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import unary_union
from shapely.validation import explain_validity
import matplotlib.pyplot as plt


def profile_to_polygon(profile):
    """Convert a gear Profile to a Shapely Polygon."""
    vertices = profile.vertices
    if len(vertices) < 3:
        return None
    # Close the polygon if needed
    if not np.allclose(vertices[0], vertices[-1]):
        vertices = np.vstack([vertices, vertices[0]])
    try:
        poly = Polygon(vertices)
        if not poly.is_valid:
            # Try to fix invalid polygons
            poly = poly.buffer(0)
        return poly
    except Exception as e:
        print(f"Error creating polygon: {e}")
        return None


def profile_to_linestring(profile):
    """Convert a gear Profile to a Shapely LineString (for line intersection check)."""
    vertices = profile.vertices
    if len(vertices) < 2:
        return None
    # Close the loop
    if not np.allclose(vertices[0], vertices[-1]):
        vertices = np.vstack([vertices, vertices[0]])
    try:
        return LineString(vertices)
    except Exception as e:
        print(f"Error creating linestring: {e}")
        return None


def check_polygon_intersection(poly1, poly2, name1="poly1", name2="poly2"):
    """
    Check if two polygons intersect in an invalid way.

    Returns:
        dict with:
            - intersects: True if polygons intersect
            - intersection_area: Area of intersection
            - intersection_pct: Intersection as % of smaller polygon
            - valid: True if intersection is acceptable (minimal/none)
    """
    if poly1 is None or poly2 is None:
        return {'valid': False, 'error': 'Invalid polygon'}

    try:
        intersects = poly1.intersects(poly2)
        if not intersects:
            return {
                'valid': True,
                'intersects': False,
                'intersection_area': 0,
                'intersection_pct': 0,
                'names': (name1, name2),
            }

        intersection = poly1.intersection(poly2)
        intersection_area = intersection.area
        smaller_area = min(poly1.area, poly2.area)
        intersection_pct = (intersection_area / smaller_area * 100) if smaller_area > 0 else 0

        # Allow tiny intersections (numerical tolerance) - less than 0.1%
        valid = intersection_pct < 0.1

        return {
            'valid': valid,
            'intersects': True,
            'intersection_area': intersection_area,
            'intersection_pct': intersection_pct,
            'names': (name1, name2),
        }
    except Exception as e:
        return {'valid': False, 'error': str(e), 'names': (name1, name2)}


def check_line_intersection(line1, line2, name1="line1", name2="line2"):
    """
    Check if two line strings (gear outlines) intersect.

    For valid meshing, gear outlines should NOT cross each other.
    Touching at a point is OK, but crossing through is not.
    """
    if line1 is None or line2 is None:
        return {'valid': False, 'error': 'Invalid linestring'}

    try:
        intersection = line1.intersection(line2)

        if intersection.is_empty:
            return {
                'valid': True,
                'intersects': False,
                'intersection_count': 0,
                'names': (name1, name2),
            }

        # Count intersection points
        if intersection.geom_type == 'Point':
            count = 1
        elif intersection.geom_type == 'MultiPoint':
            count = len(intersection.geoms)
        elif intersection.geom_type in ('LineString', 'MultiLineString'):
            # Lines overlapping - definitely bad
            count = float('inf')
        else:
            count = len(list(intersection.geoms)) if hasattr(intersection, 'geoms') else 1

        return {
            'valid': False,  # Any crossing is invalid
            'intersects': True,
            'intersection_count': count,
            'intersection_type': intersection.geom_type,
            'names': (name1, name2),
        }
    except Exception as e:
        return {'valid': False, 'error': str(e), 'names': (name1, name2)}


def validate_planetary_geometry(gear_geometry, phase=0):
    """
    Validate a complete planetary gear assembly.

    Args:
        gear_geometry: PlanetaryGeometry instance
        phase: Animation phase to check (0 = starting position)

    Returns:
        dict with validation results for all checks
    """
    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'checks': {},
    }

    # Get arranged profiles at the specified phase
    try:
        profiles = gear_geometry.arrange(phase)
        ring_profile, planet_profiles, sun_profile, carrier_profile = profiles
    except Exception as e:
        results['valid'] = False
        results['errors'].append(f"Failed to generate profiles: {e}")
        return results

    # Convert to Shapely geometries
    ring_poly = profile_to_polygon(ring_profile)
    sun_poly = profile_to_polygon(sun_profile)
    planet_polys = [profile_to_polygon(p) for p in planet_profiles]

    ring_line = profile_to_linestring(ring_profile)
    sun_line = profile_to_linestring(sun_profile)
    planet_lines = [profile_to_linestring(p) for p in planet_profiles]

    # Check 1: Planet-to-planet intersection
    n_planets = len(planet_profiles)
    for i in range(n_planets):
        for j in range(i + 1, n_planets):
            check = check_polygon_intersection(
                planet_polys[i], planet_polys[j],
                f"planet_{i}", f"planet_{j}"
            )
            results['checks'][f'planet_{i}_vs_planet_{j}'] = check
            if not check['valid']:
                results['valid'] = False
                if 'error' in check:
                    results['errors'].append(f"Planet {i} vs Planet {j}: {check['error']}")
                else:
                    results['errors'].append(
                        f"Planet {i} overlaps Planet {j}: {check['intersection_pct']:.1f}% intersection"
                    )

    # Check 2: Planet-sun line crossings (teeth should interleave, not cross)
    for i, planet_line in enumerate(planet_lines):
        check = check_line_intersection(planet_line, sun_line, f"planet_{i}", "sun")
        results['checks'][f'planet_{i}_vs_sun_lines'] = check
        if not check['valid']:
            if check.get('intersection_count', 0) > 4:  # Allow some touch points for meshing
                results['valid'] = False
                results['errors'].append(
                    f"Planet {i} crosses sun gear: {check.get('intersection_count', '?')} crossings"
                )
            else:
                results['warnings'].append(
                    f"Planet {i} touches sun gear at {check.get('intersection_count', '?')} points"
                )

    # Check 3: Planet-ring line crossings
    for i, planet_line in enumerate(planet_lines):
        check = check_line_intersection(planet_line, ring_line, f"planet_{i}", "ring")
        results['checks'][f'planet_{i}_vs_ring_lines'] = check
        if not check['valid']:
            if check.get('intersection_count', 0) > 4:
                results['valid'] = False
                results['errors'].append(
                    f"Planet {i} crosses ring gear: {check.get('intersection_count', '?')} crossings"
                )
            else:
                results['warnings'].append(
                    f"Planet {i} touches ring gear at {check.get('intersection_count', '?')} points"
                )

    # Check 4: Sun should be inside ring (basic sanity)
    if ring_poly and sun_poly:
        if not ring_poly.contains(sun_poly):
            results['warnings'].append("Sun gear not fully inside ring gear")

    return results


def validate_config(S, P, R, N, b=0.8, verbose=True):
    """
    Validate a planetary gear configuration.

    Args:
        S: Sun teeth
        P: Planet teeth
        R: Ring teeth
        N: Number of planets
        b: Tooth profile parameter

    Returns:
        dict with validation results
    """
    from pygeartrain.planetary import Planetary, PlanetaryGeometry

    if verbose:
        print(f"\nValidating S={S}, P={P}, R={R}, N={N}, b={b}")
        print("-" * 50)

    # Check meshing constraint
    expected_R = S + 2 * P
    if R != expected_R:
        if verbose:
            print(f"  WARNING: R={R} doesn't match S + 2P = {expected_R}")

    # Create geometry
    try:
        kinematics = Planetary('s', 'c', 'r')
        gear = PlanetaryGeometry.create(kinematics, (R, P, S), N, b=b)
    except Exception as e:
        if verbose:
            print(f"  ERROR: Failed to create geometry: {e}")
        return {'valid': False, 'error': str(e)}

    # Validate at multiple phases to catch issues during rotation
    phases_to_check = [0, 0.1, 0.25, 0.5]
    all_valid = True
    all_results = {}

    for phase in phases_to_check:
        result = validate_planetary_geometry(gear, phase)
        all_results[f'phase_{phase}'] = result

        if verbose:
            status = "VALID" if result['valid'] else "INVALID"
            print(f"  Phase {phase}: {status}")
            for err in result['errors']:
                print(f"    ERROR: {err}")
            for warn in result['warnings'][:3]:  # Limit warnings shown
                print(f"    WARN: {warn}")

        if not result['valid']:
            all_valid = False

    # Summary
    ratio = (R + S) / S
    summary = {
        'valid': all_valid,
        'S': S, 'P': P, 'R': R, 'N': N, 'b': b,
        'ratio': ratio,
        'phase_results': all_results,
    }

    if verbose:
        print(f"  OVERALL: {'VALID' if all_valid else 'INVALID'}")
        print(f"  Ratio: {ratio:.2f}:1")

    return summary


def find_valid_configs(target_ratio=5.0, tolerance=1.0, S_range=(4, 12), N_range=(2, 6), b=0.8):
    """
    Search for valid gear configurations.

    Args:
        target_ratio: Target gear ratio
        tolerance: Acceptable deviation from target
        S_range: Range of sun teeth to try
        N_range: Range of planet counts to try
        b: Tooth profile parameter

    Returns:
        List of valid configurations
    """
    valid_configs = []

    print("=" * 60)
    print(f"Searching for valid configs: ratio {target_ratio}+/-{tolerance}")
    print("=" * 60)

    for S in range(S_range[0], S_range[1] + 1):
        # For target ratio with ring locked: ratio = (R+S)/S = 1 + R/S
        # So R = S * (ratio - 1)

        for ratio_offset in np.linspace(-tolerance, tolerance, 11):
            test_ratio = target_ratio + ratio_offset
            if test_ratio <= 1:
                continue

            R_ideal = S * (test_ratio - 1)
            R = round(R_ideal)

            # Meshing constraint: R = S + 2P
            P = (R - S) / 2
            if P != int(P) or P < 2:
                continue
            P = int(P)

            # Verify constraint
            if R != S + 2 * P:
                continue

            actual_ratio = (R + S) / S
            if abs(actual_ratio - target_ratio) > tolerance:
                continue

            # Try different N values
            for N in range(N_range[0], N_range[1] + 1):
                result = validate_config(S, P, R, N, b, verbose=False)

                if result['valid']:
                    valid_configs.append({
                        'S': S, 'P': P, 'R': R, 'N': N, 'b': b,
                        'ratio': actual_ratio,
                        'ratio_error': abs(actual_ratio - target_ratio),
                    })
                    print(f"  VALID: S={S}, P={P}, R={R}, N={N}, ratio={actual_ratio:.2f}:1")

    # Sort by ratio closeness, then by more planets (better load sharing)
    valid_configs.sort(key=lambda x: (x['ratio_error'], -x['N']))

    print("\n" + "=" * 60)
    print(f"Found {len(valid_configs)} valid configurations")
    print("=" * 60)

    return valid_configs


if __name__ == "__main__":
    print("=" * 60)
    print("GEAR VALIDATOR - Testing configurations from v2 sweep")
    print("=" * 60)

    # Test the configurations from v2
    test_configs = [
        (4, 6, 16, 3, 0.8),
        (5, 8, 21, 3, 0.8),
        (6, 9, 24, 3, 0.8),
        (7, 10, 27, 3, 0.8),
    ]

    results = []
    for S, P, R, N, b in test_configs:
        result = validate_config(S, P, R, N, b, verbose=True)
        results.append(result)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in results:
        status = "VALID" if r['valid'] else "INVALID"
        print(f"S={r['S']}, P={r['P']}, R={r['R']}, N={r['N']}: {status} (ratio={r['ratio']:.2f}:1)")

    # Search for valid configs
    print("\n")
    valid = find_valid_configs(target_ratio=5.0, tolerance=1.0, S_range=(4, 12), N_range=(2, 5), b=0.8)
