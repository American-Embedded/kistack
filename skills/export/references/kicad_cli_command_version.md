Version commands
The version command prints the KiCad version. Without any arguments, it simply prints the version number, for example 7.0.7. You can print the version in several other formats using the --format argument.

Use kicad-cli version --format about for version information to include when submitting bug reports or feature requests on Gitlab.
Usage: kicad-cli version [--help] [--format VAR]

Optional arguments:

-h, --help

Show help for the version command.

--format <format>

Format of the version number. Options are plain (default), commit, or about. plain prints the version number (e.g. 7.0.7), which is the default if the --format argument is not used. commit prints the hash of the git commit for the build of KiCad you are using. about prints the full version information, including library versions and basic system information. You can use the about version information in bug reports.
