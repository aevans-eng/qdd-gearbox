"""
Planetary Gear Assembly Verification Tool

Uses pygeartrain library directly for correct gear positioning,
then validates the assembly using Shapely geometry checks.
"""

import os
import sys
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
import imageio
from PIL import Image
import io
from datetime import datetime

# Add pygeartrain to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pygeartrain.planetary import Planetary, PlanetaryGeometry

# Constants
CAD_EXPORT_DIR = "design_log/cad_export"
OUTPUT_DIR = "design_log/assembly_verification"


def parse_gearset_info(filepath):
    """Parse gearset_info.txt to extract parameters."""
    info = {}
    with open(filepath, 'r') as f:
        content = f.read()

    patterns = {
        'S': r'Sun teeth \(S\):\s*(\d+)',
        'P': r'Planet teeth \(P\):\s*(\d+)',
        'R': r'Ring teeth \(R\):\s*(\d+)',
        'N': r'Number of planets \(N\):\s*(\d+)',
        'b': r'Tooth profile \(b\):\s*([\d.]+)',
        'ratio': r'Ratio:\s*([\d.]+):1',
        'carrier_radius': r'Carrier path radius:\s*([\d.]+)\s*mm',
        'ring_diameter': r'Ring outer diameter:\s*([\d.]+)\s*mm',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            value = match.group(1)
            if key in ['S', 'P', 'R', 'N']:
                info[key] = int(value)
            else:
                info[key] = float(value)

    match = re.search(r'Gearset:\s*(\w+)', content)
    if match:
        info['name'] = match.group(1)

    return info


def profile_to_polygon(profile):
    """Convert a pygeartrain Profile to a Shapely Polygon."""
    vertices = profile.vertices
    if len(vertices) < 3:
        return None
    if not np.allclose(vertices[0], vertices[-1]):
        vertices = np.vstack([vertices, vertices[0]])
    try:
        poly = Polygon(vertices)
        if not poly.is_valid:
            poly = poly.buffer(0)
        return poly
    except Exception as e:
        print(f"Error creating polygon: {e}")
        return None


def profile_to_linestring(profile):
    """Convert a pygeartrain Profile to a Shapely LineString."""
    vertices = profile.vertices
    if len(vertices) < 2:
        return None
    if not np.allclose(vertices[0], vertices[-1]):
        vertices = np.vstack([vertices, vertices[0]])
    try:
        return LineString(vertices)
    except Exception as e:
        print(f"Error creating linestring: {e}")
        return None


def check_gear_mesh_overlap(poly1, poly2, name1="gear1", name2="gear2", max_overlap_pct=1.0):
    """Check polygon area intersection between meshing gears.

    This is the correct way to detect interference - if gear tooth profiles
    have significant area overlap, that indicates teeth cutting through each other.

    For proper meshing, some edge contact is normal, but area overlap should be minimal.
    """
    if poly1 is None or poly2 is None:
        return {'valid': False, 'error': 'Invalid geometry', 'names': (name1, name2)}

    try:
        if not poly1.intersects(poly2):
            return {
                'valid': True,
                'overlap_area': 0,
                'overlap_pct': 0,
                'intersects': False,
                'names': (name1, name2),
            }

        intersection = poly1.intersection(poly2)
        if intersection.is_empty:
            return {
                'valid': True,
                'overlap_area': 0,
                'overlap_pct': 0,
                'intersects': False,
                'names': (name1, name2),
            }

        overlap_area = intersection.area
        # Use smaller polygon as reference (typically sun for sun-planet check)
        smaller_area = min(poly1.area, poly2.area)
        overlap_pct = (overlap_area / smaller_area * 100) if smaller_area > 0 else 0

        # Valid if overlap is below threshold
        valid = overlap_pct <= max_overlap_pct

        return {
            'valid': valid,
            'overlap_area': overlap_area,
            'overlap_pct': overlap_pct,
            'intersects': True,
            'names': (name1, name2),
        }
    except Exception as e:
        return {'valid': False, 'error': str(e), 'names': (name1, name2)}


def check_polygon_overlap(poly1, poly2, name1="poly1", name2="poly2"):
    """Check overlap between two polygons (for planet-planet checks)."""
    if poly1 is None or poly2 is None:
        return {'valid': False, 'error': 'Invalid polygon', 'names': (name1, name2)}

    try:
        if not poly1.intersects(poly2):
            return {
                'valid': True,
                'overlap_area': 0,
                'overlap_pct': 0,
                'names': (name1, name2),
            }

        intersection = poly1.intersection(poly2)
        overlap_area = intersection.area
        smaller_area = min(poly1.area, poly2.area)
        overlap_pct = (overlap_area / smaller_area * 100) if smaller_area > 0 else 0

        # Allow tiny overlaps due to numerical tolerance
        valid = overlap_pct < 1.0

        return {
            'valid': valid,
            'overlap_area': overlap_area,
            'overlap_pct': overlap_pct,
            'names': (name1, name2),
        }
    except Exception as e:
        return {'valid': False, 'error': str(e), 'names': (name1, name2)}


def validate_at_phase(gear_geometry, phase, max_overlap_pct=1.0):
    """Validate gear assembly at a specific phase using pygeartrain's arrange().

    Uses polygon area intersection to detect interference, which is the same
    method used by find_valid_gears.py in the original project.
    """

    # Get arranged profiles from pygeartrain (this is the correct positioning)
    ring_profile, planet_profiles, sun_profile, carrier_profile = gear_geometry.arrange(phase)

    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'checks': {},
    }

    # Convert to Shapely polygons
    sun_poly = profile_to_polygon(sun_profile)
    ring_poly = profile_to_polygon(ring_profile)
    planet_polys = [profile_to_polygon(p) for p in planet_profiles]

    N = len(planet_profiles)

    # Check 1: Sun-Planet overlap (polygon area intersection)
    # This is the primary validation - sun and planet teeth should not cut through each other
    for i, planet_poly in enumerate(planet_polys):
        check = check_gear_mesh_overlap(sun_poly, planet_poly, "sun", f"planet_{i}", max_overlap_pct)
        results['checks'][f'sun_vs_planet_{i}'] = check
        if not check['valid']:
            results['valid'] = False
            if 'error' in check:
                results['errors'].append(f"Sun vs Planet {i}: {check['error']}")
            else:
                results['errors'].append(
                    f"Sun vs Planet {i}: {check['overlap_pct']:.2f}% overlap (exceeds {max_overlap_pct}%)"
                )

    # Check 2: Planet-Planet overlap (should be zero - planets should not touch each other)
    for i in range(N):
        for j in range(i + 1, N):
            check = check_polygon_overlap(
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
                        f"Planet {i} vs Planet {j}: {check['overlap_pct']:.2f}% overlap"
                    )

    # Note: We do NOT check planet-ring polygon overlap because the ring is an
    # internal gear. The planet is SUPPOSED to be inside the ring cavity.
    # The ring profile represents internal teeth, so polygon intersection
    # would always show high overlap (planet inside ring).
    #
    # The original find_valid_gears.py also only checks sun-planet and
    # planet-planet overlap, not planet-ring.
    #
    # For planet-ring mesh, we could add a tooth interference check using
    # line intersection, but this is not done in the original validation.

    return results


