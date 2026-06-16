"""Tests for the classical 2D segmentation backend (requires the geo extra)."""

from pathlib import Path

import pytest

pytest.importorskip("rasterio")
pytest.importorskip("skimage")
pytest.importorskip("shapely")

from structura.models import FeatureType, Track  # noqa: E402
from structura.segmentation.classical import ClassicalSegmenter  # noqa: E402


def test_classical_segments_blobs(synthetic_ortho: Path) -> None:
    feats = ClassicalSegmenter().segment(synthetic_ortho)
    assert len(feats) == 2
    for f in feats:
        assert f.track is Track.SEG_2D
        assert f.feature_type is FeatureType.STONE
        assert f.crs == "EPSG:32636"
        assert f.geometry.is_valid
        assert f.geometry.area > 0
        assert f.properties["segmenter"] == "classical"


def test_classical_is_deterministic(synthetic_ortho: Path) -> None:
    seg = ClassicalSegmenter()
    first = sorted(f.geometry.wkt for f in seg.segment(synthetic_ortho))
    second = sorted(f.geometry.wkt for f in seg.segment(synthetic_ortho))
    assert first == second
