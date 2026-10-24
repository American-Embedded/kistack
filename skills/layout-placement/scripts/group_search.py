#!/usr/bin/env python3
"""Joint placement check for a local group of parts that compete for the
same pins (for example the caps, ferrite and inductor around a DC/DC and its
supply pins).

The listed parts are lifted off the board; every other part stays put.  For
every placement order of the group (all orders up to --max-orders), each part
in turn takes its best legal spot given the parts already placed: no
courtyard overlap, inside the outline, fewest blocked fan-outs of other IC
signal pins, then smallest gap.  The gap of a part is its pad on the pin's
net to that pin, divided by that pin's weight; for a part with two pins (an
inductor between a switch pin and an output pin) it is the larger of its two
weighted gaps.  Weights say how much distance a connection tolerates (1 for
a decoupler pad or a switch node, larger for a smoothed output path).
Orders are ranked by the worst weighted gap in the group, then by the sum.  The best orders and their
positions are printed; nothing is written to the board.

usage: group_search.py board.kicad_pcb --ic U1 --assign C1:45 C12:43 L1:46,45 FB1:45 ...
       [--lift FB1 ...] [--radius 2.0] [--step 0.15] [--max-orders 6] [--top 3] [--thorough]
  The default runs in seconds; --thorough takes about a minute for four parts.
  Run it in the foreground and wait for the result.
  --assign REF:PIN or REF:PIN1,PIN2 (two pins: each pad to the pin on its net),
           each pin optionally with a weight, e.g. L1:46@1,45@3 (default weight 1)
"""
import argparse
import itertools
import math
import os
import signal
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ipc_board as geom  # noqa: E402
import rules as R  # noqa: E402
from local_search import fanout_lanes, moved  # noqa: E402
from shapely.ops import unary_union  # noqa: E402


def candidates(fp, pins, occ_polys, outline, lanes, lane_free, others_pads, radius, step):
    cx = sum(p.center[0] for p, w in pins) / len(pins)
    cy = sum(p.center[1] for p, w in pins) / len(pins)
    occ = unary_union(occ_polys) if occ_polys else None
    n = int(radius / step)
    best = None
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, y = cx + i * step, cy + j * step
            if math.hypot(i * step, j * step) > radius:
                continue
            for rot in (0, 90, 180, 270):
                pads, cyd = moved(fp, x, y, rot)
                if not outline.contains(cyd):
                    continue
                if occ is not None and cyd.intersects(occ) and cyd.intersection(occ).area > 1e-9:
                    continue
                gaps = []
                for pin, wt in pins:
                    on = [g for q, g in pads if q.net == pin.net]
                    if not on:
                        gaps = None
                        break
                    gaps.append(min(g.distance(pin.poly) for g in on) / wt)
                if gaps is None:
                    continue
                gap = max(gaps)
                blocks = 0
                for p, opts in lanes:
                    fr = lane_free[p.num]
                    if fr and not [k for k in fr if not any(g.intersects(opts[k]) for q, g in pads if q.net != p.net)]:
                        blocks += 1
                key = (blocks, round(gap, 3))
                if best is None or key < best[0]:
                    best = (key, (round(x, 3), round(y, 3), rot), cyd, [g for q, g in pads])
    return best


def main():
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("--ic", required=True)
    ap.add_argument("--assign", nargs="+", required=True)
    ap.add_argument("--ground", default="GND")
    ap.add_argument("--radius", type=float, default=2.0)
    ap.add_argument("--step", type=float, default=0.15)
    ap.add_argument("--front", type=float, default=2.0)
    ap.add_argument("--max-orders", type=int, default=6)
    ap.add_argument("--thorough", action="store_true", help="0.1 mm step, 2.5 mm radius, 24 orders (about a minute for four parts)")
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--lift", nargs="*", default=[],
                    help="parts taken off the board but not placed (place them afterwards, e.g. a ferrite between two nodes)")
    R.add_flags(ap)
    a = ap.parse_args()
    if a.thorough:
        a.step, a.radius, a.max_orders = 0.1, 2.5, 24
    b = geom.load(a.board)
    rules = R.resolve(a.board, a, b, need=("track", "clear"))
    fps = geom.by_ref(b)
    ic = geom.need(fps, a.ic, a.board)
    group = []
    for s in a.assign:
        ref, spec = s.split(":")
        pins = []
        for t in spec.split(","):
            num, _, wt = t.partition("@")
            pins.append(([p for p in ic.pads if p.num == num][0], float(wt) if wt else 1.0))
        group.append((ref, pins))
    refs = {r for r, _ in group} | set(a.lift)
    fixed = [o for o in b["footprints"] if o.ref not in refs]
    fixed_occ = [o.courtyard for o in fixed if o.courtyard is not None]
    outline = b["outline"].buffer(1e-6)
    own = {q.net for r, _ in group for q in fps[r].pads}
    lanes = fanout_lanes(ic, a.ground, own, a.front, rules.track, rules.clear)
    fixed_pads = [(q.net, q.poly) for o in fixed if o.ref != ic.ref for q in o.pads]
    lane_free = {p.num: [k for k, ch in enumerate(opts) if not any(n != p.net and g.intersects(ch) for n, g in fixed_pads)]
                 for p, opts in lanes}
    print("current weighted gaps:", ", ".join(
        f"{r} {max(min(q.poly.distance(p.poly) for q in fps[r].pads if q.net == p.net) / w for p, w in pins):.2f}" for r, pins in group))
    results = []
    for k, order in enumerate(itertools.permutations(range(len(group)))):
        if k >= a.max_orders:
            break
        occ = list(fixed_occ)
        placed, ok = {}, True
        for idx in order:
            ref, pins = group[idx]
            c = candidates(fps[ref], pins, occ, outline, lanes, lane_free, fixed_pads, a.radius, a.step)
            if c is None:
                ok = False
                break
            placed[ref] = (c[0], c[1])
            occ.append(c[2])
        if not ok:
            continue
        worst = max(v[0][1] for v in placed.values())
        total = sum(v[0][1] for v in placed.values())
        blocks = sum(v[0][0] for v in placed.values())
        results.append((blocks, worst, total, [group[i][0] for i in order], placed))
    results.sort(key=lambda r: (r[0], r[1], r[2]))
    for blocks, worst, total, order, placed in results[:a.top]:
        print(f"order {' > '.join(order)}: worst weighted gap {worst:.2f} mm, sum {total:.2f} mm, blocked fan-outs {blocks}")
        for ref, ((bl, gap), (x, y, rot)) in placed.items():
            print(f"   {ref:5} at ({x}, {y}) rot {rot}  weighted gap {gap:.2f} mm")


if __name__ == "__main__":
    main()
