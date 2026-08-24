Schematic export: HPGL
kicad-cli sch export hpgl is not functional in KiCad 10.0.
The sch export hpgl command is not functional in KiCad 10.0 as KiCad no longer supports HPGL output. In previous versions of KiCad it exported a schematic to an HPGL file. It is included as a non-functional command for compatibility reasons. It will be removed in a future version of KiCad.

Usage: kicad-cli sch export hpgl [--help] [--output OUTPUT_DIR] [--drawing-sheet SHEET_PATH] [--define-var KEY=VALUE]…​ [--variant VAR] [--theme THEME_NAME] [--black-and-white] [--exclude-drawing-sheet] [--default-font VAR] [--draw-hop-over] [--pages PAGE_LIST] [--pen-size PEN_SIZE] [--origin ORIGIN] INPUT_FILE
