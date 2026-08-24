Schematic export: netlist
The sch export netlist command exports a netlist in various formats from a schematic.

Usage: kicad-cli sch export netlist [--help] [--output OUTPUT_FILE] [--variant VAR] [--format FORMAT] INPUT_FILE

Positional arguments:

INPUT_FILE

Schematic file to export.

Optional arguments:

-h, --help

Show help for the netlist export command.

-o <output filename>, --output <output filename>

The output filename. When --output is not used, the output filename will be the same as the input file, with a .net file extension.

--variant <variant name>

The name of the variant to output. You can use ${VARIANT} in the output path to generate an output filename specific to the variant. When --variant is not used, the default variant is output.

--format <format>

The netlist output format. Options are kicadsexpr (default), kicadxml, cadstar, orcadpcb2, spice, spicemodel, pads, or allegro.