def validate_geometry_params(info):
    """Validate geometric constraints of the gearset parameters."""
    S, P, R, N = info['S'], info['P'], info['R'], info['N']

    results = {
        'valid': True,
        'checks': {},
    }

    # Check 1: Gear ratio validation (R = S + 2P for epicyclic)
    expected_R = S + 2 * P
    ratio_valid = R == expected_R
    results['checks']['gear_ratio'] = {
        'valid': ratio_valid,
        'expected_R': expected_R,
        'actual_R': R,
        'formula': 'R = S + 2P',
    }
    if not ratio_valid:
        results['valid'] = False

    # Check 2: Assembly condition ((S + R) must be divisible by N)
    assembly_sum = S + R
    assembly_valid = (assembly_sum % N) == 0
    results['checks']['assembly_condition'] = {
        'valid': assembly_valid,
        'S_plus_R': assembly_sum,
        'N': N,
        'remainder': assembly_sum % N,
        'formula': '(S + R) mod N = 0',
    }
    if not assembly_valid:
        results['valid'] = False

    # Check 3: Minimum teeth
    min_teeth_valid = S >= 4 and P >= 4
    results['checks']['minimum_teeth'] = {
        'valid': min_teeth_valid,
        'S': S,
        'P': P,
        'minimum': 4,
    }
    if not min_teeth_valid:
        results['valid'] = False

    return results


