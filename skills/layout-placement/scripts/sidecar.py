"""The board's companion metadata, <board>.kicad_pcb.backplane.json, kept
through a save.

Backplane's KiCad (bp.4) reads companion versions 1 and 2 and always writes
version 2 (backplane_document_metadata.cpp):

- version 1 "items": an item's native fields (custom_properties,
  start_ending, end_ending, footprint) are applied to the board item with
  that key and from then on live in the .kicad_pcb itself; its other fields
  become that key's record in version 2's "extensions";
- version 2 "extensions" are kept as they are (empty records dropped);
- anything else at the top level is dropped, and so are native fields whose
  key is no item KiCad applies them to; with no extensions left, the file is
  removed.

move.py --save therefore:

1. before any change, reads the companion and refuses to go on when a save
   would lose part of it (an unknown version or shape, other top-level keys,
   native fields for a key that is no item on the board);
2. just before saving, reads the board file and the companion again and
   refuses to save when either changed since step 1 (another writer);
3. keeps a copy of the companion under the cache folder;
4. after KiCad's save, checks that every extension record is in the new
   companion and every migrated custom property is in the saved board. A
   missing extension record is put back (version 2, written atomically,
   read back); a missing property is reported with the copy's path.
"""
import copy
import hashlib
import json
import os
import re
import tempfile
import time

FORMAT = "backplane-kicad-metadata"
NATIVE = ("custom_properties", "start_ending", "end_ending", "footprint")


class Unsupported(Exception):
    pass


def path_of(board):
    return board + ".backplane.json"


def _sha(p):
    try:
        with open(p, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None


def expected(data):
    """What a bp.4 save keeps of this companion: (extension records by key,
    custom properties by key that move into the board file)."""
    if data["version"] == 2:
        return {k: v for k, v in data["extensions"].items() if v}, {}
    ext, props = {}, {}
    for key, entry in data["items"].items():
        rest = {n: v for n, v in entry.items() if n not in NATIVE}
        if rest:
            ext[key] = rest
        if entry.get("custom_properties"):
            props[key] = entry["custom_properties"]
    return ext, props


class Snapshot:
    """The companion file and the board file as they were before a change."""

    def __init__(self, board, known_keys):
        self.board, self.path = board, path_of(board)
        self.board_sha = _sha(board)
        try:
            with open(self.path, "rb") as f:
                self.raw = f.read()
        except FileNotFoundError:
            self.raw, self.data, self.ext, self.props = None, None, {}, {}
            return
        try:
            d = json.loads(self.raw)
        except ValueError as e:
            raise Unsupported(f"{self.path} is not JSON ({e})")
        if not (isinstance(d, dict) and d.get("format") == FORMAT and d.get("version") in (1, 2)
                and type(d.get("version")) is int):
            raise Unsupported(f"{self.path} is not {FORMAT} version 1 or 2")
        body = "items" if d["version"] == 1 else "extensions"
        if not isinstance(d.get(body), dict) or not all(isinstance(v, dict) for v in d[body].values()):
            raise Unsupported(f"{self.path}: version {d['version']} needs an object of objects in {body!r}")
        extra = sorted(set(d) - {"format", "version", body})
        if extra:
            raise Unsupported(f"{self.path} has top-level keys a save drops: {', '.join(extra)}")
        if d["version"] == 1:
            orphans = sorted(k for k, e in d["items"].items() if any(n in e for n in NATIVE) and k not in known_keys)
            if orphans:
                raise Unsupported(f"{self.path} has native fields for keys that are no item on the board, "
                                  f"which a save drops: {', '.join(orphans[:5])}")
        self.data = d
        self.ext, self.props = expected(d)

    def changed(self):
        """What changed on disk since the snapshot, or None."""
        out = []
        if _sha(self.board) != self.board_sha:
            out.append(self.board)
        try:
            with open(self.path, "rb") as f:
                now = f.read()
        except FileNotFoundError:
            now = None
        if now != self.raw:
            out.append(self.path)
        return out or None

    def backup(self):
        if self.raw is None:
            return None
        d = os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"),
                         "kistack", "layout-placement", "backups")
        os.makedirs(d, exist_ok=True)
        fd, p = tempfile.mkstemp(dir=d, prefix=time.strftime("%Y%m%d-%H%M%S-"),
                                 suffix="-" + os.path.basename(self.path))
        with os.fdopen(fd, "wb") as f:
            f.write(self.raw)
        return p


def _read(path):
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except FileNotFoundError:
        return None, None
    return raw, json.loads(raw)


def lost_extensions(want, data):
    have = (data or {}).get("extensions", {}) if (data or {}).get("version") == 2 else {}
    return {k: {n: v for n, v in rec.items() if have.get(k, {}).get(n) != v}
            for k, rec in want.items() if any(have.get(k, {}).get(n) != v for n, v in rec.items())}


def lost_properties(props, board_text):
    out = []
    for key, ps in props.items():
        for name, value in ps.items():
            # items keep them as (custom_property ...), the board root as (property ...)
            pat = r'\((?:custom_)?property\s+"%s"\s+"%s"' % (re.escape(json.dumps(name)[1:-1]), re.escape(json.dumps(value)[1:-1]))
            if not re.search(pat, board_text):
                out.append(f"{key}:{name}")
    return out


def after_save(snap):
    """After KiCad's save. Returns a message; raises OSError or ValueError
    when the companion could not be kept."""
    if snap.data is None:
        return None
    with open(snap.board) as f:
        props = lost_properties(snap.props, f.read())
    if props:
        raise ValueError(f"the saved board lacks custom properties {props[:5]} from {os.path.basename(snap.path)}")
    raw, data = _read(snap.path)
    lost = lost_extensions(snap.ext, data)
    if not lost:
        n = len(snap.ext)
        return (f"{os.path.basename(snap.path)}: {n} extension record{'' if n == 1 else 's'} kept"
                + (f", {len(snap.props)} item{'s' if len(snap.props) != 1 else ''}' custom properties moved into the "
                   "board file" if snap.props else ""))
    merged = copy.deepcopy(data) if data and data.get("version") == 2 else {"format": FORMAT, "version": 2,
                                                                            "extensions": {}}
    for k, rec in lost.items():
        merged["extensions"].setdefault(k, {}).update(copy.deepcopy(rec))
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(snap.path)), prefix=".backplane.json.")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(merged, f, indent=2)
            f.write("\n")
        if _read(snap.path)[0] != raw:
            raise OSError(f"{snap.path} changed while being restored")
        os.replace(tmp, snap.path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    still = lost_extensions(snap.ext, _read(snap.path)[1])
    if still:
        raise ValueError(f"{snap.path} still lacks extension records {sorted(still)[:5]}")
    return (f"{os.path.basename(snap.path)}: put back {len(lost)} extension record"
            f"{'' if len(lost) == 1 else 's'} the save dropped: {', '.join(sorted(lost)[:6])}")
