"""
generate_planetary_cad_v3.py - CORRECT mesh rotation + herringbone

Key insight: Mesh rotation and herringbone twist must both happen while
the gear profile is at the origin. The order is:
1. Base profile at origin
2. Apply mesh rotation (rotates teeth for proper interleave)
3. Apply herringbone twist (around gear's own axis = origin)
4. Export (CATIA macro handles translation + placement rotation)

This fixes both v1 (no mesh rotation) and v2 (herringbone around wrong center).
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
b_profile = 0.2  # Validated: b=0.1 causes planet-ring crossings, b=0.2 is valid

# --- Create Gear Geometry ---
kinematics = Planetary('s', 'c', 'r')
G = (R_teeth, P_teeth, S_teeth)

gear = PlanetaryGeometry.create(
    kinematics=kinematics,
    G=G,
    N=N_planets,
    b=b_profile)

print("=" * 60)
print("PLANETARY GEAR EXPORT v3 (mesh rotation + herringbone fix)")
print("=" * 60)
print(f"Configuration: R={R_teeth}, P={P_teeth}, S={S_teeth}, N={N_planets}")
print(f"Ratio: {(R_teeth + S_teeth) / S_teeth:.2f}:1")
print(f"Target Ring Diameter: {TARGET_RING_DIAMETER_MM:.2f} mm")
print(f"Mesh rotation factor: (1 - R/P) = (1 - {R_teeth}/{P_teeth}) = {1 - R_teeth/P_teeth:.2f}")

# --- Get BASE Profiles (at origin, no mesh rotation) ---
base_ring_profile, base_planet_profile, base_sun_profile, _ = gear.generate_profiles

# --- Calculate Scaling Factor ---
unscaled_ring_vertices = base_ring_profile.vertices
radii = np.linalg.norm(unscaled_ring_vertices, axis=1)
max_radius_unscaled = np.max(radii)
target_radius = TARGET_RING_DIAMETER_MM / 2.0
scale_factor = target_radius / max_radius_unscaled
print(f"Scale Factor: {scale_factor:.6f}")

# Calculate carrier radius (where planet centers go)
# In pygeartrain, planet centers are at radius 1.0 (unscaled)
carrier_radius_scaled = 1.0 * scale_factor
print(f"Carrier Radius (scaled): {carrier_radius_scaled:.4f} mm")

# --- Output Directory ---
output_dir = f"output_{GEAR_TYPE}_v3"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
print(f"\nOutput directory: {output_dir}")

# --- Helix/Herringbone Setup ---
helix_angle_rad = math.radians(HELIX_ANGLE_DEGREES)
base_tan_helix = math.tan(helix_angle_rad)


def rotate_2d(points, angle):
    """Rotate 2D points around origin by angle (radians)."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    rotated = np.zeros_like(points)
    rotated[:, 0] = points[:, 0] * cos_a - points[:, 1] * sin_a
    rotated[:, 1] = points[:, 0] * sin_a + points[:, 1] * cos_a
    return rotated


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


def export_gear(base_vertices_2d, name, tan_helix_sign=1, mesh_rotation=0.0):
    """
    Export a gear profile with mesh rotation + herringbone twist.

    Args:
        base_vertices_2d: Original 2D profile vertices (unscaled)
        name: Output filename base
        tan_helix_sign: 1 for sun, -1 for planet/ring
        mesh_rotation: Rotation angle in radians to apply BEFORE herringbone twist
    """
    # Scale the base profile
    vertices_2d = base_vertices_2d * scale_factor

    # Apply mesh rotation (still at origin, around gear's own axis)
    if abs(mesh_rotation) > 1e-9:
        vertices_2d = rotate_2d(vertices_2d, mesh_rotation)

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


# --- Export Ring (at origin, no mesh rotation needed) ---
print("\nExporting ring gear...")
export_gear(base_ring_profile.vertices, f"ring_{R_teeth}", tan_helix_sign=-1)

# --- Export Sun (at origin, no mesh rotation needed) ---
print("\nExporting sun gear...")
export_gear(base_sun_profile.vertices, f"sun_{S_teeth}", tan_helix_sign=1)

# --- Export Each Planet (with mesh rotation applied) ---
print(f"\nExporting {N_planets} planet gears (with mesh rotation)...")
for i in range(N_planets):
    # Calculate placement angle and mesh rotation
    a = 2 * np.pi * i / N_planets  # 0°, 120°, 240°
    w = (1 - R_teeth / P_teeth) * a  # mesh rotation: -1.5 * a

    # Also calculate where CATIA should position this planet
    pos_x = carrier_radius_scaled * math.cos(a)
    pos_y = carrier_radius_scaled * math.sin(a)

    print(f"\n  Planet {i}:")
    print(f"    Placement angle a = {math.degrees(a):.1f}°")
    print(f"    Mesh rotation w = {math.degrees(w):.1f}°")
    print(f"    CATIA position: ({pos_x:.2f}, {pos_y:.2f}) mm")

    planet_name = f"planet_{P_teeth}_{i}"
    export_gear(base_planet_profile.vertices, planet_name, tan_helix_sign=-1, mesh_rotation=w)

# --- Export Carrier Path ---
print("\nExporting carrier path...")
angles = np.linspace(0, 2 * np.pi, 200, endpoint=True)
carrier_x = carrier_radius_scaled * np.cos(angles)
carrier_y = carrier_radius_scaled * np.sin(angles)
carrier_pts = np.column_stack((carrier_x, carrier_y, np.zeros_like(carrier_x)))
np.savetxt(os.path.join(output_dir, "carrier_path.txt"), carrier_pts, fmt='%.8f', delimiter=' ')
print(f"  Saved: carrier_path.txt")

# --- Export Planet Positions (for CATIA macro) ---
print("\nExporting planet positions...")
positions = []
for i in range(N_planets):
    a = 2 * np.pi * i / N_planets
    pos_x = carrier_radius_scaled * math.cos(a)
    pos_y = carrier_radius_scaled * math.sin(a)
    positions.append([pos_x, pos_y, 0.0, math.degrees(a)])  # x, y, z, angle_deg
np.savetxt(os.path.join(output_dir, "planet_positions.txt"),
           np.array(positions), fmt='%.8f', delimiter=' ',
           header='x y z placement_angle_deg')
print(f"  Saved: planet_positions.txt")

# --- Summary ---
print("\n" + "=" * 60)
print("EXPORT COMPLETE")
print("=" * 60)
print(f"Output directory: {output_dir}/")
print(f"\nFiles created:")
print(f"  - ring_{R_teeth}_z*.txt (3 files)")
print(f"  - sun_{S_teeth}_z*.txt (3 files)")
print(f"  - planet_{P_teeth}_0_z*.txt (3 files) - mesh rotation: 0°")
print(f"  - planet_{P_teeth}_1_z*.txt (3 files) - mesh rotation: -180°")
print(f"  - planet_{P_teeth}_2_z*.txt (3 files) - mesh rotation: -360°")
print(f"  - carrier_path.txt")
print(f"  - planet_positions.txt")
print(f"\nCATIA MACRO INSTRUCTIONS:")
print(f"  1. Import ring at origin")
print(f"  2. Import sun at origin")
print(f"  3. For each planet_N:")
print(f"     a. Import planet_{P_teeth}_N_z*.txt files at origin")
print(f"     b. Translate to position from planet_positions.txt")
print(f"     c. Rotate by placement_angle_deg around Z-axis")
print(f"  (Mesh rotation is already baked into each planet profile)")