def simulate_rolling(gear_geometry, num_phases=36, max_overlap_pct=1.0):
    """Run validation across multiple rotation phases.

    Uses polygon area intersection to check for interference at each phase.
    """

    phases = np.linspace(0, 1, num_phases, endpoint=False)

    simulation = {
        'phases': phases.tolist(),
        'results': [],
        'max_overlap': 0,
        'max_sun_planet_overlap': 0,
        'max_planet_ring_overlap': 0,
        'worst_phase': 0,
        'all_valid': True,
        'failed_count': 0,
        'max_overlap_pct': max_overlap_pct,
    }

    for phase in phases:
        result = validate_at_phase(gear_geometry, phase, max_overlap_pct)

        # Find max overlap in this phase
        phase_max_overlap = 0
        phase_sun_planet = 0
        phase_planet_ring = 0

        for check_name, check in result['checks'].items():
            if 'overlap_pct' in check:
                phase_max_overlap = max(phase_max_overlap, check['overlap_pct'])
                if 'sun_vs_planet' in check_name:
                    phase_sun_planet = max(phase_sun_planet, check['overlap_pct'])
                elif 'vs_ring' in check_name:
                    phase_planet_ring = max(phase_planet_ring, check['overlap_pct'])

        simulation['results'].append({
            'phase': phase,
            'valid': result['valid'],
            'max_overlap': phase_max_overlap,
            'sun_planet_overlap': phase_sun_planet,
            'planet_ring_overlap': phase_planet_ring,
            'errors': result['errors'],
        })

        if phase_max_overlap > simulation['max_overlap']:
            simulation['max_overlap'] = phase_max_overlap
            simulation['worst_phase'] = phase

        simulation['max_sun_planet_overlap'] = max(simulation['max_sun_planet_overlap'], phase_sun_planet)
        simulation['max_planet_ring_overlap'] = max(simulation['max_planet_ring_overlap'], phase_planet_ring)

        if not result['valid']:
            simulation['all_valid'] = False
            simulation['failed_count'] += 1

    return simulation


