"""
generate_step_aaron_involute.py - QDD Gearbox involute planetary gear generation

This is an isolated copy of the original STEP generator. The cycloidal exporter
remains untouched in generate_step_aaron.py.

Scope of this copy:
- Standard involute spur / helix / herringbone geometry
- External involute sun + planets
- Internal involute ring generated as a cut profile

Notes:
- This uses standard module / pressure-angle geometry, unlike the original
  cycloidal path.
- The ring pitch diameter target is kept at 75 mm to stay aligned with the
  existing QDD skeleton reference.
- This copy uses print-oriented tweaks: higher pressure angle, stub teeth,
  added root blending, and slightly more backlash than the cycloidal export.
"""

import math
import os
import sys

import cadquery as cq
import matplotlib
import numpy as np
from cadquery import exporters
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Add project root to path for shared calculator helpers.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from calc.gear_geometry import compute_contact_ratio
from calc.utils.data import GearParams


def normalize(vector):
    magnitude = np.linalg.norm(vector)
    if magnitude < 1e-9:
        return np.zeros_like(vector)
    return vector / magnitude


def cubic_bezier(start, control_1, control_2, end, num_points):
    t = np.linspace(0.0, 1.0, num_points)[:, None]
    omt = 1.0 - t
    return (
        omt**3 * start
        + 3.0 * omt**2 * t * control_1
        + 3.0 * omt * t**2 * control_2
        + t**3 * end
    )


def tangential_direction(angle_rad):
    return np.array([-math.sin(angle_rad), math.cos(angle_rad)])


def blend_root_segment(start_point, end_point, start_tangent, end_tangent, blend_radius_mm):
    chord = np.linalg.norm(end_point - start_point)
    if chord < 1e-6 or blend_radius_mm <= 0.0:
        return np.vstack((start_point, end_point))

    handle = min(blend_radius_mm, 0.45 * chord)
    control_1 = start_point + normalize(start_tangent) * handle
    control_2 = end_point - normalize(end_tangent) * handle
    return cubic_bezier(start_point, control_1, control_2, end_point, ROOT_BLEND_POINTS)


def external_gear_radii(gear):
    pitch_radius = gear.pitch_diameter_mm / 2.0
    base_radius = gear.base_diameter_mm / 2.0
    tip_radius = pitch_radius + ADDENDUM_COEFF * gear.module_mm
    root_radius = pitch_radius - DEDENDUM_COEFF * gear.module_mm
    return pitch_radius, base_radius, tip_radius, root_radius


def internal_gear_radii(tooth_count, module_mm, pressure_angle_deg):
    pitch_radius = 0.5 * module_mm * tooth_count
    base_radius = pitch_radius * math.cos(math.radians(pressure_angle_deg))
    tip_radius = pitch_radius - ADDENDUM_COEFF * module_mm
    root_radius = pitch_radius + DEDENDUM_COEFF * module_mm
    return pitch_radius, base_radius, tip_radius, root_radius


def validate_planetary_config(ring_teeth, planet_teeth, sun_teeth, planet_count):
    """
    Validate a standard single-stage planetary set.
    """
    errors = []

    expected_ring = sun_teeth + 2 * planet_teeth
    if ring_teeth != expected_ring:
        errors.append(
            f"MESH CONSTRAINT FAILED: R must equal S + 2P\n"
            f"  Got R={ring_teeth}, but S + 2P = {sun_teeth} + 2({planet_teeth}) = {expected_ring}"
        )

    sum_rs = ring_teeth + sun_teeth
    if sum_rs % planet_count != 0:
        valid_counts = [n for n in range(1, sum_rs + 1) if sum_rs % n == 0 and n <= 8]
        errors.append(
            f"ASSEMBLY CONSTRAINT FAILED: (R + S) must be divisible by N\n"
            f"  Got (R + S) = {sum_rs}, N = {planet_count}\n"
            f"  Valid N values for this gear set: {valid_counts}"
        )

    carrier_radius = 0.5 * MODULE_MM * (sun_teeth + planet_teeth)
    planet_outer_radius = 0.5 * MODULE_MM * planet_teeth + ADDENDUM_COEFF * MODULE_MM
    planet_spacing = 2.0 * carrier_radius * math.sin(math.pi / planet_count)

    if planet_spacing <= 2.0 * planet_outer_radius:
        errors.append(
            f"PLANET INTERFERENCE: planets overlap\n"
            f"  Planet spacing = {planet_spacing:.3f} mm\n"
            f"  Need > {2.0 * planet_outer_radius:.3f} mm"
        )

    if sun_teeth < 6:
        errors.append(f"SUN TOO SMALL: S={sun_teeth} teeth")
    if planet_teeth < 6:
        errors.append(f"PLANET TOO SMALL: P={planet_teeth} teeth")
    if planet_count < 2 or planet_count > 8:
        errors.append(f"INVALID PLANET COUNT: N={planet_count}")

    if errors:
        raise ValueError(
            "\n".join(
                [
                    "=" * 60,
                    "INVOLUTE PLANETARY CONFIGURATION INVALID",
                    "=" * 60,
                    "",
                    *errors,
                    "",
                    "=" * 60,
                ]
            )
        )


