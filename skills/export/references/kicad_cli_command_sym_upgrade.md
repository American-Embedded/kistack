Symbol upgrade
The sym upgrade command converts the specified symbol library from a legacy KiCad symbol format or a non-KiCad symbol format to the native format for the current version of KiCad. If the input library is already in the current file format, no action is taken.

Supported input symbol formats are:

KiCad symbol library (.kicad_sym)

KiCad (pre-6.0) symbol library (.lib)

Altium schematic library (.SchLib)

Altium integrated library (.IntLib)

CADSTAR parts library (.lib)

EAGLE XML library (.lbr)

EasyEDA (JLCEDA) Std file (.json)

EasyEDA (JLCEDA) Pro file (.elibz, .epro, .zip)

Usage: kicad-cli sym upgrade [--help] [--output OUTPUT_FILE_OR_DIR] [--force] INPUT_FILE_OR_DIR

Positional arguments:

INPUT_FILE_OR_DIR

Symbol or symbol library to upgrade. This can be an unpacked symbol (.kicad_sym file containing a single symbol), an unpacked symbol library (folder containing .kicad_sym files), or a packed symbol library (.kicad_sym file containing multiple symbols).

Optional arguments:

-h, --help

Show help for the upgrade command.

-o <output file or directory>, --output <output file or directory>

The output file or directory for the upgraded symbol library. When the output path is a file, the symbols are saved as a single-file ("packed") .kicad_sym library. When the output path is a folder, the symbols are saved as individual ("unpacked") .kicad_sym files in the folder, with one file per symbol. When --output is not used, the upgraded symbol library is saved over the original library.

--force

Re-save the input library even if it is already in the current file format.
