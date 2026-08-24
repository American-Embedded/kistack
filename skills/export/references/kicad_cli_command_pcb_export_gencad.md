PCB export: GenCAD
The pcb export gencad command exports a board design to a GenCAD file.

Usage: kicad-cli pcb export gencad [--help] [--output OUTPUT_DIR] [--define-var KEY=VALUE]…​ [--flip-bottom-pads] [--unique-pins] [--unique-footprints] [--use-drill-origin] [--store-origin-coord] INPUT_FILE

Positional arguments:

INPUT_FILE

Board file to export.

Optional arguments:

-h, --help

Show help for the DXF export command.

-o <output filename>, --output <output filename>

The output filename. When --output is not used, the output filename will be the same as the input file, with the .cad file extension.

-D <variable name>=<value>, --define-var <variable_name>=<value>

Add or override project variable definitions. Can be used multiple times to define multiple variables.

-f, --flip-bottom-pads

Flip bottom footprint padstacks.

--unique-pins

Generate unique pin names.

--unique-footprints

Generate a new shape for each footprint instance (do not reuse shapes).

--use-drill-origin

Use drill/place file origin as origin.

--store-origin-coord

Save the origin coordinates in the file.