def rotate_2d(points, angle_rad):
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    rot = np.array([[c, -s], [s, c]])
    return points @ rot.T


def polar(radius, angle_rad):
    return np.array([radius * math.cos(angle_rad), radius * math.sin(angle_rad)])


def involute_roll_angle(base_radius, target_radius):
    if target_radius < base_radius:
        return 0.0
    return math.sqrt(max((target_radius / base_radius) ** 2 - 1.0, 0.0))


def involute_xy(base_radius, roll_angles):
    t = np.asarray(roll_angles)
    x = base_radius * (np.cos(t) + t * np.sin(t))
    y = base_radius * (np.sin(t) - t * np.cos(t))
    return np.column_stack((x, y))


def arc_points(radius, start_angle, end_angle, num_points):
    if end_angle < start_angle:
        end_angle += 2.0 * math.pi
    angles = np.linspace(start_angle, end_angle, num_points)
    return np.column_stack((radius * np.cos(angles), radius * np.sin(angles)))


def dedupe_points(points, tol=1e-7):
    deduped = [points[0]]
    for point in points[1:]:
        if np.linalg.norm(point - deduped[-1]) > tol:
            deduped.append(point)
    return np.array(deduped)


def external_involute_tooth(center_angle, gear, flank_points=24, arc_points_count=12):
    """
    Build one external gear tooth boundary from lower root to upper root.
    """
    _, base_radius, tip_radius, root_radius = external_gear_radii(gear)

    alpha = math.radians(gear.pressure_angle_deg)
    inv_alpha = math.tan(alpha) - alpha
    base_half_angle = math.pi / (2.0 * gear.num_teeth) + inv_alpha

    flank_start_radius = max(base_radius, root_radius)
    t_start = involute_roll_angle(base_radius, flank_start_radius)
    t_tip = involute_roll_angle(base_radius, tip_radius)
    t_values = np.linspace(t_start, t_tip, flank_points)

    raw = involute_xy(base_radius, t_values)
    upper_flank = rotate_2d(raw * np.array([1.0, -1.0]), center_angle + base_half_angle)
    lower_flank = rotate_2d(raw, center_angle - base_half_angle)

    lower_root_angle = math.atan2(lower_flank[0, 1], lower_flank[0, 0])
    upper_root_angle = math.atan2(upper_flank[0, 1], upper_flank[0, 0])
    lower_root = polar(root_radius, lower_root_angle)
    upper_root = polar(root_radius, upper_root_angle)

    tip_arc = arc_points(
        tip_radius,
        math.atan2(lower_flank[-1, 1], lower_flank[-1, 0]),
        math.atan2(upper_flank[-1, 1], upper_flank[-1, 0]),
        arc_points_count,
    )

    lower_blend = blend_root_segment(
        lower_root,
        lower_flank[0],
        tangential_direction(lower_root_angle),
        lower_flank[1] - lower_flank[0],
        ROOT_BLEND_RADIUS_MM,
    )
    upper_blend = blend_root_segment(
        upper_flank[0],
        upper_root,
        upper_flank[0] - upper_flank[1],
        tangential_direction(upper_root_angle),
        ROOT_BLEND_RADIUS_MM,
    )

    boundary = [lower_root]
    boundary.extend(lower_blend[1:])
    boundary.extend(lower_flank[1:])
    boundary.extend(tip_arc[1:])

    upper_reverse = upper_flank[::-1]
    if np.linalg.norm(boundary[-1] - upper_reverse[0]) > 1e-7:
        boundary.append(upper_reverse[0])
    boundary.extend(upper_reverse[1:])
    boundary.extend(upper_blend[1:])

    return {
        "boundary": dedupe_points(np.array(boundary)),
        "lower_root": lower_root,
        "upper_root": upper_root,
    }


