"""
Direct side view to show herringbone V-pattern
"""

from pathlib import Path
import cadquery as cq

OUTPUT_DIR = Path(__file__).parent / "output"


def render_direct_side(step_file: Path, output_png: Path):
    """Render from directly to the side to show V at center."""
    import vtk
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer

    print(f"Rendering {step_file.name} side view...")

    solid = cq.importers.importStep(str(step_file))
    shape = solid.val().wrapped

    mesh = BRepMesh_IncrementalMesh(shape, 0.005)  # Very fine mesh
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
    actor.GetProperty().SetAmbient(0.2)

    # Add silhouette edges
    silhouette = vtk.vtkPolyDataSilhouette()
    silhouette.SetInputConnection(reader.GetOutputPort())

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(1.0, 1.0, 1.0)

    # Direct side view - looking at the teeth from the side
    camera = renderer.GetActiveCamera()
    camera.SetPosition(100, 0, 0)  # Looking from +X axis
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)  # Z is up
    renderer.ResetCamera()
    camera.Zoom(2.0)

    # Add center line indicator
    line = vtk.vtkLineSource()
    line.SetPoint1(-50, 0, 0)
    line.SetPoint2(50, 0, 0)

    render_window = vtk.vtkRenderWindow()
    render_window.SetOffScreenRendering(1)
    render_window.AddRenderer(renderer)
    render_window.SetSize(1200, 800)
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
    renders_dir = OUTPUT_DIR / "renders"

    for name in ['sun', 'planet', 'ring']:
        step_file = OUTPUT_DIR / f"{name}_herringbone_v2.step"
        if step_file.exists():
            output_png = renders_dir / f"{name}_v2_side.png"
            render_direct_side(step_file, output_png)


if __name__ == "__main__":
    main()
