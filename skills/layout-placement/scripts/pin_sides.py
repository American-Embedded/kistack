#!/usr/bin/env python3
"""Print an IC's pins grouped by package side, in order along each side, with
nets, for the IC's current rotation on the board.

usage: pin_sides.py board.kicad_pcb REF
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ipc_board as geom  # noqa: E402


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: pin_sides.py board.kicad_pcb REF")
    b = geom.load(sys.argv[1])
    fp = geom.need(geom.by_ref(b), sys.argv[2], sys.argv[1])
    cx, cy = fp.x, fp.y
    big = max(fp.pads, key=lambda p: p.poly.area)
    sides = {"left (-x)": [], "right (+x)": [], "top (-y)": [], "bottom (+y)": [], "centre": []}
    for p in fp.pads:
        dx, dy = p.center[0] - cx, p.center[1] - cy
        if p is big or (abs(dx) < 1e-6 and abs(dy) < 1e-6) or p.kind == "thru_hole":
            sides["centre"].append(p)
        elif abs(dx) >= abs(dy):
            sides["right (+x)" if dx > 0 else "left (-x)"].append(p)
        else:
            sides["bottom (+y)" if dy > 0 else "top (-y)"].append(p)
    for name, ps in sides.items():
        if name == "centre":
            nets = sorted({str(p.net) for p in ps})
            print(f"{name}: {len(ps)} pads, nets {nets}")
            continue
        key = (lambda p: p.center[1]) if "x)" in name else (lambda p: p.center[0])
        print(f"{name}:")
        for p in sorted(ps, key=key):
            print(f"   pin {p.num:>3} {str(p.net):16} at ({p.center[0]:.3f}, {p.center[1]:.3f})")


if __name__ == "__main__":
    main()
