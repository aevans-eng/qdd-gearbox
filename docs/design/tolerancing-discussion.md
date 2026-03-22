# Tolerancing Discussion — Questions for Aaron

Fill in answers below each question. Short answers are fine. Sketches/screenshots welcome if easier.

---

## Assembly Understanding

**Q1: Housing body shape**
Is the housing a cylinder/tube shape, or more of a cup (closed bottom, open top)? Does the motor mount to the bottom of the housing?

**A1:** So the gearbox assembly right now just will sit on top of the motor and the shaft goes through the housing, um, into kind of connects to the sun gear. here. I don't really understand the intent of the question, so I don't know how to answer it well, but it's basically like just a body with a lid kind of thing. I don't know.

**Q2: Lid attachment**
Does the lid sit on top of the housing body? Is there a step/rabbet (like a lip) where the lid registers into the housing, or does it just sit flat on top and the bolts locate it?

**A2:** Yeah, there is like a step. The step basically goes down and sits on top of the ring gears to kind of put pressure on them.

**Q3: Ring gear to housing interface**
You said the housing locates the ring gears concentrically (slide fit). Is there a cylindrical bore in the housing where the ring gear OD slides into? And the ring gears just drop in from the top before the lid goes on?

**A3:**  Yeah, the housing has like a cylindrical bore where the ring gears kind of slide into.

**Q4: Ring gear split plane**
The two ring gear halves — are they split at mid-height (each half has half the gear teeth), or is it a full-height gear + a spacer/adapter ring?

**A4:** Yeah, it just split in half at the middle.

**Q5: Carrier clamshell assembly**
The two carrier halves are held together by shoulder screws that pass through the planet bearings. So the shoulder screw acts as both the planet pin AND the carrier fastener? Is the shoulder of the screw what the bearing inner race sits on?

**A5:** Yes. It acts as the fastener and the pin.

**Q6: Carrier to main bearing interface**
How does the carrier connect to the main bearings (6805-2RS)? Is there a cylindrical boss on each carrier half that sits inside the bearing ID (25mm)? Or does one carrier half have the full shaft that passes through both bearings?

**A6:** So right now, the bottom of the housing has like a lip for the inner diameter of the bearing to kind of sit on. And it's constrained consensually by the bottom housing body. and then the outer diameter of the bearing sits on another kind of shoulder of the bottom of the carrier it's kind of like if we're installing it first you put the the bottom main bearing you put it onto the body and then from there the top of the carrier or the bottom half of the carrier you just push down onto the bearing and there's a there's a lip there that catches it if that makes sense

**Q7: Motor shaft to sun gear**
How is the sun gear attached to the motor shaft? Press fit? Set screw? D-shaft? Key? What's the motor shaft diameter?

**A7:** So right now we just have a press fit. The motor shaft is just like a circle with a flat part in it, so I think we're just going to do press fit for now for the prototype.

---

## Specific Interfaces

**Q8: What prevents the main bearings from moving axially?**
Are there shoulders/snap rings/retaining features in the housing bores that keep the bearings seated? Or are they just pressed in and friction holds them?

**A8:** So the whole assembly is kind of constrained actually by the lid. So what prevents the whole assembly from moving down, so the ring gears are sitting on the body of the housing and then the carrier is kind of sitting on that bottom main bearing which is sitting up on the the housing body, the lip, the bottom one, if that makes sense. And then what prevents it from moving up is the lid has its own bearing and lip that goes on to another lip of the top part of the carrier. I can add an image if it helps, but I don't know how good your image recognition is.

**Q9: Planet axial play**
After the carrier is assembled with shoulder screws through the planet bearings — what controls how much axial play the planets have? Is there a gap between the carrier shoulders and the bearing faces? Is this gap currently defined by a parameter?

**A9:** So, the planets are herringbone so they should be self-centering but they are floating.

**Q10: Are there any seals or O-rings?**
(Probably not for a prototype, but just confirming)

**A10:** No, there is not. This is not going to be a fluid bath design or anything. It's just going to be something like grease, some kind of grease in there. Silicone grease or something but no seals.

---

## Parameters & CATIA

**Q11: Key dimension parameters**
List (or paste) the parameter names and values for these critical dims. If you can't export, just type the key ones:
- Main bearing bore diameter (housing)
- Main bearing ID (carrier shaft OD)
- Planet bearing bore (in planet gear)
- Planet bearing pin diameter (carrier)
- Ring gear OD (fits into housing)
- Ring gear housing bore ID
- Sun gear bore ID
- Motor shaft OD
- Any clearance parameters you've already defined

