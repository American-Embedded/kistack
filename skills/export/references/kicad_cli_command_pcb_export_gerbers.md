PCB export: Gerber
The pcb export gerbers command exports a board design to Gerber files, with one layer per file.

Usage: kicad-cli pcb export gerbers [--help] [--output OUTPUT_DIR] [--layers LAYER_LIST] [--common-layers COMMON_LAYER_LIST] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--exclude-refdes] [--exclude-value] [--include-border-title] [--sketch-pads-on-fab-layers] [--hide-DNP-footprints-on-fab-layers] [--sketch-DNP-footprints-on-fab-layers] [--crossout-DNP-footprints-on-fab-layers] [--no-x2] [--no-netlist] [--subtract-soldermask] [--disable-aperture-macros] [--use-drill-file-origin] [--precision PRECISION] [--no-protel-ext] [--check-zones] [--variant VAR] [--board-plot-params] INPUT_FILE

Positional arguments:

INPUT_FILE

Board file to export.

Optional arguments:

-h, --help

Show help for the Gerber export command.

-o <output dir>, --output <output dir>

The output folder for the exported files. One file is output for each layer. When --output is not used, the files are exported to the current directory.

-l <layer list>, --layers <layer list>

A comma-separated list of layer names to plot from the board, such as F.Cu,B.Cu. If this argument is not used, all layers will be plotted. A seperate output file is plotted for each layer. Layer names can be specified as canonical layer names (F.Cu, In.1, F.Fab, etc.) or as user-defined (custom) layer names, but user-defined layer names are matched first.

--cl <layer list>, --common-layers <layer list>

A comma-separated list of layer names to plot on all layers, such as F.Cu,B.Cu. Each layer specified is included in every output file. Layer names can be specified as canonical layer names (F.Cu, In.1, F.Fab, etc.) or as user-defined (custom) layer names, but user-defined layer names are matched first.

--drawing-sheet <sheet path>

Path to drawing sheet to use in plot, overriding the drawing sheet specified in the board file.

-D <variable name>=<value>, --define-var <variable_name>=<value>

Add or override project variable definitions. Can be used multiple times to define multiple variables.

--erd, --exclude-refdes

Exclude footprint reference designators from plot.

--ev, --exclude-value

Exclude footprint values from plot.

--ibt, --include-border-title

Include the sheet border and title block.

--sp, --sketch-pads-on-fab-layers

Draw pad outlines and their numbers on front and back fab layers.

--hdnp, --hide-DNP-footprints-on-fab-layers

Don’t plot text and graphics of DNP footprints on fab layers.

--sdnp, --sketch-DNP-footprints-on-fab-layers

Plot graphics of DNP footprints in sketch mode on fab layers.

--cdnp, --crossout-DNP-footprints-on-fab-layers

Plot an "X" over the courtyard of DNP footprints on fab layers, and strikeout their reference designators.

--no-x2

Do not use the extended X2 format.

--no-netlist

Do not include netlist attributes.

--subtract-soldermask

Remove silkscreen from areas without soldermask.

--disable-aperture-macros

Disable aperture macros.

--use-drill-file-origin

Use drill/place file origin instead of absolute origin.

--precision <precision>

The precision (number of digits) for the Gerber files. Valid options are 5 or 6 (default).

--no-protel-ext

Use .gbr file extension instead of Protel file extensions (.gbl, .gtl, etc.).

--check-zones

Check zone fills and refill zones, if required, prior to export. Any zone fill updates are not saved in the board file.

--variant <variant name>

The name of the variant to output. You can use ${VARIANT} in the output path to generate an output filename specific to the variant. When --variant is not used, the default variant is output.

--board-plot-params

Use the Gerber plot settings already configured in the board file.
