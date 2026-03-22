"""
generate_planetary_cad_v5.py - CORRECT herringbone with gear ratio

Key insight: For mesh to track across Z levels, the twist angles must
maintain the gear ratio relationship:
  planet_twist = -sun_twist × (S/P)

If sun twists by θ, planet must twist by -θ/2 (for S=6, P=12) to maintain mesh.
"""

import numpy as np
import os
import math

from pygeartrain.planetary import Planetary, PlanetaryGeometry

# --- Parameters ---
TARGET_RING_DIAMETER_MM = 70.0
GEAR_THICKNESS_MM = 10.0
HELIX_ANGLE_DEGREES = 20.0  # Keep the original helix angle
GEAR_TYPE = 'herringbone'
CLOSE_POINT_TOLERANCE = 1e-7
SMALL_RADIUS_TOLERANCE = 1e-9

# --- Gear Configuration ---
R_teeth = 30
P_teeth = 12
S_teeth = 6
N_planets = 3
b_profile = 0.2

# --- Create Geometry ---
kinematics = Planetary('s', 'c', 'r')
gear = PlanetaryGeometry.create(kinematics, (R_teeth, P_teeth, S_teeth), N_planets, b=b_profile)

print("=" * 60)
print("PLANETARY GEAR EXPORT v5 (gear ratio twist correction)")
print("=" * 60)
print(f"Configuration: R={R_teeth}, P={P_teeth}, S={S_teeth}, N={N_planets}")

# --- Get profiles and scaling ---
base_ring_profile, base_planet_profile, base_sun_profile, _ = gear.generate_profiles

unscaled_ring_vertices = base_ring_profile.vertices
radii = np.linalg.norm(unscaled_ring_vertices, axis=1)
scale_factor = (TARGET_RING_DIAMETER_MM / 2.0) / np.max(radii)
carrier_radius = 1.0 * scale_factor

print(f"Scale factor: {scale_factor:.4f}")
print(f"Carrier radius: {carrier_radius:.4f} mm")
print(f"Helix angle: {HELIX_ANGLE_DEGREES}°")

# --- Output Directory ---
output_dir = f"output_{GEAR_TYPE}_v5"
os.makedirs(output_dir, exist_ok=True)
print(f"Output directory: {output_dir}")

# --- Helix calculation ---
helix_angle_rad = math.radians(HELIX_ANGLE_DEGREES)
tan_helix = math.tan(helix_angle_rad)

# Get reference radii
sun_outer_r = np.max(np.linalg.norm(base_sun_profile.vertices, axis=1)) * scale_factor
planet_outer_r = np.max(np.linalg.norm(base_planet_profile.vertices, axis=1)) * scale_factor
ring_inner_r = np.min(np.linalg.norm(base_ring_profile.vertices, axis=1)) * scale_factor

print(f"\nReference radii:")
print(f"  Sun outer: {sun_outer_r:.2f} mm")
print(f"  Planet outer: {planet_outer_r:.2f} mm")
print(f"  Ring inner: {ring_inner_r:.2f} mm")

# --- KEY FIX: Twist must maintain gear ratio ---
# Sun twist at z=5mm using its outer radius
z_test = GEAR_THICKNESS_MM / 2
sun_twist_angle = (z_test * tan_helix) / sun_outer_r

# Planet twist must be: -sun_twist × (S/P) to maintain mesh
# This is the gear ratio relationship!
gear_ratio_sp = S_teeth / P_teeth  # = 0.5
planet_twist_angle = -sun_twist_angle * gear_ratio_sp

# Ring twist: planet outer meshes with ring inner
# Planet twist at outer edge, ring must match at inner edge
# Ring twist = planet_twist × (planet_outer / ring_inner) with opposite sign
gear_ratio_pr = P_teeth / R_teeth  # = 0.4
ring_twist_angle = -planet_twist_angle * gear_ratio_pr

print(f"\nTwist angles at z={z_test}mm:")
print(f"  Sun: {math.degrees(sun_twist_angle):.2f}°")
print(f"  Planet: {math.degrees(planet_twist_angle):.2f}° (= sun × {gear_ratio_sp})")
print(f"  Ring: {math.degrees(ring_twist_angle):.2f}°")

