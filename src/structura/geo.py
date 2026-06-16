"""Georeferencing helpers: raster I/O and raster->vector conversion.

Requires the ``geo`` extra (rasterio, shapely, scikit-image). Imports are local
so the package imports cleanly without it installed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def read_raster(path: Path) -> tuple[Any, Any, str]:
    """Return (array, affine_transform, crs) for a raster.

    The affine transform + CRS are what make every derived vector georeferenced:
    pixel (col,row) -> world (x,y) via ``transform * (col, row)``.
    """
    import rasterio  # noqa: PLC0415

    with rasterio.open(path) as src:
        return src.read(), src.transform, str(src.crs)


def mask_to_polygons(
    mask: Any, transform: Any, crs: str, *, min_area: float = 0.0
) -> list[Any]:
    """Vectorise a boolean/label mask into georeferenced Shapely polygons.

    Used by the 2D track to turn SAM/Cellpose/classical masks into stone/surface
    outlines. ``transform`` carries the pixel size, so the returned geometries —
    and therefore ``min_area`` (a threshold in world units squared) — are in the
    raster CRS. ``crs`` is accepted for interface symmetry; the CRS is attached
    later at the :class:`~structura.models.Feature` level.

    Background pixels (label ``0``) are skipped. Each polygon is repaired with a
    zero-width buffer to fix any self-touching rings from the marching-squares
    output.
    """
    import numpy as np  # noqa: PLC0415
    from rasterio.features import shapes  # noqa: PLC0415
    from shapely.geometry import shape  # noqa: PLC0415

    # rasterio.features.shapes rejects int64; cast to a width it accepts and that
    # is stable across platforms.
    labels = np.asarray(mask).astype(np.int32)

    polygons: list[Any] = []
    for geom_dict, value in shapes(labels, mask=labels != 0, transform=transform):
        if value == 0:
            continue
        geom = shape(geom_dict).buffer(0)
        if geom.area >= min_area:
            polygons.append(geom)
    return polygons


_NEIGHBOURS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def skeleton_to_polylines(
    mask: Any,
    transform: Any,
    crs: str,
    *,
    min_length: float = 0.0,
    simplify_tol: float | None = None,
    prune_px: int = 3,
) -> list[Any]:
    """Turn a thin ridge/edge mask into georeferenced Shapely polylines.

    Skeletonises ``mask``, traces the 1-pixel skeleton into paths between nodes
    (endpoints / junctions), and maps pixel centres to world coordinates via
    ``transform``. Adjacent junction pixels are merged into one node (so a single
    crossing does not fragment into many tiny edges), and leaf spurs shorter than
    ``prune_px`` pixels are dropped. ``min_length`` / ``simplify_tol`` are in world
    units; ``crs`` is accepted for interface symmetry.
    """
    import numpy as np  # noqa: PLC0415
    from shapely.geometry import LineString  # noqa: PLC0415
    from skimage.morphology import skeletonize  # noqa: PLC0415

    skel = skeletonize(np.asarray(mask).astype(bool))
    coords = {(int(r), int(c)) for r, c in zip(*np.nonzero(skel), strict=False)}
    if not coords:
        return []

    def neighbours(p: tuple[int, int]) -> list[tuple[int, int]]:
        r, c = p
        return [(r + dr, c + dc) for dr, dc in _NEIGHBOURS if (r + dr, c + dc) in coords]

    degree = {p: len(neighbours(p)) for p in coords}
    endpoints = {p for p, d in degree.items() if d == 1}
    node_set = {p for p, d in degree.items() if d != 2}

    # Cluster adjacent node pixels (8-connectivity) so one junction is one node.
    cluster_id: dict[tuple[int, int], int] = {}
    cid = 0
    for start in node_set:
        if start in cluster_id:
            continue
        stack = [start]
        cluster_id[start] = cid
        while stack:
            cur = stack.pop()
            for n in neighbours(cur):
                if n in node_set and n not in cluster_id:
                    cluster_id[n] = cid
                    stack.append(n)
        cid += 1

    used: set[frozenset[tuple[int, int]]] = set()
    paths: list[list[tuple[int, int]]] = []

    def walk(start: tuple[int, int], step: tuple[int, int]) -> list[tuple[int, int]]:
        path = [start, step]
        used.add(frozenset((start, step)))
        prev, cur = start, step
        while degree[cur] == 2:
            nxts = [n for n in neighbours(cur) if n != prev]
            if not nxts or frozenset((cur, nxts[0])) in used:
                break
            nxt = nxts[0]
            used.add(frozenset((cur, nxt)))
            path.append(nxt)
            prev, cur = cur, nxt
        return path

    # Branches anchored at nodes; skip intra-cluster node-node steps.
    for p in node_set:
        for q in neighbours(p):
            edge = frozenset((p, q))
            if edge in used:
                continue
            if q in node_set:
                used.add(edge)
                if cluster_id[p] != cluster_id[q]:
                    paths.append([p, q])  # genuine short inter-junction link
                continue
            paths.append(walk(p, q))

    # Pure loops (no nodes): trace any remaining degree-2 pixels.
    for p in coords:
        if degree[p] == 2 and all(frozenset((p, n)) not in used for n in neighbours(p)):
            paths.append(walk(p, neighbours(p)[0]))

    # Drop leaf spurs shorter than prune_px pixels (junction/end-cap noise).
    def is_spur(path: list[tuple[int, int]]) -> bool:
        leaf = path[0] in endpoints or path[-1] in endpoints
        return leaf and len(path) <= prune_px

    lines: list[Any] = []
    for path in paths:
        if prune_px > 0 and is_spur(path):
            continue
        line = LineString([transform * (c + 0.5, r + 0.5) for r, c in path])
        if simplify_tol is not None:
            line = line.simplify(simplify_tol)
        if line.length > 0 and line.length >= min_length:
            lines.append(line)
    return lines
