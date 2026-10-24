#!/usr/bin/env python3
"""Search positions and rotations for one small part near the IC pin it
serves, keeping every other part where it is.

For each candidate (grid steps around the pin, rotations 0/90/180/270) it
rejects courtyard overlaps and courtyards outside the outline, then reports:
  gap      edge gap from the part's pad on the pin's net to the pin
  faces    True when that pad is nearer the pin than the part's other pads
  blocks   IC signal pins whose fan-out (straight or 45 degrees, --front mm,
           one track channel wide) the part's pads would block
  partner  with --partner REF: gap from the part's pad on the shared net to
           the partner's pad on that net (for example R1 next to C13)
Candidates are sorted by (blocks, gap, partner gap).  With --conflicts the
search ignores other parts' courtyards and prints, for the best spots, which
parts' courtyards they would overlap: those are the parts to move (for example
a crystal that holds the space a decoupler needs).  Nothing is written to
the board; apply the chosen position with IPC or place.py and re-run the DRC,
placement_audit.py and route_check.py.

usage: local_search.py board.kicad_pcb --ic U1 --pin 30 --part C13
       [--partner R1] [--radius 2.0] [--step 0.05] [--front 2.0] [--top 10]
       [--conflicts [--movable R1 X2 ...]]
"""
import argparse
import math
import signal
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ipc_board as geom  # noqa: E402
import rules as R  # noqa: E402
from shapely import affinity  # noqa: E402
from shapely.geometry import LineString  # noqa: E402
from shapely.ops import unary_union  # noqa: E402


def moved(fp, x, y, rot):
    """Pad polygons and courtyard of fp at (x, y, rot)."""
    d = rot - fp.rot

    def tf(g):
        g = affinity.rotate(g, -d, origin=(fp.x, fp.y))
        return affinity.translate(g, x - fp.x, y - fp.y)
    return [(p, tf(p.poly)) for p in fp.pads], tf(fp.courtyard)


def fanout_lanes(ic, gnd, own_nets, front, track, clear):
    lanes = []
    w = track + 2 * clear
    for p in ic.pads:
        if p.kind != "smd" or not p.net or p.net == gnd or p.net in own_nets:
            continue
        dx, dy = p.center[0] - ic.x, p.center[1] - ic.y
        ux, uy = ((1 if dx > 0 else -1), 0) if abs(dx) >= abs(dy) else (0, (1 if dy > 0 else -1))
        x0, y0, x1, y1 = p.poly.bounds
        sx = (x1 if ux > 0 else x0) if ux else p.center[0]
        sy = (y1 if uy > 0 else y0) if uy else p.center[1]
        opts = []
        for ang in (0, 45, -45):
            r = math.radians(ang)
            vx, vy = ux * math.cos(r) - uy * math.sin(r), ux * math.sin(r) + uy * math.cos(r)
            opts.append(LineString([(sx, sy), (sx + front * vx, sy + front * vy)]).buffer(w / 2, cap_style=2))
        lanes.append((p, opts))
    return lanes


def main():
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("--ic", required=True)
    ap.add_argument("--pin", required=True)
    ap.add_argument("--part", required=True)
    ap.add_argument("--partner")
    ap.add_argument("--ground", default="GND")
    ap.add_argument("--radius", type=float, default=2.0)
    ap.add_argument("--step", type=float, default=0.05)
    ap.add_argument("--front", type=float, default=2.0)
    R.add_flags(ap)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--conflicts", action="store_true")
    ap.add_argument("--movable", nargs="*", default=None,
                    help="with --conflicts, ignore only these parts' courtyards (default: all other parts)")
    a = ap.parse_args()
    b = geom.load(a.board)
    r = R.resolve(a.board, a, b, need=("track", "clear"))
    a.track, a.clear = r.track, r.clear
    fps = geom.by_ref(b)
    ic, fp = geom.need(fps, a.ic, a.board), geom.need(fps, a.part, a.board)
    pin = [p for p in ic.pads if p.num == a.pin][0]
    others = [o for o in b["footprints"] if o.ref != fp.ref]
    occ = unary_union([o.courtyard for o in others if o.courtyard is not None])
    outline = b["outline"].buffer(1e-6)
    own_nets = {p.net for p in fp.pads}
    lanes = fanout_lanes(ic, a.ground, own_nets, a.front, a.track, a.clear)
    # lanes already blocked by other parts do not count against the candidate
    other_pads = [(q.net, q.poly) for o in others if o.ref != ic.ref for q in o.pads]
    free_now = {}
    for p, opts in lanes:
        free_now[p.num] = [i for i, ch in enumerate(opts)
                           if not any(n != p.net and g.intersects(ch) for n, g in other_pads)]
    partner = fps[a.partner] if a.partner else None
    shared = None
    if partner:
        s = {q.net for q in partner.pads} & {p.net for p in fp.pads}
        shared = next(iter(s - {a.ground}), None)
    res = []
    n = int(a.radius / a.step)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, y = pin.center[0] + i * a.step, pin.center[1] + j * a.step
            if math.hypot(x - pin.center[0], y - pin.center[1]) > a.radius:
                continue
            for rot in (0, 90, 180, 270):
                pads, cy = moved(fp, x, y, rot)
                over = []
                if cy.intersects(occ) and cy.intersection(occ).area > 1e-9:
                    over = sorted(o.ref for o in others if o.courtyard is not None and o.ref != ic.ref
                                  and cy.intersection(o.courtyard).area > 1e-9)
                    icover = ic.courtyard is not None and cy.intersection(ic.courtyard).area > 1e-9
                    fixed_hit = a.movable is not None and any(r not in a.movable for r in over)
                    if not a.conflicts or icover or fixed_hit:
                        continue
                if not outline.contains(cy):
                    continue
                on = [g for p, g in pads if p.net == pin.net]
                if not on:
                    continue
                gap = min(g.distance(pin.poly) for g in on)
                near = min(on, key=lambda g: g.distance(pin.poly))
                faces = all(near.distance(pin.poly) <= g.distance(pin.poly) for p, g in pads)
                blocks = []
                for p, opts in lanes:
                    fr = free_now[p.num]
                    if not fr:
                        continue
                    still = [k for k in fr if not any(g.intersects(opts[k]) for q, g in pads if q.net != p.net)]
                    if not still:
                        blocks.append(p.num)
                pg = None
                if partner and shared:
                    mine = [g for p, g in pads if p.net == shared]
                    theirs = [q.poly for q in partner.pads if q.net == shared]
                    pg = min(x2.distance(y2) for x2 in mine for y2 in theirs) if mine and theirs else None
                res.append((len(blocks), round(gap, 3), 9 if pg is None else round(pg, 3), round(x, 3), round(y, 3), rot,
                            faces, blocks, over))
    res.sort(key=lambda r: (r[0], r[1], r[2]))
    print(f"{len(res)} legal candidates for {a.part} at {a.ic}.{a.pin} (current gap "
          f"{min(p.poly.distance(pin.poly) for p in fp.pads if p.net == pin.net):.3f} mm)")
    print("blocks  gap_mm  partner_mm   x        y       rot  faces  blocked pins" + ("   would overlap" if a.conflicts else ""))
    for r in res[:a.top]:
        print(f"{r[0]:6d}  {r[1]:6.3f}  {r[2]:9.3f}  {r[3]:8.3f} {r[4]:8.3f} {r[5]:4d}  {str(r[6]):5}  {r[7]}"
              + (f"   {r[8]}" if a.conflicts else ""))


if __name__ == "__main__":
    main()
