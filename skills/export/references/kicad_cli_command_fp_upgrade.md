Footprint upgrade
The fp upgrade command converts the specified footprint library from a legacy KiCad footprint format or a non-KiCad footprint format to the native format for the current version of KiCad. If the input library is already in the current file format, no action is taken.

Supported input footprint formats are:

KiCad footprint library (.pretty folder with .kicad_mod files)

KiCad (pre-5.0) footprint library (.mod, .emp)

Altium footprint library (.PcbLib)

Altium integrated library (.IntLib)

CADSTAR PCB archive (.cpa)

EAGLE XML library (.lbr)

EasyEDA (JLCEDA) Std file (.json)

EasyEDA (JLCEDA) Pro file (.elibz, .epro, .zip)

GEDA/PCB library (folder with .fp files)

Usage: kicad-cli fp upgrade [--help] [--output OUTPUT_DIR] [--force] INPUT_FILE_OR_DIR

Positional arguments:

INPUT_FILE_OR_DIR

Footprint or footprint library directory to upgrade. For KiCad format footprint libraries, this can be a footprint (.kicad_mod file) or a footprint library (.pretty directory containing .kicad_mod files).

Optional arguments:

-h, --help

Show help for the upgrade command.

-o <output dir>, --output <output dir>

The output directory for the upgraded footprints. When --output is not used, the upgraded footprints are saved over the original footprints.

--force

Re-save the input library even if it is already in the current file format.
