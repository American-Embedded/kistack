Symbol commands
The sym subcommand exports symbols to another format or upgrades symbol libraries to the current version of the KiCad symbol file format.

Symbol export
The sym export svg command exports one or more symbols from the specified library into SVG files.

Usage: kicad-cli sym export svg [--help] [--output OUTPUT_DIR] [--theme THEME_NAME] [--symbol SYMBOL] [--black-and-white] [--include-hidden-pins] [--include-hidden-fields] INPUT_FILE

Positional arguments:

INPUT_FILE

Symbol library file to use for export.

Optional arguments:

-h, --help

Show help for the symbol SVG export command.

-o <output dir>, --output <output dir>

The output folder for the exported files. Each symbol in the input library is output to a separate file. When --output is not used, the files are exported to the current directory.

-t <theme name>, --theme <theme name>

The name of the theme to use for export. If no theme is given, the symbol editor’s currently selected theme is used.

-s <symbol name>, --symbol <symbol name>

The specific symbol to export from the library. When this argument is not used, all symbols in the library are exported.

--black-and-white

Export symbols in black and white.

--include-hidden-pins

Export hidden pins in the exported SVG.

--include-hidden-fields

Export hidden symbol fields in the exported SVG.
