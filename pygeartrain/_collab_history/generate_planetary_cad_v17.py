"""
generate_planetary_cad_v17.py - With profile offset tolerance

Based on v16 with updated gear parameters.
Profile offset thins all teeth uniformly for manufacturing tolerance.

Sun/Planet: offset inward (toward center) = thinner teeth
Ring: offset outward (away from origin) = thinner internal teeth
"""

import numpy as np
import os
import math

from pygeartrain.planetary import Planetary, PlanetaryGeometry

# --- User Defined Parameters ---
TARGET_RING_DIAMETER_MM = 80.0   # Desired outer diameter for the ring gear in mm
GEAR_THICKNESS_MM = 22           # Total face width of the gear (Z-axis)
HELIX_ANGLE_DEGREES = 20.0       # Helix angle for one half of the herringbone/helix
GEAR_TYPE = 'herringbone'        # Choose 'helix' or 'herringbone'
CARRIER_PATH_POINTS = 200        # Number of points for the carrier path circle
CLOSE_POINT_TOLERANCE = 1e-7     # Tolerance for removing duplicate/close points
SMALL_RADIUS_TOLERANCE = 1e-9    # Avoid division by zero for points near origin

# --- Parameters derived from the "Blue" Stage (Stage 2) ---
R_teeth = 48
P_teeth = 18
S_teeth = 12
N_planets = 3
b_profile = 0.5

# TOLERANCE PARAMETER
PROFILE_OFFSET_MM = -0.05  # Negative = inward = thinner teeth (for sun/planet)
                           # Ring uses opposite sign internally

# Ring compensation (from v15 sweep - 0.2° was optimal)
RING_OFFSET_DEG = 0.2

# --- Create Geometry ---
kinematics = Planetary('s', 'c', 'r')
gear = PlanetaryGeometry.create(kinematics, (R_teeth, P_teeth, S_teeth), N_planets, b=b_profile)

print("=" * 60)
print("PLANETARY GEAR EXPORT v17 (with profile offset tolerance)")
print("=" * 60)
print(f"Gear Type: {GEAR_TYPE}")
print(f"Profile offset: {PROFILE_OFFSET_MM} mm (tooth thinning)")
print(f"Ring compensation: {RING_OFFSET_DEG}°")
print(f"\nGear Configuration:")
print(f"  Ring teeth (R): {R_teeth}")
print(f"  Planet teeth (P): {P_teeth}")
print(f"  Sun teeth (S): {S_teeth}")
print(f"  Number of planets: {N_planets}")
print(f"  Tooth profile (b): {b_profile}")
print(f"\nVerifying: R = S + 2P → {R_teeth} = {S_teeth} + 2×{P_teeth} = {S_teeth + 2*P_teeth}", end="")
print(" ✓" if R_teeth == S_teeth + 2*P_teeth else " ✗ INVALID!")

# Calculate ratio
ratio = (R_teeth + S_teeth) / S_teeth
print(f"  Gear ratio: {ratio:.2f}:1")

base_ring_profile, base_planet_profile, base_sun_profile, _ = gear.generate_profiles

radii = np.linalg.norm(base_ring_profile.vertices, axis=1)
scale_factor = (TARGET_RING_DIAMETER_MM / 2.0) / np.max(radii)
carrier_radius = 1.0 * scale_factor

sun_outer_r = np.max(np.linalg.norm(base_sun_profile.vertices, axis=1)) * scale_factor
planet_outer_r = np.max(np.linalg.norm(base_planet_profile.vertices, axis=1)) * scale_factor
ring_inner_r = np.min(np.linalg.norm(base_ring_profile.vertices, axis=1)) * scale_factor

print(f"\nPhysical Dimensions:")
print(f"  Target ring diameter: {TARGET_RING_DIAMETER_MM} mm")
print(f"  Gear thickness: {GEAR_THICKNESS_MM} mm")
print(f"  Carrier radius: {carrier_radius:.2f} mm")
print(f"  Sun outer radius: {sun_outer_r:.2f} mm")
print(f"  Planet outer radius: {planet_outer_r:.2f} mm")
print(f"  Ring inner radius: {ring_inner_r:.2f} mm")

output_dir = "output_herringbone_v17"
os.makedirs(output_dir, exist_ok=True)

# --- Twist calculations ---
tan_helix = math.tan(math.radians(HELIX_ANGLE_DEGREES))
sun_twist_per_z = tan_helix / sun_outer_r
planet_twist_per_z = -tan_helix / planet_outer_r
ring_twist_per_z = -tan_helix / ring_inner_r

z_test = GEAR_THICKNESS_MM / 2
print(f"\nTwist at z=±{z_test}mm:")
print(f"  Sun: {math.degrees(sun_twist_per_z * z_test):.2f}°")
print(f"  Planet: {math.degrees(planet_twist_per_z * z_test):.2f}°")
print(f"  Ring: {math.degrees(ring_twist_per_z * z_test):.2f}°")


