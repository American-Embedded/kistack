# Skill for part search, resolving BOM items

Use either of the following MCPs for search:
- https://pcbparts.dev/mcp
- https://api.zenode.ai/mcp/

If either of the MCPs are not installed, prompt the user to install at least one before proceeding.

Search for parts that meet actual requirements of the PCB. Use other skills that are available to you to determine if proposed parts will work electrically and mechanically.

If the user has not yet specified a package size for a certain part, please prompt them before proceeding.

For ceramic capacitors, ensure that their values for applied DC voltage are adequately derated, that dielectric temp spec is checked, and that the package sizes assigned per device are respected. If in an audio application, ensure that we are not using a dielectric that is likely to vibrate.

For resistors, ensure that their power rating is proper for the applied pwoer. If used in a sensitive application, use thin-film resistors for lower noise as a rule. 

For inductors, prefer those that have existing footprints in KiCad if at all possible. Since many inductors are not as standardized, please confirm with the user the value, current, saturation current, DCR, etc to assist in selecting footprint. If the footprint already exists, please find one that matches.

In the case of RF matching components, please use C0G/NP0 capacitors and high-Q inductors.

In many cases, ICs will have only one or a handful of compatible part numbers. Ensure that part numbers are respected. If only a snippet of the part number is set in the value field of the schematic, please validate the other attributes available for this part and prompt the user to decide on a full part number.

BOM standards for JLC, PCBWay, NextPCB, etc. are different from default KiCad formats. If the BOM presets are not prepared properly, please refer the user to https://github.com/i2cjak/American_Embedded_KiCad_Template that has these presets built-in.

This can be used for these manufacturers.

  ### JLCPCB

   Output column         KiCad field              Show    Group by
  ━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━  ━━━━━━━━━━
   Comment               Value                     Yes         Yes
  ────────────────────  ───────────────────────  ──────  ──────────
   Designator            Reference                 Yes         Yes
  ────────────────────  ───────────────────────  ──────  ──────────
   Qty                   ${QUANTITY}                No          No
  ────────────────────  ───────────────────────  ──────  ──────────
   MPN                   MPN                        No         Yes
  ────────────────────  ───────────────────────  ──────  ──────────
   Manufacturer          Manufacturer               No          No
  ────────────────────  ───────────────────────  ──────  ──────────
   Footprint             Footprint                 Yes         Yes
  ────────────────────  ───────────────────────  ──────  ──────────
   Description           Description                No          No
  ────────────────────  ───────────────────────  ──────  ──────────
   DNP                   ${DNP}                     No         Yes
  ────────────────────  ───────────────────────  ──────  ──────────
   Exclude from BOM      ${EXCLUDE_FROM_BOM}        No         Yes
  ────────────────────  ───────────────────────  ──────  ──────────
   Exclude from Board    ${EXCLUDE_FROM_BOARD}      No         Yes
  ────────────────────  ───────────────────────  ──────  ──────────
   Datasheet             Datasheet                  No          No
  ────────────────────  ───────────────────────  ──────  ──────────
   Item number           ${ITEM_NUMBER}             No          No
  ────────────────────  ───────────────────────  ──────  ──────────
   Customer Note         Customer Note              No          No
  ────────────────────  ───────────────────────  ──────  ──────────
   LCSC                  LCSC                      Yes          No

  Preset settings:

  {
    "name": "JLCPCB",
    "exclude_dnp": false,
    "group_symbols": true,
    "include_excluded_from_bom": true,
    "sort_asc": true,
    "sort_field": "Value",
    "filter_string": ""
  }

Ensure that the BOM can be generated from the KiCad files. As a rule, NEVER edit the BOM files themselves outside of formatting. If a part number must change, you must absolutely modify the value in the schematic.

If possible, add to schematic symbols an MPN, Manufacturer, and LCSC number. With the exact fields, not creating new fields.
