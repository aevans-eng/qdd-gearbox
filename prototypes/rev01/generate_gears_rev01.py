"""
generate_gears_rev01.py - QDD Gearbox Rev01 Gear Generation

Based on generate_step_aaron.py with rev01 change:
- Ring wall thickness: 15mm (was 10mm in rev00)

Parameters from CATIA skeleton:
- R48/P18/S12, 3 planets, 5:1 ratio
- Ring inner diameter: 75mm (matches skeleton ring_pitch_diam)
- Face width: 18.6mm (matches skeleton gear_height)
- Ring wall: 15mm (rev01 -- increased from 10mm)
- Ring OD: 105mm (75 + 2*15)

Note: pygeartrain uses cycloidal (epi/hypo) teeth, NOT involute.
The gear_module=2.5mm skeleton param does not apply here.

Screw holes are REMOVED -- CATIA skeleton handles all fastener features.
"""

import numpy as np
import os
import math
import cadquery as cq
from cadquery import exporters

# Add pygeartrain to path (lives in qdd-gearbox/pygeartrain/)
import sys
PYGEARTRAIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "pygeartrain")
sys.path.insert(0, os.path.abspath(PYGEARTRAIN_DIR))

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


# --- Aaron's QDD Parameters ---
TARGET_RING_DIAMETER_MM = 75.0   # matches skeleton ring_pitch_diam
GEAR_THICKNESS_MM = 18.6         # full rev01 gear height
GEAR_TYPE = 'spur'               # 'spur', 'herringbone', or 'helix'
HELIX_ANGLE_DEGREES = 30.0       # ignored when GEAR_TYPE = 'spur'
CLOSE_POINT_TOLERANCE = 1e-7
SMALL_RADIUS_TOLERANCE = 1e-9
PLANET_0_ANGLE_DEG = 90.0        # planet_0 orbital angle (90 = +Y axis, 0 = +X axis)

# Gear parameters
R_teeth = 48
P_teeth = 18
S_teeth = 12
N_planets = 3                    # matches skeleton number_of_planets
b_profile = 0.5

# VALIDATE IMMEDIATELY
validate_planetary_config(R_teeth, P_teeth, S_teeth, N_planets)

# Profile offset for clearance
# Negative values shrink the external gears and enlarge the ring profile.
# Export only the next-print set by default to keep the output folder clean.
CLEARANCE_VARIANTS = [
    ("actual_print_0p13_total_clearance_top_taper_0p25x1p0", -0.065),  # 0.13 mm total mesh clearance
]
RING_OFFSET_DEG = 0.2
TOP_TAPER_OFFSET_MM = 0.25
TOP_TAPER_HEIGHT_MM = 1.0

SUN_TEST_VARIANTS = [
    "sun_test_bottom_taper_0p25x1p0_square_pocket_9p6x11_no_chamfer",
]
SUN_TEST_SQUARE_POCKET_MM = 9.6
SUN_TEST_POCKET_DEPTH_MM = 11.0

# Ring wall thickness
RING_WALL_MM = 15.0              # full rev01 ring wall

# Override helix angle for spur gears
if GEAR_TYPE == 'spur':
    HELIX_ANGLE_DEGREES = 0.0

# Output directory -- rev01 gears folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_BASE_DIR = os.path.join(SCRIPT_DIR, "gears")

print("=" * 60)
print("STEP FILE GENERATOR - Aaron's QDD Gearbox")
print(f"Gear type: {GEAR_TYPE}")
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
ring_root_r = np.max(np.linalg.norm(base_ring_profile.vertices, axis=1)) * scale_factor
ring_outer_r = TARGET_RING_DIAMETER_MM / 2 + RING_WALL_MM
ring_tooth_depth = ring_root_r - ring_inner_r
ring_solid_wall = ring_outer_r - ring_root_r


print(f"\n--- Clearance variants ---")
for variant_name, profile_offset_mm in CLEARANCE_VARIANTS:
    print(f"{variant_name:>12}: {profile_offset_mm:+.3f}mm per gear ({abs(profile_offset_mm) * 2:.3f}mm total)")
