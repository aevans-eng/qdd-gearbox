# Importing Gear Profiles into 3DEXPERIENCE

## Overview

This guide explains how to import the XYZ point curves and build 3D gear geometry in 3DEXPERIENCE (SOLIDWORKS Connected or CATIA).

## Exported Files

Each gearset folder contains:

| File | Description |
|------|-------------|
| `ring_z0.txt`, `ring_z_top.txt`, `ring_z_bot.txt` | Ring gear profile at Z=0, +5mm, -5mm |
| `planet_z0.txt`, `planet_z_top.txt`, `planet_z_bot.txt` | Planet gear profile (import once, pattern for others) |
| `sun_z0.txt`, `sun_z_top.txt`, `sun_z_bot.txt` | Sun gear profile at three Z levels |
| `carrier_path.txt` | Circle showing where planet centers are located |
| `planet_centers.txt` | XYZ coordinates of each planet center |
| `gearset_info.txt` | Parameters and dimensions reference |

## File Format

Each `.txt` file contains space-delimited XYZ coordinates:
```
x1 y1 z1
x2 y2 z2
...
```
Units are **millimeters**.

---

## Method 1: SOLIDWORKS Connected (3DEXPERIENCE)

### Step 1: Import Curve from XYZ Points

1. **Open a new Part**
2. Go to **Insert → Curve → Curve Through XYZ Points**
3. Click **Browse** and select a `.txt` file (e.g., `sun_z0.txt`)
4. Click **OK** to create the curve

### Step 2: Create the Gear Profile (Spur Gear - Simple Extrude)

For a simple spur gear (no helix):

1. Import only the `_z0.txt` file for each gear
2. **Insert → Boss/Base → Extruded Boss/Base**
3. Select the imported curve as the profile
4. Set extrusion depth to **10mm** (or your gear thickness)
5. Use **Mid Plane** direction to center the gear

### Step 3: Create Helical/Herringbone Gears (Loft Method)

For twisted teeth:

1. Import all three curves: `_z_bot.txt`, `_z0.txt`, `_z_top.txt`
2. **Insert → Boss/Base → Loft**
3. Select the three curves as loft profiles (in order: bot → z0 → top)
4. Ensure **Closed Contour** is checked
5. Click **OK** to create the lofted solid

### Step 4: Pattern the Planet Gears

1. Create ONE planet gear using the steps above
2. **Insert → Pattern/Mirror → Circular Pattern**
3. Set axis to the Z-axis (through origin)
4. Set number of instances:
   - Gearset A: **4 planets**
   - Gearset B: **3 planets**
5. Set spacing to **360° / N** (90° for 4 planets, 120° for 3 planets)

### Step 5: Create Assembly

1. Create a new Assembly
2. Insert each gear as a component
3. Use **Concentric** and **Coincident** mates to position:
   - Sun gear: centered at origin
   - Ring gear: centered at origin (concentric with sun)
   - Planet gears: centered on `carrier_path` circle

---

## Method 2: CATIA (3DEXPERIENCE)

### Step 1: Import Points

1. Open **Part Design** workbench
2. Go to **Insert → Wireframe → Spline**
3. Use **Import** option to load `.txt` file
4. Or use **Digitized Shape Editor** → **Import** → **Cloud of Points**

### Step 2: Create Curve from Points

1. In **Generative Shape Design**:
2. **Insert → Curves → Spline** through imported points
3. Ensure curve is closed (connect last point to first)

### Step 3: Create Solid

**For Spur Gears:**
1. Use **Pad** feature with the Z=0 curve
2. Set length to gear thickness

**For Helical Gears:**
1. Import all three Z-level curves
2. Use **Multi-Sections Solid** (loft)
3. Select curves as sections

### Step 4: Pattern Planets

1. Use **Circular Pattern**
2. Reference the Z-axis
3. Set instance count (3 or 4)

---

## Gearset Specifications

### Gearset A (S=4, P=6, R=16, N=4)

| Parameter | Value |
|-----------|-------|
| Sun teeth | 4 |
| Planet teeth | 6 |
| Ring teeth | 16 |
| Number of planets | 4 |
| Gear ratio | 5.00:1 |
| Ring outer diameter | 70 mm |
| Gear thickness | 10 mm |
| Carrier path radius | ~21 mm |

### Gearset B (S=6, P=9, R=24, N=3)

| Parameter | Value |
|-----------|-------|
| Sun teeth | 6 |
| Planet teeth | 9 |
| Ring teeth | 24 |
| Number of planets | 3 |
| Gear ratio | 5.00:1 |
| Ring outer diameter | 70 mm |
| Gear thickness | 10 mm |
| Carrier path radius | ~21 mm |

---

## Configuration

**Locked Gear:** RING (stationary, attached to housing)
**Input:** SUN (motor shaft)
**Output:** CARRIER (output shaft, planets rotate around it)

---

## Tips

1. **Start with the Sun gear** - it's the simplest profile
2. **Check units** - files are in millimeters
3. **Verify closure** - curves should be closed loops
4. **Use reference geometry** - create a center axis and planes first
5. **Save often** - especially before loft operations

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Curve not closed | Manually close by adding a line from last to first point |
| Loft fails | Ensure curves are in correct Z-order and have similar point counts |
| Import fails | Check file path has no special characters |
| Profile looks wrong | Verify scale - should be ~70mm diameter for ring |

---

## File Locations

```
cad_export/
├── Gearset_A_S4_P6_R16_N4/
│   ├── ring_z0.txt, ring_z_top.txt, ring_z_bot.txt
│   ├── planet_z0.txt, planet_z_top.txt, planet_z_bot.txt
│   ├── sun_z0.txt, sun_z_top.txt, sun_z_bot.txt
│   ├── carrier_path.txt
│   ├── planet_centers.txt
│   └── gearset_info.txt
│
├── Gearset_B_S6_P9_R24_N3/
│   └── (same structure)
│
└── 3DEXPERIENCE_IMPORT_INSTRUCTIONS.md (this file)
```
