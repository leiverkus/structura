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


def skeleton_to_polylines(ridge_mask: Any, transform: Any, crs: str) -> list[Any]:
    """Turn a thin ridge/edge mask into georeferenced polylines.

    Used by the 2.5D track for wall courses and edges (skeletonise -> trace ->
    simplify). Must tolerate gaps from partially destroyed walls.
    """
    raise NotImplementedError(
        "Skeletonise (skimage), trace paths, simplify (shapely), apply `transform`."
    )