print()
print(f"--- Geometry ---")
print(f"Ring diameter: {TARGET_RING_DIAMETER_MM}mm, Thickness: {GEAR_THICKNESS_MM}mm")
print(f"Ring outer diameter: {ring_outer_r * 2}mm (with {RING_WALL_MM}mm wall)")
print(f"Top taper relief: {TOP_TAPER_OFFSET_MM:.3f}mm over {TOP_TAPER_HEIGHT_MM:.3f}mm")
print(f"Ratio: {(R_teeth + S_teeth) / S_teeth:.2f}:1")
print(f"(No screw holes -- CATIA skeleton handles fasteners)")

# Print pitch diameters for CATIA skeleton update
# For cycloidal gears, "pitch diameter" ~ where teeth mesh
# Approximate as: carrier_radius * 2 * (S or P) / (S+P) for sun/planet
sun_pitch_r = carrier_radius * S_teeth / (S_teeth + P_teeth) * 2
planet_pitch_r = carrier_radius * P_teeth / (S_teeth + P_teeth) * 2
ring_pitch_r = sun_pitch_r + 2 * planet_pitch_r
print(f"\n--- Dimensions for CATIA skeleton update ---")
print(f"Sun outer radius:    {sun_outer_r:.3f}mm  (diameter: {sun_outer_r*2:.3f}mm)")
print(f"Planet outer radius: {planet_outer_r:.3f}mm  (diameter: {planet_outer_r*2:.3f}mm)")
print(f"Ring inner radius:   {ring_inner_r:.3f}mm  (diameter: {ring_inner_r*2:.3f}mm, tooth tips)")
print(f"Ring root radius:    {ring_root_r:.3f}mm  (diameter: {ring_root_r*2:.3f}mm, tooth roots)")
print(f"Ring tooth depth:    {ring_tooth_depth:.3f}mm  (tip to root)")
print(f"Ring solid wall:     {ring_solid_wall:.3f}mm  (root to OD -- minimum solid material)")
print(f"Ring outer radius:   {ring_outer_r:.3f}mm  (diameter: {ring_outer_r*2:.3f}mm, OD)")
print(f"Carrier radius:      {carrier_radius:.3f}mm  (planet center distance from axis)")
print(f"Scale factor:        {scale_factor:.6f}")

os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

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



def create_gear_shape(
    profile_2d,
    twist_per_z,
    z_start,
    z_end,
    extra_rotation=0.0,
    translate=(0, 0),
    bottom_taper_offset_mm=0.0,
    bottom_taper_height_mm=0.0,
    top_taper_offset_mm=0.0,
    top_taper_height_mm=0.0,
):
    """
    Create gear solid using loft between two Z levels.
    """
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
    from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.gp import gp_Pnt

    def get_profile_at_z(z_val, radial_offset_mm=0.0):
        profile_for_section = profile_2d
        if abs(radial_offset_mm) > SMALL_RADIUS_TOLERANCE:
            profile_for_section = offset_profile_radial(profile_2d, radial_offset_mm)
        if abs(z_val) > SMALL_RADIUS_TOLERANCE:
            twist = abs(z_val) * twist_per_z + extra_rotation
        else:
            twist = 0.0
        rotated = rotate_2d(profile_for_section, twist)
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

    if (
        bottom_taper_height_mm > SMALL_RADIUS_TOLERANCE
        and abs(bottom_taper_offset_mm) > SMALL_RADIUS_TOLERANCE
    ):
        taper_top_z = min(z_start + bottom_taper_height_mm, z_end)
        if taper_top_z >= z_end - SMALL_RADIUS_TOLERANCE:
            loft = BRepOffsetAPI_ThruSections(True)
            loft.AddWire(make_wire_from_pts(get_profile_at_z(z_start, bottom_taper_offset_mm), z_start))
            loft.AddWire(make_wire_from_pts(get_profile_at_z(z_end, 0.0), z_end))
            loft.Build()
            return loft.Shape()

        bottom_loft = BRepOffsetAPI_ThruSections(True)
        bottom_loft.AddWire(make_wire_from_pts(get_profile_at_z(z_start, bottom_taper_offset_mm), z_start))
        bottom_loft.AddWire(make_wire_from_pts(get_profile_at_z(taper_top_z, 0.0), taper_top_z))
        bottom_loft.Build()

        upper_loft = BRepOffsetAPI_ThruSections(True)
        upper_loft.AddWire(make_wire_from_pts(get_profile_at_z(taper_top_z, 0.0), taper_top_z))
        upper_loft.AddWire(make_wire_from_pts(get_profile_at_z(z_end, 0.0), z_end))
        upper_loft.Build()

        fuse = BRepAlgoAPI_Fuse(bottom_loft.Shape(), upper_loft.Shape())
        fuse.Build()
        return fuse.Shape()

    if (
        top_taper_height_mm > SMALL_RADIUS_TOLERANCE
        and abs(top_taper_offset_mm) > SMALL_RADIUS_TOLERANCE
    ):
        taper_bottom_z = max(z_end - top_taper_height_mm, z_start)
        if taper_bottom_z <= z_start + SMALL_RADIUS_TOLERANCE:
            loft = BRepOffsetAPI_ThruSections(True)
            loft.AddWire(make_wire_from_pts(get_profile_at_z(z_start, 0.0), z_start))
            loft.AddWire(make_wire_from_pts(get_profile_at_z(z_end, top_taper_offset_mm), z_end))
            loft.Build()
            return loft.Shape()

        lower_loft = BRepOffsetAPI_ThruSections(True)
        lower_loft.AddWire(make_wire_from_pts(get_profile_at_z(z_start, 0.0), z_start))
        lower_loft.AddWire(make_wire_from_pts(get_profile_at_z(taper_bottom_z, 0.0), taper_bottom_z))
        lower_loft.Build()

        top_loft = BRepOffsetAPI_ThruSections(True)
        top_loft.AddWire(make_wire_from_pts(get_profile_at_z(taper_bottom_z, 0.0), taper_bottom_z))
        top_loft.AddWire(make_wire_from_pts(get_profile_at_z(z_end, top_taper_offset_mm), z_end))
        top_loft.Build()

        fuse = BRepAlgoAPI_Fuse(lower_loft.Shape(), top_loft.Shape())
        fuse.Build()
        return fuse.Shape()

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


