#!/usr/bin/env python3
"""Pin-centred placement audit around one IC.

Prints, worst first:
  pins     every IC pin whose net reaches a small part (<= 4 pads): the gap
           to the nearest such part pad, which part, and whether that part's
           ground pad is nearer the pin than its other pad (wrong way round)
  parts    every small part pad on an IC net: gap to the nearest IC pin on
           the same net (a part close only to another passive shows up here)
  ground   every ground pad of a small part: gap to the nearest legal via
           site (via diameter plus clearance from other-net copper, no via in
           a pad, inside the edge clearance)
  pairs    two-pad parts whose both pads go to IC pins (crystals, flying
           caps): the two gaps and their difference
  fronts   IC signal pins whose fan-out is blocked: no channel (one track
           wide) straight out or at 45 degrees is free of other nets' pads for
           --front mm
  chain    with --chain: the gap of every link along an ordered RF chain, and for
           every shunt on it whether its node pad lies on the series path (a
           --rf-track wide track between the two series pads or the port it joins)
           or how long a branch track it needs to reach that path
  ties     with --tie: the gap of each vendor-mandated pad-to-pin connection,
           flagged when it is longer than the part's courtyard; a shunt on the
           chain also shows its tie, since a documented return takes precedence
           over an inline node pad

usage: placement_audit.py board.kicad_pcb --ic REF [--ground GND] [--front 2.0]
       [--via MM] [--clear MM] [--track MM] [--edge MM]
       [--chain U1.31 L2 L3 L4 RF --rf-track MM] [--tie C6:GND=U1.32 ...]
  --chain  antenna pin, series parts in schematic order, then the RF port net
  --rf-track  the width of the track that will run through the chain (its
           50 ohm width on this board); --chain needs it, there is no default
  --tie    PART:NET=IC.PIN for a pad the schematic ties to one pin
  --via --clear --track --edge  default to the strictest rules the board
           applies (rules.py); --rules-override allows looser flags
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ipc_board as geom  # noqa: E402
import rules as R  # noqa: E402
from shapely.geometry import LineString, Point, box  # noqa: E402
from shapely import affinity  # noqa: E402
from shapely.ops import nearest_points, unary_union  # noqa: E402


def via_gap(b, pad, via, clear, edge, search=1.2):
    r = via / 2
    others, smd = [], []
    for fp in b["footprints"]:
        for p in fp.pads:
            if p.net != pad.net:
                others.append(p.poly)
            if p.kind == "smd":
                smd.append(p.poly)
    others += [poly for l, n, poly in b["fixed_copper"] if n != pad.net]
    allowed = b["outline"].buffer(-(edge + r))
    if others:
        allowed = allowed.difference(unary_union(others).buffer(clear + r, 8))
    if smd:
        allowed = allowed.difference(unary_union(smd).buffer(r, 8))
    cand = allowed.intersection(pad.poly.buffer(search + r))
    if cand.is_empty:
        return None
    return max(0.0, cand.distance(pad.poly) - r)


def tie_gaps(fps, ties):
    """{part: (spec, gap_mm, stretched)} for each PART:NET=IC.PIN tie. A tie counts as
    stretched when its gap is longer than the part's own courtyard: the part has been
    moved away from its documented return."""
    out = {}
    for t in ties or []:
        lhs, rhs = t.split("=")
        ref, net = lhs.split(":")
        ir, pin = rhs.split(".")
        q = [x for x in fps[ref].pads if x.net == net]
        pp = [x for x in fps[ir].pads if x.num == pin]
        if q and pp:
            gap = min(x.poly.distance(y.poly) for x in q for y in pp)
            cy = fps[ref].courtyard
            size = max(cy.bounds[2] - cy.bounds[0], cy.bounds[3] - cy.bounds[1]) if cy is not None else float("inf")
            out[ref] = (t, gap, gap > size)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("--ic", required=True)
    ap.add_argument("--ground", default="GND")
    R.add_flags(ap)
    ap.add_argument("--front", type=float, default=2.0)
    ap.add_argument("--chain", nargs="*")
    ap.add_argument("--rf-track", type=float,
                    help="width of the track through the RF chain, mm, for the inline check (needed with --chain)")
    ap.add_argument("--tie", nargs="*", default=[])
    a = ap.parse_args()
    if a.chain and not (a.rf_track and math.isfinite(a.rf_track) and a.rf_track > 0):
        sys.exit("--chain needs --rf-track MM, the width of the track that will run through the chain")
    b = geom.load(a.board)
    r = R.resolve(a.board, a, b)
    a.track, a.clear, a.via, a.edge = r.track, r.clear, r.via, r.edge
    fps = geom.by_ref(b)
    if a.ic not in fps:
        sys.exit(f"no footprint {a.ic} on {a.board}")
    ic = fps[a.ic]
    small = [fp for fp in b["footprints"] if len(fp.pads) <= 4 and fp.ref != a.ic]
    icpins = [p for p in ic.pads if p.net and p.kind == "smd"]
    gnd = a.ground

    print("pins (IC pin -> nearest small-part pad on the same net)")
    rows = []
    for p in icpins:
        if p.net == gnd:
            continue
        cands = [(p.poly.distance(q.poly), fp, q) for fp in small for q in fp.pads if q.net == p.net]
        if not cands:
            continue
        d, fp, q = min(cands, key=lambda t: t[0])
        g = [x for x in fp.pads if x.net == gnd]
        wrong = bool(g) and math.dist(g[0].center, p.center) < math.dist(q.center, p.center)
        rows.append((d, f"  pin {p.num:>3} {p.net:14} {d:6.3f} mm to {q.name}{'  GROUND PAD FACES PIN' if wrong else ''}"))
    for d, s in sorted(rows, reverse=True):
        print(s)

    print("parts (small-part pad -> nearest IC pin on the same net)")
    rows = []
    for fp in small:
        for q in fp.pads:
            if not q.net or q.net == gnd:
                continue
            pins = [p for p in icpins if p.net == q.net]
            if not pins:
                continue
            d, p = min(((q.poly.distance(p.poly), p) for p in pins), key=lambda t: t[0])
            rows.append((d, f"  {q.name:7} {q.net:14} {d:6.3f} mm to pin {p.num}"))
    for d, s in sorted(rows, reverse=True):
        print(s)

    print("ground (ground pad -> nearest legal via site, None = no site within 1.2 mm)")
    rows = []
    for fp in small:
        for q in fp.pads:
            if q.net == gnd:
                v = via_gap(b, q, a.via, a.clear, a.edge)
                rows.append((9 if v is None else v, f"  {q.name:7} {('None' if v is None else f'{v:6.3f} mm')}"))
    for d, s in sorted(rows, reverse=True):
        print(s)

    print("pairs (two-pad parts with both pads on IC pins)")
    for fp in small:
        sig = [q for q in fp.pads if q.net and q.net != gnd]
        if len(sig) != 2 or len({q.net for q in sig}) != 2:
            continue
        ds = []
        for q in sig:
            pins = [p for p in icpins if p.net == q.net]
            if not pins:
                break
            ds.append((min(q.poly.distance(p.poly) for p in pins), q.name))
        if len(ds) == 2:
            print(f"  {fp.ref:5} {ds[0][1]} {ds[0][0]:.3f} mm, {ds[1][1]} {ds[1][0]:.3f} mm, difference {abs(ds[0][0]-ds[1][0]):.3f} mm")

    print(f"fronts (IC signal pins with no free {a.front} mm channel straight out or at 45 degrees)")
    w = a.track + 2 * a.clear
    for p in icpins:
        if p.net == gnd or any(q.net == p.net for fp in small for q in fp.pads):
            continue
        dx, dy = p.center[0] - ic.x, p.center[1] - ic.y
        ux, uy = ((1 if dx > 0 else -1), 0) if abs(dx) >= abs(dy) else (0, (1 if dy > 0 else -1))
        x0, y0, x1, y1 = p.poly.bounds
        sx = (x1 if ux > 0 else x0) if ux else p.center[0]
        sy = (y1 if uy > 0 else y0) if uy else p.center[1]
        hits, ok = set(), False
        for ang in (0, 45, -45):
            r = math.radians(ang)
            vx, vy = ux * math.cos(r) - uy * math.sin(r), ux * math.sin(r) + uy * math.cos(r)
            ch = LineString([(sx, sy), (sx + a.front * vx, sy + a.front * vy)]).buffer(w / 2, cap_style=2)
            h = {q.name for fp in small for q in fp.pads if q.net != p.net and q.poly.intersects(ch)}
            if not h:
                ok = True
                break
            hits |= h
        if not ok:
            print(f"  pin {p.num:>3} {p.net:14} blocked by {', '.join(sorted(hits))}")

    ties = tie_gaps(fps, a.tie)
    if a.chain:
        print("chain (gap of each link, antenna pin to port)")
        start_ref, start_pin = a.chain[0].split(".")
        prev = [q for q in fps[start_ref].pads if q.num == start_pin]
        total = 0.0
        for ref in a.chain[1:-1]:
            fp = fps[ref]
            nets = {q.net for q in prev}
            pin_in = [q for q in fp.pads if q.net in nets]
            if not pin_in:
                print(f"  {ref}: no pad on {sorted(nets)}, chain order or nets wrong")
                break
            d = min(x.poly.distance(y.poly) for x in prev for y in pin_in)
            total += d
            print(f"  {prev[0].name:7} -> {pin_in[0].name:7} {d:6.3f} mm")
            prev = [q for q in fp.pads if q not in pin_in]
        port = [poly for l, n, poly in b["fixed_copper"] if n == a.chain[-1]]
        if port and prev:
            d = min(x.poly.distance(port[0]) for x in prev)
            total += d
            print(f"  {prev[0].name:7} -> port    {d:6.3f} mm")
        print(f"  sum of link gaps {total:.3f} mm")
        # shunts: small parts with one pad on a chain node and one on ground
        nodes = set()
        prev_nets = {q.net for q in fps[start_ref].pads if q.num == start_pin}
        for ref in a.chain[1:-1]:
            nodes |= {q.net for q in fps[ref].pads}
        nodes.add(a.chain[-1])
        node_copper = {}
        for fp in b["footprints"]:
            if fp.ref in a.chain[1:-1] or fp.ref == start_ref:
                for q in fp.pads:
                    if q.net in nodes:
                        node_copper.setdefault(q.net, []).append((fp.ref, q.poly))
        for l, n, poly in b["fixed_copper"]:
            if n in nodes:
                node_copper.setdefault(n, []).append(("port", poly))
        print("  shunts (gap from the shunt's node pad to the node's series pads or port)")
        print(f"  and whether the node pad sits on the path a {a.rf_track} mm track takes through that node")
        for fp in small:
            if fp.ref in a.chain:
                continue
            nets = {q.net for q in fp.pads}
            if gnd in nets and nets & nodes:
                q = [x for x in fp.pads if x.net in nodes][0]
                d = min(q.poly.distance(g) for r_, g in node_copper.get(q.net, []))
                ends = node_copper.get(q.net, [])
                verdict = ""
                if len(ends) >= 2:
                    # the series path through this node: from one piece of series copper to the
                    # other (a pad of each neighbouring series part, or a pad and the port)
                    (r1, g1), (r2, g2) = max(((x, y) for i, x in enumerate(ends) for y in ends[i + 1:]),
                                             key=lambda t: t[0][1].centroid.distance(t[1][1].centroid))
                    p1, p2 = nearest_points(g1, g2)
                    c1 = p1 if r1 == "port" else g1.centroid   # a track meets the port at its edge
                    c2 = p2 if r2 == "port" else g2.centroid
                    path = LineString([c1, c2]).buffer(a.rf_track / 2, cap_style=2)
                    if q.poly.intersects(path):
                        verdict = "inline (node pad on the series path)"
                    elif d == 0:
                        verdict = ("no branch, but the node pad only touches series copper off the path "
                                   f"(its edge is {q.poly.distance(LineString([c1, c2])):.3f} mm from the path's centre line)")
                    else:
                        verdict = f"OFF THE PATH: a {q.poly.distance(path):.3f} mm branch (stub) to reach it"
                if fp.ref in ties:
                    spec, gap, stretched = ties[fp.ref]
                    verdict += f"; documented tie {spec} {gap:.3f} mm"
                    if stretched:
                        verdict += (" TIE STRETCHED: longer than the part; the documented return takes "
                                    "precedence, so move the ground back to it and accept a short branch")
                print(f"    {fp.ref:5} on {q.net:12} {d:6.3f} mm  {verdict}")

    if a.tie:
        print("ties (vendor-mandated pad to pin)")
        for ref, (spec, gap, stretched) in ties.items():
            print(f"  {spec:20} {gap:6.3f} mm" + ("  TIE STRETCHED: longer than the part itself" if stretched else ""))


if __name__ == "__main__":
    main()
