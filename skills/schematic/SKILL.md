# SKILL ON HOW TO WIRE UP OR MODIFY A KICAD SCHEMATIC

## For Humans:

This skill for fully wiring up a schematic after initial IC selection, or modifying subcircuits after

You need to give the agent a good idea of the goal/vision for the schematic. Ideally, you need to provide it with as many relevant datasheets as possible so it doesn't have trouble sourcing them.

## For Agents:

These are instructions on how to wire up a schematic after initial IC selection. If you were asked to choose/find parts (besides passives, oscillators, or similar) and create symbols, start with that.

This skill is not for selecting specific parts/part numbers, and you shouldn't do so if you weren't asked to.

### How to draw the schematic

You can move anything around and label things. Generally, do almost everything with just labels instead of drawing lines.

You should color related nets so they stand out (e.g., SPI1 is one color, I2C2 is another, etc.).

Prefer single-sheet schematics that you can view all at once, even if it means bigger sheets. Break them down into more sheets and hierarchy when repetition is required, stuff starts getting complex, or if user supplied them like that to begin with.

After understanding what subcircuits need to look like in general, put each subcircuit in a simple KiCad rectangle, colored and labeled with brief, bold text somewhere inside it. Prefer big-ish subcircuits that are not too defined. For example, most power supplies can usually be one subcircuit; ICs and their passives/oscillators/etc. can certainly be one subcircuit.

I know for a fact that your skill set is not adequate for wiring cleanly and correctly by just looking/modifying at the schematic file and the netlist that you can export from KiCad.

You need, instead, to iterate based on image input. That means you need to plot high-resolution SVG files of the schematic in KiCad and convert them into images that you can take in as image input and use for what you need. This way you will be able to validate that it is connected correctly and looks right as well.

You still need to look at netlists to deterministically validate connections.

Important things you should be looking for are that all visible properties of components are not overlapping with other things or each other, and that everything is clean and tidy (no overly long wires, etc.).

You need to make it look like it's straight out of a reference schematic for the parts: clean and tidy.

To do that, you will need to modify symbols to make them clean, readable, easy to wire up, and easy to read. But this carries risk: make sure you deterministically check that symbols keep the exact same pins as originally and have the same pin name for each pin number.

You need to use a ton of image input; do not hesitate. Every time it's not clean, you need to make it look good and look at it again. Develop efficient ways to do that at the start of the project so it doesn't cause slowdowns later.

You should also be plotting pictures of subcircuits and more specific things you need to clean up. I know for a fact that you can't take in the whole schematic all at once, so zoom in. Iterate. It has to look clean and functional and be correct.

For passives, use the small KiCad standard symbols.

You will need to modify symbols of ICs to make passives look good.

Wire them up logically next to the component where it makes sense (for example, pull-downs/ups and decoupling). Passives are an exception to the general "use labels instead of lines" rule.

Again, you need to iterate with pictures to make sure they look clean.

For new passives, mostly as placeholders, add footprints from the standard KiCad library (unless otherwise instructed) of a roughly logical size based on the function.

Do use some discretion about what passives should be directly connected to what for aesthetics.

You can't start looking for parts during the schematic wire-up process. If a part was not already given to you and you were not asked to find it, don't look for it.

If you need something like a voltage regulator, an oscillator, or small stuff like that, feel free to create a generic/abstact symbol for one and place it in the self-contained library in this directory (if it exists; otherwise, create one). Then use it. For more complex stuff, you might need to just leave a comprehensive but short note that a whole complex component is missing, continue with the schematic, and mention it briefly at the end as an important item.

### How to do research

Now that you know how to wire up a schematic in KiCad cleanly, we will go over research. These two parts are not separate; you might need to do them together. You can start wiring up subcircuits after researching how, looking at them and how they fit into the general schematic (with pictures and netlists), and then iterating in your research.

You really need to understand the science behind the board, really understand the goal and how everything ties together. Take time for introspection about what the goal is every step of the way. Every time you complete a part, think about it and how it helps the vision for the schematic.

Also, a very quick second step is looking for important datasheets based on the ICs and general vision. If you are missing some datasheets and realize that you really need them, look for them on the internet and try to download them. You might find it hard to get around bot protection; quickly find ways around that and see if you have any other skills available for that purpose as well.

Do not be hesitant to do internet searches to figure stuff out and understand what you need to do. If you have any uncertainty about how something should work, you can use internet search to clear things up.

But the real sources of truth are datasheets and reference material; you can base decisions on these. You will often need to extract information from PDFs, and very often you will need to take shots of pictures in the PDFs. Don't be hesitant to actually use image input to directly look at reference-design pictures or graphs (or other stuff like that) in PDF material. And contiually compare your schematic to the reference.

Once you know enough about how to wire up a subcircuit, you can start bit by bit, always referring to reference material. Be logical and precise, but don't overdo it. That means that you should not overthink decisions. Instead, you should note down all real liberties you took and provide them in a nice, readable, and brief report as part of your answer to the user.

You can take some liberties based on the goal of the project, but they should definitely be mentioned at the end.

For the most part, your job with this skill will be adding adding decoupling, wiring up MCUs to peripherals with legal pin selection for each function, adding oscillators, adding voltage conversion, and filtering if necessary, and other low level work like this. You need to look into reference materials and base your decisions on truths in them. Often you may choose a reference design in them, look at it as a picture, and follow it. But most importantly, you need to be thinking at a high level.

For example, for decoupling, think about derating depending on conditions, DC voltage, etc., and think about upstream circuitry like voltage regulators and switches and how much capacitance they can take.

If you need to do more high-level work than the work described above as "most of your job," you can go ahead, but make sure you understand why it's necessary and do not add a lot of bloat. Always be able to explain your decisions logically without much possibility of dispute, and do explain them in your answer at the end, along with other liberties you took.
