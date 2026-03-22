"""
create_v20c_clearance.py - Add laser-kerf style gaps where gears touch

Finds vertices that are too close to neighboring gears and pushes them
apart just enough to create separate outlines. Doesn't change overall
gear profiles - just creates minimum separation at contact points.
"""

import numpy as np
import trimesh
import os
from scipy.spatial import cKDTree

INPUT_DIR = "step_output_v20"
OUTPUT_DIR = "step_output_v20c"
N_planets = 4

MIN_GAP = 0.08  # mm - minimum gap to create (increased for margin)
THRESHOLD = 0.15  # mm - vertices closer than this get adjusted
ITERATIONS = 3  # Run multiple passes to converge

def load_stl(filename, directory=INPUT_DIR):
    path = os.path.join(directory, filename)
    if not os.path.exists(path):
        return None
    mesh = trimesh.load(path)
    if hasattr(mesh, 'geometry'):
        mesh = list(mesh.geometry.values())[0]
    return mesh

def push_apart(mesh, other_mesh, min_gap=MIN_GAP, threshold=THRESHOLD):
    """Push vertices of mesh away from other_mesh where they're too close."""
    tree = cKDTree(other_mesh.vertices)

    # Find closest point on other mesh for each vertex
    dists, indices = tree.query(mesh.vertices, k=1)

    # Find vertices that are too close
    too_close = dists < threshold
    n_adjusted = np.sum(too_close)

    if n_adjusted == 0:
        return mesh, 0

    # Calculate push direction (away from closest point on other mesh)
    new_vertices = mesh.vertices.copy()

    for i in np.where(too_close)[0]:
        closest_pt = other_mesh.vertices[indices[i]]
        direction = mesh.vertices[i] - closest_pt
        dist = dists[i]

        if dist > 1e-6:
            # Normalize direction
            direction = direction / dist
            # Push to minimum gap distance
            push_amount = min_gap - dist
            if push_amount > 0:
                new_vertices[i] = mesh.vertices[i] + direction * (push_amount + 0.01)

    result = trimesh.Trimesh(vertices=new_vertices, faces=mesh.faces)
    return result, n_adjusted

print("=" * 60)
print("CREATING v20c - Laser Kerf Gaps")
print(f"Min gap: {MIN_GAP}mm, Threshold: {THRESHOLD}mm")
print("=" * 60)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load all meshes
print("\nLoading meshes...")
sun = load_stl("sun.stl")
ring_internal = load_stl("ring_internal.stl")
ring = load_stl("ring.stl")
planets = [load_stl(f"planet_{i}.stl") for i in range(N_planets)]

# Iterative adjustment - run multiple passes
sun_adj = sun
planets_adj = list(planets)
ring_adj = ring

for iteration in range(ITERATIONS):
    print(f"\n=== ITERATION {iteration + 1}/{ITERATIONS} ===")

    # Adjust sun away from planets
    print("Adjusting Sun...")
    for i, p in enumerate(planets_adj):
        sun_adj, n = push_apart(sun_adj, p)
        if n > 0:
            print(f"  vs planet_{i}: {n} vertices")

    # Adjust planets away from sun and ring
    print("Adjusting Planets...")
    new_planets = []
    for i, planet in enumerate(planets_adj):
        p_adj = planet
        p_adj, n1 = push_apart(p_adj, sun_adj)
        p_adj, n2 = push_apart(p_adj, ring_internal)
        if n1 + n2 > 0:
            print(f"  Planet {i}: {n1} (sun) + {n2} (ring)")
        new_planets.append(p_adj)
    planets_adj = new_planets

    # Adjust ring away from planets
    print("Adjusting Ring...")
    for i, p in enumerate(planets_adj):
        ring_adj, n = push_apart(ring_adj, p)
        if n > 0:
            print(f"  vs planet_{i}: {n} vertices")

# Save outputs
print("\nSaving...")
sun_adj.export(os.path.join(OUTPUT_DIR, "sun.stl"))
ring_adj.export(os.path.join(OUTPUT_DIR, "ring.stl"))
ring_internal.export(os.path.join(OUTPUT_DIR, "ring_internal.stl"))
for i, p in enumerate(planets_adj):
    p.export(os.path.join(OUTPUT_DIR, f"planet_{i}.stl"))

# Create assembly
assembly = trimesh.util.concatenate([sun_adj, ring_adj] + planets_adj)
assembly.export(os.path.join(OUTPUT_DIR, "gearbox_assembled.stl"))

# Verify clearances
print("\n" + "-" * 40)
print("VERIFYING CLEARANCES")
print("-" * 40)

def min_dist(a, b):
    tree = cKDTree(b.vertices)
    d, _ = tree.query(a.vertices, k=1)
    return np.min(d)

for i, p in enumerate(planets_adj):
    d = min_dist(sun_adj, p)
    status = "OK" if d >= MIN_GAP else "STILL CLOSE"
    print(f"  Sun <-> Planet_{i}: {d:.4f}mm [{status}]")

for i, p in enumerate(planets_adj):
    d = min_dist(p, ring_internal)
    status = "OK" if d >= MIN_GAP else "STILL CLOSE"
    print(f"  Planet_{i} <-> Ring: {d:.4f}mm [{status}]")

print("\n" + "=" * 60)
print(f"v20c saved to {OUTPUT_DIR}/")
print("=" * 60)
