# GD&T Annotations — QDD Gearbox

This file supplements `docs/08-gdt-notes.md` with specific callout notes
that would appear on engineering drawings. Use these when creating formal
drawings in CATIA or as inspection criteria for printed parts.

## Drawing Callout Reference

### DWG-001: Housing (Bottom)

```
Feature: Main bearing bore (6710-2RS seat)
  |-- Diameter: 50.00 +0.025/+0.000 (H7 fit)
  |-- Cylindricity: 0.05
  |-- Position: dia 0.10 | A | B |
  |-- Surface finish: Ra 3.2 (post-process: ream)

Feature: Motor pilot bore
  |-- Diameter: per motor spec +0.05/-0.00
  |-- Concentricity: dia 0.08 | B |
  |-- Perpendicularity to A: 0.05

Feature: M3 mounting holes (x6)
  |-- Position: dia 0.20 | A | B | C |
  |-- Through hole: 3.2 +0.1/-0.0
```

### DWG-002: Housing Lid

```
Feature: Output bearing bore (6805-2RS seat)
  |-- Diameter: 25.00 +0.025/+0.000 (H7 fit)
  |-- Cylindricity: 0.05
  |-- Position: dia 0.10 | A | B |

Feature: Mating face
  |-- Flatness: 0.10
  |-- Parallelism to Datum A: 0.10

Feature: M3 bolt holes (x6)
  |-- Position: dia 0.20 | A | B |
  |-- Counterbore: 5.5 dia x 3.0 deep
```

### DWG-003: Planet Carrier

```
Feature: Planet pin holes (x3)
  |-- Diameter: 5.00 +0.025/+0.000
  |-- Position: dia 0.08 | B | (120 deg spacing)
  |-- Perpendicularity to carrier face: 0.05

Feature: Output shaft interface
  |-- Runout (total): 0.05 | B |
  |-- Concentricity: dia 0.05 | B |
```

### DWG-004: Sun Gear

```
Feature: Shaft bore
  |-- Diameter: per motor shaft +0.02/+0.00 (light press)
  |-- Concentricity to pitch circle: dia 0.05

Feature: Tooth form
  |-- Total runout: 0.08 | bore axis |
  |-- Profile per involute spec (module, teeth, PA)
```

### DWG-005: Planet Gear (x3)

```
Feature: Pin bore
  |-- Diameter: per bearing ID -0.00/-0.01
  |-- Cylindricity: 0.03

Feature: Tooth form
  |-- Total runout: 0.08 | bore axis |
```

### DWG-006: Ring Gear (Internal)

```
Feature: Internal teeth
  |-- Concentricity to housing bore: dia 0.05 | B |
  |-- Runout: 0.10 | B |

Feature: Outer diameter (press-fit to housing)
  |-- Diameter: housing bore -0.05/-0.10 (interference)
  |-- Cylindricity: 0.05
```

## Notes

- All dimensions in mm unless noted
- General tolerance: +/- 0.3 mm (FDM printing)
- Critical features (marked above) require post-processing
- Datum A = housing bottom face, B = main bearing bore axis, C = motor mount face
