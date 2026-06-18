# SPDX-License-Identifier: AGPL-3.0-or-later

"""Segment Anything (SAM) backend for the 2D track, via samgeo.

Uses ``segment-geospatial`` (samgeo): it runs SAM's automatic mask generation on
a (tiled) georeferenced orthophoto and writes a label raster that preserves the
source CRS/transform. We read that back and reuse the shared vectorisation path,
so SAM, Cellpose, and the classical backend all produce features identically.
Heavy imports are local so the package imports without the ``sam`` extra.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from .. import geo
from ..models import Feature
from ._common import label_mask_to_features

# Default SAM automatic-mask-generation grid (samgeo passes these to SAM).
_DEFAULT_SAM_KWARGS = {
    "points_per_side": 32,
    "pred_iou_thresh": 0.88,
    "stability_score_thresh": 0.95,
    "min_mask_region_area": 100,
}


class SamSegmenter:
    """Stone/surface segmentation via SAM automatic mask generation (samgeo)."""

    name = "sam"

    def __init__(
        self,
        model_type: str = "vit_h",
        sam_kwargs: dict | None = None,
        min_size: int = 100,
        min_area: float = 1e-4,
        checkpoint: Path | None = None,
    ) -> None:
        self.model_type = model_type
        self.sam_kwargs = sam_kwargs if sam_kwargs is not None else dict(_DEFAULT_SAM_KWARGS)
        self.min_size = min_size
        self.min_area = min_area
        self.checkpoint = checkpoint

    def segment(self, ortho_path: Path) -> list[Feature]:
        import numpy as np  # noqa: PLC0415
        from samgeo import SamGeo  # noqa: PLC0415

        sam = SamGeo(
            model_type=self.model_type,
            automatic=True,
            sam_kwargs=self.sam_kwargs,
            checkpoint=self.checkpoint,
        )

        with tempfile.TemporaryDirectory() as tmp:
            mask_tif = Path(tmp) / "sam_masks.tif"
            sam.generate(
                source=str(ortho_path),
                output=str(mask_tif),
                unique=True,  # one integer label per object
                min_size=self.min_size,
                batch=True,
                batch_sample_size=(512, 512),
            )
            # samgeo preserves the source georeferencing on the label raster.
            array, transform, crs = geo.read_raster(mask_tif)
            mask = np.asarray(array)[0]  # single-band label raster

        return label_mask_to_features(
            mask,
            transform,
            crs,
            segmenter=self.name,
            source_raster=ortho_path,
            min_area=self.min_area,
        )
