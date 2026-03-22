import matplotlib.pyplot as plt
import numpy as np
import os
import math
from pygeartrain.cycloid import Cycloid, CycloidGeometry

# --- 1. Basic Parameters ---
N_LOBES = 11          
N_PINS = 12           
ECCENTRICITY = 1.0    
PIN_RADIUS = 2.5      
TARGET_PIN_DIAMETER_MM = 70.0    
GEAR_THICKNESS_MM = 10.0 
HELIX_ANGLE_DEGREES = 20.0 
GEAR_TYPE = 'herringbone'

# --- 2. Initialize Kinematics FIRST ---
# This defines the motion: 's' (eccentric input) to 'c' (disk output)
kinematics = Cycloid('s', 'c')

# --- 3. Create Geometry ---
# We will use the most basic call possible to satisfy the 3-5 argument requirement
try:
    print("Attempting to create Cycloid Geometry...")
    # Attempting 4 arguments: (kinematics, lobes, eccentricity, pin_radius)
    # The library likely calculates pins (P) as lobes + 1 automatically
    gear = CycloidGeometry.create(
        kinematics, 
        int(N_LOBES), 
        float(ECCENTRICITY), 
        float(PIN_RADIUS)
    )
except Exception as e:
    print(f"Fallback failed: {e}. Trying raw positional arguments...")
    # If that fails, we pass the counts and measurements directly
    gear = CycloidGeometry.create(kinematics, int(N_LOBES), int(N_PINS), float(ECCENTRICITY), float(PIN_RADIUS))

# --- 4. Force Integers on Internal Attributes ---
# Based on your traceback, the library uses 'P' for the pin count and 'f' for lobe count
# We force these to int to prevent the 'float' error in generate_profiles
if hasattr(gear, 'P'):
    gear.P = int(gear.P)
if hasattr(gear, 'f'):
    gear.f = int(gear.f)
if hasattr(gear, 'N'): # Just in case N exists
    gear.N = int(gear.N)

print("Generating profiles...")
disk_profile, pin_profile = gear.generate_profiles

# --- 5. Scaling and Export ---
unscaled_pin_vertices = pin_profile.vertices
max_radius_unscaled = np.max(np.linalg.norm(unscaled_pin_vertices, axis=1)) + PIN_RADIUS
scale_factor = (TARGET_PIN_DIAMETER_MM / 2.0) / max_radius_unscaled

output_dir = f"output_cycloid_{GEAR_TYPE}"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def apply_rigid_twist(xy_points, z_offset, tan_helix, is_herringbone, ref_radius):
    z_calc = abs(z_offset) if is_herringbone else z_offset
    twist_angle = (z_calc * tan_helix) / ref_radius if ref_radius > 1e-9 else 0
    cos_t, sin_t = math.cos(twist_angle), math.sin(twist_angle)
    return np.array([[x * cos_t - y * sin_t, x * sin_t + y * cos_t, z_offset] for x, y in xy_points])

def save_gear(profile, name, scale, thickness, tan_helix, g_type):
    scaled_verts = profile.vertices * scale
    ref_r = np.max(np.linalg.norm(scaled_verts, axis=1))
    for z_val, suffix in [(0, "z0"), (thickness/2, "z_pos"), (-thickness/2, "z_neg")]:
        pts = apply_rigid_twist(scaled_verts, z_val, tan_helix, g_type == 'herringbone', ref_r)
        # Ensure closure
        pts = np.vstack((pts, pts[0]))
        np.savetxt(os.path.join(output_dir, f"{name}_{suffix}.txt"), pts, fmt='%.8f')

# Run Export
tan_h = math.tan(math.radians(HELIX_ANGLE_DEGREES))
save_gear(disk_profile, "cycloid_disk", scale_factor, GEAR_THICKNESS_MM, tan_h, GEAR_TYPE)
save_gear(pin_profile, "pin_ring", scale_factor, GEAR_THICKNESS_MM, 0, GEAR_TYPE)

print(f"Done! Check the folder: {output_dir}")

gear.animate()