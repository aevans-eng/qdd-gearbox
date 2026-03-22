"""
generate_planetary_cad_v6.py - Compensated herringbone twist

The issue: In standard herringbone calculation, each gear twists based on its
own radius. But for mesh to track across Z, planet twist must equal
sun_twist × (S/P). The difference creates a small error.

Fix: Add compensation to planet twist to correct for the gear ratio error.
"""

import numpy as np
import os
import math

from pygeartrain.planetary import Planetary, PlanetaryGeometry

# --- Parameters ---
TARGET_RING_DIAMETER_MM = 70.0
GEAR_THICKNESS_MM = 10.0
HELIX_ANGLE_DEGREES = 20.0
GEAR_TYPE = 'herringbone'
CLOSE_POINT_TOLERANCE = 1e-7
SMALL_RADIUS_TOLERANCE = 1e-9

R_teeth = 30
P_teeth = 12
S_teeth = 6
N_planets = 3
b_profile = 0.2

# --- Create Geometry ---
kinematics = Planetary('s', 'c', 'r')
gear = PlanetaryGeometry.create(kinematics, (R_teeth, P_teeth, S_teeth), N_planets, b=b_profile)

print("=" * 60)
print("PLANETARY GEAR EXPORT v6 (compensated herringbone)")
print("=" * 60)

base_ring_profile, base_planet_profile, base_sun_profile, _ = gear.generate_profiles

radii = np.linalg.norm(base_ring_profile.vertices, axis=1)
scale_factor = (TARGET_RING_DIAMETER_MM / 2.0) / np.max(radii)
carrier_radius = 1.0 * scale_factor

sun_outer_r = np.max(np.linalg.norm(base_sun_profile.vertices, axis=1)) * scale_factor
planet_outer_r = np.max(np.linalg.norm(base_planet_profile.vertices, axis=1)) * scale_factor
ring_inner_r = np.min(np.linalg.norm(base_ring_profile.vertices, axis=1)) * scale_factor

print(f"Sun outer: {sun_outer_r:.2f}mm, Planet outer: {planet_outer_r:.2f}mm")

output_dir = f"output_{GEAR_TYPE}_v6"
os.makedirs(output_dir, exist_ok=True)

# --- Calculate twist with compensation ---
tan_helix = math.tan(math.radians(HELIX_ANGLE_DEGREES))

# Standard twist rates (as in v3)
sun_twist_per_z = tan_helix / sun_outer_r
planet_twist_per_z_raw = -tan_helix / planet_outer_r

# Required planet twist for mesh tracking
required_planet_twist_per_z = -sun_twist_per_z * (S_teeth / P_teeth)

# Compensation to add to planet
compensation_per_z = required_planet_twist_per_z - planet_twist_per_z_raw

# Corrected planet twist
planet_twist_per_z = planet_twist_per_z_raw + compensation_per_z

# Ring twist (planet outer meshes with ring, same compensation logic)
ring_twist_per_z_raw = -tan_helix / ring_inner_r
required_ring_twist_per_z = -planet_twist_per_z * (P_teeth / R_teeth)
ring_compensation_per_z = required_ring_twist_per_z - ring_twist_per_z_raw
ring_twist_per_z = ring_twist_per_z_raw + ring_compensation_per_z

z_test = GEAR_THICKNESS_MM / 2
print(f"\nAt z={z_test}mm:")
print(f"  Sun twist: {math.degrees(sun_twist_per_z * z_test):.2f}°")
print(f"  Planet raw: {math.degrees(planet_twist_per_z_raw * z_test):.2f}°")
print(f"  Planet compensated: {math.degrees(planet_twist_per_z * z_test):.2f}°")
print(f"  Compensation applied: {math.degrees(compensation_per_z * z_test):.2f}°")


def rotate_2d(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    rotated = np.zeros_like(points)
    rotated[:, 0] = points[:, 0] * c - points[:, 1] * s
    rotated[:, 1] = points[:, 0] * s + points[:, 1] * c
    return rotated


def apply_herringbone_twist(xy_points, z_offset, twist_per_z):
    z_for_calc = abs(z_offset)
    twist_angle = 0.0 if abs(z_offset) < SMALL_RADIUS_TOLERANCE else z_for_calc * twist_per_z
    c, s = math.cos(twist_angle), math.sin(twist_angle)
    return np.array([[x*c - y*s, x*s + y*c, z_offset] for x, y in xy_points])


def save_curve(points_3d, filepath):
    if points_3d is None or len(points_3d) < 3:
        return
    if np.linalg.norm(points_3d[-1, :2] - points_3d[0, :2]) > CLOSE_POINT_TOLERANCE:
        points_3d = np.vstack((points_3d, points_3d[0]))
    np.savetxt(filepath, points_3d, fmt='%.8f', delimiter=' ')
    print(f"  {os.path.basename(filepath)}")


def export_gear(base_vertices, name, twist_per_z, mesh_rotation=0.0):
    vertices = base_vertices * scale_factor
    if abs(mesh_rotation) > 1e-9:
        vertices = rotate_2d(vertices, mesh_rotation)

    filtered = [vertices[0]]
    for i in range(len(vertices) - 1):
        if np.linalg.norm(vertices[i+1] - filtered[-1]) > CLOSE_POINT_TOLERANCE * scale_factor:
            filtered.append(vertices[i+1])
    filtered = np.array(filtered)

    z_pos, z_neg = GEAR_THICKNESS_MM / 2.0, -GEAR_THICKNESS_MM / 2.0
    save_curve(apply_herringbone_twist(filtered, 0.0, twist_per_z), os.path.join(output_dir, f"{name}_z0.txt"))
    save_curve(apply_herringbone_twist(filtered, z_pos, twist_per_z), os.path.join(output_dir, f"{name}_z_pos.txt"))
    save_curve(apply_herringbone_twist(filtered, z_neg, twist_per_z), os.path.join(output_dir, f"{name}_z_neg.txt"))


print("\nExporting:")
export_gear(base_ring_profile.vertices, f"ring_{R_teeth}", ring_twist_per_z)
export_gear(base_sun_profile.vertices, f"sun_{S_teeth}", sun_twist_per_z)

for i in range(N_planets):
    a = 2 * np.pi * i / N_planets
    w = (1 - R_teeth / P_teeth) * a
    export_gear(base_planet_profile.vertices, f"planet_{P_teeth}_{i}", planet_twist_per_z, mesh_rotation=w)

positions = [[carrier_radius * math.cos(2*np.pi*i/N_planets),
              carrier_radius * math.sin(2*np.pi*i/N_planets),
              0.0, math.degrees(2*np.pi*i/N_planets)] for i in range(N_planets)]
np.savetxt(os.path.join(output_dir, "planet_positions.txt"), np.array(positions), fmt='%.8f')

print("\n" + "=" * 60)
print("v6 COMPLETE")
print("=" * 60)
