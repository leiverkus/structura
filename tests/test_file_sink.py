"""Tests for the FileSink (requires the geo extra)."""

import json
from pathlib import Path

import pytest

pytest.importorskip("geopandas")
pytest.importorskip("shapely")

import geopandas as gpd  # noqa: E402
from shapely.geometry import box  # noqa: E402

from structura.db.file import FileSink  # noqa: E402
from structura.models import Feature, FeatureType, Track  # noqa: E402


def _features() -> list[Feature]:
    return [
        Feature(
            feature_type=FeatureType.STONE,
            geometry=box(0, 0, 1, 1),
            crs="EPSG:32636",
            track=Track.SEG_2D,
            properties={"segmenter": "classical", "n": 1},
        ),
        Feature(
            feature_type=FeatureType.SURFACE,
            geometry=box(2, 2, 4, 4),
            crs="EPSG:32636",
            track=Track.SEG_2D,
            properties={},
        ),
    ]


def test_filesink_gpkg_roundtrip(tmp_path: Path) -> None:
    out = tmp_path / "out.gpkg"
    n = FileSink(out).write(_features())
    assert n == 2
    assert out.exists()

    gdf = gpd.read_file(out)
    assert len(gdf) == 2
    assert str(gdf.crs).upper().endswith("32636")
    assert {"feature_type", "track", "properties"} <= set(gdf.columns)
    props = json.loads(gdf.iloc[0]["properties"])
    assert props["segmenter"] == "classical"


def test_filesink_geojson(tmp_path: Path) -> None:
    out = tmp_path / "out.geojson"
    assert FileSink(out).write(_features()) == 2
    assert len(gpd.read_file(out)) == 2


def test_filesink_empty_returns_zero(tmp_path: Path) -> None:
    out = tmp_path / "empty.gpkg"
    assert FileSink(out).write([]) == 0
    assert not out.exists()


def test_filesink_mixed_crs_raises(tmp_path: Path) -> None:
    feats = _features()
    feats[1].crs = "EPSG:4326"
    with pytest.raises(AssertionError):
        FileSink(tmp_path / "mixed.gpkg").write(feats)


def test_filesink_bad_extension_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="extension"):
        FileSink(tmp_path / "out.shp").write(_features())
