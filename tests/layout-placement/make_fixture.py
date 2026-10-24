#!/usr/bin/env python3
"""Write a small synthetic board for the layout-placement checks.

    make_fixture.py DIR [--track 0.15 --clearance 0.1 --via 0.5 --edge 0.2]

DIR/fixture.kicad_pro and DIR/fixture.kicad_pcb: a 20 x 20 mm two-layer board
with U1 (a 16-pin QFN-like part, 0.65 mm pitch), C1..C3 (0402) and R1 (0402),
courtyards on every part, and one netted F.Cu rectangle (fixed copper on net
RF). Nothing here comes from a real design.
"""
import argparse
import json
import os
import uuid

NETS = ["", "GND", "VDD", "RF", "XC1", "SIG1", "SIG2", "SIG3", "SIG4", "SIG5", "SIG6", "SIG7", "SIG8", "SIG9", "USB_P", "USB_N",
        "ANT1", "RFN"]


def u():
    return str(uuid.uuid4())


def net(name):
    return f'(net {NETS.index(name)} "{name}")' if name else ""


PAD_CLEARANCE = {}


def pad(num, x, y, w, h, n):
    c = PAD_CLEARANCE.get(str(num))
    return (f'(pad "{num}" smd roundrect (at {x} {y}) (size {w} {h}) (layers "F.Cu" "F.Paste" "F.Mask") '
            f'(roundrect_rratio 0.25) {net(n)}' + (f" (clearance {c})" if c else "") + f' (uuid "{u()}"))')


def crt(x0, y0, x1, y1):
    return f'(fp_rect (start {x0} {y0}) (end {x1} {y1}) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd") (uuid "{u()}"))'


def fp(ref, val, x, y, rot, pads, cy):
    return (f'(footprint "fixture:{ref}" (layer "F.Cu") (uuid "{u()}") (at {x} {y} {rot})\n'
            f'  (property "Reference" "{ref}" (at 0 -1.5 0) (layer "F.SilkS") (uuid "{u()}") (effects (font (size 0.5 0.5) (thickness 0.1))))\n'
            f'  (property "Value" "{val}" (at 0 1.5 0) (layer "F.Fab") (uuid "{u()}") (effects (font (size 0.5 0.5) (thickness 0.1))))\n'
            f'  (attr smd)\n  {cy}\n  ' + "\n  ".join(pads) + "\n)")


def two_pin_v(n1, n2):
    return [pad(1, 0, -0.48, 0.62, 0.56, n1), pad(2, 0, 0.48, 0.62, 0.56, n2)]


def qfn(pad_clearance=None, rf=False):
    # 16 pins, 4 a side, 0.65 mm pitch, pads 0.3 x 0.7 at 1.95 mm from centre
    PAD_CLEARANCE.clear()
    if pad_clearance:
        num, mm = pad_clearance.split("=")
        PAD_CLEARANCE[num] = mm
    nets = ["VDD", "SIG1", "SIG2", "XC1", "SIG3", "SIG4", "RF", "GND", "SIG5", "SIG6", "VDD", "SIG7",
            "SIG8", "SIG9", "USB_P", "USB_N"]
    if rf:
        nets[6] = "ANT1"
    ps, k = [], 0
    offs = [-0.975, -0.325, 0.325, 0.975]
    for side in range(4):
        for o in offs:
            n = nets[k]
            k += 1
            if side == 0:
                ps.append(pad(k, -1.95, o, 0.7, 0.3, n))
            elif side == 1:
                ps.append(pad(k, o, 1.95, 0.3, 0.7, n))
            elif side == 2:
                ps.append(pad(k, 1.95, -o, 0.7, 0.3, n))
            else:
                ps.append(pad(k, -o, -1.95, 0.3, 0.7, n))
    ps.append(pad(17, 0, 0, 2.4, 2.4, "GND"))
    # a paste-only aperture, as many QFN footprints have under the exposed pad
    ps.append(f'(pad "" smd rect (at 0 0) (size 1 1) (layers "F.Paste") (uuid "{u()}"))')
    return ps


def two_pin(n1, n2):
    return [pad(1, -0.48, 0, 0.56, 0.62, n1), pad(2, 0.48, 0, 0.56, 0.62, n2)]


