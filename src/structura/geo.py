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


def mask_to_polygons(mask: Any, transform: Any, crs: str) -> list[Any]:
    """Vectorise a boolean/label mask into georeferenced Shapely polygons.

    Used by the 2D track to turn SAM/Cellpose masks into stone/surface outlines.
    """
    raise NotImplementedError(
        "Vectorise mask via rasterio.features.shapes + shapely, applying `transform`."
    )


def skeleton_to_polylines(ridge_mask: Any, transform: Any, crs: str) -> list[Any]:
    """Turn a thin ridge/edge mask into georeferenced polylines.

    Used by the 2.5D track for wall courses and edges (skeletonise -> trace ->
    simplify). Must tolerate gaps from partially destroyed walls.
    """
    raise NotImplementedError(
        "Skeletonise (skimage), trace paths, simplify (shapely), apply `transform`."
    )