def internal_involute_tooth(center_angle, tooth_count, module_mm, pressure_angle_deg, flank_points=24, arc_points_count=12):
    """
    Build one internal ring tooth boundary from lower root to upper root.

    Returned points trace the cavity boundary for one tooth pocket.
    """
    _, base_radius, tip_radius, root_radius = internal_gear_radii(tooth_count, module_mm, pressure_angle_deg)

    alpha = math.radians(pressure_angle_deg)
    inv_alpha = math.tan(alpha) - alpha
    base_half_angle = math.pi / (2.0 * tooth_count) - inv_alpha

    flank_start_radius = max(base_radius, root_radius)
    flank_end_radius = max(base_radius, tip_radius)
    t_root = involute_roll_angle(base_radius, flank_start_radius)
    t_tip = involute_roll_angle(base_radius, flank_end_radius)
    t_values = np.linspace(t_root, t_tip, flank_points)

    raw = involute_xy(base_radius, t_values)
    upper_flank = rotate_2d(raw, center_angle + base_half_angle)
    lower_flank = rotate_2d(raw * np.array([1.0, -1.0]), center_angle - base_half_angle)

    lower_root = lower_flank[0]
    upper_root = upper_flank[0]
    lower_tip = polar(tip_radius, math.atan2(lower_flank[-1, 1], lower_flank[-1, 0]))
    upper_tip = polar(tip_radius, math.atan2(upper_flank[-1, 1], upper_flank[-1, 0]))

    tip_arc = arc_points(
        tip_radius,
        math.atan2(lower_tip[1], lower_tip[0]),
        math.atan2(upper_tip[1], upper_tip[0]),
        arc_points_count,
    )

    lower_root_angle = math.atan2(lower_root[1], lower_root[0])
    upper_root_angle = math.atan2(upper_root[1], upper_root[0])
    lower_blend = blend_root_segment(
        lower_root,
        lower_flank[0],
        tangential_direction(lower_root_angle),
        lower_flank[1] - lower_flank[0],
        ROOT_BLEND_RADIUS_MM,
    )
    upper_blend = blend_root_segment(
        upper_flank[0],
        upper_root,
        upper_flank[0] - upper_flank[1],
        tangential_direction(upper_root_angle),
        ROOT_BLEND_RADIUS_MM,
    )

    boundary = [lower_root]
    boundary.extend(lower_blend[1:])
    boundary.extend(lower_flank[1:])
    if np.linalg.norm(boundary[-1] - lower_tip) > 1e-7:
        boundary.append(lower_tip)
    boundary.extend(tip_arc[1:])
    if np.linalg.norm(boundary[-1] - upper_tip) > 1e-7:
        boundary.append(upper_tip)

    upper_reverse = upper_flank[::-1]
    if np.linalg.norm(boundary[-1] - upper_reverse[0]) > 1e-7:
        boundary.append(upper_reverse[0])
    boundary.extend(upper_reverse[1:])
    boundary.extend(upper_blend[1:])

    return {
        "boundary": dedupe_points(np.array(boundary)),
        "lower_root": lower_root,
        "upper_root": upper_root,
        "root_radius": root_radius,
    }


def build_external_gear_profile(gear, tooth_count_points=24, arc_points_count=12):
    teeth = []
    for tooth_index in range(gear.num_teeth):
        center_angle = 2.0 * math.pi * tooth_index / gear.num_teeth
        teeth.append(
            external_involute_tooth(
                center_angle,
                gear,
                flank_points=tooth_count_points,
                arc_points_count=arc_points_count,
            )
        )

    _, _, _, root_radius = external_gear_radii(gear)
    profile = list(teeth[0]["boundary"])
    for tooth_index, tooth in enumerate(teeth):
        next_tooth = teeth[(tooth_index + 1) % gear.num_teeth]
        root_arc = arc_points(
            root_radius,
            math.atan2(tooth["upper_root"][1], tooth["upper_root"][0]),
            math.atan2(next_tooth["lower_root"][1], next_tooth["lower_root"][0]),
            arc_points_count,
        )
        profile.extend(root_arc[1:])
        if tooth_index + 1 < gear.num_teeth:
            profile.extend(next_tooth["boundary"][1:])

    return dedupe_points(np.array(profile))