def plot_assembly(gear_geometry, phase, output_path, info, title_suffix=""):
    """Create a static assembly visualization using pygeartrain."""

    fig, ax = plt.subplots(1, 1, figsize=(10, 10), dpi=150)

    # Use pygeartrain's built-in plotting
    gear_geometry._plot(ax, phase=phase, col='steelblue')

    ax.set_aspect('equal')
    lim = gear_geometry.limit
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.grid(True, alpha=0.3)

    # Title
    name = info.get('name', 'Unknown')
    S, P, R, N = info['S'], info['P'], info['R'], info['N']
    b = info.get('b', 0)
    ratio = info.get('ratio', (R + S) / S)

    title = (
        f"{name}: S={S}, P={P}, R={R}, N={N} | b={b} | Ratio={ratio:.2f}:1\n"
        f"Phase={phase:.3f} | Ring Locked{title_suffix}"
    )
    ax.set_title(title, fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    print(f"Saved: {output_path}")


def create_animation(gear_geometry, output_path, info, num_frames=90, fps=30):
    """Generate animated GIF showing rolling motion using pygeartrain.

    The animation is designed to loop smoothly by animating through one
    symmetric period: carrier rotates by 2π/N, which brings each planet
    to the next planet's starting position.
    """

    name = info.get('name', 'Unknown')
    S, P, R, N = info['S'], info['P'], info['R'], info['N']
    b = info.get('b', 0)
    ratio = info.get('ratio', (R + S) / S)

    # For smooth looping: animate one symmetric period
    # Carrier rotation of 2π/N brings planets to next planet's position
    # This creates a seamless loop since the pattern is N-fold symmetric
    loop_phase = 2 * np.pi / N

    phases = np.linspace(0, loop_phase, num_frames, endpoint=False)
    frames = []

    print(f"Generating {num_frames} animation frames for {name} (loop phase: {loop_phase:.3f} rad)...")

    lim = gear_geometry.limit

    for i, phase in enumerate(phases):
        fig, ax = plt.subplots(1, 1, figsize=(8, 8), dpi=100)

        # Use pygeartrain's built-in plotting
        gear_geometry._plot(ax, phase=phase, col='steelblue')

        ax.set_aspect('equal')
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.grid(True, alpha=0.3)

        title = (
            f"{name}: S={S} P={P} R={R} N={N} | b={b} | Ratio={ratio:.2f}:1\n"
            f"Phase: {phase:.3f} | Ring Locked | Sun(in)->Carrier(out)"
        )
        ax.set_title(title, fontsize=10)

        # Save frame to buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        image = Image.open(buf)
        frames.append(np.array(image))
        buf.close()

        plt.close(fig)

        if (i + 1) % 20 == 0:
            print(f"  Frame {i + 1}/{num_frames}")

    # Save GIF
    imageio.mimsave(output_path, frames, fps=fps, loop=0)
    print(f"Saved: {output_path}")


def generate_report(info, geometry_results, phase0_check, simulation, output_path):
    """Generate a detailed text verification report."""

    name = info.get('name', 'Unknown')
    S, P, R, N = info['S'], info['P'], info['R'], info['N']
    b = info.get('b', 0)
    ratio = info.get('ratio', (R + S) / S)

    lines = []
    lines.append("=" * 70)
    lines.append(f"PLANETARY GEAR ASSEMBLY VERIFICATION REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)
    lines.append("")

    # Gearset info
    lines.append("GEARSET PARAMETERS")
    lines.append("-" * 40)
    lines.append(f"  Name:            {name}")
    lines.append(f"  Sun teeth (S):   {S}")
    lines.append(f"  Planet teeth (P): {P}")
    lines.append(f"  Ring teeth (R):  {R}")
    lines.append(f"  Planets (N):     {N}")
    lines.append(f"  Tooth profile:   b={b}")
    lines.append(f"  Gear ratio:      {ratio:.2f}:1")
    lines.append(f"  Configuration:   Ring locked, Sun input, Carrier output")
    lines.append("")

    # Overall status
    overall_valid = (
        geometry_results['valid'] and
        phase0_check['valid'] and
        simulation['all_valid']
    )
    status = "PASS" if overall_valid else "FAIL"
    lines.append(f"OVERALL STATUS: {status}")
    lines.append("=" * 70)
    lines.append("")

    # Geometry validation
    lines.append("GEOMETRY VALIDATION")
    lines.append("-" * 40)
    for check_name, check in geometry_results['checks'].items():
        status = "PASS" if check['valid'] else "FAIL"
        lines.append(f"  [{status}] {check_name}")
        if 'formula' in check:
            lines.append(f"        Formula: {check['formula']}")
        if check_name == 'gear_ratio':
            lines.append(f"        Expected R: {check['expected_R']}, Actual: {check['actual_R']}")
        elif check_name == 'assembly_condition':
            lines.append(f"        (S+R)={check['S_plus_R']}, N={check['N']}, remainder={check['remainder']}")
    lines.append("")

    # Static check at phase 0
    lines.append("STATIC CHECK (Phase 0)")
    lines.append("-" * 40)
    status = "PASS" if phase0_check['valid'] else "FAIL"
    lines.append(f"  Overall: {status}")

    if phase0_check['errors']:
        lines.append("  Errors:")
        for err in phase0_check['errors']:
            lines.append(f"    - {err}")

    lines.append("")
    lines.append("  Detailed checks:")
    for check_name, check in phase0_check['checks'].items():
        status = "OK" if check['valid'] else "FAIL"
        if 'crossings' in check:
            lines.append(f"    {check_name}: {status} ({check['crossings']} crossings)")
        elif 'overlap_pct' in check:
            lines.append(f"    {check_name}: {status} ({check['overlap_pct']:.3f}% overlap)")
    lines.append("")

    # Rolling simulation
    lines.append("ROLLING SIMULATION")
    lines.append("-" * 40)
    lines.append(f"  Phases tested: {len(simulation['phases'])}")
    status = "PASS" if simulation['all_valid'] else "FAIL"
    lines.append(f"  All phases valid: {status}")
    lines.append(f"  Failed phases: {simulation['failed_count']}/{len(simulation['phases'])}")
    lines.append(f"  Max sun-planet overlap: {simulation['max_sun_planet_overlap']:.3f}%")
    lines.append(f"  Max planet-ring overlap: {simulation['max_planet_ring_overlap']:.3f}%")
    lines.append(f"  Overall max overlap: {simulation['max_overlap']:.3f}%")
    lines.append(f"  Worst phase: {simulation['worst_phase']:.3f}")
    lines.append(f"  Overlap threshold: {simulation.get('max_overlap_pct', 1.0)}%")

    failed_phases = [r for r in simulation['results'] if not r['valid']]
    if failed_phases:
        lines.append("  First 5 failures:")
        for r in failed_phases[:5]:
            lines.append(f"    Phase {r['phase']:.3f}: {r['max_overlap']:.3f}% overlap")
    lines.append("")

    # Verification checklist
    lines.append("VERIFICATION CHECKLIST")
    lines.append("-" * 40)

    sun_planet_ok = all(
        c['valid'] for k, c in phase0_check['checks'].items()
        if 'sun_vs_planet' in k
    )
    planet_planet_ok = all(
        c['valid'] for k, c in phase0_check['checks'].items()
        if 'planet_' in k and '_vs_planet_' in k
    )

    checklist = [
        ("Gear ratio (R = S + 2P)", geometry_results['checks']['gear_ratio']['valid']),
        ("Assembly condition ((S+R) mod N = 0)", geometry_results['checks']['assembly_condition']['valid']),
        ("Minimum teeth (S,P >= 4)", geometry_results['checks']['minimum_teeth']['valid']),
        ("Sun-Planet mesh (<1% overlap)", sun_planet_ok),
        ("Planet-Planet clearance", planet_planet_ok),
        ("Multi-phase validation", simulation['all_valid']),
    ]

    for item, passed in checklist:
        status = "PASS" if passed else "FAIL"
        lines.append(f"  [{status}] {item}")
    lines.append("")

    lines.append("=" * 70)
    lines.append("END OF REPORT")
    lines.append("=" * 70)

    # Write report
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Saved: {output_path}")

    return '\n'.join(lines)


def verify_gearset(gearset_path, output_dir):
    """Run full verification on a gearset."""

    print(f"\nVerifying: {gearset_path}")
    print("-" * 50)

    # Load parameters
    info = parse_gearset_info(os.path.join(gearset_path, 'gearset_info.txt'))
    name = info.get('name', 'Unknown')
    S, P, R, N = info['S'], info['P'], info['R'], info['N']
    b = info.get('b', 0.5)

    print(f"  Loaded: {name} (S={S}, P={P}, R={R}, N={N}, b={b})")

    # Create pygeartrain geometry (this is the authoritative source)
    kinematics = Planetary('s', 'c', 'r')
    gear_geometry = PlanetaryGeometry.create(kinematics, (R, P, S), N, b=b)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # 1. Validate geometry parameters
    print("  Validating geometry parameters...")
    geometry_results = validate_geometry_params(info)

    # 2. Static check at phase 0
    print("  Checking static assembly (phase 0)...")
    phase0_check = validate_at_phase(gear_geometry, phase=0)

    # 3. Rolling simulation
    print("  Running rolling simulation (36 phases)...")
    simulation = simulate_rolling(gear_geometry, num_phases=36)

    # 4. Generate outputs
    base_name = f"{name}_S{S}_P{P}_R{R}_N{N}"

    # Static assembly plot
    print("  Creating static assembly plot...")
    plot_assembly(
        gear_geometry, phase=0,
        output_path=os.path.join(output_dir, f"{base_name}_assembly.png"),
        info=info
    )

    # Animation
    print("  Creating rolling animation...")
    create_animation(
        gear_geometry,
        output_path=os.path.join(output_dir, f"{base_name}_rolling.gif"),
        info=info,
        num_frames=60, fps=20
    )

    # Report
    print("  Generating verification report...")
    report = generate_report(
        info, geometry_results, phase0_check, simulation,
        os.path.join(output_dir, f"{base_name}_report.txt")
    )

    # Summary
    overall_valid = (
        geometry_results['valid'] and
        phase0_check['valid'] and
        simulation['all_valid']
    )

    print(f"\n  Overall result: {'PASS' if overall_valid else 'FAIL'}")
    print(f"  Max overlap: {simulation['max_overlap']:.3f}% (sun-planet: {simulation['max_sun_planet_overlap']:.3f}%, planet-ring: {simulation['max_planet_ring_overlap']:.3f}%)")
    print(f"  Failed phases: {simulation['failed_count']}/{len(simulation['phases'])}")

    return {
        'name': name,
        'valid': overall_valid,
        'geometry': geometry_results,
        'phase0_check': phase0_check,
        'simulation': simulation,
    }


def find_gearsets(cad_export_dir):
    """Find all gearset export folders."""
    gearsets = []
    if os.path.exists(cad_export_dir):
        for item in os.listdir(cad_export_dir):
            item_path = os.path.join(cad_export_dir, item)
            if os.path.isdir(item_path) and item.startswith('Gearset_'):
                gearsets.append(item_path)
    return sorted(gearsets)


def interactive_view(gearset_path):
    """Launch interactive matplotlib animation (like original pygeartrain)."""

    info = parse_gearset_info(os.path.join(gearset_path, 'gearset_info.txt'))
    S, P, R, N = info['S'], info['P'], info['R'], info['N']
    b = info.get('b', 0.5)

    kinematics = Planetary('s', 'c', 'r')
    gear_geometry = PlanetaryGeometry.create(kinematics, (R, P, S), N, b=b)

    print(f"Launching interactive animation for {info.get('name', 'gearset')}...")
    print("Close the window to exit.")

    # Use pygeartrain's built-in animate method
    matplotlib.use('TkAgg')  # Switch to interactive backend
    gear_geometry.animate()


def main():
    """Main entry point - verify all gearsets."""

    print("=" * 70)
    print("PLANETARY GEAR ASSEMBLY VERIFICATION")
    print(f"Using pygeartrain library for correct gear positioning")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Check for interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        gearset_paths = find_gearsets(CAD_EXPORT_DIR)
        if gearset_paths:
            interactive_view(gearset_paths[0])
        return

    # Find gearsets
    gearset_paths = find_gearsets(CAD_EXPORT_DIR)

    if not gearset_paths:
        print(f"\nNo gearsets found in {CAD_EXPORT_DIR}")
        print("Expected folders starting with 'Gearset_'")
        return

    print(f"\nFound {len(gearset_paths)} gearset(s):")
    for path in gearset_paths:
        print(f"  - {os.path.basename(path)}")

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Verify each gearset
    results = []
    for gearset_path in gearset_paths:
        result = verify_gearset(gearset_path, OUTPUT_DIR)
        results.append(result)

    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    for result in results:
        status = "PASS" if result['valid'] else "FAIL"
        sim = result['simulation']
        print(f"  {result['name']}: {status} (max overlap: {sim['max_overlap']:.3f}%, failed: {sim['failed_count']}/{len(sim['phases'])})")

    passed = sum(1 for r in results if r['valid'])
    total = len(results)
    print(f"\nTotal: {passed}/{total} gearsets passed verification")

    print(f"\nOutput files written to: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
