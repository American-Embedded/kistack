Footprint commands
The fp subcommand exports footprints to another format or upgrades the footprint libraries to the current version of the KiCad footprint file format.

Footprint export
The fp export svg command exports one or more footprints from the specified library into SVG files.

Usage: kicad-cli fp export svg [--help] [--output OUTPUT_DIR] [--layers LAYER_LIST] [--define-var KEY=VALUE]…​ [--theme VAR] [--footprint FOOTPRINT_NAME] [--sketch-pads-on-fab-layers] [--hide-DNP-footprints-on-fab-layers] [--sketch-DNP-footprints-on-fab-layers] [--crossout-DNP-footprints-on-fab-layers] [--black-and-white] INPUT_FILE_OR_DIR

Positional arguments:

INPUT_FILE_OR_DIR

Footprint (.kicad_mod) or footprint library directory (.pretty) to export.

Optional arguments:

-h, --help

Show help for the footprint SVG export command.

-o <output dir>, --output <output dir>

The output folder for the exported files. One file is output for each layer of each footprint in the library. When --output is not used, the files are exported to the current directory.

-l <layer list>, --layers <layer list>

A comma-separated list of layer names to export from the footprint, such as F.Cu,B.Cu. If no layers are given, all layers are exported. Layer names can be specified as canonical layer names (F.Cu, In.1, F.Fab, etc.) or as user-defined (custom) layer names, but user-defined layer names are matched first.

-D <variable name>=<value>, --define-var <variable_name>=<value>

Add or override project variable definitions. Can be used multiple times to define multiple variables.

-t <theme name>, --theme <theme name>

The name of the theme to use for export. If no theme is given, the footprint editor’s currently selected theme is used.

--fp <footprint>, --footprint <footprint>

The name of the specific footprint to export from the library. When this argument is not used, all footprints in the library are exported.

--sp, --sketch-pads-on-fab-layers

Draw pad outlines and their numbers on front and back fab layers.

--hdnp, --hide-DNP-footprints-on-fab-layers

Don’t plot text and graphics of DNP footprints on fab layers.

--sdnp, --sketch-DNP-footprints-on-fab-layers

Plot graphics of DNP footprints in sketch mode on fab layers.

--cdnp, --crossout-DNP-footprints-on-fab-layers

Plot an "X" over the courtyard of DNP footprints on fab layers, and strikeout their reference designators.

--black-and-white

Export footprints in black and white.
