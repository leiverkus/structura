"""Tests for geo.skeleton_to_polylines (requires the geo extra)."""

import pytest

pytest.importorskip("skimage")
pytest.importorskip("shapely")

import numpy as np  # noqa: E402
from rasterio.transform import from_origin  # noqa: E402

from structura import geo  # noqa: E402

TRANSFORM = from_origin(1000, 2000, 1.0, 1.0)  # 1 m pixels


def test_straight_line_one_polyline() -> None:
    mask = np.zeros((20, 20), dtype=bool)
    mask[10, 2:18] = True  # a horizontal bar
    lines = geo.skeleton_to_polylines(mask, TRANSFORM, "EPSG:32636")
    assert len(lines) == 1
    line = lines[0]
    # Endpoints sit within the raster footprint and span most of the width.
    minx, _, maxx, _ = line.bounds
    assert 1000 <= minx <= maxx <= 1020
    assert line.length > 10  # ~15 m bar


def test_blank_mask_returns_empty() -> None:
    assert geo.skeleton_to_polylines(np.zeros((10, 10), dtype=bool), TRANSFORM, "EPSG:32636") == []


def test_branches_kept_separate() -> None:
    # A T-shape: one horizontal bar + one vertical stem -> 3 branches from the junction.
    mask = np.zeros((20, 20), dtype=bool)
    mask[5, 2:18] = True
    mask[5:18, 10] = True
    lines = geo.skeleton_to_polylines(mask, TRANSFORM, "EPSG:32636")
    assert len(lines) == 3


def test_min_length_drops_short_lines() -> None:
    mask = np.zeros((20, 20), dtype=bool)
    mask[10, 2:18] = True
    assert geo.skeleton_to_polylines(mask, TRANSFORM, "EPSG:32636", min_length=1000) == []
