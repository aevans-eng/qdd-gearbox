"""
generate_step_aaron_cq_gears.py - QDD involute planetary generator using cq_gears

This is a separate path from the original cycloidal generator and the custom
involute sandbox copy. It uses cq_gears' native PlanetaryGearset assembly
logic so the sun / planets / ring start from a coherent involute mesh.
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


WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CQ_GEARS_CLONE = os.path.join(WORKSPACE_ROOT, "_dump", "cq_gears")
if CQ_GEARS_CLONE not in sys.path:
    sys.path.insert(0, CQ_GEARS_CLONE)

from cq_gears import HerringbonePlanetaryGearset, PlanetaryGearset
from cq_gears.spur_gear import HerringboneGear, SpurGear
from cq_gears.ring_gear import HerringboneRingGear, RingGear


# Cycloidal reference dimensions from the confirmed Rev01 STEP notes.
# These are the dimensions most likely to matter for fit in the existing carrier.
REFERENCE_CARRIER_RADIUS_MM = 22.959
REFERENCE_SUN_OD_MM = 19.898
REFERENCE_PLANET_OD_MM = 29.082
REFERENCE_RING_INNER_TIP_D_MM = 71.938
REFERENCE_RING_ROOT_D_MM = 75.000
REFERENCE_RING_OD_MM = 95.000

GEAR_THICKNESS_MM = 18.6
GEAR_TYPE = "spur"  # spur, helix, herringbone
HELIX_ANGLE_DEG = 28.0
PRESSURE_ANGLE_DEG = 20.0
# Map the proven cycloidal print setting of 0.13 mm total mesh clearance into
# involute terms instead of copying a raw offset directly.
TARGET_TOTAL_MESH_CLEARANCE_MM = 0.13
RADIAL_ROOT_CLEARANCE_MM = TARGET_TOTAL_MESH_CLEARANCE_MM / 2.0
CLEARANCE_MM = RADIAL_ROOT_CLEARANCE_MM

R_teeth = 72
P_teeth = 27
S_teeth = 18
N_planets = 3

PLANET_0_ANGLE_DEG = 90.0
ANIMATION_FRAMES = 48
ANIMATION_FPS = 20
ANIMATION_VIEW_HALFSPAN_MM = 44.0
SLOWMO_FRAMES = 84
SLOWMO_FPS = 10
SLOWMO_SUN_ROTATION_DEG = 30.0
CONTACT_VIEW_X_HALFSPAN_MM = 10.0
CONTACT_VIEW_Y_HALFSPAN_MM = 8.0
GENERATE_DIAGNOSTICS = False
EXPORT_COMPONENT_STEPS = False
EXPORT_COMPONENT_STLS = False
EXPORT_COMPOUND_STEP = False
TOOTH_CURVE_POINTS = 80
TOOTH_SURFACE_SPLINES = 10
GEOMETRY_TOL_MM = 1e-3
# Static assembly phasing verified by direct solid-intersection checks for the
# current printable baseline family (R72 / P27 / S18).
STATIC_SUN_PHASE_DEG = 8.333333333333334
STATIC_PLANET_PHASE_DEG = 11.111111111111112
STATIC_RING_PHASE_DEG = 0.4166666666666667


def rotation_matrix(angle_rad):
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    return np.array([[c, -s], [s, c]])


def rotate_xy(points_xyz, angle_rad):
    rotated = points_xyz.copy()
    rotated[:, :2] = rotated[:, :2] @ rotation_matrix(angle_rad).T
    return rotated


def translate_xy(points_xyz, dx, dy):
    translated = points_xyz.copy()
    translated[:, 0] += dx
    translated[:, 1] += dy
    return translated


def closed_xy(points_xyz):
    curve = np.vstack((points_xyz[:, :2], points_xyz[0, :2]))
    return curve


def unit(vector):
    norm = np.linalg.norm(vector)
    if norm < 1e-12:
        return np.zeros_like(vector)
    return vector / norm


def densify_closed_curve(points_xyz, subdivisions=6):
    xy = points_xyz[:, :2]
    dense = []
    for index in range(len(xy)):
        start = xy[index]
        end = xy[(index + 1) % len(xy)]
        segment = np.linspace(start, end, subdivisions, endpoint=False)
        dense.append(segment)
    return np.vstack(dense)


def nearest_vertex_pair(points_a_xy, points_b_xy):
    diff = points_a_xy[:, None, :] - points_b_xy[None, :, :]
    dist2 = np.sum(diff * diff, axis=2)
    index = np.unravel_index(np.argmin(dist2), dist2.shape)
    point_a = points_a_xy[index[0]]
    point_b = points_b_xy[index[1]]
    midpoint = 0.5 * (point_a + point_b)
    gap = math.sqrt(dist2[index])
    return point_a, point_b, midpoint, gap


def configure_geometry_quality():
    for cls in (SpurGear, HerringboneGear, RingGear, HerringboneRingGear):
        cls.curve_points = TOOTH_CURVE_POINTS
        cls.surface_splines = TOOTH_SURFACE_SPLINES
        cls.wire_comb_tol = GEOMETRY_TOL_MM
        cls.spline_approx_tol = GEOMETRY_TOL_MM
        cls.shell_sewing_tol = GEOMETRY_TOL_MM


def static_phase_offsets_deg(gearset):
    if (
        gearset.sun.z == 18
        and gearset.planet.z == 27
        and gearset.ring.z == 72
        and abs(math.degrees(gearset.sun.a0) - 20.0) < 1e-6
    ):
        return STATIC_SUN_PHASE_DEG, STATIC_PLANET_PHASE_DEG, STATIC_RING_PHASE_DEG

    sun_deg = math.degrees(gearset.sun.tau / 2.0) if (gearset.planet.z % 2) != 0 else 0.0
    planet_deg = math.degrees(gearset.planet.tau / 2.0)
    ring_deg = math.degrees(gearset.ring.tau / 2.0)
    return sun_deg, planet_deg, ring_deg


def make_gearset():
    configure_geometry_quality()
    module_mm = 2.0 * REFERENCE_CARRIER_RADIUS_MM / (S_teeth + P_teeth)
    pressure_angle_rad = math.radians(PRESSURE_ANGLE_DEG)
    backlash = TARGET_TOTAL_MESH_CLEARANCE_MM / (
        2.0 * module_mm * math.tan(pressure_angle_rad)
    )
    addendum_coeff = (
        ((REFERENCE_SUN_OD_MM / module_mm) - S_teeth) / 2.0
        + (R_teeth - (REFERENCE_RING_INNER_TIP_D_MM / module_mm)) / 2.0
    ) / 2.0
    dedendum_coeff = (
        REFERENCE_RING_ROOT_D_MM - R_teeth * module_mm - 2.0 * CLEARANCE_MM
    ) / (2.0 * module_mm)
    rim_width_mm = REFERENCE_RING_OD_MM / 2.0 - REFERENCE_RING_ROOT_D_MM / 2.0
    helix_angle = 0.0 if GEAR_TYPE == "spur" else HELIX_ANGLE_DEG
    gearset_cls = HerringbonePlanetaryGearset if GEAR_TYPE == "herringbone" else PlanetaryGearset

    gearset = gearset_cls(
        module=module_mm,
        sun_teeth_number=S_teeth,
        planet_teeth_number=P_teeth,
        width=GEAR_THICKNESS_MM,
        rim_width=rim_width_mm,
        n_planets=N_planets,
        pressure_angle=PRESSURE_ANGLE_DEG,
        helix_angle=helix_angle,
        clearance=CLEARANCE_MM,
        backlash=backlash,
        addendum_coeff=addendum_coeff,
        dedendum_coeff=dedendum_coeff,
    )
    return gearset


def assembly_profiles(gearset, sun_angle_deg=0.0):
    """
    Return animated 2D profile positions.
    """
    sun_angle = math.radians(sun_angle_deg)
    planet_ratio = gearset.sun.z / (gearset.planet.z * 2.0)
    carrier_ratio = 1.0 / (gearset.ring.z / gearset.sun.z + 1.0)
    carrier_angle = sun_angle * carrier_ratio
    planet_spin = -sun_angle * planet_ratio
    sun_base_deg, planet_base_deg, ring_base_deg = static_phase_offsets_deg(gearset)
    sun_base = math.radians(sun_base_deg)
    planet_base = math.radians(planet_base_deg)
    ring_base = math.radians(ring_base_deg)

    arranged = {
        "sun_center": np.array([0.0, 0.0]),
        "ring_center": np.array([0.0, 0.0]),
        "sun": rotate_xy(gearset.sun.gear_points(), sun_base + sun_angle),
        "ring": rotate_xy(gearset.ring.gear_points(), ring_base),
        "planets": [],
        "planet_centers": [],
    }

    planet_step = 2.0 * math.pi / gearset.n_planets
    for planet_index in range(gearset.n_planets):
        orbit_angle = math.radians(PLANET_0_ANGLE_DEG) + planet_index * planet_step + carrier_angle
        local = rotate_xy(gearset.planet.gear_points(), planet_base + planet_spin - carrier_angle)
        local = translate_xy(local, gearset.orbit_r, 0.0)
        world = rotate_xy(local, orbit_angle)
        arranged["planets"].append(world)
        arranged["planet_centers"].append(
            np.array([
                math.cos(orbit_angle) * gearset.orbit_r,
                math.sin(orbit_angle) * gearset.orbit_r,
            ])
        )

    return arranged


def static_assembly_profiles(gearset):
    """
    Return 2D profiles using the same static body transforms as the exported
    STEP assembly. This is the path to use for static mesh verification.
    """
    sun_deg, planet_deg, ring_deg = static_phase_offsets_deg(gearset)
    arranged = {
        "sun_center": np.array([0.0, 0.0]),
        "ring_center": np.array([0.0, 0.0]),
        "sun": rotate_xy(gearset.sun.gear_points(), math.radians(sun_deg)),
        "ring": rotate_xy(gearset.ring.gear_points(), math.radians(ring_deg)),
        "planets": [],
        "planet_centers": [],
    }

    planet_body = rotate_xy(gearset.planet.gear_points(), math.radians(planet_deg))
    planet_step_deg = 360.0 / gearset.n_planets
    for planet_index in range(gearset.n_planets):
        orbit_angle_deg = PLANET_0_ANGLE_DEG + planet_index * planet_step_deg
        x = math.cos(math.radians(orbit_angle_deg)) * gearset.orbit_r
        y = math.sin(math.radians(orbit_angle_deg)) * gearset.orbit_r
        arranged["planets"].append(translate_xy(planet_body, x, y))
        arranged["planet_centers"].append(np.array([x, y]))

    return arranged


def sun_planet_geometry_overlay(gearset, arrangement, planet_index=0):
    sun_center = arrangement["sun_center"]
    planet_center = arrangement["planet_centers"][planet_index]

    centerline_dir = unit(planet_center - sun_center)
    tangent_dir = np.array([-centerline_dir[1], centerline_dir[0]])
    alpha = math.radians(PRESSURE_ANGLE_DEG)
    line_of_action_dir = unit(tangent_dir * math.cos(alpha) + centerline_dir * math.sin(alpha))

    pitch_point = sun_center + centerline_dir * gearset.sun.r0
    sun_tangent = pitch_point - line_of_action_dir * (gearset.sun.r0 * math.sin(alpha))
    planet_tangent = pitch_point + line_of_action_dir * (gearset.planet.r0 * math.sin(alpha))

    sun_dense = densify_closed_curve(arrangement["sun"])
    planet_dense = densify_closed_curve(arrangement["planets"][planet_index])
    sun_contact, planet_contact, contact_mid, contact_gap = nearest_vertex_pair(sun_dense, planet_dense)

    return {
        "sun_center": sun_center,
        "planet_center": planet_center,
        "pitch_point": pitch_point,
        "sun_tangent": sun_tangent,
        "planet_tangent": planet_tangent,
        "centerline_dir": centerline_dir,
        "line_of_action_dir": line_of_action_dir,
        "sun_contact": sun_contact,
        "planet_contact": planet_contact,
        "contact_mid": contact_mid,
        "contact_gap": contact_gap,
    }


def draw_contact_overlay(ax, gearset, arrangement, overlay):
    ax.add_patch(plt.Circle(overlay["sun_center"], gearset.sun.r0, fill=False, linestyle="--", linewidth=0.8, color="#2a9d8f", alpha=0.7))
    ax.add_patch(plt.Circle(overlay["planet_center"], gearset.planet.r0, fill=False, linestyle="--", linewidth=0.8, color="#e76f51", alpha=0.7))
    ax.add_patch(plt.Circle(overlay["sun_center"], gearset.sun.rb, fill=False, linestyle=":", linewidth=0.8, color="#1d3557", alpha=0.8))
    ax.add_patch(plt.Circle(overlay["planet_center"], gearset.planet.rb, fill=False, linestyle=":", linewidth=0.8, color="#9b2226", alpha=0.8))

    centerline = np.vstack((overlay["sun_center"], overlay["planet_center"]))
    ax.plot(centerline[:, 0], centerline[:, 1], color="#6c757d", linewidth=0.8, alpha=0.8)

    line_span = 18.0
    loa = np.vstack((
        overlay["pitch_point"] - overlay["line_of_action_dir"] * line_span,
        overlay["pitch_point"] + overlay["line_of_action_dir"] * line_span,
    ))
    ax.plot(loa[:, 0], loa[:, 1], color="#6d597a", linewidth=1.0, alpha=0.9)

    tangency = np.vstack((overlay["sun_tangent"], overlay["planet_tangent"]))
    ax.plot(tangency[:, 0], tangency[:, 1], color="#8338ec", linewidth=1.2, alpha=0.9)

    ax.scatter(*overlay["pitch_point"], color="#000000", s=18, zorder=5)
    ax.scatter(*overlay["contact_mid"], color="#ff006e", s=20, zorder=6)
    ax.plot([overlay["sun_contact"][0], overlay["planet_contact"][0]], [overlay["sun_contact"][1], overlay["planet_contact"][1]], color="#ff006e", linewidth=0.9, alpha=0.9)


def save_contact_diagnostics(output_dir, gearset):
    arrangement = static_assembly_profiles(gearset)
    overlay = sun_planet_geometry_overlay(gearset, arrangement, planet_index=0)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(*closed_xy(arrangement["sun"]).T, color="#006d77", linewidth=1.0)
    ax.plot(*closed_xy(arrangement["planets"][0]).T, color="#ae2012", linewidth=1.0)
    draw_contact_overlay(ax, gearset, arrangement, overlay)

    center_x = 0.5 * (overlay["sun_center"][0] + overlay["planet_center"][0])
    center_y = 0.5 * (overlay["sun_center"][1] + overlay["planet_center"][1])
    ax.set_xlim(center_x - CONTACT_VIEW_X_HALFSPAN_MM, center_x + CONTACT_VIEW_X_HALFSPAN_MM)
    ax.set_ylim(center_y - CONTACT_VIEW_Y_HALFSPAN_MM, center_y + CONTACT_VIEW_Y_HALFSPAN_MM)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Sun-planet involute contact geometry")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.grid(True, linewidth=0.3, alpha=0.35)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "sun_planet_contact_geometry.png"), dpi=240)
    plt.close(fig)


def save_contact_slowmo_gif(output_dir, gearset):
    frames = []

    for frame_index in range(SLOWMO_FRAMES):
        sun_angle_deg = SLOWMO_SUN_ROTATION_DEG * frame_index / max(SLOWMO_FRAMES - 1, 1)
        arrangement = assembly_profiles(gearset, sun_angle_deg)
        overlay = sun_planet_geometry_overlay(gearset, arrangement, planet_index=0)

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.plot(*closed_xy(arrangement["sun"]).T, color="#006d77", linewidth=1.0)
        ax.plot(*closed_xy(arrangement["planets"][0]).T, color="#ae2012", linewidth=1.0)
        draw_contact_overlay(ax, gearset, arrangement, overlay)

        center_x = 0.5 * (overlay["sun_center"][0] + overlay["planet_center"][0])
        center_y = 0.5 * (overlay["sun_center"][1] + overlay["planet_center"][1])
        ax.set_xlim(center_x - CONTACT_VIEW_X_HALFSPAN_MM, center_x + CONTACT_VIEW_X_HALFSPAN_MM)
        ax.set_ylim(center_y - CONTACT_VIEW_Y_HALFSPAN_MM, center_y + CONTACT_VIEW_Y_HALFSPAN_MM)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title("Sun-planet contact slow motion")
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.text(
            0.02,
            0.02,
            f"sun={sun_angle_deg:0.1f} deg  gap~{overlay['contact_gap']:.3f} mm",
            transform=ax.transAxes,
            fontsize=9,
            bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "#bbbbbb"},
        )
        ax.grid(True, linewidth=0.3, alpha=0.35)
        fig.tight_layout()
        fig.canvas.draw()

        image = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(
            fig.canvas.get_width_height()[1],
            fig.canvas.get_width_height()[0],
            4,
        )[:, :, :3]
        frames.append(Image.fromarray(image))
        plt.close(fig)

    frames[0].save(
        os.path.join(output_dir, "sun_planet_contact_slowmo.gif"),
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / SLOWMO_FPS),
        loop=0,
    )


def save_preview_images(output_dir, gearset):
    def draw(ax, arrangement):
        ax.plot(*closed_xy(arrangement["ring"]).T, color="#1f1f1f", linewidth=0.8)
        ax.plot(*closed_xy(arrangement["sun"]).T, color="#006d77", linewidth=0.9)
        for planet in arrangement["planets"]:
            ax.plot(*closed_xy(planet).T, color="#ae2012", linewidth=0.85)

    arrangement = static_assembly_profiles(gearset)

    fig, ax = plt.subplots(figsize=(8, 8))
    draw(ax, arrangement)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("cq_gears involute planetary mesh preview")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.grid(True, linewidth=0.3, alpha=0.35)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "mesh_preview_full.png"), dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 8))
    draw(ax, arrangement)
    ax.set_xlim(-ANIMATION_VIEW_HALFSPAN_MM, ANIMATION_VIEW_HALFSPAN_MM)
    ax.set_ylim(-ANIMATION_VIEW_HALFSPAN_MM, ANIMATION_VIEW_HALFSPAN_MM)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("cq_gears involute planetary mesh preview (zoom)")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.grid(True, linewidth=0.3, alpha=0.35)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "mesh_preview_zoom.png"), dpi=220)
    plt.close(fig)

    contact = static_assembly_profiles(gearset)
    top_planet = contact["planets"][0]
    center_x = np.mean(top_planet[:, 0])
    center_y = np.mean(top_planet[:, 1])

    fig, ax = plt.subplots(figsize=(8, 8))
    draw(ax, contact)
    ax.set_xlim(center_x - 18.0, center_x + 18.0)
    ax.set_ylim(center_y - 20.0, center_y + 20.0)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("cq_gears involute mesh preview (contact detail)")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.grid(True, linewidth=0.3, alpha=0.35)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "mesh_preview_contact.png"), dpi=220)
    plt.close(fig)


def save_animation_gif(output_dir, gearset):
    frames = []
    max_sun_rotation_deg = 360.0 * 2.0

    for frame_index in range(ANIMATION_FRAMES):
        sun_angle_deg = max_sun_rotation_deg * frame_index / ANIMATION_FRAMES
        arrangement = assembly_profiles(gearset, sun_angle_deg)

        fig, ax = plt.subplots(figsize=(7, 7))
        ax.plot(*closed_xy(arrangement["ring"]).T, color="#1f1f1f", linewidth=0.8)
        ax.plot(*closed_xy(arrangement["sun"]).T, color="#006d77", linewidth=0.9)
        for planet in arrangement["planets"]:
            ax.plot(*closed_xy(planet).T, color="#ae2012", linewidth=0.85)

        ax.set_aspect("equal", adjustable="box")
        ax.set_xlim(-ANIMATION_VIEW_HALFSPAN_MM, ANIMATION_VIEW_HALFSPAN_MM)
        ax.set_ylim(-ANIMATION_VIEW_HALFSPAN_MM, ANIMATION_VIEW_HALFSPAN_MM)
        ax.set_title("cq_gears involute planetary mesh animation")
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
        frames.append(Image.fromarray(image))
        plt.close(fig)

    frames[0].save(
        os.path.join(output_dir, "mesh_animation.gif"),
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / ANIMATION_FPS),
        loop=0,
    )


def export_bodies(output_dir, gearset):
    sun = gearset.sun.build()
    planet = gearset.planet.build()
    ring = gearset.ring.build()

    if EXPORT_COMPONENT_STEPS:
        exporters.export(cq.Workplane("XY").add(sun), os.path.join(output_dir, "sun_PRINT.step"))

    for planet_index in range(gearset.n_planets):
        if EXPORT_COMPONENT_STEPS:
            exporters.export(cq.Workplane("XY").add(planet), os.path.join(output_dir, f"planet_{planet_index}_PRINT.step"))

    if EXPORT_COMPONENT_STEPS:
        exporters.export(cq.Workplane("XY").add(ring), os.path.join(output_dir, "ring_PRINT.step"))

    if EXPORT_COMPONENT_STLS:
        exporters.export(cq.Workplane("XY").add(sun), os.path.join(output_dir, "sun_PRINT.stl"))
        for planet_index in range(gearset.n_planets):
            exporters.export(cq.Workplane("XY").add(planet), os.path.join(output_dir, f"planet_{planet_index}_PRINT.stl"))
        exporters.export(cq.Workplane("XY").add(ring), os.path.join(output_dir, "ring_PRINT.stl"))


def export_assembly(output_dir, gearset):
    sun_phase_deg, planet_phase_deg, ring_phase_deg = static_phase_offsets_deg(gearset)
    assembly = cq.Assembly(name="planetary")

    sun = gearset.sun.build()
    assembly.add(
        sun,
        name="sun",
        loc=cq.Location(cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 0.0, 1.0), sun_phase_deg),
        color=cq.Color("gold"),
    )

    planets = cq.Assembly(name="planets")
    planet_body = gearset.planet.build()
    planet_step_deg = 360.0 / gearset.n_planets
    for planet_index in range(gearset.n_planets):
        orbit_angle_deg = PLANET_0_ANGLE_DEG + planet_index * planet_step_deg
        x = math.cos(math.radians(orbit_angle_deg)) * gearset.orbit_r
        y = math.sin(math.radians(orbit_angle_deg)) * gearset.orbit_r
        planets.add(
            planet_body,
            name=f"planet_{planet_index:02d}",
            loc=cq.Location(cq.Vector(x, y, 0.0), cq.Vector(0.0, 0.0, 1.0), planet_phase_deg),
            color=cq.Color("lightsteelblue"),
        )
    assembly.add(planets)

    ring = gearset.ring.build()
    assembly.add(
        ring,
        name="ring",
        loc=cq.Location(cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 0.0, 1.0), ring_phase_deg),
        color=cq.Color("goldenrod"),
    )

    assembly.save(os.path.join(output_dir, "gearbox_CAD.step"))
    if EXPORT_COMPOUND_STEP:
        exporters.export(cq.Workplane("XY").add(assembly.toCompound()), os.path.join(output_dir, "gearbox_CAD_compound.step"))


def next_output_dir():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_output_dir = os.path.join(script_dir, "step_output_aaron_cq_gears", GEAR_TYPE)
    os.makedirs(base_output_dir, exist_ok=True)
    existing_runs = [
        entry
        for entry in os.listdir(base_output_dir)
        if os.path.isdir(os.path.join(base_output_dir, entry)) and entry[:3].isdigit()
    ]
    next_num = max([int(entry[:3]) for entry in existing_runs], default=-1) + 1
    outdir = os.path.join(base_output_dir, f"{next_num:03d}")
    os.makedirs(outdir, exist_ok=True)
    return next_num, outdir


def main():
    gearset = make_gearset()
    next_num, output_dir = next_output_dir()

    print("=" * 60)
    print("STEP FILE GENERATOR - Aaron's QDD Gearbox (cq_gears)")
    print(f"Gear type: {GEAR_TYPE} | Run {next_num:03d}")
    print("=" * 60)
    print(f"Module: {gearset.sun.m:.4f} mm")
    print(f"Pressure angle: {PRESSURE_ANGLE_DEG:.1f} deg")
    print(f"Addendum coefficient: {gearset.sun.ka:.4f}")
    print(f"Dedendum coefficient: {gearset.sun.kd:.4f}")
    print(f"Backlash factor: {gearset.sun.backlash:.4f}")
    print(f"Radial root clearance: {CLEARANCE_MM:.3f} mm")
    print(f"Mapped total mesh clearance target: {TARGET_TOTAL_MESH_CLEARANCE_MM:.3f} mm")
    print(f"Sun teeth: {gearset.sun.z}")
    print(f"Planet teeth: {gearset.planet.z}")
    print(f"Ring teeth: {gearset.ring.z}")
    print(f"Orbit radius: {gearset.orbit_r:.3f} mm")
    print(f"Sun OD: {gearset.sun.ra * 2.0:.3f} mm  (ref {REFERENCE_SUN_OD_MM:.3f})")
    print(f"Planet OD: {gearset.planet.ra * 2.0:.3f} mm  (ref {REFERENCE_PLANET_OD_MM:.3f})")
    print(f"Ring inner tip D: {gearset.ring.ra * 2.0:.3f} mm  (ref {REFERENCE_RING_INNER_TIP_D_MM:.3f})")
    print(f"Ring root D: {gearset.ring.rd * 2.0:.3f} mm  (ref {REFERENCE_RING_ROOT_D_MM:.3f})")
    print(f"Ring OD: {gearset.ring.rim_r * 2.0:.3f} mm  (ref {REFERENCE_RING_OD_MM:.3f})")
    print()

    if GENERATE_DIAGNOSTICS:
        save_preview_images(output_dir, gearset)
        save_animation_gif(output_dir, gearset)
        save_contact_diagnostics(output_dir, gearset)
        save_contact_slowmo_gif(output_dir, gearset)
        print("Saved mesh previews, mesh_animation.gif, sun_planet_contact_geometry.png, and sun_planet_contact_slowmo.gif")
    else:
        print("Skipping PNG/GIF diagnostics for fast export-only run")

    if EXPORT_COMPONENT_STEPS or EXPORT_COMPONENT_STLS:
        export_bodies(output_dir, gearset)
        print("Exported individual gears")
    else:
        print("Skipping individual gear exports")

    export_assembly(output_dir, gearset)
    print("Exported assembly STEP")

    print()
    print("=" * 60)
    print(f"cq_gears GENERATION COMPLETE -- {GEAR_TYPE} Run {next_num:03d}")
    print(f"Output directory: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
