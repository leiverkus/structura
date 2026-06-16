"""Shared post-processing for 2.5D DEM tracers.

Both tracers end the same way: a binary relief-response mask is (optionally)
gap-bridged, skeletonised into polylines, and wrapped as ``Feature`` objects.
That step lives here so ``WallTracer`` and ``EdgeTracer`` stay consistent
(parallel to ``segmentation/_common.label_mask_to_features``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .. import geo
from ..models import Feature, FeatureType, Track


def relief_response_to_features(
    response_mask: Any,
    transform: Any,
    crs: str,
    *,
    tracer: str,
    source_raster: Path | str,
    feature_type: FeatureType,
    gap_bridge_px: int = 0,
    min_length: float = 0.0,
    simplify_tol: float | None = None,
) -> list[Feature]:
    """Bridge gaps, skeletonise, and wrap a binary response into polyline features."""
    import numpy as np  # noqa: PLC0415
    from skimage.morphology import dilation, disk  # noqa: PLC0415

    mask = np.asarray(response_mask).astype(bool)
    if gap_bridge_px > 0:
        # Dilation connects collinear segments across small gaps; the subsequent
        # skeletonise in skeleton_to_polylines thins the result back to a centreline.
        # (Closing can't bridge gaps in 1-px-thin ridges — the disk erodes the bridge.)
        mask = dilation(mask, disk(gap_bridge_px))

    lines = geo.skeleton_to_polylines(
        mask, transform, crs, min_length=min_length, simplify_tol=simplify_tol
    )
    return [
        Feature(
            feature_type=feature_type,
            geometry=line,
            crs=crs,
            track=Track.DEM_25D,
            properties={"tracer": tracer, "source_raster": str(source_raster)},
        )
        for line in lines
    ]
