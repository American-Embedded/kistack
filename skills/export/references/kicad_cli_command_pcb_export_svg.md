PCB export: SVG
The pcb export svg command exports a board design to an SVG file.

Usage: kicad-cli pcb export svg [--help] [--output OUTPUT_DIR] [--layers LAYER_LIST] [--common-layers COMMON_LAYER_LIST] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--subtract-soldermask] [--mirror] [--theme THEME_NAME] [--negative] [--black-and-white] [--sketch-pads-on-fab-layers] [--hide-DNP-footprints-on-fab-layers] [--sketch-DNP-footprints-on-fab-layers] [--crossout-DNP-footprints-on-fab-layers] [--page-size-mode MODE] [--fit-page-to-board] [--exclude-drawing-sheet] [--drill-shape-opt SHAPE_OPTION] [--mode-single] [--mode-multi] [--scale SCALE] [--check-zones] [--variant VAR] INPUT_FILE

Positional arguments:

INPUT_FILE

Board file to export.

Optional arguments:

-h, --help

Show help for the SVG file export command.

-o <output dir>, --output <output dir>

The output folder or filename for the exported files. When --mode-single is used, this is the output filename. If --output is not used, the output filename will be the same as the input file, with the .pdf file extension. When --mode-multi is used, this is the output directory. If --output is not used, the files are exported to the current directory.

-l <layer list>, --layers <layer list>

A comma-separated list of layer names to export from the board, such as F.Cu,B.Cu. At least one layer must be given. Layer names can be specified as canonical layer names (F.Cu, In.1, F.Fab, etc.) or as user-defined (custom) layer names, but user-defined layer names are matched first.

--cl <layer list>, --common-layers <layer list>

A comma-separated list of layer names to plot on all layers, such as F.Cu,B.Cu. Layer names can be specified as canonical layer names (F.Cu, In.1, F.Fab, etc.) or as user-defined (custom) layer names, but user-defined layer names are matched first.

--drawing-sheet <sheet path>

Path to drawing sheet to use in plot, overriding the drawing sheet specified in the board file.

-D <variable name>=<value>, --define-var <variable_name>=<value>

Add or override project variable definitions. Can be used multiple times to define multiple variables.

--subtract-soldermask

Remove silkscreen from areas without soldermask.

-m, --mirror

Mirror the board. This can be useful for showing bottom layers.

-t <theme name>, --theme <theme name>

The name of the theme to use for export. If no theme is given, the board editor’s currently selected theme is used.

-n, --negative

Plot in negative.

--black-and-white

Plot in black and white.

--sp, --sketch-pads-on-fab-layers

Draw pad outlines and their numbers on front and back fab layers.

--hdnp, --hide-DNP-footprints-on-fab-layers

Don’t plot text and graphics of DNP footprints on fab layers.

--sdnp, --sketch-DNP-footprints-on-fab-layers

Plot graphics of DNP footprints in sketch mode on fab layers.

--cdnp, --crossout-DNP-footprints-on-fab-layers

Plot an "X" over the courtyard of DNP footprints on fab layers, and strikeout their reference designators.

--page-size-mode <mode>

Set page sizing mode. Options are 0 (default), 1, or 2. 0 sets the output page size to fit the entire sheet, including drawing sheet frame and title block. 1 sets the output page size to match the current page size. 2 sets the output page size to the size of the board itself.

--fit-page-to-board

Set the SVG size to match the board outline. This is equivalent to --page-size-mode 2.

--exclude-drawing-sheet

Plot SVG without a drawing sheet.

--drill-shape-opt

The shape of drill marks in the plot. Options are 0 for no drill marks, 1 for small marks, or 2 for actual size marks (default).

--mode-single

Generates a single file with the output arg path acting as the complete directory and filename path. COMMON_LAYER_LIST does not function in this mode. Instead LAYER_LIST controls all layers plotted.

--mode-multi

Plot the layers to one or more SVG files, with each file representing a single layer from LAYER_LIST. The output path specifies the directory in which the files will be written.

--scale <scale>

A scaling factor to use for plotting the PCB. The border and title block are not scaled. A scale factor of 0 autoscales the plot.

--check-zones

Check zone fills and refill zones, if required, prior to export. Any zone fill updates are not saved in the board file.

--variant <variant name>

The name of the variant to output. You can use ${VARIANT} in the output path to generate an output filename specific to the variant. When --variant is not used, the default variant is output.
