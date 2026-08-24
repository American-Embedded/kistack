Schematic export: bill of materials
The sch export bom command exports a BOM from a schematic. The BOM export has a number of options for controlling the format and included fields. This export method is equivalent to exporting a BOM from the symbol fields table.

To export a BOM using the legacy XML and Python BOM script workflow, use the sch export python-bom command.
Usage: kicad-cli sch export bom [--help] [--output OUTPUT_FILE] [--variant VAR] [--preset PRESET] [--format-preset FMT_PRESET] [--fields FIELDS] [--labels LABELS] [--group-by GROUP_BY] [--sort-field SORT_BY] [--sort-asc VAR] [--filter FILTER] [--exclude-dnp] [--include-excluded-from-bom] [--field-delimiter FIELD_DELIM] [--string-delimiter STR_DELIM] [--ref-delimiter REF_DELIM] [--ref-range-delimiter REF_RANGE_DELIM] [--keep-tabs] [--keep-line-breaks] INPUT_FILE

Positional arguments:

INPUT_FILE

Schematic file to export.

Optional arguments:

-h, --help

Shows help message and exits

-o <output filename>, --output <output filename>

The output filename. When --output is not used, the output filename will be the same as the input file, with a .csv file extension.

--variant <variant name>

The name of the variant to output. You can use ${VARIANT} in the output path to generate an output filename specific to the variant. When --variant is not used, the default variant is output.

--preset <preset>

Use a named BOM preset setting from the schematic, e.g. "Grouped By Value".

--format-preset <format preset>

Use a named BOM format preset setting from the schematic, e.g. CSV.

--fields <fields>

An ordered list of fields to export. * includes all fields. Virtual BOM symbol fields such as DNP or Exclude from board can be accessed with ${DNP} or ${EXCLUDE_FROM_BOARD}, respectively (see the BOM export documentation for a list of fields). These fields can be specified in this argument with or without the ${} syntax. Default: "Reference,Value,Footprint,QUANTITY,DNP".

--labels <labels>

An ordered list of labels to apply the exported fields (default: "Refs,Value,Footprint,Qty,DNP").

--group-by <fields>

Fields to group references by when field values match.

--sort-field <fields>

Field name to sort by (default: "Reference").

--sort-asc

If given, sort in ascending order. If not given, sort in descending order.

--filter <filter>

If given, only components with reference designators that match the given filter string are included in the output. The filter supports wildcards: * matches any number of any characters, including none, and ? matches any single character.

--exclude-dnp

Exclude symbols with the "Do not populate" attribute.

--include-excluded-from-bom

Include symbols marked "Exclude from BOM". This argument is deprecated as of KiCad 10.0 and has no effect.

--field-delimiter <delimiter>

Separator between output fields/columns (default: ",").

--string-delimiter <delimiter>

Character to surround fields with (none by default).

--ref-delimiter <delimiter>

Character to place between individual references (default: ",").

--ref-range-delimiter <delimiter>

Character to place in ranges of references (default: "-"). Leave blank for no ranges.

--keep-tabs

Keep tab characters from input fields. Stripped by default.

--keep-line-breaks

Keep line break characters from input fields. Stripped by default.
