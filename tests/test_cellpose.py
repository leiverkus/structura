"""Cellpose backend test — skipped unless the `cellpose` extra is installed.

Runs a real (CPU) Cellpose-SAM segmentation on the synthetic ortho. This is a
local/manual check; CI does not install the cellpose extra, so it skips.
"""

from pathlib import Path

import pytest

pytest.importorskip("cellpose")
pytest.importorskip("rasterio")

from structura.models import FeatureType, Track  # noqa: E402
from structura.segmentation.cellpose import CellposeSegmenter  # noqa: E402


def test_cellpose_segment_runs(synthetic_ortho: Path) -> None:
    feats = CellposeSegmenter(gpu=False).segment(synthetic_ortho)
    for f in feats:
        assert f.track is Track.SEG_2D
        assert f.feature_type is FeatureType.STONE
        assert f.crs == "EPSG:32636"
        assert f.geometry.is_valid
        assert f.properties["segmenter"] == "cellpose"
