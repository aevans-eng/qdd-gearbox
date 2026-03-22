"""
Fixed validation visualization with correct zoom regions
"""

import numpy as np
import matplotlib.pyplot as plt
import os

output_dir = "output_herringbone_v3"
carrier_radius = 20.7496

def load_profile(filename):
    return np.loadtxt(os.path.join(output_dir, filename))

def translate(points, dx, dy):
    t = points.copy()
    t[:, 0] += dx
    t[:, 1] += dy
    return t

# Create figure: 3 rows (Z-levels) x 2 cols (sun-planet, planet-ring)
fig, axes = plt.subplots(3, 2, figsize=(14, 18))

z_levels = ['z_neg', 'z0', 'z_pos']
z_labels = ['z=-5mm', 'z=0mm', 'z=+5mm']

for row, (z_level, z_label) in enumerate(zip(z_levels, z_labels)):
    # Load profiles
    ring = load_profile(f"ring_30_{z_level}.txt")
    sun = load_profile(f"sun_6_{z_level}.txt")
    planet = load_profile(f"planet_12_0_{z_level}.txt")

    # Position planet
    planet_pos = translate(planet, carrier_radius, 0)

    # Find actual mesh regions
    sun_max_r = np.max(np.linalg.norm(sun[:,:2], axis=1))
    planet_min_r = np.min(np.linalg.norm(planet[:,:2], axis=1))
    planet_max_r = np.max(np.linalg.norm(planet[:,:2], axis=1))
    ring_min_r = np.min(np.linalg.norm(ring[:,:2], axis=1))

    # Sun-planet mesh point (where sun outer meets planet inner)
    sun_planet_mesh_x = (sun_max_r + carrier_radius - planet_max_r) / 2 + 2

    # Planet-ring mesh point (where planet outer meets ring inner)
    planet_ring_mesh_x = (carrier_radius + planet_max_r + ring_min_r) / 2

    # Column 0: Sun-Planet mesh
    ax = axes[row, 0]
    ax.plot(sun[:, 0], sun[:, 1], 'r-', linewidth=1.5, label='Sun')
    ax.plot(planet_pos[:, 0], planet_pos[:, 1], 'g-', linewidth=1.5, label='Planet 0')

    # Zoom to actual mesh region
    ax.set_xlim(4, 12)
    ax.set_ylim(-4, 4)
    ax.set_aspect('equal')
    ax.set_title(f'Sun-Planet Mesh ({z_label})')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Column 1: Planet-Ring mesh
    ax = axes[row, 1]
    ax.plot(ring[:, 0], ring[:, 1], 'b-', linewidth=1.5, label='Ring')
    ax.plot(planet_pos[:, 0], planet_pos[:, 1], 'g-', linewidth=1.5, label='Planet 0')

    # Zoom to actual mesh region (planet outer edge meets ring inner)
    ax.set_xlim(30, 38)
    ax.set_ylim(-4, 4)
    ax.set_aspect('equal')
    ax.set_title(f'Planet-Ring Mesh ({z_label})')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Print diagnostic info
    print(f"{z_label}:")
    print(f"  Sun max radius: {sun_max_r:.2f}")
    print(f"  Planet radii: {planet_min_r:.2f} - {planet_max_r:.2f}")
    print(f"  Ring inner radius: {ring_min_r:.2f}")
    print(f"  Planet outer edge X: {carrier_radius + planet_max_r:.2f}")
    print()

plt.suptitle('v3 Mesh Validation - Fixed Zoom Regions', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'validation_fixed.png'), dpi=150)
print(f"Saved: {output_dir}/validation_fixed.png")
plt.show()
