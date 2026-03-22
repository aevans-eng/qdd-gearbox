# Cycloidal Gear Parameter Reference

How to think about cycloidal planetary gear dimensions when coming from an involute background.
Applies to this project: R48/P18/S12, pygeartrain, herringbone, scaled to 75mm ring ID.

---

## Involute vs Cycloidal — Parameter Comparison

| Parameter | Involute | Cycloidal |
|-----------|----------|-----------|
| **Module** | $m$ — sets tooth scale, $d = m \times N$ | **N/A — delete this parameter.** Tooth scale is set by specifying ring diameter + tooth counts. Do not set to zero (breaks formulas). |
| **Pitch diameter** | Clean definition: $d = m \times N$, the reference circle where teeth mesh | No clean equivalent. Use **outer diameter (tip circle)** as the functional reference for skeleton checks. Carrier radius = `(ring_pitch_diam - planet_outer_diam) / 2` — planet tips are tangent to ring tooth roots which sit at the pitch reference. |
| **Tooth depth** | $2.25m$ (standard full depth) | Falls out of rolling circle geometry. Cannot be calculated from a simple formula — **measure from STEP in CATIA.** |
| **What sets the scale** | Module | Target ring inner diameter + tooth counts (R, P, S) |
| **What you specify** | $m$, $N$, pressure angle | $R$, $P$, $S$, ring diameter, face width |

---

## This Project's Dimensions (Run 001 STEP files)

From `generate_step_aaron.py` output and `catia/step-integration.md`:

| Part | Dimension | Value | What it is |
|------|-----------|-------|------------|
| Sun | Outer diameter | 19.9mm | Tip circle — largest solid extent |
| Planet | Outer diameter | 29.1mm | Tip circle — largest solid extent |
| Planet | Center-to-axis distance | 23.0mm | Carrier radius — where planet center sits |
| Ring | Inner reference diameter | 75.0mm | Pitch reference / engagement zone |
| Ring | Outer diameter | 95.0mm | OD — fits in housing bore (95.3mm, 0.3mm clearance) |
| Ring | Nominal wall | 10.0mm | From 75mm ID reference to 95mm OD — **includes tooth depth** |
| Ring | Solid wall (root to OD) | **Measure in CATIA** | Less than 10mm — see below |
| All gears | Face width | 18.6mm | Axial thickness |

---

## The Ring Gear Wall Problem

`RING_WALL_MM = 10mm` in the script is measured from the **pitch reference radius (37.5mm) to the outer cylinder (47.5mm).**

The tooth roots cut *outward* from the pitch reference, eating into that 10mm. The actual solid wall between the deepest tooth root and the OD is less than 10mm.

**To get the real solid wall:**
1. Import `gearbox_CAD.step` into CATIA
2. Section view through the ring gear (section on the gear midplane)
3. Pick a tooth root face (the outermost point of the internal tooth profile)
4. Measure radial distance from that face to the OD cylinder
5. Record that number — it's the minimum solid wall for fastener and structural design

**Why this matters for the skeleton:**
- Fastener holes through the ring wall must stay radially outside the tooth root circle
- The skeleton parameter `ring_wall_thickness = 10mm` is the nominal design wall, not the solid wall
- Don't position fastener hole centers using 10mm as the solid material — wait for the STEP measurement

---

## Skeleton Parameter Updates (Old Involute → New Cycloidal)

Changes to make in SKEL_Gearbox before importing STEP:

| Skeleton Param | Action | New Value | Priority |
|---------------|--------|-----------|----------|
| `planet_mid_path` | Update | **23.0mm** | Critical — drives bearing pocket placement |
| `planet_pitch_diam` → rename to `planet_outer_diam` | Update | **29.1mm** | Important — drives clearance checks |
| `sun_pitch_diam` → rename to `sun_outer_diam` | Update | **19.9mm** | Minor — 0.1mm change |
| `gear_module` | **Delete** | N/A | Do not set to zero |
| `ring_pitch_diam` | No change | 75mm | Already correct |
| `gear_height` | No change | 18.6mm | Already correct |
| `ring_wall_thickness` | No change (for now) | 10mm | Verify actual solid wall after STEP import |
| `housing_ring_gear_bore` | No change | 95.3mm | Already correct |

---

## Notes

- For pygeartrain cycloidal gears, "pitch diameter" and "outer diameter" are not the same thing, but outer diameter is the useful number for physical fit checks in CATIA.
- The gear ratio is still $\frac{R + S}{S} = \frac{48 + 12}{12} = 5:1$ — same math as involute.
- Tooth counts R/P/S fully define the geometry proportions; ring diameter sets the scale.
