# Electrical Intuition Primer

> Not a physics textbook. Just enough intuition to make motor concepts land.
> Read in 10-15 minutes. Play with the simulator after.

---

## The Big Four

### Voltage (V) — Pressure

Voltage is electrical pressure. It's the "push" that wants to move electrons through a wire. A battery sitting on a table has voltage even if nothing is connected — the push exists, it's just not going anywhere yet.

**Feel it:** You've been shocked by static electricity (~3000V) and not by a AA battery (1.5V). Voltage is the "how hard does it push" feeling. But voltage alone doesn't tell you how dangerous or powerful something is — that depends on how much current it can deliver.

| Source | Voltage |
|--------|---------|
| AA battery | 1.5V |
| USB charger | 5V |
| Your ODrive supply | 24V |
| Wall outlet (Canada) | 120V |
| EV battery pack | 400V |
| Static shock | ~3000V (but tiny current, so harmless) |

### Current (A, amps) — Flow

Current is how many electrons are actually flowing through the wire right now. Voltage is the push; current is the flow that results from that push.

**Feel it:** A phone charger delivers ~1-2A. Your ODrive can push 20A+ through the motor — that's a lot of flow, enough to heat wires and melt thin conductors. This is why motor wires are thick.

| Thing | Current |
|-------|---------|
| LED | 0.02A (20mA) |
| Phone charging | 1-2A |
| Laptop charging | 1-3A |
| Your motor at moderate torque | 5-10A |
| Your motor at full effort | 20A+ |
| Electric car motor | 300A+ |
| Lightning bolt | ~20,000A |

### Resistance (Ω, ohms) — Restriction

Resistance is how hard it is for current to flow through something. Thin wire = more resistance. Thick copper = less resistance. A perfect conductor would have zero resistance (current flows freely). An insulator (rubber, air) has near-infinite resistance (no current flows).

This is where Ohm's Law comes in: **V = I × R**

If you apply 24V across something with 12Ω resistance:
- I = V / R = 24 / 12 = 2A flows

If resistance drops to 6Ω:
- I = 24 / 6 = 4A — double the current with the same voltage

**This is why shorting motor wires locks the shaft:** a short circuit has near-zero resistance, so maximum current flows, creating maximum electromagnetic braking force.

### Power (W, watts) — How Fast Energy Is Being Used Right Now

Power = voltage × current: **P = V × I**

Power is a *rate*. It tells you how fast energy is being consumed or produced at this instant. A 100W light bulb converts 100 joules of electrical energy into heat and light every second.

**The real-world scale:**

| Power | What it feels like |
|-------|--------------------|
| 1W | Tiny LED. You wouldn't notice it's on. |
| 5W | Phone charger. Barely warm. |
| 65W | Laptop at full load. Fan spinning. |
| 100W | Old incandescent bulb. Hot to touch. |
| 1,000W (1kW) | Microwave. You can hear it working. |
| 1,500W | Hair dryer on high. Trips breakers if you run two. |
| 3,000W (3kW) | Electric oven element. Heats a room. |
| 10,000W (10kW) | EV cruising on highway. |
| 200,000W (200kW) | Tesla Model 3 at full acceleration. Pushes you into the seat. |

**Your motor's range:** At 24V and 20A, max electrical power = 24 × 20 = 480W. About half a microwave. That's the energy flowing into the motor — some becomes torque, some becomes heat.

---

## Energy vs Power — The Key Distinction

**Power** = how fast. **Energy** = how much total.

Power is like speed (km/h). Energy is like distance (km). You can go fast (high power) for a short time, or slow (low power) for a long time, and end up with the same total energy used.

**Energy = Power × Time: E = P × t**

The unit is **watt-hours (Wh)** or **kilowatt-hours (kWh)**.

- 100W for 1 hour = 100 Wh
- 1000W for 1 hour = 1000 Wh = 1 kWh
- 1000W for 30 minutes = 500 Wh

| Thing | Energy stored |
|-------|---------------|
| Phone battery | ~15 Wh |
| Laptop battery | ~60 Wh |
| E-bike battery | ~500 Wh |
| Your house (daily usage) | ~30 kWh |
| Tesla Model 3 battery | 60 kWh |
| Gas in a full car tank | ~600 kWh equivalent |

**What does 1 kWh feel like?** It's what your microwave uses in 1 hour. Or your laptop for about 15 hours. Or enough to drive a Tesla about 6 km. BC Hydro charges you about $0.10 per kWh.

---

## The Three Laws You Need

Everything in this primer comes from three relationships:

| Law | Equation | What it means |
|-----|----------|---------------|
| Ohm's Law | V = I × R | More pressure (V) or less restriction (R) = more flow (I) |
| Power | P = V × I | Pressure × flow = how fast energy moves |
| Energy | E = P × t | Rate × time = total energy |

You can rearrange these:
- Need current? I = V / R
- Need resistance? R = V / I
- Need voltage from power? V = P / I
- Need current from power? I = P / V

---

## Capacitance and Impedance (Brief)

You mentioned these — quick intuition:

**Capacitance (Farads):** A capacitor stores energy in an electric field. Think of it as a tiny rechargeable bucket — it fills up fast and dumps fast. Your ODrive has capacitors on the DC bus to handle sudden current spikes when the motor demands more than the power supply can instantly deliver.

**Impedance (Ohms):** Resistance, but for AC circuits. When current oscillates (like your motor's phase currents), the coils' inductance and any capacitance affect how current flows — not just resistance. Impedance bundles all three effects into one number. For DC (steady current), impedance = resistance. For AC, it's more complex.

You don't need to understand impedance math right now. When it comes up in Topic 09 (Impedance Control), it's a different meaning — controlling how the actuator *feels* to external forces, not the electrical property.

---

## Interactive Tool

Play with this to build intuition:

**[Falstad Circuit Simulator](https://www.falstad.com/circuit/)** — free, runs in browser. Click Circuits → Basics → Ohm's Law. You'll see current flowing (animated dots), and you can drag sliders to change voltage and resistance and watch what happens to current. The moving dots make V/I/R tangible.

Try these experiments:
1. Increase voltage → watch current increase (more pressure = more flow)
2. Increase resistance → watch current decrease (more restriction = less flow)
3. Add a second resistor in series → total resistance goes up, current goes down
4. Short circuit a resistor → all current flows through the short (zero resistance path)
