"""
validate_v16_tolerance.py - Compare v15 (no offset) vs v16 (with profile offset)

Shows the effect of -0.05mm profile offset tolerance on gear mesh clearances.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

V15_DIR = "output_herringbone_v15"
V16_DIR = "output_herringbone_v16"

def load(directory, filename):
    return np.loadtxt(os.path.join(directory, filename))

# Geometry from the generation script
carrier_radius = 20.75
sun_outer_r = 8.76
planet_outer_r = 14.25
ring_inner_r = 32.74
planet_ring_interface = carrier_radius + planet_outer_r

print("=" * 60)
print("V15 vs V16 TOLERANCE COMPARISON")
print("V15: No profile offset")
print("V16: -0.05mm profile offset (tooth thinning)")
print("=" * 60)

z_levels = [('z_neg', 'z=-5mm'), ('z0', 'z=0mm'), ('z_pos', 'z=+5mm')]

# ============================================================================
# FIGURE 1: Sun-Planet Comparison (V15 vs V16)
# ============================================================================
fig1, axes1 = plt.subplots(2, 3, figsize=(18, 12))

print("\n--- Sun-Planet Mesh Clearance ---")
print(f"{'Z-level':<12} {'V15 (mm)':<12} {'V16 (mm)':<12} {'Difference':<12}")
print("-" * 48)

for col, (z_suffix, z_label) in enumerate(z_levels):
    # V15 (top row)
    sun_v15 = load(V15_DIR, f"sun_6_{z_suffix}.txt")
    planet_v15 = load(V15_DIR, f"planet_12_0_{z_suffix}.txt")

    ax_v15 = axes1[0, col]
    ax_v15.plot(sun_v15[:, 0], sun_v15[:, 1], 'r-', lw=2, label='Sun')
    ax_v15.plot(planet_v15[:, 0], planet_v15[:, 1], 'g-', lw=2, label='Planet')
    ax_v15.set_xlim(sun_outer_r - 3, sun_outer_r + 3)
    ax_v15.set_ylim(-3, 3)
    ax_v15.set_aspect('equal')
    ax_v15.set_title(f'V15 (no offset) @ {z_label}', fontsize=12, fontweight='bold')
    ax_v15.grid(True, alpha=0.3)
    if col == 0:
        ax_v15.legend()
        ax_v15.set_ylabel('Y (mm)')

    # V16 (bottom row)
    sun_v16 = load(V16_DIR, f"sun_6_{z_suffix}.txt")
    planet_v16 = load(V16_DIR, f"planet_12_0_{z_suffix}.txt")

    ax_v16 = axes1[1, col]
    ax_v16.plot(sun_v16[:, 0], sun_v16[:, 1], 'r-', lw=2, label='Sun')
    ax_v16.plot(planet_v16[:, 0], planet_v16[:, 1], 'g-', lw=2, label='Planet')
    ax_v16.set_xlim(sun_outer_r - 3, sun_outer_r + 3)
    ax_v16.set_ylim(-3, 3)
    ax_v16.set_aspect('equal')
    ax_v16.set_title(f'V16 (-0.05mm offset) @ {z_label}', fontsize=12, fontweight='bold')
    ax_v16.set_xlabel('X (mm)')
    ax_v16.grid(True, alpha=0.3)
    if col == 0:
        ax_v16.legend()
        ax_v16.set_ylabel('Y (mm)')

    # Measure clearances
    sun_outer_idx_v15 = np.argmax(sun_v15[:, 0])
    sun_outer_pt_v15 = sun_v15[sun_outer_idx_v15, :2]
    dists_v15 = np.linalg.norm(planet_v15[:, :2] - sun_outer_pt_v15, axis=1)
    clearance_v15 = np.min(dists_v15)

    sun_outer_idx_v16 = np.argmax(sun_v16[:, 0])
    sun_outer_pt_v16 = sun_v16[sun_outer_idx_v16, :2]
    dists_v16 = np.linalg.norm(planet_v16[:, :2] - sun_outer_pt_v16, axis=1)
    clearance_v16 = np.min(dists_v16)

    diff = clearance_v16 - clearance_v15
    print(f"{z_label:<12} {clearance_v15:<12.4f} {clearance_v16:<12.4f} {diff:+.4f}")

fig1.suptitle('Sun-Planet Mesh: V15 vs V16 Tolerance Comparison', fontsize=16, fontweight='bold')
plt.tight_layout()
fig1.savefig(os.path.join(V16_DIR, 'comparison_sun_planet.png'), dpi=150)
print(f"\nSaved: {V16_DIR}/comparison_sun_planet.png")

# ============================================================================
# FIGURE 2: Planet-Ring Comparison (V15 vs V16)
# ============================================================================
fig2, axes2 = plt.subplots(2, 3, figsize=(18, 12))

print("\n--- Planet-Ring Mesh Clearance ---")
print(f"{'Z-level':<12} {'V15 (mm)':<12} {'V16 (mm)':<12} {'Difference':<12}")
print("-" * 48)

# V15 uses ring with 0.2° offset
ring_offset_str = "0p20"

for col, (z_suffix, z_label) in enumerate(z_levels):
    # V15 (top row)
    planet_v15 = load(V15_DIR, f"planet_12_0_{z_suffix}.txt")
    ring_v15 = load(V15_DIR, f"ring_30_offset{ring_offset_str}_{z_suffix}.txt")

    ax_v15 = axes2[0, col]
    ax_v15.plot(ring_v15[:, 0], ring_v15[:, 1], 'b-', lw=2, label='Ring')
    ax_v15.plot(planet_v15[:, 0], planet_v15[:, 1], 'g-', lw=2, label='Planet')
    ax_v15.set_xlim(planet_ring_interface - 3, planet_ring_interface + 3)
    ax_v15.set_ylim(-3, 3)
    ax_v15.set_aspect('equal')
    ax_v15.set_title(f'V15 (no offset) @ {z_label}', fontsize=12, fontweight='bold')
    ax_v15.grid(True, alpha=0.3)
    if col == 0:
        ax_v15.legend()
        ax_v15.set_ylabel('Y (mm)')

    # V16 (bottom row) - ring files have fixed name (0.2° baked in)
    planet_v16 = load(V16_DIR, f"planet_12_0_{z_suffix}.txt")
    ring_v16 = load(V16_DIR, f"ring_30_{z_suffix}.txt")

    ax_v16 = axes2[1, col]
    ax_v16.plot(ring_v16[:, 0], ring_v16[:, 1], 'b-', lw=2, label='Ring')
    ax_v16.plot(planet_v16[:, 0], planet_v16[:, 1], 'g-', lw=2, label='Planet')
    ax_v16.set_xlim(planet_ring_interface - 3, planet_ring_interface + 3)
    ax_v16.set_ylim(-3, 3)
    ax_v16.set_aspect('equal')
    ax_v16.set_title(f'V16 (-0.05mm offset) @ {z_label}', fontsize=12, fontweight='bold')
    ax_v16.set_xlabel('X (mm)')
    ax_v16.grid(True, alpha=0.3)
    if col == 0:
        ax_v16.legend()
        ax_v16.set_ylabel('Y (mm)')

    # Measure clearances
    planet_outer_idx_v15 = np.argmax(planet_v15[:, 0])
    planet_outer_pt_v15 = planet_v15[planet_outer_idx_v15, :2]
    dists_v15 = np.linalg.norm(ring_v15[:, :2] - planet_outer_pt_v15, axis=1)
    clearance_v15 = np.min(dists_v15)

    planet_outer_idx_v16 = np.argmax(planet_v16[:, 0])
    planet_outer_pt_v16 = planet_v16[planet_outer_idx_v16, :2]
    dists_v16 = np.linalg.norm(ring_v16[:, :2] - planet_outer_pt_v16, axis=1)
    clearance_v16 = np.min(dists_v16)

    diff = clearance_v16 - clearance_v15
    print(f"{z_label:<12} {clearance_v15:<12.4f} {clearance_v16:<12.4f} {diff:+.4f}")

fig2.suptitle('Planet-Ring Mesh: V15 vs V16 Tolerance Comparison', fontsize=16, fontweight='bold')
plt.tight_layout()
fig2.savefig(os.path.join(V16_DIR, 'comparison_planet_ring.png'), dpi=150)
print(f"Saved: {V16_DIR}/comparison_planet_ring.png")

# ============================================================================
# FIGURE 3: Full Assembly V16
# ============================================================================
fig3, axes3 = plt.subplots(1, 3, figsize=(18, 6))

print("\n--- Full Assembly V16 ---")
for col, (z_suffix, z_label) in enumerate(z_levels):
    ax = axes3[col]

    sun = load(V16_DIR, f"sun_6_{z_suffix}.txt")
    ring = load(V16_DIR, f"ring_30_{z_suffix}.txt")

    ax.plot(sun[:, 0], sun[:, 1], 'r-', lw=1.5, label='Sun')

    for i in range(3):
        planet = load(V16_DIR, f"planet_12_{i}_{z_suffix}.txt")
        label = 'Planets' if i == 0 else None
        ax.plot(planet[:, 0], planet[:, 1], 'g-', lw=1.5, label=label)

    ax.plot(ring[:, 0], ring[:, 1], 'b-', lw=1.5, label='Ring')

    ax.set_xlim(-40, 40)
    ax.set_ylim(-40, 40)
    ax.set_aspect('equal')
    ax.set_title(f'V16 Assembly @ {z_label}', fontsize=14, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')

fig3.suptitle('V16 Full Planetary Assembly (with -0.05mm Profile Offset)', fontsize=16, fontweight='bold')
plt.tight_layout()
fig3.savefig(os.path.join(V16_DIR, 'assembly_v16.png'), dpi=150)
print(f"Saved: {V16_DIR}/assembly_v16.png")

print("\n" + "=" * 60)
print("TOLERANCE VALIDATION COMPLETE")
print("=" * 60)
print(f"\nExpected clearance increase: ~0.10mm (2 × 0.05mm offset)")
print("(Both mating gears are thinned, so total gap = 2× offset)")