def build_internal_ring_profile(tooth_count, module_mm, pressure_angle_deg, tooth_count_points=24, arc_points_count=12):
    teeth = []
    for tooth_index in range(tooth_count):
        center_angle = 2.0 * math.pi * tooth_index / tooth_count
        teeth.append(
            internal_involute_tooth(
                center_angle,
                tooth_count,
                module_mm,
                pressure_angle_deg,
                flank_points=tooth_count_points,
                arc_points_count=arc_points_count,
            )
        )

    root_radius = teeth[0]["root_radius"]
    profile = list(teeth[0]["boundary"])
    for tooth_index, tooth in enumerate(teeth):
        next_tooth = teeth[(tooth_index + 1) % tooth_count]
        root_arc = arc_points(
            root_radius,
            math.atan2(tooth["upper_root"][1], tooth["upper_root"][0]),
            math.atan2(next_tooth["lower_root"][1], next_tooth["lower_root"][0]),
            arc_points_count,
        )
        profile.extend(root_arc[1:])
        if tooth_index + 1 < tooth_count:
            profile.extend(next_tooth["boundary"][1:])

    return dedupe_points(np.array(profile))


def offset_profile_radial(points, offset, small_radius_tol=1e-9):
    offset_points = np.zeros_like(points)
    for index, point in enumerate(points):
        radius = np.linalg.norm(point)
        if radius > small_radius_tol:
            offset_points[index] = point + offset * (point / radius)
        else:
            offset_points[index] = point
    return offset_points


def filter_points(vertices, tol):
    filtered = [vertices[0]]
    for point in vertices[1:]:
        if np.linalg.norm(point - filtered[-1]) > tol:
            filtered.append(point)
    return np.array(filtered)


def create_gear_shape(profile_2d, twist_per_z, z_start, z_end, extra_rotation=0.0, translate=(0.0, 0.0)):
    """
    Create a lofted gear body between two z levels.
    """
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
    from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
    from OCP.gp import gp_Pnt

    def get_profile_at_z(z_val):
        twist = abs(z_val) * twist_per_z + extra_rotation if abs(z_val) > 1e-9 else 0.0
        rotated = rotate_2d(profile_2d, twist)
        translated = rotated.copy()
        translated[:, 0] += translate[0]
        translated[:, 1] += translate[1]
        return translated

    def make_wire(points_2d, z_val):
        builder = BRepBuilderAPI_MakePolygon()
        for point in points_2d:
            builder.Add(gp_Pnt(float(point[0]), float(point[1]), float(z_val)))
        builder.Close()
        return builder.Wire()

    if z_start < 0.0 < z_end:
        profile_start = get_profile_at_z(z_start)
        profile_mid = get_profile_at_z(0.0)
        profile_end = get_profile_at_z(z_end)

        wire_start = make_wire(profile_start, z_start)
        wire_mid = make_wire(profile_mid, 0.0)
        wire_end = make_wire(profile_end, z_end)

        loft_bottom = BRepOffsetAPI_ThruSections(True)
        loft_bottom.AddWire(wire_start)
        loft_bottom.AddWire(wire_mid)
        loft_bottom.Build()

        loft_top = BRepOffsetAPI_ThruSections(True)
        loft_top.AddWire(wire_mid)
        loft_top.AddWire(wire_end)
        loft_top.Build()

        fuse = BRepAlgoAPI_Fuse(loft_bottom.Shape(), loft_top.Shape())
        fuse.Build()
        return fuse.Shape()

    profile_start = get_profile_at_z(z_start)
    profile_end = get_profile_at_z(z_end)

    wire_start = make_wire(profile_start, z_start)
    wire_end = make_wire(profile_end, z_end)

    loft = BRepOffsetAPI_ThruSections(True)
    loft.AddWire(wire_start)
    loft.AddWire(wire_end)
    loft.Build()
    return loft.Shape()


def create_ring_half(profile_2d, twist_per_z, z_start, z_end, outer_radius, extra_rotation):
    """
    Create one half of the ring gear by subtracting the internal tooth cavity
    from an outer cylinder.
    """
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    z_base = min(z_start, z_end)
    height = abs(z_end - z_start)

    cylinder = BRepPrimAPI_MakeCylinder(
        gp_Ax2(gp_Pnt(0.0, 0.0, z_base), gp_Dir(0.0, 0.0, 1.0)),
        outer_radius,
        height,
    ).Shape()

    cavity = create_gear_shape(profile_2d, twist_per_z, z_start, z_end, extra_rotation=extra_rotation)
    ring_half = BRepAlgoAPI_Cut(cylinder, cavity)
    ring_half.Build()
    return ring_half.Shape()


