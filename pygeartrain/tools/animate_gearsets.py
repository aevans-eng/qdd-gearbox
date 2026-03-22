"""
Animate the two valid gearsets from v4
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from pygeartrain.planetary import Planetary, PlanetaryGeometry
import imageio
import io
from PIL import Image

KINEMATICS = Planetary('s', 'c', 'r')
ITERATION_ID = "2026-01-15_sun_sweep_5to1_v4"

# The 2 valid gearsets with b=0.35 (middle of optimal range)
GEARSETS = [
    {"S": 4, "P": 6, "R": 16, "N": 4, "b": 0.35, "label": "Gearset_A_S4_N4"},
    {"S": 6, "P": 9, "R": 24, "N": 3, "b": 0.35, "label": "Gearset_B_S6_N3"},
]


def create_animation_gif(gearset, output_dir="design_log", n_frames=60, fps=20):
    """Create an animated GIF of the gear rotation."""

    S, P, R, N, b = gearset["S"], gearset["P"], gearset["R"], gearset["N"], gearset["b"]
    label = gearset["label"]
    ratio = (R + S) / S

    # Create gear geometry
    gear = PlanetaryGeometry.create(KINEMATICS, (R, P, S), N, b=b)

    # Generate frames
    frames = []
    phases = np.linspace(0, 1, n_frames, endpoint=False)

    print(f"Generating {n_frames} frames for {label}...")

    for i, phase in enumerate(phases):
        fig, ax = plt.subplots(1, 1, figsize=(8, 8), dpi=100)

        # Plot gear at this phase
        gear._plot(ax, phase=phase, col='steelblue')

        ax.set_aspect('equal')
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.grid(True, alpha=0.3)

        # Title
        title = (
            f"{ITERATION_ID} | {label}\n"
            f"S={S} P={P} R={R} | N={N} | b={b} | Ratio={ratio:.2f}:1\n"
            f"RING LOCKED | Sun(in)->Carrier(out)"
        )
        ax.set_title(title, fontsize=11, fontweight='bold')

        # Save to buffer and read as image
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        image = Image.open(buf)
        frames.append(np.array(image))
        buf.close()

        plt.close(fig)

        if (i + 1) % 10 == 0:
            print(f"  Frame {i + 1}/{n_frames}")

    # Save as GIF
    filename = f"{output_dir}/{ITERATION_ID}_{label}_animation.gif"
    imageio.mimsave(filename, frames, fps=fps, loop=0)

    print(f"Saved: {filename}")
    return filename


def main():
    print("=" * 70)
    print(f"Animating Gearsets from v4")
    print(f"Iteration: {ITERATION_ID}")
    print("=" * 70)
    print()

    for gearset in GEARSETS:
        print(f"\n--- Animating {gearset['label']} ---")
        create_animation_gif(gearset, n_frames=60, fps=20)

    print("\n" + "=" * 70)
    print("ANIMATIONS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
