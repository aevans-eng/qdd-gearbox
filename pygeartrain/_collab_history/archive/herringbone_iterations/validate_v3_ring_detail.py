"""
Detailed planet-ring mesh validation with tighter zoom
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import math

output_dir = "output_herringbone_v3"
carrier_radius = 20.7496

def load_profile(filename):
    filepath = os.path.join(output_dir, filename)
    return np.loadtxt(filepath)

def translate(points, dx, dy):
    translated = points.copy()
    translated[:, 0] += dx
    translated[:, 1] += dy
    return translated

# Load z0 level (center of herringbone)
ring = load_profile("ring_30_z0.txt")
planet_0 = load_profile("planet_12_0_z0.txt")

# Position planet 0 at carrier radius on X-axis
pos_x = carrier_radius
pos_y = 0
planet_positioned = translate(planet_0, pos_x, pos_y)

# Planet outer radius from unpositioned profile
planet_radii = np.linalg.norm(planet_0[:, :2], axis=1)
planet_outer_radius = np.max(planet_radii)
print(f"Planet outer radius: {planet_outer_radius:.2f} mm")

# Planet 0 center is at (20.75, 0)
# Planet outer edge toward ring is at x ≈ 20.75 + 6.5 = 27.25 mm
planet_outer_x = carrier_radius + planet_outer_radius

# Ring inner radius (where teeth valleys are)
ring_radii = np.linalg.norm(ring[:, :2], axis=1)
ring_inner_radius = np.min(ring_radii)
ring_outer_radius = np.max(ring_radii)
print(f"Ring inner radius: {ring_inner_radius:.2f} mm")
print(f"Ring outer radius: {ring_outer_radius:.2f} mm")
print(f"Planet outer edge X: {planet_outer_x:.2f} mm")

# The mesh point is where planet touches ring
mesh_x = (planet_outer_x + ring_inner_radius) / 2
print(f"Approximate mesh X: {mesh_x:.2f} mm")

# Create figure with multiple zoom levels
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Plot 1: Wide view showing planet 0 and ring
ax = axes[0]
ax.plot(ring[:, 0], ring[:, 1], 'b-', linewidth=0.8, label='Ring (internal teeth)')
ax.plot(planet_positioned[:, 0], planet_positioned[:, 1], 'g-', linewidth=0.8, label='Planet 0')
ax.scatter([carrier_radius], [0], color='red', s=50, zorder=5, label='Planet center')
ax.set_xlim(10, 40)
ax.set_ylim(-15, 15)
ax.set_aspect('equal')
ax.set_title('Planet-Ring Overview')
ax.legend(fontsize=8, loc='upper left')
ax.grid(True, alpha=0.3)

# Plot 2: Medium zoom on mesh region
ax = axes[1]
ax.plot(ring[:, 0], ring[:, 1], 'b-', linewidth=1.5, label='Ring')
ax.plot(planet_positioned[:, 0], planet_positioned[:, 1], 'g-', linewidth=1.5, label='Planet 0')
ax.set_xlim(22, 32)
ax.set_ylim(-5, 5)
ax.set_aspect('equal')
ax.set_title('Planet-Ring Mesh Region')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Plot 3: Tight zoom on teeth
ax = axes[2]
ax.plot(ring[:, 0], ring[:, 1], 'b-', linewidth=2, label='Ring', marker='.', markersize=2)
ax.plot(planet_positioned[:, 0], planet_positioned[:, 1], 'g-', linewidth=2, label='Planet 0', marker='.', markersize=2)
ax.set_xlim(25, 30)
ax.set_ylim(-2.5, 2.5)
ax.set_aspect('equal')
ax.set_title('Planet-Ring Teeth Detail')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

plt.suptitle('Planet-Ring Mesh Detail at z=0mm', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'validation_ring_detail.png'), dpi=150)
print(f"Saved: {output_dir}/validation_ring_detail.png")
plt.show()
