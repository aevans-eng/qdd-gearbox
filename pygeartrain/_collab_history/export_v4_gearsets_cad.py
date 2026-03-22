"""
Export v4 gearsets to XYZ point files for CAD import
Creates files compatible with 3DEXPERIENCE / SOLIDWORKS
"""

import numpy as np
import os
import math
from pygeartrain.planetary import Planetary, PlanetaryGeometry

# --- Configuration ---
TARGET_RING_DIAMETER_MM = 70.0   # Outer diameter of ring gear in mm
GEAR_THICKNESS_MM = 10.0         # Face width (Z-axis)
HELIX_ANGLE_DEGREES = 0.0        # 0 = spur gears (no helix)
CLOSE_POINT_TOLERANCE = 1e-7

KINEMATICS = Planetary('s', 'c', 'r')  # Ring locked, Sun in, Carrier out

# V4 Gearsets
GEARSETS = [
    {"S": 4, "P": 6, "R": 16, "N": 4, "b": 0.35, "name": "Gearset_A"},
    {"S": 6, "P": 9, "R": 24, "N": 3, "b": 0.35, "name": "Gearset_B"},
]


def save_curve_to_file(points_3d, filepath):
    """Save 3D points to text file for CAD import."""
    if points_3d is None or len(points_3d) < 3:
        print(f"Warning: Not enough points for {filepath}")
        return

    # Ensure curve is closed
    first_point = points_3d[0, :2]
    last_point = points_3d[-1, :2]
    if np.linalg.norm(last_point - first_point) > CLOSE_POINT_TOLERANCE:
        points_3d = np.vstack((points_3d, points_3d[0]))

    np.savetxt(filepath, points_3d, fmt='%.8f', delimiter=' ')
    print(f"  Exported: {filepath} ({len(points_3d)} points)")


def export_gear_profile(profile, gear_name, scale_factor, thickness, output_dir):
    """Export a single gear profile to XYZ files."""
    if profile is None or len(profile.vertices) < 3:
        print(f"Warning: Invalid profile for {gear_name}")
        return

    # Scale to mm
    vertices_2d = profile.vertices * scale_factor

    # Create 3D points at different Z levels
    z_levels = {
        "z0": 0.0,
        "z_top": thickness / 2.0,
        "z_bot": -thickness / 2.0,
    }

    for z_name, z_val in z_levels.items():
        points_3d = np.column_stack([
            vertices_2d[:, 0],
            vertices_2d[:, 1],
            np.full(len(vertices_2d), z_val)
        ])
        filepath = os.path.join(output_dir, f"{gear_name}_{z_name}.txt")
        save_curve_to_file(points_3d, filepath)


