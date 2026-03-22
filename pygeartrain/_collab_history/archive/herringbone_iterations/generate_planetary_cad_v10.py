"""
generate_planetary_cad_v10.py - Ring compensation using derived rule

IMPORTANT: Sun and planet are COPIED from v9 output (unchanged)
Only the ring is regenerated with calculated compensation.

Ring compensation rule:
    ring_offset = |planet_twist - sun_twist * (S/P)| / 4
    = 1.37° / 4 = 0.343° at z=±5mm
"""

import numpy as np
import os
import math
import shutil

from pygeartrain.planetary import Planetary, PlanetaryGeometry

# --- Parameters ---
TARGET_RING_DIAMETER_MM = 70.0
GEAR_THICKNESS_MM = 10.0
HELIX_ANGLE_DEGREES = 20.0
CLOSE_POINT_TOLERANCE = 1e-7
SMALL_RADIUS_TOLERANCE = 1e-9

R_teeth, P_teeth, S_teeth = 30, 12, 6
N_planets = 3
b_profile = 0.2

print("=" * 60)
print("PLANETARY GEAR EXPORT v10 (calculated ring compensation)")
print("=" * 60)

# --- Copy sun and planet from v9 (UNCHANGED) ---
v9_dir = "output_herringbone_v9"
v10_dir = "output_herringbone_v10"
os.makedirs(v10_dir, exist_ok=True)

print("\nCopying sun and planet from v9 (unchanged)...")
for z_name in ['z0', 'z_pos', 'z_neg']:
    # Copy sun
    src = os.path.join(v9_dir, f"sun_{S_teeth}_{z_name}.txt")
    dst = os.path.join(v10_dir, f"sun_{S_teeth}_{z_name}.txt")
    shutil.copy(src, dst)

    # Copy all planets
    for i in range(N_planets):
        src = os.path.join(v9_dir, f"planet_{P_teeth}_{i}_{z_name}.txt")
        dst = os.path.join(v10_dir, f"planet_{P_teeth}_{i}_{z_name}.txt")
        shutil.copy(src, dst)

print("  Sun: copied")
print("  Planets: copied")

# --- Generate ring with calculated compensation ---
kinematics = Planetary('s', 'c', 'r')
gear = PlanetaryGeometry.create(kinematics, (R_teeth, P_teeth, S_teeth), N_planets, b=b_profile)

base_ring_profile, base_planet_profile, base_sun_profile, _ = gear.generate_profiles

radii = np.linalg.norm(base_ring_profile.vertices, axis=1)
scale_factor = (TARGET_RING_DIAMETER_MM / 2.0) / np.max(radii)

sun_outer_r = np.max(np.linalg.norm(base_sun_profile.vertices, axis=1)) * scale_factor
planet_outer_r = np.max(np.linalg.norm(base_planet_profile.vertices, axis=1)) * scale_factor
ring_inner_r = np.min(np.linalg.norm(base_ring_profile.vertices, axis=1)) * scale_factor

# --- Twist calculations ---
tan_helix = math.tan(math.radians(HELIX_ANGLE_DEGREES))
sun_twist_per_z = tan_helix / sun_outer_r
planet_twist_per_z = -tan_helix / planet_outer_r
ring_twist_per_z = -tan_helix / ring_inner_r

z_test = GEAR_THICKNESS_MM / 2
sun_twist_at_z = sun_twist_per_z * z_test
planet_twist_at_z = planet_twist_per_z * z_test

# --- Ring compensation rule ---
# ring_offset = |planet_twist - sun_twist * (S/P)| / 4
gear_ratio_SP = S_teeth / P_teeth
required_planet_twist = sun_twist_at_z * gear_ratio_SP
actual_planet_twist = abs(planet_twist_at_z)
twist_error = abs(actual_planet_twist - required_planet_twist)
ring_compensation_at_z = twist_error / 4
ring_compensation_per_z = ring_compensation_at_z / z_test

print(f"\nRing compensation calculation:")
print(f"  Twist error: {math.degrees(twist_error):.2f}°")
print(f"  Ring compensation (error/4): {math.degrees(ring_compensation_at_z):.3f}°")


def rotate_2d(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    rotated = np.zeros_like(points)
    rotated[:, 0] = points[:, 0] * c - points[:, 1] * s
    rotated[:, 1] = points[:, 0] * s + points[:, 1] * c
    return rotated


def save_curve(points_3d, filepath):
    if points_3d is None or len(points_3d) < 3:
        return
    if np.linalg.norm(points_3d[-1, :2] - points_3d[0, :2]) > CLOSE_POINT_TOLERANCE:
        points_3d = np.vstack((points_3d, points_3d[0]))
    np.savetxt(filepath, points_3d, fmt='%.8f', delimiter=' ')


def filter_points(vertices):
    filtered = [vertices[0]]
    for i in range(len(vertices) - 1):
        if np.linalg.norm(vertices[i+1] - filtered[-1]) > CLOSE_POINT_TOLERANCE * scale_factor:
            filtered.append(vertices[i+1])
    return np.array(filtered)


# --- Export ring with calculated compensation ---
print(f"\nExporting ring with {math.degrees(ring_compensation_at_z):.3f}° compensation...")
ring_scaled = base_ring_profile.vertices * scale_factor
ring_filtered = filter_points(ring_scaled)

for z_name, z_val in [('z0', 0.0), ('z_pos', GEAR_THICKNESS_MM/2), ('z_neg', -GEAR_THICKNESS_MM/2)]:
    # Standard ring twist
    twist = abs(z_val) * ring_twist_per_z if abs(z_val) > SMALL_RADIUS_TOLERANCE else 0.0

    # Add compensation at z≠0
    if abs(z_val) > SMALL_RADIUS_TOLERANCE:
        compensation = abs(z_val) * ring_compensation_per_z
        total_rotation = twist + compensation
    else:
        total_rotation = twist

    rotated = rotate_2d(ring_filtered, total_rotation)
    pts_3d = np.column_stack([rotated, np.full(len(rotated), z_val)])
    save_curve(pts_3d, os.path.join(v10_dir, f"ring_{R_teeth}_{z_name}.txt"))

print("\n" + "=" * 60)
print("v10 COMPLETE")
print("Sun and planet: UNCHANGED from v9")
print(f"Ring compensation: {math.degrees(ring_compensation_at_z):.3f}° at z=±5mm")
print("=" * 60)
