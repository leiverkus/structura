"""Shared test fixtures."""

from pathlib import Path

import pytest

# Canonical project CRS (UTM 36N, metric) and a 1 cm pixel grid.
TEST_CRS = "EPSG:32636"
N_BLOBS = 2


@pytest.fixture
def synthetic_ortho(tmp_path: Path) -> Path:
    """Write a small georeferenced RGB GeoTIFF with two non-touching bright blobs.

    Two separated blobs on a dark background → Otsu cleanly separates fore- and
    background → exactly ``N_BLOBS`` connected components → a deterministic,
    assertable polygon count. The filename contains ``ortho`` so
    ``discover_inputs`` tags it as an orthophoto.
    """
    pytest.importorskip("rasterio")
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin

    height = width = 100
    array = np.full((3, height, width), 10, dtype="uint8")  # dark background
    array[:, 10:30, 10:30] = 230  # blob 1
    array[:, 60:90, 60:85] = 230  # blob 2 (different size, still separate)

    transform = from_origin(500000, 4500000, 0.01, 0.01)  # 1 cm pixels
    path = tmp_path / "odm_orthophoto.tif"
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=3,
        dtype="uint8",
        crs=TEST_CRS,
        transform=transform,
    ) as dst:
        dst.write(array)
    return path


def _write_dem(path: Path, dem) -> Path:
    """Write a single-band float32 DEM GeoTIFF at 5 cm pixels in TEST_CRS."""
    import rasterio
    from rasterio.transform import from_origin

    height, width = dem.shape
    transform = from_origin(500000, 4500000, 0.05, 0.05)  # 5 cm pixels
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype="float32",
        crs=TEST_CRS,
        transform=transform,
    ) as dst:
        dst.write(dem[None, :, :])
    return path


@pytest.fixture
def synthetic_dem(tmp_path: Path) -> Path:
    """A flat DEM with one raised horizontal ridge (a wall). Filename tags it DEM."""
    pytest.importorskip("rasterio")
    import numpy as np

    dem = np.full((100, 100), 100.0, dtype="float32")
    dem[48:52, :] = 100.20  # a 20 cm ridge across the whole width
    return _write_dem(tmp_path / "odm_dem.tif", dem)


@pytest.fixture
def synthetic_dem_step(tmp_path: Path) -> Path:
    """A flat DEM with a raised terrace half (a slope edge). Filename tags it DEM."""
    pytest.importorskip("rasterio")
    import numpy as np

    dem = np.full((100, 100), 100.0, dtype="float32")
    dem[:, 50:] = 100.50  # a 50 cm step → high slope along the boundary
    return _write_dem(tmp_path / "dem_step.tif", dem)
