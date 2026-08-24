PCB export: IPC-2581
The pcb export ipc2581 command exports a board design in IPC-2581 format.

Usage: kicad-cli pcb export ipc2581 [--help] [--output OUTPUT_FILE] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--precision PRECISION] [--compress] [--version VAR] [--units VAR] [--bom-col-int-id FIELD_NAME] [--bom-col-mfg-pn FIELD_NAME] [--bom-col-mfg FIELD_NAME] [--bom-col-dist-pn FIELD_NAME] [--bom-col-dist FIELD_NAME] [--bom-rev REVISION] [--variant VAR] INPUT_FILE

Positional arguments:

INPUT_FILE

Board file to export.

Optional arguments:

-h, --help

Show help for the IPC-2581 export command.

-o <output filename>, --output <output filename>

The output filename. When --output is not used, the output filename will be the same as the input file, with the .xml file extension.

--drawing-sheet <sheet path>

Path to drawing sheet to use in plot, overriding the drawing sheet specified in the board file.

-D <variable name>=<value>, --define-var <variable name>=<value>

Add or override project variable definitions. Can be used multiple times to define multiple variables.

--precision <precision>

The precision (number of digits after the decimal separator) for the exported file. The default is 6.

--compress

Compress output file as a ZIP file.

--version <IPC-2581 standard version>

IPC-2581 standard version to use. Options are B or C (default).

--units <unit>

Units to use in export. Options are mm (default) or in.

--bom-col-int-id <field>

Name of the part field to use for the Bill of Materials Internal ID column. This can be any footprint field, or blank to omit this column.

--bom-col-mfg-pn <field>

Name of the part field to use for the Bill of Materials Manufacturer Part Number column. This can be any footprint field, or blank to omit this column.

--bom-col-mfg <field>

Name of the part field to use for the Bill of Materials Manufacturer column. This can be any footprint field, or blank to omit this column.

--bom-col-dist-pn <field>

Name of the part field to use for the Bill of Materials Distributor Part Number column. This can be any footprint field, or blank to omit this column.

--bom-col-dist <field>

Name of the part field to use for the Bill of Materials Distributor column. This can be any footprint field, or blank to omit this column.

--bom-rev <revision>

Revision to use for the Bill of Materials Revision field. If not given, the Revision field from the schematic’s root sheet is used instead.

--variant <variant name>

The name of the variant to output. You can use ${VARIANT} in the output path to generate an output filename specific to the variant. When --variant is not used, the default variant is output.
