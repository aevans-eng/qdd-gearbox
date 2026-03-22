"""Render all 3 approaches side by side for comparison"""

from pathlib import Path
import cadquery as cq

OUTPUT_DIR = Path(__file__).parent / "output"


def render_gear(step_file: Path, output_png: Path):
    import vtk
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer

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

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(1.0, 1.0, 1.0)

    # Side view
    camera = renderer.GetActiveCamera()
    camera.SetPosition(100, 0, 0)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)
    renderer.ResetCamera()
    camera.Zoom(1.8)

    render_window = vtk.vtkRenderWindow()
    render_window.SetOffScreenRendering(1)
    render_window.AddRenderer(renderer)
    render_window.SetSize(800, 600)
    render_window.Render()

    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(render_window)
    w2if.SetScale(2)
    w2if.Update()

    png_writer = vtk.vtkPNGWriter()
    png_writer.SetFileName(str(output_png))
    png_writer.SetInputConnection(w2if.GetOutputPort())
    png_writer.Write()

    stl_path.unlink()


def main():
    renders_dir = OUTPUT_DIR / "renders"
    renders_dir.mkdir(exist_ok=True)

    gears = ['sun', 'planet', 'ring']
    approaches = ['approach1', 'approach2', 'approach3']

    for gear in gears:
        print(f"\nRendering {gear}:")
        for approach in approaches:
            step_file = OUTPUT_DIR / f"{gear}_{approach}.step"
            if step_file.exists():
                output_png = renders_dir / f"{gear}_{approach}.png"
                render_gear(step_file, output_png)
                print(f"  {approach}: {output_png.name}")

    print("\nDone!")


if __name__ == "__main__":
    main()
