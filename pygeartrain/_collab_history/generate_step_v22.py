"""
generate_step_v22.py - Zero Offset Herringbone Planetary Gearbox

Based on v21 with same teeth (R48/P18/S12) but:
- Zero offset: 0.00mm (was +0.05mm interference)
- Same 30° helix angle

Goal: Exact nominal fit - no interference, no clearance.
"""

import numpy as np
import os
import math
import cadquery as cq
from cadquery import exporters

# Add pygeartrain to path
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pygeartrain.planetary import Planetary, PlanetaryGeometry


# =============================================================================
# GEAR VALIDATION - Run before anything else
# =============================================================================

def validate_planetary_config(R, P, S, N):
    """
    Validate planetary gear configuration against fundamental rules.
    Raises ValueError immediately if any rule fails.

    Rules:
    1. Mesh constraint: R = S + 2P
    2. Assembly constraint: (R + S) divisible by N
    3. Planet non-interference: planets must not collide with each other
    4. Minimum teeth: S >= 6, P >= 6
    5. Planet count: 2 <= N <= 8
    """
    import math
    errors = []

    # Rule 1: Mesh constraint - R = S + 2P
    expected_R = S + 2 * P
    if R != expected_R:
        errors.append(
            f"MESH CONSTRAINT FAILED: R must equal S + 2P\n"
            f"  Got R={R}, but S + 2P = {S} + 2({P}) = {expected_R}"
        )

    # Rule 2: Assembly constraint - (R + S) must be divisible by N
    sum_RS = R + S
    if sum_RS % N != 0:
        valid_N = [n for n in range(1, sum_RS + 1) if sum_RS % n == 0 and n <= 8]
        errors.append(
            f"ASSEMBLY CONSTRAINT FAILED: (R + S) must be divisible by N\n"
            f"  Got (R + S) = {sum_RS}, N = {N}\n"
            f"  {sum_RS} / {N} = {sum_RS / N:.2f} (not an integer)\n"
            f"  Valid N values for this gear set: {valid_N}"
        )

    # Rule 3: Planet non-interference - planets must not collide
    carrier_factor = S + P
    planet_clearance_needed = P + 2
    planet_spacing = carrier_factor * math.sin(math.pi / N)

    if planet_spacing <= planet_clearance_needed:
        max_N_for_config = None
        for test_N in range(N, 1, -1):
            if carrier_factor * math.sin(math.pi / test_N) > planet_clearance_needed:
                max_N_for_config = test_N
                break

        min_S_for_config = math.ceil((planet_clearance_needed) / math.sin(math.pi / N) - P + 1)

        errors.append(
            f"PLANET INTERFERENCE: Planets will collide with each other\n"
            f"  Spacing check: (S + P) * sin(pi/N) > P + 2\n"
            f"  Got: ({S} + {P}) * sin(pi/{N}) = {planet_spacing:.2f}\n"
            f"  Need: > {planet_clearance_needed}\n"
            f"  {planet_spacing:.2f} <= {planet_clearance_needed} --> COLLISION\n"
            f"\n"
            f"  Options to fix:\n"
            f"    - Reduce planets: max N = {max_N_for_config} for this S/P\n"
            f"    - Increase sun: min S = {min_S_for_config} for P={P}, N={N}"
        )

    # Rule 4: Minimum teeth
    if S < 6:
        errors.append(f"SUN TOO SMALL: S={S} teeth (minimum practical is 6)")
    if P < 6:
        errors.append(f"PLANET TOO SMALL: P={P} teeth (minimum practical is 6)")

    # Rule 5: Planet count sanity
    if N < 2:
        errors.append(f"TOO FEW PLANETS: N={N} (minimum is 2 for balance)")
    if N > 8:
        errors.append(f"TOO MANY PLANETS: N={N} (maximum practical is ~8)")

    if errors:
        error_msg = "\n\n".join(errors)
        raise ValueError(
            f"\n{'='*60}\n"
            f"GEAR CONFIGURATION INVALID\n"
            f"{'='*60}\n\n"
            f"{error_msg}\n\n"
            f"{'='*60}\n"
            f"Fix the parameters before running.\n"
            f"{'='*60}"
        )

    # All passed - print confirmation
    ratio = (R + S) / S
    print(f"[OK] Gear validation passed: R{R}/P{P}/S{S}, N={N}, Ratio={ratio:.2f}:1")
    print(f"     Planet spacing margin: {planet_spacing:.2f} > {planet_clearance_needed} (clearance OK)")


