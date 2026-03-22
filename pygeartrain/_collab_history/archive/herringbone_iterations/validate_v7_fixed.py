"""Validate v7 - with proper mesh region detection"""
import numpy as np
import matplotlib.pyplot as plt
import os

output_dir = "output_herringbone_v7"

def load(f): return np.loadtxt(os.path.join(output_dir, f))

fig, axes = plt.subplots(3, 3, figsize=(18, 18))
z_levels = ['z_neg', 'z0', 'z_pos']
z_labels = ['z=-5mm', 'z=0mm', 'z=+5mm']

for row, (zl, zlab) in enumerate(zip(z_levels, z_labels)):
    ring = load(f"ring_30_{zl}.txt")
    sun = load(f"sun_6_{zl}.txt")
    planet0 = load(f"planet_12_0_{zl}.txt")
    planet1 = load(f"planet_12_1_{zl}.txt")
    planet2 = load(f"planet_12_2_{zl}.txt")

    # Get planet 0 center for reference
    p0_center_x = np.mean(planet0[:,0])
    p0_center_y = np.mean(planet0[:,1])

    # Column 0: Full assembly
    ax = axes[row, 0]
    ax.plot(ring[:,0], ring[:,1], 'b-', lw=0.5, label='Ring')
    ax.plot(sun[:,0], sun[:,1], 'r-', lw=0.5, label='Sun')
    ax.plot(planet0[:,0], planet0[:,1], 'g-', lw=0.5, label='P0')
    ax.plot(planet1[:,0], planet1[:,1], 'm-', lw=0.5, label='P1')
    ax.plot(planet2[:,0], planet2[:,1], 'c-', lw=0.5, label='P2')
    ax.scatter([p0_center_x], [p0_center_y], c='green', s=30, zorder=5)
    ax.set_xlim(-40, 40); ax.set_ylim(-40, 40)
    ax.set_aspect('equal')
    ax.set_title(f'Full Assembly ({zlab})')
    if row == 0: ax.legend(fontsize=7, loc='upper right')
    ax.grid(True, alpha=0.3)

    # Column 1: Sun-Planet 0 mesh (zoom to midpoint between sun and planet)
    ax = axes[row, 1]
    ax.plot(sun[:,0], sun[:,1], 'r-', lw=1.5, label='Sun')
    ax.plot(planet0[:,0], planet0[:,1], 'g-', lw=1.5, label='Planet 0')
    # Mesh is between sun outer and planet inner (toward sun)
    mesh_x = p0_center_x / 2  # Roughly halfway between origin and planet center
    mesh_y = p0_center_y / 2
    ax.set_xlim(mesh_x - 4, mesh_x + 4)
    ax.set_ylim(mesh_y - 4, mesh_y + 4)
    ax.set_aspect('equal')
    ax.set_title(f'Sun-Planet ({zlab})')
    if row == 0: ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Column 2: Planet 0-Ring mesh (zoom to planet outer edge toward ring)
    ax = axes[row, 2]
    ax.plot(ring[:,0], ring[:,1], 'b-', lw=1.5, label='Ring')
    ax.plot(planet0[:,0], planet0[:,1], 'g-', lw=1.5, label='Planet 0')
    # Mesh is at planet outer edge, away from sun
    # Direction from origin to planet center, extended outward
    dist_to_center = np.sqrt(p0_center_x**2 + p0_center_y**2)
    dir_x = p0_center_x / dist_to_center
    dir_y = p0_center_y / dist_to_center
    # Planet outer edge is ~14mm from planet center
    mesh_x = p0_center_x + dir_x * 14
    mesh_y = p0_center_y + dir_y * 14
    ax.set_xlim(mesh_x - 4, mesh_x + 4)
    ax.set_ylim(mesh_y - 4, mesh_y + 4)
    ax.set_aspect('equal')
    ax.set_title(f'Planet-Ring ({zlab})')
    if row == 0: ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.suptitle('v7 Validation - Mesh Axis Alignment + Ring Compensation', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'validation_fixed.png'), dpi=150)
print(f"Saved: {output_dir}/validation_fixed.png")
