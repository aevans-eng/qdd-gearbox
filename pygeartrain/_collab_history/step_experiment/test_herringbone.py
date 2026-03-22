"""
Test herringbone with exaggerated angle to verify V-pattern
"""

import numpy as np
from pathlib import Path
import cadquery as cq
import math

OUTPUT_DIR = Path(__file__).parent / "output"


def create_simple_gear_profile(n_teeth: int, outer_radius: float, tooth_depth: float) -> list:
    """Create a simple gear profile for testing."""
    points = []
    n_points_per_tooth = 20

    for i in range(n_teeth):
        tooth_angle = 2 * math.pi * i / n_teeth
        for j in range(n_points_per_tooth):
            t = j / n_points_per_tooth
            angle = tooth_angle + (2 * math.pi / n_teeth) * t

            # Simple sine wave for tooth profile
            r = outer_radius - tooth_depth * 0.5 * (1 + math.cos(n_teeth * angle))
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            points.append((x, y))

    return points


def rotate_profile(points: list, angle_rad: float) -> list:
    """Rotate 2D points around origin."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return [(x * cos_a - y * sin_a, x * sin_a + y * cos_a) for x, y in points]


def generate_test_herringbone():
    """Generate a test herringbone gear with very visible V-pattern."""
    print("Creating test herringbone gear...")

    # Simple 8-tooth gear for clarity
    n_teeth = 8
    outer_radius = 20.0
    tooth_depth = 4.0
    thickness = 15.0  # Taller to show V
    helix_angle_deg = 45.0  # Very aggressive angle

    # Create base profile
    profile = create_simple_gear_profile(n_teeth, outer_radius, tooth_depth)
    profile.append(profile[0])  # Close

    print(f"  {n_teeth} teeth, {outer_radius}mm radius, {helix_angle_deg}° helix")

    # Calculate twist
    tan_helix = math.tan(math.radians(helix_angle_deg))
    z_half = thickness / 2

    # For herringbone: opposite twists at top and bottom
    twist_angle = (z_half * tan_helix) / outer_radius
    print(f"  Twist angle at ends: {math.degrees(twist_angle):.1f}°")

    # Profiles at each level
    profile_bot = rotate_profile(profile, -twist_angle)  # Bottom: twisted one way
    profile_mid = profile  # Center: no twist
    profile_top = rotate_profile(profile, +twist_angle)  # Top: twisted other way

    z_bot = -z_half
    z_mid = 0.0
    z_top = z_half

    print("  Building bottom half (z=-7.5 to z=0)...")
    bottom_half = (
        cq.Workplane("XY", origin=(0, 0, z_bot))
        .spline(profile_bot).close()
        .workplane(offset=z_half)
        .spline(profile_mid).close()
        .loft(ruled=True)
    )

    print("  Building top half (z=0 to z=+7.5)...")
    top_half = (
        cq.Workplane("XY", origin=(0, 0, z_mid))
        .spline(profile_mid).close()
        .workplane(offset=z_half)
        .spline(profile_top).close()
        .loft(ruled=True)
    )

    print("  Joining halves...")
    solid = bottom_half.union(top_half)

    # Export
    output_file = OUTPUT_DIR / "test_herringbone.step"
    cq.exporters.export(solid, str(output_file))
    print(f"  Saved: {output_file}")

    return solid


def render_test():
    """Render the test herringbone."""
    import vtk
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer

    step_file = OUTPUT_DIR / "test_herringbone.step"
    solid = cq.importers.importStep(str(step_file))
    shape = solid.val().wrapped

    mesh = BRepMesh_IncrementalMesh(shape, 0.05)
    mesh.Perform()

    stl_path = OUTPUT_DIR / "test_herringbone.stl"
    writer = StlAPI_Writer()
    writer.Write(shape, str(stl_path))

    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(stl_path))
    reader.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.7, 0.7, 0.75)
    actor.GetProperty().SetSpecular(0.3)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(1.0, 1.0, 1.0)

    # Side view
    camera = renderer.GetActiveCamera()
    camera.SetPosition(80, 0, 0)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)
    renderer.ResetCamera()
    camera.Zoom(1.5)

    render_window = vtk.vtkRenderWindow()
    render_window.SetOffScreenRendering(1)
    render_window.AddRenderer(renderer)
    render_window.SetSize(1200, 800)
    render_window.Render()

    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(render_window)
    w2if.SetScale(2)
    w2if.Update()

    output_png = OUTPUT_DIR / "renders" / "test_herringbone_side.png"
    png_writer = vtk.vtkPNGWriter()
    png_writer.SetFileName(str(output_png))
    png_writer.SetInputConnection(w2if.GetOutputPort())
    png_writer.Write()
    print(f"  Side view: {output_png}")

    # 3D view
    camera.SetPosition(50, 60, 40)
    renderer.ResetCamera()
    camera.Zoom(1.3)
    render_window.Render()
    w2if.Modified()
    w2if.Update()

    output_png_3d = OUTPUT_DIR / "renders" / "test_herringbone_3d.png"
    png_writer.SetFileName(str(output_png_3d))
    png_writer.Write()
    print(f"  3D view: {output_png_3d}")

    stl_path.unlink()


def main():
    print("=" * 60)
    print("Test Herringbone (45° helix - exaggerated)")
    print("=" * 60)

    generate_test_herringbone()
    render_test()

    print("\nDone!")


if __name__ == "__main__":
    main()