def board(rules):
    dup = [fp("R1", "10k", 116.0, 105.0, 0, two_pin("SIG2", "VDD"), crt(-0.91, -0.46, 0.91, 0.46))] if rules.dup else []
    # an RF pi chain U1.7 (ANT1) - L1 - RFN - L2 - RF port: C20 sits inline in
    # the gap between L1 and L2, C21 (on the port node) sits off the path
    v = crt(-0.46, -0.91, 0.46, 0.91)
    dup += [fp("L1", "2n2", 112.0, 104.0, 0, two_pin("ANT1", "RFN"), crt(-0.91, -0.46, 0.91, 0.46)),
            fp("L2", "3n3", 115.0, 104.0, 0, two_pin("RFN", "RF"), crt(-0.91, -0.46, 0.91, 0.46)),
            fp("C20", "1p0", 113.5, 104.48, 0, two_pin_v("RFN", "GND"), v),
            fp("C21", "1p2", 117.8, 104.48, 0, two_pin_v("RF", "GND"), v)] if rules.rf else []
    fps = dup + [
        fp("U1", "QFN16", 110, 100, 0, qfn(rules.pad_clearance, rules.rf), crt(-2.6, -2.6, 2.6, 2.6)),
        fp("C1", "100n", 106.2, 99.0, 0, two_pin("VDD", "GND"), crt(-0.91, -0.46, 0.91, 0.46)),
        fp("C2", "100n", 113.8, 101.0, 0, two_pin("VDD", "GND"), crt(-0.91, -0.46, 0.91, 0.46)),
        fp("C3", "12p", 106.2, 101.5, 0, two_pin("XC1", "GND"), crt(-0.91, -0.46, 0.91, 0.46)),
        fp("R1", "10k", 104.0, 104.0, 0, two_pin("SIG1", "VDD"), crt(-0.91, -0.46, 0.91, 0.46)),
    ]
    nets = "\n".join(f'(net {i} "{n}")' for i, n in enumerate(NETS))
    edge = f'(gr_rect (start 100 90) (end 120 110) (stroke (width 0.1) (type solid)) (fill no) (layer "Edge.Cuts") (uuid "{u()}"))'
    port = f'(gr_rect (start 116 99.6) (end 119.5 100.4) (stroke (width 0) (type solid)) (fill yes) (layer "F.Cu") (net {NETS.index("RF")}) (uuid "{u()}"))'
    return f"""(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")
(general (thickness 1.6) (legacy_teardrops no))
(paper "A4")
(layers
  (0 "F.Cu" signal) (2 "B.Cu" signal)
  (9 "F.Adhes" user "F.Adhesive") (11 "B.Adhes" user "B.Adhesive")
  (13 "F.Paste" user) (15 "B.Paste" user)
  (5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")
  (1 "F.Mask" user) (3 "B.Mask" user)
  (17 "Dwgs.User" user "User.Drawings") (19 "Cmts.User" user "User.Comments")
  (25 "Edge.Cuts" user) (27 "Margin" user)
  (31 "F.CrtYd" user "F.Courtyard") (29 "B.CrtYd" user "B.Courtyard")
  (35 "F.Fab" user) (33 "B.Fab" user)
)
(setup (pad_to_mask_clearance 0))
{nets}
{edge}
{port}
""" + "\n".join(fps) + "\n)\n"


def project(rules):
    classes = [{"name": "Default", "clearance": rules.clearance, "track_width": rules.track,
                "via_diameter": rules.via, "via_drill": round(rules.via / 2, 3), "priority": 2147483647,
                "diff_pair_width": rules.track, "diff_pair_gap": rules.clearance}]
    patterns = []
    for i, k in enumerate(rules.klass or []):
        f = k.split(":")
        c = {"name": f[0], "track_width": float(f[1]), "clearance": float(f[2]), "via_diameter": float(f[3]),
             "via_drill": round(float(f[3]) / 2, 3), "priority": i}
        if len(f) > 7:
            c["diff_pair_width"], c["diff_pair_gap"] = float(f[6]), float(f[7])
        classes.append(c)
        patterns.append({"netclass": f[0], "pattern": f[4]})
    return {
        "board": {"design_settings": {"rules": {"min_copper_edge_clearance": rules.edge,
                                                 "min_clearance": rules.min_clearance or rules.clearance,
                                                 "min_track_width": rules.track,
                                                 "min_via_diameter": rules.via}}},
        "meta": {"filename": "fixture.kicad_pro", "version": 3},
        "net_settings": {"classes": classes, "netclass_patterns": patterns, "meta": {"version": 4}},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--name", default="fixture")
    ap.add_argument("--track", type=float, default=0.15)
    ap.add_argument("--clearance", type=float, default=0.1)
    ap.add_argument("--via", type=float, default=0.5)
    ap.add_argument("--edge", type=float, default=0.2)
    ap.add_argument("--no-project", action="store_true")
    ap.add_argument("--dup", action="store_true", help="a second footprint with the reference R1")
    ap.add_argument("--rf", action="store_true", help="an RF pi chain on U1 pin 7, one shunt inline, one off the path")
    ap.add_argument("--klass", action="append",
                    help="NAME:track:clearance:via:netpattern[:x:pairwidth:pairgap], a net class assigned by pattern")
    ap.add_argument("--min-clearance", type=float, help="the board's min_clearance (default: --clearance)")
    ap.add_argument("--dru", help="text of a custom rules file <name>.kicad_dru")
    ap.add_argument("--pad-clearance", help="PIN=mm, a clearance override on that U1 pad")
    a = ap.parse_args()
    os.makedirs(a.dir, exist_ok=True)
    with open(os.path.join(a.dir, a.name + ".kicad_pcb"), "w") as f:
        f.write(board(a))
    if a.dru:
        with open(os.path.join(a.dir, a.name + ".kicad_dru"), "w") as f:
            f.write(a.dru)
    if not a.no_project:
        p = project(a)
        p["meta"]["filename"] = a.name + ".kicad_pro"
        with open(os.path.join(a.dir, a.name + ".kicad_pro"), "w") as f:
            json.dump(p, f, indent=2)


if __name__ == "__main__":
    main()
