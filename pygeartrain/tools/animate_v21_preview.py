"""
Quick animation preview for v21 config: R30/P12/S6 with 4 planets
Validates gear mesh before generating STEP files.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pygeartrain.planetary import Planetary, PlanetaryGeometry
import imageio
import io
from PIL import Image
import os


def validate_planetary_config(R, P, S, N):
    """Validate planetary gear configuration. Raises ValueError if invalid."""
    errors = []

    # Rule 1: Mesh constraint
    if R != S + 2 * P:
        errors.append(f"MESH: R={R} != S + 2P = {S + 2*P}")

    # Rule 2: Assembly constraint
    if (R + S) % N != 0:
        errors.append(f"ASSEMBLY: (R+S)={R+S} not divisible by N={N}")

    if errors:
        raise ValueError(f"Invalid config: {'; '.join(errors)}")

    print(f"[OK] Config valid: R{R}/P{P}/S{S}, N={N}, Ratio={(R+S)/S:.1f}:1")


# v21 Configuration
R_teeth = 30
P_teeth = 12
S_teeth = 6
N_planets = 4
b_profile = 0.5

# Validate before proceeding
validate_planetary_config(R_teeth, P_teeth, S_teeth, N_planets)

KINEMATICS = Planetary('s', 'c', 'r')
OUTPUT_DIR = "design_log"

def create_animation_gif(n_frames=60, fps=20):
    """Create an animated GIF of the v21 gear configuration."""

    ratio = (R_teeth + S_teeth) / S_teeth
    label = f"v21_R{R_teeth}_P{P_teeth}_S{S_teeth}_N{N_planets}"

    # Create gear geometry
    gear = PlanetaryGeometry.create(KINEMATICS, (R_teeth, P_teeth, S_teeth), N_planets, b=b_profile)

    # Generate frames
    frames = []
    phases = np.linspace(0, 1, n_frames, endpoint=False)

    print(f"Generating {n_frames} frames for {label}...")
    print(f"Config: R={R_teeth}, P={P_teeth}, S={S_teeth}, N={N_planets}")
    print(f"Ratio: {ratio:.2f}:1")
    print(f"b-profile: {b_profile}")

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
            f"v21 Preview | {label}\n"
            f"S={S_teeth} P={P_teeth} R={R_teeth} | N={N_planets} | b={b_profile} | Ratio={ratio:.2f}:1\n"
            f"RING LOCKED | Sun(in)->Carrier(out)"
        )
        ax.set_title(title, fontsize=11, fontweight='bold')

        # Save to buffer
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
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"{OUTPUT_DIR}/{label}_animation.gif"
    imageio.mimsave(filename, frames, fps=fps, loop=0)

    print(f"\nSaved: {filename}")
    return filename


if __name__ == "__main__":
    print("=" * 60)
    print("v21 GEAR MESH PREVIEW")
    print("=" * 60)
    create_animation_gif(n_frames=60, fps=20)
    print("=" * 60)
