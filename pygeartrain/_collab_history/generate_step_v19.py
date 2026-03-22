"""
generate_step_v19.py - Print-in-Place Herringbone Planetary Gearbox (Optimized)

Generates STEP/STL files with optimized clearance for print-in-place FDM.
Uses 0.15mm total clearance - tight but printable on well-tuned printers.
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

# --- User Defined Parameters (same as v17) ---
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
N_planets = 3
b_profile = 0.5

# PRINT-IN-PLACE CLEARANCE (OPTIMIZED)
# Each gear thinned by this amount → total mesh clearance = 2x this value
# -0.10mm per gear = 0.20mm total clearance
PROFILE_OFFSET_MM = -0.10
RING_OFFSET_DEG = 0.2

# Output directory
OUTPUT_DIR = "step_output_v19"

print("=" * 60)
print("STEP FILE GENERATOR v19 (Print-in-Place, 0.20mm clearance)")
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

print(f"Gear Configuration: R{R_teeth}/P{P_teeth}/S{S_teeth}, {N_planets} planets")
print(f"Ring diameter: {TARGET_RING_DIAMETER_MM}mm, Thickness: {GEAR_THICKNESS_MM}mm")
print(f"Ratio: {(R_teeth + S_teeth) / S_teeth:.2f}:1")

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


def points_to_spline(points_2d, z_val):
    """Convert 2D points to 3D tuples for CadQuery spline."""
    pts = [(float(p[0]), float(p[1]), float(z_val)) for p in points_2d]
    # Close the profile
    if np.linalg.norm(np.array(pts[-1][:2]) - np.array(pts[0][:2])) > CLOSE_POINT_TOLERANCE:
        pts.append(pts[0])
    return pts


def create_herringbone_loft(profile_2d, twist_per_z, z_half, extra_rotation=0.0, translate=(0, 0)):
    """Create a herringbone solid by lofting between z_neg, z0, z_pos profiles."""

    # Generate profiles at each Z level
    z_levels = [-z_half, 0.0, z_half]
    wires = []

    for z_val in z_levels:
        # Calculate twist for this Z level
        if abs(z_val) > SMALL_RADIUS_TOLERANCE:
            twist = abs(z_val) * twist_per_z + extra_rotation
        else:
            twist = 0.0

        # Rotate profile
        rotated = rotate_2d(profile_2d, twist)

        # Translate if needed
        if translate != (0, 0):
            rotated = rotated.copy()
            rotated[:, 0] += translate[0]
            rotated[:, 1] += translate[1]

        # Create 3D points
        pts_3d = points_to_spline(rotated, z_val)

        # Create wire from spline
        wire = cq.Workplane("XY").workplane(offset=z_val).spline(pts_3d, periodic=True).close().val()
        wires.append(wire)

    # Create loft - for herringbone we loft all three profiles
    try:
        solid = cq.Workplane("XY").add(wires[0]).toPending().loft(ruled=False)
        # This simple approach may not work for herringbone
        # Let's try a different approach - two half-lofts
    except Exception as e:
        print(f"  Loft failed: {e}")
        return None

    return solid


def create_gear_solid(profile_2d, twist_per_z, z_half, name, extra_rotation=0.0, translate=(0, 0)):
    """Create gear solid using two lofts for herringbone (z_neg→z0, z0→z_pos)."""

    print(f"  Creating {name}...")

    # Generate profiles at each Z level
    profiles = {}
    for z_name, z_val in [('neg', -z_half), ('mid', 0.0), ('pos', z_half)]:
        if abs(z_val) > SMALL_RADIUS_TOLERANCE:
            twist = abs(z_val) * twist_per_z + extra_rotation
        else:
            twist = 0.0

        rotated = rotate_2d(profile_2d, twist)

        if translate != (0, 0):
            rotated = rotated.copy()
            rotated[:, 0] += translate[0]
            rotated[:, 1] += translate[1]

        profiles[z_name] = (rotated, z_val)

    # Create 3D point lists
    def make_pts_3d(pts_2d, z):
        pts_3d = [(float(p[0]), float(p[1]), float(z)) for p in pts_2d]
        return pts_3d

    pts_neg = make_pts_3d(profiles['neg'][0], profiles['neg'][1])
    pts_mid = make_pts_3d(profiles['mid'][0], profiles['mid'][1])
    pts_pos = make_pts_3d(profiles['pos'][0], profiles['pos'][1])

    try:
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeWire
        from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
        from OCP.gp import gp_Pnt
        from OCP.TopoDS import TopoDS_Wire

        def make_wire_from_pts(pts_3d):
            """Create a closed wire from 3D points using polygon."""
            builder = BRepBuilderAPI_MakePolygon()
            for pt in pts_3d:
                builder.Add(gp_Pnt(pt[0], pt[1], pt[2]))
            builder.Close()
            return builder.Wire()

        wire_neg = make_wire_from_pts(pts_neg)
        wire_mid = make_wire_from_pts(pts_mid)
        wire_pos = make_wire_from_pts(pts_pos)

        # Create bottom half loft (neg to mid)
        loft_bottom = BRepOffsetAPI_ThruSections(True)  # True = solid
        loft_bottom.AddWire(wire_neg)
        loft_bottom.AddWire(wire_mid)
        loft_bottom.Build()

        if not loft_bottom.IsDone():
            print(f"    Bottom loft failed for {name}")
            return None

        # Create top half loft (mid to pos)
        loft_top = BRepOffsetAPI_ThruSections(True)
        loft_top.AddWire(wire_mid)
        loft_top.AddWire(wire_pos)
        loft_top.Build()

        if not loft_top.IsDone():
            print(f"    Top loft failed for {name}")
            return None

        # Union the two halves
        from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
        fuse = BRepAlgoAPI_Fuse(loft_bottom.Shape(), loft_top.Shape())
        fuse.Build()

        if not fuse.IsDone():
            print(f"    Fuse failed for {name}")
            return None

        # Wrap in CadQuery workplane for export
        result = cq.Workplane("XY").add(cq.Shape(fuse.Shape()))
        return result

    except Exception as e:
        print(f"    Error creating {name}: {e}")
        import traceback
        traceback.print_exc()
        return None


# --- Generate Sun Gear ---
print("\nGenerating Sun gear...")
sun_scaled = base_sun_profile.vertices * scale_factor
sun_offset = offset_profile_radial(sun_scaled, PROFILE_OFFSET_MM)
sun_filtered = filter_points(sun_offset)

sun_solid = create_gear_solid(sun_filtered, sun_twist_per_z, GEAR_THICKNESS_MM/2, "sun")
if sun_solid:
    exporters.export(sun_solid, os.path.join(OUTPUT_DIR, "sun.step"))
    exporters.export(sun_solid, os.path.join(OUTPUT_DIR, "sun.stl"))
    print("  Exported sun.step and sun.stl")


# --- Generate Planet Gears ---
print("\nGenerating Planet gears...")
planet_scaled = base_planet_profile.vertices * scale_factor
planet_offset = offset_profile_radial(planet_scaled, PROFILE_OFFSET_MM)

for i in range(N_planets):
    a = 2 * np.pi * i / N_planets
    w = (1 - R_teeth / P_teeth) * a

    planet_rotated = rotate_2d(planet_offset, w)
    planet_filtered = filter_points(planet_rotated)

    pos_x = carrier_radius * math.cos(a)
    pos_y = carrier_radius * math.sin(a)

    planet_solid = create_gear_solid(
        planet_filtered, planet_twist_per_z, GEAR_THICKNESS_MM/2,
        f"planet_{i}", translate=(pos_x, pos_y)
    )

    if planet_solid:
        exporters.export(planet_solid, os.path.join(OUTPUT_DIR, f"planet_{i}.step"))
        exporters.export(planet_solid, os.path.join(OUTPUT_DIR, f"planet_{i}.stl"))
        print(f"  Exported planet_{i}.step and planet_{i}.stl")


# --- Generate Ring Gear ---
print("\nGenerating Ring gear...")
ring_scaled = base_ring_profile.vertices * scale_factor
ring_offset = offset_profile_radial(ring_scaled, -PROFILE_OFFSET_MM)  # Opposite for internal gear
ring_filtered = filter_points(ring_offset)

# Ring needs extra compensation rotation at z != 0
ring_solid = create_gear_solid(
    ring_filtered, ring_twist_per_z, GEAR_THICKNESS_MM/2,
    "ring", extra_rotation=ring_comp_rad
)

if ring_solid:
    # For 3D printing, we need the ring as a solid cylinder with internal teeth cut out
    # Create outer cylinder and subtract the internal gear shape
    ring_outer_r = TARGET_RING_DIAMETER_MM / 2 + 5  # 5mm wall thickness

    try:
        # Create outer cylinder
        outer_cylinder = (cq.Workplane("XY")
                         .cylinder(GEAR_THICKNESS_MM, ring_outer_r, centered=(True, True, True)))

        # The ring_solid is the internal profile - we need to subtract it
        # Actually, for internal gear, ring_solid represents the void
        # Let's just export the ring profile as-is for now
        exporters.export(ring_solid, os.path.join(OUTPUT_DIR, "ring_internal.step"))
        exporters.export(ring_solid, os.path.join(OUTPUT_DIR, "ring_internal.stl"))

        # Create printable ring (cylinder with internal teeth)
        # This requires boolean subtraction
        ring_printable = outer_cylinder.cut(ring_solid)
        exporters.export(ring_printable, os.path.join(OUTPUT_DIR, "ring.step"))
        exporters.export(ring_printable, os.path.join(OUTPUT_DIR, "ring.stl"))
        print("  Exported ring.step and ring.stl (with 5mm wall)")

    except Exception as e:
        print(f"  Ring boolean failed: {e}")
        # Just export internal profile
        exporters.export(ring_solid, os.path.join(OUTPUT_DIR, "ring.step"))
        print("  Exported ring.step (internal profile only)")


# --- Create Assembled Version (Print-in-Place) ---
print("\nCreating assembled gearbox (print-in-place)...")

try:
    # Collect all solids for assembly
    assembly_solids = []

    # Re-generate all gears and collect their OCP shapes
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.TopoDS import TopoDS_Compound
    from OCP.BRep import BRep_Builder
    from OCP.gp import gp_Trsf, gp_Vec
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform

    def get_gear_shape(profile_2d, twist_per_z, z_half, extra_rotation=0.0, translate=(0, 0)):
        """Generate gear shape (returns OCP TopoDS_Shape)."""
        profiles = {}
        for z_name, z_val in [('neg', -z_half), ('mid', 0.0), ('pos', z_half)]:
            if abs(z_val) > SMALL_RADIUS_TOLERANCE:
                twist = abs(z_val) * twist_per_z + extra_rotation
            else:
                twist = 0.0
            rotated = rotate_2d(profile_2d, twist)
            if translate != (0, 0):
                rotated = rotated.copy()
                rotated[:, 0] += translate[0]
                rotated[:, 1] += translate[1]
            profiles[z_name] = (rotated, z_val)

        def make_pts_3d(pts_2d, z):
            return [(float(p[0]), float(p[1]), float(z)) for p in pts_2d]

        pts_neg = make_pts_3d(profiles['neg'][0], profiles['neg'][1])
        pts_mid = make_pts_3d(profiles['mid'][0], profiles['mid'][1])
        pts_pos = make_pts_3d(profiles['pos'][0], profiles['pos'][1])

        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
        from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
        from OCP.gp import gp_Pnt

        def make_wire_from_pts(pts_3d):
            builder = BRepBuilderAPI_MakePolygon()
            for pt in pts_3d:
                builder.Add(gp_Pnt(pt[0], pt[1], pt[2]))
            builder.Close()
            return builder.Wire()

        wire_neg = make_wire_from_pts(pts_neg)
        wire_mid = make_wire_from_pts(pts_mid)
        wire_pos = make_wire_from_pts(pts_pos)

        loft_bottom = BRepOffsetAPI_ThruSections(True)
        loft_bottom.AddWire(wire_neg)
        loft_bottom.AddWire(wire_mid)
        loft_bottom.Build()

        loft_top = BRepOffsetAPI_ThruSections(True)
        loft_top.AddWire(wire_mid)
        loft_top.AddWire(wire_pos)
        loft_top.Build()

        fuse = BRepAlgoAPI_Fuse(loft_bottom.Shape(), loft_top.Shape())
        fuse.Build()

        return fuse.Shape()

    # Get sun shape
    sun_shape = get_gear_shape(sun_filtered, sun_twist_per_z, GEAR_THICKNESS_MM/2)
    assembly_solids.append(sun_shape)
    print("  Added sun to assembly")

    # Get planet shapes (already positioned)
    for i in range(N_planets):
        a = 2 * np.pi * i / N_planets
        w = (1 - R_teeth / P_teeth) * a
        planet_rotated = rotate_2d(planet_offset, w)
        planet_filtered_i = filter_points(planet_rotated)
        pos_x = carrier_radius * math.cos(a)
        pos_y = carrier_radius * math.sin(a)

        planet_shape = get_gear_shape(
            planet_filtered_i, planet_twist_per_z, GEAR_THICKNESS_MM/2,
            translate=(pos_x, pos_y)
        )
        assembly_solids.append(planet_shape)
        print(f"  Added planet_{i} to assembly")

    # Get ring shape (with outer wall for printing)
    ring_shape = get_gear_shape(
        ring_filtered, ring_twist_per_z, GEAR_THICKNESS_MM/2,
        extra_rotation=ring_comp_rad
    )

    # Create outer cylinder for ring
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    ring_outer_r = TARGET_RING_DIAMETER_MM / 2 + 5  # 5mm wall
    cylinder = BRepPrimAPI_MakeCylinder(
        gp_Ax2(gp_Pnt(0, 0, -GEAR_THICKNESS_MM/2), gp_Dir(0, 0, 1)),
        ring_outer_r,
        GEAR_THICKNESS_MM
    ).Shape()

    # Cut internal gear profile from cylinder
    ring_with_wall = BRepAlgoAPI_Cut(cylinder, ring_shape)
    ring_with_wall.Build()
    assembly_solids.append(ring_with_wall.Shape())
    print("  Added ring to assembly")

    # Combine all into a compound (keeps parts separate for print-in-place)
    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)

    for solid in assembly_solids:
        builder.Add(compound, solid)

    # Export assembled version
    assembly_cq = cq.Workplane("XY").add(cq.Shape(compound))
    exporters.export(assembly_cq, os.path.join(OUTPUT_DIR, "gearbox_assembled.step"))
    exporters.export(assembly_cq, os.path.join(OUTPUT_DIR, "gearbox_assembled.stl"))
    print("\n  Exported gearbox_assembled.step and gearbox_assembled.stl")

except Exception as e:
    print(f"  Assembly creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print(f"STEP GENERATION COMPLETE")
print(f"Output directory: {OUTPUT_DIR}/")
print("Files for 3D printing:")
print("  - Individual gears: sun.stl, planet_0/1/2.stl, ring.stl")
print("  - Print-in-place assembly: gearbox_assembled.stl")
print("=" * 60)
