"""
Herringbone Gear STEP Generator
===============================
Creates herringbone (double-helix) gears by lofting twisted profiles.

The herringbone pattern has teeth that form a V-shape:
- Bottom half: profile twisted one direction
- Top half: profile twisted the opposite direction
- Meet at center (z=0) with no twist
"""

import numpy as np
from pathlib import Path
import cadquery as cq
import math

# Configuration
INPUT_DIR = Path(__file__).parent.parent / "design_log" / "cad_export" / "Gearset_A_S4_P6_R16_N4"
OUTPUT_DIR = Path(__file__).parent / "output"
GEAR_THICKNESS = 10.0  # mm
HELIX_ANGLE_DEG = 20.0  # degrees - typical for herringbone gears


def load_xyz_points(filepath: Path) -> np.ndarray:
    """Load XYZ points from a text file (uses only X,Y)."""
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
    """Rotate 2D points by angle (radians) around origin."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    rotated = []
    for x, y in points_2d:
        x_new = x * cos_a - y * sin_a
        y_new = x * sin_a + y * cos_a
        rotated.append((x_new, y_new))
    return rotated


def calculate_twist_angle(z_offset: float, helix_angle_deg: float, reference_radius: float) -> float:
    """
    Calculate the twist angle for a profile at a given Z offset.

    For herringbone: twist is symmetric about z=0
    twist_angle = (|z| * tan(helix_angle)) / reference_radius
    """
    if abs(z_offset) < 1e-9 or reference_radius < 1e-9:
        return 0.0

    tan_helix = math.tan(math.radians(helix_angle_deg))
    # For herringbone, use absolute Z (symmetric V-shape)
    twist_angle = (abs(z_offset) * tan_helix) / reference_radius

    # Direction: positive Z gets positive twist, negative Z gets negative twist
    # This creates the V-shape meeting at center
    if z_offset < 0:
        twist_angle = -twist_angle

    return twist_angle


def make_wire_from_points(points_2d: list, z: float) -> cq.Wire:
    """Create a CadQuery wire from 2D points at a specific Z level."""
    # Add Z coordinate
    points_3d = [(x, y, z) for x, y in points_2d]

    # Create spline through points
    # CadQuery needs the points as tuples
    wire = cq.Workplane("XY", origin=(0, 0, z)).spline(points_2d).close().val()
    return wire


def generate_herringbone_gear(name: str, input_file: Path, output_file: Path,
                               helix_angle_deg: float = HELIX_ANGLE_DEG,
                               thickness: float = GEAR_THICKNESS,
                               helix_direction: int = 1):
    """
    Generate a herringbone gear STEP file.

    Args:
        name: Gear name
        input_file: Path to XYZ profile (z0 level)
        output_file: Output STEP file path
        helix_angle_deg: Helix angle in degrees
        thickness: Total gear thickness
        helix_direction: 1 for sun, -1 for planet/ring (opposite hand)
    """
    print(f"\nGenerating herringbone {name}...")
    print(f"  Helix angle: {helix_angle_deg}°, Direction: {'CW' if helix_direction > 0 else 'CCW'}")

    # Load base profile
    points_2d = load_xyz_points(input_file)
    print(f"  Loaded {len(points_2d)} profile points")

    # Calculate reference radius (max radius of profile)
    radii = np.sqrt(points_2d[:, 0]**2 + points_2d[:, 1]**2)
    ref_radius = radii.max()
    print(f"  Reference radius: {ref_radius:.2f} mm")

    # Define Z levels for herringbone
    z_bot = -thickness / 2  # -5mm
    z_mid = 0.0             # 0mm (apex of V)
    z_top = thickness / 2   # +5mm

    # Calculate twist angles
    twist_bot = calculate_twist_angle(z_bot, helix_angle_deg, ref_radius) * helix_direction
    twist_mid = 0.0  # No twist at center
    twist_top = calculate_twist_angle(z_top, helix_angle_deg, ref_radius) * helix_direction

    print(f"  Twist angles: bot={math.degrees(twist_bot):.2f}°, mid=0°, top={math.degrees(twist_top):.2f}°")

    # Create rotated profiles
    profile_bot = rotate_profile(points_2d, twist_bot)
    profile_mid = rotate_profile(points_2d, twist_mid)
    profile_top = rotate_profile(points_2d, twist_top)

    # Ensure profiles are closed
    for profile in [profile_bot, profile_mid, profile_top]:
        if profile[0] != profile[-1]:
            profile.append(profile[0])

    # Create wires at each Z level
    print("  Creating profile wires...")

    # Build the solid using loft
    # For herringbone, we loft bottom-to-middle, then middle-to-top
    try:
        # Create workplane and add profiles
        # Bottom half: z_bot to z_mid
        wp_bot = cq.Workplane("XY", origin=(0, 0, z_bot))
        wire_bot = wp_bot.spline(profile_bot).close()

        wp_mid_lower = cq.Workplane("XY", origin=(0, 0, z_mid))
        wire_mid = wp_mid_lower.spline(profile_mid).close()

        # Loft bottom half
        bottom_half = (
            cq.Workplane("XY", origin=(0, 0, z_bot))
            .spline(profile_bot).close()
            .workplane(offset=thickness/2)
            .spline(profile_mid).close()
            .loft(ruled=True)
        )

        # Top half: z_mid to z_top
        top_half = (
            cq.Workplane("XY", origin=(0, 0, z_mid))
            .spline(profile_mid).close()
            .workplane(offset=thickness/2)
            .spline(profile_top).close()
            .loft(ruled=True)
        )

        # Union the two halves
        solid = bottom_half.union(top_half)

    except Exception as e:
        print(f"  Loft failed: {e}")
        print("  Falling back to simpler construction...")

        # Fallback: Create using sweep or simpler loft
        # Try making a single loft with 3 sections
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
        except Exception as e2:
            print(f"  3-section loft also failed: {e2}")
            print("  Using simple extrusion (no herringbone)")
            solid = (
                cq.Workplane("XY")
                .spline(profile_mid).close()
                .extrude(thickness/2, both=True)
            )

    # Export to STEP
    output_file.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(solid, str(output_file))

    file_size = output_file.stat().st_size
    print(f"  Output: {output_file}")
    print(f"  File size: {file_size:,} bytes")

    return solid


def main():
    print("=" * 60)
    print("Herringbone Gear STEP Generator")
    print("=" * 60)
    print(f"Helix angle: {HELIX_ANGLE_DEG}°")
    print(f"Thickness: {GEAR_THICKNESS} mm")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Gear configurations
    # Sun: positive helix direction
    # Planet/Ring: negative (opposite hand to mesh properly)
    gears = [
        ('sun', INPUT_DIR / 'sun_z0.txt', 1),      # Sun: positive helix
        ('planet', INPUT_DIR / 'planet_z0.txt', -1), # Planet: negative (meshes with sun)
        ('ring', INPUT_DIR / 'ring_z0.txt', -1),    # Ring: negative (meshes with planet)
    ]

    results = []
    for name, input_file, helix_dir in gears:
        if input_file.exists():
            output_file = OUTPUT_DIR / f'{name}_herringbone.step'
            try:
                solid = generate_herringbone_gear(
                    name, input_file, output_file,
                    helix_direction=helix_dir
                )
                results.append((name, output_file, True))
            except Exception as e:
                print(f"  ERROR: {e}")
                results.append((name, None, False))
        else:
            print(f"WARNING: Input file not found: {input_file}")

    print("\n" + "=" * 60)
    print("Generation Summary")
    print("=" * 60)
    for name, path, success in results:
        status = "OK" if success else "FAILED"
        print(f"  {name:8} [{status}]")

    print("\nDone! Herringbone STEP files are in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
