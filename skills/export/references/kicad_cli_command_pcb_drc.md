PCB commands
The pcb command runs a design rule check or exports a board to various other file formats, including fabrication and 3D files.

PCB DRC
The pcb drc command runs a design rule check on a board and generates a report.

Usage: kicad-cli pcb drc [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--format FORMAT] [--all-track-errors] [--schematic-parity] [--units UNITS] [--severity-all] [--severity-error] [--severity-warning] [--severity-exclusions] [--exit-code-violations] [--refill-zones] [--save-board] INPUT_FILE

Positional arguments:

INPUT_FILE

Board file to run DRC on.

Optional arguments:

-h, --help

Show help for the DRC command.

-o <output filename>, --output <output filename>

Output filename for the generated DRC report. When --output is not used, the output filename will be the same as the input file, with the .rpt or .json file extension, depending on the selected format.

-D <variable name>=<value>, --define-var <variable_name>=<value>

Add or override project variable definitions. Can be used multiple times to define multiple variables.

--format <format>

Report file format. Options are report (default) or json.

--all-track-errors

Report all errors for each track.

--schematic-parity

Test for parity between PCB and schematic.

--units <unit>

Units to use in the report. Options are mm (default), in, or mils.

--severity-all

Report all DRC violations. This is equivalent to using all of the other DRC severity options.

--severity-error

Report all error-level DRC violations. This can be combined with the other DRC severity options.

--severity-warning

Report all warning-level DRC violations. This can be combined with the other DRC severity options.

--severity-exclusions

Report all excluded DRC violations. This can be combined with the other DRC severity options.

--exit-code-violations

Return an exit code depending on whether or not DRC violations exist. The exit code is 0 if no violations are found, and 5 if any violations are found.

--refill-zones

Refill all zones before running DRC. The board will not be saved after refilling zones unless --save-board is also used.

--save-board

Save the board after running DRC. The board will not be saved unless --refill-zones is also used.
