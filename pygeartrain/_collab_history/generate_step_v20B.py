"""
generate_step_v20B.py - Split Ring Herringbone Planetary Gearbox (4 Planets)

Based on v20 but with ring gear split at z=0 for assembly (not print-in-place).
Includes M2 self-threading screw holes near outer edge for bolting the two ring halves together.
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

# --- User Defined Parameters ---
TARGET_RING_DIAMETER_MM = 80.0
GEAR_THICKNESS_MM = 22
HELIX_ANGLE_DEGREES = 20.0
GEAR_TYPE = 'herringbone'
CLOSE_POINT_TOLERANCE = 1e-7
SMALL_RADIUS_TOLERANCE = 1e-9

# Gear parameters
R_teeth = 48
P_teeth = 18
S_teeth = 12
N_planets = 4
b_profile = 0.5

# PRINT CLEARANCE
PROFILE_OFFSET_MM = -0.10
RING_OFFSET_DEG = 0.2

# Ring wall thickness
RING_WALL_MM = 8.0

# M2 Self-threading screw parameters
M2_CLEARANCE_DIA = 2.4      # Clearance hole for M2 screw
M2_TAP_DIA = 1.6            # Pilot hole for self-threading into plastic
M2_HEAD_DIA = 3.8           # Socket head cap screw head diameter
M2_HEAD_DEPTH = 2.2         # Counterbore depth for screw head
N_SCREWS = 6                # Number of screws around the ring
SCREW_RADIUS_MM = None      # Will be calculated (near outer edge)

# Output directory
OUTPUT_DIR = "step_output_v20B"

print("=" * 60)
print("STEP FILE GENERATOR v20B (Split Ring, M3 Bolts)")
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

# Calculate screw hole radius (near outer edge, 2mm inset from outer diameter)
SCREW_RADIUS_MM = ring_outer_r - (M2_HEAD_DIA / 2) - 0.5  # Leave clearance from edge

print(f"Gear Configuration: R{R_teeth}/P{P_teeth}/S{S_teeth}, {N_planets} planets")
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
    For herringbone, z_start and z_end should be on opposite sides of z=0,
    or you need to include z=0 as a middle profile.
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
        # Full herringbone - need z_start, 0, z_end
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
    is_bottom=True: counterbored clearance holes (screw head side)
    is_bottom=False: pilot holes for self-threading (thread side)
    """
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform

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
            # Clearance hole goes all the way through
            clearance_hole = BRepPrimAPI_MakeCylinder(
                gp_Ax2(gp_Pnt(sx, sy, z_base), gp_Dir(0, 0, 1)),
                M2_CLEARANCE_DIA / 2,
                half_height
            ).Shape()

            # Counterbore at bottom face
            counterbore = BRepPrimAPI_MakeCylinder(
                gp_Ax2(gp_Pnt(sx, sy, z_base), gp_Dir(0, 0, 1)),
                M2_HEAD_DIA / 2,
                M2_HEAD_DEPTH
            ).Shape()

            # Cut both from ring
            cut1 = BRepAlgoAPI_Cut(result_shape, clearance_hole)
            cut1.Build()
            cut2 = BRepAlgoAPI_Cut(cut1.Shape(), counterbore)
            cut2.Build()
            result_shape = cut2.Shape()
        else:
            # Top half: pilot hole for self-threading (smaller diameter)
            pilot_depth = half_height - 1.5  # Leave 1.5mm at top
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
ring_offset = offset_profile_radial(ring_scaled, -PROFILE_OFFSET_MM)
ring_filtered = filter_points(ring_offset)

# Bottom half: z = -z_half to 0 (with counterbored clearance holes)
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

# Top half: z = 0 to z_half (with pilot holes for self-threading)
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


# --- Create Assembly (for visualization) ---
print("\nCreating assembly preview...")
try:
    from OCP.TopoDS import TopoDS_Compound
    from OCP.BRep import BRep_Builder

    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)

    # Add sun
    builder.Add(compound, sun_shape)

    # Add planets
    for ps in planet_shapes:
        builder.Add(compound, ps)

    # Add both ring halves
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
print("v20B GENERATION COMPLETE")
print(f"Output directory: {OUTPUT_DIR}/")
print("\nFiles:")
print("  - sun.step/.stl")
print("  - planet_0.step/.stl through planet_3.step/.stl")
print("  - ring_bottom.step/.stl (M2 counterbores, screw head side)")
print("  - ring_top.step/.stl (M2 pilot holes, self-threading side)")
print("  - gearbox_assembly.step/.stl (preview)")
print(f"\nAssembly: {N_SCREWS}x M2 self-threading socket head screws")
print(f"Screw length: ~{GEAR_THICKNESS_MM/2 - 1.5:.0f}mm (self-threads into top half)")
print("=" * 60)
