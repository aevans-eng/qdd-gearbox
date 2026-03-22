"""
generate_planetary_cad_v7.py - Mesh axis alignment method

Key insight from user: At z=0, the mesh has a symmetric axis pointing from
sun center toward planet center. At z≠0, the sun twists, rotating this axis.
The planet should be positioned along this rotated axis to maintain mesh symmetry.

Method:
1. Sun twists by θ_sun at z=5mm (standard helix calculation)
2. This rotates the mesh axis by θ_sun
3. Planet center must move to lie on this rotated axis
4. Planet orientation adjusted to maintain mesh symmetry
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
print("PLANETARY GEAR EXPORT v7 (mesh axis alignment)")
print("=" * 60)

base_ring_profile, base_planet_profile, base_sun_profile, _ = gear.generate_profiles

radii = np.linalg.norm(base_ring_profile.vertices, axis=1)
scale_factor = (TARGET_RING_DIAMETER_MM / 2.0) / np.max(radii)
carrier_radius = 1.0 * scale_factor

sun_outer_r = np.max(np.linalg.norm(base_sun_profile.vertices, axis=1)) * scale_factor
planet_outer_r = np.max(np.linalg.norm(base_planet_profile.vertices, axis=1)) * scale_factor

print(f"Carrier radius: {carrier_radius:.2f}mm")
print(f"Sun outer: {sun_outer_r:.2f}mm")

output_dir = f"output_{GEAR_TYPE}_v7"
os.makedirs(output_dir, exist_ok=True)

# --- Helix calculation ---
tan_helix = math.tan(math.radians(HELIX_ANGLE_DEGREES))

# Sun twist: standard calculation
sun_twist_per_z = tan_helix / sun_outer_r

# Ring twist: standard calculation
ring_inner_r = np.min(np.linalg.norm(base_ring_profile.vertices, axis=1)) * scale_factor
ring_twist_per_z = -tan_helix / ring_inner_r  # Opposite hand

z_test = GEAR_THICKNESS_MM / 2
sun_twist_at_z = sun_twist_per_z * z_test
print(f"\nAt z={z_test}mm, sun twists by {math.degrees(sun_twist_at_z):.2f}°")
print("This rotates the mesh axis by the same amount")


def rotate_2d(points, angle):
    """Rotate points around origin"""
    c, s = math.cos(angle), math.sin(angle)
    rotated = np.zeros_like(points)
    rotated[:, 0] = points[:, 0] * c - points[:, 1] * s
    rotated[:, 1] = points[:, 0] * s + points[:, 1] * c
    return rotated


def apply_herringbone_twist(xy_points, z_offset, twist_per_z):
    """Apply herringbone twist (symmetric about z=0)"""
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


def export_sun(base_vertices, name, twist_per_z):
    """Export sun with standard herringbone twist"""
    vertices = base_vertices * scale_factor

    filtered = [vertices[0]]
    for i in range(len(vertices) - 1):
        if np.linalg.norm(vertices[i+1] - filtered[-1]) > CLOSE_POINT_TOLERANCE * scale_factor:
            filtered.append(vertices[i+1])
    filtered = np.array(filtered)

    for z_name, z_val in [('z0', 0.0), ('z_pos', GEAR_THICKNESS_MM/2), ('z_neg', -GEAR_THICKNESS_MM/2)]:
        pts = apply_herringbone_twist(filtered, z_val, twist_per_z)
        save_curve(pts, os.path.join(output_dir, f"{name}_{z_name}.txt"))
    print(f"  Exported {name}")


def export_ring(base_vertices, name, twist_per_z, compensation_per_z):
    """Export ring with herringbone twist + compensation to follow planet movement"""
    vertices = base_vertices * scale_factor

    filtered = [vertices[0]]
    for i in range(len(vertices) - 1):
        if np.linalg.norm(vertices[i+1] - filtered[-1]) > CLOSE_POINT_TOLERANCE * scale_factor:
            filtered.append(vertices[i+1])
    filtered = np.array(filtered)

    for z_name, z_val in [('z0', 0.0), ('z_pos', GEAR_THICKNESS_MM/2), ('z_neg', -GEAR_THICKNESS_MM/2)]:
        z_abs = abs(z_val)

        # Ring's own herringbone twist
        own_twist = z_abs * twist_per_z if z_abs > SMALL_RADIUS_TOLERANCE else 0.0

        # Compensation: rotate ring to follow planet's moved position
        # Planet moved by sun_twist, ring needs to compensate
        compensation = z_abs * compensation_per_z if z_abs > SMALL_RADIUS_TOLERANCE else 0.0

        total_twist = own_twist + compensation

        c, s = math.cos(total_twist), math.sin(total_twist)
        pts_3d = np.array([[x*c - y*s, x*s + y*c, z_val] for x, y in filtered])
        save_curve(pts_3d, os.path.join(output_dir, f"{name}_{z_name}.txt"))
    print(f"  Exported {name} (with {math.degrees(compensation_per_z * 5):.2f}° compensation at z=5mm)")


def export_planet_with_mesh_axis_alignment(base_vertices, planet_idx, base_mesh_rotation):
    """
    Export planet using mesh axis alignment method.

    At z=0: planet is at (carrier_radius, 0) with mesh_rotation applied
    At z≠0: the mesh axis has rotated by sun_twist, so:
      - Planet center moves to (carrier_radius, 0) rotated by sun_twist
      - Planet profile also rotates to maintain mesh symmetry
    """
    vertices = base_vertices * scale_factor

    # Apply base mesh rotation (from pygeartrain)
    if abs(base_mesh_rotation) > 1e-9:
        vertices = rotate_2d(vertices, base_mesh_rotation)

    # Filter close points
    filtered = [vertices[0]]
    for i in range(len(vertices) - 1):
        if np.linalg.norm(vertices[i+1] - filtered[-1]) > CLOSE_POINT_TOLERANCE * scale_factor:
            filtered.append(vertices[i+1])
    filtered = np.array(filtered)

    # Base planet position (at z=0)
    base_angle = 2 * np.pi * planet_idx / N_planets

    for z_name, z_val in [('z0', 0.0), ('z_pos', GEAR_THICKNESS_MM/2), ('z_neg', -GEAR_THICKNESS_MM/2)]:
        # Sun twist at this Z level (absolute value for herringbone)
        sun_twist = abs(z_val) * sun_twist_per_z if abs(z_val) > SMALL_RADIUS_TOLERANCE else 0.0

        # The mesh axis rotates by sun_twist
        # Planet must follow: rotate profile by same amount, translate to rotated position

        # Step 1: Apply sun_twist rotation to the planet profile (around origin)
        # This keeps the teeth aligned with the rotated sun teeth
        if abs(sun_twist) > 1e-9:
            rotated_profile = rotate_2d(filtered, sun_twist)
        else:
            rotated_profile = filtered.copy()

        # Step 2: Translate to planet position
        # Position is on the rotated mesh axis: base_angle + sun_twist
        new_angle = base_angle + sun_twist
        pos_x = carrier_radius * math.cos(new_angle)
        pos_y = carrier_radius * math.sin(new_angle)

        # Create 3D points with translation
        points_3d = np.zeros((len(rotated_profile), 3))
        points_3d[:, 0] = rotated_profile[:, 0] + pos_x
        points_3d[:, 1] = rotated_profile[:, 1] + pos_y
        points_3d[:, 2] = z_val

        save_curve(points_3d, os.path.join(output_dir, f"planet_{P_teeth}_{planet_idx}_{z_name}.txt"))

    print(f"  Exported planet_{P_teeth}_{planet_idx}")


# --- Ring compensation ---
# Ring needs to rotate by 1.37° × 3 = 4.11° counterclockwise at z=5mm
# This aligns the ring-planet mesh symmetry like z=0mm
ring_compensation_deg = 1.37 * 3  # 4.11 degrees
ring_compensation_per_z = math.radians(ring_compensation_deg) / z_test  # Convert to per-z rate

print(f"Ring compensation: {ring_compensation_deg:.2f}° at z=5mm (counterclockwise)")

# --- Export gears ---
print("\nExporting gears:")
export_sun(base_sun_profile.vertices, f"sun_{S_teeth}", sun_twist_per_z)
export_ring(base_ring_profile.vertices, f"ring_{R_teeth}", ring_twist_per_z, ring_compensation_per_z)

for i in range(N_planets):
    a = 2 * np.pi * i / N_planets
    w = (1 - R_teeth / P_teeth) * a  # mesh rotation from pygeartrain
    export_planet_with_mesh_axis_alignment(base_planet_profile.vertices, i, w)

# Export planet positions (these now vary with Z!)
print("\n  Note: Planet positions vary with Z level in v7")

print("\n" + "=" * 60)
print("v7 COMPLETE - Mesh axis alignment method")
print("=" * 60)
