# layout-placement provenance

## Source

The Nordic PCB placement skill lab's frozen v18, handed off as
`layout-placement-v18.tar.gz`
(sha256 `39c00c45e66b1ba6938fa3b84cfcab13268776b7f2345d86c4b581936d796a54`).
Its files match the lab's `skills/snapshots/v18.sha256`:

```
edbb639cf71645eec2e7188679f5476d6f90219b273754fe1d7e7a27d3a60c1a  SKILL.md
f37c85f7aae992774acc4c6dd47212e35002aef2928c9368b6dfa0eda5acf330  scripts/grid_router.py
e112d192b135bb57d58b8126f0ed22a718e4c198107535ffe0f65b7c130a1b18  scripts/group_search.py
ad83535e93d463b38a46cae2af295cf24d9d5af7e471090f313149cfa363d532  scripts/ipc_board.py
3bb282dcd7cf3190304669b847e9ebda48e53480dfe6ef83c73493f8d06d51a7  scripts/local_search.py
f3ae39bc67909101f2acc005247dab3d59959b6240845d2e940a9322e7658a2a  scripts/move.py
69615a716533804d28a2f524016c222eda873ae9ceaf8fe1d6f33ddae7be9f24  scripts/pin_sides.py
7bec7b9dedde6aa80fb6fef38babbf6e6f3855d90c8ac9297c535981ad5e108a  scripts/placement_audit.py
75dd0f805adb01706bda27552698c5e2e53f9b3812aef8b37188400f03702ec5  scripts/route_check.py
```

In KiStack's history the commit "import layout-placement v18 ... unchanged"
holds exactly these files, and the commit after it holds every change below.

## What the lab measured

The lab's handoff reports these results for v18 (copied from the handoff
brief, not checked again here). They come from a few small Nordic QFN
benchmark boards, with the lab's own evaluators, and are not a fresh-model
comparison or an untouched holdout:

- with the v1.5 evaluator (links and DRC checked together), two of two runs
  on the nRF54L15 board (gpt-6.1-sol) passed;
- the older v1.1 to v1.3 evaluators fail one link on that board;
- the nRF54LS05B validation board misses one escape.

Nothing in this copy was measured again. The changes below are packaging,
safety and wording. They do not requalify the skill's placement results.

## Changes in this copy

Scripts:

- `rules.py` (new): track width, clearance, via diameter and edge clearance
  come from the flags, else from the board's `.kicad_pro` (Default net class
  and `min_copper_edge_clearance`). A value found in neither stops the
  script. v18 had 0.15 / 0.1 / 0.5 / 0.2 mm built in. On a board with those
  rules, `route_check.py` and `placement_audit.py` print exactly what v18
  printed (tested).
- `grid_router.py`: the rules are the `Witness`'s, from `rules.py`. The
  unused `via_site_gap`, which had the built-in rules, is gone.
- `route_check.py`, `placement_audit.py`, `local_search.py`,
  `group_search.py`: the rules flags and `rules.py`; a clear error for a
  part that is not on the board; `route_check.py` states its scope and what
  an escape failing in both orders means.
- `ipc_board.py`: the board must be the one the nearest `.backplane.json`
  names (`LAYOUT_PLACEMENT_ALTERNATE=1` allows another when the user asked
  for one); exactly one server may have it open; a `KICAD_API_SOCKET`
  server with another board is refused; Backplane's sockets are looked for
  under `$XDG_RUNTIME_DIR/backplane/kicad` and `<Backplane home>/run/kicad`
  (macOS) as well as `/run/user/<uid>/backplane/kicad`.
- `move.py`: arguments checked before any request; KiCad's answer for each
  part compared with the request, and the commit dropped when they differ;
  after the commit, a failed integrity check (footprint count, fixed copper
  nets, moved parts read back) puts the parts back in a second commit
  instead of leaving them moved; non-zero exit whenever the board was not
  changed as asked; says whether it saved. v18 pushed the commit and then
  only told the agent to undo it.
- `run.sh` (new), `requirements.in`, `requirements.txt` (new): a private
  Python environment with exact versions and hashes, the versions the lab
  tested (kicad-python 0.8.0, shapely 2.2.0, numpy 2.5.4, protobuf 5.29.6;
  Python 3.12 or newer).

SKILL.md:

- a status paragraph with these limits; a section on the rules and scope
  the checks assume; how to run the scripts and what they refuse;
- "Two cases" had three; it now says three, and long paragraphs are split;
- wording scoped where v18 stated a rule more widely than it holds: the
  switching loop by topology (buck, boost) as the datasheet names it rather
  than "input cap, switch and inductor"; the smallest decoupler closest
  "usually, unless the vendor orders them otherwise"; a via site for ground
  pads that return through a via, and the vendor's ground and layer
  arrangement otherwise; crystal balance preferred when it costs little
  length rather than always; pull-ups anywhere only on slow or static nets;
  no ferrite or other part the schematic does not have;
- what to do when an escape fails in both orders: unresolved, try a
  physical alternative, confirm the rules, and report it, rather than
  calling the board unroutable.

Tests (not part of the skill): `tests/layout-placement/` in KiStack makes
synthetic boards and checks reading, board binding, moves, saving, rollback
and rules against `kicad-cli api-server` processes of its own.
