"""
STEP File Verification Script
=============================
Validates generated STEP files by checking geometry, creating renders,
and producing a verification report.
"""

import numpy as np
from pathlib import Path
import cadquery as cq
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent / "output"
RENDERS_DIR = OUTPUT_DIR / "renders"

# Expected values from gearset_info.txt
EXPECTED = {
    'sun': {
        'max_radius': (8, 12),   # Expected range in mm
        'min_radius': (6, 10),
        'thickness': 10.0,
    },
    'planet': {
        'max_radius': (12, 16),
        'min_radius': (8, 12),
        'thickness': 10.0,
    },
    'ring': {
        'max_radius': (34, 36),  # Should be ~35mm (70mm diameter / 2)
        'min_radius': (28, 34),
        'thickness': 10.0,
    },
}


def load_step_file(filepath: Path):
    """Load a STEP file and return the CadQuery object."""
    return cq.importers.importStep(str(filepath))


def get_bounding_box(solid):
    """Get the bounding box of a solid."""
    bb = solid.val().BoundingBox()
    return {
        'xmin': bb.xmin, 'xmax': bb.xmax,
        'ymin': bb.ymin, 'ymax': bb.ymax,
        'zmin': bb.zmin, 'zmax': bb.zmax,
        'width': bb.xmax - bb.xmin,
        'height': bb.ymax - bb.ymin,
        'depth': bb.zmax - bb.zmin,
    }


def verify_geometry(name: str, solid, expected: dict) -> dict:
    """Verify the geometry of a loaded solid against expected values."""
    results = {
        'name': name,
        'checks': [],
        'all_passed': True
    }

    # Get bounding box
    bb = get_bounding_box(solid)

    # Check 1: Bounding box radius (X/Y should match expected radius range)
    actual_radius_x = max(abs(bb['xmin']), abs(bb['xmax']))
    actual_radius_y = max(abs(bb['ymin']), abs(bb['ymax']))
    actual_max_radius = max(actual_radius_x, actual_radius_y)

    exp_min, exp_max = expected['max_radius']
    radius_ok = exp_min <= actual_max_radius <= exp_max
    results['checks'].append({
        'name': 'Max radius',
        'expected': f"{exp_min}-{exp_max} mm",
        'actual': f"{actual_max_radius:.2f} mm",
        'passed': radius_ok
    })
    if not radius_ok:
        results['all_passed'] = False

    # Check 2: Thickness (Z dimension)
    actual_thickness = bb['depth']
    expected_thickness = expected['thickness']
    thickness_tolerance = 0.1  # 0.1mm tolerance
    thickness_ok = abs(actual_thickness - expected_thickness) < thickness_tolerance
    results['checks'].append({
        'name': 'Thickness',
        'expected': f"{expected_thickness} mm",
        'actual': f"{actual_thickness:.2f} mm",
        'passed': thickness_ok
    })
    if not thickness_ok:
        results['all_passed'] = False

    # Check 3: Solid is valid (has faces)
    faces = solid.faces().vals()
    has_faces = len(faces) >= 2  # At least top and bottom
    results['checks'].append({
        'name': 'Has faces',
        'expected': '>= 2',
        'actual': str(len(faces)),
        'passed': has_faces
    })
    if not has_faces:
        results['all_passed'] = False

    # Check 4: Symmetry about Z=0 (mid-plane extrusion)
    z_symmetric = abs(bb['zmin'] + bb['zmax']) < 0.1
    results['checks'].append({
        'name': 'Z-symmetric',
        'expected': 'centered at Z=0',
        'actual': f"Z: {bb['zmin']:.2f} to {bb['zmax']:.2f}",
        'passed': z_symmetric
    })
    if not z_symmetric:
        results['all_passed'] = False

    # Store bounding box for report
    results['bounding_box'] = bb
    results['face_count'] = len(faces)

    return results


