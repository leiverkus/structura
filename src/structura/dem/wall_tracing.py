# SPDX-License-Identifier: AGPL-3.0-or-later

"""Trace wall courses from a DEM as polylines (2.5D track).

A wall protrudes slightly from its surroundings, so it stands out in a
multiscale local-relief response far better than in the orthophoto.
"""

from __future__ import annotations

from pathlib import Path

from .. import geo
from ..models import Feature, FeatureType
from . import relief
from ._common import relief_response_to_features


class WallTracer:
    """Detect wall courses from DEM relief and emit WALL polyline features.

    Pipeline: multiscale local-relief response -> threshold (walls protrude) ->
    gap-bridge (binary closing) -> skeletonise -> polylines. Gap bridging tolerates
    partially destroyed / discontinuous walls.
    """

    name = "dem-wall-tracer"

    def __init__(
        self,
        gap_bridge_m: float = 0.3,
        threshold_k: float = 1.0,
        min_length_m: float = 0.5,
        simplify_m: float | None = None,
    ) -> None:
        self.gap_bridge_m = gap_bridge_m
        self.threshold_k = threshold_k
        self.min_length_m = min_length_m
        self.simplify_m = simplify_m

    def trace(self, dem_path: Path) -> list[Feature]:
        import numpy as np  # noqa: PLC0415

        array, transform, crs = geo.read_raster(dem_path)
        dem = np.asarray(array)[0]
        res = abs(transform.a)  # pixel size in world units

        response = relief.multiscale_relief(dem)
        threshold = float(np.mean(response)) + self.threshold_k * float(np.std(response))
        ridge = response > threshold

        return relief_response_to_features(
            ridge,
            transform,
            crs,
            tracer=self.name,
            source_raster=dem_path,
            feature_type=FeatureType.WALL,
            gap_bridge_px=round(self.gap_bridge_m / res),
            min_length=self.min_length_m,
            simplify_tol=self.simplify_m,
        )
