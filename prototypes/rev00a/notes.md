## Initial Fitment Notes

### Housing Body
- Main bearing fitment hair too loose. Currently a tight clearance fit but should be closer to a loose transition fit.
	- Addressed in REV00A
- M3 clearance holes to motor housing measure at 2.87mm — too tight. Need another 0.1mm clearance.
	- Addressed in REV00A
- M4 clearance holes to motor — good.

### Carrier Top
- Bearing fitment currently a tightish clearance fit — should be a loose transition fit.
	- Addressed in REV00A
- Need to analyze why housing body and carrier top were chosen as clearance fits? Presumably for assembly. Perhaps in future carrier should be clearance as it is less material to reprint?
	- Adjusted in REV00A
- Tree supports are difficult to remove.
	- Will be reprinted

### Lid
- Top bearing to lid fitment good, loose-medium transition fit.
- Lid-body indexing ring/ring gear spacer could be a little tighter — 0.49 + 0.18 difference in max-min play.
	- Addressed in REV00A

### Planets
- Bearing fit slightly loose. Most are a loose-medium transition fit but one was a clearance fit (tolerancing issue).
- Total height with bearings installed: 18.78mm

### Motor Housing
- Bottom hole cutout for shaft may need to be enlarged. When mounting the gearbox to motor/motor-housing, the shaft becomes no longer square to the motor housing making the opposite end shaft rub. Root cause of misalignment should be investigated, or if minimal performance impact the hole could simply be made bigger.

### General
- Need to make it clear what each clearance parameter does in the skeleton — confusing to remember if higher value = tighter or looser.

---

## REV00A Reprint/Change Notes

- [x] Sun gear reprinted with slightly looser clearances and fillets around hole edges so it can fit onto motor shaft easier
- [x] Replacing heatserts with simple plastic self-tapped threads:
	- [x] Bottom carrier shell and perhaps upper carrier shell reprinted to remove heatsert features (upper has no heatsert but OD needs to be slightly larger)
	- [x] Slightly enlarge output shaft diam
	- [x] Slightly loosen bottom carrier bore diam
	- [x] Housing body reprinted to have transition fit on main bearing shaft (slightly larger)
- [ ] Printing tool to remove sun gear from motor shaft (not needed likely)
- [x] Coupon self-tapping hole test
	- M3: 2.6mm
	- M4: 3.6mm
	- M5: 4.6mm
- Skeleton changes:
	- carrier_shaft_offset: 0.1 → 0.12
	- carrier_bearing_bore_offset: 0.1 → 0.12
	- main_bearing_shaft_offset: 0.1 → 0.12
	- lid_step_clearance: 0.25 -> 0.18

---

## Post REV00A Notes

- What was reprinted:
	- Bottom carrier shell
	- Housing body
- Sun gear still quite tight, but able to be installed by pressing down on table. Maybe should be a hair looser?
	- Changing from diam 10.05mm to 10.075mm, leaving flat face distance from center same. ill call this REV00A-B for completeness. Going to be printed for the REV00A assembly. 
- Self-tapping hole sizes work well.
- Tree support branch distance: 5 -> 4
- REV00A lower carrier half 
	- noticed slight print quality issue on bearing shoulder. Tree support setting inadequate causing some delamination of the shoulder, which can cause concentricity issues with the bearing without a some extra post processing care. Tree supports can be removed easily.  
- REV00A gearbox Housing body 
	- main bearing shaft has a loose transistion fit. Feels decent but should be slightly tighter in a future revision.
	- gearbox housing body to motor housing m3 clearance holes fit good now.\
- Need to add text features that make it clear which parts of the gears are top/bottom.
- When lid is tight on, there is additional drag, likely something is over constrained? Perhaps lid is putting pressure on carrier?
- Lid should likely index with gearbox body, currently rings and lid are only contrained to resist twist through the clamping of the lid, but the lid cant be torqued too much or there is resistance. Need to do some revision here
- Carrier planet bearing shoulders likely to be deformed easily. not much confidence in them. Especially when torquing the carrier bolts. likely resulting in some drag? Shoulders may need to be taller. Or a washer may be needed.
- Encoder housing needs cutout for wire, base should be 0.5mm thinner. 
- Carrier halves should likely index together — prevents possible planet axial misalignment.
- Carrier bearing shoulders prone to deformation during torquing due to low surface area (high pressure on shoulder face).
- Gear tooth tolerances may be fine individually, but planet positioning relative to sun/ring could cause poor meshing. Need to think about whether the issue is gear geometry or assembly positioning (bearing fits, carrier bore locations, etc.).

Side notes:
- Need to start brainstorming testing methods, procedures, plan.
- Need to learn how to properly interface with the motor and control it and integrating the fundamentals.
