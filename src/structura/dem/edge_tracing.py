# SPDX-License-Identifier: AGPL-3.0-or-later

"""Trace terrace/cut edges from a DEM as polylines (2.5D track).

Edges (terrace edges, cuts, pit rims) are surface discontinuities — they show up
as high slope rather than positive relief, so this traces a slope response.
"""

from __future__ import annotations

from pathlib import Path

from .. import geo
from ..models import Feature, FeatureType
from . import relief
from ._common import relief_response_to_features


class EdgeTracer:
    """Detect edges from DEM slope and emit EDGE polyline features.

    Pipeline: slope response -> threshold (edges are steep) -> skeletonise ->
    polylines. No gap bridging — edges are continuous discontinuities.
    """

    name = "dem-edge-tracer"

    def __init__(
        self,
        threshold_k: float = 1.0,
        min_length_m: float = 0.5,
        simplify_m: float | None = None,
    ) -> None:
        self.threshold_k = threshold_k
        self.min_length_m = min_length_m
        self.simplify_m = simplify_m

    def trace(self, dem_path: Path) -> list[Feature]:
        import numpy as np  # noqa: PLC0415

        array, transform, crs = geo.read_raster(dem_path)
        dem = np.asarray(array)[0]
        res = abs(transform.a)

        response = relief.slope(dem, resolution=res)
        threshold = float(np.mean(response)) + self.threshold_k * float(np.std(response))
        edges = response > threshold

        return relief_response_to_features(
            edges,
            transform,
            crs,
            tracer=self.name,
            source_raster=dem_path,
            feature_type=FeatureType.EDGE,
            gap_bridge_px=0,
            min_length=self.min_length_m,
            simplify_tol=self.simplify_m,
        )
