"""
STEP File Generator for Planetary Gear Profiles
================================================
Reads XYZ point files and generates STEP solids using CadQuery.

Uses the same OpenCASCADE kernel as 3DEXPERIENCE/CATIA for maximum compatibility.
"""

import numpy as np
from pathlib import Path
import cadquery as cq

# Configuration
INPUT_DIR = Path(__file__).parent.parent / "design_log" / "cad_export" / "Gearset_A_S4_P6_R16_N4"
OUTPUT_DIR = Path(__file__).parent / "output"
GEAR_THICKNESS = 10.0  # mm (from gearset_info.txt)


def load_xyz_points(filepath: Path) -> np.ndarray:
    """Load XYZ points from a space-delimited text file."""
    points = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                coords = line.split()
                if len(coords) >= 2:  # At minimum need X, Y
                    x, y = float(coords[0]), float(coords[1])
                    z = float(coords[2]) if len(coords) >= 3 else 0.0
                    points.append((x, y, z))
    return np.array(points)


def points_to_wire(points: np.ndarray) -> cq.Workplane:
    """
    Convert 2D points to a closed CadQuery wire using a spline.
    Uses only X, Y coordinates (ignores Z from input).
    """
    # Extract just X, Y for the profile
    xy_points = [(p[0], p[1]) for p in points]

    # Check if the profile is closed (first point ~ last point)
    first = np.array(xy_points[0])
    last = np.array(xy_points[-1])
    distance = np.linalg.norm(first - last)

    if distance > 0.001:  # Not closed, need to close it
        print(f"  Warning: Profile not closed (gap: {distance:.4f}mm). Closing automatically.")
        xy_points.append(xy_points[0])

    # Create a spline through the points
    # CadQuery's spline expects a list of tuples
    wire = cq.Workplane("XY").spline(xy_points, includeCurrent=False).close()

    return wire


def generate_gear_step(name: str, input_file: Path, output_file: Path, thickness: float = GEAR_THICKNESS):
    """
    Generate a STEP file from an XYZ profile file.

    Args:
        name: Gear name (for logging)
        input_file: Path to XYZ point file
        output_file: Path for output STEP file
        thickness: Extrusion thickness in mm

    Returns:
        dict with generation metadata
    """
    print(f"\nGenerating {name}...")
    print(f"  Input: {input_file}")

    # Load points
    points = load_xyz_points(input_file)
    print(f"  Loaded {len(points)} points")

    # Calculate profile metrics
    radii = np.sqrt(points[:, 0]**2 + points[:, 1]**2)
    min_radius = radii.min()
    max_radius = radii.max()
    print(f"  Radius range: {min_radius:.2f} - {max_radius:.2f} mm")

    # Create the profile wire
    try:
        profile = points_to_wire(points)
    except Exception as e:
        print(f"  ERROR creating spline: {e}")
        # Fallback: try with fewer points (subsampling)
        print(f"  Trying with subsampled points...")
        step = max(1, len(points) // 200)  # Target ~200 points max
        subsampled = points[::step]
        # Ensure we include the last point for closure
        if not np.allclose(subsampled[-1], points[-1]):
            subsampled = np.vstack([subsampled, points[-1]])
        profile = points_to_wire(subsampled)
        print(f"  Using {len(subsampled)} subsampled points")

    # Extrude to create solid
    # Use mid-plane extrusion (symmetric about Z=0)
    solid = profile.extrude(thickness / 2, both=True)

    # Export to STEP
    output_file.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(solid, str(output_file))

    file_size = output_file.stat().st_size
    print(f"  Output: {output_file}")
    print(f"  File size: {file_size:,} bytes")

    # Return metadata for verification
    return {
        'name': name,
        'input_file': str(input_file),
        'output_file': str(output_file),
        'point_count': len(points),
        'min_radius': min_radius,
        'max_radius': max_radius,
        'thickness': thickness,
        'file_size': file_size,
        'solid': solid  # Keep for verification
    }


def generate_all_gears():
    """Generate STEP files for all gears in the gearset."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    gears = [
        ('sun', INPUT_DIR / 'sun_z0.txt'),
        ('planet', INPUT_DIR / 'planet_z0.txt'),
        ('ring', INPUT_DIR / 'ring_z0.txt'),
    ]

    results = []
    for name, input_file in gears:
        if input_file.exists():
            output_file = OUTPUT_DIR / f'{name}.step'
            result = generate_gear_step(name, input_file, output_file)
            results.append(result)
        else:
            print(f"WARNING: Input file not found: {input_file}")

    return results


def main():
    print("=" * 60)
    print("STEP File Generator for Planetary Gears")
    print("=" * 60)
    print(f"Input directory: {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")

    results = generate_all_gears()

    print("\n" + "=" * 60)
    print("Generation Summary")
    print("=" * 60)
    for r in results:
        print(f"  {r['name']:8} | {r['point_count']:4} pts | "
              f"r={r['max_radius']:.1f}mm | {r['file_size']:,} bytes")

    print("\nDone! STEP files are in:", OUTPUT_DIR)
    return results


if __name__ == "__main__":
    main()
