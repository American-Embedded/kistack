Jobset commands
The jobset run command runs a predefined jobset.

Usage: kicad-cli jobset run [--help] [--stop-on-error] [--file JOB_FILE] [--output OUTPUT] INPUT_FILE

Positional arguments:

INPUT_FILE

Project file to use with the jobset.

Optional arguments:

-h, --help

Show help for the jobset command.

--stop-on-error

As jobs are executed in sequence, stop running after a job fails. If not given, jobs will continue executing after any job fails.

-f <jobset file>, --file <jobset file>

The jobset file (.kicad_jobset) to run.

--output <destination description or ID>

The jobset destination to generate. If no destination is specified, all destinations will be generated.

The destination is specified by its description or by its unique ID. The specified description must be unique; if the jobset contains more than one destination with the given description, none of them will be run.

IDs are inherently unique and can be used to refer to a destination even if the destination’s description is not unique. The ID for each destination is printed by the jobset run command when --output is not used. It can also be found in the .kicad_jobset file under the destination’s id key.
