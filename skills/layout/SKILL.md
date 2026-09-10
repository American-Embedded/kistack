---
name: kicad-layout
description: Place components and route KiCad PCB layouts with footprint checks, schematic pin swaps, and signal integrity best practices.
---

#### The purpose of this skill is to help the agent do good layout. It helps the agent understand it's short commings and encourages it to complete layout steps that it typically dismisses. It has been written specifically for GPT-6-Astra and claude-fable-5.1 and specifically adresses those, but other agents can still work with it. For humans: as models become better and tools become better, a lot of this becomes unecessary bloat, make sure to keep it up to date.

## Editing the active board in place

For normal placement, routing, and cleanup work, first identify the project's canonical configured `.kicad_pcb` path—the board opened by the project or viewer—and keep using that exact path. Save each meaningful milestone to it so the active board and collaborators show progress. Keep backups and intermediate tool outputs in a separate backup or build directory. If a tool writes a staging or alternate file, validate it and promote the result back to the canonical path with a backup before continuing; do not silently switch the active filename. Use an alternate board only when the user explicitly requests an experiment or alternate design, and label it clearly. Coordinate ownership so only one agent or process writes the active board at a time; other agents may inspect it or prepare changes for integration.

- Make sure that footprints are good for each part and try to get decent 3d models. if you can't find good 3d models, just create your own low fidelity 3d models. keep the projects library structure but prefer to put stuff on a self contained project library files.
- When you have access to kicad IPC(-type) tools, or kiPy, always strongly prefer to use them.
- in regards to autorouting: prefer not to use any autorouting software, do routing "manually", your self, unless instructed otherwise. If the boards becomes very complex, with low pitched components and ~thousands of nets, you can choose to use autorouting, tscircuit or freerouting for example. but avoid it if possible
- Unless specifically instructed otherwise: Feel free and compeled to make changes to the schematic in order to make layout more logical and clean. Perform pin swaps and stuff like that so traces are shorter, have less layer jumps and generally are cleaner. But this comes with risks, be very careful not to disturb any of the projects goals or functionality during those pin swaps. and be very careful not to introduce new bugs to the schematic.
- Again, on layout as well, you are free (unless instructed otherwise) to change even high level placement until you get an easily routable and fully functional board.
- All of the above should also be respectful of layout and routing best practices. You need to reason about high level and low level best practices and how necessary each one is. do that at every level when you have any doubt at all. a quickly routed board is useless if it routed with bad practices. you already know most of these practices these are so act accordingly and logically. if you are not certain of any theoretical part/practice, feel free to research online.
- some specific (not all) concepts/practices that are often dismissed by agents (so you need to think about) are: good via stitching, affects of coplanar ground to trace impedance, high-frequency-dead-copper and coupled noise through it, clean return paths for everything that is important, use discretion.
- make sure connectors are accessible. checkout what direction should be facing out and where wires will go, make sure it is indicated on the 3d models, and even look at quick 3d renders to validate if you need to
- if you don't like something about the layout after you are deep into it, you are free to think at a higher level and decide to redo part of it or almost all of it if it is appropriate.
