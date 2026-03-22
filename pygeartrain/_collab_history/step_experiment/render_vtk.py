"""
Direct VTK 3D Renderer for STEP files
=====================================
"""

from pathlib import Path
import cadquery as cq

OUTPUT_DIR = Path(__file__).parent / "output"


def render_gear_vtk(step_file: Path, output_png: Path):
    """Render STEP file to PNG using VTK offscreen rendering."""
    import vtk
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer

    print(f"Rendering {step_file.name}...")

    # Load STEP
    solid = cq.importers.importStep(str(step_file))
    shape = solid.val().wrapped

    # Mesh the shape for STL export
    mesh = BRepMesh_IncrementalMesh(shape, 0.05)  # Fine mesh
    mesh.Perform()

    # Export to STL (temporary)
    stl_path = output_png.with_suffix('.stl')
    writer = StlAPI_Writer()
    writer.Write(shape, str(stl_path))

    # Read STL into VTK
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(stl_path))
    reader.Update()

    # Create mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    # Create actor with nice material
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.7, 0.7, 0.75)  # Silver/steel color
    actor.GetProperty().SetSpecular(0.5)
    actor.GetProperty().SetSpecularPower(50)
    actor.GetProperty().SetAmbient(0.2)
    actor.GetProperty().SetDiffuse(0.8)

    # Create renderer with lighting
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(0.95, 0.95, 0.95)  # Light gray background

    # Add a light
    light = vtk.vtkLight()
    light.SetPosition(100, 100, 100)
    light.SetFocalPoint(0, 0, 0)
    light.SetIntensity(1.0)
    renderer.AddLight(light)

    # Set isometric camera
    camera = renderer.GetActiveCamera()
    camera.SetPosition(80, 80, 60)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)
    renderer.ResetCamera()
    camera.Zoom(1.3)

    # Create offscreen render window
    render_window = vtk.vtkRenderWindow()
    render_window.SetOffScreenRendering(1)
    render_window.AddRenderer(renderer)
    render_window.SetSize(800, 800)
    render_window.Render()

    # Capture to PNG
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(render_window)
    w2if.SetScale(2)  # 2x resolution
    w2if.Update()

    png_writer = vtk.vtkPNGWriter()
    png_writer.SetFileName(str(output_png))
    png_writer.SetInputConnection(w2if.GetOutputPort())
    png_writer.Write()

    print(f"  Saved: {output_png}")

    # Clean up STL
    stl_path.unlink()

    return True


def main():
    print("=" * 60)
    print("VTK 3D Renderer for Gear STEP Files")
    print("=" * 60)

    renders_dir = OUTPUT_DIR / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)

    for name in ['sun', 'planet', 'ring']:
        step_file = OUTPUT_DIR / f"{name}.step"
        if step_file.exists():
            output_png = renders_dir / f"{name}_3d.png"
            try:
                render_gear_vtk(step_file, output_png)
            except Exception as e:
                print(f"  Error: {e}")

    print("\nDone!")


if __name__ == "__main__":
    main()
