---
name: kicad-pcb
description: Review KiCad PCB layouts with DRC, layer renders, and 3D-model interference inspection.
---

# Skill for PCB design and review

## Editing the active board in place

For normal placement, routing, and cleanup work, first identify the project's canonical configured `.kicad_pcb` path—the board opened by the project or viewer—and keep using that exact path. Save each meaningful milestone to it so the active board and collaborators show progress. Keep backups and intermediate tool outputs in a separate backup or build directory. If a tool writes a staging or alternate file, validate it and promote the result back to the canonical path with a backup before continuing; do not silently switch the active filename. Use an alternate board only when the user explicitly requests an experiment or alternate design, and label it clearly. Coordinate ownership so only one agent or process writes the active board at a time; other agents may inspect it or prepare changes for integration.

## Placement

Place components like decoupling capacitors in orientations and locations that minimize loop area for ground and minimize trace length for inductance. If packages do not fit, consult the engineer to confirm that their recommended size per the schematic may need to change.

Your goal is to optimize placement of components, that is paramount. Good placement brings good routing. 

Review placement by carefully thinking about the actual size of the component, its relation to the other packages. Keep things neatly aligned. Consult the engineer before proceeding with double-sided designs, unless this is explicitly stated. You can render images of specific areas of the PCB or render SVGs from GERBERs with the $kicad-gerbers skill to review this. kicad-monkey also has some capabilities here to allow you to parse the schematic more easily.

You are unlikely to one-shot perfect placement, so do not spend time over-optimizing. Place parts in reasonable locations so that it is easier for the engineer to modify them.

### Congested routing → move parts (do not spaghetti)

When a net repeatedly fails the structural DRC gate (`shorting_items` / `tracks_crossing` / `clearance` / `hole_to_hole`) because corridors are blocked by other copper or packages:

1. **Stop lengthening detours.** A 3-layer wrap around the board is a placement smell, not a routing win.
2. **Move the obstructing or endpoint footprints** (even a few mm) to open a short Manhattan channel. Prefer moving passives / sense shunts / inductors before moving MCUs.
3. **One net (or one local island) at a time**, then re-run DRC with `kicad-cli pcb drc --format json --severity-all --refill-zones`.
4. After a move: delete orphan tracks that still end at the old pad coordinates (add-only + bak restore is safer than `Remove()` mid-iteration on Windows pcbnew).
5. Keep power-loop intent: SW node ↔ inductor ↔ rectifier/cap stays short even after the nudge.

Engineer-authorized signal: if the user says placement may change when corridors are too tight, treat footprint nudges as in-scope without re-asking.

Board outlines should have rounded or chamfered corners, confirm with the engineer. 

Connectors that are horizontal should be placed near board edges as a rule. Vertical connectors may be placed in various locations depending on the engineer's requirements.

## Review

Confirm with kicad-cli that DRC rules pass. 

Use kicad-cli to render SVGs of board layers to validate that their connections look reasonable.

Use kicad-cli to render images of various areas of the PCB to validate interference with 3D models.

## After schematic net changes

1. Export a fresh netlist (`kicad-cli sch export netlist`) and read annotation warnings.
2. Sync PCB pad nets from that netlist (KiCad `bin\python.exe` + pcbnew, or Update PCB from schematic in the GUI).
3. Remap copper that still carries the old net name near remapped pads; refill zones; re-run DRC with `--refill-zones --schematic-parity`.
4. Treat large clearance/short bursts after a net rename as a sync problem first, not a place-from-scratch problem.

## Tooling caveats

- KiCad MCP / footprint-parity tools that only read instance `Footprint` fields can report "0 schematic footprints" when instances leave Footprint blank and the library symbol holds the real footprint. Cross-check with netlist refs vs PCB refs before ripping up the board.
- IPC/`pcbnew` live sessions may be unavailable; file-backed `.kicad_pcb` + `kicad-cli` is the reliable path on Windows agents.
- Windows agents: use KiCad `bin\python.exe` + full-path `kicad-cli.exe`. DRC gate flag is `--severity-all` (not `--satisfaction-all`).
- Never call `PCB_VIA.GetWidth()` without a layer (hang/assert). Prefer add-only artwork scripts; restore from `.bak_ok_*` instead of mid-session `Remove()` sweeps when possible.
- Structural gate before advancing a net family: `shorting_items` / `tracks_crossing` / `clearance` / `hole_to_hole` == 0. Other DRC noise can wait.