def rotate_2d(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    rotated = np.zeros_like(points)
    rotated[:, 0] = points[:, 0] * c - points[:, 1] * s
    rotated[:, 1] = points[:, 0] * s + points[:, 1] * c
    return rotated


def offset_profile_radial(points, offset, center=np.array([0.0, 0.0])):
    """Offset profile points radially from a center point.
    
    Positive offset = outward (away from center)
    Negative offset = inward (toward center) = thinner teeth for external gears
    """
    offset_points = np.zeros_like(points)
    for i, pt in enumerate(points):
        # Vector from center to point
        vec = pt - center
        dist = np.linalg.norm(vec)
        if dist > SMALL_RADIUS_TOLERANCE:
            # Unit vector pointing outward
            unit_vec = vec / dist
            # Apply offset
            offset_points[i] = pt + offset * unit_vec
        else:
            offset_points[i] = pt
    return offset_points


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


# --- Export sun (with profile offset) ---
print("\nExporting sun (with profile offset)...")
sun_scaled = base_sun_profile.vertices * scale_factor
sun_offset = offset_profile_radial(sun_scaled, PROFILE_OFFSET_MM, center=np.array([0.0, 0.0]))
sun_filtered = filter_points(sun_offset)

for z_name, z_val in [('z0', 0.0), ('z_pos', GEAR_THICKNESS_MM/2), ('z_neg', -GEAR_THICKNESS_MM/2)]:
    twist = abs(z_val) * sun_twist_per_z if abs(z_val) > SMALL_RADIUS_TOLERANCE else 0.0
    rotated = rotate_2d(sun_filtered, twist)
    pts_3d = np.column_stack([rotated, np.full(len(rotated), z_val)])
    save_curve(pts_3d, os.path.join(output_dir, f"sun_{S_teeth}_{z_name}.txt"))


# --- Export planets (with profile offset) ---
print("Exporting planets (with profile offset)...")
planet_scaled = base_planet_profile.vertices * scale_factor
# Offset planet profile toward its center (origin before translation)
planet_offset = offset_profile_radial(planet_scaled, PROFILE_OFFSET_MM, center=np.array([0.0, 0.0]))

for i in range(N_planets):
    a = 2 * np.pi * i / N_planets
    w = (1 - R_teeth / P_teeth) * a

    planet_rotated = rotate_2d(planet_offset, w)
    planet_filtered = filter_points(planet_rotated)

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


# --- Export ring (with profile offset + compensation) ---
print("Exporting ring (with profile offset + compensation)...")
ring_scaled = base_ring_profile.vertices * scale_factor
# Ring is internal gear - offset OUTWARD to thin teeth (opposite sign)
ring_offset = offset_profile_radial(ring_scaled, -PROFILE_OFFSET_MM, center=np.array([0.0, 0.0]))
ring_filtered = filter_points(ring_offset)

ring_comp_rad = math.radians(RING_OFFSET_DEG)

for z_name, z_val in [('z0', 0.0), ('z_pos', GEAR_THICKNESS_MM/2), ('z_neg', -GEAR_THICKNESS_MM/2)]:
    twist = abs(z_val) * ring_twist_per_z if abs(z_val) > SMALL_RADIUS_TOLERANCE else 0.0
    
    if abs(z_val) > SMALL_RADIUS_TOLERANCE:
        total_rotation = twist + ring_comp_rad
    else:
        total_rotation = twist

    rotated = rotate_2d(ring_filtered, total_rotation)
    pts_3d = np.column_stack([rotated, np.full(len(rotated), z_val)])
    save_curve(pts_3d, os.path.join(output_dir, f"ring_{R_teeth}_{z_name}.txt"))


# --- Export carrier path ---
print("Exporting carrier path...")
angles = np.linspace(0, 2*np.pi, CARRIER_PATH_POINTS, endpoint=False)
carrier_x = carrier_radius * np.cos(angles)
carrier_y = carrier_radius * np.sin(angles)
carrier_z = np.zeros(CARRIER_PATH_POINTS)
carrier_pts = np.column_stack([carrier_x, carrier_y, carrier_z])
save_curve(carrier_pts, os.path.join(output_dir, "carrier_path.txt"))

# --- Export planet centers ---
print("Exporting planet centers...")
with open(os.path.join(output_dir, "planet_centers.txt"), 'w') as f:
    for i in range(N_planets):
        a = 2 * np.pi * i / N_planets
        pos_x = carrier_radius * math.cos(a)
        pos_y = carrier_radius * math.sin(a)
        f.write(f"{pos_x:.8f} {pos_y:.8f} 0.00000000\n")


print("\n" + "=" * 60)
print("v17 COMPLETE")
print(f"Profile offset: {PROFILE_OFFSET_MM} mm applied to all gears")
print(f"Output: {output_dir}/")
print("=" * 60)
