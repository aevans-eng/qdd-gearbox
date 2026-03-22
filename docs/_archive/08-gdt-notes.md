# GD&T Notes — Critical Features

Geometric Dimensioning and Tolerancing decisions per ASME Y14.5-2018.
These apply to the QDD gearbox even though parts are FDM-printed — tolerancing
drives design intent and post-processing decisions.

## Datum Reference Frame

| Datum | Feature | Rationale |
|-------|---------|-----------|
| A | Housing bottom face | Primary mounting surface, establishes Z-plane |
| B | Main bearing bore (output side) | Establishes central axis |
| C | Motor mounting face | Orients rotational alignment |

## Critical Feature Tolerances

### 1. Bearing Bores

**Feature:** All bearing seats (housing bores for 6805, 6710, planet pin holes)

| Characteristic | Tolerance | Datum Ref | Notes |
|----------------|-----------|-----------|-------|
| Cylindricity | 0.05 mm | — | Bearing press-fit quality; FDM may need reaming |
| Position | ⌀ 0.1 mm | A, B | Planet bores relative to central axis |
| Size | H7 fit (+0.000/+0.025) | — | Slight interference for bearing retention |

**FDM consideration:** Print with undersized holes (~0.1 mm under), ream or sand to final size. Vertical orientation preferred for round bores.

### 2. Gear Mesh Alignment

**Feature:** Sun gear bore, planet gear bores, ring gear internal teeth

| Characteristic | Tolerance | Datum Ref | Notes |
|----------------|-----------|-----------|-------|
| Runout (total) | 0.08 mm | B | Sun and planet gears — controls mesh quality |
| Concentricity | ⌀ 0.05 mm | B | Ring gear ID to housing bore |
| Perpendicularity | 0.05 mm | A | Gear faces to housing base |

**FDM consideration:** Print gears flat (teeth up) for best tooth accuracy. Post-process with shaft reaming.

### 3. Housing Mating Surfaces

**Feature:** Housing-to-lid interface, motor mount face

| Characteristic | Tolerance | Datum Ref | Notes |
|----------------|-----------|-----------|-------|
| Flatness | 0.1 mm | — | Mating faces for seal/alignment |
| Parallelism | 0.1 mm | A | Lid face parallel to base |
| Position (bolt holes) | ⌀ 0.2 mm | A, B | M3 clearance holes |

**FDM consideration:** Print mating surfaces face-down on build plate for best flatness. Use raft if warping is an issue.

### 4. Planet Carrier

**Feature:** Carrier pin holes and output interface

| Characteristic | Tolerance | Datum Ref | Notes |
|----------------|-----------|-----------|-------|
| Position (pin holes) | ⌀ 0.08 mm | B | Equal spacing critical for load sharing |
| Runout | 0.05 mm | B | Output shaft interface |
| Perpendicularity | 0.05 mm | A | Pins must be normal to carrier plate |

## GD&T Symbols Reference (ASME Y14.5)

| Symbol | Name | Controls |
|--------|------|----------|
| ⌭ | Cylindricity | Form of cylindrical surface |
| ⊕ | Position | Location of feature |
| ↗ | Runout (circular) | Combined form and location relative to datum axis |
| ⟂ | Perpendicularity | Orientation to datum |
| ∥ | Parallelism | Orientation to datum |
| ⏥ | Flatness | Form of a planar surface |
| ◎ | Concentricity | Coaxiality of median points |

## FDM Achievable Tolerances (Typical)

| Characteristic | Typical FDM | Our Target | Strategy |
|----------------|-------------|------------|----------|
| Dimensional accuracy | ±0.2 mm | ±0.1 mm | Calibrated printer, test prints |
| Cylindricity | ~0.1 mm | 0.05 mm | Post-process (ream) |
| Flatness | ~0.1 mm on bed | 0.1 mm | Print face-down |
| Surface roughness | Ra 10-15 μm | Ra 5 μm on mesh | Sand/polish gear teeth |

## Notes

- All tolerances assume post-processing (reaming, sanding) on critical features
- Non-critical features: general tolerance ±0.3 mm
- Prototype first, measure, iterate — FDM tolerances are printer-dependent
- Document actual measured values after printing for design feedback loop
