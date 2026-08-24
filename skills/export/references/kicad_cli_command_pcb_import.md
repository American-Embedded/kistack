PCB import
The pcb import command imports a non-KiCad PCB file to KiCad format. Layers in the input board file are automatically mapped to KiCad layers.

Usage: kicad-cli pcb import [--help] [--output OUTPUT_FILE] [--format FORMAT] [--report-format FORMAT] [--report-file FILE] INPUT_FILE

Positional arguments:

INPUT_FILE

Non-KiCad format board file to import.

Optional arguments:

-h, --help

Show help for the import command.

-o <output filename>, --output <output filename>

The output filename. When --output is not used, the output filename will be the same as the input file, with the .kicad_pcb file extension.

--format <format>

The input board file format. Options are auto (default), pads, altium, eagle, cadstar, fabmaster, pcad, and solidworks. If the format is auto, or if no format is given, KiCad will attempt to automatically determine the input board file format.

--report-format <format>

Report file format. Options are none (default), json, or text.

--report-file <report filename>

Output filename for the generated import report. When --report-file is not used, the report is printed to stdout.
