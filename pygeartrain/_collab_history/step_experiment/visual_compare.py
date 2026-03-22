"""
Visual Comparison: Original XYZ vs STEP File Geometry
=====================================================
Creates side-by-side comparison of original profile and STEP geometry.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import cadquery as cq

INPUT_DIR = Path(__file__).parent.parent / "design_log" / "cad_export" / "Gearset_A_S4_P6_R16_N4"
OUTPUT_DIR = Path(__file__).parent / "output"


def load_xyz_points(filepath: Path) -> np.ndarray:
    """Load XYZ points from a text file."""
    points = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                coords = line.split()
                if len(coords) >= 2:
                    x, y = float(coords[0]), float(coords[1])
                    points.append((x, y))
    return np.array(points)


def extract_top_face_edges(step_file: Path):
    """
    Extract boundary points from the top face of a STEP solid using tessellation.
    Returns list of boundary point arrays.
    """
    solid = cq.importers.importStep(str(step_file))

    # Get the top face (highest Z)
    top_face = solid.faces(">Z").val()

    # Tessellate the face to get triangles
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.BRep import BRep_Tool
    from OCP.TopLoc import TopLoc_Location

    # Mesh the shape
    mesh = BRepMesh_IncrementalMesh(top_face.wrapped, 0.05)  # Fine tolerance
    mesh.Perform()

    # Get the triangulation
    loc = TopLoc_Location()
    triangulation = BRep_Tool.Triangulation_s(top_face.wrapped, loc)

    if triangulation is None:
        return None

    # Extract unique boundary points (vertices on the edge)
    # For a gear profile, we want the outer boundary
    all_points = []
    n_nodes = triangulation.NbNodes()

    for i in range(1, n_nodes + 1):
        pnt = triangulation.Node(i)
        # Only keep points at the top Z level (within tolerance)
        if abs(pnt.Z() - 5.0) < 0.01:  # Top face at Z=5
            all_points.append((pnt.X(), pnt.Y()))

    # Remove duplicates and sort by angle for cleaner plotting
    if all_points:
        points = np.array(all_points)
        # Remove exact duplicates
        points = np.unique(points, axis=0)
        # Sort by angle from center
        angles = np.arctan2(points[:, 1], points[:, 0])
        sorted_idx = np.argsort(angles)
        points = points[sorted_idx]
        return points

    return None


def create_comparison(name: str, xyz_file: Path, step_file: Path, output_file: Path):
    """Create a visual comparison plot."""
    print(f"\nComparing {name}...")

    # Load original XYZ points
    original_points = load_xyz_points(xyz_file)
    print(f"  Original: {len(original_points)} points")

    # Extract from STEP
    try:
        step_points = extract_top_face_edges(step_file)
        has_step = step_points is not None and len(step_points) > 0
        if has_step:
            print(f"  STEP: {len(step_points)} sampled points")
    except Exception as e:
        print(f"  Warning: Could not extract STEP edges: {e}")
        step_points = None
        has_step = False

    # Create figure
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    # Left: Original XYZ profile
    ax1 = axes[0]
    ax1.plot(original_points[:, 0], original_points[:, 1], 'b-', linewidth=1.5, label='Profile')
    ax1.scatter(original_points[::10, 0], original_points[::10, 1], c='blue', s=10, alpha=0.5)
    ax1.set_title(f'{name.upper()} - Original XYZ Points\n({len(original_points)} points)', fontsize=12)
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='k', linewidth=0.5)
    ax1.axvline(x=0, color='k', linewidth=0.5)

    # Right: STEP extracted profile
    ax2 = axes[1]
    if has_step:
        ax2.scatter(step_points[:, 0], step_points[:, 1], c='red', s=5, alpha=0.7, label='STEP edges')
        ax2.set_title(f'{name.upper()} - STEP File Geometry\n({len(step_points)} sampled points)', fontsize=12)
    else:
        ax2.text(0.5, 0.5, 'Could not extract\nSTEP geometry',
                 transform=ax2.transAxes, ha='center', va='center', fontsize=14)
        ax2.set_title(f'{name.upper()} - STEP File Geometry', fontsize=12)

    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='k', linewidth=0.5)
    ax2.axvline(x=0, color='k', linewidth=0.5)

    # Match axis limits
    all_x = original_points[:, 0]
    all_y = original_points[:, 1]
    margin = 5
    xlim = (all_x.min() - margin, all_x.max() + margin)
    ylim = (all_y.min() - margin, all_y.max() + margin)
    ax1.set_xlim(xlim)
    ax1.set_ylim(ylim)
    ax2.set_xlim(xlim)
    ax2.set_ylim(ylim)

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_file}")
    return has_step


def main():
    print("=" * 60)
    print("Visual Comparison: XYZ vs STEP")
    print("=" * 60)

    renders_dir = OUTPUT_DIR / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)

    gears = [
        ('sun', INPUT_DIR / 'sun_z0.txt', OUTPUT_DIR / 'sun.step'),
        ('planet', INPUT_DIR / 'planet_z0.txt', OUTPUT_DIR / 'planet.step'),
        ('ring', INPUT_DIR / 'ring_z0.txt', OUTPUT_DIR / 'ring.step'),
    ]

    for name, xyz_file, step_file in gears:
        if xyz_file.exists() and step_file.exists():
            output_file = renders_dir / f"{name}_comparison.png"
            create_comparison(name, xyz_file, step_file, output_file)
        else:
            print(f"WARNING: Missing files for {name}")

    print("\n" + "=" * 60)
    print("Comparison images saved to:", renders_dir)
    print("=" * 60)


if __name__ == "__main__":
    main()
