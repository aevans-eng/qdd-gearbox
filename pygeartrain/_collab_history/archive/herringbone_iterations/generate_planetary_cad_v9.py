"""
generate_planetary_cad_v9.py - Ring rotation sweep

Sun and planet gears: EXACTLY as v3 (standard herringbone, fixed positions)
Ring gear: standard herringbone + additional rotation to align with planets

This script generates multiple ring versions with different rotation offsets
to find the correct alignment.
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

R_teeth, P_teeth, S_teeth = 30, 12, 6
N_planets = 3
b_profile = 0.2

# --- Create Geometry ---
kinematics = Planetary('s', 'c', 'r')
gear = PlanetaryGeometry.create(kinematics, (R_teeth, P_teeth, S_teeth), N_planets, b=b_profile)

print("=" * 60)
print("PLANETARY GEAR EXPORT v9 (ring rotation sweep)")
print("=" * 60)

base_ring_profile, base_planet_profile, base_sun_profile, _ = gear.generate_profiles

radii = np.linalg.norm(base_ring_profile.vertices, axis=1)
scale_factor = (TARGET_RING_DIAMETER_MM / 2.0) / np.max(radii)
carrier_radius = 1.0 * scale_factor

sun_outer_r = np.max(np.linalg.norm(base_sun_profile.vertices, axis=1)) * scale_factor
planet_outer_r = np.max(np.linalg.norm(base_planet_profile.vertices, axis=1)) * scale_factor
ring_inner_r = np.min(np.linalg.norm(base_ring_profile.vertices, axis=1)) * scale_factor

print(f"Carrier radius: {carrier_radius:.2f}mm")
print(f"Planet outer radius: {planet_outer_r:.2f}mm")

output_dir = f"output_{GEAR_TYPE}_v9"
os.makedirs(output_dir, exist_ok=True)

# --- Twist calculations (standard, as in v3) ---
tan_helix = math.tan(math.radians(HELIX_ANGLE_DEGREES))
sun_twist_per_z = tan_helix / sun_outer_r
planet_twist_per_z = -tan_helix / planet_outer_r  # Opposite hand
ring_twist_per_z = -tan_helix / ring_inner_r

z_test = GEAR_THICKNESS_MM / 2
print(f"\nStandard twist at z={z_test}mm:")
print(f"  Sun: {math.degrees(sun_twist_per_z * z_test):.2f}°")
print(f"  Planet: {math.degrees(planet_twist_per_z * z_test):.2f}°")
print(f"  Ring: {math.degrees(ring_twist_per_z * z_test):.2f}°")


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


# --- Export sun (standard v3 approach) ---
print("\nExporting sun (standard)...")
sun_scaled = base_sun_profile.vertices * scale_factor
sun_filtered = filter_points(sun_scaled)

for z_name, z_val in [('z0', 0.0), ('z_pos', GEAR_THICKNESS_MM/2), ('z_neg', -GEAR_THICKNESS_MM/2)]:
    twist = abs(z_val) * sun_twist_per_z if abs(z_val) > SMALL_RADIUS_TOLERANCE else 0.0
    rotated = rotate_2d(sun_filtered, twist)
    pts_3d = np.column_stack([rotated, np.full(len(rotated), z_val)])
    save_curve(pts_3d, os.path.join(output_dir, f"sun_{S_teeth}_{z_name}.txt"))


# --- Export planets (standard v3 approach, fixed positions) ---
print("Exporting planets (standard, fixed positions)...")
planet_scaled = base_planet_profile.vertices * scale_factor

for i in range(N_planets):
    a = 2 * np.pi * i / N_planets
    w = (1 - R_teeth / P_teeth) * a  # mesh rotation

    # Apply mesh rotation
    planet_rotated = rotate_2d(planet_scaled, w)
    planet_filtered = filter_points(planet_rotated)

    # Fixed position
    pos_x = carrier_radius * math.cos(a)
    pos_y = carrier_radius * math.sin(a)

    for z_name, z_val in [('z0', 0.0), ('z_pos', GEAR_THICKNESS_MM/2), ('z_neg', -GEAR_THICKNESS_MM/2)]:
        twist = abs(z_val) * planet_twist_per_z if abs(z_val) > SMALL_RADIUS_TOLERANCE else 0.0
        rotated = rotate_2d(planet_filtered, twist)
        translated = rotated.copy()
        translated[:, 0] += pos_x
        translated[:, 1] += pos_y
        pts_3d = np.column_stack([translated, np.full(len(translated), z_val)])
        save_curve(pts_3d, os.path.join(output_dir, f"planet_{P_teeth}_{i}_{z_name}.txt"))


# --- Export ring with different rotation offsets ---
print("\nExporting ring with rotation sweep...")
ring_scaled = base_ring_profile.vertices * scale_factor
ring_filtered = filter_points(ring_scaled)

# Test fine rotation offsets around 0°
rotation_offsets_deg = [-0.343, 0, 0.1, 0.2, 0.343, 0.685]

for offset_deg in rotation_offsets_deg:
    offset_rad = math.radians(offset_deg)

    for z_name, z_val in [('z0', 0.0), ('z_pos', GEAR_THICKNESS_MM/2), ('z_neg', -GEAR_THICKNESS_MM/2)]:
        # Standard ring twist
        twist = abs(z_val) * ring_twist_per_z if abs(z_val) > SMALL_RADIUS_TOLERANCE else 0.0

        # Add offset rotation only at z≠0
        if abs(z_val) > SMALL_RADIUS_TOLERANCE:
            total_rotation = twist + offset_rad
        else:
            total_rotation = twist  # No offset at z=0

        rotated = rotate_2d(ring_filtered, total_rotation)
        pts_3d = np.column_stack([rotated, np.full(len(rotated), z_val)])

        # Save with offset in filename
        offset_str = f"{offset_deg:.2f}".replace('.', 'p')
        save_curve(pts_3d, os.path.join(output_dir, f"ring_{R_teeth}_offset{offset_str}_{z_name}.txt"))

    print(f"  Ring with {offset_deg:.2f}° offset")


# --- Save planet outer point for reference ---
# Planet 0 outermost point (toward ring) for zoom reference
planet0_center = np.array([carrier_radius, 0])
planet0_outer_point = planet0_center + np.array([planet_outer_r, 0])
print(f"\nPlanet 0 outer point (for zoom): ({planet0_outer_point[0]:.2f}, {planet0_outer_point[1]:.2f})")

print("\n" + "=" * 60)
print("v9 COMPLETE - Ring rotation sweep")
print("=" * 60)
