"""Tests for the 2.5D wall tracer (requires the geo extra)."""

from pathlib import Path

import pytest

pytest.importorskip("rasterio")
pytest.importorskip("skimage")
pytest.importorskip("shapely")

import numpy as np  # noqa: E402
from rasterio.transform import from_origin  # noqa: E402

from structura.dem._common import relief_response_to_features  # noqa: E402
from structura.dem.wall_tracing import WallTracer  # noqa: E402
from structura.models import FeatureType, Track  # noqa: E402


def test_wall_tracer_finds_ridge(synthetic_dem: Path) -> None:
    feats = WallTracer().trace(synthetic_dem)
    assert len(feats) >= 1
    for f in feats:
        assert f.track is Track.DEM_25D
        assert f.feature_type is FeatureType.WALL
        assert f.crs == "EPSG:32636"
        assert f.geometry.geom_type == "LineString"
        assert f.geometry.is_valid
        assert f.properties["tracer"] == "dem-wall-tracer"


def test_gap_bridging_merges_split_line() -> None:
    transform = from_origin(0, 0, 1.0, 1.0)
    mask = np.zeros((20, 20), dtype=bool)
    mask[10, 2:10] = True
    mask[10, 11:18] = True  # one-pixel gap at column 10

    without = relief_response_to_features(
        mask, transform, "EPSG:32636", tracer="t", source_raster="d.tif",
        feature_type=FeatureType.WALL, gap_bridge_px=0,
    )
    bridged = relief_response_to_features(
        mask, transform, "EPSG:32636", tracer="t", source_raster="d.tif",
        feature_type=FeatureType.WALL, gap_bridge_px=2,
    )
    assert len(without) == 2  # two separate segments
    assert len(bridged) == 1  # closing bridged the gap