# Convert to twist per Z (radians/mm)
sun_twist_per_z = sun_twist_angle / z_test
planet_twist_per_z = planet_twist_angle / z_test
ring_twist_per_z = ring_twist_angle / z_test


def rotate_2d(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    rotated = np.zeros_like(points)
    rotated[:, 0] = points[:, 0] * c - points[:, 1] * s
    rotated[:, 1] = points[:, 0] * s + points[:, 1] * c
    return rotated


def apply_herringbone_twist(xy_points, z_offset, twist_per_z):
    """Apply herringbone twist (reverses at z=0)."""
    z_for_calc = abs(z_offset)  # Herringbone: symmetric about z=0

    if abs(z_offset) < SMALL_RADIUS_TOLERANCE:
        twist_angle = 0.0
    else:
        twist_angle = z_for_calc * twist_per_z

    c, s = math.cos(twist_angle), math.sin(twist_angle)
    points_3d = []
    for x, y in xy_points:
        points_3d.append([x * c - y * s, x * s + y * c, z_offset])
    return np.array(points_3d)


def save_curve(points_3d, filepath):
    if points_3d is None or len(points_3d) < 3:
        return
    if np.linalg.norm(points_3d[-1, :2] - points_3d[0, :2]) > CLOSE_POINT_TOLERANCE:
        points_3d = np.vstack((points_3d, points_3d[0]))
    np.savetxt(filepath, points_3d, fmt='%.8f', delimiter=' ')
    print(f"  Saved: {os.path.basename(filepath)} ({len(points_3d)} pts)")


def export_gear(base_vertices, name, twist_per_z, mesh_rotation=0.0):
    vertices = base_vertices * scale_factor

    if abs(mesh_rotation) > 1e-9:
        vertices = rotate_2d(vertices, mesh_rotation)

    # Filter close points
    filtered = [vertices[0]]
    for i in range(len(vertices) - 1):
        if np.linalg.norm(vertices[i+1] - filtered[-1]) > CLOSE_POINT_TOLERANCE * scale_factor:
            filtered.append(vertices[i+1])
    filtered = np.array(filtered)

    z_pos = GEAR_THICKNESS_MM / 2.0
    z_neg = -GEAR_THICKNESS_MM / 2.0

    save_curve(apply_herringbone_twist(filtered, 0.0, twist_per_z),
               os.path.join(output_dir, f"{name}_z0.txt"))
    save_curve(apply_herringbone_twist(filtered, z_pos, twist_per_z),
               os.path.join(output_dir, f"{name}_z_pos.txt"))
    save_curve(apply_herringbone_twist(filtered, z_neg, twist_per_z),
               os.path.join(output_dir, f"{name}_z_neg.txt"))


# --- Export gears ---
print("\nExporting ring...")
export_gear(base_ring_profile.vertices, f"ring_{R_teeth}", ring_twist_per_z)

print("\nExporting sun...")
export_gear(base_sun_profile.vertices, f"sun_{S_teeth}", sun_twist_per_z)

print(f"\nExporting {N_planets} planets...")
for i in range(N_planets):
    a = 2 * np.pi * i / N_planets
    w = (1 - R_teeth / P_teeth) * a
    print(f"  Planet {i}: mesh_rot={math.degrees(w):.0f}°")
    export_gear(base_planet_profile.vertices, f"planet_{P_teeth}_{i}",
                planet_twist_per_z, mesh_rotation=w)

# --- Export positions ---
positions = []
for i in range(N_planets):
    a = 2 * np.pi * i / N_planets
    positions.append([carrier_radius * math.cos(a),
                      carrier_radius * math.sin(a),
                      0.0, math.degrees(a)])
np.savetxt(os.path.join(output_dir, "planet_positions.txt"),
           np.array(positions), fmt='%.8f', delimiter=' ',
           header='x y z placement_angle_deg')

print("\n" + "=" * 60)
print("v5 COMPLETE - Gear ratio twist correction applied")
print("=" * 60)
