"""Smoke tests: the package imports and the skeleton wires together."""

from pathlib import Path

from structura import __version__
from structura.intake import RasterKind, discover_inputs
from structura.models import Feature, FeatureType, Track


def test_version() -> None:
    assert __version__


def test_discover_empty(tmp_path: Path) -> None:
    assert discover_inputs(tmp_path) == []


def test_discover_by_name(tmp_path: Path) -> None:
    (tmp_path / "odm_orthophoto.tif").touch()
    (tmp_path / "dsm.tif").touch()
    kinds = {p.kind for p in discover_inputs(tmp_path)}
    assert kinds == {RasterKind.ORTHO, RasterKind.DEM}


def test_feature_model() -> None:
    f = Feature(feature_type=FeatureType.WALL, geometry=None, crs="EPSG:32636", track=Track.DEM_25D)
    assert f.feature_type is FeatureType.WALL
    assert f.track.value == "2.5d"
