PCB export: U3D
The pcb export u3d command exports a board design to a PDF file containing an embedded 3D model of the board.

Usage: kicad-cli pcb export u3d [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--force] [--no-unspecified] [--no-dnp] [--variant VAR] [--grid-origin] [--drill-origin] [--subst-models] [--board-only] [--cut-vias-in-body] [--no-board-body] [--no-components] [--component-filter VAR] [--include-tracks] [--include-pads] [--include-zones] [--include-inner-copper] [--include-silkscreen] [--include-soldermask] [--fuse-shapes] [--fill-all-vias] [--no-extra-pad-thickness] [--min-distance MIN_DIST] [--net-filter VAR] [--user-origin VAR] INPUT_FILE

Positional arguments:

INPUT_FILE

Board file to export.

Optional arguments:

-h, --help

Show help for the 3D PDF export command.

-o <output filename>, --output <output filename>

The output filename. When --output is not used, the output filename will be the same as the input file, with the .pdf file extension.

-D <variable name>=<value>, --define-var <variable_name>=<value>

Add or override project variable definitions. Can be used multiple times to define multiple variables.

-f, --force

Overwrite output file.

--no-unspecified

Exclude 3D models of components with "unspecified" footprint type.

--no-dnp

Exclude 3D models of components with "Do not populate" attribute.

--variant <variant name>

The name of the variant to output. You can use ${VARIANT} in the output path to generate an output filename specific to the variant. When --variant is not used, the default variant is output.

--grid-origin

Use grid origin as origin of output file.

--drill-origin

Use drill origin as origin of output file.

--subst-models

Replace VRML models in footprints with STEP or IGS models of the same name, if they exist.

--board-only

Only include the board itself in the generated model; exclude all component models.

--cut-vias-in-body

Cut via holes in board body even if conductor layers are not exported.

--no-board-body

Exclude board body.

--no-components

Exclude 3D models for components.

--component-filter <reference designator list>

Only include component 3D models matching this list of reference designators (comma-separated, wildcards supported)

--include-tracks

Include tracks and vias on outer conductor layers in export (time consuming).

--include-pads

Include pads in export (time consuming).

--include-zones

Include zones in export (time consuming).

--include-inner-copper

Include elements on inner conductor layers in export.

--include-silkscreen

Include silkscreen graphics in export as a set of flat faces.

--include-soldermask

Include solder mask layers in export as a set of flat faces.

--fuse-shapes

Fuse overlapping geometry together in export (time consuming).

--fill-all-vias

Don’t cut via holes in conductor layers.

--no-extra-pad-thickness

Disable adding additional metal thickness to pads. When not used, pads have 0.005mm added to their metal thickness, which causes pads to be separate faces in the exported model, distinct from the surrounding metal.

--min-distance <min distance>

Tolerance for considering two points to be in the same location. Default: 0.01mm.

--net-filter <net filter>

Only include copper items belonging to nets matching this wildcard.

--user-origin <output origin>

Specify a custom origin for the output file, with X and Y coordinates. For example, 1x1in, 1x1inch, or 25.4x25.4mm. The default unit is millimeters.
