#!/usr/bin/env python3
"""Move, rotate or flip footprints over KiCad IPC, as one undoable commit.

    move.py board.kicad_pcb C4=146.2,101.89,90 L1=150.1,99.6,0,B [--save]

Each argument is REF=x,y,rotation[,F|B] in millimetres and degrees (absolute,
y down, as KiCad shows them). F or B puts the part on that side. Without
--save the board changes in the server only: the checks in this folder read
the server, so you can try a move and check it before saving. kicad-cli DRC
reads the file, so save before running it.
"""
import argparse
import sys

from kipy.proto.board.board_types_pb2 import BoardLayer, FootprintInstance
from kipy.proto.common.commands.editor_commands_pb2 import UpdateItems, UpdateItemsResponse
from kipy.util import pack_any

import ipc_board


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("moves", nargs="+")
    ap.add_argument("--save", action="store_true")
    a = ap.parse_args()
    b = ipc_board.load(a.board)["board"]
    fps = {f.reference_field.text.value: f for f in b.get_footprints()}
    refs = [m.split("=")[0] for m in a.moves]
    dup = sorted({r for r in refs if refs.count(r) > 1})
    if dup:
        sys.exit("each part may appear once per call; repeated: " + " ".join(dup))
    count = len(fps)
    nets_before = {sh.id.value: sh.net.name for sh in b.get_shapes()}
    changed = []
    for m in a.moves:
        ref, spec = m.split("=")
        if ref not in fps:
            sys.exit(f"no footprint {ref}")
        v = spec.split(",")
        # send only id, position, orientation and layer: a full footprint makes KiCad
        # rebuild its graphics, which leaves rounding in the stored courtyards
        p = FootprintInstance()
        p.id.value = fps[ref].id.value
        p.position.x_nm = round(float(v[0]) * 1e6)
        p.position.y_nm = round(float(v[1]) * 1e6)
        p.orientation.value_degrees = float(v[2])
        p.layer = fps[ref].layer
        if len(v) > 3:
            p.layer = BoardLayer.BL_B_Cu if v[3].upper() == "B" else BoardLayer.BL_F_Cu
        changed.append(p)
    c = b.begin_commit()
    try:
        cmd = UpdateItems()
        cmd.header.document.CopyFrom(b._doc)
        cmd.items.extend(pack_any(p) for p in changed)
        b._kicad.send(cmd, UpdateItemsResponse)
    except Exception:
        b.drop_commit(c)
        raise
    b.push_commit(c, "move " + " ".join(refs))
    after = len(b.get_footprints())
    if after != count:
        sys.exit(f"footprint count changed from {count} to {after}; undo this commit, do not save")
    changed_nets = [(k, v, sh.net.name) for sh in b.get_shapes()
                    for k, v in [(sh.id.value, nets_before.get(sh.id.value))] if v != sh.net.name]
    if changed_nets:
        sys.exit("fixed copper changed net, not saving: " +
                 ", ".join(f"{k[:8]} {v} -> {n}" for k, v, n in changed_nets))
    if a.save:
        b.save()
    for f in b.get_footprints():
        r = f.reference_field.text.value
        if r in {m.split("=")[0] for m in a.moves}:
            print(f"{r:6s} {f.position.x / 1e6:.4f} {f.position.y / 1e6:.4f} {f.orientation.degrees:.1f}"
                  f" {'B' if f.layer == BoardLayer.BL_B_Cu else 'F'}")


if __name__ == "__main__":
    main()
