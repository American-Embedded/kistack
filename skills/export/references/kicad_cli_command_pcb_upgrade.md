PCB upgrade
The pcb upgrade command converts a KiCad board file from a previous KiCad board file format to the native format for the current version of KiCad. If the input board file is already in the current file format, no action is taken.

Usage: kicad-cli pcb upgrade [--help] [--force] INPUT_FILE

Positional arguments:

INPUT_FILE

Board file to upgrade.

Optional arguments:

-h, --help

Show help for the upgrade command.

--force

Re-save the input board file even if it is already in the current file format.
