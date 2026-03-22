"""Validate v5 with gear ratio twist"""
import numpy as np
import matplotlib.pyplot as plt
import os

output_dir = "output_herringbone_v5"
carrier_radius = 20.7496

def load(f): return np.loadtxt(os.path.join(output_dir, f))
def translate(p, dx, dy):
    t = p.copy(); t[:,0] += dx; t[:,1] += dy; return t

fig, axes = plt.subplots(3, 2, figsize=(14, 18))
z_levels = ['z_neg', 'z0', 'z_pos']
z_labels = ['z=-5mm', 'z=0mm', 'z=+5mm']

for row, (zl, zlab) in enumerate(zip(z_levels, z_labels)):
    ring = load(f"ring_30_{zl}.txt")
    sun = load(f"sun_6_{zl}.txt")
    planet = translate(load(f"planet_12_0_{zl}.txt"), carrier_radius, 0)

    ax = axes[row, 0]
    ax.plot(sun[:,0], sun[:,1], 'r-', lw=1.5, label='Sun')
    ax.plot(planet[:,0], planet[:,1], 'g-', lw=1.5, label='Planet')
    ax.set_xlim(4, 12); ax.set_ylim(-4, 4)
    ax.set_aspect('equal'); ax.set_title(f'Sun-Planet ({zlab})')
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

    ax = axes[row, 1]
    ax.plot(ring[:,0], ring[:,1], 'b-', lw=1.5, label='Ring')
    ax.plot(planet[:,0], planet[:,1], 'g-', lw=1.5, label='Planet')
    ax.set_xlim(30, 38); ax.set_ylim(-4, 4)
    ax.set_aspect('equal'); ax.set_title(f'Planet-Ring ({zlab})')
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

plt.suptitle('v5 Validation - Gear Ratio Twist', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'validation.png'), dpi=150)
print(f"Saved: {output_dir}/validation.png")