def export_gearset(gearset, base_output_dir="cad_export"):
    """Export all components of a gearset."""
    S, P, R, N, b = gearset["S"], gearset["P"], gearset["R"], gearset["N"], gearset["b"]
    name = gearset["name"]
    ratio = (R + S) / S

    print(f"\n{'='*60}")
    print(f"Exporting {name}: S={S}, P={P}, R={R}, N={N}, b={b}")
    print(f"Ratio: {ratio:.2f}:1 | Ring Locked | Sun->Carrier")
    print(f"{'='*60}")

    # Create output directory
    output_dir = os.path.join(base_output_dir, f"{name}_S{S}_P{P}_R{R}_N{N}")
    os.makedirs(output_dir, exist_ok=True)

    # Create gear geometry
    gear = PlanetaryGeometry.create(KINEMATICS, (R, P, S), N, b=b)

    # Get base profiles
    ring_profile, planet_profile, sun_profile, _ = gear.generate_profiles

    # Calculate scale factor (ring diameter -> target)
    ring_vertices = ring_profile.vertices
    max_radius_unscaled = np.max(np.linalg.norm(ring_vertices, axis=1))
    scale_factor = (TARGET_RING_DIAMETER_MM / 2.0) / max_radius_unscaled

    print(f"\nScale factor: {scale_factor:.4f}")
    print(f"Target ring diameter: {TARGET_RING_DIAMETER_MM} mm")
    print(f"Gear thickness: {GEAR_THICKNESS_MM} mm")

    # Export each gear
    print(f"\nExporting gear profiles to {output_dir}/")
    export_gear_profile(ring_profile, "ring", scale_factor, GEAR_THICKNESS_MM, output_dir)
    export_gear_profile(planet_profile, "planet", scale_factor, GEAR_THICKNESS_MM, output_dir)
    export_gear_profile(sun_profile, "sun", scale_factor, GEAR_THICKNESS_MM, output_dir)

    # Export carrier path (circle where planet centers go)
    carrier_radius = 1.0 * scale_factor  # Planet centers are at radius 1.0 in normalized coords
    angles = np.linspace(0, 2 * np.pi, 100, endpoint=True)
    carrier_points = np.column_stack([
        carrier_radius * np.cos(angles),
        carrier_radius * np.sin(angles),
        np.zeros_like(angles)
    ])
    carrier_path = os.path.join(output_dir, "carrier_path.txt")
    save_curve_to_file(carrier_points, carrier_path)

    # Export planet positions (for patterning reference)
    planet_angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
    planet_centers = np.column_stack([
        carrier_radius * np.cos(planet_angles),
        carrier_radius * np.sin(planet_angles),
        np.zeros(N)
    ])
    planet_pos_path = os.path.join(output_dir, "planet_centers.txt")
    np.savetxt(planet_pos_path, planet_centers, fmt='%.8f', delimiter=' ')
    print(f"  Exported: {planet_pos_path} ({N} planet positions)")

    # Write info file
    info_path = os.path.join(output_dir, "gearset_info.txt")
    with open(info_path, 'w') as f:
        f.write(f"Gearset: {name}\n")
        f.write(f"Configuration: Ring Locked, Sun Input, Carrier Output\n")
        f.write(f"Ratio: {ratio:.2f}:1\n")
        f.write(f"\nGear Parameters:\n")
        f.write(f"  Sun teeth (S): {S}\n")
        f.write(f"  Planet teeth (P): {P}\n")
        f.write(f"  Ring teeth (R): {R}\n")
        f.write(f"  Number of planets (N): {N}\n")
        f.write(f"  Tooth profile (b): {b}\n")
        f.write(f"\nPhysical Dimensions:\n")
        f.write(f"  Ring outer diameter: {TARGET_RING_DIAMETER_MM} mm\n")
        f.write(f"  Gear thickness: {GEAR_THICKNESS_MM} mm\n")
        f.write(f"  Carrier path radius: {carrier_radius:.4f} mm\n")
        f.write(f"\nFiles:\n")
        f.write(f"  ring_z0.txt, ring_z_top.txt, ring_z_bot.txt - Ring gear profiles\n")
        f.write(f"  planet_z0.txt, planet_z_top.txt, planet_z_bot.txt - Planet gear profile (one, pattern for others)\n")
        f.write(f"  sun_z0.txt, sun_z_top.txt, sun_z_bot.txt - Sun gear profiles\n")
        f.write(f"  carrier_path.txt - Circle for carrier/planet centers\n")
        f.write(f"  planet_centers.txt - XYZ positions of planet gear centers\n")
    print(f"  Exported: {info_path}")

    return output_dir


def main():
    print("="*60)
    print("CAD Export for V4 Gearsets")
    print("="*60)

    output_dirs = []
    for gearset in GEARSETS:
        output_dir = export_gearset(gearset)
        output_dirs.append(output_dir)

    print("\n" + "="*60)
    print("EXPORT COMPLETE")
    print("="*60)
    print("\nExported directories:")
    for d in output_dirs:
        print(f"  {d}/")


if __name__ == "__main__":
    main()
