"""
validate_v2.py - Validation for herringbone v2 (Sun + Ring Compensation)

Compares v2 (dual compensation) against original (ring-only compensation)
to show the improvement in sun-planet mesh alignment.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# Geometry constants
carrier_radius = 20.75
sun_outer_r = 8.76
planet_outer_r = 14.25
ring_inner_r = 32.74

sun_planet_interface = sun_outer_r
planet_ring_interface = carrier_radius + planet_outer_r

def load(output_dir, f):
    return np.loadtxt(os.path.join(output_dir, f))

def measure_clearance(pts1, pts2, interface_x):
    """Measure clearance at interface."""
    # Find point closest to interface on positive x axis
    idx1 = np.argmax(pts1[:, 0])
    pt1 = pts1[idx1, :2]

    # Find nearest point on other gear
    dists = np.linalg.norm(pts2[:, :2] - pt1, axis=1)
    idx2 = np.argmin(dists)
    pt2 = pts2[idx2, :2]

    clearance = np.linalg.norm(pt2 - pt1)
    return clearance, pt1, pt2

def measure_angular_offset(pts1, pts2):
    """Measure angular offset between closest points."""
    idx1 = np.argmax(pts1[:, 0])
    pt1 = pts1[idx1, :2]

    dists = np.linalg.norm(pts2[:, :2] - pt1, axis=1)
    idx2 = np.argmin(dists)
    pt2 = pts2[idx2, :2]

    angle1 = np.degrees(np.arctan2(pt1[1], pt1[0]))
    angle2 = np.degrees(np.arctan2(pt2[1], pt2[0]))

    return angle1 - angle2

print("=" * 70)
print("HERRINGBONE v2 VALIDATION (Sun + Ring Compensation)")
print("=" * 70)

z_levels = [('z_neg', 'z=-5mm', -5), ('z0', 'z=0mm', 0), ('z_pos', 'z=+5mm', 5)]

# Load v2 data
v2_dir = "output_herringbone_v2"
sun_v2 = {}
planet_v2 = {}
ring_v2 = {}

for z_suffix, z_label, z_val in z_levels:
    sun_v2[z_suffix] = load(v2_dir, f"sun_6_{z_suffix}.txt")
    planet_v2[z_suffix] = load(v2_dir, f"planet_12_0_{z_suffix}.txt")
    ring_v2[z_suffix] = load(v2_dir, f"ring_30_{z_suffix}.txt")

# Load original data for comparison
orig_dir = "output_herringbone_final"
sun_orig = {}
planet_orig = {}
ring_orig = {}

if os.path.exists(orig_dir):
    for z_suffix, z_label, z_val in z_levels:
        sun_orig[z_suffix] = load(orig_dir, f"sun_6_{z_suffix}.txt")
        planet_orig[z_suffix] = load(orig_dir, f"planet_12_0_{z_suffix}.txt")
        ring_orig[z_suffix] = load(orig_dir, f"ring_30_{z_suffix}.txt")
    has_orig = True
else:
    has_orig = False

# ============================================================================
# FIGURE 1: Sun-Planet Comparison (v2 vs Original)
# ============================================================================
fig1, axes1 = plt.subplots(2, 3, figsize=(18, 12))

print("\n--- Sun-Planet Mesh (v2 with Sun Compensation) ---")
for col, (z_suffix, z_label, z_val) in enumerate(z_levels):
    # Top row: v2
    ax = axes1[0, col]
    s = sun_v2[z_suffix]
    p = planet_v2[z_suffix]

    ax.plot(s[:, 0], s[:, 1], 'r-', lw=2, label='Sun (v2)')
    ax.plot(p[:, 0], p[:, 1], 'g-', lw=2, label='Planet')

    ax.set_xlim(sun_outer_r - 3, sun_outer_r + 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.set_title(f'v2 Sun-Planet @ {z_label}', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')

    clearance, _, _ = measure_clearance(s, p, sun_outer_r)
    print(f"  v2 {z_label}: clearance = {clearance:.4f} mm")

    # Bottom row: Original (if available)
    ax2 = axes1[1, col]
    if has_orig:
        s_o = sun_orig[z_suffix]
        p_o = planet_orig[z_suffix]

        ax2.plot(s_o[:, 0], s_o[:, 1], 'r-', lw=2, label='Sun (orig)')
        ax2.plot(p_o[:, 0], p_o[:, 1], 'g-', lw=2, label='Planet')

        clearance_o, _, _ = measure_clearance(s_o, p_o, sun_outer_r)
        print(f"  orig {z_label}: clearance = {clearance_o:.4f} mm")

        ax2.set_xlim(sun_outer_r - 3, sun_outer_r + 3)
        ax2.set_ylim(-3, 3)
        ax2.set_aspect('equal')
        ax2.set_title(f'Original Sun-Planet @ {z_label}', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='upper right')
    else:
        ax2.text(0.5, 0.5, 'Original not available', ha='center', va='center', transform=ax2.transAxes)

fig1.suptitle('Sun-Planet Mesh: v2 (Sun Compensation) vs Original', fontsize=16, fontweight='bold')
plt.tight_layout()
fig1.savefig(os.path.join(v2_dir, 'validate_sun_planet_comparison.png'), dpi=150)
print(f"Saved: {v2_dir}/validate_sun_planet_comparison.png")

# ============================================================================
# FIGURE 2: Planet-Ring (v2)
# ============================================================================
fig2, axes2 = plt.subplots(1, 3, figsize=(18, 6))

print("\n--- Planet-Ring Mesh (v2) ---")
for col, (z_suffix, z_label, z_val) in enumerate(z_levels):
    ax = axes2[col]
    p = planet_v2[z_suffix]
    r = ring_v2[z_suffix]

    ax.plot(r[:, 0], r[:, 1], 'b-', lw=2, label='Ring')
    ax.plot(p[:, 0], p[:, 1], 'g-', lw=2, label='Planet')

    ax.set_xlim(planet_ring_interface - 3, planet_ring_interface + 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.set_title(f'Planet-Ring @ {z_label}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')

    offset = measure_angular_offset(p, r)
    clearance, _, _ = measure_clearance(p, r, planet_ring_interface)
    print(f"  {z_label}: angular offset = {offset:.4f}°, clearance = {clearance:.4f} mm")

fig2.suptitle('Planet-Ring Mesh (v2 with Ring Compensation)', fontsize=16, fontweight='bold')
plt.tight_layout()
fig2.savefig(os.path.join(v2_dir, 'validate_planet_ring.png'), dpi=150)
print(f"Saved: {v2_dir}/validate_planet_ring.png")

# ============================================================================
# FIGURE 3: Full Assembly (v2)
# ============================================================================
fig3, axes3 = plt.subplots(1, 3, figsize=(18, 6))

print("\n--- Full Assembly (v2) ---")
for col, (z_suffix, z_label, z_val) in enumerate(z_levels):
    ax = axes3[col]

    s = sun_v2[z_suffix]
    r = ring_v2[z_suffix]

    ax.plot(s[:, 0], s[:, 1], 'r-', lw=1.5, label='Sun')

    for i in range(3):
        p = load(v2_dir, f"planet_12_{i}_{z_suffix}.txt")
        label = 'Planets' if i == 0 else None
        ax.plot(p[:, 0], p[:, 1], 'g-', lw=1.5, label=label)

    ax.plot(r[:, 0], r[:, 1], 'b-', lw=1.5, label='Ring')

    ax.set_xlim(-40, 40)
    ax.set_ylim(-40, 40)
    ax.set_aspect('equal')
    ax.set_title(f'Full Assembly @ {z_label}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')

fig3.suptitle('v2 Full Planetary Assembly (Sun + Ring Compensation)', fontsize=16, fontweight='bold')
plt.tight_layout()
fig3.savefig(os.path.join(v2_dir, 'validate_full_assembly.png'), dpi=150)
print(f"Saved: {v2_dir}/validate_full_assembly.png")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 70)
print("v2 VALIDATION COMPLETE")
print("=" * 70)
print(f"\nCompensation applied:")
print(f"  Sun: +3.44° (tracks planet inner point)")
print(f"  Ring: +0.21° (accounts for planet center offset)")
print(f"\nGenerated images in {v2_dir}/:")
print("  - validate_sun_planet_comparison.png")
print("  - validate_planet_ring.png")
print("  - validate_full_assembly.png")
