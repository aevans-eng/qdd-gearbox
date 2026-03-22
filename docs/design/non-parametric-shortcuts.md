# Non-Parametric Shortcuts — Prototype Debt

Things hardcoded or done in haste for the prototype that will break if design parameters change. Fix these before any serious design iteration.

---

## Gear Cutting Bodies — Hardcoded to 3 Planets

The `cutting/adding bodies` part has 3 separate cutting body entities, one per planet. CATIA can't (as far as we know) apply one cutting body to multiple target entities, so the count is manually matched to `number_of_planets = 3`.

**Breaks if:** planet count changes (e.g. 4 planets → need a 4th cutting body manually added).

**Proper fix:** Investigate if CircPattern or body-level patterning can drive cutting bodies from `number_of_planets`. If not, at minimum document the manual step clearly so it's not forgotten during a redesign.

---

## Housing Base Fasteners — Fixed Counts

Some housing base fastener holes are set to fixed numbers rather than driven by a parameter or pattern.

**Breaks if:** fastener layout changes (different bolt count or pattern).

**Proper fix:** Drive from skeleton parameter + circular/rectangular pattern.

---

## Motor Housing Fasteners — Not Parametric

From `motor-fastener-specs.md`: "currently, the fastener holes for body to motor and motor housing are NOT parametric."

**Breaks if:** motor changes, lid thickness changes, or fastener spec changes.

---

*Add more shortcuts here as you notice them. Review before any major design change.*
