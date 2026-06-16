"""Tests for the 2.5D edge tracer (requires the geo extra)."""

from pathlib import Path

import pytest

pytest.importorskip("rasterio")
pytest.importorskip("skimage")
pytest.importorskip("shapely")

from structura.dem.edge_tracing import EdgeTracer  # noqa: E402
from structura.models import FeatureType, Track  # noqa: E402


def test_edge_tracer_finds_step(synthetic_dem_step: Path) -> None:
    feats = EdgeTracer().trace(synthetic_dem_step)
    assert len(feats) >= 1
    for f in feats:
        assert f.track is Track.DEM_25D
        assert f.feature_type is FeatureType.EDGE
        assert f.crs == "EPSG:32636"
        assert f.geometry.geom_type == "LineString"
        assert f.geometry.is_valid
        assert f.properties["tracer"] == "dem-edge-tracer"
