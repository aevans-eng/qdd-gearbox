"""
generate_herringbone_planetary_v2.py - With Sun AND Ring Compensation

Both sun-planet and planet-ring interfaces have different rotation centers:
- Sun rotates around origin
- Planet rotates around planet center (at carrier_radius)
- Ring rotates around origin

This causes drift at both interfaces. This version compensates BOTH:
1. SUN compensation: sun tracks planet inner point
2. RING compensation: ring tracks planet outer point
"""

import numpy as np
import os
import math

from pygeartrain.planetary import Planetary, PlanetaryGeometry

# =============================================================================
# PARAMETERS
# =============================================================================

R_teeth, P_teeth, S_teeth = 30, 12, 6
N_planets = 3
b_profile = 0.2

TARGET_RING_DIAMETER_MM = 70.0
GEAR_THICKNESS_MM = 10.0
HELIX_ANGLE_DEGREES = 20.0

OUTPUT_DIR = "output_herringbone_v2"

CLOSE_POINT_TOLERANCE = 1e-7
SMALL_RADIUS_TOLERANCE = 1e-9

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def rotate_2d(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    rotated = np.zeros_like(points)
    rotated[:, 0] = points[:, 0] * c - points[:, 1] * s
    rotated[:, 1] = points[:, 0] * s + points[:, 1] * c
    return rotated


def rotate_point_around_center(pt, center, angle):
    """Rotate a single point around a center."""
    c, s = math.cos(angle), math.sin(angle)
    translated = pt - center
    rotated = np.array([translated[0]*c - translated[1]*s, translated[0]*s + translated[1]*c])
    return rotated + center


def save_curve(points_3d, filepath):
    if points_3d is None or len(points_3d) < 3:
        return
    if np.linalg.norm(points_3d[-1, :2] - points_3d[0, :2]) > CLOSE_POINT_TOLERANCE:
        points_3d = np.vstack((points_3d, points_3d[0]))
    np.savetxt(filepath, points_3d, fmt='%.8f', delimiter=' ')


def filter_points(vertices, scale_factor):
    filtered = [vertices[0]]
    for i in range(len(vertices) - 1):
        if np.linalg.norm(vertices[i+1] - filtered[-1]) > CLOSE_POINT_TOLERANCE * scale_factor:
            filtered.append(vertices[i+1])
    return np.array(filtered)


# =============================================================================
# MAIN
# =============================================================================

def generate():
    print("=" * 60)
    print("HERRINGBONE PLANETARY v2 (Sun + Ring Compensation)")
    print("=" * 60)

    # Create geometry
    kinematics = Planetary('s', 'c', 'r')
    gear = PlanetaryGeometry.create(kinematics, (R_teeth, P_teeth, S_teeth), N_planets, b=b_profile)
    base_ring_profile, base_planet_profile, base_sun_profile, _ = gear.generate_profiles

    # Calculate radii
    radii = np.linalg.norm(base_ring_profile.vertices, axis=1)
    scale_factor = (TARGET_RING_DIAMETER_MM / 2.0) / np.max(radii)
    carrier_radius = 1.0 * scale_factor

    sun_outer_r = np.max(np.linalg.norm(base_sun_profile.vertices, axis=1)) * scale_factor
    planet_outer_r = np.max(np.linalg.norm(base_planet_profile.vertices, axis=1)) * scale_factor
    ring_inner_r = np.min(np.linalg.norm(base_ring_profile.vertices, axis=1)) * scale_factor

    print(f"\nGeometry:")
    print(f"  Carrier radius: {carrier_radius:.2f}mm")
    print(f"  Sun outer radius: {sun_outer_r:.2f}mm")
    print(f"  Planet outer radius: {planet_outer_r:.2f}mm")
    print(f"  Ring inner radius: {ring_inner_r:.2f}mm")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Twist calculations
    tan_helix = math.tan(math.radians(HELIX_ANGLE_DEGREES))
    sun_twist_per_z = tan_helix / sun_outer_r
    planet_twist_per_z = -tan_helix / planet_outer_r
    ring_twist_per_z = -tan_helix / ring_inner_r

    # Reference z for calculations
    z_ref = GEAR_THICKNESS_MM / 2

    print(f"\nStandard twist at z={z_ref}mm:")
    print(f"  Sun: {math.degrees(sun_twist_per_z * z_ref):.2f}°")
    print(f"  Planet: {math.degrees(planet_twist_per_z * z_ref):.2f}°")
    print(f"  Ring: {math.degrees(ring_twist_per_z * z_ref):.2f}°")

    # ==========================================================================
    # SUN COMPENSATION
    # Sun needs to track where planet inner point goes (as seen from origin)
    # ==========================================================================

    # Calculate planet inner point position at z_ref
    planet_center = np.array([carrier_radius, 0])
    planet_inner_z0 = np.array([carrier_radius - planet_outer_r, 0])
    planet_twist_at_ref = planet_twist_per_z * z_ref
    planet_inner_at_ref = rotate_point_around_center(planet_inner_z0, planet_center, planet_twist_at_ref)

    # Angular position of planet inner point from origin
    planet_inner_angle = math.atan2(planet_inner_at_ref[1], planet_inner_at_ref[0])

    # Sun standard twist
    sun_twist_at_ref = sun_twist_per_z * z_ref

    # Sun compensation = target angle - standard twist
    sun_comp_at_ref = planet_inner_angle - sun_twist_at_ref
    sun_comp_per_z = sun_comp_at_ref / z_ref

    print(f"\nSun compensation:")
    print(f"  Planet inner angle at z={z_ref}mm: {math.degrees(planet_inner_angle):.2f}°")
    print(f"  Standard sun twist: {math.degrees(sun_twist_at_ref):.2f}°")
    print(f"  Sun compensation: {math.degrees(sun_comp_at_ref):.2f}°")

    # ==========================================================================
    # RING COMPENSATION (same as before)
    # ==========================================================================

    mesh_radius = carrier_radius + planet_outer_r
    ring_comp_per_z = tan_helix * (1/ring_inner_r - 1/mesh_radius)

    print(f"\nRing compensation:")
    print(f"  Ring compensation at z={z_ref}mm: {math.degrees(ring_comp_per_z * z_ref):.4f}°")

    z_levels = [('z0', 0.0), ('z_pos', GEAR_THICKNESS_MM/2), ('z_neg', -GEAR_THICKNESS_MM/2)]

    # --- EXPORT SUN (with compensation) ---
    print("\nExporting sun (with compensation)...")
    sun_scaled = base_sun_profile.vertices * scale_factor
    sun_filtered = filter_points(sun_scaled, scale_factor)

    for z_name, z_val in z_levels:
        if abs(z_val) > SMALL_RADIUS_TOLERANCE:
            standard_twist = abs(z_val) * sun_twist_per_z
            compensation = abs(z_val) * sun_comp_per_z
            total_twist = standard_twist + compensation
        else:
            total_twist = 0.0

        rotated = rotate_2d(sun_filtered, total_twist)
        pts_3d = np.column_stack([rotated, np.full(len(rotated), z_val)])
        save_curve(pts_3d, os.path.join(OUTPUT_DIR, f"sun_{S_teeth}_{z_name}.txt"))

    # --- EXPORT PLANETS (standard - no compensation) ---
    print("Exporting planets (standard)...")
    planet_scaled = base_planet_profile.vertices * scale_factor

    for i in range(N_planets):
        a = 2 * np.pi * i / N_planets
        w = (1 - R_teeth / P_teeth) * a

        planet_rotated = rotate_2d(planet_scaled, w)
        planet_filtered = filter_points(planet_rotated, scale_factor)

        pos_x = carrier_radius * math.cos(a)
        pos_y = carrier_radius * math.sin(a)

        for z_name, z_val in z_levels:
            twist = abs(z_val) * planet_twist_per_z if abs(z_val) > SMALL_RADIUS_TOLERANCE else 0.0
            rotated = rotate_2d(planet_filtered, twist)
            translated = rotated.copy()
            translated[:, 0] += pos_x
            translated[:, 1] += pos_y
            pts_3d = np.column_stack([translated, np.full(len(translated), z_val)])
            save_curve(pts_3d, os.path.join(OUTPUT_DIR, f"planet_{P_teeth}_{i}_{z_name}.txt"))

    # --- EXPORT RING (with compensation) ---
    print("Exporting ring (with compensation)...")
    ring_scaled = base_ring_profile.vertices * scale_factor
    ring_filtered = filter_points(ring_scaled, scale_factor)

    for z_name, z_val in z_levels:
        twist = abs(z_val) * ring_twist_per_z if abs(z_val) > SMALL_RADIUS_TOLERANCE else 0.0
        compensation = abs(z_val) * ring_comp_per_z if abs(z_val) > SMALL_RADIUS_TOLERANCE else 0.0
        total_rotation = twist + compensation

        rotated = rotate_2d(ring_filtered, total_rotation)
        pts_3d = np.column_stack([rotated, np.full(len(rotated), z_val)])
        save_curve(pts_3d, os.path.join(OUTPUT_DIR, f"ring_{R_teeth}_{z_name}.txt"))

    print("\n" + "=" * 60)
    print("v2 COMPLETE")
    print(f"Sun compensation: {math.degrees(sun_comp_at_ref):.2f}° at z=±5mm")
    print(f"Ring compensation: {math.degrees(ring_comp_per_z * z_ref):.4f}° at z=±5mm")
    print("=" * 60)


if __name__ == "__main__":
    generate()