def save_mesh_preview(output_dir, ring_profile, sun_profile, planet_profile, carrier_radius, planet_count, planet_zero_angle_deg):
    """
    Save simple top-down outline previews of the involute mesh.
    """

    def closed(points):
        return np.vstack((points, points[0]))

    def draw_profile(ax, points, color, linewidth=0.8):
        curve = closed(points)
        ax.plot(curve[:, 0], curve[:, 1], color=color, linewidth=linewidth)

    def draw_arrangement(ax):
        rotated_ring = rotate_2d(ring_profile, RING_MESH_PHASE_RAD)
        draw_profile(ax, rotated_ring, "#1f1f1f", linewidth=0.9)
        draw_profile(ax, sun_profile, "#006d77", linewidth=0.9)

        for planet_index in range(planet_count):
            carrier_angle = 2.0 * math.pi * planet_index / planet_count + math.radians(planet_zero_angle_deg)
            spin_angle = PLANET_MESH_PHASE_RAD + (1.0 - R_teeth / P_teeth) * carrier_angle
            pos_x = carrier_radius * math.cos(carrier_angle)
            pos_y = carrier_radius * math.sin(carrier_angle)

            rotated = rotate_2d(planet_profile, spin_angle)
            translated = rotated.copy()
            translated[:, 0] += pos_x
            translated[:, 1] += pos_y
            draw_profile(ax, translated, "#ae2012", linewidth=0.9)

    fig, ax = plt.subplots(figsize=(8, 8))
    draw_arrangement(ax)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Involute planetary mesh preview")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.grid(True, linewidth=0.3, alpha=0.35)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "mesh_preview_full.png"), dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 8))
    draw_arrangement(ax)
    zoom_half_span = carrier_radius + planet_outer_r + 6.0
    ax.set_xlim(-zoom_half_span, zoom_half_span)
    ax.set_ylim(-zoom_half_span, zoom_half_span)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Involute mesh preview (zoom)")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.grid(True, linewidth=0.3, alpha=0.35)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "mesh_preview_zoom.png"), dpi=220)
    plt.close(fig)

    top_planet_angle = math.radians(planet_zero_angle_deg)
    top_planet_x = carrier_radius * math.cos(top_planet_angle)
    top_planet_y = carrier_radius * math.sin(top_planet_angle)

    fig, ax = plt.subplots(figsize=(8, 8))
    draw_arrangement(ax)
    ax.set_xlim(top_planet_x - 18.0, top_planet_x + 18.0)
    ax.set_ylim(top_planet_y - 20.0, top_planet_y + 20.0)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Involute mesh preview (contact detail)")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.grid(True, linewidth=0.3, alpha=0.35)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "mesh_preview_contact.png"), dpi=220)
    plt.close(fig)


def arrangement_profiles(ring_profile, sun_profile, planet_profile, carrier_radius, planet_count, planet_zero_angle_deg, phase_rad):
    """
    Return the animated top-down arrangement for one phase step.
    """
    ring_phase = 0.0
    sun_phase = phase_rad
    carrier_phase = phase_rad * S_teeth / (R_teeth + S_teeth)
    planet_phase = -((R_teeth - P_teeth) / P_teeth) * carrier_phase

    arranged = {
        "ring": rotate_2d(ring_profile, RING_MESH_PHASE_RAD + ring_phase),
        "sun": rotate_2d(sun_profile, sun_phase),
        "planets": [],
    }

    for planet_index in range(planet_count):
        base_angle = 2.0 * math.pi * planet_index / planet_count + math.radians(planet_zero_angle_deg)
        carrier_angle = carrier_phase + base_angle
        mesh_spin = (1.0 - R_teeth / P_teeth) * carrier_angle
        total_spin = PLANET_MESH_PHASE_RAD + planet_phase + mesh_spin

        rotated = rotate_2d(planet_profile, total_spin)
        translated = rotated.copy()
        translated[:, 0] += carrier_radius
        translated = rotate_2d(translated, carrier_angle)
        arranged["planets"].append(translated)

    return arranged


