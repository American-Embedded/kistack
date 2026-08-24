PCB export: drill file
The pcb export drill command exports a drill file from a board.

Usage: kicad-cli pcb export drill [--help] [--output OUTPUT_DIR] [--format FORMAT] [--drill-origin DRILL_ORIGIN] [--excellon-zeros-format ZEROS_FORMAT] [--excellon-oval-format OVAL_FORMAT] [--excellon-units UNITS] [--excellon-mirror-y] [--excellon-min-header] [--excellon-separate-th] [--generate-map] [--generate-report] [--report-path REPORT_FILE] [--generate-tenting] [--map-format MAP_FORMAT] [--gerber-precision VAR] INPUT_FILE

Positional arguments:

INPUT_FILE

Board file to export.

Optional arguments:

-h, --help

Show help for the drill file export command.

-o <output dir>, --output <output dir>

The output directory for the drill file(s). When --output is not used, the drill file(s) are saved in the current directory.

--format <format>

The drill file format. Options are excellon (default) or gerber.

--drill-origin <origin>

The coordinate origin for the drill file. Options are absolute (default) to use the board’s absolute origin or plot to use the board’s drill/placement origin.

--excellon-zeros-format <format>

The zeros format for the drill file. Options are decimal (default), suppressleading, suppresstrailing, or keep. Only applies to Excellon format drill files.

--excellon-oval-format <format>

Control the oval holes drill mode. Options are route and alternate (default). Only applies to Excellon format drill files.

-u <units>, --excellon-units <units>

The units for the drill file. Options are mm (default) or in. Only applies to Excellon format drill files.

--excellon-mirror-y

Mirror the drill file in the Y direction. Only applies to Excellon format drill files.

--excellon-min-header

Use a minimal header in the drill file. Only applies to Excellon format drill files.

--excellon-separate-th

Generate separate drill files for plated and non-plated through holes. Only applies to Excellon format drill files.

--generate-map

Generate a map file in addition to the drill file.

--generate-report

Generate a report file listing all drill hits.

--report-path <report filename>

The output filename for the drill report file. When --report-path is not used, the report filename will be the same as the input file, with the -drill.rpt suffix and file extension.

--generate-tenting

Generate separate drill files for tented drill hits. Only applies to Gerber X2 format drill files.

--map-format <format>

The map file format. Options are pdf (default), gerberx2, ps, dxf, or svg.

--gerber-precision <precision>

The precision (number of digits) for the drill file. Valid options are 5 or 6 (default). Only applies to Gerber format drill files.
