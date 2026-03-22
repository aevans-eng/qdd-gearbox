"""
3D STEP File Renderer using VTK
================================
Renders STEP files to PNG images for visual inspection.
"""

import numpy as np
from pathlib import Path
import cadquery as cq

OUTPUT_DIR = Path(__file__).parent / "output"


def render_step_to_png(step_file: Path, output_file: Path, view='iso'):
    """
    Render a STEP file to a PNG image using CadQuery's VTK export.

    Args:
        step_file: Path to STEP file
        output_file: Path for output PNG
        view: 'iso', 'top', 'front', or 'right'
    """
    print(f"Rendering {step_file.name}...")

    # Load the STEP file
    solid = cq.importers.importStep(str(step_file))

    # Export to VTK format, then render
    # CadQuery can export to various formats
    try:
        # Try using the assembly export with SVG (simpler, works headlessly)
        svg_path = output_file.with_suffix('.svg')
        cq.exporters.export(solid, str(svg_path), exportType='SVG')
        print(f"  Exported SVG: {svg_path}")

        # Convert SVG to PNG using cairosvg if available
        try:
            import cairosvg
            cairosvg.svg2png(url=str(svg_path), write_to=str(output_file), scale=2.0)
            print(f"  Converted to PNG: {output_file}")
            return True
        except ImportError:
            print(f"  Note: Install cairosvg to convert SVG to PNG")
            return True  # SVG is still useful

    except Exception as e:
        print(f"  SVG export failed: {e}")

    # Fallback: Use VTK directly for 3D rendering
    try:
        import vtk
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        from OCP.StlAPI import StlAPI_Writer
        from OCP.BRep import BRep_Builder
        from OCP.TopoDS import TopoDS_Compound

        # Export to STL first (VTK can read STL easily)
        stl_path = output_file.with_suffix('.stl')

        # Mesh the shape
        shape = solid.val().wrapped
        mesh = BRepMesh_IncrementalMesh(shape, 0.1)
        mesh.Perform()

        # Write STL
        writer = StlAPI_Writer()
        writer.Write(shape, str(stl_path))
        print(f"  Exported STL: {stl_path}")

        # Now render STL with VTK
        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(stl_path))
        reader.Update()

        # Create mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.3, 0.5, 0.8)  # Blue-ish
        actor.GetProperty().SetSpecular(0.3)
        actor.GetProperty().SetSpecularPower(20)

        # Create renderer
        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        renderer.SetBackground(1.0, 1.0, 1.0)  # White background

        # Set camera based on view
        camera = renderer.GetActiveCamera()
        if view == 'iso':
            camera.SetPosition(100, 100, 100)
            camera.SetViewUp(0, 0, 1)
        elif view == 'top':
            camera.SetPosition(0, 0, 100)
            camera.SetViewUp(0, 1, 0)
        elif view == 'front':
            camera.SetPosition(0, -100, 0)
            camera.SetViewUp(0, 0, 1)

        renderer.ResetCamera()

        # Create render window (offscreen)
        render_window = vtk.vtkRenderWindow()
        render_window.SetOffScreenRendering(1)
        render_window.AddRenderer(renderer)
        render_window.SetSize(800, 800)
        render_window.Render()

        # Save to PNG
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(render_window)
        w2if.Update()

        writer = vtk.vtkPNGWriter()
        writer.SetFileName(str(output_file))
        writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()

        print(f"  Rendered PNG: {output_file}")
        return True

    except Exception as e:
        print(f"  VTK rendering failed: {e}")
        return False


def main():
    print("=" * 60)
    print("3D STEP Renderer")
    print("=" * 60)

    renders_dir = OUTPUT_DIR / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)

    gears = ['sun', 'planet', 'ring']

    for name in gears:
        step_file = OUTPUT_DIR / f"{name}.step"
        if step_file.exists():
            # Render isometric view
            output_file = renders_dir / f"{name}_3d_iso.png"
            render_step_to_png(step_file, output_file, view='iso')

            # Render top view
            output_file = renders_dir / f"{name}_3d_top.png"
            render_step_to_png(step_file, output_file, view='top')

    print("\n" + "=" * 60)
    print("Done! Check renders in:", renders_dir)


if __name__ == "__main__":
    main()
