---
name: kicad-symbol
description: Generate compliant KiCad symbols
---

# This skill allows an LLM to generate KiCad symbols using a variety of data sources, validated against KLC standards.

## Setup
Clone the https://gitlab.com/kicad/libraries/klc standard. This includes a means of checking if a symbol is KLC compliant. In some cases, it is acceptable to be non-compliant but this should be the way, the truth, and the light for looping to create a compliant symbol. https://gitlab.com/kicad/libraries/kicad-library-tools can also be used to generate symbols if necessary, but this may not be a requirement.

## Usage

- If available, use easyeda2kicad for ground truth pin table. If this is not available, that's okay, but ask the user to install it. This takes an LCSC part number and returns a symbol if available.
- If this doesn't help, look for the pin table in HTML format. If this fails, get an image of the pin table from a PDF and convert it there. These methods require the user to approve the pin table so please ask them to review it!
- Use proper text formatting, pin formatting, and pin type. If there are alternate values for a pin, make sure you use alternates with proper pin type instead of creating a long list delimited with slashes! KiCad supports bars with ~{FOO} syntax, underscores with _{BAR}, and superscripts with ^{BAZ}.
- Per KLC, keep inputs on the left, outputs on the right, grounds on the bottom, NC pins invisible and on outline of symbol, power pins on top. This isn't a hard and fast set of rules honestly but it's helpful.
- Combine/stack pins whenever possible! Do not use legacy stacking, create a proper pin group that displays these pin number groups.
- Render the symbol as an image to confirm that it looks correct. kicad-cli should be able to assist here.
- Pins that are internally connected should be handled properly as well as a jumper group.
- If a symbol you need to embed in a schematic (see $kicad-schematic) uses `(extends "Base")` inheritance — common in vendor-generated multi-variant libraries like KiCad's own `MCU_ST_*` families — it cannot be pasted into a schematic's `lib_symbols` block as-is; the schematic needs a fully resolved, standalone symbol. Flatten it first: parse both the derived symbol and its base, take the derived symbol's own property overrides (Reference/Value/Footprint/Datasheet/etc., keeping the base's order and falling back to the base's value where the derived symbol doesn't override), then copy the base's non-property/non-`extends` items (graphics, sub-unit symbols) renamed from `<Base><suffix>` to `<NewName><suffix>`. A ~150-line hand-rolled S-expression tokenizer/parser is enough for this — KiCad's own S-expressions are simple enough not to need a real parser library. Always re-render the flattened result with `kicad-cli sym export svg` and check the pin count/labels match the original before trusting it.
- Get the pin *electrical type* right, not just the name/number/position — it's easy to default an interrupt or status pin to `output` when the datasheet actually specifies open-drain. Caught one on a hand-authored I/O-expander symbol: its INT pin was typed `output`, and wiring it to another chip's genuinely open-drain alert pin on the same net produced an ERC `pin_to_pin` type-conflict warning that pointed straight at the mistake. If ERC flags a pin-to-pin type conflict on a custom symbol, check the real datasheet's pin description table before assuming the wiring is wrong — the symbol's declared type may be the actual bug.
