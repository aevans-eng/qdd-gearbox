"""
generate_planetary_cad_v2.py - FIXED VERSION

Key fix: Uses gear.arrange() to get properly meshed/positioned profiles.
Each planet is exported at its correct position WITH mesh rotation applied.

This fixes the gear overlap issue from v1 where planets were only translated
but not rotated for proper tooth interleave.
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import math

from pygeartrain.planetary import Planetary, PlanetaryGeometry

# --- User Defined Parameters ---
TARGET_RING_DIAMETER_MM = 70.0
GEAR_THICKNESS_MM = 10.0
HELIX_ANGLE_DEGREES = 20.0
GEAR_TYPE = 'herringbone'
CLOSE_POINT_TOLERANCE = 1e-7
SMALL_RADIUS_TOLERANCE = 1e-9

# --- Gear Configuration ---
R_teeth = 30
P_teeth = 12
S_teeth = 6
N_planets = 3
b_profile = 0.1

# --- Create Gear Geometry ---
kinematics = Planetary('s', 'c', 'r')
G = (R_teeth, P_teeth, S_teeth)

gear = PlanetaryGeometry.create(
    kinematics=kinematics,
    G=G,
    N=N_planets,
    b=b_profile)

print("=" * 60)
print("PLANETARY GEAR EXPORT v2 (with mesh rotation fix)")
print("=" * 60)
print(f"Configuration: R={R_teeth}, P={P_teeth}, S={S_teeth}, N={N_planets}")
print(f"Ratio: {(R_teeth + S_teeth) / S_teeth:.2f}:1")
print(f"Target Ring Diameter: {TARGET_RING_DIAMETER_MM:.2f} mm")
print(f"Gear Thickness: {GEAR_THICKNESS_MM:.2f} mm")
print(f"Helix Angle: {HELIX_ANGLE_DEGREES:.2f} degrees")

# --- Get ARRANGED profiles (properly meshed) ---
# phase=0 gives the starting mesh position
ring_profile, planet_profiles, sun_profile, carrier_profile = gear.arrange(phase=0)

print(f"\nArranged profiles: ring, {len(planet_profiles)} planets, sun")

# --- Calculate Scaling Factor ---
unscaled_ring_vertices = ring_profile.vertices
radii = np.linalg.norm(unscaled_ring_vertices, axis=1)
max_radius_unscaled = np.max(radii)
target_radius = TARGET_RING_DIAMETER_MM / 2.0
scale_factor = target_radius / max_radius_unscaled
print(f"Scale Factor: {scale_factor:.6f}")

# Calculate carrier radius for reference
scaled_carrier_radius = 1.0 * scale_factor
print(f"Scaled Carrier Radius: {scaled_carrier_radius:.4f} mm")

# --- Output Directory ---
output_dir = f"output_{GEAR_TYPE}_v2"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
print(f"\nOutput directory: {output_dir}")

# --- Helix/Herringbone Setup ---
helix_angle_rad = math.radians(HELIX_ANGLE_DEGREES)
base_tan_helix = math.tan(helix_angle_rad)


def apply_rigid_twist(xy_points, z_offset, tan_helix, is_herringbone, reference_radius):
    """Apply herringbone twist to 2D points, return 3D points."""
    z_for_calc = abs(z_offset) if is_herringbone else z_offset

    if abs(z_offset) < SMALL_RADIUS_TOLERANCE or reference_radius < SMALL_RADIUS_TOLERANCE:
        twist_angle = 0.0
    else:
        twist_angle = (z_for_calc * tan_helix) / reference_radius

    cos_t = math.cos(twist_angle)
    sin_t = math.sin(twist_angle)

    points_3d = []
    for x, y in xy_points:
        x_new = x * cos_t - y * sin_t
        y_new = x * sin_t + y * cos_t
        points_3d.append([x_new, y_new, z_offset])

    return np.array(points_3d)


def save_curve(points_3d, filepath):
    """Save 3D points to file, ensuring curve closure."""
    if points_3d is None or len(points_3d) < 3:
        print(f"  Warning: Not enough points for {filepath}")
        return

    # Ensure closure
    if np.linalg.norm(points_3d[-1, :2] - points_3d[0, :2]) > CLOSE_POINT_TOLERANCE:
        points_3d = np.vstack((points_3d, points_3d[0]))

    np.savetxt(filepath, points_3d, fmt='%.8f', delimiter=' ')
    print(f"  Saved: {os.path.basename(filepath)} ({len(points_3d)} points)")


def export_gear(profile, name, tan_helix_sign=1):
    """Export a gear profile at 3 Z-levels with herringbone twist."""
    vertices_2d = profile.vertices * scale_factor

    # Filter close points
    filtered = [vertices_2d[0]]
    for i in range(len(vertices_2d) - 1):
        if np.linalg.norm(vertices_2d[i+1] - filtered[-1]) > CLOSE_POINT_TOLERANCE * scale_factor:
            filtered.append(vertices_2d[i+1])
    filtered = np.array(filtered)

    # Reference radius for twist
    ref_radius = np.max(np.linalg.norm(filtered, axis=1))

    # Helix direction
    tan_helix = base_tan_helix * tan_helix_sign
    is_herringbone = (GEAR_TYPE.lower() == 'herringbone')

    # Z levels
    z_pos = GEAR_THICKNESS_MM / 2.0
    z_neg = -GEAR_THICKNESS_MM / 2.0

    # Generate and save
    pts_z0 = apply_rigid_twist(filtered, 0.0, tan_helix, is_herringbone, ref_radius)
    pts_zp = apply_rigid_twist(filtered, z_pos, tan_helix, is_herringbone, ref_radius)
    pts_zn = apply_rigid_twist(filtered, z_neg, tan_helix, is_herringbone, ref_radius)

    save_curve(pts_z0, os.path.join(output_dir, f"{name}_z0.txt"))
    save_curve(pts_zp, os.path.join(output_dir, f"{name}_z_pos.txt"))
    save_curve(pts_zn, os.path.join(output_dir, f"{name}_z_neg.txt"))


# --- Export Ring (at origin) ---
print("\nExporting ring gear...")
export_gear(ring_profile, f"ring_{R_teeth}", tan_helix_sign=-1)

# --- Export Sun (at origin, with mesh rotation already applied by arrange()) ---
print("\nExporting sun gear...")
export_gear(sun_profile, f"sun_{S_teeth}", tan_helix_sign=1)

# --- Export Each Planet (at their ARRANGED positions with mesh rotation) ---
print(f"\nExporting {N_planets} planet gears (positioned + rotated)...")
for i, planet_profile in enumerate(planet_profiles):
    # Get planet center position from the arranged profile
    center = np.mean(planet_profile.vertices, axis=0)
    center_scaled = center * scale_factor

    # Use integer position for filename
    pos_x = int(round(center_scaled[0]))
    pos_y = int(round(center_scaled[1]))

    planet_name = f"planet_{P_teeth}_{pos_x}_{pos_y}"
    print(f"\n  Planet {i+1}: center at ({center_scaled[0]:.1f}, {center_scaled[1]:.1f}) mm")
    export_gear(planet_profile, planet_name, tan_helix_sign=-1)

# --- Export Carrier Path ---
print("\nExporting carrier path...")
angles = np.linspace(0, 2 * np.pi, 200, endpoint=True)
carrier_x = scaled_carrier_radius * np.cos(angles)
carrier_y = scaled_carrier_radius * np.sin(angles)
carrier_pts = np.column_stack((carrier_x, carrier_y, np.zeros_like(carrier_x)))
np.savetxt(os.path.join(output_dir, "carrier_path.txt"), carrier_pts, fmt='%.8f', delimiter=' ')
print(f"  Saved: carrier_path.txt")

# --- Export Planet Centers ---
print("\nExporting planet centers...")
planet_centers = []
for i, planet_profile in enumerate(planet_profiles):
    center = np.mean(planet_profile.vertices, axis=0) * scale_factor
    planet_centers.append([center[0], center[1], 0.0])
np.savetxt(os.path.join(output_dir, "planet_centers.txt"), np.array(planet_centers), fmt='%.8f', delimiter=' ')
print(f"  Saved: planet_centers.txt ({N_planets} centers)")

# --- Summary ---
print("\n" + "=" * 60)
print("EXPORT COMPLETE")
print("=" * 60)
print(f"Output directory: {output_dir}/")
print(f"Files created:")
print(f"  - ring_{R_teeth}_z*.txt (3 files)")
print(f"  - sun_{S_teeth}_z*.txt (3 files)")
print(f"  - planet_{P_teeth}_*_z*.txt ({N_planets * 3} files)")
print(f"  - carrier_path.txt")
print(f"  - planet_centers.txt")
print(f"\nIMPORTANT: Planets are PRE-POSITIONED and PRE-ROTATED for meshing.")
print(f"Import directly without additional translation in CAD.")
