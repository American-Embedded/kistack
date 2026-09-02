---
name: kicad-footprint
description: Generate compliant KiCad footprints from official KiCad Library Tools
---

# This skill allows an LLM to generate KiCad footprints in a programmatic way, using KiCad Library Tools and the infrastructure built up around it. It does not necessarily provide a whole solution for library management.

## Setup
Using the https://gitlab.com/kicad/libraries/kicad-library-tools repository, clone it somewhere for safe-keeping, possibly as a submodule under the existing project. Create a dedicated virtual environment for the Python dependencies it has. The docs directory has information on setup, including how to use ./manage.sh. As a rule, the user will want to also have 3D files generated for footprints, so include these dependencies.

## Usage

- First, identify if the footprint the user is asking for already exists in their KiCad library! If it does, there's no need to recreate it unless they are asking for modifications like solder mask expansion for BGAs or smaller courtyard areas, or silkscreen modification.
- Next, identify what category the footprint the user is requesting likely corresponds to. Is it a QFN? Is it an LGA? What is it? If unsure, ask the user.
- You should look at existing yaml definitions and the generator script for that category to see what options are available. Make sure your footprints look compliant with other similar footprints.
- Did the user supply a PDF or image of the land pattern? Describe the land pattern using text before implementing a yaml description. "This pad is 5mm away from center in x, 5mm away in y" and similar descriptions are very helpful for your understanding. Confirm this understanding with the user unless they have written out a description in this way already. Even then, it's not a bad idea for you to also render an image of the land pattern for your own info.
- Ask the user for the 3D dimensions if necessary to render the 3D model (unless the user specifies not to render a 3D model of course).
- Verify the footprint by investigating the files and rendering them. Also do the same with the 3D model
- When complete, ask the user where the footprint should live. If this info is already in context, please use it. (AGENTS.md or CLAUDE.md might contain that so if so please use that.)

Items to watch for that may require human intervention:
- When pads are non-standard in shape
- When an existing generator is not available, please ask before implementing a new generator

As a rule, keep any new yaml files co-located with the library that you generate from. Do not modify other footprints when making a new one.