**A11:** Root: Skeleton A.1

=== Skeleton A.1 ===
  PARAM: Skeleton A.1\PartBody\datum_point (offset from motor)\X = 0mm
  PARAM: Skeleton A.1\PartBody\datum_point (offset from motor)\Y = 0mm
  PARAM: Skeleton A.1\PartBody\datum_point (offset from motor)\Z = 0mm
  PARAM: Skeleton A.1\PartBody\Housing_inside_base\Offset = 5mm
  PARAM: Skeleton A.1\PartBody\Gear_midplane\Offset = 22.45mm
  PARAM: Skeleton A.1\PartBody\top_motor_shaft_plane\Offset = 30mm
  PARAM: Skeleton A.1\PartBody\planet_bearings\Radius.1\Radius = 10mm
  PARAM: Skeleton A.1\PartBody\planet_bearings\Radius.1\Diameter = 20mm
  PARAM: Skeleton A.1\PartBody\planet_bearings\Radius.8\Radius = 2.5mm
  PARAM: Skeleton A.1\PartBody\planet_bearings\Radius.8\Diameter = 5mm
  PARAM: Skeleton A.1\PartBody\planet_bearings\Radius.9\Radius = 7mm
  PARAM: Skeleton A.1\PartBody\planet_bearings\Radius.9\Diameter = 14mm
  PARAM: Skeleton A.1\PartBody\planet_bearings\Length.15\Length = 13.75mm
  PARAM: Skeleton A.1\PartBody\point_abs_datum\X = 0mm
  PARAM: Skeleton A.1\PartBody\point_abs_datum\Y = 0mm
  PARAM: Skeleton A.1\PartBody\point_abs_datum\Z = 0mm
  PARAM: Skeleton A.1\PartBody\PUB_z_axis\X = 0
  PARAM: Skeleton A.1\PartBody\PUB_z_axis\Y = 0
  PARAM: Skeleton A.1\PartBody\PUB_z_axis\Z = 1
  PARAM: Skeleton A.1\PartBody\PUB_z_axis\Start = 0mm
  PARAM: Skeleton A.1\PartBody\PUB_z_axis\End = 150mm
  PARAM: Skeleton A.1\PartBody\Gears\Radius.1\Radius = 37.5mm
  PARAM: Skeleton A.1\PartBody\Gears\Radius.1\Diameter = 75mm
  PARAM: Skeleton A.1\PartBody\Gears\Radius.2\Radius = 10mm
  PARAM: Skeleton A.1\PartBody\Gears\Radius.2\Diameter = 20mm
  PARAM: Skeleton A.1\PartBody\Gears\Radius.9\Radius = 13.75mm
  PARAM: Skeleton A.1\PartBody\Gears\Radius.9\Diameter = 27.5mm
  PARAM: Skeleton A.1\PartBody\Gears\Radius.11\Radius = 2.5mm
  PARAM: Skeleton A.1\PartBody\Gears\Radius.11\Diameter = 5mm
  PARAM: Skeleton A.1\PartBody\Gears\Radius.12\Radius = 7mm
  PARAM: Skeleton A.1\PartBody\Gears\Radius.12\Diameter = 14mm
  PARAM: Skeleton A.1\PartBody\main_bearing\Radius.1\Radius = 12.5mm
  PARAM: Skeleton A.1\PartBody\main_bearing\Radius.1\Diameter = 25mm
  PARAM: Skeleton A.1\PartBody\main_bearing\Radius.2\Radius = 18.5mm
  PARAM: Skeleton A.1\PartBody\main_bearing\Radius.2\Diameter = 37mm
  PARAM: Skeleton A.1\PartBody\main_bearing\Radius.3\Radius = 10mm
  PARAM: Skeleton A.1\PartBody\main_bearing\Radius.3\Diameter = 20mm
  PARAM: Skeleton A.1\PartBody\Carrier\Radius.3\Radius = 35mm
  PARAM: Skeleton A.1\PartBody\Carrier\Radius.3\Diameter = 70mm
  PARAM: Skeleton A.1\PartBody\Carrier\Radius.5\Radius = 23.75mm
  PARAM: Skeleton A.1\PartBody\Carrier\Radius.5\Diameter = 47.5mm
  PARAM: Skeleton A.1\PartBody\carrier_bottom\Offset = 1.5mm
  PARAM: Skeleton A.1\PartBody\carrier_top\Offset = 14mm
  PARAM: Skeleton A.1\PartBody\carrier_min_thickness_top\Offset = 2mm
  PARAM: Skeleton A.1\PartBody\carrier_min_thickness_bottom\Offset = 8.95mm
  PARAM: Skeleton A.1\PartBody\Point.2\H = 0mm
  PARAM: Skeleton A.1\PartBody\Point.2\V = 0mm
  PARAM: Skeleton A.1\PartBody\Point.2\X = 1
  PARAM: Skeleton A.1\PartBody\Point.2\Y = -3.622271632e-071
  PARAM: Skeleton A.1\PartBody\Point.2\Z = -1.504632769e-036
  PARAM: Skeleton A.1\PartBody\gear_top\Offset = 10mm
  PARAM: Skeleton A.1\PartBody\housing_body_top\Offset = 66.35mm
  PARAM: Skeleton A.1\PartBody\Point.5\Length = 23.75mm
  PARAM: Skeleton A.1\PartBody\planet_center_datum_axis\Start = 0mm
  PARAM: Skeleton A.1\PartBody\planet_center_datum_axis\End = 150mm
  PARAM: Skeleton A.1\PartBody\housing_base_mounting_layout\Length.18\Length = 44mm
  PARAM: Skeleton A.1\PartBody\housing_base_mounting_layout\Length.19\Length = 76mm
  PARAM: Skeleton A.1\PartBody\housing_base_mounting_layout\Length.20\Length = 46mm
  PARAM: Skeleton A.1\PartBody\housing_base_mounting_layout\Radius.39\Radius = 2mm
  PARAM: Skeleton A.1\PartBody\housing_base_mounting_layout\Radius.39\Diameter = 4mm
  PARAM: Skeleton A.1\PartBody\housing_base_mounting_layout\Radius.43\Radius = 1.5mm
  PARAM: Skeleton A.1\PartBody\housing_base_mounting_layout\Radius.43\Diameter = 3mm
  PARAM: Skeleton A.1\PartBody\gearbox_assembly_sandwich_fastener_distn\Radius.3\Radius = 42.5mm
  PARAM: Skeleton A.1\PartBody\gearbox_assembly_sandwich_fastener_distn\Radius.3\Diameter = 85mm
  PARAM: Skeleton A.1\PartBody\gearbox_assembly_sandwich_fastener_distn\Radius.6\Radius = 2.5mm
  PARAM: Skeleton A.1\PartBody\gearbox_assembly_sandwich_fastener_distn\Radius.6\Diameter = 5mm
  PARAM: Housing_base_thickness = 5mm
  PARAM: Housing_min_wall_thickness = 7mm
  PARAM: Main_bearing_ID = 25mm
  PARAM: Main_bearing_OD = 37mm
  PARAM: Main_bearing_height = 6.95mm
  PARAM: sun_pitch_diam = 20mm
  PARAM: planet_pitch_diam = 27.5mm
  PARAM: ring_pitch_diam = 75mm
  PARAM: carrier_bearing_ID = 5mm
  PARAM: carrier_bearing_OD = 14mm
  PARAM: carrier_bearing_h = 5mm
  PARAM: number_of_planets = 3
  PARAM: main_bearing_base_clearance = 1.5mm
  PARAM: carrier_plate_bottom_h = 10.95mm
  PARAM: gear_height = 20mm
  PARAM: ring_wall_thickness = 10mm
  PARAM: carrier_ring_clearance = 5mm
  PARAM: carrier_plate_thickness = 4mm
  PARAM: planet_mid_path = 23.75mm
  PARAM: planet_spacing = 120deg
  PARAM: carrier_planet_clearance = 2mm
  PARAM: carrier_diam = 70mm
  PARAM: housing_width = 109mm
  PARAM: housing_body_total_height = 66.35mm
  PARAM: carrier_lid_clearance = 2mm
  PARAM: motor_shaft_clearance_hole = 18mm
  PARAM: main_bearing_shoulder_ID = 27.4mm
  PARAM: housing_lid_thickness = 15.95mm
  PARAM: main_bearing_shoulder_OD = 34.5mm
  PARAM: carrier_output_OD = 25mm
  PARAM: carrier_output_lid_stickout = 1.5mm
  PARAM: carrier_output_shaft_length = 17.45mm
  PARAM: housing_lid_min_thickness = 7mm
  PARAM: carrier_base_clearance = 3mm
  PARAM: planet_bearing_OD = 14mm
  PARAM: planet_bearing_ID = 5mm
  PARAM: planet_bearing_h = 5mm
  PARAM: carrier_plate_min_thickness = 2mm
  PARAM: planet_bearing_shoulder_ID = 6.6mm
  PARAM: planet_bearing_shoulder_OD = 12.4mm
  PARAM: gearbox_housing_motor_fastener_diam = 4mm
  PARAM: gearbox_housing_motor_housing_fastener_diam = 3mm
  PARAM: gearbox_housing_sandwich_fastener_diam = 5mm
  PARAM: number_of_sandwich_fasteners = 4
  PARAM: output_shaft_heatsert_diam = 5.84mm
  PARAM: output_shaft_heatsert_depth = 4.7mm
  PARAM: carrier_heatsert_diam = 0mm
  PARAM: carrier_heatsert_depth = 0mm
  PARAM: carrier_planet_fastener_diam = 5mm
  PARAM: m4_heatsert_diam = 5.84mm
  PARAM: m4_heatsert_depth = 4.7mm
  PARAM: Skeleton A.1\Length.8 = 0mm
  PARAM: Skeleton A.1\Length.9 = 0mm
  PARAM: Skeleton A.1\ABS_origin_axis\Origin\X = 0mm
  PARAM: Skeleton A.1\ABS_origin_axis\Origin\Y = 0mm
  PARAM: Skeleton A.1\ABS_origin_axis\Origin\Z = 0mm
  PARAM: Skeleton A.1\ABS_origin_axis\XAxis\X = 1
  PARAM: Skeleton A.1\ABS_origin_axis\XAxis\Y = 0
  PARAM: Skeleton A.1\ABS_origin_axis\XAxis\Z = 0
  PARAM: Skeleton A.1\ABS_origin_axis\YAxis\X = 0
  PARAM: Skeleton A.1\ABS_origin_axis\YAxis\Y = 1
  PARAM: Skeleton A.1\ABS_origin_axis\YAxis\Z = 0
  PARAM: Skeleton A.1\ABS_origin_axis\ZAxis\X = 0
  PARAM: Skeleton A.1\ABS_origin_axis\ZAxis\Y = 0
  PARAM: Skeleton A.1\ABS_origin_axis\ZAxis\Z = 1
  PARAM: Skeleton A.1\datum_axis (mounting height)\Origin\X = 0mm
  PARAM: Skeleton A.1\datum_axis (mounting height)\Origin\Y = 0mm
  PARAM: Skeleton A.1\datum_axis (mounting height)\Origin\Z = 0mm
  PARAM: Skeleton A.1\datum_axis (mounting height)\XAxis\X = 1
  PARAM: Skeleton A.1\datum_axis (mounting height)\XAxis\Y = 0
  PARAM: Skeleton A.1\datum_axis (mounting height)\XAxis\Z = 0
  PARAM: Skeleton A.1\datum_axis (mounting height)\YAxis\X = 0
  PARAM: Skeleton A.1\datum_axis (mounting height)\YAxis\Y = 1
  PARAM: Skeleton A.1\datum_axis (mounting height)\YAxis\Z = 0
  PARAM: Skeleton A.1\datum_axis (mounting height)\ZAxis\X = 0
  PARAM: Skeleton A.1\datum_axis (mounting height)\ZAxis\Y = 0
  PARAM: Skeleton A.1\datum_axis (mounting height)\ZAxis\Z = 1

  REL [Formula.2]: Housing_base_thickness
  REL [Formula.3]: clearance
  REL [Formula.4]: gear_height/2 + carrier_plate_bottom_h + main_bearing_base_clearance
  REL [Formula.6]: ring_pitch_diam 
  REL [Formula.7]: sun_pitch_diam 
  REL [Formula.8]: (ring_pitch_diam -sun_pitch_diam)/2
  REL [Formula.9]: planet_pitch_diam 
  REL [Formula.13]: Main_bearing_ID 
  REL [Formula.14]: Main_bearing_OD 
  REL [Formula.15]: ring_pitch_diam-carrier_ring_clearance
  REL [Formula.17]: (sun_pitch_diam+planet_pitch_diam)/2
  REL [Formula.18]: planet_mid_path
  REL [Formula.20]: 360deg/number_of_planets
  REL [Formula.29]: main_bearing_base_clearance
  REL [Formula.30]: gear_height/2 + carrier_plate_thickness
  REL [Formula.31]: ring_pitch_diam - carrier_ring_clearance
  REL [Formula.32]: ring_pitch_diam+2*ring_wall_thickness+2*Housing_min_wall_thickness
  REL [Formula.33]: Housing_base_thickness+main_bearing_base_clearance+Main_bearing_height+carrier_plate_bottom_h+gear_height+carrier_plate_thickness +carrier_lid_clearance + housing_lid_thickness
  REL [Formula.34]: gear_height/2
  REL [Formula.35]: housing_body_total_height
  REL [Formula.36]: housing_lid_thickness+carrier_output_lid_stickout
  REL [Formula.37]: housing_lid_min_thickness+Main_bearing_height+carrier_lid_clearance
  REL [Formula.38]: carrier_plate_min_thickness + carrier_planet_clearance
  REL [Formula.39]: carrier_plate_thickness+Main_bearing_height
  REL [Formula.40]: sun_pitch_diam 
  REL [Formula.44]: sun_pitch_diam 
  REL [Formula.46]: planet_bearing_ID 
  REL [Formula.47]: planet_bearing_OD 
  REL [Formula.48]: planet_pitch_diam/2
  REL [Formula.49]: carrier_plate_min_thickness 
  REL [Formula.50]: carrier_plate_bottom_h-carrier_planet_clearance
  REL [Formula.52]: planet_mid_path 
  REL [Formula.53]: gearbox_housing_motor_fastener_diam
  REL [Formula.54]: gearbox_housing_motor_housing_fastener_diam
  REL [Formula.55]: ring_pitch_diam + ring_wall_thickness
  REL [Formula.56]: gearbox_housing_sandwich_fastener_diam
  REL [Formula.57]: m4_heatsert_diam
  REL [Formula.58]: m4_heatsert_depth



