"""
validate_final.py - Comprehensive mesh validation for herringbone planetary

Generates closeup images of all gear interactions:
- Sun-Planet mesh at z=-5mm, z=0mm, z=+5mm
- Planet-Ring mesh at z=-5mm, z=0mm, z=+5mm

Also measures and reports alignment offsets.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

OUTPUT_DIR = "output_herringbone_v14"

def load(f):
    return np.loadtxt(os.path.join(OUTPUT_DIR, f))

# Geometry from the generation script
carrier_radius = 20.75
sun_outer_r = 8.76
planet_outer_r = 14.25
ring_inner_r = 32.74

# Calculate interface points
sun_planet_interface = sun_outer_r  # Where sun meets planet (from origin)
planet_ring_interface = carrier_radius + planet_outer_r  # Where planet meets ring (from origin)

print("=" * 60)
print("HERRINGBONE PLANETARY VALIDATION")
print("=" * 60)

# Load all gears
z_levels = [('z_neg', 'z=-5mm', -5), ('z0', 'z=0mm', 0), ('z_pos', 'z=+5mm', 5)]

sun = {}
planet = {}
ring = {}

for z_suffix, z_label, z_val in z_levels:
    sun[z_suffix] = load(f"sun_6_{z_suffix}.txt")
    planet[z_suffix] = load(f"planet_12_0_{z_suffix}.txt")
    ring[z_suffix] = load(f"ring_30_{z_suffix}.txt")

# ============================================================================
# FIGURE 1: Sun-Planet Mesh (3 panels)
# ============================================================================
fig1, axes1 = plt.subplots(1, 3, figsize=(18, 6))

print("\n--- Sun-Planet Mesh ---")
for col, (z_suffix, z_label, z_val) in enumerate(z_levels):
    ax = axes1[col]

    s = sun[z_suffix]
    p = planet[z_suffix]

    ax.plot(s[:, 0], s[:, 1], 'r-', lw=2, label='Sun')
    ax.plot(p[:, 0], p[:, 1], 'g-', lw=2, label='Planet')

    # Zoom to sun-planet interface
    # The interface is roughly at x = sun_outer_r (toward planet at carrier_radius)
    zoom_x = sun_outer_r
    ax.set_xlim(zoom_x - 3, zoom_x + 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.set_title(f'Sun-Planet @ {z_label}', fontsize=14, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')

    # Measure closest approach
    sun_pts = s[:, :2]
    planet_pts = p[:, :2]

    # Find sun point closest to sun_outer_r on positive x
    sun_outer_idx = np.argmax(sun_pts[:, 0])
    sun_outer_pt = sun_pts[sun_outer_idx]

    # Find planet point closest to that
    dists = np.linalg.norm(planet_pts - sun_outer_pt, axis=1)
    planet_nearest_idx = np.argmin(dists)
    planet_nearest = planet_pts[planet_nearest_idx]

    clearance = np.linalg.norm(planet_nearest - sun_outer_pt)
    print(f"  {z_label}: clearance = {clearance:.4f} mm")

fig1.suptitle('Sun-Planet Mesh Verification', fontsize=16, fontweight='bold')
plt.tight_layout()
fig1.savefig(os.path.join(OUTPUT_DIR, 'validation_sun_planet.png'), dpi=150)
print(f"Saved: {OUTPUT_DIR}/validation_sun_planet.png")

# ============================================================================
# FIGURE 2: Planet-Ring Mesh (3 panels)
# ============================================================================
fig2, axes2 = plt.subplots(1, 3, figsize=(18, 6))

print("\n--- Planet-Ring Mesh ---")
for col, (z_suffix, z_label, z_val) in enumerate(z_levels):
    ax = axes2[col]

    p = planet[z_suffix]
    r = ring[z_suffix]

    ax.plot(r[:, 0], r[:, 1], 'b-', lw=2, label='Ring')
    ax.plot(p[:, 0], p[:, 1], 'g-', lw=2, label='Planet')

    # Zoom to planet-ring interface
    zoom_x = planet_ring_interface
    ax.set_xlim(zoom_x - 3, zoom_x + 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.set_title(f'Planet-Ring @ {z_label}', fontsize=14, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')

    # Measure alignment
    planet_pts = p[:, :2]
    ring_pts = r[:, :2]

    # Find planet outer point
    planet_outer_idx = np.argmax(planet_pts[:, 0])
    planet_outer_pt = planet_pts[planet_outer_idx]

    # Find nearest ring point
    dists = np.linalg.norm(ring_pts - planet_outer_pt, axis=1)
    ring_nearest_idx = np.argmin(dists)
    ring_nearest = ring_pts[ring_nearest_idx]

    # Angular offset
    planet_angle = np.degrees(np.arctan2(planet_outer_pt[1], planet_outer_pt[0]))
    ring_angle = np.degrees(np.arctan2(ring_nearest[1], ring_nearest[0]))
    offset = planet_angle - ring_angle
    clearance = np.linalg.norm(ring_nearest - planet_outer_pt)

    print(f"  {z_label}: offset = {offset:.4f}°, clearance = {clearance:.4f} mm")

fig2.suptitle('Planet-Ring Mesh Verification (with Ring Compensation)', fontsize=16, fontweight='bold')
plt.tight_layout()
fig2.savefig(os.path.join(OUTPUT_DIR, 'validation_planet_ring.png'), dpi=150)
print(f"Saved: {OUTPUT_DIR}/validation_planet_ring.png")

# ============================================================================
# FIGURE 3: Full Assembly Overview (3 panels)
# ============================================================================
fig3, axes3 = plt.subplots(1, 3, figsize=(18, 6))

print("\n--- Full Assembly ---")
for col, (z_suffix, z_label, z_val) in enumerate(z_levels):
    ax = axes3[col]

    s = sun[z_suffix]
    r = ring[z_suffix]

    # Plot sun
    ax.plot(s[:, 0], s[:, 1], 'r-', lw=1.5, label='Sun')

    # Plot all 3 planets
    for i in range(3):
        p = load(f"planet_12_{i}_{z_suffix}.txt")
        label = 'Planets' if i == 0 else None
        ax.plot(p[:, 0], p[:, 1], 'g-', lw=1.5, label=label)

    # Plot ring
    ax.plot(r[:, 0], r[:, 1], 'b-', lw=1.5, label='Ring')

    ax.set_xlim(-40, 40)
    ax.set_ylim(-40, 40)
    ax.set_aspect('equal')
    ax.set_title(f'Full Assembly @ {z_label}', fontsize=14, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')

fig3.suptitle('Full Planetary Assembly at Each Z-Level', fontsize=16, fontweight='bold')
plt.tight_layout()
fig3.savefig(os.path.join(OUTPUT_DIR, 'validation_full_assembly.png'), dpi=150)
print(f"Saved: {OUTPUT_DIR}/validation_full_assembly.png")

# ============================================================================
# FIGURE 4: Rules Verification - Detailed Mesh Points
# ============================================================================
fig4, axes4 = plt.subplots(2, 3, figsize=(18, 12))

print("\n--- Detailed Mesh Verification ---")
for col, (z_suffix, z_label, z_val) in enumerate(z_levels):
    s = sun[z_suffix]
    p = planet[z_suffix]
    r = ring[z_suffix]

    # Top row: Sun-Planet detail
    ax_sp = axes4[0, col]
    ax_sp.plot(s[:, 0], s[:, 1], 'r-', lw=2, label='Sun')
    ax_sp.plot(p[:, 0], p[:, 1], 'g-', lw=2, label='Planet')

    # Mark mesh contact region
    sun_outer_idx = np.argmax(s[:, :2][:, 0])
    ax_sp.plot(s[sun_outer_idx, 0], s[sun_outer_idx, 1], 'ro', markersize=8)

    ax_sp.set_xlim(sun_outer_r - 2, sun_outer_r + 2)
    ax_sp.set_ylim(-2, 2)
    ax_sp.set_aspect('equal')
    ax_sp.set_title(f'Sun-Planet Detail @ {z_label}')
    ax_sp.grid(True, alpha=0.3)
    if col == 0:
        ax_sp.legend()

    # Bottom row: Planet-Ring detail
    ax_pr = axes4[1, col]
    ax_pr.plot(r[:, 0], r[:, 1], 'b-', lw=2, label='Ring')
    ax_pr.plot(p[:, 0], p[:, 1], 'g-', lw=2, label='Planet')

    # Mark mesh contact region
    planet_outer_idx = np.argmax(p[:, :2][:, 0])
    ax_pr.plot(p[planet_outer_idx, 0], p[planet_outer_idx, 1], 'go', markersize=8)

    ax_pr.set_xlim(planet_ring_interface - 2, planet_ring_interface + 2)
    ax_pr.set_ylim(-2, 2)
    ax_pr.set_aspect('equal')
    ax_pr.set_title(f'Planet-Ring Detail @ {z_label}')
    ax_pr.grid(True, alpha=0.3)
    if col == 0:
        ax_pr.legend()

fig4.suptitle('Detailed Mesh Contact Verification', fontsize=16, fontweight='bold')
plt.tight_layout()
fig4.savefig(os.path.join(OUTPUT_DIR, 'validation_mesh_detail.png'), dpi=150)
print(f"Saved: {OUTPUT_DIR}/validation_mesh_detail.png")

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)
print(f"\nGenerated images in {OUTPUT_DIR}/:")
print("  - validation_sun_planet.png")
print("  - validation_planet_ring.png")
print("  - validation_full_assembly.png")
print("  - validation_mesh_detail.png")
