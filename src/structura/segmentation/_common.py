"""Shared post-processing for 2D segmentation backends.

Every backend ends the same way: an integer instance-label mask is vectorised
into georeferenced polygons and wrapped as :class:`~structura.models.Feature`
objects. That step lives here so the classical, Cellpose, and SAM backends stay
consistent (same CRS handling, same ``properties`` shape).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .. import geo
from ..models import Feature, FeatureType, Track


def label_mask_to_features(
    mask: Any,
    transform: Any,
    crs: str,
    *,
    segmenter: str,
    source_raster: Path | str,
    min_area: float = 1e-4,
    feature_type: FeatureType = FeatureType.STONE,
) -> list[Feature]:
    """Vectorise an instance-label ``mask`` into 2D-track ``Feature`` objects.

    ``mask`` is an integer array (label 0 = background). ``min_area`` is in world
    units squared (CRS); ``transform``/``crs`` come from the source raster.
    """
    geoms = geo.mask_to_polygons(mask, transform, crs, min_area=min_area)
    return [
        Feature(
            feature_type=feature_type,
            geometry=geom,
            crs=crs,
            track=Track.SEG_2D,
            properties={"segmenter": segmenter, "source_raster": str(source_raster)},
        )
        for geom in geoms
    ]
