"""Deterministic grid router used as a routability witness.

Two copper layers (F.Cu = 0, B.Cu = 1), inner layers assumed to be ground
planes.  Each route keeps clearance to copper of other nets on its layer;
routed tracks and vias become obstacles for later nets.
"""
import heapq
import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

# Track width, clearance, via diameter and edge clearance come from the
# board (rules.py), never from defaults here. The grid and the via cost are
# the router's own.
GRID = 0.05
VIA_COST = 12.0
SEARCH_MARGIN = 0.01


class Witness:
    def __init__(self, board, rules):
        self.b = board
        self.track, self.clear, self.via, self.edge = rules.track, rules.clear, rules.via, rules.edge
        self.outline = board["outline"]
        x0, y0, x1, y1 = self.outline.bounds
        self.x0, self.y0 = x0, y0
        self.nx = int(math.ceil((x1 - x0) / GRID)) + 1
        self.ny = int(math.ceil((y1 - y0) / GRID)) + 1
        xs = x0 + np.arange(self.nx) * GRID
        ys = y0 + np.arange(self.ny) * GRID
        self.X, self.Y = np.meshgrid(xs, ys)
        # copper by layer: list of (net, polygon)
        self.copper = {0: [], 1: []}
        for fp in board["footprints"]:
            for p in fp.pads:
                lays = p.layers
                on_f = any(l in ("F.Cu", "*.Cu") for l in lays)
                on_b = any(l in ("B.Cu", "*.Cu") for l in lays)
                if on_f:
                    self.copper[0].append((p.net, p.poly))
                if on_b:
                    self.copper[1].append((p.net, p.poly))
        for layer, net, poly in board["fixed_copper"]:
            if layer == "F.Cu":
                self.copper[0].append((net, poly))
            elif layer == "B.Cu":
                self.copper[1].append((net, poly))
        inner = self.outline.buffer(-(self.edge + self.track / 2))
        self.inside = shapely.contains_xy(inner, self.X, self.Y)
        vinner = self.outline.buffer(-(self.edge + self.via / 2))
        self.via_inside = shapely.contains_xy(vinner, self.X, self.Y)
        ring = inner.difference(self.outline.buffer(-(self.edge + self.track / 2 + 2 * GRID)))
        self.edge_ring = shapely.contains_xy(ring, self.X, self.Y)
        self.routes = []

    def _mask(self, geom):
        if geom is None or geom.is_empty:
            return np.zeros(self.X.shape, bool)
        minx, miny, maxx, maxy = geom.bounds
        m = np.zeros(self.X.shape, bool)
        i0 = max(0, int((miny - self.y0) / GRID) - 1)
        i1 = min(self.ny, int((maxy - self.y0) / GRID) + 2)
        j0 = max(0, int((minx - self.x0) / GRID) - 1)
        j1 = min(self.nx, int((maxx - self.x0) / GRID) + 2)
        if i0 >= i1 or j0 >= j1:
            return m
        m[i0:i1, j0:j1] = shapely.contains_xy(geom, self.X[i0:i1, j0:j1], self.Y[i0:i1, j0:j1])
        return m

    def blocked(self, net, layer, r):
        # SEARCH_MARGIN keeps grid paths clear of the exact clearance on
        # diagonals; committed copper is then checked at the exact rule
        r = r + SEARCH_MARGIN
        others = [poly for n, poly in self.copper[layer] if n != net]
        u = unary_union(others).buffer(r, 8) if others else None
        return self._mask(u)

    def net_mask(self, net, layer, exclude=None):
        polys = [poly for n, poly in self.copper[layer] if n == net and poly is not exclude]
        return self._mask(unary_union(polys)) if polys else np.zeros(self.X.shape, bool)

    def route(self, net, start_polys, goal, allow_via=True, layers_start=(0,), max_len_mm=None):
        """goal: list of (layer, polygon) or the string 'edge'.  Returns path length or None."""
        r = self.clear + self.track / 2
        free = [self.inside & ~self.blocked(net, l, r) for l in (0, 1)]
        vfree = self.via_inside & ~self.blocked(net, 0, self.clear + self.via / 2) & ~self.blocked(net, 1, self.clear + self.via / 2)
        start = []
        for l in layers_start:
            sm = np.zeros(self.X.shape, bool)
            for sp in start_polys:
                sm |= self._mask(sp)
            sm &= free[l] | ~self.inside & False | sm  # start cells inside the start pad
            for i, j in zip(*np.nonzero(sm)):
                start.append((l, i, j))
        if goal == "edge":
            gmask = [self.edge_ring & free[0], self.edge_ring & free[1]]
        else:
            gmask = [np.zeros(self.X.shape, bool), np.zeros(self.X.shape, bool)]
            for l, gp in goal:
                gmask[l] |= self._mask(gp)
        if not start or not (gmask[0].any() or gmask[1].any()):
            return None
        gpts = [np.argwhere(gmask[l]) for l in (0, 1)]
        gall = np.vstack([g for g in gpts if len(g)])

        def h(i, j):
            d = np.abs(gall - (i, j))
            dd = np.min(np.maximum(d[:, 0], d[:, 1]) + 0.414 * np.minimum(d[:, 0], d[:, 1]))
            return float(dd)
        # use a coarse heuristic: distance to goal bbox centre is cheaper; compute exact once per node via cache
        gi0, gj0 = gall.min(0)
        gi1, gj1 = gall.max(0)

        def hb(i, j):
            di = max(gi0 - i, 0, i - gi1)
            dj = max(gj0 - j, 0, j - gj1)
            return max(di, dj) + 0.414 * min(di, dj)
        dist = {}
        prev = {}
        pq = []
        for s in start:
            dist[s] = 0.0
            heapq.heappush(pq, (hb(s[1], s[2]), 0.0, s))
        steps = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
                 (-1, -1, 1.4142), (-1, 1, 1.4142), (1, -1, 1.4142), (1, 1, 1.4142)]
        found = None
        limit = None if max_len_mm is None else max_len_mm / GRID
        while pq:
            fcost, g, node = heapq.heappop(pq)
            if g > dist.get(node, 1e18):
                continue
            l, i, j = node
            if gmask[l][i, j]:
                found = node
                break
            if limit is not None and g > limit:
                continue
            for di, dj, c in steps:
                ii, jj = i + di, j + dj
                if not (0 <= ii < self.ny and 0 <= jj < self.nx):
                    continue
                if not (free[l][ii, jj] or gmask[l][ii, jj]):
                    continue
                if di and dj and not (free[l][i + di, j] or free[l][i, j + dj]):
                    continue
                nn = (l, ii, jj)
                ng = g + c
                if ng < dist.get(nn, 1e18):
                    dist[nn] = ng
                    prev[nn] = node
                    heapq.heappush(pq, (ng + hb(ii, jj), ng, nn))
            if allow_via and vfree[i, j]:
                nn = (1 - l, i, j)
                ng = g + VIA_COST
                if ng < dist.get(nn, 1e18) and free[1 - l][i, j]:
                    dist[nn] = ng
                    prev[nn] = node
                    heapq.heappush(pq, (ng + hb(i, j), ng, nn))
        if found is None:
            return None
        path = [found]
        while path[-1] in prev:
            path.append(prev[path[-1]])
        path.reverse()
        if not self._commit(net, path):
            return None
        return dist[found] * GRID

    def _commit(self, net, path):
        """Build the route's copper, check it keeps the clearance to other
        nets and the edge, and add it only if it does."""
        def xy(n):
            return (self.x0 + n[2] * GRID, self.y0 + n[1] * GRID)

        def seg(pts):
            return LineString(pts).buffer(self.track / 2, 4) if len(pts) > 1 else Point(pts[0]).buffer(self.track / 2, 4)
        pieces, cur, pts = [], path[0][0], []
        for n in path:
            if n[0] != cur:
                if pts:
                    pieces.append((cur, seg(pts)))
                v = Point(xy(n)).buffer(self.via / 2, 12)
                pieces += [(0, v), (1, v)]
                cur, pts = n[0], [xy(n)]
            else:
                pts.append(xy(n))
        if pts:
            pieces.append((cur, seg(pts)))
        edge = self.outline.buffer(-self.edge + 0.0005)
        for layer, g in pieces:
            others = [p for n2, p in self.copper[layer] if n2 != net]
            if (others and unary_union(others).distance(g) < self.clear - 0.0005) or not edge.contains(g):
                return False
        for layer, g in pieces:
            self.copper[layer].append((net, g))
        self.routes.append({"net": net, "cells": len(path)})
        return True
