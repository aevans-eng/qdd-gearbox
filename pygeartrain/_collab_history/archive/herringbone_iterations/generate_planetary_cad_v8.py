"""
generate_planetary_cad_v8.py - Fixed position, adjusted rotation

Insight: Planet center stays at fixed carrier radius.
The planet PROFILE rotation is adjusted to maintain mesh with the twisted sun.

At z=0: standard mesh rotation
At z≠0: add sun_twist to planet rotation (keeps teeth aligned with sun)
        The planet's own twist (based on planet radius) handles the ring mesh
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
print("PLANETARY GEAR EXPORT v8 (fixed position, adjusted rotation)")
print("=" * 60)

base_ring_profile, base_planet_profile, base_sun_profile, _ = gear.generate_profiles

radii = np.linalg.norm(base_ring_profile.vertices, axis=1)
scale_factor = (TARGET_RING_DIAMETER_MM / 2.0) / np.max(radii)
carrier_radius = 1.0 * scale_factor

sun_outer_r = np.max(np.linalg.norm(base_sun_profile.vertices, axis=1)) * scale_factor
planet_outer_r = np.max(np.linalg.norm(base_planet_profile.vertices, axis=1)) * scale_factor
ring_inner_r = np.min(np.linalg.norm(base_ring_profile.vertices, axis=1)) * scale_factor

print(f"Carrier radius: {carrier_radius:.2f}mm")

output_dir = f"output_{GEAR_TYPE}_v8"
os.makedirs(output_dir, exist_ok=True)

# --- Twist calculations ---
tan_helix = math.tan(math.radians(HELIX_ANGLE_DEGREES))

sun_twist_per_z = tan_helix / sun_outer_r      # Sun twist rate
planet_twist_per_z = -tan_helix / planet_outer_r  # Planet's own twist (opposite hand)
ring_twist_per_z = -tan_helix / ring_inner_r   # Ring twist

z_test = GEAR_THICKNESS_MM / 2
print(f"\nTwist at z={z_test}mm:")
print(f"  Sun: {math.degrees(sun_twist_per_z * z_test):.2f}°")
print(f"  Planet (own): {math.degrees(planet_twist_per_z * z_test):.2f}°")
print(f"  Ring: {math.degrees(ring_twist_per_z * z_test):.2f}°")


def rotate_2d(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    rotated = np.zeros_like(points)
    rotated[:, 0] = points[:, 0] * c - points[:, 1] * s
    rotated[:, 1] = points[:, 0] * s + points[:, 1] * c
    return rotated


def translate_2d(points, dx, dy):
    t = points.copy()
    t[:, 0] += dx
    t[:, 1] += dy
    return t


def save_curve(points_3d, filepath):
    if points_3d is None or len(points_3d) < 3:
        return
    if np.linalg.norm(points_3d[-1, :2] - points_3d[0, :2]) > CLOSE_POINT_TOLERANCE:
        points_3d = np.vstack((points_3d, points_3d[0]))
    np.savetxt(filepath, points_3d, fmt='%.8f', delimiter=' ')


def export_gear_standard(base_vertices, name, twist_per_z):
    """Export sun or ring with standard twist"""
    vertices = base_vertices * scale_factor
    filtered = [vertices[0]]
    for i in range(len(vertices) - 1):
        if np.linalg.norm(vertices[i+1] - filtered[-1]) > CLOSE_POINT_TOLERANCE * scale_factor:
            filtered.append(vertices[i+1])
    filtered = np.array(filtered)

    for z_name, z_val in [('z0', 0.0), ('z_pos', GEAR_THICKNESS_MM/2), ('z_neg', -GEAR_THICKNESS_MM/2)]:
        twist = abs(z_val) * twist_per_z if abs(z_val) > SMALL_RADIUS_TOLERANCE else 0.0
        rotated = rotate_2d(filtered, twist)
        pts_3d = np.column_stack([rotated, np.full(len(rotated), z_val)])
        save_curve(pts_3d, os.path.join(output_dir, f"{name}_{z_name}.txt"))
    print(f"  Exported {name}")


def export_planet(base_vertices, planet_idx, base_mesh_rotation):
    """
    Export planet with:
    - Fixed center position
    - Profile rotation = mesh_rotation + sun_twist (to track sun) + planet_twist (for herringbone)
    """
    vertices = base_vertices * scale_factor

    # Apply base mesh rotation
    if abs(base_mesh_rotation) > 1e-9:
        vertices = rotate_2d(vertices, base_mesh_rotation)

    filtered = [vertices[0]]
    for i in range(len(vertices) - 1):
        if np.linalg.norm(vertices[i+1] - filtered[-1]) > CLOSE_POINT_TOLERANCE * scale_factor:
            filtered.append(vertices[i+1])
    filtered = np.array(filtered)

    # Fixed planet position
    base_angle = 2 * np.pi * planet_idx / N_planets
    pos_x = carrier_radius * math.cos(base_angle)
    pos_y = carrier_radius * math.sin(base_angle)

    for z_name, z_val in [('z0', 0.0), ('z_pos', GEAR_THICKNESS_MM/2), ('z_neg', -GEAR_THICKNESS_MM/2)]:
        z_abs = abs(z_val)

        # Sun twist at this Z
        sun_twist = z_abs * sun_twist_per_z if z_abs > SMALL_RADIUS_TOLERANCE else 0.0

        # Planet's own twist (herringbone)
        planet_own_twist = z_abs * planet_twist_per_z if z_abs > SMALL_RADIUS_TOLERANCE else 0.0

        # Total planet rotation = sun_twist (to track sun mesh) + planet_own_twist (herringbone shape)
        total_twist = sun_twist + planet_own_twist

        # Apply rotation around planet's own center (origin before translation)
        rotated = rotate_2d(filtered, total_twist)

        # Translate to fixed position
        translated = translate_2d(rotated, pos_x, pos_y)

        pts_3d = np.column_stack([translated, np.full(len(translated), z_val)])
        save_curve(pts_3d, os.path.join(output_dir, f"planet_{P_teeth}_{planet_idx}_{z_name}.txt"))

    print(f"  Exported planet_{P_teeth}_{planet_idx}")


# --- Export ---
print("\nExporting:")
export_gear_standard(base_sun_profile.vertices, f"sun_{S_teeth}", sun_twist_per_z)
export_gear_standard(base_ring_profile.vertices, f"ring_{R_teeth}", ring_twist_per_z)

for i in range(N_planets):
    a = 2 * np.pi * i / N_planets
    w = (1 - R_teeth / P_teeth) * a
    export_planet(base_planet_profile.vertices, i, w)

# Positions file
positions = [[carrier_radius * math.cos(2*np.pi*i/N_planets),
              carrier_radius * math.sin(2*np.pi*i/N_planets),
              0.0, math.degrees(2*np.pi*i/N_planets)] for i in range(N_planets)]
np.savetxt(os.path.join(output_dir, "planet_positions.txt"), np.array(positions), fmt='%.8f')

print("\n" + "=" * 60)
print("v8 COMPLETE")
print("=" * 60)