def save_mesh_animation(output_dir, ring_profile, sun_profile, planet_profile, carrier_radius, planet_count, planet_zero_angle_deg):
    """
    Save a simple top-down animated GIF for the involute copy.
    """
    frames = []
    total_phase = math.pi / 2.0

    for frame_index in range(ANIMATION_FRAMES):
        phase_rad = total_phase * frame_index / ANIMATION_FRAMES
        arranged = arrangement_profiles(
            ring_profile,
            sun_profile,
            planet_profile,
            carrier_radius,
            planet_count,
            planet_zero_angle_deg,
            phase_rad,
        )

        fig, ax = plt.subplots(figsize=(7, 7))

        def plot_closed(points, color, linewidth=0.8):
            curve = np.vstack((points, points[0]))
            ax.plot(curve[:, 0], curve[:, 1], color=color, linewidth=linewidth)

        plot_closed(arranged["ring"], "#1f1f1f", linewidth=0.9)
        plot_closed(arranged["sun"], "#006d77", linewidth=0.9)
        for planet_points in arranged["planets"]:
            plot_closed(planet_points, "#ae2012", linewidth=0.9)

        ax.set_aspect("equal", adjustable="box")
        ax.set_xlim(-ANIMATION_VIEW_HALFSPAN_MM, ANIMATION_VIEW_HALFSPAN_MM)
        ax.set_ylim(-ANIMATION_VIEW_HALFSPAN_MM, ANIMATION_VIEW_HALFSPAN_MM)
        ax.set_title("Involute planetary mesh animation")
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.grid(True, linewidth=0.3, alpha=0.35)
        fig.tight_layout()
        fig.canvas.draw()

        image = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(
            fig.canvas.get_width_height()[1],
            fig.canvas.get_width_height()[0],
            4,
        )[:, :, :3]
        frames.append(image)
        plt.close(fig)

    pil_frames = [Image.fromarray(frame) for frame in frames]
    pil_frames[0].save(
        os.path.join(output_dir, "mesh_animation.gif"),
        save_all=True,
        append_images=pil_frames[1:],
        duration=int(1000 / ANIMATION_FPS),
        loop=0,
    )


# =============================================================================
# Aaron's QDD involute parameters
# =============================================================================

TARGET_RING_PITCH_DIAMETER_MM = 75.0
GEAR_THICKNESS_MM = 18.6
GEAR_TYPE = "spur"  # spur, helix, herringbone
HELIX_ANGLE_DEGREES = 30.0
PRESSURE_ANGLE_DEG = 25.0
CLOSE_POINT_TOLERANCE = 1e-6
PROFILE_FLANK_POINTS = 12
PROFILE_ARC_POINTS = 6
RING_FLANK_POINTS = 8
RING_ARC_POINTS = 4
ADDENDUM_COEFF = 0.85
DEDENDUM_COEFF = 1.0
ROOT_BLEND_RADIUS_MM = 0.45
ROOT_BLEND_POINTS = 5
ANIMATION_FRAMES = 48
ANIMATION_FPS = 20
ANIMATION_VIEW_HALFSPAN_MM = 44.0
PLANET_0_ANGLE_DEG = 90.0

R_teeth = 48
P_teeth = 18
S_teeth = 12
N_planets = 3

PLANET_MESH_PHASE_RAD = math.pi - math.pi / P_teeth
RING_MESH_PHASE_RAD = -math.pi / R_teeth

PROFILE_OFFSET_MM = -0.04
RING_OFFSET_DEG = 0.2
RING_WALL_MM = 10.0

MODULE_MM = TARGET_RING_PITCH_DIAMETER_MM / R_teeth

validate_planetary_config(R_teeth, P_teeth, S_teeth, N_planets)

if GEAR_TYPE == "spur":
    HELIX_ANGLE_DEGREES = 0.0

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "step_output_aaron_involute", GEAR_TYPE)
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

existing_runs = [
    entry
    for entry in os.listdir(BASE_OUTPUT_DIR)
    if os.path.isdir(os.path.join(BASE_OUTPUT_DIR, entry)) and entry[:3].isdigit()
]
next_num = max([int(entry[:3]) for entry in existing_runs], default=-1) + 1
OUTPUT_DIR = os.path.join(BASE_OUTPUT_DIR, f"{next_num:03d}")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("STEP FILE GENERATOR - Aaron's QDD Gearbox (Involute Copy)")
print(f"Gear type: {GEAR_TYPE} | Run {next_num:03d}")
print("=" * 60)

sun_gear = GearParams(MODULE_MM, S_teeth, PRESSURE_ANGLE_DEG, GEAR_THICKNESS_MM, HELIX_ANGLE_DEGREES)
planet_gear = GearParams(MODULE_MM, P_teeth, PRESSURE_ANGLE_DEG, GEAR_THICKNESS_MM, HELIX_ANGLE_DEGREES)

sun_profile = build_external_gear_profile(
    sun_gear,
    tooth_count_points=PROFILE_FLANK_POINTS,
    arc_points_count=PROFILE_ARC_POINTS,
)
planet_profile = build_external_gear_profile(
    planet_gear,
    tooth_count_points=PROFILE_FLANK_POINTS,
    arc_points_count=PROFILE_ARC_POINTS,
)
ring_profile = build_internal_ring_profile(
    R_teeth,
    MODULE_MM,
    PRESSURE_ANGLE_DEG,
    tooth_count_points=RING_FLANK_POINTS,
    arc_points_count=RING_ARC_POINTS,
)

