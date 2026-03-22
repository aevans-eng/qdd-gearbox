"""
Validate v4 herringbone fix
"""

import numpy as np
import matplotlib.pyplot as plt
import os

output_dir = "output_herringbone_v4"
carrier_radius = 20.7496

def load_profile(filename):
    return np.loadtxt(os.path.join(output_dir, filename))

def translate(points, dx, dy):
    t = points.copy()
    t[:, 0] += dx
    t[:, 1] += dy
    return t

fig, axes = plt.subplots(3, 2, figsize=(14, 18))

z_levels = ['z_neg', 'z0', 'z_pos']
z_labels = ['z=-5mm', 'z=0mm', 'z=+5mm']

for row, (z_level, z_label) in enumerate(zip(z_levels, z_labels)):
    ring = load_profile(f"ring_30_{z_level}.txt")
    sun = load_profile(f"sun_6_{z_level}.txt")
    planet = load_profile(f"planet_12_0_{z_level}.txt")
    planet_pos = translate(planet, carrier_radius, 0)

    # Sun-Planet mesh
    ax = axes[row, 0]
    ax.plot(sun[:, 0], sun[:, 1], 'r-', linewidth=1.5, label='Sun')
    ax.plot(planet_pos[:, 0], planet_pos[:, 1], 'g-', linewidth=1.5, label='Planet 0')
    ax.set_xlim(4, 12)
    ax.set_ylim(-4, 4)
    ax.set_aspect('equal')
    ax.set_title(f'Sun-Planet Mesh ({z_label})')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Planet-Ring mesh
    ax = axes[row, 1]
    ax.plot(ring[:, 0], ring[:, 1], 'b-', linewidth=1.5, label='Ring')
    ax.plot(planet_pos[:, 0], planet_pos[:, 1], 'g-', linewidth=1.5, label='Planet 0')
    ax.set_xlim(30, 38)
    ax.set_ylim(-4, 4)
    ax.set_aspect('equal')
    ax.set_title(f'Planet-Ring Mesh ({z_label})')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.suptitle('v4 Validation - Fixed Herringbone Twist', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'validation.png'), dpi=150)
print(f"Saved: {output_dir}/validation.png")
plt.show()
