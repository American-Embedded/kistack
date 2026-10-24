#!/usr/bin/env python3
"""Move, rotate or flip footprints over KiCad IPC, as one undoable commit.

    move.py board.kicad_pcb C4=146.2,101.89,90 L1=150.1,99.6,0,B [--save]

Each argument is REF=x,y,rotation[,F|B] in millimetres and degrees (absolute,
y down, as KiCad shows them). F or B puts the part on that side. Without
--save the board changes in the server only: the checks in this folder read
the server, so you can try a move and check it before saving. kicad-cli DRC
reads the file, so save before running it.

Every argument is checked before KiCad is asked anything, a part may appear
once per call, and its reference must be unique on the board. A side change
is KiCad's own flip (pads, courtyard and graphics mirrored), committed
first; then the poses are set in one commit. KiCad's answer for each part
must match the request, or that commit is dropped. After it the footprint
count, the net of every fixed copper shape, each moved part's pose and the
side of its SMD pads are read back. If anything differs, the parts are put
back (flipped back, old poses), the board is read back again, and nothing is
saved. The script exits non-zero whenever the board was not changed as
asked, and says whether putting the parts back worked.

With --save, the board's companion metadata (<board>.backplane.json) is
kept (sidecar.py): before anything changes the script refuses a companion
that a save would lose part of, it refuses to save when the board or the
companion changed on disk meanwhile, and after the save it checks that
every extension record and custom property survived, putting back an
extension record the save dropped.
"""
import argparse
import json
import math
import os
import sys

from kipy.proto.board.board_commands_pb2 import BoardFlipDirection, FlipItems, FlipItemsResponse
from kipy.proto.board.board_types_pb2 import BoardLayer, FootprintInstance, PadType
from kipy.proto.common.commands.editor_commands_pb2 import ItemStatusCode, UpdateItems, UpdateItemsResponse
from kipy.util import pack_any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ipc_board  # noqa: E402
import sidecar  # noqa: E402


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


def flip(b, ids, message):
    """One commit flipping these footprints to the other side, mirrored as
    KiCad's own flip does. Returns None when every one flipped, else the
    reason, after dropping the commit."""
    if not ids:
        return None
    c = b.begin_commit()
    try:
        cmd = FlipItems()
        cmd.header.document.CopyFrom(b._doc)
        cmd.direction = BoardFlipDirection.BFD_LEFT_RIGHT
        for i in ids:
            cmd.items.add().value = i
        r = b._kicad.send(cmd, FlipItemsResponse)
        bad = [f"{i[:8]}: {ItemStatusCode.Name(got.status.code)} {got.status.error_message}"
               for i, got in zip(ids, r.flipped_items) if got.status.code != ItemStatusCode.ISC_OK]
        if len(r.flipped_items) != len(ids):
            bad.append(f"KiCad answered {len(r.flipped_items)} items for {len(ids)}")
    except BaseException:
        b.drop_commit(c)
        raise
    if bad:
        b.drop_commit(c)
        return "; ".join(bad)
    b.push_commit(c, message)
    return None


def side_of(f):
    return BoardLayer.BL_B_Cu if f.layer == BoardLayer.BL_B_Cu else BoardLayer.BL_F_Cu


def wrong(b, wants, refs):
    """What reads back differently from the poses wanted: position,
    orientation, side, and SMD pads that are not on the part's side."""
    by_id = {f.id.value: f for f in b.get_footprints()}
    out = []
    for want, ref in zip(wants, refs):
        got = by_id.get(want.id.value)
        if got is None:
            out.append(f"{ref} is gone")
            continue
        if not same(want, pose(ref, got.id.value, got.position.x, got.position.y, got.orientation.degrees,
                               got.layer)):
            out.append(f"{ref} reads back at {got.position.x / 1e6:.4f},{got.position.y / 1e6:.4f},"
                       f"{got.orientation.degrees:.1f} {'B' if got.layer == BoardLayer.BL_B_Cu else 'F'}")
            continue
        # an SMD pad's copper must not be on the other side only (paste-only
        # apertures have no copper and are left alone)
        other = BoardLayer.BL_F_Cu if side_of(got) == BoardLayer.BL_B_Cu else BoardLayer.BL_B_Cu
        for pd in got.definition.pads:
            lays = set(pd.padstack.layers)
            if pd.pad_type == PadType.PT_SMD and other in lays and side_of(got) not in lays:
                out.append(f"{ref} pad {pd.number} is on the other side")
                break
    return out