# --- v22 Parameters ---
TARGET_RING_DIAMETER_MM = 80.0
GEAR_THICKNESS_MM = 22
HELIX_ANGLE_DEGREES = 30.0
GEAR_TYPE = 'herringbone'
CLOSE_POINT_TOLERANCE = 1e-7
SMALL_RADIUS_TOLERANCE = 1e-9

# Gear parameters
R_teeth = 48
P_teeth = 18
S_teeth = 12
N_planets = 4
b_profile = 0.5

# VALIDATE IMMEDIATELY
validate_planetary_config(R_teeth, P_teeth, S_teeth, N_planets)

# ZERO OFFSET - CHANGED from v21
PROFILE_OFFSET_MM = 0.00  # was +0.05 (interference), now zero
RING_OFFSET_DEG = 0.2

# Ring wall thickness
RING_WALL_MM = 8.0

# M2 Self-threading screw parameters
M2_CLEARANCE_DIA = 2.4
M2_TAP_DIA = 1.6
M2_HEAD_DIA = 3.8
M2_HEAD_DEPTH = 2.2
N_SCREWS = 6
SCREW_RADIUS_MM = None  # Calculated below

# Output directory
OUTPUT_DIR = "step_output_v22"

print("=" * 60)
print("STEP FILE GENERATOR v22 (Zero Offset, 30° Helix)")
print("=" * 60)

# --- Create Geometry ---
kinematics = Planetary('s', 'c', 'r')
gear = PlanetaryGeometry.create(kinematics, (R_teeth, P_teeth, S_teeth), N_planets, b=b_profile)

base_ring_profile, base_planet_profile, base_sun_profile, _ = gear.generate_profiles

radii = np.linalg.norm(base_ring_profile.vertices, axis=1)
scale_factor = (TARGET_RING_DIAMETER_MM / 2.0) / np.max(radii)
carrier_radius = 1.0 * scale_factor

sun_outer_r = np.max(np.linalg.norm(base_sun_profile.vertices, axis=1)) * scale_factor
planet_outer_r = np.max(np.linalg.norm(base_planet_profile.vertices, axis=1)) * scale_factor
ring_inner_r = np.min(np.linalg.norm(base_ring_profile.vertices, axis=1)) * scale_factor
ring_outer_r = TARGET_RING_DIAMETER_MM / 2 + RING_WALL_MM

# Calculate screw hole radius
SCREW_RADIUS_MM = ring_outer_r - (M2_HEAD_DIA / 2) - 0.5

print(f"\n--- v22 Changes from v21 ---")
print(f"Fit: {PROFILE_OFFSET_MM:+.2f}mm (was +0.05mm interference)")
print()
print(f"--- Geometry ---")
print(f"Ring diameter: {TARGET_RING_DIAMETER_MM}mm, Thickness: {GEAR_THICKNESS_MM}mm")
print(f"Ring outer diameter: {ring_outer_r * 2}mm (with {RING_WALL_MM}mm wall)")
print(f"Ratio: {(R_teeth + S_teeth) / S_teeth:.2f}:1")
print(f"Screw holes: {N_SCREWS}x M2 self-threading at radius {SCREW_RADIUS_MM:.1f}mm")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Helper functions ---
tan_helix = math.tan(math.radians(HELIX_ANGLE_DEGREES))
sun_twist_per_z = tan_helix / sun_outer_r
planet_twist_per_z = -tan_helix / planet_outer_r
ring_twist_per_z = -tan_helix / ring_inner_r
ring_comp_rad = math.radians(RING_OFFSET_DEG)


