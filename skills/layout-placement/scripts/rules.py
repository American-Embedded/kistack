"""The design rules the checks use: track width, clearance, via diameter and
copper-to-edge clearance, in millimetres.

Each value comes from its command-line flag when given, else from the board's
project file (<board>.kicad_pro beside it): the Default net class's
track_width, clearance and via_diameter, and the board's
min_copper_edge_clearance. A value found in neither place stops the script:
the checks never fall back to rules of their own. The rules used, and where
each came from, are printed to stderr.

Only the Default net class is read. A board whose critical nets use other
classes (wider power tracks, RF clearances) needs those values passed with
the flags for that run.
"""
import json
import math
import os
import sys

NAMES = (("track", "track width", "track_width"),
         ("clear", "clearance", "clearance"),
         ("via", "via diameter", "via_diameter"),
         ("edge", "copper to edge", None))


class Rules:
    def __init__(self, track, clear, via, edge, source):
        self.track, self.clear, self.via, self.edge, self.source = track, clear, via, edge, source

    def line(self):
        return "rules: " + ", ".join(f"{label} {getattr(self, k):.3f} mm ({self.source[k]})"
                                     for k, label, _ in NAMES if getattr(self, k) is not None)


def add_flags(ap):
    ap.add_argument("--track", type=float, help="track width, mm (default: the board's Default net class)")
    ap.add_argument("--clear", type=float, help="clearance, mm (default: the board's Default net class)")
    ap.add_argument("--via", type=float, help="via diameter, mm (default: the board's Default net class)")
    ap.add_argument("--edge", type=float, help="copper to board edge, mm (default: the board's min_copper_edge_clearance)")


def _project(board):
    pro = os.path.splitext(board)[0] + ".kicad_pro"
    if not os.path.isfile(pro):
        return pro, {}
    try:
        with open(pro) as f:
            j = json.load(f)
    except (OSError, ValueError) as e:
        sys.exit(f"{pro} is unreadable ({e}); pass --track --clear --via --edge")
    found = {}
    for c in (j.get("net_settings") or {}).get("classes") or []:
        if c.get("name") == "Default":
            for k, _, key in NAMES:
                if key and isinstance(c.get(key), (int, float)):
                    found[k] = float(c[key])
    r = ((j.get("board") or {}).get("design_settings") or {}).get("rules") or {}
    if isinstance(r.get("min_copper_edge_clearance"), (int, float)):
        found["edge"] = float(r["min_copper_edge_clearance"])
    return pro, found


def resolve(board, a, need=("track", "clear", "via", "edge")):
    """Rules from the flags in a (argparse namespace), then the project file.
    Only the rules in need must be found; the others are None."""
    pro, found = _project(board)
    vals, src, missing = {}, {}, []
    for k, label, _ in NAMES:
        v = getattr(a, k, None)
        if v is not None:
            vals[k], src[k] = v, "flag"
        elif k in found:
            vals[k], src[k] = found[k], os.path.basename(pro)
        elif k in need:
            missing.append(f"--{k} ({label})")
        else:
            vals[k], src[k] = None, "not used"
    if missing:
        sys.exit(f"no {', '.join(m.split(' ', 1)[1].strip('()') for m in missing)} in {pro}; pass "
                 + " ".join(m.split(" ")[0] for m in missing) + " with the values this board is made to")
    bad = [k for k in vals if vals[k] is not None and not (math.isfinite(vals[k]) and vals[k] > 0) and not (k == "edge" and vals[k] == 0)]
    if bad:
        sys.exit("rules must be positive: " + ", ".join(f"{k}={vals[k]}" for k in bad))
    r = Rules(vals["track"], vals["clear"], vals["via"], vals["edge"], src)
    print(r.line(), file=sys.stderr)
    return r
