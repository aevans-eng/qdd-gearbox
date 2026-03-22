"""
Herringbone Gear with more visible V-pattern
=============================================
Uses higher helix angle to make the herringbone pattern clearly visible.
"""

import numpy as np
from pathlib import Path
import cadquery as cq
import math

INPUT_DIR = Path(__file__).parent.parent / "design_log" / "cad_export" / "Gearset_A_S4_P6_R16_N4"
OUTPUT_DIR = Path(__file__).parent / "output"
GEAR_THICKNESS = 10.0
HELIX_ANGLE_DEG = 45.0  # Aggressive angle to clearly show herringbone V-pattern


def load_xyz_points(filepath: Path) -> np.ndarray:
    points = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                coords = line.split()
                if len(coords) >= 2:
                    x, y = float(coords[0]), float(coords[1])
                    points.append((x, y))
    return np.array(points)


def rotate_profile(points_2d: np.ndarray, angle_rad: float) -> list:
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    rotated = []
    for x, y in points_2d:
        x_new = x * cos_a - y * sin_a
        y_new = x * sin_a + y * cos_a
        rotated.append((x_new, y_new))
    return rotated


def generate_herringbone(name: str, input_file: Path, output_file: Path,
                          helix_angle_deg: float, thickness: float, helix_dir: int):
    """Generate herringbone gear with clear V-pattern."""
    print(f"\nGenerating {name} with {helix_angle_deg}° helix...")

    points_2d = load_xyz_points(input_file)
    print(f"  Loaded {len(points_2d)} points")

    radii = np.sqrt(points_2d[:, 0]**2 + points_2d[:, 1]**2)
    ref_radius = radii.max()

    z_bot = -thickness / 2
    z_mid = 0.0
    z_top = thickness / 2

    # Calculate twist: use reference radius for consistent angle across gear
    tan_helix = math.tan(math.radians(helix_angle_deg))

    # For herringbone: bottom and top twist in opposite directions from center
    # twist = z * tan(helix) / radius
    twist_bot = (abs(z_bot) * tan_helix / ref_radius) * (-1) * helix_dir  # negative Z direction
    twist_top = (abs(z_top) * tan_helix / ref_radius) * (1) * helix_dir   # positive Z direction

    print(f"  Ref radius: {ref_radius:.2f}mm")
    print(f"  Twist: bot={math.degrees(twist_bot):.1f}°, top={math.degrees(twist_top):.1f}°")

    # Create profiles at each level
    profile_bot = rotate_profile(points_2d, twist_bot)
    profile_mid = list(map(tuple, points_2d))  # No rotation at center
    profile_top = rotate_profile(points_2d, twist_top)

    # Close profiles
    for p in [profile_bot, profile_mid, profile_top]:
        if p[0] != p[-1]:
            p.append(p[0])

    # Build herringbone as two separate lofts joined at center
    print("  Building bottom half...")
    bottom_half = (
        cq.Workplane("XY", origin=(0, 0, z_bot))
        .spline(profile_bot).close()
        .workplane(offset=thickness/2)
        .spline(profile_mid).close()
        .loft(ruled=True)
    )

    print("  Building top half...")
    top_half = (
        cq.Workplane("XY", origin=(0, 0, z_mid))
        .spline(profile_mid).close()
        .workplane(offset=thickness/2)
        .spline(profile_top).close()
        .loft(ruled=True)
    )

    print("  Joining halves...")
    solid = bottom_half.union(top_half)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(solid, str(output_file))
    print(f"  Saved: {output_file} ({output_file.stat().st_size:,} bytes)")

    return solid


def main():
    print("=" * 60)
    print(f"Herringbone Generator (Helix angle: {HELIX_ANGLE_DEG}°)")
    print("=" * 60)

    gears = [
        ('sun', INPUT_DIR / 'sun_z0.txt', 1),
        ('planet', INPUT_DIR / 'planet_z0.txt', -1),
        ('ring', INPUT_DIR / 'ring_z0.txt', -1),
    ]

    for name, input_file, helix_dir in gears:
        if input_file.exists():
            output_file = OUTPUT_DIR / f'{name}_herringbone_v2.step'
            generate_herringbone(name, input_file, output_file,
                                  HELIX_ANGLE_DEG, GEAR_THICKNESS, helix_dir)

    print("\nDone!")


if __name__ == "__main__":
    main()
