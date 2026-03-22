"""Render herringbone v3"""

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

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(1.0, 1.0, 1.0)

    camera = renderer.GetActiveCamera()
    camera.SetPosition(*camera_pos)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)
    renderer.ResetCamera()
    camera.Zoom(1.8)

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
        step_file = OUTPUT_DIR / f"{name}_herringbone_v3.step"
        if step_file.exists():
            # Side view
            output_png = renders_dir / f"{name}_v3_side.png"
            render_gear(step_file, output_png, camera_pos=(100, 0, 0))

            # 3D view
            output_png_3d = renders_dir / f"{name}_v3_3d.png"
            render_gear(step_file, output_png_3d, camera_pos=(50, 60, 35))


if __name__ == "__main__":
    main()
