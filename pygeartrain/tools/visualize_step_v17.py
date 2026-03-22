"""
Visualize the generated STEP assembly to verify geometry.
Creates a 3D plot showing all gears in position.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import os

# Read STL files and visualize
def read_stl_ascii(filepath):
    """Read ASCII STL file and return vertices and faces."""
    vertices = []
    faces = []

    with open(filepath, 'r') as f:
        content = f.read()

    # Parse triangles
    import re
    triangles = re.findall(r'facet normal.*?endfacet', content, re.DOTALL)

    for tri in triangles:
        verts = re.findall(r'vertex\s+([-\d.e+]+)\s+([-\d.e+]+)\s+([-\d.e+]+)', tri)
        if len(verts) == 3:
            face_verts = []
            for v in verts:
                pt = [float(v[0]), float(v[1]), float(v[2])]
                vertices.append(pt)
                face_verts.append(len(vertices) - 1)
            faces.append(face_verts)

    return np.array(vertices), faces


def read_stl_binary(filepath):
    """Read binary STL file."""
    import struct

    vertices = []
    faces = []

    with open(filepath, 'rb') as f:
        header = f.read(80)
        num_triangles = struct.unpack('<I', f.read(4))[0]

        for i in range(num_triangles):
            # Normal (skip)
            f.read(12)
            # 3 vertices
            face_verts = []
            for j in range(3):
                x, y, z = struct.unpack('<fff', f.read(12))
                vertices.append([x, y, z])
                face_verts.append(len(vertices) - 1)
            faces.append(face_verts)
            # Attribute byte count
            f.read(2)

    return np.array(vertices), faces


def read_stl(filepath):
    """Read STL file (auto-detect ASCII vs binary)."""
    with open(filepath, 'rb') as f:
        header = f.read(80)

    # Check if ASCII
    try:
        header_str = header.decode('ascii')
        if 'solid' in header_str.lower():
            # Might be ASCII, try reading
            try:
                return read_stl_ascii(filepath)
            except:
                pass
    except:
        pass

    return read_stl_binary(filepath)


def plot_stl(ax, filepath, color, alpha=0.7, label=None, subsample=10):
    """Plot STL mesh on 3D axes with subsampling for speed."""
    vertices, faces = read_stl(filepath)

    if len(faces) == 0:
        print(f"  Warning: No faces in {filepath}")
        return

    # Subsample faces for faster rendering
    faces_subset = faces[::subsample]

    # Create polygon collection
    polygons = []
    for face in faces_subset:
        polygon = [vertices[i] for i in face]
        polygons.append(polygon)

    collection = Poly3DCollection(polygons, alpha=alpha, facecolor=color, edgecolor='none')
    ax.add_collection3d(collection)

    print(f"  Plotted {filepath} ({len(faces_subset)} triangles)")


# Output directory
OUTPUT_DIR = "step_output_v17"

# Create figure
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

# Plot each component with different colors
print("Loading STL files for visualization...")

# Sun - red/magenta
if os.path.exists(os.path.join(OUTPUT_DIR, "sun.stl")):
    plot_stl(ax, os.path.join(OUTPUT_DIR, "sun.stl"), 'magenta', alpha=0.8, subsample=5)

# Planets - green
for i in range(3):
    path = os.path.join(OUTPUT_DIR, f"planet_{i}.stl")
    if os.path.exists(path):
        plot_stl(ax, path, 'green', alpha=0.7, subsample=5)

# Ring - blue
if os.path.exists(os.path.join(OUTPUT_DIR, "ring.stl")):
    plot_stl(ax, os.path.join(OUTPUT_DIR, "ring.stl"), 'blue', alpha=0.5, subsample=10)

# Set axis properties
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm)')

# Set equal aspect ratio
max_range = 50
ax.set_xlim([-max_range, max_range])
ax.set_ylim([-max_range, max_range])
ax.set_zlim([-15, 15])

ax.set_title('v17 Herringbone Planetary Gearset (STEP Generated)\nR=48, P=18, S=12 | 80mm Ø × 22mm | 5:1 Ratio', fontsize=12)

# Set view angle similar to reference image
ax.view_init(elev=25, azim=45)

# Save figure
output_path = os.path.join(OUTPUT_DIR, "assembly_preview.png")
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"\nSaved preview to: {output_path}")

# Also save a top-down view
ax.view_init(elev=90, azim=0)
output_path2 = os.path.join(OUTPUT_DIR, "assembly_preview_topdown.png")
plt.savefig(output_path2, dpi=150, bbox_inches='tight')
print(f"Saved top-down view to: {output_path2}")

plt.show()