def create_ring_half(
    profile_2d,
    twist_per_z,
    z_start,
    z_end,
    extra_rotation,
    top_taper_offset_mm=0.0,
    top_taper_height_mm=0.0,
):
    """
    Create one half of the ring gear (tooth geometry only, no fastener holes).
    Fastener features are handled in CATIA via skeleton-driven design.
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
    gear_shape = create_gear_shape(
        profile_2d,
        twist_per_z,
        z_start,
        z_end,
        extra_rotation,
        top_taper_offset_mm=top_taper_offset_mm,
        top_taper_height_mm=top_taper_height_mm,
    )

    # Cut internal teeth from cylinder
    ring_half = BRepAlgoAPI_Cut(cylinder, gear_shape)
    ring_half.Build()
    return ring_half.Shape()


def make_square_wire(side_mm, z):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
    from OCP.gp import gp_Pnt

    half = side_mm / 2.0
    builder = BRepBuilderAPI_MakePolygon()
    for x, y in [
        (-half, -half),
        (half, -half),
        (half, half),
        (-half, half),
    ]:
        builder.Add(gp_Pnt(float(x), float(y), float(z)))
    builder.Close()
    return builder.Wire()


def create_square_pocket_cutter(top_z, side_mm, depth_mm):
    from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections

    cutter_extension_mm = 0.2
    bottom_z = top_z - depth_mm

    loft = BRepOffsetAPI_ThruSections(True)
    loft.AddWire(make_square_wire(side_mm, top_z + cutter_extension_mm))
    loft.AddWire(make_square_wire(side_mm, bottom_z))
    loft.Build()
    return loft.Shape()


def cut_sun_square_pocket(sun_shape):
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut

    top_z = GEAR_THICKNESS_MM / 2.0
    cutter = create_square_pocket_cutter(
        top_z,
        SUN_TEST_SQUARE_POCKET_MM,
        SUN_TEST_POCKET_DEPTH_MM,
    )
    cut = BRepAlgoAPI_Cut(sun_shape, cutter)
    cut.Build()
    return cut.Shape()


def generate_variant(variant_name, profile_offset_mm):
    output_dir = os.path.join(OUTPUT_BASE_DIR, variant_name)
    step_parts_dir = os.path.join(output_dir, "parts_step")
    stl_parts_dir = os.path.join(output_dir, "parts_stl")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(step_parts_dir, exist_ok=True)
    os.makedirs(stl_parts_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print(f"Generating variant: {variant_name}")
    print(f"Profile offset: {profile_offset_mm:+.3f} mm per gear ({abs(profile_offset_mm) * 2:.3f} mm total)")
    print("=" * 60)

    z_half = GEAR_THICKNESS_MM / 2

    # --- Generate Sun Gear ---
    print("\nGenerating Sun gear...")
    sun_scaled = base_sun_profile.vertices * scale_factor
    sun_offset = offset_profile_radial(sun_scaled, profile_offset_mm)
    sun_filtered = filter_points(sun_offset)

    sun_shape = create_gear_shape(
        sun_filtered,
        sun_twist_per_z,
        -z_half,
        z_half,
        top_taper_offset_mm=-TOP_TAPER_OFFSET_MM,
        top_taper_height_mm=TOP_TAPER_HEIGHT_MM,
    )
    sun_cq = cq.Workplane("XY").add(cq.Shape(sun_shape))
    exporters.export(sun_cq, os.path.join(step_parts_dir, "sun_PRINT.step"))
    exporters.export(sun_cq, os.path.join(stl_parts_dir, "sun_PRINT.stl"))
    print("  Exported sun_PRINT.step/.stl")

    # --- Generate Planet Gears ---
    print("\nGenerating Planet gears...")
    planet_scaled = base_planet_profile.vertices * scale_factor
    planet_offset = offset_profile_radial(planet_scaled, profile_offset_mm)

    a0 = math.radians(PLANET_0_ANGLE_DEG)
    w0 = (1 - R_teeth / P_teeth) * a0

    planet_rotated = rotate_2d(planet_offset, w0)
    planet_filtered = filter_points(planet_rotated)

    planet_shape = create_gear_shape(
        planet_filtered,
        planet_twist_per_z,
        -z_half,
        z_half,
        top_taper_offset_mm=-TOP_TAPER_OFFSET_MM,
        top_taper_height_mm=TOP_TAPER_HEIGHT_MM,
    )

    planet_cq = cq.Workplane("XY").add(cq.Shape(planet_shape))
    exporters.export(planet_cq, os.path.join(step_parts_dir, "planet_PRINT.step"))
    exporters.export(planet_cq, os.path.join(stl_parts_dir, "planet_PRINT.stl"))
    print("  Exported planet_PRINT.step/.stl")

    planet_shapes_for_assembly = []
    planet_cqs_for_assembly = []
    for i in range(N_planets):
        a = 2 * np.pi * i / N_planets + math.radians(PLANET_0_ANGLE_DEG)
        w = (1 - R_teeth / P_teeth) * a
        planet_rotated_i = rotate_2d(planet_offset, w)
        planet_filtered_i = filter_points(planet_rotated_i)
        pos_x = carrier_radius * math.cos(a)
        pos_y = carrier_radius * math.sin(a)
        planet_shape_i = create_gear_shape(
            planet_filtered_i, planet_twist_per_z, -z_half, z_half,
            translate=(pos_x, pos_y),
            top_taper_offset_mm=-TOP_TAPER_OFFSET_MM,
            top_taper_height_mm=TOP_TAPER_HEIGHT_MM,
        )
        planet_shapes_for_assembly.append(planet_shape_i)
        planet_cqs_for_assembly.append((f"planet_{i}_PRINT", cq.Workplane("XY").add(cq.Shape(planet_shape_i))))

    # --- Generate Ring Gear ---
    ring_scaled = base_ring_profile.vertices * scale_factor
    ring_offset = offset_profile_radial(ring_scaled, -profile_offset_mm)
    ring_filtered = filter_points(ring_offset)

    if GEAR_TYPE == 'herringbone':
        raise ValueError("Test-print export currently supports spur/helix single-piece ring only.")

    else:
        print("\nGenerating Ring gear...")
        ring_shape = create_ring_half(
            ring_filtered, ring_twist_per_z,
            -z_half, z_half,
            ring_comp_rad,
            top_taper_offset_mm=TOP_TAPER_OFFSET_MM,
            top_taper_height_mm=TOP_TAPER_HEIGHT_MM,
        )
        ring_cq = cq.Workplane("XY").add(cq.Shape(ring_shape))
        exporters.export(ring_cq, os.path.join(step_parts_dir, "ring_PRINT.step"))
        exporters.export(ring_cq, os.path.join(stl_parts_dir, "ring_PRINT.stl"))
        print("  Exported ring_PRINT.step/.stl")

    print("\nCreating STEP assembly...")
    try:
        step_assembly = cq.Assembly(name=f"rev01_gears_{variant_name}")
        step_assembly.add(sun_cq, name="sun_PRINT")
        for planet_name, planet_cq_i in planet_cqs_for_assembly:
            step_assembly.add(planet_cq_i, name=planet_name)
        step_assembly.add(ring_cq, name="ring_PRINT")

        step_assembly_path = os.path.join(output_dir, "gears_assembly_export.stp")
        step_assembly.save(step_assembly_path, exportType="STEP")
        print(f"  Exported {os.path.basename(step_assembly_path)}")
    except Exception as e:
        print(f"  STEP assembly export failed: {e}")
        import traceback
        traceback.print_exc()

    print("\nCreating multi-body CAD part...")
    try:
        from OCP.TopoDS import TopoDS_Compound
        from OCP.BRep import BRep_Builder
        from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
        from OCP.Interface import Interface_Static

        compound = TopoDS_Compound()
        builder = BRep_Builder()
        builder.MakeCompound(compound)

        builder.Add(compound, sun_shape)
        for planet_shape_i in planet_shapes_for_assembly:
            builder.Add(compound, planet_shape_i)
        builder.Add(compound, ring_shape)

        writer = STEPControl_Writer()
        Interface_Static.SetIVal_s("write.step.assembly", 0)
        writer.Transfer(compound, STEPControl_AsIs)
        status = writer.Write(os.path.join(output_dir, "gearbox_CAD.step"))
        if status == 1:
            print("  Exported gearbox_CAD.step")
        else:
            print(f"  STEP write returned status {status}")
    except Exception as e:
        print(f"  CAD export failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n--- Variant output ---")
    print(f"  {output_dir}")
    print("  - parts_step/")
    print("  - parts_stl/")
    print("  - gears_assembly_export.stp")
    print("  - gearbox_CAD.step")


def generate_sun_test_variant(variant_name, profile_offset_mm):
    output_dir = os.path.join(OUTPUT_BASE_DIR, variant_name)
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print(f"Generating sun test variant: {variant_name}")
    print(f"Profile offset: {profile_offset_mm:+.3f} mm per gear ({abs(profile_offset_mm) * 2:.3f} mm total)")
    print(
        "Square pocket: "
        f"{SUN_TEST_SQUARE_POCKET_MM:.3f} mm x {SUN_TEST_SQUARE_POCKET_MM:.3f} mm, "
        f"{SUN_TEST_POCKET_DEPTH_MM:.3f} mm deep, no chamfer"
    )
    print("=" * 60)

    z_half = GEAR_THICKNESS_MM / 2
    sun_scaled = base_sun_profile.vertices * scale_factor
    sun_offset = offset_profile_radial(sun_scaled, profile_offset_mm)
    sun_filtered = filter_points(sun_offset)

    sun_shape = create_gear_shape(
        sun_filtered,
        sun_twist_per_z,
        -z_half,
        z_half,
        bottom_taper_offset_mm=-TOP_TAPER_OFFSET_MM,
        bottom_taper_height_mm=TOP_TAPER_HEIGHT_MM,
    )
    sun_with_pocket_shape = cut_sun_square_pocket(sun_shape)
    sun_cq = cq.Workplane("XY").add(cq.Shape(sun_with_pocket_shape))

    step_path = os.path.join(output_dir, "sun_TEST.step")
    stl_path = os.path.join(output_dir, "sun_TEST.stl")
    exporters.export(sun_cq, step_path)
    exporters.export(sun_cq, stl_path)
    print(f"  Exported {step_path}")
    print(f"  Exported {stl_path}")


for variant_name, profile_offset_mm in CLEARANCE_VARIANTS:
    generate_variant(variant_name, profile_offset_mm)

for variant_name in SUN_TEST_VARIANTS:
    generate_sun_test_variant(variant_name, -0.065)


print("\n" + "=" * 60)
print(f"GENERATION COMPLETE -- {GEAR_TYPE}")
print(f"Output base directory: {OUTPUT_BASE_DIR}/")
print("Generated variants:")
for variant_name, profile_offset_mm in CLEARANCE_VARIANTS:
    print(f"  - {variant_name}: {profile_offset_mm:+.3f} mm per gear")
for variant_name in SUN_TEST_VARIANTS:
    print(f"  - {variant_name}: sun test")
print("\nNext: Import the chosen variant's gearbox_CAD.step into CATIA as a part, constrain to skeleton.")
print("=" * 60)
