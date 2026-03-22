# Rev 00B — Design Changes

Consolidation of all known issues from Rev 00A. Organized by part so changes can be worked through in CATIA one part at a time.

---

## Carrier — Top

### Enlarge output shaft + larger top bearing ✅
**Source:** T-001, U-07 | **Priority:** Must-have
**Problem:** Current shaft clearly undersized.
**Solution:** Enlarged output shaft and larger top bearing — both changed parametrically in CATIA.
**Notes:**

### Fix planet bearing shoulder print quality ✅
**Source:** T-003, T-005, U-04 | **Priority:** Must-have
**Problem:** Print orientation trade-off — output shaft up gives good top bearing surface but bad planet shoulders. T-005 confirmed shoulders are sensitive to bolt torque (narrow window between carrier play and planet binding).
**Chosen approach:** Changed print strategy — top carrier no longer has walls, only bottom carrier has walls. Improves print viability for top carrier (no overhangs on shoulder surfaces).
**Notes:** No parametric/geometry change to the shoulder dimensions themselves — this is a print orientation fix.

### ~~Carrier halves indexing feature~~ — DEPRIORITIZED
**Source:** U-05, T-004 | **Priority:** Optional
**Reason:** Load path analysis shows no operational force drives clocking. ~0.5 mm play exists but is not loaded. Indexing only useful for assembly repeatability, not structural.
**Notes:**

---

## Carrier — Bottom

### Planet bearing shoulders ✅
**Source:** T-003, T-005, U-04 | **Priority:** Must-have
**Solution:** Bottom carrier now has all the walls (top carrier walls removed). No geometry change needed — bottom shoulders looked OK in visual inspection.
**Notes:**

### Adjust planet bearing clearances — NO CHANGE
**Source:** Assembly observation | **Priority:** Should-have
**Notes:** Not changing for Rev 00B.

### ~~Carrier halves indexing feature~~ — DEPRIORITIZED
(See Carrier — Top)

---

## Carrier — General (both halves)

### Thread into plastic (no heat inserts) ✅
**Source:** T-001 | **Priority:** Must-have
**Problem:** Heat inserts not worth it for prototype iteration. Self-tap holes already validated with coupon (M3: 2.6mm, M4: 3.6mm, M5: 4.6mm).
**Solution:** Top carrier M5 output shaft holes changed to 4.2mm. Bottom carrier M3 thread holes changed from 2.6mm to 2.4mm.
**Notes:**

---

## Lid

### Redesign lid constraint — decouple ring gear clamping from carrier constraint
**Source:** T-002, U-03 | **Priority:** Must-have
**Problem:** Lid double-constrains ring gear + carrier top. Tolerance stackup through carrier assembly causes drag.
**Options:**
- (a) Add axial clearance between lid bearing and carrier top shaft
	- added extra axial clearance on carrier top shaft
- (b) Deepen lid bearing recess
- (c) Space lid out further from ring gear
**Chosen approach:** (a) Added extra axial clearance on carrier top shaft.
**Notes:**

### Lid-to-body indexing
**Source:** Prototype notes | **Priority:** Should-have
**Problem:** Lid currently only constrained against twist by clamping friction — needs positive indexing feature.
**Solution:**
**CATIA params changed:**
**Notes:** Ignoring for now. not a concern

---

## Housing Body

### Main bearing shaft fit slightly tighter
**Source:** Post-REV00A notes | **Priority:** Should-have
**Problem:** Currently loose transition fit, should be slightly tighter.
**Solution:**
**CATIA params changed:**
**Notes:** ignoring for now

---

## Motor Housing

### Bottom shaft cutout — investigate misalignment or enlarge
**Source:** Prototype notes | **Priority:** Should-have
**Problem:** Shaft rubs opposite end when mounted. Root cause unclear — could be misalignment or just undersized cutout.
**Solution:**
**Notes:** Ignoring for now

---

## Gears (Sun, Planets, Ring)

### Switch from herringbone to spur gears (0° helix)
**Source:** T-001 observation | **Priority:** Must-have
**Problem:** Herringbone helix is very slight, not providing meaningful benefit at this scale. Over-constrains the mesh and creates an assembly error mode (wrong alignment) that's hard to detect. At least one planet was misaligned in Rev 00A.
**Solution:** Reprint all gears with 0° helix angle.
**pygeartrain params changed:**
**Notes:**

### Add text features for gear top/bottom identification
**Source:** Prototype notes | **Priority:** Nice-to-have
**Problem:** Currently unclear which way gears install. Less critical with spur gears (no helix alignment), but still useful for assembly.
**Solution:**
**Notes:**

### Sun gear fit — possibly slightly looser
**Source:** Post-REV00A notes | **Priority:** Should-have
**Problem:** Currently tight enough to need pressing on table (10.075mm was tried for Rev 00A-B).
**Solution:**
**CATIA params changed:**
**Notes:**

---

## Encoder Housing

### Wire cutout + base 0.5mm thinner
**Source:** Prototype notes | **Priority:** Should-have
**Problem:** No wire routing, base too thick.
**Solution:**
**CATIA params changed:**
**Notes:**

---

## Skeleton (global)

### Clearance parameter naming — clarify higher = tighter or looser
**Source:** Prototype notes | **Priority:** Nice-to-have
**Problem:** Currently confusing which direction offset values go.
**Solution:**
**Notes:**

---

## Pending Investigation

- **Carrier shoulder deformation** — need quantitative measurement (T-003), not just visual. Current visual says bottom OK, top has print quality issues.
- **3D printer dimensional bias on sun-planet clearance** — hypothesis that printer growing ODs squeezes sun-planet gap (both grow into same space) while ring-planet self-compensates. Backlash observed with sun installed suggests tolerances may be OK, but worth measuring to confirm.

## Design Decisions Still Needed

- Which approach for lid constraint fix?
- Which approach for top carrier shoulders?
- Metal spacers vs redesigned geometry — trade-off between part count and print quality
