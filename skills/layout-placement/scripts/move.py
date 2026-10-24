#!/usr/bin/env python3
"""Move, rotate or flip footprints over KiCad IPC, as one undoable commit.

    move.py board.kicad_pcb C4=146.2,101.89,90 L1=150.1,99.6,0,B [--save]

Each argument is REF=x,y,rotation[,F|B] in millimetres and degrees (absolute,
y down, as KiCad shows them). F or B puts the part on that side. Without
--save the board changes in the server only: the checks in this folder read
the server, so you can try a move and check it before saving. kicad-cli DRC
reads the file, so save before running it.

Every argument is checked before KiCad is asked anything, and a part may
appear once per call. KiCad's answer for each part must match the request,
or the commit is dropped and nothing changes. After the commit the footprint
count, the net of every fixed copper shape and each moved part's position
are read back; if any differ, the parts are put back where they were in a
second commit and nothing is saved. The script exits non-zero whenever the
board was not changed as asked.
"""
import argparse
import math
import os
import sys

from kipy.proto.board.board_types_pb2 import BoardLayer, FootprintInstance
from kipy.proto.common.commands.editor_commands_pb2 import ItemStatusCode, UpdateItems, UpdateItemsResponse
from kipy.util import pack_any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ipc_board  # noqa: E402


def parse(moves):
    out, refs = [], []
    for m in moves:
        ref, eq, spec = m.partition("=")
        v = spec.split(",")
        try:
            x, y, rot = (float(t) for t in v[:3])
        except ValueError:
            x = y = rot = float("nan")
        side = v[3].upper() if len(v) == 4 else None
        if not eq or not ref or len(v) not in (3, 4) or not all(map(math.isfinite, (x, y, rot))) \
                or side not in (None, "F", "B"):
            sys.exit(f"bad move {m!r}: expected REF=x,y,rotation[,F|B] in mm and degrees")
        out.append((ref, x, y, rot, side))
        refs.append(ref)
    dup = sorted({r for r in refs if refs.count(r) > 1})
    if dup:
        sys.exit("each part may appear once per call; repeated: " + " ".join(dup))
    return out


def pose(ref, fid, x_nm, y_nm, deg, layer):
    p = FootprintInstance()
    p.id.value = fid
    p.position.x_nm = x_nm
    p.position.y_nm = y_nm
    p.orientation.value_degrees = deg
    p.layer = layer
    return p


def same(p, q):
    d = (p.orientation.value_degrees - q.orientation.value_degrees) % 360.0
    return (p.position.x_nm == q.position.x_nm and p.position.y_nm == q.position.y_nm
            and min(d, 360.0 - d) < 1e-6 and p.layer == q.layer)


def update(b, items, message):
    """One commit with these partial footprint updates. Returns None when
    KiCad applied each as asked, else the reason, after dropping the commit."""
    c = b.begin_commit()
    try:
        cmd = UpdateItems()
        cmd.header.document.CopyFrom(b._doc)
        cmd.items.extend(pack_any(p) for p in items)
        r = b._kicad.send(cmd, UpdateItemsResponse)
        bad = []
        if len(r.updated_items) != len(items):
            bad.append(f"KiCad answered {len(r.updated_items)} items for {len(items)}")
        for want, got in zip(items, r.updated_items):
            f = FootprintInstance()
            if got.status.code != ItemStatusCode.ISC_OK or not got.item.Unpack(f):
                bad.append(f"{want.id.value[:8]}: {ItemStatusCode.Name(got.status.code)} {got.status.error_message}")
            elif not same(want, f):
                bad.append(f"{want.id.value[:8]}: KiCad placed it at {f.position.x_nm / 1e6:.4f},"
                           f"{f.position.y_nm / 1e6:.4f},{f.orientation.value_degrees:.1f}")
    except BaseException:
        b.drop_commit(c)
        raise
    if bad:
        b.drop_commit(c)
        return "; ".join(bad)
    b.push_commit(c, message)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("moves", nargs="+")
    ap.add_argument("--save", action="store_true")
    a = ap.parse_args()
    moves = parse(a.moves)
    loaded = ipc_board.load(a.board)
    b = loaded["board"]
    fps = {f.reference_field.text.value: f for f in b.get_footprints()}
    missing = [r for r, *_ in moves if r not in fps]
    if missing:
        sys.exit("no footprint " + " ".join(missing) + f" on {a.board}; nothing changed")
    count = len(fps)
    nets_before = {sh.id.value: sh.net.name for sh in b.get_shapes()}
    before, changed = [], []
    for ref, x, y, rot, side in moves:
        f = fps[ref]
        before.append(pose(ref, f.id.value, f.position.x, f.position.y, f.orientation.degrees, f.layer))
        # send only id, position, orientation and layer: a full footprint makes KiCad
        # rebuild its graphics, which leaves rounding in the stored courtyards
        layer = f.layer if side is None else (BoardLayer.BL_B_Cu if side == "B" else BoardLayer.BL_F_Cu)
        changed.append(pose(ref, f.id.value, round(x * 1e6), round(y * 1e6), rot, layer))
    refs = [m[0] for m in moves]
    why = update(b, changed, "move " + " ".join(refs))
    if why:
        sys.exit(f"KiCad did not apply the move as asked ({why}); the commit was dropped, nothing changed")
    now = b.get_footprints()
    problems = []
    if len(now) != count:
        problems.append(f"footprint count changed from {count} to {len(now)}")
    moved_nets = [(k, v, sh.net.name) for sh in b.get_shapes()
                  for k, v in [(sh.id.value, nets_before.get(sh.id.value))] if v != sh.net.name]
    if moved_nets:
        problems.append("fixed copper changed net: " + ", ".join(f"{k[:8]} {v} -> {n}" for k, v, n in moved_nets))
    by_id = {f.id.value: f for f in now}
    for want, ref in zip(changed, refs):
        got = by_id.get(want.id.value)
        if got is None or not same(want, pose(ref, got.id.value, got.position.x, got.position.y,
                                              got.orientation.degrees, got.layer)):
            problems.append(f"{ref} did not read back where it was put")
    if problems:
        undo = update(b, before, "undo move " + " ".join(refs))
        state = "the parts were put back" if undo is None else f"putting the parts back failed too ({undo})"
        sys.exit("; ".join(problems) + f"; {state}; not saved")
    for f in b.get_footprints():
        r = f.reference_field.text.value
        if r in refs:
            print(f"{r:6s} {f.position.x / 1e6:.4f} {f.position.y / 1e6:.4f} {f.orientation.degrees:.1f}"
                  f" {'B' if f.layer == BoardLayer.BL_B_Cu else 'F'}")
    if a.save:
        b.save()
        print(f"saved {loaded['path']}")
    else:
        print("not saved: the change is in the KiCad server only (--save writes the board)")


if __name__ == "__main__":
    main()
