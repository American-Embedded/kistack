Schematic upgrade
The sch upgrade command converts a KiCad schematic file from a previous KiCad schematic file format to the native format for the current version of KiCad. If the input schematic file is already in the current file format, no action is taken.

Only the specified schematic file is upgraded. If the schematic file contains any child sheets, the child sheets are not upgraded.
Usage: kicad-cli sch upgrade [--help] [--force] INPUT_FILE

Positional arguments:

INPUT_FILE

Schematic file to upgrade.

Optional arguments:

-h, --help

Show help for the upgrade command.

--force

Re-save the input schematic file even if it is already in the current file format.
