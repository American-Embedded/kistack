PCB export: position file
The pcb export pos command exports a position file from a board design.

Usage: kicad-cli pcb export pos [--help] [--output OUTPUT_FILE] [--side VAR] [--format FORMAT] [--units UNITS] [--bottom-negate-x] [--use-drill-file-origin] [--smd-only] [--exclude-fp-th] [--exclude-dnp] [--gerber-board-edge] [--variant VAR] INPUT_FILE

Positional arguments:

INPUT_FILE

Board file to export.

Optional arguments:

-h, --help

Show help for the position file export command.

-o <output filename>, --output <output filename>

The output filename. When --output is not used, the output filename will be the same as the input file, with the .pos file extension.

--side <side>

The side of the board to export. Options are front, back, or both (default). Gerber format does not support both.

--format <format>

The position file format. Options are ascii (default), csv, or gerber.

--units <unit>

Units for position file. Options are in (default) or mm. This option has no effect for Gerber format.

--bottom-negate-x

Use negative X coordinates for footprints on the bottom layer. This option has no effect for Gerber format.

--use-drill-file-origin

Use drill/place file origin instead of absolute origin. This option has no effect for Gerber format.

--smd-only

Include only surface-mount components. This option has no effect for Gerber format.

--exclude-fp-th

Exclude all footprints with through-hole pads. This option has no effect for Gerber format.

--exclude-dnp

Exclude all footprints with "Do not populate" attribute.

--gerber-board-edge

Include board edge layer in export (Gerber format only).

--variant <variant name>

The name of the variant to output. You can use ${VARIANT} in the output path to generate an output filename specific to the variant. When --variant is not used, the default variant is output.
