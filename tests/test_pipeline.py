"""End-to-end pipeline tests (requires the geo extra)."""

from pathlib import Path

import pytest

pytest.importorskip("rasterio")
pytest.importorskip("skimage")
pytest.importorskip("geopandas")

import geopandas as gpd  # noqa: E402

from structura import pipeline  # noqa: E402
from structura.config import Settings  # noqa: E402


def _settings(input_dir: Path, output_path: Path) -> Settings:
    return Settings(
        input_dir=input_dir,
        sink="file",
        segmentation_backend="classical",
        gpu=False,
        gap_bridge_m=0.3,
        output_path=output_path,
        pg_dsn=None,
        pg_schema="public",
        pg_table="features",
        api_base_url=None,
        api_token=None,
    )


def test_run_end_to_end(synthetic_ortho: Path, tmp_path: Path) -> None:
    out = tmp_path / "features.gpkg"
    settings = _settings(synthetic_ortho.parent, out)

    features = pipeline.run(settings, write=True)

    assert len(features) == 2
    assert out.exists()
    gdf = gpd.read_file(out)
    assert len(gdf) == 2
    assert str(gdf.crs).upper().endswith("32636")


def test_run_traces_dem_to_polylines(synthetic_dem: Path, tmp_path: Path) -> None:
    out = tmp_path / "features.gpkg"
    settings = _settings(synthetic_dem.parent, out)

    features = pipeline.run(settings, write=True)

    # The DEM ridge yields at least one WALL polyline feature.
    assert any(f.feature_type.value == "wall" for f in features)
    assert all(
        f.geometry.geom_type == "LineString" for f in features if f.track.value == "2.5d"
    )
    gdf = gpd.read_file(out)
    assert (gdf.geometry.geom_type == "LineString").any()


def test_run_dry_run_writes_nothing(synthetic_ortho: Path, tmp_path: Path) -> None:
    out = tmp_path / "features.gpkg"
    settings = _settings(synthetic_ortho.parent, out)

    features = pipeline.run(settings, write=False)

    assert len(features) == 2
    assert not out.exists()
