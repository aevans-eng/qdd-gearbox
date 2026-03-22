# QDD Test Bench Design

**Status:** Brainstorming
**Started:** 2026-03-12

## What This Is

A portable, modular test bench that holds the QDD actuator for all testing. Clamps to any table, keeps everything secured, nothing loose.

## Requirements

- Table-mountable with C-clamps
- Reversible 180° — output shaft can point off table edge (lever arm, hanging loads) OR inward (onto a scale on the table surface)
- Withstands 16 Nm peak reaction torque without slipping or tipping
- Modular — bolt-on everything, easy to swap actuator, replace broken parts
- Mounts all electronics (driver, brake resistor, PSU, controller) — nothing loose
- Buildable from 2x4 lumber + 3D printed brackets
- Light enough to move around

## Actuator Constraints

| Parameter | Value |
|-----------|-------|
| Housing OD | 109 mm |
| Axial length | ~88 mm (housing + lid, before motor) — **measure actual with calipers** |
| Peak output torque | 16 Nm |
| Tangential reaction force at housing surface | ~290 N |
| Sandwich bolts | 4x M5, accessible from outside — potential anti-rotation index |
| Weight | < 2 kg |

## General Setup

- **Actuator axis horizontal**, parallel to table surface
- **Motor on the inboard end**, output shaft on the outboard end
- **Two 2x4 rails** running the length, connected by cross members — simple rectangular frame
- **3D-printed split clamps** (saddle + cap) wrap the housing, bolt to the rails
- **Electronics zone** behind the actuator on the bench — driver, brake resistor, PSU all have printed standoffs/brackets screwed to the rails

## Key Considerations

**Anti-rotation:** Friction clamps alone probably won't hold 16 Nm. Need a positive index — slots in the printed saddle that capture the M5 sandwich bolt heads, or a pin/key feature on the housing.

**Anti-tipping:** Cantilevered output shaft + lever arm creates a tipping moment. The C-clamp nearest the table edge handles this, but the base rails need to extend well back for leverage. Think about worst-case moment arm.

**Reversibility:** Clamps are symmetric so actuator can face either way. Electronics stay fixed — they don't need to move when you flip the actuator.

**Motor housing adapter:** Current motor housing may not have great flat surfaces for mounting. May need a printed collar/adapter with bolt flanges. Evaluate once you have the prototype in hand.

**Brake resistor thermal:** Gets hot under load. Mount on standoffs for airflow, not flat against wood. Keep away from PLA brackets.

**Cable management:** Printed clips screwed to the rails. Route wires along the frame, not dangling.

**Output shaft clearance:** When cantilevered off the table, need enough room below for lever arms, hanging weights, load cell fixtures. Plan for at least 200-300mm clear below shaft centerline.

## Open Questions

1. What's the full electronics list? (ODrive? which one? PSU specs? encoder interface?)
2. Motor + actuator total axial length with motor attached — drives clamp spacing
3. What output shaft tooling do you need? (lever arm, brake disc, coupling?)
4. One clamp pair or two? One might be enough if it's wide and indexes well
5. Plywood base vs. 2x4 frame? Frame is lighter and more modular, plywood is stiffer

## BOM (Draft)

| Item | Qty | Notes |
|------|-----|-------|
| 2x4 lumber (~500mm) | 2-4 | Base rails + cross members |
| Wood screws | ~12 | Frame assembly |
| C-clamps (3-4") | 2-4 | Table mounting |
| 3D printed: clamp saddle | 1-2 | PETG preferred (stiffer than PLA) |
| 3D printed: clamp cap | 1-2 | Matches saddle |
| 3D printed: electronics brackets | 3-5 | Per-component |
| 3D printed: cable clips | 4-6 | Screw-mount to rails |
| M4 bolts + nuts | ~8 | Clamp assembly |
| M3 bolts + nuts | ~8 | Electronics mounting |

## Next Steps

- [ ] Measure motor + actuator total axial length
- [ ] Sketch the bench (pen and paper / CAD)
- [ ] Cut 2x4 rails, dry-fit frame
- [ ] Design clamp in CAD (109mm bore, split, with anti-rotation index)
- [ ] Print clamp, test fit
- [ ] Identify full electronics list
