"""
Complete validation of v3 export:
- All 3 Z-levels (z_neg, z0, z_pos)
- Sun-planet mesh interaction
- Planet-ring mesh interaction
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import math

output_dir = "output_herringbone_v3"

# Configuration
carrier_radius = 20.7496
N_planets = 3

def load_profile(filename):
    """Load XYZ profile, return X, Y, Z."""
    filepath = os.path.join(output_dir, filename)
    data = np.loadtxt(filepath)
    return data

def translate(points, dx, dy):
    """Translate 2D points (only X, Y)."""
    translated = points.copy()
    translated[:, 0] += dx
    translated[:, 1] += dy
    return translated

# Load all Z-levels for each gear
z_levels = ['z_neg', 'z0', 'z_pos']
z_labels = ['z=-5mm', 'z=0mm', 'z=+5mm']

# Create figure: 3 rows (Z-levels) x 3 cols (full, sun-planet zoom, planet-ring zoom)
fig, axes = plt.subplots(3, 3, figsize=(18, 15))

for row, (z_level, z_label) in enumerate(zip(z_levels, z_labels)):
    # Load profiles for this Z-level
    ring = load_profile(f"ring_30_{z_level}.txt")
    sun = load_profile(f"sun_6_{z_level}.txt")
    planet_0 = load_profile(f"planet_12_0_{z_level}.txt")
    planet_1 = load_profile(f"planet_12_1_{z_level}.txt")
    planet_2 = load_profile(f"planet_12_2_{z_level}.txt")

    # Position planets
    planets_positioned = []
    for i, planet in enumerate([planet_0, planet_1, planet_2]):
        a = 2 * np.pi * i / N_planets
        pos_x = carrier_radius * math.cos(a)
        pos_y = carrier_radius * math.sin(a)
        positioned = translate(planet, pos_x, pos_y)
        planets_positioned.append(positioned)

    # Column 0: Full assembly
    ax = axes[row, 0]
    ax.plot(ring[:, 0], ring[:, 1], 'b-', linewidth=0.5, label='Ring')
    ax.plot(sun[:, 0], sun[:, 1], 'r-', linewidth=0.5, label='Sun')
    colors = ['g', 'm', 'c']
    for i, planet in enumerate(planets_positioned):
        ax.plot(planet[:, 0], planet[:, 1], f'{colors[i]}-', linewidth=0.5, label=f'Planet {i}')
    ax.set_aspect('equal')
    ax.set_title(f'Full Assembly ({z_label})')
    if row == 0:
        ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

    # Column 1: Sun-Planet 0 mesh zoom
    ax = axes[row, 1]
    ax.plot(sun[:, 0], sun[:, 1], 'r-', linewidth=1.5, label='Sun')
    ax.plot(planets_positioned[0][:, 0], planets_positioned[0][:, 1], 'g-', linewidth=1.5, label='Planet 0')

    # Zoom to mesh point (between sun outer and planet inner)
    zoom_x = carrier_radius / 2
    zoom_y = 0
    zoom_range = 6
    ax.set_xlim(zoom_x - zoom_range, zoom_x + zoom_range)
    ax.set_ylim(zoom_y - zoom_range, zoom_y + zoom_range)
    ax.set_aspect('equal')
    ax.set_title(f'Sun-Planet Mesh ({z_label})')
    if row == 0:
        ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

    # Column 2: Planet 0-Ring mesh zoom
    ax = axes[row, 2]
    ax.plot(ring[:, 0], ring[:, 1], 'b-', linewidth=1.5, label='Ring')
    ax.plot(planets_positioned[0][:, 0], planets_positioned[0][:, 1], 'g-', linewidth=1.5, label='Planet 0')

    # Zoom to ring mesh point (planet outer edge toward ring)
    # Planet 0 is at (carrier_radius, 0), ring inner edge is around radius ~27mm
    zoom_x = carrier_radius + 5  # Between planet outer and ring inner
    zoom_y = 0
    zoom_range = 6
    ax.set_xlim(zoom_x - zoom_range, zoom_x + zoom_range)
    ax.set_ylim(zoom_y - zoom_range, zoom_y + zoom_range)
    ax.set_aspect('equal')
    ax.set_title(f'Planet-Ring Mesh ({z_label})')
    if row == 0:
        ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

plt.suptitle('v3 Export Validation: All Z-Levels and Mesh Points', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'validation_complete.png'), dpi=150)
print(f"Saved: {output_dir}/validation_complete.png")
plt.show()
