"""
generate_planetary_cad_v4.py - FIXED herringbone twist

Key fix: Herringbone twist must be calculated using consistent reference
so meshing teeth track each other across Z levels.

For sun-planet mesh: planet twist = sun_twist * (S/P)
For planet-ring mesh: handled by opposite helix hands
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import math

from pygeartrain.planetary import Planetary, PlanetaryGeometry

# --- User Defined Parameters ---
TARGET_RING_DIAMETER_MM = 70.0
GEAR_THICKNESS_MM = 10.0
HELIX_ANGLE_DEGREES = 5.0  # Minimal helix to reduce sun-planet mesh mismatch
GEAR_TYPE = 'herringbone'
CLOSE_POINT_TOLERANCE = 1e-7
SMALL_RADIUS_TOLERANCE = 1e-9

# --- Gear Configuration ---
R_teeth = 30
P_teeth = 12
S_teeth = 6
N_planets = 3
b_profile = 0.2  # Validated as working

# --- Create Gear Geometry ---
kinematics = Planetary('s', 'c', 'r')
G = (R_teeth, P_teeth, S_teeth)

gear = PlanetaryGeometry.create(
    kinematics=kinematics,
    G=G,
    N=N_planets,
    b=b_profile)

print("=" * 60)
print("PLANETARY GEAR EXPORT v4 (fixed herringbone twist)")
print("=" * 60)
print(f"Configuration: R={R_teeth}, P={P_teeth}, S={S_teeth}, N={N_planets}")
print(f"Ratio: {(R_teeth + S_teeth) / S_teeth:.2f}:1")

# --- Get BASE Profiles (at origin, no mesh rotation) ---
base_ring_profile, base_planet_profile, base_sun_profile, _ = gear.generate_profiles

# --- Calculate Scaling Factor ---
unscaled_ring_vertices = base_ring_profile.vertices
radii = np.linalg.norm(unscaled_ring_vertices, axis=1)
max_radius_unscaled = np.max(radii)
target_radius = TARGET_RING_DIAMETER_MM / 2.0
scale_factor = target_radius / max_radius_unscaled
print(f"Scale Factor: {scale_factor:.6f}")

# Calculate carrier radius and pitch radii
carrier_radius_scaled = 1.0 * scale_factor  # pygeartrain uses normalized units

# Calculate module from geometry
# carrier_radius = (r_pitch_sun + r_pitch_planet) = module * (S + P) / 2
module = carrier_radius_scaled * 2 / (S_teeth + P_teeth)
sun_pitch_r = module * S_teeth / 2
planet_pitch_r = module * P_teeth / 2
ring_pitch_r = module * R_teeth / 2

print(f"Module: {module:.4f} mm")
print(f"Sun pitch radius: {sun_pitch_r:.4f} mm")
print(f"Planet pitch radius: {planet_pitch_r:.4f} mm")
print(f"Carrier radius: {carrier_radius_scaled:.4f} mm")

# --- Output Directory ---
output_dir = f"output_{GEAR_TYPE}_v4"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
print(f"\nOutput directory: {output_dir}")

# --- Helix Setup ---
# Use pitch radius for twist calculation so meshing teeth track correctly
helix_angle_rad = math.radians(HELIX_ANGLE_DEGREES)
tan_helix = math.tan(helix_angle_rad)

# Calculate twist at z=5mm for each gear using PITCH radius
z_test = GEAR_THICKNESS_MM / 2
sun_twist_test = (z_test * tan_helix) / sun_pitch_r
planet_twist_test = (z_test * tan_helix) / planet_pitch_r  # Same direction initially

print(f"\nHelix angle: {HELIX_ANGLE_DEGREES}°")
print(f"Sun twist at z={z_test}mm: {math.degrees(sun_twist_test):.2f}° (using pitch radius)")
print(f"Planet twist at z={z_test}mm: {math.degrees(planet_twist_test):.2f}°")


def rotate_2d(points, angle):
    """Rotate 2D points around origin by angle (radians)."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    rotated = np.zeros_like(points)
    rotated[:, 0] = points[:, 0] * cos_a - points[:, 1] * sin_a
    rotated[:, 1] = points[:, 0] * sin_a + points[:, 1] * cos_a
    return rotated


def apply_herringbone_twist(xy_points, z_offset, twist_per_z, is_herringbone):
    """
    Apply herringbone twist using pre-calculated twist rate.

    Args:
        xy_points: 2D profile points
        z_offset: Z position
        twist_per_z: twist angle per mm of Z (radians/mm)
        is_herringbone: if True, twist reverses at z=0
    """
    z_for_calc = abs(z_offset) if is_herringbone else z_offset

    if abs(z_offset) < SMALL_RADIUS_TOLERANCE:
        twist_angle = 0.0
    else:
        twist_angle = z_for_calc * twist_per_z

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

    if np.linalg.norm(points_3d[-1, :2] - points_3d[0, :2]) > CLOSE_POINT_TOLERANCE:
        points_3d = np.vstack((points_3d, points_3d[0]))

    np.savetxt(filepath, points_3d, fmt='%.8f', delimiter=' ')
    print(f"  Saved: {os.path.basename(filepath)} ({len(points_3d)} points)")


