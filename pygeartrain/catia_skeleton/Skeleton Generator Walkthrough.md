# Planetary Skeleton Generator Walkthrough

> [!tip] Purpose
> Create wireframe reference geometry in 3DExperience CATIA for planetary gearbox design using skeleton-first modeling.

---

## What Gets Created

```
Skeleton (Geometrical Set)
├── POINT_ORIGIN
├── AXIS_SUN
├── CIRCLE_PITCH_SUN
├── CIRCLE_PITCH_RING
├── CIRCLE_OUTER_RING
├── CIRCLE_ORBIT
├── POINT_PLANET_1, _2, _3
├── AXIS_PLANET_1, _2, _3
└── CIRCLE_PITCH_PLANET_1, _2, _3
```

![[photos/skeleton-working-result.png]]

---

## Step 1: Edit Dimensions in Macro

Open `PlanetarySkeletonTrue.bas` and edit the dimensions section:

```vba
' === DIMENSIONS (edit these for your gearset) ===
Dim SunPD As Double: SunPD = 14       ' Sun pitch diameter
Dim PlanetPD As Double: PlanetPD = 28 ' Planet pitch diameter
Dim RingPD As Double: RingPD = 70     ' Ring pitch diameter
Dim RingOD As Double: RingOD = 80     ' Ring outer diameter
Dim OrbitR As Double: OrbitR = 21     ' Planet orbit radius
```

> [!note] Calculating Values
> - `PitchDiameter = Module × Teeth`
> - `OrbitRadius = (SunPD + PlanetPD) / 2`
> - Validate: `RingTeeth = SunTeeth + 2 × PlanetTeeth`
>
> **Example (Module 2.33, R30/P12/S6):**
> - Sun: 2.33 × 6 = 14mm
> - Planet: 2.33 × 12 = 28mm
> - Ring: 2.33 × 30 = 70mm
> - Orbit: (14 + 28) / 2 = 21mm

---

## Step 2: Open New Part in 3DExperience

1. Launch 3DExperience
2. **3D Part** → Create new part
3. Make sure part is in **edit mode** (double-click if needed)

---

## Step 3: Run the Macro

1. Press `Alt+F8` or search "**Macros**" in command search
2. In the Macros dialog, click **Select...**
3. Change file type to **"VB Script files (*.vbs;*.bas)"**
4. Browse to `PlanetarySkeletonTrue.bas`
5. Select `CATMain` from the list
6. Click **Run**

---

## Step 4: Create Solid Cylinders (Optional)

To visualize as solid bodies:

1. Press `Alt+F8` → Macros → Select → `SkeletonToCylinders.bas`
2. Run `CATMain`

This creates Bodies (Sun_Gear, Planet_1/2/3, Ring_Gear) by projecting and padding the skeleton circles.

![[photos/skeleton-with-cylinders.png]]

---

## Generated Geometry

The skeleton macro creates a **Geometrical Set** called "Skeleton" with:

| Element | Purpose |
|---------|---------|
| `POINT_ORIGIN` | Center reference |
| `AXIS_SUN` | Sun gear centerline |
| `AXIS_PLANET_1,2,3` | Planet gear centerlines |
| `CIRCLE_PITCH_SUN` | Sun pitch circle |
| `CIRCLE_PITCH_PLANET_1,2,3` | Planet pitch circles |
| `CIRCLE_PITCH_RING` | Ring internal pitch |
| `CIRCLE_OUTER_RING` | Ring OD / housing bore |
| `CIRCLE_ORBIT` | Planet center path |

---

## Next Steps

Once skeleton looks correct:

1. **Add actual gear profiles** - Use [[CATIA XYZ Import Progress]] to import tooth geometry
2. **Create gear parts** - Reference skeleton axes and circles
3. **Add top/bottom planes** - For extrusion limits (future enhancement)
4. **Link external parts** - Use publications for assembly references

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No active editor" | Make sure 3DExperience is open with a Part |
| "No active Part" | Double-click the part in the tree to enter edit mode |
| Geometry not visible | Check View → Hide/Show, or Fit All (Ctrl+Shift+F) |
| Wrong positions | Check OrbitR calculation matches your pitch diameters |

---

## Files

| File | Purpose |
|------|---------|
| `PlanetarySkeletonTrue.bas` | **Main macro** - edit dimensions here |
| `README.md` | Technical reference and API notes |
| `photos/` | Screenshots |

---

## Alternative: Bounding Cylinders

For quick throwaway visualization (solid cylinders instead of wireframe), use `PlanetarySkeletonGenerator.bas` with `parameters.txt`. Not recommended for real design work.
