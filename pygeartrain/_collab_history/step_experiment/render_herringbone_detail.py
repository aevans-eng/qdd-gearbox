"""
Render herringbone detail - side view looking at tooth edge to show V-pattern
"""

from pathlib import Path
import cadquery as cq

OUTPUT_DIR = Path(__file__).parent / "output"


def render_side_detail(step_file: Path, output_png: Path):
    """Render from the side, looking at a tooth to show herringbone V."""
    import vtk
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer

    print(f"Rendering {step_file.name} detail...")

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
    actor.GetProperty().SetColor(0.55, 0.6, 0.65)
    actor.GetProperty().SetSpecular(0.3)
    actor.GetProperty().SetSpecularPower(30)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(1.0, 1.0, 1.0)  # White background

    # Camera looking from the side, directly at the teeth
    # Position at Y = large value, looking at origin
    camera = renderer.GetActiveCamera()
    camera.SetPosition(0, 100, 0)  # Side view
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)  # Z is up
    renderer.ResetCamera()
    camera.Zoom(2.5)  # Zoom in on teeth

    render_window = vtk.vtkRenderWindow()
    render_window.SetOffScreenRendering(1)
    render_window.AddRenderer(renderer)
    render_window.SetSize(1200, 600)
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
    print("Herringbone Detail Views")
    print("=" * 60)

    renders_dir = OUTPUT_DIR / "renders"

    for name in ['sun', 'planet', 'ring']:
        step_file = OUTPUT_DIR / f"{name}_herringbone.step"
        if step_file.exists():
            output_png = renders_dir / f"{name}_herringbone_detail.png"
            render_side_detail(step_file, output_png)


if __name__ == "__main__":
    main()
