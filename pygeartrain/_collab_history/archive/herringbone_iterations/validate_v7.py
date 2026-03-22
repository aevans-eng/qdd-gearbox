"""Validate v7 - mesh axis alignment method"""
import numpy as np
import matplotlib.pyplot as plt
import os

output_dir = "output_herringbone_v7"

def load(f): return np.loadtxt(os.path.join(output_dir, f))

fig, axes = plt.subplots(3, 2, figsize=(14, 18))
z_levels = ['z_neg', 'z0', 'z_pos']
z_labels = ['z=-5mm', 'z=0mm', 'z=+5mm']

for row, (zl, zlab) in enumerate(zip(z_levels, z_labels)):
    ring = load(f"ring_30_{zl}.txt")
    sun = load(f"sun_6_{zl}.txt")
    # In v7, planet is already positioned (translation baked in)
    planet = load(f"planet_12_0_{zl}.txt")

    # Sun-Planet mesh
    ax = axes[row, 0]
    ax.plot(sun[:,0], sun[:,1], 'r-', lw=1.5, label='Sun')
    ax.plot(planet[:,0], planet[:,1], 'g-', lw=1.5, label='Planet')

    # Find mesh region dynamically
    sun_max_x = np.max(sun[:,0])
    planet_min_x = np.min(planet[:,0])
    mesh_x = (sun_max_x + planet_min_x) / 2

    ax.set_xlim(mesh_x - 5, mesh_x + 5)
    ax.set_ylim(-4, 4)
    ax.set_aspect('equal')
    ax.set_title(f'Sun-Planet ({zlab})')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Planet-Ring mesh
    ax = axes[row, 1]
    ax.plot(ring[:,0], ring[:,1], 'b-', lw=1.5, label='Ring')
    ax.plot(planet[:,0], planet[:,1], 'g-', lw=1.5, label='Planet')

    # Find planet-ring mesh region
    planet_max_x = np.max(planet[:,0])
    ring_min_x = np.min(ring[:,0][ring[:,1] > -5])  # Ring points near y=0
    mesh_x = (planet_max_x + ring_min_x) / 2

    ax.set_xlim(mesh_x - 5, mesh_x + 5)
    ax.set_ylim(-4, 4)
    ax.set_aspect('equal')
    ax.set_title(f'Planet-Ring ({zlab})')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.suptitle('v7 Validation - Mesh Axis Alignment (20° helix)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'validation.png'), dpi=150)
print(f"Saved: {output_dir}/validation.png")
