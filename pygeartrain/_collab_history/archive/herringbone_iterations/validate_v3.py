"""
Validate v3 export - visualize all gears at their final positions
to confirm mesh rotation is working correctly.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import math

output_dir = "output_herringbone_v3"

# Planet positions from export
carrier_radius = 20.8609
N_planets = 3

def load_profile(filename):
    """Load XYZ profile, return just X,Y."""
    filepath = os.path.join(output_dir, filename)
    data = np.loadtxt(filepath)
    return data[:, :2]

def translate(points, dx, dy):
    """Translate 2D points."""
    translated = points.copy()
    translated[:, 0] += dx
    translated[:, 1] += dy
    return translated

def rotate_around_origin(points, angle_rad):
    """Rotate 2D points around origin."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    rotated = np.zeros_like(points)
    rotated[:, 0] = points[:, 0] * cos_a - points[:, 1] * sin_a
    rotated[:, 1] = points[:, 0] * sin_a + points[:, 1] * cos_a
    return rotated

# Load profiles (z0 level)
ring = load_profile("ring_30_z0.txt")
sun = load_profile("sun_6_z0.txt")
planet_0 = load_profile("planet_12_0_z0.txt")
planet_1 = load_profile("planet_12_1_z0.txt")
planet_2 = load_profile("planet_12_2_z0.txt")

# Position planets at their final locations
# Each needs: translate to carrier position, then rotate by placement angle
planets_positioned = []
for i, planet in enumerate([planet_0, planet_1, planet_2]):
    a = 2 * np.pi * i / N_planets  # placement angle

    # Translate to carrier position
    pos_x = carrier_radius * math.cos(a)
    pos_y = carrier_radius * math.sin(a)
    positioned = translate(planet, pos_x, pos_y)

    # Rotate around origin by placement angle
    # (This rotates the whole translated planet around the global origin)
    # Actually, we need to think about this...
    # The planet profile already has mesh rotation baked in.
    # We just translate it to its position. The "placement rotation"
    # is really just about where around the carrier it sits.

    planets_positioned.append((positioned, f"Planet {i}"))

# Create figure
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# Left plot: Full assembly
ax1 = axes[0]
ax1.plot(ring[:, 0], ring[:, 1], 'b-', linewidth=0.5, label='Ring')
ax1.plot(sun[:, 0], sun[:, 1], 'r-', linewidth=0.5, label='Sun')
colors = ['g', 'm', 'c']
for i, (planet, label) in enumerate(planets_positioned):
    ax1.plot(planet[:, 0], planet[:, 1], f'{colors[i]}-', linewidth=0.5, label=label)
ax1.set_aspect('equal')
ax1.set_title('v3 Full Assembly (z0 level)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Right plot: Zoomed to one mesh point
ax2 = axes[1]
# Zoom to planet 0 mesh with sun
zoom_center_x = carrier_radius / 2  # Between sun and planet 0
zoom_center_y = 0
zoom_range = 8

ax2.plot(ring[:, 0], ring[:, 1], 'b-', linewidth=0.5, label='Ring')
ax2.plot(sun[:, 0], sun[:, 1], 'r-', linewidth=1.0, label='Sun')
planet0_pos = planets_positioned[0][0]
ax2.plot(planet0_pos[:, 0], planet0_pos[:, 1], 'g-', linewidth=1.0, label='Planet 0')

ax2.set_xlim(zoom_center_x - zoom_range, zoom_center_x + zoom_range)
ax2.set_ylim(zoom_center_y - zoom_range, zoom_center_y + zoom_range)
ax2.set_aspect('equal')
ax2.set_title('Zoomed: Sun-Planet 0 Mesh Point')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'validation_plot.png'), dpi=150)
print(f"Saved: {output_dir}/validation_plot.png")
plt.show()
