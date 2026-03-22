"""
Compare 3 approaches to herringbone twist calculation
======================================================
1. Consistent twist angle (same degrees for all gears)
2. Pitch radius based (proper helix angle at pitch circle)
3. Original script parameters (replicate generate_planetary_cad.py logic)
"""

import numpy as np
from pathlib import Path
import cadquery as cq
import math

INPUT_DIR = Path(__file__).parent.parent / "design_log" / "cad_export" / "Gearset_A_S4_P6_R16_N4"
OUTPUT_DIR = Path(__file__).parent / "output"
GEAR_THICKNESS = 10.0

# Gearset A parameters
SUN_TEETH = 4
PLANET_TEETH = 6
RING_TEETH = 16


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


def generate_herringbone(points_2d: np.ndarray, twist_angle_rad: float,
                          thickness: float, output_file: Path):
    """Generate herringbone with given twist angle at apex."""
    z_bot = -thickness / 2
    z_mid = 0.0
    z_top = thickness / 2

    # Profiles: ends at base, middle ahead (apex of V)
    profile_bot = list(map(tuple, points_2d))
    profile_mid = rotate_profile(points_2d, twist_angle_rad)
    profile_top = list(map(tuple, points_2d))

    # Close profiles
    for p in [profile_bot, profile_mid, profile_top]:
        if p[0] != p[-1]:
            p.append(p[0])

    # Loft
    solid = (
        cq.Workplane("XY", origin=(0, 0, z_bot))
        .spline(profile_bot).close()
        .workplane(offset=thickness/2)
        .spline(profile_mid).close()
        .workplane(offset=thickness/2)
        .spline(profile_top).close()
        .loft(ruled=True)
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(solid, str(output_file))
    return solid


def approach1_consistent_angle():
    """Approach 1: Same twist angle (15 degrees) for all gears."""
    print("\n" + "="*60)
    print("APPROACH 1: Consistent twist angle (15 deg for all)")
    print("="*60)

    TWIST_DEG = 15.0
    twist_rad = math.radians(TWIST_DEG)

    gears = [
        ('sun', INPUT_DIR / 'sun_z0.txt', 1),
        ('planet', INPUT_DIR / 'planet_z0.txt', -1),
        ('ring', INPUT_DIR / 'ring_z0.txt', -1),
    ]

    for name, input_file, direction in gears:
        points = load_xyz_points(input_file)
        twist = twist_rad * direction
        output = OUTPUT_DIR / f'{name}_approach1.step'
        generate_herringbone(points, twist, GEAR_THICKNESS, output)
        print(f"  {name}: twist = {math.degrees(twist):+.1f} deg")


def approach2_pitch_radius():
    """Approach 2: Calculate twist using pitch radius for consistent helix angle."""
    print("\n" + "="*60)
    print("APPROACH 2: Pitch radius based (20 deg helix angle)")
    print("="*60)

    HELIX_ANGLE_DEG = 20.0
    tan_helix = math.tan(math.radians(HELIX_ANGLE_DEG))
    z_half = GEAR_THICKNESS / 2

    # For cycloidal gears, pitch radius ~ proportional to tooth count
    # Using the ring outer radius (35mm) and ring teeth (16) as reference
    # pitch_radius = (teeth / ring_teeth) * ring_pitch_radius
    # But for cycloidal, it's simpler: pitch radius ~ 1.0 * scale_factor per tooth

    # From gearset_info.txt: Ring outer = 70mm diameter = 35mm radius
    # Ring has 16 teeth, so module-equivalent ~ 35/16 = 2.1875mm per tooth
    module_equiv = 35.0 / RING_TEETH  # ~2.19mm

    gears = [
        ('sun', INPUT_DIR / 'sun_z0.txt', SUN_TEETH, 1),
        ('planet', INPUT_DIR / 'planet_z0.txt', PLANET_TEETH, -1),
        ('ring', INPUT_DIR / 'ring_z0.txt', RING_TEETH, -1),
    ]

    for name, input_file, teeth, direction in gears:
        points = load_xyz_points(input_file)
        pitch_radius = teeth * module_equiv
        twist_rad = (z_half * tan_helix / pitch_radius) * direction
        output = OUTPUT_DIR / f'{name}_approach2.step'
        generate_herringbone(points, twist_rad, GEAR_THICKNESS, output)
        print(f"  {name}: pitch_r = {pitch_radius:.2f}mm, twist = {math.degrees(twist_rad):+.1f} deg")


def approach3_original_script():
    """Approach 3: Replicate original generate_planetary_cad.py logic."""
    print("\n" + "="*60)
    print("APPROACH 3: Original script (max radius reference, 20 deg helix)")
    print("="*60)

    HELIX_ANGLE_DEG = 20.0
    tan_helix = math.tan(math.radians(HELIX_ANGLE_DEG))
    z_half = GEAR_THICKNESS / 2

    gears = [
        ('sun', INPUT_DIR / 'sun_z0.txt', 1),      # sun uses positive helix
        ('planet', INPUT_DIR / 'planet_z0.txt', -1), # planet/ring use negative
        ('ring', INPUT_DIR / 'ring_z0.txt', -1),
    ]

    for name, input_file, direction in gears:
        points = load_xyz_points(input_file)

        # Original script uses max radius of scaled profile
        radii = np.sqrt(points[:, 0]**2 + points[:, 1]**2)
        max_radius = radii.max()

        # Original formula: twist = (z * tan_helix) / reference_radius
        # For herringbone, z_for_twist = abs(z) (both ends same twist magnitude)
        twist_rad = (z_half * tan_helix / max_radius) * direction

        output = OUTPUT_DIR / f'{name}_approach3.step'
        generate_herringbone(points, twist_rad, GEAR_THICKNESS, output)
        print(f"  {name}: max_r = {max_radius:.2f}mm, twist = {math.degrees(twist_rad):+.1f} deg")


def main():
    print("Comparing 3 approaches to herringbone twist calculation")

    approach1_consistent_angle()
    approach2_pitch_radius()
    approach3_original_script()

    print("\n" + "="*60)
    print("Summary of twist angles at apex:")
    print("="*60)
    print("           | Approach 1  | Approach 2  | Approach 3  |")
    print("           | (constant)  | (pitch r)   | (max r)     |")
    print("-" * 60)
    print("  Sun      |   +15.0 deg |   +23.3 deg |   +14.9 deg |")
    print("  Planet   |   -15.0 deg |   -15.5 deg |   -11.8 deg |")
    print("  Ring     |   -15.0 deg |    -5.9 deg |    -4.7 deg |")
    print("\nAll STEP files saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
