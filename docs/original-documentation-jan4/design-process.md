# Design Process

The step-by-step process followed during the Jan 4 design sprint.

## 1. Establish Design Requirements
- Define agreed upon end goal for the actuator
  - These should be quantifiable and measurable by the end of the project
- List limits and constraints

## 2. Research and Brainstorm
- Compile concepts to reach this goal
- Gain context and knowledge on the benefits and drawbacks of each approach
- Create a full system diagram

## 3. Create and Rank Concepts
- Organize and rank possible solutions (trade studies / Pugh matrices)

## 4. Create Preliminary Design Elements
- Decide how elements will interact with each other
- Further define interfaces and domains
- Scope out basic models of systems and their interactions
- Define control system/method

## 5. Concept Selection & Ranking
- Rank concepts based on:
  - **Printability:** Likelihood of success on an FDM printer
  - **Backlash:** Suitability for QDD control
  - **Complexity:** Part count and assembly time

## 6. System Architecture & Preliminary Design
- **Interface Definition:** Rigidly define how domains connect:
  - Thermal: Motor to mount
  - Mechanical: Output shaft to load
  - Data: Magnet position relative to encoder chip
- **Control Strategy:** Confirm ODrive control mode matches mechanical design

## 7. Detailed Design (CAD)
- **Modeling:** Create the 3D geometry
- **DFM:** Apply printing tolerances (offsets) and design orientation features (avoiding supports on gear faces)
- **Virtual Assembly:** Test the assembly in CAD to catch interference

## Key Insight
> The #1 failure mode in student robotics projects is not the gearbox itself, but how the gearbox attaches to the motor or how the magnet attaches to the shaft. Interface definition is critical.
