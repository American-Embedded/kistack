PCB export: PostScript
The pcb export ps command exports a board design to a PostScript file.

Usage: kicad-cli pcb export ps [--help] [--output OUTPUT_DIR] [--layers LAYER_LIST] [--common-layers COMMON_LAYER_LIST] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--mirror] [--exclude-refdes] [--exclude-value] [--include-border-title] [--subtract-soldermask] [--sketch-pads-on-fab-layers] [--hide-DNP-footprints-on-fab-layers] [--sketch-DNP-footprints-on-fab-layers] [--crossout-DNP-footprints-on-fab-layers] [--negative] [--black-and-white] [--theme THEME_NAME] [--drill-shape-opt VAR] [--mode-single] [--mode-multi] [--track-width-correction TRACK_COR] [--x-scale-factor X_SCALE] [--y-scale-factor Y_SCALE] [--force-a4] [--scale SCALE] [--check-zones] [--variant VAR] INPUT_FILE

Positional arguments:

INPUT_FILE

Board file to export.

Optional arguments:

-h, --help

Show help for the PS export command.

-o <output dir>, --output <output dir>

The output folder or filename for the exported files. When --mode-single is used, this is the output filename. If --output is not used, the output filename will be the same as the input file, with the .ps file extension. When --mode-multi is used, this is the output directory. If --output is not used, the files are exported to the current directory.

-l <layer list>, --layers <layer list>

A comma-separated list of layer names to export from the board, such as F.Cu,B.Cu. At least one layer must be given. Layer names can be specified as canonical layer names (F.Cu, In.1, F.Fab, etc.) or as user-defined (custom) layer names, but user-defined layer names are matched first.

--cl <layer list>, --common-layers <layer list>

A comma-separated list of layer names to plot on all layers, such as F.Cu,B.Cu. Each layer specified is included in every output file. Layer names can be specified as canonical layer names (F.Cu, In.1, F.Fab, etc.) or as user-defined (custom) layer names, but user-defined layer names are matched first.

--drawing-sheet <sheet path>

Path to drawing sheet to use in plot, overriding the drawing sheet specified in the board file.

-D <variable name>=<value>, --define-var <variable_name>=<value>

Add or override project variable definitions. Can be used multiple times to define multiple variables.

-m, --mirror

Mirror the board. This can be useful for showing bottom layers.

--erd, --exclude-refdes

Exclude footprint reference designators from plot.

--ev, --exclude-value

Exclude footprint values from plot.

--ibt, --include-border-title

Include the sheet border and title block.

--subtract-soldermask

Remove silkscreen from areas without soldermask.

--sp, --sketch-pads-on-fab-layers

Draw pad outlines and their numbers on front and back fab layers.

--hdnp, --hide-DNP-footprints-on-fab-layers

Don’t plot text and graphics of DNP footprints on fab layers.

--sdnp, --sketch-DNP-footprints-on-fab-layers

Plot graphics of DNP footprints in sketch mode on fab layers.

--cdnp, --crossout-DNP-footprints-on-fab-layers

Plot an "X" over the courtyard of DNP footprints on fab layers, and strikeout their reference designators.

-n, --negative

Plot in negative.

--black-and-white

Plot in black and white.

-t <theme name>, --theme <theme name>

The name of the theme to use for export. If no theme is given, the board editor’s currently selected theme is used.

--drill-shape-opt

The shape of drill marks in the plot. Options are 0 for no drill marks, 1 for small marks, or 2 for actual size marks (default).

--mode-single

Generates a single file with the output arg path acting as the complete directory and filename path. COMMON_LAYER_LIST does not function in this mode. Instead LAYER_LIST controls all layers plotted.

--mode-multi

Plot the layers to one or more PS files, with each file representing a single layer from LAYER_LIST. The output path specifies the directory in which the files will be written.

-C, --track-width-correction

A global correction, in millimeters, that is added to the size of tracks, vias, and pads when plotted. This correction can be used to correct for errors in the PostScript output device to achieve an exact-scale output.

-X, --x-scale-factor

X scale adjust for exact scale.

-Y, --y-scale-factor

Y scale adjust for exact scale.

-A, --force-a4

Force A4 paper size.

--scale <scale>

A scaling factor to use for plotting the PCB. The border and title block are not scaled. A scale factor of 0 autoscales the plot.

--check-zones

Check zone fills and refill zones, if required, prior to export. Any zone fill updates are not saved in the board file.

--variant <variant name>

The name of the variant to output. You can use ${VARIANT} in the output path to generate an output filename specific to the variant. When --variant is not used, the default variant is output.
