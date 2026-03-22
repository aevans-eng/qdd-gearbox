"""Render existing STEP files to PNG"""

from pathlib import Path
import cadquery as cq

OUTPUT_DIR = Path(__file__).parent / "output"


def render_gear(step_file: Path, output_png: Path, camera_pos):
    import vtk
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer

    print(f"Rendering {step_file.name}...")

    solid = cq.importers.importStep(str(step_file))
    shape = solid.val().wrapped

    mesh = BRepMesh_IncrementalMesh(shape, 0.01)
    mesh.Perform()

    stl_path = output_png.with_suffix('.stl')
    writer = StlAPI_Writer()
    writer.Write(shape, str(stl_path))

    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(stl_path))
    reader.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.6, 0.65, 0.7)
    actor.GetProperty().SetSpecular(0.3)
    actor.GetProperty().SetSpecularPower(30)
    actor.GetProperty().SetAmbient(0.2)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(0.95, 0.95, 0.98)

    light = vtk.vtkLight()
    light.SetPosition(100, 100, 80)
    light.SetIntensity(0.9)
    renderer.AddLight(light)

    camera = renderer.GetActiveCamera()
    camera.SetPosition(*camera_pos)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)
    renderer.ResetCamera()
    camera.Zoom(1.6)

    render_window = vtk.vtkRenderWindow()
    render_window.SetOffScreenRendering(1)
    render_window.AddRenderer(renderer)
    render_window.SetSize(1200, 1200)
    render_window.Render()

    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(render_window)
    w2if.SetScale(2)
    w2if.Update()

    png_writer = vtk.vtkPNGWriter()
    png_writer.SetFileName(str(output_png))
    png_writer.SetInputConnection(w2if.GetOutputPort())
    png_writer.Write()

    print(f"  Saved: {output_png}")
    stl_path.unlink()


def main():
    print("=" * 60)
    print("Rendering STEP files to PNG")
    print("=" * 60)

    renders_dir = OUTPUT_DIR / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)

    gears = ['sun', 'planet', 'ring']

    # Render herringbone versions
    for name in gears:
        step_file = OUTPUT_DIR / f"{name}_herringbone_v3.step"
        if step_file.exists():
            # Isometric view
            output_png = renders_dir / f"{name}_herringbone_iso.png"
            render_gear(step_file, output_png, camera_pos=(50, 60, 35))

            # Side view to show herringbone pattern
            output_png_side = renders_dir / f"{name}_herringbone_side.png"
            render_gear(step_file, output_png_side, camera_pos=(80, 10, 5))
        else:
            print(f"Not found: {step_file}")

    print("\nDone! Renders saved to:", renders_dir)


if __name__ == "__main__":
    main()
