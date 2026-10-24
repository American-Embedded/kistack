#!/usr/bin/env python3
"""Routability check for a placement: a greedy grid router tries
  1. every non-ground connection between the IC and the small parts (<= 4
     pads) and among the small parts (a minimum spanning tree per net), top
     layer only, shortest connections first
  2. every other IC signal pin to the board edge, vias to the bottom allowed
and reports what fails when routing shortest-first or longest-first.
A failure means the placement probably blocks that connection; a success is
feasibility under simple rules, not a finished route.

usage: route_check.py board.kicad_pcb --ic REF [--ground GND] [--no-escape NET ...] [--escape NET ...]
       [--track MM --clear MM --via MM --edge MM]
  --escape     nets that leave the board even though they also reach a small
               part (reset through its resistor, crystal pins that are GPIOs,
               the supply feed); they are routed to the edge from any of
               their pads
  --no-escape  nets that do not leave the board (supplies, internal nodes);
               by default every IC net that reaches a small part, and GND,
               is skipped for escapes
  --track --clear --via --edge  the rules to route with; each defaults to the
               strictest the board applies (rules.py: every net's class as
               KiCad resolves it, the board minimums, clearance overrides).
               Custom DRC rules are not evaluated: such a board needs all
               four flags. A flag looser than the board needs
               --rules-override. The grid is 0.05 mm.
Scope: one IC per run (run it again for each IC), parts of four pads or fewer
count as its local parts, local links use F.Cu only, and two copper layers
are modelled. A failure in this check is a heuristic's failure, not proof
that the board cannot be routed.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ipc_board as geom  # noqa: E402
import grid_router as W  # noqa: E402
import rules as R  # noqa: E402


def plan(b, ic, gnd):
    """Every non-ground connection a router will need near the IC: for each net
    that touches a small part (<= 4 pads), the edges of a minimum spanning tree
    over that net's pads (pad-edge gaps), shortest first."""
    small = {fp.ref for fp in b["footprints"] if len(fp.pads) <= 4 and fp.ref != ic.ref}
    bynet = {}
    for fp in b["footprints"]:
        for p in fp.pads:
            if p.net and p.net != gnd and p.kind == "smd" and (fp.ref in small or fp.ref == ic.ref):
                bynet.setdefault(p.net, []).append(p)
    links, local_nets = [], set()
    for net, ps in bynet.items():
        if not any(p.ref in small for p in ps) or len(ps) < 2:
            continue
        local_nets.add(net)
        used, rest = [ps[0]], ps[1:]
        while rest:
            d, a, c = min(((x.poly.distance(y.poly), x, y) for x in used for y in rest), key=lambda t: t[0])
            if a.ref != c.ref:
                links.append((d, f"{a.name} -> {c.name} ({net})", net, c, a))
            used.append(c)
            rest.remove(c)
    links.sort(key=lambda t: t[0])
    return links, local_nets


def run(path, rules, ic_ref, gnd, no_escape, order_links=None, order_esc=None, extra=()):
    b = geom.load(path)
    fps = geom.by_ref(b)
    if ic_ref not in fps:
        sys.exit(f"no footprint {ic_ref} on {path}")
    ic = fps[ic_ref]
    links, local = plan(b, ic, gnd)
    skip = (set(no_escape) | local | {gnd}) - set(extra)
    esc = []
    for p in sorted(ic.pads, key=lambda p: int(p.num) if p.num.isdigit() else 999):
        if p.net and p.net not in skip and p.net not in esc:
            esc.append(p.net)
    esc += [n for n in extra if n not in esc]
    li = order_links or list(range(len(links)))
    en = order_esc or esc
    w = W.Witness(b, rules)
    lf, ef = [], []
    for i in li:
        d, name, net, q, p = links[i]
        if w.route(net, [q.poly], [(0, p.poly)], allow_via=False, max_len_mm=12) is None:
            lf.append(i)
    netpads = geom.pads_by_net(b)
    for net in en:
        sp = [x.poly for x in netpads.get(net, [])] + [poly for n, poly in w.copper[0] if n == net]
        if w.route(net, sp, "edge", allow_via=True, max_len_mm=30) is None:
            ef.append(net)
    return links, esc, lf, ef


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("--ic", required=True)
    ap.add_argument("--ground", default="GND")
    ap.add_argument("--no-escape", nargs="*", default=[])
    ap.add_argument("--escape", nargs="*", default=[])
    R.add_flags(ap)
    a = ap.parse_args()
    rules = R.resolve(a.board, a, geom.load(a.board))
    # A placement that routes in only one order is fragile. Route twice,
    # shortest links first and longest links first, and report what fails in
    # either order.
    links, esc, lf1, ef1 = run(a.board, rules, a.ic, a.ground, a.no_escape, extra=a.escape)
    rev = list(range(len(links)))[::-1]
    _, _, lf2, ef2 = run(a.board, rules, a.ic, a.ground, a.no_escape, rev, esc[::-1], extra=a.escape)
    lf = sorted(set(lf1) | set(lf2))
    ef = [n for n in esc if n in set(ef1) | set(ef2)]
    print(f"local links routed in both orders: {len(links) - len(lf)}/{len(links)}")
    for i in lf:
        which = "both orders" if i in lf1 and i in lf2 else ("shortest-first" if i in lf1 else "longest-first")
        print(f"  FAILED {links[i][1]}  ({which})")
    if not lf1 or not lf2:
        print("all local links together: yes, " + ("shortest-first" if not lf1 else "longest-first"))
    else:
        print("all local links together: NO, neither order routes every local link; open a corridor before going on")
    print(f"escapes to the edge routed in both orders: {len(esc) - len(ef)}/{len(esc)}")
    for n in ef:
        which = "both orders" if n in ef1 and n in ef2 else ("pin order" if n in ef1 else "reverse order")
        print(f"  FAILED {n}  ({which})")
    both = [n for n in ef if n in ef1 and n in ef2]
    if both:
        print("escapes that failed in both orders: unresolved by this check, which is not proof the board cannot "
              "route them. Try a physical alternative (another edge, a via sooner, a rotation, moving the part "
              "in the way) and confirm the rules above are the board's before calling the placement blocked.")


if __name__ == "__main__":
    main()
