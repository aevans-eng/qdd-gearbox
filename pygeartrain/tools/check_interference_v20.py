"""
check_interference_v20.py - Fast interference check using collision detection
"""

import numpy as np
import trimesh
import os
from scipy.spatial import cKDTree

OUTPUT_DIR = "step_output_v20"
N_planets = 4

def load_stl(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return None
    return trimesh.load(path)

def min_vertex_distance(mesh_a, mesh_b):
    """Fast minimum distance between mesh vertices using KD-tree."""
    tree = cKDTree(mesh_b.vertices)
    dists, _ = tree.query(mesh_a.vertices, k=1)
    return np.min(dists)

print("=" * 60)
print("INTERFERENCE CHECK - v20 (4 Planets)")
print("=" * 60)

# Load meshes
print("\nLoading meshes...")
sun = load_stl("sun.stl")
ring_internal = load_stl("ring_internal.stl")
planets = [load_stl(f"planet_{i}.stl") for i in range(N_planets)]

print(f"  Sun: {len(sun.vertices)} vertices")
print(f"  Ring: {len(ring_internal.vertices)} vertices")
for i, p in enumerate(planets):
    c = p.centroid
    print(f"  Planet {i}: {len(p.vertices)} verts at ({c[0]:.1f}, {c[1]:.1f})")

# Check minimum distances (fast vertex-to-vertex)
print("\n" + "-" * 40)
print("MINIMUM VERTEX DISTANCES")
print("-" * 40)

all_distances = []

# Sun vs planets
for i, p in enumerate(planets):
    d = min_vertex_distance(sun, p)
    status = "OVERLAP LIKELY!" if d < 0.05 else "TIGHT" if d < 0.15 else "OK"
    print(f"  Sun <-> Planet_{i}: {d:.4f}mm [{status}]")
    all_distances.append(("sun", f"planet_{i}", d))

# Planets vs ring
for i, p in enumerate(planets):
    d = min_vertex_distance(p, ring_internal)
    status = "OVERLAP LIKELY!" if d < 0.05 else "TIGHT" if d < 0.15 else "OK"
    print(f"  Planet_{i} <-> Ring: {d:.4f}mm [{status}]")
    all_distances.append((f"planet_{i}", "ring", d))

# Adjacent planets
for i in range(N_planets):
    j = (i + 1) % N_planets
    d = min_vertex_distance(planets[i], planets[j])
    status = "OVERLAP LIKELY!" if d < 0.05 else "TIGHT" if d < 0.15 else "OK"
    print(f"  Planet_{i} <-> Planet_{j}: {d:.4f}mm [{status}]")
    all_distances.append((f"planet_{i}", f"planet_{j}", d))

# Summary
print("\n" + "=" * 60)
min_d = min(d[2] for d in all_distances)
min_pair = [d for d in all_distances if d[2] == min_d][0]

print(f"MINIMUM CLEARANCE: {min_d:.4f}mm ({min_pair[0]} <-> {min_pair[1]})")

if min_d < 0.05:
    print("\nWARNING: Parts may intersect or be too close!")
    print("Slicer will likely fuse these parts together.")
    print("SOLUTION: Increase PROFILE_OFFSET_MM (currently -0.10mm)")
elif min_d < 0.15:
    print("\nTIGHT FIT: May work on well-tuned printer.")
    print("Risk of parts fusing on first layer or with elephant's foot.")
elif min_d < 0.30:
    print("\nGOOD: Should print-in-place reliably.")
else:
    print("\nLOOSE: Parts will have noticeable play/backlash.")

print("\nCurrent settings:")
print("  PROFILE_OFFSET_MM = -0.10 (0.20mm total mesh clearance)")
print("=" * 60)
