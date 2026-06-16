"""SAM backend test — skipped unless the `sam` (samgeo) extra is installed.

Runs a real SAM automatic mask generation via samgeo on the synthetic ortho
(downloads the checkpoint on first use). Local/manual check; CI does not install
the sam extra, so it skips.
"""

from pathlib import Path

import pytest

pytest.importorskip("samgeo")
pytest.importorskip("rasterio")

from structura.models import FeatureType, Track  # noqa: E402
from structura.segmentation.sam import SamSegmenter  # noqa: E402


def test_sam_segment_runs(synthetic_ortho: Path) -> None:
    feats = SamSegmenter().segment(synthetic_ortho)
    for f in feats:
        assert f.track is Track.SEG_2D
        assert f.feature_type is FeatureType.STONE
        assert f.crs == "EPSG:32636"
        assert f.geometry.is_valid
        assert f.properties["segmenter"] == "sam"
