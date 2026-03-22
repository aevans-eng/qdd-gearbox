"""
generate_planetary_cad_v11.py - Exact ring compensation from measurement

IMPORTANT: Sun and planet are COPIED from v9 output (unchanged)
Only the ring is regenerated with measured compensation.

Ring compensation: 0.21° at z=±5mm (measured from v10 offset)
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

# EXACT measured compensation
RING_COMPENSATION_DEG = 0.21

print("=" * 60)
print("PLANETARY GEAR EXPORT v11 (measured ring compensation)")
print("=" * 60)

# --- Copy sun and planet from v9 (UNCHANGED) ---
v9_dir = "output_herringbone_v9"
v11_dir = "output_herringbone_v11"
os.makedirs(v11_dir, exist_ok=True)

print("\nCopying sun and planet from v9 (unchanged)...")
for z_name in ['z0', 'z_pos', 'z_neg']:
    # Copy sun
    src = os.path.join(v9_dir, f"sun_{S_teeth}_{z_name}.txt")
    dst = os.path.join(v11_dir, f"sun_{S_teeth}_{z_name}.txt")
    shutil.copy(src, dst)

    # Copy all planets
    for i in range(N_planets):
        src = os.path.join(v9_dir, f"planet_{P_teeth}_{i}_{z_name}.txt")
        dst = os.path.join(v11_dir, f"planet_{P_teeth}_{i}_{z_name}.txt")
        shutil.copy(src, dst)

print("  Sun: copied")
print("  Planets: copied")

# --- Generate ring with exact compensation ---
kinematics = Planetary('s', 'c', 'r')
gear = PlanetaryGeometry.create(kinematics, (R_teeth, P_teeth, S_teeth), N_planets, b=b_profile)

base_ring_profile, _, _, _ = gear.generate_profiles

radii = np.linalg.norm(base_ring_profile.vertices, axis=1)
scale_factor = (TARGET_RING_DIAMETER_MM / 2.0) / np.max(radii)
ring_inner_r = np.min(radii) * scale_factor

# --- Twist calculations ---
tan_helix = math.tan(math.radians(HELIX_ANGLE_DEGREES))
ring_twist_per_z = -tan_helix / ring_inner_r

z_half = GEAR_THICKNESS_MM / 2
ring_compensation_at_z = math.radians(RING_COMPENSATION_DEG)
ring_compensation_per_z = ring_compensation_at_z / z_half

print(f"\nRing compensation: {RING_COMPENSATION_DEG}° at z=±5mm")


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


# --- Export ring with exact compensation ---
print(f"Exporting ring with {RING_COMPENSATION_DEG}° compensation...")
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
    save_curve(pts_3d, os.path.join(v11_dir, f"ring_{R_teeth}_{z_name}.txt"))

print("\n" + "=" * 60)
print("v11 COMPLETE")
print("Sun and planet: UNCHANGED from v9")
print(f"Ring compensation: {RING_COMPENSATION_DEG}° at z=±5mm")
print("=" * 60)
