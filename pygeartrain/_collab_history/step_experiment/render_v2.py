"""
Render herringbone v2 with edge highlighting
"""

from pathlib import Path
import cadquery as cq

OUTPUT_DIR = Path(__file__).parent / "output"


def render_with_edges(step_file: Path, output_png: Path):
    """Render with edge highlighting to show herringbone pattern."""
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

    # Main surface
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.7, 0.75, 0.8)
    actor.GetProperty().SetSpecular(0.2)

    # Edge extraction for highlighting
    edges = vtk.vtkFeatureEdges()
    edges.SetInputConnection(reader.GetOutputPort())
    edges.BoundaryEdgesOn()
    edges.FeatureEdgesOn()
    edges.ManifoldEdgesOff()
    edges.NonManifoldEdgesOff()
    edges.SetFeatureAngle(30)  # Detect edges at 30° angle changes

    edge_mapper = vtk.vtkPolyDataMapper()
    edge_mapper.SetInputConnection(edges.GetOutputPort())

    edge_actor = vtk.vtkActor()
    edge_actor.SetMapper(edge_mapper)
    edge_actor.GetProperty().SetColor(0.1, 0.1, 0.1)
    edge_actor.GetProperty().SetLineWidth(2)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.AddActor(edge_actor)
    renderer.SetBackground(1.0, 1.0, 1.0)

    # Angled view to show V-pattern
    camera = renderer.GetActiveCamera()
    camera.SetPosition(40, 60, 25)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)
    renderer.ResetCamera()
    camera.Zoom(1.6)

    render_window = vtk.vtkRenderWindow()
    render_window.SetOffScreenRendering(1)
    render_window.AddRenderer(renderer)
    render_window.SetSize(1000, 1000)
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
            output_png = renders_dir / f"{name}_herringbone_v2.png"
            render_with_edges(step_file, output_png)


if __name__ == "__main__":
    main()