sun_profile = filter_points(offset_profile_radial(sun_profile, PROFILE_OFFSET_MM), CLOSE_POINT_TOLERANCE)
planet_profile = filter_points(offset_profile_radial(planet_profile, PROFILE_OFFSET_MM), CLOSE_POINT_TOLERANCE)
ring_profile = filter_points(offset_profile_radial(ring_profile, -PROFILE_OFFSET_MM), CLOSE_POINT_TOLERANCE)

carrier_radius = 0.5 * MODULE_MM * (S_teeth + P_teeth)
_, _, sun_outer_r, sun_root_r = external_gear_radii(sun_gear)
_, _, planet_outer_r, planet_root_r = external_gear_radii(planet_gear)
ring_pitch_r, _, ring_tip_r, ring_root_r = internal_gear_radii(R_teeth, MODULE_MM, PRESSURE_ANGLE_DEG)
ring_outer_r = ring_root_r + RING_WALL_MM

cr_sp = compute_contact_ratio(MODULE_MM, S_teeth, P_teeth, PRESSURE_ANGLE_DEG)
cr_pr = compute_contact_ratio(MODULE_MM, P_teeth, R_teeth, PRESSURE_ANGLE_DEG)

print(f"Module: {MODULE_MM:.4f} mm")
print(f"Pressure angle: {PRESSURE_ANGLE_DEG:.1f} deg")
print(f"Addendum coefficient: {ADDENDUM_COEFF:.2f}")
print(f"Dedendum coefficient: {DEDENDUM_COEFF:.2f}")
print(f"Ring pitch diameter target: {TARGET_RING_PITCH_DIAMETER_MM:.3f} mm")
print(f"Ratio: {(R_teeth + S_teeth) / S_teeth:.2f}:1")
print()
print("--- Geometry ---")
print(f"Sun outer diameter:    {2.0 * sun_outer_r:.3f} mm")
print(f"Sun root diameter:     {2.0 * sun_root_r:.3f} mm")
print(f"Planet outer diameter: {2.0 * planet_outer_r:.3f} mm")
print(f"Planet root diameter:  {2.0 * planet_root_r:.3f} mm")
print(f"Ring tip diameter:     {2.0 * ring_tip_r:.3f} mm")
print(f"Ring root diameter:    {2.0 * ring_root_r:.3f} mm")
print(f"Ring outer diameter:   {2.0 * ring_outer_r:.3f} mm")
print(f"Carrier radius:        {carrier_radius:.3f} mm")
print()
print("--- Contact Ratio ---")
print(f"Sun-planet:   {cr_sp:.3f}")
print(f"Planet-ring:  {cr_pr:.3f}  (external approximation)")
print(f"Planet base phase: {math.degrees(PLANET_MESH_PHASE_RAD):.3f} deg")
print(f"Ring base phase:   {math.degrees(RING_MESH_PHASE_RAD):.3f} deg")

save_mesh_preview(
    OUTPUT_DIR,
    ring_profile,
    sun_profile,
    planet_profile,
    carrier_radius,
    N_planets,
    PLANET_0_ANGLE_DEG,
)
save_mesh_animation(
    OUTPUT_DIR,
    ring_profile,
    sun_profile,
    planet_profile,
    carrier_radius,
    N_planets,
    PLANET_0_ANGLE_DEG,
)
print()
print("Saved mesh_preview_full.png, mesh_preview_zoom.png, mesh_preview_contact.png, and mesh_animation.gif")

tan_helix = math.tan(math.radians(HELIX_ANGLE_DEGREES))
z_half = GEAR_THICKNESS_MM / 2.0
sun_twist_per_z = tan_helix / max(sun_outer_r, 1e-9)
planet_twist_per_z = -tan_helix / max(planet_outer_r, 1e-9)
ring_twist_per_z = -tan_helix / max(ring_tip_r, 1e-9)
ring_comp_rad = math.radians(RING_OFFSET_DEG) + RING_MESH_PHASE_RAD

# --- Generate Sun Gear ---
print()
print("Generating Sun gear...")
sun_shape = create_gear_shape(sun_profile, sun_twist_per_z, -z_half, z_half)
sun_cq = cq.Workplane("XY").add(cq.Shape(sun_shape))
exporters.export(sun_cq, os.path.join(OUTPUT_DIR, "sun_PRINT.step"))
exporters.export(sun_cq, os.path.join(OUTPUT_DIR, "sun_PRINT.stl"))
print("  Exported sun_PRINT.step/.stl")

