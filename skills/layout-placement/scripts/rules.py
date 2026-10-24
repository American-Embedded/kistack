"""The design rules the checks use: track width, clearance, via diameter and
copper-to-edge clearance, in millimetres.

The checks route and measure with one value of each, so each value is the
strictest the board applies to any copper on it:

- every net's effective net class, as KiCad itself resolves it (explicit
  assignments, patterns, schematic directives): its track width, clearance
  and via diameter, and for a class with differential pair settings its
  pair track width;
- the board's minimum rules in <board>.kicad_pro (min_clearance,
  min_track_width, min_via_diameter, min_copper_edge_clearance);
- clearance overrides on pads and footprints.

Custom DRC rules (a <board>.kicad_dru with rules in it) are not evaluated,
so such a board is refused unless all four values are passed as flags. A
board without a .kicad_pro is refused unless all four are passed. A flag
may make a rule stricter than the board's; a flag looser than the board's
is refused unless --rules-override is given, and then every line the script
prints about rules says the check was looser than the board. The rules used
and what set each one are printed to stderr.
"""
import math
import json
import os
import re
import sys

NM = 1e-6
NAMES = (("track", "track width"), ("clear", "clearance"), ("via", "via diameter"), ("edge", "copper to edge"))


class Rules:
    def __init__(self, vals, source, notes):
        self.track, self.clear, self.via, self.edge = (vals.get(k) for k, _ in NAMES)
        self.source, self.notes = source, notes

    def line(self):
        return "rules: " + ", ".join(f"{label} {getattr(self, k):.3f} mm ({self.source[k]})"
                                     for k, label in NAMES if getattr(self, k) is not None)


def add_flags(ap):
    ap.add_argument("--track", type=float, help="track width, mm (default: the strictest the board applies)")
    ap.add_argument("--clear", type=float, help="clearance, mm (default: the strictest the board applies)")
    ap.add_argument("--via", type=float, help="via diameter, mm (default: the strictest the board applies)")
    ap.add_argument("--edge", type=float, help="copper to board edge, mm (default: the board's min_copper_edge_clearance)")
    ap.add_argument("--rules-override", action="store_true",
                    help="allow flags looser than the board's rules; the output says the check was looser")


def _project(board):
    pro = os.path.splitext(board)[0] + ".kicad_pro"
    if not os.path.isfile(pro):
        return pro, None
    try:
        with open(pro) as f:
            return pro, json.load(f)
    except (OSError, ValueError) as e:
        sys.exit(f"{pro} is unreadable ({e})")


def _custom_rules(board):
    dru = os.path.splitext(board)[0] + ".kicad_dru"
    if not os.path.isfile(dru):
        return None
    with open(dru) as f:
        text = f.read()
    # a rule is "(rule <name> ...)"; comments start with '#'
    body = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    return dru if re.search(r"\(\s*rule\b", body) else None


def _strictest(cands):
    """The largest (value, source) of the candidates that have a value."""
    cands = [c for c in cands if c[0] is not None and c[0] > 0]
    return max(cands, key=lambda c: c[0]) if cands else (None, None)


def _class_name(nc):
    # an effective class is its constituents; Default is in every one
    parts = [c for c in (nc.constituents or []) if c != "Default"] or list(nc.constituents or [])
    return "+".join(parts) if parts else nc.name


def _pair_nets(names):
    """Nets KiCad pairs as differential: a name ending in + or -, P or N,
    whose partner is on the board too."""
    have, out = set(names), set()
    for n in names:
        for a, b in (("+", "-"), ("P", "N")):
            for x, y in ((a, b), (b, a)):
                if n.endswith(x) and n[:-1] + y in have:
                    out.add(n)
    return out


