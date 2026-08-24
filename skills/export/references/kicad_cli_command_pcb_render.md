PCB render
The pcb render command generates a raytraced rendering of the 3D model of the board and saves it to a PNG or JPEG file.

Usage: kicad-cli pcb render [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--variant VAR] [--width WIDTH] [--height HEIGHT] [--side SIDE] [--background BG] [--quality QUALITY] [--preset PRESET] [--use-board-stackup-colors VAR] [--floor] [--perspective] [--zoom ZOOM] [--pan VECTOR] [--pivot PIVOT] [--rotate ANGLES] [--light-top COLOR] [--light-bottom COLOR] [--light-side COLOR] [--light-camera COLOR] [--light-side-elevation ANGLE] INPUT_FILE

Positional arguments:

INPUT_FILE

Board file to render.

Optional arguments:

-h, --help

Show help for the render command.

-o <output filename>, --output <output filename>

The output filename. This argument must be given. The file extension given in this argument determines the output image file format. The filename must end with either .png (for PNG files) or .jpg/.jpeg (for JPG files).

-D <variable name>=<value>, --define-var <variable_name>=<value>

Add or override project variable definitions. Can be used multiple times to define multiple variables.

--variant <variant name>

The name of the variant to output. You can use ${VARIANT} in the output path to generate an output filename specific to the variant. When --variant is not used, the default variant is output.

-w <width>, --width <width>

Image width in pixels. Default: 1600.

-h <height>, --height <height>

Image height in pixels. Default: 900.

--side <side>

The side of the board to render. Options are top (default), bottom, left, right, front, or back.

--background <background>

Image background. Options are default (default), transparent, or opaque. For PNG files, default is transparent. For JPG files, default is opaque.

--quality <quality>

Render quality. Options are basic (default), high, user. When user is specified, the render settings stored in the project are used.

--preset <color preset>

Color preset. Options are follow_pcb_editor, follow_plot_settings (default), or legacy_preset_flag.

--use-board-stackup-colors

Colors defined in the board stackup override colors from the preset.

--floor

Enables floor, shadows and post-processing, even if disabled in quality preset.

--perspective

Use perspective projection instead of orthogonal.

--zoom <zoom level>

Camera zoom factor as an integer. Default: 1.

--pan <camera pan>

Set camera pan location, in millimeters, with the format 'X,Y,Z', e.g. '3,0,0'.

--pivot <pivot>

Set pivot point relative to the board center in centimeters, with the format 'X,Y,Z' e.g. '-10,2,0'.

--rotate <rotation>

Set board rotation around pivot point, in degrees, with the format 'X,Y,Z', e.g. '-45,0,45' for isometric view.

--light-top <intensity>

Top light intensity, format 'R,G,B' or a single number, range: 0-1.

--light-bottom <intensity>

Bottom light intensity, format 'R,G,B' or a single number, range: 0-1.

--light-side <intensity>

Side lights intensity, format 'R,G,B' or a single number, range: 0-1.

--light-camera <intensity>

Camera light intensity, format 'R,G,B' or a single number, range: 0-1.

--light-side-elevation <elevation>

Side lights elevation angle in degrees, range: 0-90.
