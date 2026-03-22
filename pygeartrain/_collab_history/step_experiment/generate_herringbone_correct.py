"""
Correct Herringbone Gear Generator
==================================
The middle profile must be AHEAD in phase (rotated more than the ends).
This creates the V-pattern where teeth go one direction then reverse.

Bottom (0°) -> Middle (+θ) -> Top (0°)
         ↗               ↘
    helix one way    helix other way
"""

import numpy as np
from pathlib import Path
import cadquery as cq
import math

INPUT_DIR = Path(__file__).parent.parent / "design_log" / "cad_export" / "Gearset_A_S4_P6_R16_N4"
OUTPUT_DIR = Path(__file__).parent / "output"
GEAR_THICKNESS = 10.0
HELIX_ANGLE_DEG = 30.0  # Helix angle


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
    """
    Generate proper herringbone gear.

    The key insight: middle profile is AHEAD in rotation.
    - Bottom: 0° rotation
    - Middle: +twist_angle (apex of V)
    - Top: 0° rotation

    This makes teeth go one way (bottom→middle) then reverse (middle→top).
    """
    print(f"\nGenerating {name}...")

    points_2d = load_xyz_points(input_file)
    print(f"  Loaded {len(points_2d)} points")

    radii = np.sqrt(points_2d[:, 0]**2 + points_2d[:, 1]**2)
    ref_radius = radii.max()

    z_bot = -thickness / 2
    z_mid = 0.0
    z_top = thickness / 2

    # Calculate twist for the middle (apex) profile
    # twist = (z_half * tan(helix)) / radius
    tan_helix = math.tan(math.radians(helix_angle_deg))
    twist_angle = (abs(z_bot) * tan_helix / ref_radius) * helix_dir

    print(f"  Ref radius: {ref_radius:.2f}mm")
    print(f"  Middle profile twist: {math.degrees(twist_angle):.1f}° (apex of V)")

    # Create profiles:
    # - Bottom and Top: NO rotation (base position)
    # - Middle: rotated AHEAD by twist_angle
    profile_bot = list(map(tuple, points_2d))  # 0° - base
    profile_mid = rotate_profile(points_2d, twist_angle)  # +θ - ahead (apex)
    profile_top = list(map(tuple, points_2d))  # 0° - back to base

    # Close profiles
    for p in [profile_bot, profile_mid, profile_top]:
        if p[0] != p[-1]:
            p.append(p[0])

    # Build herringbone by lofting through all 3 profiles
    print("  Lofting bottom -> middle -> top...")

    try:
        solid = (
            cq.Workplane("XY", origin=(0, 0, z_bot))
            .spline(profile_bot).close()
            .workplane(offset=thickness/2)
            .spline(profile_mid).close()
            .workplane(offset=thickness/2)
            .spline(profile_top).close()
            .loft(ruled=True)
        )
    except Exception as e:
        print(f"  3-profile loft failed: {e}")
        print("  Trying 2-part loft...")

        bottom_half = (
            cq.Workplane("XY", origin=(0, 0, z_bot))
            .spline(profile_bot).close()
            .workplane(offset=thickness/2)
            .spline(profile_mid).close()
            .loft(ruled=True)
        )

        top_half = (
            cq.Workplane("XY", origin=(0, 0, z_mid))
            .spline(profile_mid).close()
            .workplane(offset=thickness/2)
            .spline(profile_top).close()
            .loft(ruled=True)
        )

        solid = bottom_half.union(top_half)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(solid, str(output_file))
    print(f"  Saved: {output_file} ({output_file.stat().st_size:,} bytes)")

    return solid


def main():
    print("=" * 60)
    print("Correct Herringbone Generator")
    print("Middle profile AHEAD in phase (apex of V)")
    print("=" * 60)

    gears = [
        ('sun', INPUT_DIR / 'sun_z0.txt', 1),
        ('planet', INPUT_DIR / 'planet_z0.txt', -1),
        ('ring', INPUT_DIR / 'ring_z0.txt', -1),
    ]

    for name, input_file, helix_dir in gears:
        if input_file.exists():
            output_file = OUTPUT_DIR / f'{name}_herringbone_v3.step'
            generate_herringbone(name, input_file, output_file,
                                 HELIX_ANGLE_DEG, GEAR_THICKNESS, helix_dir)

    print("\nDone!")


if __name__ == "__main__":
    main()
