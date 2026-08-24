Schematic export: bill of materials (legacy BOM scripts)
The sch export python-bom command exports an XML BOM file from a schematic. The XML BOM file can then be processed into your desired BOM format using a custom script or one of the scripts described in the schematic BOM export documentation.

Usage: kicad-cli sch export python-bom [--help] [--output OUTPUT_FILE] INPUT_FILE

Positional arguments:

INPUT_FILE

Schematic file to export.

Optional arguments:

-h, --help

Show help for the BOM export command.

-o <output filename>, --output <output filename>

The output filename. When --output is not used, the output filename will be the same as the input file, with a -bom.xml suffix and file extension.
