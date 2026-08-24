PCB export: ODB++
The pcb export odb command exports a board design in ODB++ format.

Usage: kicad-cli pcb export odb [--help] [--output OUTPUT_FILE] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--precision PRECISION] [--compression VAR] [--units VAR] [--variant VAR] INPUT_FILE

Positional arguments:

INPUT_FILE

Board file to export.

Optional arguments:

-h, --help

Show help for the ODB++ export command.

-o <output filename>, --output <output filename>

The output filename, or folder name if no compression is used.

--drawing-sheet <sheet path>

Path to drawing sheet to use in plot, overriding the drawing sheet specified in the board file.

-D <variable name>=<value>, --define-var <variable_name>=<value>

Add or override project variable definitions. Can be used multiple times to define multiple variables.

--precision <precision>

The precision (number of digits after the decimal separator) for the exported file. The default is 2.

--compression <mode>

Compression mode. Options are none, zip (default), or tgz.

--units <unit>

Units to use in the output file. Options are mm (default) or in.

--variant <variant name>

The name of the variant to output. You can use ${VARIANT} in the output path to generate an output filename specific to the variant. When --variant is not used, the default variant is output.