def derive(board_path, loaded):
    """The board's strictest rules: {key: (mm, source)}, and notes."""
    pro, j = _project(board_path)
    if j is None:
        return None, [f"no {os.path.basename(pro)}"], []
    r = ((j.get("board") or {}).get("design_settings") or {}).get("rules") or {}
    mins = {k: (float(r[f]), f"board minimum {f}") for k, f in (("track", "min_track_width"),
                                                                  ("clear", "min_clearance"),
                                                                  ("via", "min_via_diameter"),
                                                                  ("edge", "min_copper_edge_clearance"))
            if isinstance(r.get(f), (int, float))}
    kb = loaded["board"]
    nets = [n for n in kb.get_nets() if n.name]
    classes = kb.get_netclass_for_nets(nets) if nets else {}
    cand = {k: [mins[k]] if k in mins else [] for k, _ in NAMES}
    problems, notes, pairs = [], [], []
    paired = _pair_nets(list(classes))
    for net, nc in sorted(classes.items()):
        name = _class_name(nc)
        for k, attr in (("track", "track_width"), ("clear", "clearance"), ("via", "via_diameter")):
            v = getattr(nc, attr)
            if v is None:
                problems.append(f"KiCad gives no {attr} for net class {name} (net {net})")
            else:
                cand[k].append((v * NM, f"net class {name} on {net}"))
        if net in paired:
            pairs.append(net)
            dw = nc.diff_pair_track_width
            if dw:
                cand["track"].append((dw * NM, f"net class {name} pair width on {net}"))
    for fp in kb.get_footprints():
        ref = fp.reference_field.text.value
        o = fp.proto.overrides
        if o.HasField("copper_clearance"):
            cand["clear"].append((o.copper_clearance.value_nm * NM, f"footprint {ref} clearance override"))
        for p in fp.definition.pads:
            pp = p.proto
            if pp.HasField("copper_clearance_override"):
                cand["clear"].append((pp.copper_clearance_override.value_nm * NM,
                                      f"pad {ref}.{pp.number} clearance override"))
    if pairs:
        notes.append(f"{len(pairs)} nets are differential pairs ({', '.join(pairs[:6])}"
                     f"{'...' if len(pairs) > 6 else ''}); the checks route them as single tracks, at least the "
                     "pair width wide, and do not check their coupling or gap")
    return {k: _strictest(cand[k]) for k, _ in NAMES}, problems, notes


def resolve(board, a, loaded, need=("track", "clear", "via", "edge")):
    """The rules for a run: the board's strictest, or the flags in a."""
    flags = {k: getattr(a, k, None) for k, _ in NAMES}
    bad = [f"--{k} {v}" for k, v in flags.items() if v is not None and not (math.isfinite(v) and v >= 0)]
    if bad:
        sys.exit("rules must be positive: " + ", ".join(bad))
    override = getattr(a, "rules_override", False)
    derived, problems, notes = derive(board, loaded)
    dru = _custom_rules(board)
    all_flags = all(flags[k] is not None for k in need)
    if derived is None and not all_flags:
        sys.exit(f"{problems[0]} beside {board}, so its rules are unknown; pass "
                 + " ".join(f"--{k}" for k in need) + " with the values this board is made to")
    if problems and not all_flags:
        sys.exit("; ".join(problems) + "; pass " + " ".join(f"--{k}" for k in need) + " to run anyway")
    if dru and not all_flags:
        sys.exit(f"{dru} has custom DRC rules, which these checks cannot evaluate; pass "
                 + " ".join(f"--{k}" for k in need) + " with values that satisfy those rules")
    if dru:
        notes.append(f"custom rules in {os.path.basename(dru)} are not evaluated; the flagged values are what "
                     "was checked")
    vals, src, looser = {}, {}, []
    for k, label in NAMES:
        have = derived.get(k, (None, None)) if derived else (None, None)
        if flags[k] is not None:
            vals[k], src[k] = flags[k], "flag"
            if have[0] is not None and flags[k] < have[0] - 1e-9:
                looser.append(f"{label} {flags[k]:.3f} mm is looser than the board's {have[0]:.3f} mm ({have[1]})")
        elif have[0] is not None:
            vals[k], src[k] = have
        elif k in need:
            sys.exit(f"the board gives no {label}; pass --{k}")
        else:
            vals[k], src[k] = None, "not used"
    if looser and not override:
        sys.exit("; ".join(looser) + "; a looser rule would report clearance the board does not have. Pass "
                 "--rules-override only when the user wants a check looser than the board")
    for m in looser:
        src[[k for k, label in NAMES if m.startswith(label)][0]] += ", LOOSER THAN THE BOARD"
        notes.append("rules override: " + m + "; results do not hold under the board's own rules")
    r = Rules(vals, src, notes)
    print(r.line(), file=sys.stderr)
    for n in notes:
        print("rules: " + n, file=sys.stderr)
    return r
