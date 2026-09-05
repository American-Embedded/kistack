---
name: kicad-pcb
description: Review KiCad PCB layouts with DRC, layer renders, and 3D-model interference inspection.
---

# Skill for PCB design and review

## Placement

Place components like decoupling capacitors in orientations and locations that minimize loop area for ground and minimize trace length for inductance. If packages do not fit, consult the engineer to confirm that their recommended size per the schematic may need to change.

Your goal is to optimize placement of components, that is paramount. Good placement brings good routing. 

Review placement by carefully thinking about the actual size of the component, its relation to the other packages. Keep things neatly aligned. Consult the engineer before proceeding with double-sided designs, unless this is explicitly stated. You can render images of specific areas of the PCB or render SVGs from GERBERs with the $kicad-gerbers skill to review this. kicad-monkey also has some capabilities here to allow you to parse the schematic more easily.

You are unlikely to one-shot perfect placement, so do not spend time over-optimizing. Place parts in reasonable locations so that it is easier for the engineer to modify them.

Board outlines should have rounded or chamfered corners, confirm with the engineer. 

Connectors that are horizontal should be placed near board edges as a rule. Vertical connectors may be placed in various locations depending on the engineer's requirements.

## Review

Confirm with kicad-cli that DRC rules pass. 

Use kicad-cli to render SVGs of board layers to validate that their connections look reasonable.

Use kicad-cli to render images of various areas of the PCB to validate interference with 3D models.
