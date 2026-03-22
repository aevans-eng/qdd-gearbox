"""
Validate v11 - Show planet-ring mesh and measure remaining offset
"""

import numpy as np
import matplotlib.pyplot as plt
import os

output_dir = "output_herringbone_v11"

def load(f):
    return np.loadtxt(os.path.join(output_dir, f))

# Reference points for zoom
carrier_radius = 20.75
planet_outer_r = 14.25

# Create 1x3 grid: planet-ring mesh at each z level
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

z_levels = [('z_neg', 'z=-5mm'), ('z0', 'z=0mm'), ('z_pos', 'z=+5mm')]

for col, (z_suffix, z_label) in enumerate(z_levels):
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

plt.suptitle('v11: Ring Compensation = 0.21° (measured exact)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'v11_validation.png'), dpi=150)
print(f"Saved: {output_dir}/v11_validation.png")

# Measure remaining offset
print("\nRemaining offset measurement:")
for z_name, z_label in [('z_pos', 'z=+5mm'), ('z_neg', 'z=-5mm')]:
    planet = load(f"planet_12_0_{z_name}.txt")
    ring = load(f"ring_30_{z_name}.txt")

    planet_outer_idx = np.argmax(planet[:, 0])
    planet_outer = planet[planet_outer_idx, :2]

    ring_2d = ring[:, :2]
    distances = np.linalg.norm(ring_2d - planet_outer, axis=1)
    nearest_idx = np.argmin(distances)
    ring_nearest = ring_2d[nearest_idx]

    planet_angle = np.degrees(np.arctan2(planet_outer[1], planet_outer[0]))
    ring_angle = np.degrees(np.arctan2(ring_nearest[1], ring_nearest[0]))
    angle_diff = planet_angle - ring_angle

    a = np.linalg.norm(ring_nearest - planet_outer)
    r = np.linalg.norm(ring_nearest)

    print(f"  {z_label}: offset = {angle_diff:.4f}°, distance = {a:.4f}mm")
