"""
Render herringbone gears with VTK - angled view to show the V-pattern
"""

from pathlib import Path
import cadquery as cq

OUTPUT_DIR = Path(__file__).parent / "output"


def render_gear_vtk(step_file: Path, output_png: Path, camera_pos=(60, 80, 40)):
    """Render STEP file to PNG with custom camera angle."""
    import vtk
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer

    print(f"Rendering {step_file.name}...")

    # Load STEP
    solid = cq.importers.importStep(str(step_file))
    shape = solid.val().wrapped

    # Mesh the shape
    mesh = BRepMesh_IncrementalMesh(shape, 0.02)  # Finer mesh for detail
    mesh.Perform()

    # Export to STL
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

    # Create actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.6, 0.65, 0.7)  # Steel blue-gray
    actor.GetProperty().SetSpecular(0.4)
    actor.GetProperty().SetSpecularPower(40)
    actor.GetProperty().SetAmbient(0.15)
    actor.GetProperty().SetDiffuse(0.85)

    # Create renderer
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(0.92, 0.92, 0.95)

    # Add lights
    light1 = vtk.vtkLight()
    light1.SetPosition(100, 100, 80)
    light1.SetFocalPoint(0, 0, 0)
    light1.SetIntensity(0.8)
    renderer.AddLight(light1)

    light2 = vtk.vtkLight()
    light2.SetPosition(-50, -50, 100)
    light2.SetFocalPoint(0, 0, 0)
    light2.SetIntensity(0.4)
    renderer.AddLight(light2)

    # Set camera - angled to show herringbone pattern
    camera = renderer.GetActiveCamera()
    camera.SetPosition(*camera_pos)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)
    renderer.ResetCamera()
    camera.Zoom(1.4)

    # Create offscreen render window
    render_window = vtk.vtkRenderWindow()
    render_window.SetOffScreenRendering(1)
    render_window.AddRenderer(renderer)
    render_window.SetSize(1000, 1000)
    render_window.Render()

    # Capture to PNG
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(render_window)
    w2if.SetScale(2)
    w2if.Update()

    png_writer = vtk.vtkPNGWriter()
    png_writer.SetFileName(str(output_png))
    png_writer.SetInputConnection(w2if.GetOutputPort())
    png_writer.Write()

    print(f"  Saved: {output_png}")

    # Clean up STL
    stl_path.unlink()


def main():
    print("=" * 60)
    print("Herringbone Gear 3D Renders")
    print("=" * 60)

    renders_dir = OUTPUT_DIR / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)

    gears = ['sun', 'planet', 'ring']

    for name in gears:
        step_file = OUTPUT_DIR / f"{name}_herringbone.step"
        if step_file.exists():
            # Isometric view showing herringbone pattern
            output_png = renders_dir / f"{name}_herringbone_3d.png"
            render_gear_vtk(step_file, output_png, camera_pos=(50, 70, 35))

            # Side view to clearly show the V-pattern
            output_png_side = renders_dir / f"{name}_herringbone_side.png"
            render_gear_vtk(step_file, output_png_side, camera_pos=(80, 10, 5))

    print("\nDone!")


if __name__ == "__main__":
    main()