def export_gear(base_vertices_2d, name, twist_per_z, mesh_rotation=0.0):
    """
    Export a gear profile with mesh rotation + herringbone twist.

    Args:
        base_vertices_2d: Original 2D profile vertices (unscaled)
        name: Output filename base
        twist_per_z: Twist rate in radians per mm (sign determines helix hand)
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

    is_herringbone = (GEAR_TYPE.lower() == 'herringbone')

    # Z levels
    z_pos = GEAR_THICKNESS_MM / 2.0
    z_neg = -GEAR_THICKNESS_MM / 2.0

    # Generate and save
    pts_z0 = apply_herringbone_twist(filtered, 0.0, twist_per_z, is_herringbone)
    pts_zp = apply_herringbone_twist(filtered, z_pos, twist_per_z, is_herringbone)
    pts_zn = apply_herringbone_twist(filtered, z_neg, twist_per_z, is_herringbone)

    save_curve(pts_z0, os.path.join(output_dir, f"{name}_z0.txt"))
    save_curve(pts_zp, os.path.join(output_dir, f"{name}_z_pos.txt"))
    save_curve(pts_zn, os.path.join(output_dir, f"{name}_z_neg.txt"))


# --- Calculate twist rates for each gear ---
# Key insight: For teeth to track at mesh point, use the MESH RADIUS as reference
# Sun-planet mesh: sun outer ≈ 8.76mm, planet toward sun ≈ 8.75mm (similar!)
# Planet-ring mesh: planet outer ≈ 14.25mm, ring inner ≈ 14.25mm (similar!)

# Get actual mesh radii from profiles
sun_outer_r = np.max(np.linalg.norm(base_sun_profile.vertices, axis=1)) * scale_factor
planet_outer_r = np.max(np.linalg.norm(base_planet_profile.vertices, axis=1)) * scale_factor
planet_inner_r = np.min(np.linalg.norm(base_planet_profile.vertices, axis=1)) * scale_factor

print(f"Sun outer radius: {sun_outer_r:.2f} mm")
print(f"Planet inner radius: {planet_inner_r:.2f} mm")
print(f"Planet outer radius: {planet_outer_r:.2f} mm")

# For sun-planet mesh, use sun's outer radius as reference for BOTH
# This way the tangential displacement at the mesh point is the same
sun_planet_mesh_r = sun_outer_r

# Sun: positive twist
sun_twist_per_z = tan_helix / sun_planet_mesh_r

# Planet: negative twist using SAME reference radius
# This ensures teeth track at the sun-planet mesh point
planet_twist_per_z = -tan_helix / sun_planet_mesh_r

# Ring: use planet's outer radius as reference
# Planet outer meshes with ring inner
ring_twist_per_z = -tan_helix / planet_outer_r  # Same direction as planet

print(f"\nTwist rates (rad/mm):")
print(f"  Sun: {sun_twist_per_z:.6f} ({math.degrees(sun_twist_per_z * 5):.2f}° at z=5mm)")
print(f"  Planet: {planet_twist_per_z:.6f} ({math.degrees(planet_twist_per_z * 5):.2f}° at z=5mm)")
print(f"  Ring: {ring_twist_per_z:.6f} ({math.degrees(ring_twist_per_z * 5):.2f}° at z=5mm)")

# --- Export Ring ---
print("\nExporting ring gear...")
export_gear(base_ring_profile.vertices, f"ring_{R_teeth}", ring_twist_per_z)

# --- Export Sun ---
print("\nExporting sun gear...")
export_gear(base_sun_profile.vertices, f"sun_{S_teeth}", sun_twist_per_z)

# --- Export Planets (with mesh rotation) ---
print(f"\nExporting {N_planets} planet gears...")
for i in range(N_planets):
    a = 2 * np.pi * i / N_planets
    w = (1 - R_teeth / P_teeth) * a  # mesh rotation

    pos_x = carrier_radius_scaled * math.cos(a)
    pos_y = carrier_radius_scaled * math.sin(a)

    print(f"\n  Planet {i}: angle={math.degrees(a):.0f}°, mesh_rot={math.degrees(w):.0f}°")
    print(f"    Position: ({pos_x:.2f}, {pos_y:.2f}) mm")

    planet_name = f"planet_{P_teeth}_{i}"
    export_gear(base_planet_profile.vertices, planet_name, planet_twist_per_z, mesh_rotation=w)

# --- Export positions file ---
print("\nExporting planet positions...")
positions = []
for i in range(N_planets):
    a = 2 * np.pi * i / N_planets
    pos_x = carrier_radius_scaled * math.cos(a)
    pos_y = carrier_radius_scaled * math.sin(a)
    positions.append([pos_x, pos_y, 0.0, math.degrees(a)])
np.savetxt(os.path.join(output_dir, "planet_positions.txt"),
           np.array(positions), fmt='%.8f', delimiter=' ',
           header='x y z placement_angle_deg')
print(f"  Saved: planet_positions.txt")

# --- Summary ---
print("\n" + "=" * 60)
print("EXPORT COMPLETE (v4 - fixed herringbone)")
print("=" * 60)
print(f"Key fix: Planet twist uses sun's pitch radius as reference")
print(f"         so sun and planet teeth track together across Z")
