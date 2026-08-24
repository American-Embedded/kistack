PCB export: VRML
The pcb export vrml command exports a board design to a VRML 3D model file.

Usage: kicad-cli pcb export vrml [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--force] [--no-unspecified] [--no-dnp] [--variant VAR] [--user-origin VAR] [--units VAR] [--models-dir VAR] [--models-relative] INPUT_FILE

Positional arguments:

INPUT_FILE

Board file to export.

Optional arguments:

-h, --help

Show help for the VRML export command.

-o <output filename>, --output <output filename>

The output filename. When --output is not used, the output filename will be the same as the input file, with the .wrl file extension.

-D <variable name>=<value>, --define-var <variable_name>=<value>

Add or override project variable definitions. Can be used multiple times to define multiple variables.

-f, --force

Overwrite output file.

--no-unspecified

Exclude 3D models of components with "unspecified" footprint type.

--no-dnp

Exclude 3D models of components with "Do not populate" attribute.

--variant <variant name>

The name of the variant to output. You can use ${VARIANT} in the output path to generate an output filename specific to the variant. When --variant is not used, the default variant is output.

--user-origin <output origin>

Specify a custom origin for the output file, with X and Y coordinates. For example, 1x1in, 1x1inch, or 25.4x25.4mm. The default unit is millimeters. If this option is not given, the board center is used.

--units <units>

Units to use in the output file. Options are mm, m, in (default), or tenths (tenths of an inch).

--models-dir <output model directory>

Name of output directory to copy component models into. If not used, component models are embedded into the output file.

--models-relative

With --models-dir, use relative paths in the output file.