**Q12: Do you have separate parameters for "nominal" vs "modeled" dimensions?**
e.g., do you have `main_bearing_od = 37` and then the bore is set to `main_bearing_od + some_clearance`? Or is the bore just set to `37` directly?

**A12:** No, there is no nominal or modeled. It's just I did it all as the same. So that's where some of the complexity comes in. Yeah. So for example, for the main bearing, it would just be the main underscore bearing underscore OD equals 37 as my dimension I use to model things.

---

## Manufacturing & Practical

**Q13: Bambu P1S — have you done any test prints for fit?**
Have you printed any test pieces to check how accurate your printer is for bores, pins, and mating surfaces? If so, what offsets did you find?

**A13:** No, we haven't done any testing yet. But we likely will before printing this. But it's parametric, so once we learn the fitment, then we can adjust accordingly. As long as there's some way to translate the test info to the parametric values in the assembly. like maybe a calculator or something we could do in python that's like oh you print a 20 millimeter cube it's this off therefore your bearing from it should be this or like it could be like I don't know we could discuss this again

**Q14: Post-processing plan**
Which features do you plan to post-process (ream, sand, drill)? Or are you hoping most things work as-printed?

**A14:** I'm hoping everything works as printed, as simple as possible. Yeah.

**Q15: Print orientation**
Are you planning to print the housing upright (open top up)? Gears flat? What about the carrier halves?

**A15:** Yeah, the design will need some supports. It's not perfect. It is a prototype. First time learning this CAD software so just trying to get this done as soon as possible. Yeah, open top up. Gear is flat. Carrier halves. Probably just printed beside each other.

---

## Anything else?

**Q16: Any interfaces I missed in the plan?**
Look at the 15 interfaces I listed in the plan. Anything not on that list?

**A16:**

**Q17: Any features you're particularly worried about fitting?**
What keeps you up at night tolerance-wise?

**A17:** Kind of a weird phrase in what keeps you up at night. But what is most concerning for me is making sure the bearings fit all good. It's probably the biggest one. The rest, like the fasteners, they're mostly going to be like tight clearance fits. And then the lid to the body should fit pretty good. And then there's also the case where the carrier is going to be constrained axially with the body, ring gears and lid. So there is definitely some tolerance stack up there that has to work out well.
