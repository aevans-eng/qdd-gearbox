"""
Validate v10 - Show planet-ring mesh only (sun/planet unchanged from v9)
"""

import numpy as np
import matplotlib.pyplot as plt
import os

output_dir = "output_herringbone_v10"

def load(f):
    return np.loadtxt(os.path.join(output_dir, f))

# Reference points for zoom
carrier_radius = 20.75
planet_outer_r = 14.25

# Create 1x3 grid: planet-ring mesh at each z level
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

z_levels = [('z_neg', 'z=-5mm'), ('z0', 'z=0mm'), ('z_pos', 'z=+5mm')]

for col, (z_suffix, z_label) in enumerate(z_levels):
    # Load gears
    planet = load(f"planet_12_0_{z_suffix}.txt")
    ring = load(f"ring_30_{z_suffix}.txt")

    ax = axes[col]
    ax.plot(ring[:, 0], ring[:, 1], 'b-', lw=1.5, label='Ring')
    ax.plot(planet[:, 0], planet[:, 1], 'g-', lw=1.5, label='Planet')

    # Zoom to planet-ring interface
    zoom_x = carrier_radius + planet_outer_r
    ax.set_xlim(zoom_x - 4, zoom_x + 4)
    ax.set_ylim(-4, 4)
    ax.set_aspect('equal')
    ax.set_title(f'Planet-Ring @ {z_label}')
    ax.grid(True, alpha=0.3)
    if col == 0:
        ax.legend(fontsize=8)

plt.suptitle('v10: Ring Compensation = 0.343° (sun/planet unchanged from v9)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'v10_validation.png'), dpi=150)
print(f"Saved: {output_dir}/v10_validation.png")