def rotate_2d(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    rotated = np.zeros_like(points)
    rotated[:, 0] = points[:, 0] * c - points[:, 1] * s
    rotated[:, 1] = points[:, 0] * s + points[:, 1] * c
    return rotated


def offset_profile_radial(points, offset, center=np.array([0.0, 0.0])):
    offset_points = np.zeros_like(points)
    for i, pt in enumerate(points):
        vec = pt - center
        dist = np.linalg.norm(vec)
        if dist > SMALL_RADIUS_TOLERANCE:
            unit_vec = vec / dist
            offset_points[i] = pt + offset * unit_vec
        else:
            offset_points[i] = pt
    return offset_points


def filter_points(vertices):
    filtered = [vertices[0]]
    for i in range(len(vertices) - 1):
        if np.linalg.norm(vertices[i+1] - filtered[-1]) > CLOSE_POINT_TOLERANCE * scale_factor:
            filtered.append(vertices[i+1])
    return np.array(filtered)


def get_screw_positions():
    """Return list of (x, y) positions for screw holes."""
    positions = []
    for i in range(N_SCREWS):
        angle = 2 * math.pi * i / N_SCREWS
        x = SCREW_RADIUS_MM * math.cos(angle)
        y = SCREW_RADIUS_MM * math.sin(angle)
        positions.append((x, y))
    return positions


def create_gear_shape(profile_2d, twist_per_z, z_start, z_end, extra_rotation=0.0, translate=(0, 0)):
    """
    Create gear solid using loft between two Z levels.
    """
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
    from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.gp import gp_Pnt

    def get_profile_at_z(z_val):
        if abs(z_val) > SMALL_RADIUS_TOLERANCE:
            twist = abs(z_val) * twist_per_z + extra_rotation
        else:
            twist = 0.0
        rotated = rotate_2d(profile_2d, twist)
        if translate != (0, 0):
            rotated = rotated.copy()
            rotated[:, 0] += translate[0]
            rotated[:, 1] += translate[1]
        return rotated

    def make_wire_from_pts(pts_2d, z):
        builder = BRepBuilderAPI_MakePolygon()
        for pt in pts_2d:
            builder.Add(gp_Pnt(float(pt[0]), float(pt[1]), float(z)))
        builder.Close()
        return builder.Wire()

    # For herringbone, if spanning z=0, we need 3 profiles
    if z_start < 0 and z_end > 0:
        prof_start = get_profile_at_z(z_start)
        prof_mid = get_profile_at_z(0.0)
        prof_end = get_profile_at_z(z_end)

        wire_start = make_wire_from_pts(prof_start, z_start)
        wire_mid = make_wire_from_pts(prof_mid, 0.0)
        wire_end = make_wire_from_pts(prof_end, z_end)

        # Loft bottom half
        loft_bottom = BRepOffsetAPI_ThruSections(True)
        loft_bottom.AddWire(wire_start)
        loft_bottom.AddWire(wire_mid)
        loft_bottom.Build()

        # Loft top half
        loft_top = BRepOffsetAPI_ThruSections(True)
        loft_top.AddWire(wire_mid)
        loft_top.AddWire(wire_end)
        loft_top.Build()

        # Fuse
        fuse = BRepAlgoAPI_Fuse(loft_bottom.Shape(), loft_top.Shape())
        fuse.Build()
        return fuse.Shape()
    else:
        # Single direction helix (half of herringbone)
        prof_start = get_profile_at_z(z_start)
        prof_end = get_profile_at_z(z_end)

        wire_start = make_wire_from_pts(prof_start, z_start)
        wire_end = make_wire_from_pts(prof_end, z_end)

        loft = BRepOffsetAPI_ThruSections(True)
        loft.AddWire(wire_start)
        loft.AddWire(wire_end)
        loft.Build()
        return loft.Shape()


def create_ring_half(profile_2d, twist_per_z, z_start, z_end, extra_rotation, is_bottom):
    """
    Create one half of the ring gear with M2 self-threading holes.
    """
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    half_height = abs(z_end - z_start)
    z_base = min(z_start, z_end)

    # Create outer cylinder for this half
    cylinder = BRepPrimAPI_MakeCylinder(
        gp_Ax2(gp_Pnt(0, 0, z_base), gp_Dir(0, 0, 1)),
        ring_outer_r,
        half_height
    ).Shape()

    # Create internal gear profile shape
    gear_shape = create_gear_shape(profile_2d, twist_per_z, z_start, z_end, extra_rotation)

    # Cut internal teeth from cylinder
    ring_half = BRepAlgoAPI_Cut(cylinder, gear_shape)
    ring_half.Build()
    result_shape = ring_half.Shape()

    # Add screw holes
    screw_positions = get_screw_positions()

    for (sx, sy) in screw_positions:
        if is_bottom:
            # Bottom half: counterbored clearance hole
            clearance_hole = BRepPrimAPI_MakeCylinder(
                gp_Ax2(gp_Pnt(sx, sy, z_base), gp_Dir(0, 0, 1)),
                M2_CLEARANCE_DIA / 2,
                half_height
            ).Shape()

            counterbore = BRepPrimAPI_MakeCylinder(
                gp_Ax2(gp_Pnt(sx, sy, z_base), gp_Dir(0, 0, 1)),
                M2_HEAD_DIA / 2,
                M2_HEAD_DEPTH
            ).Shape()

            cut1 = BRepAlgoAPI_Cut(result_shape, clearance_hole)
            cut1.Build()
            cut2 = BRepAlgoAPI_Cut(cut1.Shape(), counterbore)
            cut2.Build()
            result_shape = cut2.Shape()
        else:
            # Top half: pilot hole for self-threading
            pilot_depth = half_height - 1.5
            pilot_hole = BRepPrimAPI_MakeCylinder(
                gp_Ax2(gp_Pnt(sx, sy, z_base), gp_Dir(0, 0, 1)),
                M2_TAP_DIA / 2,
                pilot_depth
            ).Shape()

            cut1 = BRepAlgoAPI_Cut(result_shape, pilot_hole)
            cut1.Build()
            result_shape = cut1.Shape()

    return result_shape


# --- Generate Sun Gear ---
print("\nGenerating Sun gear...")
sun_scaled = base_sun_profile.vertices * scale_factor
sun_offset = offset_profile_radial(sun_scaled, PROFILE_OFFSET_MM)
sun_filtered = filter_points(sun_offset)

z_half = GEAR_THICKNESS_MM / 2
sun_shape = create_gear_shape(sun_filtered, sun_twist_per_z, -z_half, z_half)
sun_cq = cq.Workplane("XY").add(cq.Shape(sun_shape))
exporters.export(sun_cq, os.path.join(OUTPUT_DIR, "sun.step"))
exporters.export(sun_cq, os.path.join(OUTPUT_DIR, "sun.stl"))
print("  Exported sun.step and sun.stl")


# --- Generate Planet Gears ---
print("\nGenerating Planet gears...")
planet_scaled = base_planet_profile.vertices * scale_factor
planet_offset = offset_profile_radial(planet_scaled, PROFILE_OFFSET_MM)

planet_shapes = []
for i in range(N_planets):
    a = 2 * np.pi * i / N_planets
    w = (1 - R_teeth / P_teeth) * a

    planet_rotated = rotate_2d(planet_offset, w)
    planet_filtered = filter_points(planet_rotated)

    pos_x = carrier_radius * math.cos(a)
    pos_y = carrier_radius * math.sin(a)

    planet_shape = create_gear_shape(
        planet_filtered, planet_twist_per_z, -z_half, z_half,
        translate=(pos_x, pos_y)
    )
    planet_shapes.append(planet_shape)

    planet_cq = cq.Workplane("XY").add(cq.Shape(planet_shape))
    exporters.export(planet_cq, os.path.join(OUTPUT_DIR, f"planet_{i}.step"))
    exporters.export(planet_cq, os.path.join(OUTPUT_DIR, f"planet_{i}.stl"))
    print(f"  Exported planet_{i}.step and planet_{i}.stl")


# --- Generate Split Ring Gear ---
print("\nGenerating Split Ring gear...")
ring_scaled = base_ring_profile.vertices * scale_factor
# For zero offset, ring also gets zero (negated zero is still zero)
ring_offset = offset_profile_radial(ring_scaled, -PROFILE_OFFSET_MM)
ring_filtered = filter_points(ring_offset)

# Bottom half: z = -z_half to 0
print("  Creating ring_bottom (with M2 counterbores)...")
ring_bottom_shape = create_ring_half(
    ring_filtered, ring_twist_per_z,
    -z_half, 0.0,
    ring_comp_rad,
    is_bottom=True
)
ring_bottom_cq = cq.Workplane("XY").add(cq.Shape(ring_bottom_shape))
exporters.export(ring_bottom_cq, os.path.join(OUTPUT_DIR, "ring_bottom.step"))
exporters.export(ring_bottom_cq, os.path.join(OUTPUT_DIR, "ring_bottom.stl"))
print("  Exported ring_bottom.step and ring_bottom.stl")

# Top half: z = 0 to z_half
print("  Creating ring_top (with M2 pilot holes)...")
ring_top_shape = create_ring_half(
    ring_filtered, ring_twist_per_z,
    0.0, z_half,
    ring_comp_rad,
    is_bottom=False
)
ring_top_cq = cq.Workplane("XY").add(cq.Shape(ring_top_shape))
exporters.export(ring_top_cq, os.path.join(OUTPUT_DIR, "ring_top.step"))
exporters.export(ring_top_cq, os.path.join(OUTPUT_DIR, "ring_top.stl"))
print("  Exported ring_top.step and ring_top.stl")


# --- Create Assembly ---
print("\nCreating assembly preview...")
try:
    from OCP.TopoDS import TopoDS_Compound
    from OCP.BRep import BRep_Builder

    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)

    builder.Add(compound, sun_shape)
    for ps in planet_shapes:
        builder.Add(compound, ps)
    builder.Add(compound, ring_bottom_shape)
    builder.Add(compound, ring_top_shape)

    assembly_cq = cq.Workplane("XY").add(cq.Shape(compound))
    exporters.export(assembly_cq, os.path.join(OUTPUT_DIR, "gearbox_assembly.step"))
    exporters.export(assembly_cq, os.path.join(OUTPUT_DIR, "gearbox_assembly.stl"))
    print("  Exported gearbox_assembly.step and gearbox_assembly.stl")

except Exception as e:
    print(f"  Assembly export failed: {e}")
    import traceback
    traceback.print_exc()


print("\n" + "=" * 60)
print("v22 GENERATION COMPLETE")
print(f"Output directory: {OUTPUT_DIR}/")
print("\n--- Key Changes from v21 ---")
print(f"  Fit: {PROFILE_OFFSET_MM:+.2f}mm (was +0.05mm interference)")
print("\n--- Files ---")
print("  - sun.step/.stl")
print(f"  - planet_0.step/.stl through planet_{N_planets-1}.step/.stl")
print("  - ring_bottom.step/.stl (M2 counterbores)")
print("  - ring_top.step/.stl (M2 pilot holes)")
print("  - gearbox_assembly.step/.stl")
print(f"\nAssembly: {N_SCREWS}x M2 self-threading screws")
print("=" * 60)
