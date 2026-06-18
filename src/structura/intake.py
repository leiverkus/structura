# SPDX-License-Identifier: AGPL-3.0-or-later

"""Intake of WebODM raster products (orthophoto + DEM).

Discovers georeferenced rasters delivered into the input directory and tags
them by kind so downstream tracks know what to consume.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path


class RasterKind(str, Enum):
    ORTHO = "ortho"  # RGB orthophoto -> 2D segmentation track
    DEM = "dem"      # elevation model -> 2.5D track


@dataclass(slots=True)
class RasterProduct:
    path: Path
    kind: RasterKind
    crs: str | None = None        # filled by reading the raster (geo extra)
    captured_on: date | None = None


def discover_inputs(input_dir: Path) -> list[RasterProduct]:
    """Find raster products under ``input_dir``.

    Heuristic by filename; refine to match the actual WebODM delivery layout
    (e.g. ``odm_orthophoto/odm_orthophoto.tif`` and ``odm_dem/dsm.tif``).
    """
    products: list[RasterProduct] = []
    for tif in sorted(input_dir.rglob("*.tif")):
        name = tif.name.lower()
        if "ortho" in name:
            products.append(RasterProduct(tif, RasterKind.ORTHO))
        elif "dem" in name or "dsm" in name or "dtm" in name:
            products.append(RasterProduct(tif, RasterKind.DEM))
    return products