def restore(b, flips, before, refs, count):
    """Put the parts back (flip back, then the old poses) and say whether
    the board reads back as it was."""
    undo = flip(b, flips, "undo flip") or update(b, before, "undo move " + " ".join(refs))
    left = [undo] if undo else wrong(b, before, refs)
    if len(b.get_footprints()) != count:
        left.append("the footprint count still differs")
    if not left:
        return "the parts were put back where they were"
    return "putting the parts back did not work (" + "; ".join(left) + "): inspect the board"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("moves", nargs="+")
    ap.add_argument("--save", action="store_true")
    a = ap.parse_args()
    moves = parse(a.moves)
    loaded = ipc_board.load(a.board)
    b = loaded["board"]
    snap = None
    if a.save:
        # the companion metadata and the board file as they are now, before
        # any change: refused if the companion is not metadata we can keep
        known = {"root"}
        for f in b.get_footprints():
            known.add(f.id.value)
            known.update(p.id.value for p in f.definition.pads)
        known.update(sh.id.value for sh in b.get_shapes())
        try:
            snap = sidecar.Snapshot(loaded["path"], known)
        except sidecar.Unsupported as e:
            sys.exit(f"{e}; --save would lose it, so nothing was changed")
    all_fps = b.get_footprints()
    count = len(all_fps)
    fps, seen = {}, {}
    for f in all_fps:
        r = f.reference_field.text.value
        seen[r] = seen.get(r, 0) + 1
        fps[r] = f
    missing = [r for r, *_ in moves if r not in fps]
    if missing:
        sys.exit("no footprint " + " ".join(missing) + f" on {a.board}; nothing changed")
    shared = [r for r, *_ in moves if seen[r] > 1]
    if shared:
        sys.exit("more than one footprint has the reference " + " ".join(shared) + "; give each a unique "
                 "reference first; nothing changed")
    # bp.4's footprint update drops a footprint's custom properties (the
    # board file's (custom_property ...), and v1 companion ones applied at
    # load): refuse to move such a part rather than lose them
    with open(loaded["path"]) as fh:
        text = fh.read()
    try:
        with open(sidecar.path_of(loaded["path"])) as fh:
            comp = json.load(fh)
        v1_props = {k for k, e in comp.get("items", {}).items() if isinstance(e, dict) and e.get("custom_properties")} \
            if comp.get("version") == 1 else set()
    except (OSError, ValueError, AttributeError):
        v1_props = set()
    held = []
    for ref, *_ in moves:
        fid = fps[ref].id.value
        i = text.find(f'(uuid "{fid}")')
        j = text.find("\n\t(footprint ", i) if i >= 0 else -1
        block = text[i:j if j >= 0 else len(text)] if i >= 0 else ""
        if "(custom_property " in block or fid in v1_props:
            held.append(ref)
    if held:
        sys.exit(" ".join(held) + " ha" + ("s" if len(held) == 1 else "ve") + " custom properties, which this "
                 "KiCad's footprint update drops; move " + ("it" if len(held) == 1 else "them")
                 + " in KiCad itself. Nothing was changed")
    nets_before = {sh.id.value: sh.net.name for sh in b.get_shapes()}
    refs = [m[0] for m in moves]
    before, changed, flips = [], [], []
    for ref, x, y, rot, side in moves:
        f = fps[ref]
        before.append(pose(ref, f.id.value, f.position.x, f.position.y, f.orientation.degrees, f.layer))
        layer = side_of(f) if side is None else (BoardLayer.BL_B_Cu if side == "B" else BoardLayer.BL_F_Cu)
        if layer != side_of(f):
            flips.append(f.id.value)
        # send only id, position, orientation and layer: a full footprint makes KiCad
        # rebuild its graphics, which leaves rounding in the stored courtyards
        changed.append(pose(ref, f.id.value, round(x * 1e6), round(y * 1e6), rot, layer))
    # A side change is KiCad's flip (pads, courtyard and graphics mirrored to
    # the other side), committed on its own; then every pose is set.
    why = flip(b, flips, "flip " + " ".join(r for r, c in zip(refs, changed) if c.id.value in flips))
    if why:
        sys.exit(f"KiCad did not flip the parts ({why}); the commit was dropped, nothing changed")
    try:
        why = update(b, changed, "move " + " ".join(refs))
    except BaseException as e:
        if not flips:
            raise
        sys.exit(f"moving the parts failed ({type(e).__name__}: {e}); "
                 + restore(b, flips, before, refs, count) + "; not saved")
    if why and not flips:
        sys.exit(f"KiCad did not apply the move as asked ({why}); the commit was dropped, nothing changed")
    if why:
        sys.exit(f"KiCad did not apply the move as asked ({why}); the commit was dropped; "
                 + restore(b, flips, before, refs, count) + "; not saved")
    problems = []
    now = len(b.get_footprints())
    if now != count:
        problems.append(f"footprint count changed from {count} to {now}")
    moved_nets = [(k, v, sh.net.name) for sh in b.get_shapes()
                  for k, v in [(sh.id.value, nets_before.get(sh.id.value))] if v != sh.net.name]
    if moved_nets:
        problems.append("fixed copper changed net: " + ", ".join(f"{k[:8]} {v} -> {n}" for k, v, n in moved_nets))
    problems += wrong(b, changed, refs)
    if problems:
        sys.exit("; ".join(problems) + "; " + restore(b, flips, before, refs, count) + "; not saved")
    for f in b.get_footprints():
        r = f.reference_field.text.value
        if r in refs:
            print(f"{r:6s} {f.position.x / 1e6:.4f} {f.position.y / 1e6:.4f} {f.orientation.degrees:.1f}"
                  f" {'B' if f.layer == BoardLayer.BL_B_Cu else 'F'}")
    if a.save:
        changed = snap.changed()
        if changed:
            sys.exit(", ".join(changed) + " changed on disk since this script started (another writer?); "
                     + restore(b, flips, before, refs, count) + "; not saved")
        kept = snap.backup()
        b.save()
        try:
            msg = sidecar.after_save(snap)
        except (OSError, ValueError) as e:
            sys.exit(f"saved {loaded['path']}, but its companion metadata was not kept ({e}); "
                     f"the earlier {os.path.basename(snap.path)} is at {kept}")
        print(f"saved {loaded['path']}")
        if msg:
            print(msg)
    else:
        print("not saved: the change is in the KiCad server only (--save writes the board)")


if __name__ == "__main__":
    main()
