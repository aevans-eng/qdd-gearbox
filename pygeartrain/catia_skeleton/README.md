# CATIA Planetary Gearbox Skeleton Generator

Creates reference geometry for planetary gearbox design in 3DExperience CATIA.

## Status: WORKING

![[photos/skeleton-working-result.png]]
*Wireframe skeleton*

![[photos/skeleton-with-cylinders.png]]
*Solid cylinders generated from skeleton*

## Workflow

| Version | File | Purpose | Status |
|---------|------|---------|--------|
| **Bounding Cylinders** | `PlanetarySkeletonGenerator.bas` | Quick visualization with solids | Untested |
| **True Skeleton** | `PlanetarySkeletonTrue.bas` | Wireframe for skeleton-first design | **WORKING** |

**Recommendation:** Use True Skeleton for any real design work.

## Key Learnings (2026-01-31)

### 3DExperience VBA Differences

1. **Get active part:** Use `CATIA.ActiveEditor.ActiveObject` (NOT `CATIA.ActiveDocument`)

2. **Create circles:** `AddNewCircleCtrRad` requires 4 arguments:
   ```vba
   ' WRONG (3 args - fails silently)
   hsFactory.AddNewCircleCtrRad(center, plane, radius)

   ' CORRECT (4 args - geodesic boolean required)
   hsFactory.AddNewCircleCtrRad(center, plane, False, radius)
   ```

3. **Create axes:** `AddNewLinePtDir` works with 5 args:
   ```vba
   hsFactory.AddNewLinePtDir(point, direction, startLength, endLength, False)
   ```

4. **Direction from plane:** Get Z-direction by passing XY plane to `AddNewDirection`:
   ```vba
   Set dirZ = hsFactory.AddNewDirection(part.OriginElements.PlaneXY)
   ```

## Files

| File | Purpose |
|------|---------|
| `PlanetarySkeletonTrue.bas` | Step 1: Creates wireframe skeleton |
| `SkeletonToCylinders.bas` | Step 2: Pads circles into solid cylinders |
| `PlanetarySkeletonGenerator.bas` | Alt: Bounding cylinders (untested) |
| `Skeleton Generator Walkthrough.md` | Detailed usage guide |
| `photos/` | Screenshots |

## Quick Start

1. Open a new **3D Part** in 3DExperience
2. Make sure part is in edit mode (double-click if needed)
3. Press `Alt+F8` → Macros → Select → `PlanetarySkeletonTrue.bas` → Run
4. Run again with `SkeletonToCylinders.bas` to create solid bodies

### Generated Geometry

```
Skeleton (Geometrical Set)
├── POINT_ORIGIN
├── AXIS_SUN
├── CIRCLE_PITCH_SUN (r=7mm)
├── CIRCLE_PITCH_RING (r=35mm)
├── CIRCLE_OUTER_RING (r=40mm)
├── CIRCLE_ORBIT (r=21mm)
├── POINT_PLANET_1, _2, _3
├── AXIS_PLANET_1, _2, _3
└── CIRCLE_PITCH_PLANET_1, _2, _3 (r=14mm)
```

### Customizing Dimensions

Edit these variables at the top of the macro:
```vba
Dim SunPD As Double: SunPD = 14       ' Sun pitch diameter
Dim PlanetPD As Double: PlanetPD = 28 ' Planet pitch diameter
Dim RingPD As Double: RingPD = 70     ' Ring pitch diameter
Dim RingOD As Double: RingOD = 80     ' Ring outer diameter
Dim OrbitR As Double: OrbitR = 21     ' = (SunPD + PlanetPD) / 2
```

## Planetary Gear Validation

For proper mesh: `RingTeeth = SunTeeth + 2 × PlanetTeeth`

Example (HackathonActuator): 30 = 6 + 2×12 ✓

## Roadmap

### Next: Additional Components
- [ ] Carrier disc with planet bores
- [ ] Carrier pins (cylinder at each planet axis)
- [ ] Bearing cylinders (ID/OD representation)
- [ ] Input/output shaft cylinders

### Future: Parametric Enhancements
- [ ] CATIA parameters (edit in tree instead of macro)
- [ ] Formulas for derived dimensions
- [ ] Publications for external linking
- [ ] Top/bottom planes for extrusion limits

## Related

- [[CATIA XYZ Import Progress]] - Import actual gear tooth profiles
- [[HackathonActuator]] - Gearbox this was developed for