# --- Generate Planet Gears ---
print()
print("Generating Planet gears...")
planet_shapes = []
for planet_index in range(N_planets):
    carrier_angle = 2.0 * math.pi * planet_index / N_planets + math.radians(PLANET_0_ANGLE_DEG)
    spin_angle = PLANET_MESH_PHASE_RAD + (1.0 - R_teeth / P_teeth) * carrier_angle

    planet_rotated = rotate_2d(planet_profile, spin_angle)
    pos_x = carrier_radius * math.cos(carrier_angle)
    pos_y = carrier_radius * math.sin(carrier_angle)

    planet_shape = create_gear_shape(
        planet_rotated,
        planet_twist_per_z,
        -z_half,
        z_half,
        translate=(pos_x, pos_y),
    )
    planet_shapes.append(planet_shape)

    planet_cq = cq.Workplane("XY").add(cq.Shape(planet_shape))
    exporters.export(planet_cq, os.path.join(OUTPUT_DIR, f"planet_{planet_index}_PRINT.step"))
    exporters.export(planet_cq, os.path.join(OUTPUT_DIR, f"planet_{planet_index}_PRINT.stl"))
    print(f"  Exported planet_{planet_index}_PRINT.step/.stl")

# --- Generate Ring Gear ---
ring_shapes_for_assembly = []
print()
if GEAR_TYPE == "herringbone":
    print("Generating Split Ring gear...")

    ring_bottom = create_ring_half(ring_profile, ring_twist_per_z, -z_half, 0.0, ring_outer_r, ring_comp_rad)
    ring_bottom_cq = cq.Workplane("XY").add(cq.Shape(ring_bottom))
    exporters.export(ring_bottom_cq, os.path.join(OUTPUT_DIR, "ring_bottom_PRINT.step"))
    exporters.export(ring_bottom_cq, os.path.join(OUTPUT_DIR, "ring_bottom_PRINT.stl"))
    print("  Exported ring_bottom_PRINT.step/.stl")

    ring_top = create_ring_half(ring_profile, ring_twist_per_z, 0.0, z_half, ring_outer_r, ring_comp_rad)
    ring_top_cq = cq.Workplane("XY").add(cq.Shape(ring_top))
    exporters.export(ring_top_cq, os.path.join(OUTPUT_DIR, "ring_top_PRINT.step"))
    exporters.export(ring_top_cq, os.path.join(OUTPUT_DIR, "ring_top_PRINT.stl"))
    print("  Exported ring_top_PRINT.step/.stl")

    ring_shapes_for_assembly = [ring_bottom, ring_top]
else:
    print("Generating Ring gear...")
    ring_shape = create_ring_half(ring_profile, ring_twist_per_z, -z_half, z_half, ring_outer_r, ring_comp_rad)
    ring_cq = cq.Workplane("XY").add(cq.Shape(ring_shape))
    exporters.export(ring_cq, os.path.join(OUTPUT_DIR, "ring_PRINT.step"))
    exporters.export(ring_cq, os.path.join(OUTPUT_DIR, "ring_PRINT.stl"))
    print("  Exported ring_PRINT.step/.stl")
    ring_shapes_for_assembly = [ring_shape]

# --- Create Assembly ---
print()
print("Creating multi-body CAD part...")
try:
    from OCP.BRep import BRep_Builder
    from OCP.Interface import Interface_Static
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.TopoDS import TopoDS_Compound

    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)

    builder.Add(compound, sun_shape)
    for planet_shape in planet_shapes:
        builder.Add(compound, planet_shape)
    for ring_shape in ring_shapes_for_assembly:
        builder.Add(compound, ring_shape)

    writer = STEPControl_Writer()
    Interface_Static.SetIVal_s("write.step.assembly", 0)
    writer.Transfer(compound, STEPControl_AsIs)
    status = writer.Write(os.path.join(OUTPUT_DIR, "gearbox_CAD.step"))
    if status == 1:
        print("  Exported gearbox_CAD.step (multi-body part, no assembly structure)")
    else:
        print(f"  STEP write returned status {status}")
except Exception as exc:
    print(f"  CAD export failed: {exc}")
    raise

print()
print("=" * 60)
print(f"INVOLUTE GENERATION COMPLETE -- {GEAR_TYPE} Run {next_num:03d}")
print(f"Output directory: {OUTPUT_DIR}")
print("=" * 60)
