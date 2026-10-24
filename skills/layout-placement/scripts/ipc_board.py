"""Read a board's placement geometry from KiCad over IPC (kicad-python).

The board must already be open in the KiCad API server (Backplane: call the
kicad_ipc tool with kiapi.common.commands.OpenDocument first).  Positions are
millimetres, y down, as in KiCad.

    from ipc_board import load
    b = load("/path/board.kicad_pcb")          # finds the server holding that board
                                                # (or set KICAD_API_SOCKET=ipc://...)
    b = load(socket="ipc:///run/.../api.sock")  # or name the socket

Returns a dict with "footprints" (ref, value, x, y, rot, layer, courtyard,
pads), "outline" (shapely Polygon), "fixed_copper" [(layer, net, polygon)]
and "board" (the kipy Board, for edits).
"""
import glob
import math
import os
import sys

from kipy import KiCad
from kipy.board_types import to_concrete_board_shape
from kipy.proto.board.board_types_pb2 import BoardLayer, PadType
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import polygonize, unary_union

NM = 1e-6


def _mm(v):
    return (v.x * NM, v.y * NM)


class Pad:
    def __init__(self, ref, num, net, poly, center, layers, through):
        self.ref, self.num, self.net, self.poly, self.center = ref, num, net, poly, center
        self.layers, self.through = layers, through
        self.kind = "thru_hole" if through else "smd"

    @property
    def name(self):
        return f"{self.ref}.{self.num}"


class Footprint:
    def __init__(self, ref, value, x, y, rot, layer, courtyard, pads):
        self.ref, self.value, self.x, self.y, self.rot = ref, value, x, y, rot
        self.layer, self.courtyard, self.pads = layer, courtyard, pads


def _poly_from_polyline(pl):
    pts = [_mm(n.point) for n in pl.nodes if hasattr(n, "point")]
    return Polygon(pts) if len(pts) >= 3 else None


def _shape_segments(shape):
    """Line segments of a board graphic (segment, rectangle, polygon, arc, circle)."""
    if type(shape).__name__ == "BoardShape":
        # footprint graphics arrive as the generic type; get the concrete one
        shape = to_concrete_board_shape(shape)
    t = type(shape).__name__
    if t == "BoardSegment":
        return [(_mm(shape.start), _mm(shape.end))]
    if t == "BoardRectangle":
        (x0, y0), (x1, y1) = _mm(shape.top_left), _mm(shape.bottom_right)
        return [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
    if t == "BoardArc":
        s, m, e = _mm(shape.start), _mm(shape.mid), _mm(shape.end)
        return [(s, m), (m, e)]
    if t == "BoardCircle":
        c = _mm(shape.center)
        r = math.dist(c, _mm(shape.radius_point))
        pts = [(c[0] + r * math.cos(k * math.pi / 16), c[1] + r * math.sin(k * math.pi / 16)) for k in range(32)]
        return list(zip(pts, pts[1:] + pts[:1]))
    if t == "BoardPolygon":
        out = []
        for pwh in shape.polygons:
            pts = [_mm(n.point) for n in pwh.outline.nodes if hasattr(n, "point")]
            out += list(zip(pts, pts[1:] + pts[:1]))
        return out
    raise ValueError(f"unhandled board shape {t}")


def _polys(segs):
    lines = [LineString([a, b]) for a, b in segs if a != b]
    return list(polygonize(unary_union(lines))) if lines else []


def find_socket(board_path):
    """The Backplane API socket whose server has this board open."""
    if os.environ.get("KICAD_API_SOCKET"):
        return os.environ["KICAD_API_SOCKET"]
    target = os.path.realpath(board_path)
    seen = []
    for sock in glob.glob(f"/run/user/{os.getuid()}/backplane/kicad/*/api.sock"):
        try:
            k = KiCad(socket_path="ipc://" + sock, client_name="works.backplane.placement", timeout_ms=15000)
            d = k.get_board().document
            path = os.path.realpath(os.path.join(d.project.path, d.board_filename))
        except Exception as e:
            seen.append(f"{sock}: {type(e).__name__}")
            continue
        if path == target:
            return "ipc://" + sock
        seen.append(f"{sock}: {path}")
    raise SystemExit(f"no KiCad API server has {board_path} open; open it with kicad_ipc OpenDocument first, "
                     "or pass the socket. Servers seen:\n  " + "\n  ".join(seen))


def load(board_path=None, socket=None):
    k = KiCad(socket_path=socket or find_socket(board_path), client_name="works.backplane.placement", timeout_ms=30000)
    board = k.get_board()
    fps_raw = board.get_footprints()
    pads_raw = board.get_pads()
    front = board.get_pad_shapes_as_polygons(pads_raw, BoardLayer.BL_F_Cu)
    back = board.get_pad_shapes_as_polygons(pads_raw, BoardLayer.BL_B_Cu)
    pad_poly = {}
    for p, pf, pb in zip(pads_raw, front, back):
        # the shape query answers for any layer, so take the copper layers from the padstack
        through = p.pad_type in (PadType.PT_PTH, PadType.PT_NPTH)
        lays = set(p.padstack.layers)
        on_f = through or BoardLayer.BL_F_Cu in lays
        on_b = through or BoardLayer.BL_B_Cu in lays
        pl = pf if on_f else pb
        g = _poly_from_polyline(pl.outline) if pl is not None else None
        pad_poly[p.id.value] = (g, on_f, on_b, through)
    fps = []
    for f in fps_raw:
        ref = f.reference_field.text.value
        crt_layer = BoardLayer.BL_B_CrtYd if f.layer == BoardLayer.BL_B_Cu else BoardLayer.BL_F_CrtYd
        segs = []
        for it in f.definition.items:
            if getattr(it, "layer", None) == crt_layer and type(it).__name__ != "BoardText":
                segs += _shape_segments(it)
        crt = _polys(segs)
        pads = []
        for p in f.definition.pads:
            g, on_f, on_b, through = pad_poly.get(p.id.value, (None, False, False, False))
            if g is None:
                continue
            layers = (["F.Cu"] if on_f else []) + (["B.Cu"] if on_b else [])
            pads.append(Pad(ref, p.number, p.net.name or None, g, _mm(p.position), layers, through))
        fps.append(Footprint(ref, f.value_field.text.value, f.position.x * NM, f.position.y * NM,
                             f.orientation.degrees, "B.Cu" if f.layer == BoardLayer.BL_B_Cu else "F.Cu",
                             unary_union(crt) if crt else None, pads))
    edge, fixed = [], []
    for s in board.get_shapes():
        if s.layer == BoardLayer.BL_Edge_Cuts:
            edge += _shape_segments(s)
        elif s.layer in (BoardLayer.BL_F_Cu, BoardLayer.BL_B_Cu) and s.net and s.net.name:
            for poly in _polys(_shape_segments(s)):
                fixed.append(("F.Cu" if s.layer == BoardLayer.BL_F_Cu else "B.Cu", s.net.name, poly))
    missing = [f.ref for f in fps if f.courtyard is None]
    if missing:
        print("warning: no courtyard read for " + " ".join(missing), file=sys.stderr)
    outl = _polys(edge)
    return {"footprints": fps, "outline": max(outl, key=lambda p: p.area) if outl else None,
            "fixed_copper": fixed, "board": board}


def by_ref(b):
    return {fp.ref: fp for fp in b["footprints"]}


def pads_by_net(b):
    d = {}
    for fp in b["footprints"]:
        for p in fp.pads:
            if p.net:
                d.setdefault(p.net, []).append(p)
    return d
