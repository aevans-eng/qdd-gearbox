"""
Sweep b parameter (0.3-0.45) for each valid gearset with N>=3
Iteration: 2026-01-15_sun_sweep_5to1_v4

From v3, valid gearsets with N>=3:
- Gearset A: S=4, P=6, R=16, N=4 (exact 5:1)
- Gearset B: S=6, P=9, R=24, N=3 (exact 5:1)

Discarded (N=2 only):
- S=5, P=8, R=21
- S=7, P=10, R=27

OUTPUT:
- 2 panels, each with 4 images showing b sweep for one gearset
"""

import matplotlib.pyplot as plt
import numpy as np
from pygeartrain.planetary import Planetary, PlanetaryGeometry
from find_valid_gears import check_overlap
import os

KINEMATICS = Planetary('s', 'c', 'r')
ITERATION_ID = "2026-01-15_sun_sweep_5to1_v4"

# The 2 valid gearsets from v3 with N>=3
GEARSETS = [
    {"S": 4, "P": 6, "R": 16, "N": 4, "label": "Gearset A: S=4, P=6, R=16, N=4"},
    {"S": 6, "P": 9, "R": 24, "N": 3, "label": "Gearset B: S=6, P=9, R=24, N=3"},
]

# b values to sweep (0.3 to 0.45)
B_VALUES = [0.30, 0.35, 0.40, 0.45]


def archive_previous_iteration(design_log_dir="design_log"):
    """Archive previous v4 files if they exist."""
    import glob
    from datetime import datetime

    v4_files = glob.glob(f"{design_log_dir}/{ITERATION_ID}*")
    if v4_files:
        archive_dir = f"{design_log_dir}/v4_archived_{datetime.now().strftime('%H%M%S')}"
        os.makedirs(archive_dir, exist_ok=True)
        for f in v4_files:
            os.rename(f, f"{archive_dir}/{os.path.basename(f)}")
        print(f"Archived {len(v4_files)} previous v4 files to {archive_dir}/")


def generate_b_sweep_panel(gearset, b_values, output_dir="design_log"):
    """Generate a 2x2 panel showing b sweep for one gearset."""

    S, P, R, N = gearset["S"], gearset["P"], gearset["R"], gearset["N"]
    label = gearset["label"]
    ratio = (R + S) / S

    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    axes = axes.flatten()

    results = []

    for idx, b in enumerate(b_values):
        ax = axes[idx]

        # Validate
        validation = check_overlap(S, P, R, N, b, max_overlap_pct=1.0)

        # Create gear geometry
        gear = PlanetaryGeometry.create(KINEMATICS, (R, P, S), N, b=b)

        # Plot
        gear._plot(ax, phase=0, col='steelblue')

        ax.set_aspect('equal')
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.grid(True, alpha=0.3)

        # Title for each panel
        status = "VALID" if validation['valid'] else "INVALID"
        overlap = validation['sun_planet_overlap_pct']

        # Color code the title based on validity
        title_color = 'green' if validation['valid'] else 'red'
        title = f"b = {b:.2f}\n{status} ({overlap:.2f}% overlap)"
        ax.set_title(title, fontsize=12, fontweight='bold', color=title_color)

        results.append({
            'b': b,
            'valid': validation['valid'],
            'overlap': overlap,
        })

    # Main title for this panel
    fig.suptitle(
        f"{ITERATION_ID}\n"
        f"{label} | Ratio={ratio:.2f}:1\n"
        f"RING LOCKED | Sun(in)->Carrier(out) | b sweep: 0.30-0.45",
        fontsize=13, fontweight='bold', y=0.98
    )

    plt.tight_layout(rect=[0, 0, 1, 0.93])

    # Filename based on gearset
    filename = f"{output_dir}/{ITERATION_ID}_S{S}_P{P}_R{R}_N{N}_b_sweep.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Saved: {filename}")
    return filename, results


def main():
    print("=" * 70)
    print(f"Sun Gear Sweep v4 - b Parameter Sweep for Valid Gearsets")
    print(f"Iteration: {ITERATION_ID}")
    print("=" * 70)
    print()
    print("VALID GEARSETS FROM v3 (N>=3 only):")
    for gs in GEARSETS:
        print(f"  - {gs['label']}")
    print()
    print("DISCARDED (N=2 only):")
    print("  - S=5, P=8, R=21, N=2")
    print("  - S=7, P=10, R=27, N=2")
    print()
    print(f"b VALUES TO SWEEP: {B_VALUES}")
    print()
    print("LOCKED GEAR: RING")
    print("INPUT: SUN -> OUTPUT: CARRIER")
    print()

    # Archive any previous v4 files
    archive_previous_iteration()

    all_results = []

    for gearset in GEARSETS:
        print(f"\n--- {gearset['label']} ---")
        filename, results = generate_b_sweep_panel(gearset, B_VALUES)
        all_results.append({
            'gearset': gearset,
            'filename': filename,
            'results': results,
        })

    # Print summary
    print()
    print("=" * 70)
    print("SUMMARY - b SWEEP RESULTS")
    print("=" * 70)

    for ar in all_results:
        gs = ar['gearset']
        print(f"\n{gs['label']}:")
        print(f"  {'b':>6} {'Valid':>8} {'Overlap%':>10}")
        print(f"  {'-'*26}")
        for r in ar['results']:
            valid_str = "YES" if r['valid'] else "NO"
            print(f"  {r['b']:>6.2f} {valid_str:>8} {r['overlap']:>9.2f}%")


if __name__ == "__main__":
    main()
