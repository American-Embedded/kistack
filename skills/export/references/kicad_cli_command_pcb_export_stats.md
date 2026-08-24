PCB export: statistics
The pcb export stats command exports a report of statistics about the board design.

Usage: kicad-cli pcb export stats [--help] [--output OUTPUT_FILE] [--format FORMAT] [--units UNITS] [--exclude-footprints-without-pads] [--subtract-holes-from-board] [--subtract-holes-from-copper] INPUT_FILE

Positional arguments:

INPUT_FILE

Board file to export statistics from.

Optional arguments:

-h, --help

Show help for the statistics command.

-o <output filename>, --output <output filename>

Output filename for the generated statistics report. When --output is not used, the output filename will be the same as the input file, with a _statistics suffix and the .rpt or .json file extension, depending on the selected format.

--format <format>

Report file format. Options are report (default) or json.

--units <unit>

Units to use in the report. Options are mm (default) or in.

--exclude-footprints-without-pads

Exclude footprints that do not contain any pads from component counts.

--subtract-holes-from-board

Subtract the area of holes from the total board area.

--subtract-holes-from-copper

Subtract the area of holes from the total copper area.
