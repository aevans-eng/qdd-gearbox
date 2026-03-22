"""Validate v7 - full assembly view"""
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

    # Column 0: Full assembly
    ax = axes[row, 0]
    ax.plot(ring[:,0], ring[:,1], 'b-', lw=0.5, label='Ring')
    ax.plot(sun[:,0], sun[:,1], 'r-', lw=0.5, label='Sun')
    ax.plot(planet0[:,0], planet0[:,1], 'g-', lw=0.5, label='Planet 0')
    ax.plot(planet1[:,0], planet1[:,1], 'm-', lw=0.5, label='Planet 1')
    ax.plot(planet2[:,0], planet2[:,1], 'c-', lw=0.5, label='Planet 2')
    ax.set_xlim(-40, 40); ax.set_ylim(-40, 40)
    ax.set_aspect('equal')
    ax.set_title(f'Full Assembly ({zlab})')
    if row == 0: ax.legend(fontsize=7, loc='upper right')
    ax.grid(True, alpha=0.3)

    # Column 1: Sun-Planet 0 mesh
    ax = axes[row, 1]
    ax.plot(sun[:,0], sun[:,1], 'r-', lw=1.5, label='Sun')
    ax.plot(planet0[:,0], planet0[:,1], 'g-', lw=1.5, label='Planet 0')
    # Dynamic zoom to mesh region
    sun_max_x = np.max(sun[:,0])
    planet_min_x = np.min(planet0[:,0])
    center_x = (sun_max_x + planet_min_x) / 2
    ax.set_xlim(center_x - 4, center_x + 4)
    ax.set_ylim(-4, 4)
    ax.set_aspect('equal')
    ax.set_title(f'Sun-Planet ({zlab})')
    if row == 0: ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Column 2: Planet 0-Ring mesh
    ax = axes[row, 2]
    ax.plot(ring[:,0], ring[:,1], 'b-', lw=1.5, label='Ring')
    ax.plot(planet0[:,0], planet0[:,1], 'g-', lw=1.5, label='Planet 0')
    # Dynamic zoom - find where planet outer meets ring inner
    planet_max_x = np.max(planet0[:,0])
    # Ring points near Y=0 region where planet 0 is
    planet_center_y = np.mean(planet0[:,1])
    ring_near_planet = ring[np.abs(ring[:,1] - planet_center_y) < 10]
    if len(ring_near_planet) > 0:
        ring_min_x = np.min(ring_near_planet[:,0])
    else:
        ring_min_x = planet_max_x + 3
    center_x = (planet_max_x + ring_min_x) / 2
    ax.set_xlim(center_x - 4, center_x + 4)
    ax.set_ylim(planet_center_y - 4, planet_center_y + 4)
    ax.set_aspect('equal')
    ax.set_title(f'Planet-Ring ({zlab})')
    if row == 0: ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.suptitle('v7 Full Validation - Mesh Axis Alignment (20° helix)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'validation_full.png'), dpi=150)
print(f"Saved: {output_dir}/validation_full.png")
