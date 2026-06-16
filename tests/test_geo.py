"""Tests for geo.mask_to_polygons (requires the geo extra)."""

import pytest

pytest.importorskip("rasterio")
pytest.importorskip("shapely")

import numpy as np  # noqa: E402
from rasterio.transform import from_origin  # noqa: E402

from structura import geo  # noqa: E402

# 1 m pixels anchored at a known origin.
TRANSFORM = from_origin(1000, 2000, 1.0, 1.0)


def _two_label_mask() -> np.ndarray:
    mask = np.zeros((10, 10), dtype=np.int32)
    mask[1:3, 1:3] = 1  # 2x2 block -> 4 m^2
    mask[6:9, 6:9] = 2  # 3x3 block -> 9 m^2
    return mask


def test_mask_to_polygons_counts_and_georeferences() -> None:
    polys = geo.mask_to_polygons(_two_label_mask(), TRANSFORM, "EPSG:32636")
    assert len(polys) == 2
    # All geometry must sit inside the raster's world footprint.
    for poly in polys:
        minx, miny, maxx, maxy = poly.bounds
        assert 1000 <= minx <= maxx <= 1010
        assert 1990 <= miny <= maxy <= 2000
    # Areas are in world units (m^2): one 2x2 block and one 3x3 block.
    areas = sorted(round(p.area) for p in polys)
    assert areas == [4, 9]


def test_mask_to_polygons_min_area_filters() -> None:
    polys = geo.mask_to_polygons(_two_label_mask(), TRANSFORM, "EPSG:32636", min_area=100)
    assert polys == []


def test_mask_to_polygons_empty_mask() -> None:
    assert geo.mask_to_polygons(np.zeros((5, 5), dtype=np.int32), TRANSFORM, "EPSG:32636") == []
