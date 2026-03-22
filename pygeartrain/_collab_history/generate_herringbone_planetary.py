"""
generate_herringbone_planetary.py - Herringbone Planetary Gear XYZ Export

Generates XYZ point profiles for herringbone planetary gears for CATIA import.

RULES:
1. Sun: standard herringbone twist around origin
2. Planets: mesh rotation + herringbone twist around planet centers
3. Ring: herringbone twist + COMPENSATION for planet center offset

RING COMPENSATION FORMULA:
    compensation = z × tan(helix) × (1/ring_inner_r - 1/mesh_radius)
    where mesh_radius = carrier_radius + planet_outer_radius

See 'Herringbone Planetary Pipeline.md' for full documentation.
"""

import numpy as np
import os
import math

from pygeartrain.planetary import Planetary, PlanetaryGeometry

# =============================================================================
# PARAMETERS - Modify these for different gear configurations
# =============================================================================

R_teeth, P_teeth, S_teeth = 30, 12, 6  # Must satisfy: R = S + 2P
N_planets = 3
b_profile = 0.2  # Tooth profile parameter (0.2 validated, 0.1 causes overlap)

TARGET_RING_DIAMETER_MM = 70.0
GEAR_THICKNESS_MM = 10.0
HELIX_ANGLE_DEGREES = 20.0

OUTPUT_DIR = "output_herringbone_final"

# =============================================================================
# CONSTANTS
# =============================================================================

CLOSE_POINT_TOLERANCE = 1e-7
SMALL_RADIUS_TOLERANCE = 1e-9

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def rotate_2d(points, angle):
    """Rotate 2D points by angle (radians) around origin."""
    c, s = math.cos(angle), math.sin(angle)
    rotated = np.zeros_like(points)
    rotated[:, 0] = points[:, 0] * c - points[:, 1] * s
    rotated[:, 1] = points[:, 0] * s + points[:, 1] * c
    return rotated


def save_curve(points_3d, filepath):
    """Save 3D points to file, ensuring closed curve."""
    if points_3d is None or len(points_3d) < 3:
        return
    if np.linalg.norm(points_3d[-1, :2] - points_3d[0, :2]) > CLOSE_POINT_TOLERANCE:
        points_3d = np.vstack((points_3d, points_3d[0]))
    np.savetxt(filepath, points_3d, fmt='%.8f', delimiter=' ')


def filter_points(vertices, scale_factor):
    """Remove duplicate/close points."""
    filtered = [vertices[0]]
    for i in range(len(vertices) - 1):
        if np.linalg.norm(vertices[i+1] - filtered[-1]) > CLOSE_POINT_TOLERANCE * scale_factor:
            filtered.append(vertices[i+1])
    return np.array(filtered)


# =============================================================================
# MAIN GENERATION
# =============================================================================

def generate_herringbone_planetary():
    print("=" * 60)
    print("HERRINGBONE PLANETARY GEAR EXPORT")
    print("=" * 60)

    # Validate constraint
    assert R_teeth == S_teeth + 2 * P_teeth, f"Invalid: R({R_teeth}) != S({S_teeth}) + 2P({2*P_teeth})"

    # Create geometry
    kinematics = Planetary('s', 'c', 'r')
    gear = PlanetaryGeometry.create(kinematics, (R_teeth, P_teeth, S_teeth), N_planets, b=b_profile)
    base_ring_profile, base_planet_profile, base_sun_profile, _ = gear.generate_profiles

    # Calculate scale factor and radii
    radii = np.linalg.norm(base_ring_profile.vertices, axis=1)
    scale_factor = (TARGET_RING_DIAMETER_MM / 2.0) / np.max(radii)
    carrier_radius = 1.0 * scale_factor

    sun_outer_r = np.max(np.linalg.norm(base_sun_profile.vertices, axis=1)) * scale_factor
    planet_outer_r = np.max(np.linalg.norm(base_planet_profile.vertices, axis=1)) * scale_factor
    ring_inner_r = np.min(np.linalg.norm(base_ring_profile.vertices, axis=1)) * scale_factor
    mesh_radius = carrier_radius + planet_outer_r

    print(f"\nGeometry:")
    print(f"  Carrier radius: {carrier_radius:.2f}mm")
    print(f"  Sun outer radius: {sun_outer_r:.2f}mm")
    print(f"  Planet outer radius: {planet_outer_r:.2f}mm")
    print(f"  Ring inner radius: {ring_inner_r:.2f}mm")
    print(f"  Mesh radius: {mesh_radius:.2f}mm")

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Twist calculations
    tan_helix = math.tan(math.radians(HELIX_ANGLE_DEGREES))
    sun_twist_per_z = tan_helix / sun_outer_r
    planet_twist_per_z = -tan_helix / planet_outer_r  # Opposite hand
    ring_twist_per_z = -tan_helix / ring_inner_r

    # RING COMPENSATION FORMULA
    # compensation = z × tan(helix) × (1/ring_inner_r - 1/mesh_radius)
    ring_comp_per_z = tan_helix * (1/ring_inner_r - 1/mesh_radius)

    z_half = GEAR_THICKNESS_MM / 2
    print(f"\nTwist at z={z_half}mm:")
    print(f"  Sun: {math.degrees(sun_twist_per_z * z_half):.2f}°")
    print(f"  Planet: {math.degrees(planet_twist_per_z * z_half):.2f}°")
    print(f"  Ring: {math.degrees(ring_twist_per_z * z_half):.2f}°")
    print(f"  Ring compensation: {math.degrees(ring_comp_per_z * z_half):.4f}°")

    z_levels = [('z0', 0.0), ('z_pos', GEAR_THICKNESS_MM/2), ('z_neg', -GEAR_THICKNESS_MM/2)]

    # --- EXPORT SUN ---
    print("\nExporting sun...")
    sun_scaled = base_sun_profile.vertices * scale_factor
    sun_filtered = filter_points(sun_scaled, scale_factor)

    for z_name, z_val in z_levels:
        twist = abs(z_val) * sun_twist_per_z if abs(z_val) > SMALL_RADIUS_TOLERANCE else 0.0
        rotated = rotate_2d(sun_filtered, twist)
        pts_3d = np.column_stack([rotated, np.full(len(rotated), z_val)])
        save_curve(pts_3d, os.path.join(OUTPUT_DIR, f"sun_{S_teeth}_{z_name}.txt"))

    # --- EXPORT PLANETS ---
    print("Exporting planets...")
    planet_scaled = base_planet_profile.vertices * scale_factor

    for i in range(N_planets):
        a = 2 * np.pi * i / N_planets
        w = (1 - R_teeth / P_teeth) * a  # Mesh rotation

        # Apply mesh rotation at origin
        planet_rotated = rotate_2d(planet_scaled, w)
        planet_filtered = filter_points(planet_rotated, scale_factor)

        # Planet position
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
        # Standard twist + compensation
        twist = abs(z_val) * ring_twist_per_z if abs(z_val) > SMALL_RADIUS_TOLERANCE else 0.0
        compensation = abs(z_val) * ring_comp_per_z if abs(z_val) > SMALL_RADIUS_TOLERANCE else 0.0
        total_rotation = twist + compensation

        rotated = rotate_2d(ring_filtered, total_rotation)
        pts_3d = np.column_stack([rotated, np.full(len(rotated), z_val)])
        save_curve(pts_3d, os.path.join(OUTPUT_DIR, f"ring_{R_teeth}_{z_name}.txt"))

    print("\n" + "=" * 60)
    print("EXPORT COMPLETE")
    print(f"Output: {OUTPUT_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    generate_herringbone_planetary()
