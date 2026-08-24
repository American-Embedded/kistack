Schematic commands
The sch command runs an electrical rule check, exports a schematic to various other file formats, or exports a bill of materials or netlist. Each subcommand has its own options.

Schematic ERC
The sch erc command runs an electrical rule check on a schematic and generates a report.

Usage: kicad-cli sch erc [--help] [--output OUTPUT_FILE] [--define-var KEY=VALUE]…​ [--format VAR] [--units VAR] [--severity-all] [--severity-error] [--severity-warning] [--severity-exclusions] [--exit-code-violations] INPUT_FILE

Positional arguments:

INPUT_FILE

Schematic file to run ERC on.

Optional arguments:

-h, --help

Show help for the ERC command.

-o <output filename>, --output <output filename>

Output filename for the generated ERC report. When --output is not used, the output filename will be the same as the input file, with the .rpt or .json file extension, depending on the selected format.

-D <variable name>=<value>, --define-var <variable_name>=<value>

Add or override project variable definitions. Can be used multiple times to define multiple variables.

--format <format>

Report file format. Options are report (default) or json.

--units <unit>

Units to use in the report. Options are mm (default), in, or mils.

--severity-all

Report all ERC violations. This is equivalent to using all of the other ERC severity options.

--severity-error

Report all error-level ERC violations. This can be combined with the other ERC severity options.

--severity-warning

Report all warning-level ERC violations. This can be combined with the other ERC severity options.

--severity-exclusions

Report all excluded ERC violations. This can be combined with the other ERC severity options.

--exit-code-violations

Return an exit code depending on whether or not ERC violations exist. The exit code is 0 if no violations are found, and 5 if any violations are found.
