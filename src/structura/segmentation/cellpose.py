"""Cellpose backend for the 2D track. Candidate for dense, roundish stones.

Targets Cellpose v4 (Cellpose-SAM): ``CellposeModel`` loads the ``cpsam`` model
by default and downloads its weights on first use. Heavy imports are local so the
package imports without the ``cellpose`` extra installed.
"""

from __future__ import annotations

from pathlib import Path

from .. import geo
from ..models import Feature
from ._common import label_mask_to_features


class CellposeSegmenter:
    """Stone segmentation via Cellpose-SAM (instance masks -> polygons)."""

    name = "cellpose"

    def __init__(
        self,
        gpu: bool = False,
        diameter: float | None = None,
        flow_threshold: float = 0.4,
        min_area: float = 1e-4,
    ) -> None:
        self.gpu = gpu
        self.diameter = diameter
        self.flow_threshold = flow_threshold
        self.min_area = min_area

    def segment(self, ortho_path: Path) -> list[Feature]:
        import numpy as np  # noqa: PLC0415
        from cellpose import models  # noqa: PLC0415

        array, transform, crs = geo.read_raster(ortho_path)

        # rasterio (bands, rows, cols) -> (rows, cols, channels), keep up to RGB.
        img = np.transpose(np.asarray(array), (1, 2, 0))[:, :, :3]

        model = models.CellposeModel(gpu=self.gpu)
        masks, _, _ = model.eval(
            img, diameter=self.diameter, flow_threshold=self.flow_threshold
        )

        # masks is an instance-label array (0 = background).
        return label_mask_to_features(
            masks,
            transform,
            crs,
            segmenter=self.name,
            source_raster=ortho_path,
            min_area=self.min_area,
        )
