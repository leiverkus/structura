# SPDX-License-Identifier: AGPL-3.0-or-later

"""Classical CV baseline for the 2D track (watershed / contour-based)."""

from __future__ import annotations

from pathlib import Path

from .. import geo
from ..models import Feature
from ._common import label_mask_to_features


class ClassicalSegmenter:
    """Edge/watershed segmentation baseline — no learned model.

    A cheap, deterministic comparison point for the evaluation, and the default
    backend that lets the pipeline run end-to-end without a model download or a
    GPU. The pipeline is intentionally simple (plumbing, not accuracy): Otsu
    thresholding drives the foreground/background markers, so the result is fully
    reproducible across runs and platforms.
    """

    name = "classical"

    def __init__(self, min_area: float = 1e-4) -> None:
        # Minimum polygon area to keep, in world units squared (CRS).
        self.min_area = min_area

    def segment(self, ortho_path: Path) -> list[Feature]:
        import numpy as np  # noqa: PLC0415
        from skimage.color import rgb2gray  # noqa: PLC0415
        from skimage.filters import sobel, threshold_otsu  # noqa: PLC0415
        from skimage.measure import label  # noqa: PLC0415
        from skimage.segmentation import watershed  # noqa: PLC0415

        array, transform, crs = geo.read_raster(ortho_path)

        # read_raster returns rasterio's (bands, rows, cols); move bands last.
        img = np.transpose(np.asarray(array), (1, 2, 0))
        # Normalise to float [0, 1] explicitly by dtype (avoid img_as_float heuristics).
        img = img.astype(np.float64)
        max_val = float(img.max())
        if max_val > 0:
            img = img / max_val

        if img.shape[2] >= 3:
            gray = rgb2gray(img[:, :, :3])
        else:
            gray = img[:, :, 0]

        gradient = sobel(gray)

        # Deterministic markers from a global Otsu threshold.
        thresh = threshold_otsu(gray)
        markers = np.where(gray > thresh, 2, 1).astype(np.int32)
        basins = watershed(gradient, markers)

        # One label per spatially separate foreground blob — this is the count
        # the tests assert against, and it is independent of basin numbering.
        foreground = basins == 2
        labeled = label(foreground)

        # Speckle is dropped by the world-unit area filter in mask_to_polygons.
        return label_mask_to_features(
            labeled,
            transform,
            crs,
            segmenter=self.name,
            source_raster=ortho_path,
            min_area=self.min_area,
        )