def render_gear(name: str, solid, output_path: Path):
    """
    Render the gear to a PNG file using matplotlib (simple top-down view).
    This is a fallback since CadQuery's VTK viewer may not work headlessly.
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon
        from matplotlib.collections import PatchCollection

        # Get the top face edges for visualization
        bb = get_bounding_box(solid)

        # Create a simple visualization using the bounding box
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))

        # Draw a circle representing the approximate shape
        theta = np.linspace(0, 2*np.pi, 100)
        r_outer = max(abs(bb['xmax']), abs(bb['ymax']))
        r_inner = min(abs(bb['xmin']), abs(bb['ymin'])) * 0.7  # Approximate inner

        x_outer = r_outer * np.cos(theta)
        y_outer = r_outer * np.sin(theta)

        ax.plot(x_outer, y_outer, 'b-', linewidth=2, label='Outer bound')
        ax.fill(x_outer, y_outer, alpha=0.3, color='blue')

        # Add info text
        ax.set_title(f"{name.upper()} Gear\n"
                     f"Radius: {r_outer:.1f}mm, Thickness: {bb['depth']:.1f}mm",
                     fontsize=14)
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linewidth=0.5)
        ax.axvline(x=0, color='k', linewidth=0.5)

        # Add bounding box info
        info_text = (f"Bounding Box:\n"
                     f"  X: {bb['xmin']:.1f} to {bb['xmax']:.1f}\n"
                     f"  Y: {bb['ymin']:.1f} to {bb['ymax']:.1f}\n"
                     f"  Z: {bb['zmin']:.1f} to {bb['zmax']:.1f}")
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
                fontsize=9, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return True
    except Exception as e:
        print(f"  Warning: Could not render {name}: {e}")
        return False


def generate_verification_report(results: list, output_path: Path):
    """Generate a text verification report."""
    lines = [
        "=" * 70,
        "STEP File Verification Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        "",
    ]

    all_passed = True
    for r in results:
        status = "PASS" if r['all_passed'] else "FAIL"
        if not r['all_passed']:
            all_passed = False

        lines.append(f"\n{r['name'].upper()} Gear [{status}]")
        lines.append("-" * 40)

        for check in r['checks']:
            check_status = "OK" if check['passed'] else "FAIL"
            lines.append(f"  [{check_status}] {check['name']}: {check['actual']} (expected: {check['expected']})")

        lines.append(f"  Face count: {r['face_count']}")
        bb = r['bounding_box']
        lines.append(f"  Dimensions: {bb['width']:.2f} x {bb['height']:.2f} x {bb['depth']:.2f} mm")

    lines.append("")
    lines.append("=" * 70)
    overall = "ALL CHECKS PASSED" if all_passed else "SOME CHECKS FAILED"
    lines.append(f"Overall Result: {overall}")
    lines.append("=" * 70)

    lines.append("")
    lines.append("External Verification:")
    lines.append("  - Open STEP files in 3DEXPERIENCE to verify import")
    lines.append("  - Online viewer: https://3dviewer.net/ (drag & drop STEP files)")
    lines.append("  - FreeCAD: File > Import > select .step file")

    output_path.write_text("\n".join(lines))
    return all_passed


def main():
    print("=" * 60)
    print("STEP File Verification")
    print("=" * 60)

    RENDERS_DIR.mkdir(parents=True, exist_ok=True)

    gears = ['sun', 'planet', 'ring']
    results = []

    for name in gears:
        step_file = OUTPUT_DIR / f"{name}.step"
        if not step_file.exists():
            print(f"\nWARNING: {step_file} not found, skipping")
            continue

        print(f"\nVerifying {name}...")
        print(f"  Loading: {step_file}")

        # Load the STEP file
        solid = load_step_file(step_file)
        print(f"  Loaded successfully")

        # Verify geometry
        result = verify_geometry(name, solid, EXPECTED[name])

        # Print results
        for check in result['checks']:
            status = "OK" if check['passed'] else "FAIL"
            print(f"  [{status}] {check['name']}: {check['actual']}")

        # Render to PNG
        render_path = RENDERS_DIR / f"{name}_verification.png"
        if render_gear(name, solid, render_path):
            print(f"  Rendered: {render_path}")

        results.append(result)

    # Generate report
    report_path = OUTPUT_DIR / "verification_report.txt"
    all_passed = generate_verification_report(results, report_path)

    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    for r in results:
        status = "PASS" if r['all_passed'] else "FAIL"
        print(f"  {r['name']:8} [{status}]")

    print(f"\nReport saved: {report_path}")
    print(f"Renders saved: {RENDERS_DIR}")

    if all_passed:
        print("\nAll verification checks PASSED!")
    else:
        print("\nSome verification checks FAILED - see report for details")

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
