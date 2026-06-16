"""Tests for the shared label-mask -> Feature wrapper (requires the geo extra)."""

import pytest

pytest.importorskip("rasterio")
pytest.importorskip("shapely")

import numpy as np  # noqa: E402
from rasterio.transform import from_origin  # noqa: E402

from structura.models import FeatureType, Track  # noqa: E402
from structura.segmentation._common import label_mask_to_features  # noqa: E402


def test_label_mask_to_features() -> None:
    mask = np.zeros((10, 10), dtype=np.int32)
    mask[1:3, 1:3] = 1
    mask[6:9, 6:9] = 2
    transform = from_origin(1000, 2000, 1.0, 1.0)  # 1 m pixels

    feats = label_mask_to_features(
        mask, transform, "EPSG:32636", segmenter="test", source_raster="ortho.tif"
    )

    assert len(feats) == 2
    for f in feats:
        assert f.feature_type is FeatureType.STONE
        assert f.track is Track.SEG_2D
        assert f.crs == "EPSG:32636"
        assert f.geometry.is_valid and f.geometry.area > 0
        assert f.properties == {"segmenter": "test", "source_raster": "ortho.tif"}


def test_label_mask_min_area_filters_all() -> None:
    mask = np.zeros((10, 10), dtype=np.int32)
    mask[1:3, 1:3] = 1
    transform = from_origin(1000, 2000, 1.0, 1.0)
    feats = label_mask_to_features(
        mask, transform, "EPSG:32636", segmenter="t", source_raster="o.tif", min_area=100
    )
    assert feats == []
