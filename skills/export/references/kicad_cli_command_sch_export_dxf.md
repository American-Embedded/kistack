Schematic export: DXF
The sch export dxf command exports a schematic to a DXF file. Each sheet in the design is exported to its own file.

Usage: kicad-cli sch export dxf [--help] [--output OUTPUT_DIR] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--variant VAR] [--theme THEME_NAME] [--black-and-white] [--exclude-drawing-sheet] [--default-font VAR] [--draw-hop-over] [--pages PAGE_LIST] INPUT_FILE

Positional arguments:

INPUT_FILE

Schematic file to export.

Optional arguments:

-h, --help

Show help for the DXF file export command.

-o <output dir>, --output <output dir>

The output folder for the exported files. One file is output for each sheet. When --output is not used, the files are exported to the current directory.

--drawing-sheet <sheet path>

Path to drawing sheet to use in plot, overriding the drawing sheet specified in the schematic file.

-D <variable name>=<value>, --define-var <variable_name>=<value>

Add or override project variable definitions. Can be used multiple times to define multiple variables.

--variant <variant name>

The name of the variant to output. You can use ${VARIANT} in the output path to generate an output filename specific to the variant. When --variant is not used, the default variant is output.

-t <theme name>, --theme <theme name>

The name of the theme to use for export. If no theme is given, the schematic editor’s currently selected theme is used.

-b, --black-and-white

Export schematic in black and white.

-e, --exclude-drawing-sheet

Plot DXF without a drawing sheet.

--default-font <font name>

Default font name. Default: "KiCad Font".

--draw-hop-over

Draw hop-overs at wire crossings.

--pages <page list>

Comma-separated list of pages to export. Blank or unspecified means all pages. To plot specific pages, give the root sheet as INPUT_FILE and specify the desired output pages with the --pages argument.
