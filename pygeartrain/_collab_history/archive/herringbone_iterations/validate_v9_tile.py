"""
Validate v9 - Tile of ring rotation offsets at z=-5mm

Shows planet-ring mesh with different ring rotation offsets.
Planet position is FIXED - zoom centered on planet outer point.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

output_dir = "output_herringbone_v9"

def load(f):
    return np.loadtxt(os.path.join(output_dir, f))

# Planet 0 outer point (fixed reference)
carrier_radius = 20.75
planet_outer_r = 14.25
zoom_x = carrier_radius + planet_outer_r  # ~35mm
zoom_y = 0

rotation_offsets = [-0.343, 0, 0.1, 0.2, 0.343, 0.685]

# Create tile: rows = z levels, cols = rotation offsets
fig, axes = plt.subplots(3, len(rotation_offsets), figsize=(24, 12))

z_levels = [('z_neg', 'z=-5mm'), ('z0', 'z=0mm'), ('z_pos', 'z=+5mm')]

for row, (z_suffix, z_label) in enumerate(z_levels):
    # Load planet (same for all columns - it's fixed)
    planet = load(f"planet_12_0_{z_suffix}.txt")

    for col, offset_deg in enumerate(rotation_offsets):
        ax = axes[row, col]

        # Load ring with this offset
        offset_str = f"{offset_deg:.2f}".replace('.', 'p')
        ring = load(f"ring_30_offset{offset_str}_{z_suffix}.txt")

        ax.plot(ring[:, 0], ring[:, 1], 'b-', lw=1.5, label='Ring')
        ax.plot(planet[:, 0], planet[:, 1], 'g-', lw=1.5, label='Planet')

        # Zoom to planet outer point
        ax.set_xlim(zoom_x - 4, zoom_x + 4)
        ax.set_ylim(zoom_y - 4, zoom_y + 4)
        ax.set_aspect('equal')

        if row == 0:
            sign = '+' if offset_deg >= 0 else ''
            ax.set_title(f'Ring {sign}{offset_deg:.2f}°')
        if col == 0:
            ax.set_ylabel(z_label)
        if row == 0 and col == 0:
            ax.legend(fontsize=7)

        ax.grid(True, alpha=0.3)

plt.suptitle('v9: Ring Rotation Sweep - Planet-Ring Mesh at Planet 0 Outer Point',
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'ring_rotation_tile.png'), dpi=150)
print(f"Saved: {output_dir}/ring_rotation_tile.png")
