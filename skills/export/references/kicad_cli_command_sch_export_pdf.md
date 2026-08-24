Schematic export: PDF
The sch export pdf command exports a schematic to a PDF file. Each sheet in the design is exported to its own page in the PDF file.

Usage: kicad-cli sch export pdf [--help] [--output OUTPUT_FILE] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--variant VAR] [--theme THEME_NAME] [--black-and-white] [--exclude-drawing-sheet] [--default-font VAR] [--draw-hop-over] [--exclude-pdf-property-popups] [--exclude-pdf-hierarchical-links] [--exclude-pdf-metadata] [--no-background-color] [--pages PAGE_LIST] INPUT_FILE

Positional arguments:

INPUT_FILE

Schematic file to export.

Optional arguments:

-h, --help

Show help for the PDF file export command.

-o <output filename>, --output <output filename>

The output filename. When --output is not used, the output filename will be the same as the input file, with a .pdf file extension.

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

Plot PDF without a drawing sheet.

--default-font <font name>

Default font name. Default: "KiCad Font".

--draw-hop-over

Draw hop-overs at wire crossings.

--exclude-pdf-property-popups

Do not generate property popups in PDF.

--exclude-pdf-hierarchical-links

Do not generate clickable links for hierarchical elements in PDF.

--exclude-pdf-metadata

Do not generate PDF metadata from AUTHOR and SUBJECT variables.

-n, --no-background-color

Export schematic without a background color, regardless of theme.

--pages <page list>

Comma-separated list of pages to export. Blank or unspecified means all pages. To plot specific pages, give the root sheet as INPUT_FILE and specify the desired output pages with the --pages argument.
