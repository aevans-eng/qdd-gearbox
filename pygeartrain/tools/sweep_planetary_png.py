import matplotlib
# MUST be called before importing pyplot
matplotlib.use('Agg') 

import matplotlib.pyplot as plt
import numpy as np
import os
from pygeartrain.planetary import Planetary, PlanetaryGeometry

# --- Fixed Parameters ---
R_teeth = 30
P_teeth = 12
S_teeth = 6
N_planets = 3

# --- Sweep Parameters ---
b_start = 0.01
b_end = 1.0
b_step = 0.05
b_values = np.arange(b_start, b_end + b_step, b_step)

# --- Directory Setup (png_sweeps/Subfolder) ---
base_folder = "png_sweeps"
sub_folder = f"R{R_teeth}_P{P_teeth}_S{S_teeth}_N{N_planets}"
target_path = os.path.join(base_folder, sub_folder)

if not os.path.exists(target_path):
    os.makedirs(target_path)

# --- Kinematics Setup ---
kinematics = Planetary('s', 'c', 'r')
G = (R_teeth, P_teeth, S_teeth)

print(f"Starting background sweep into: {target_path}")

for b in b_values:
    b_rounded = round(b, 3)
    
    # 1. Create the Gear Geometry
    gear = PlanetaryGeometry.create(
        kinematics=kinematics,
        G=G,
        N=N_planets,
        b=b_rounded
    )
    
    # 2. Setup Figure (Hidden)
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)
    
    # 3. Plot to axis
    gear.plot(ax=ax)
    
    ax.set_aspect('equal')
    ax.axis('off') 
    ax.set_title(f"R:{R_teeth} P:{P_teeth} S:{S_teeth} N:{N_planets} | b:{b_rounded:.2f}")

    # 4. Save
    file_name = f"R{R_teeth}_P{P_teeth}_S{S_teeth}_N{N_planets}_b{b_rounded:.2f}.png"
    save_full_path = os.path.join(target_path, file_name)
    
    fig.savefig(save_full_path, dpi=100, bbox_inches='tight')
    
    # 5. Clean up
    plt.close(fig)
    print(f"Saved {file_name}")

print(f"\nDone! All {len(b_values)} images are in {target_path}")