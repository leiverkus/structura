"""Tests for DEM relief derivatives (requires the geo extra)."""

import pytest

pytest.importorskip("skimage")

import numpy as np  # noqa: E402

from structura.dem import relief  # noqa: E402


def _ridge_dem() -> np.ndarray:
    dem = np.full((60, 60), 100.0, dtype=float)
    dem[28:32, :] = 100.2  # raised horizontal ridge
    return dem


def _step_dem() -> np.ndarray:
    dem = np.full((60, 60), 100.0, dtype=float)
    dem[:, 30:] = 100.5  # terrace step
    return dem


def test_local_relief_positive_on_ridge() -> None:
    lrm = relief.local_relief_model(_ridge_dem(), kernel=15)
    assert lrm.shape == (60, 60)
    # The ridge rows have higher residual than the flat background.
    assert lrm[30, 30] > lrm[5, 30]
    assert lrm[30, 30] > 0


def test_multiscale_relief_peaks_on_ridge() -> None:
    ms = relief.multiscale_relief(_ridge_dem())
    assert ms.shape == (60, 60)
    assert ms[30, 30] > ms[5, 30]


def test_slope_high_on_step() -> None:
    s = relief.slope(_step_dem(), resolution=0.05)
    assert s.shape == (60, 60)
    # Slope at the step boundary is much higher than on the flat interior.
    assert s[30, 29] > s[30, 5]
    assert s[30, 29] > s[30, 5] * 10


def test_hillshade_in_unit_range() -> None:
    hs = relief.hillshade(_ridge_dem(), resolution=0.05)
    assert hs.shape == (60, 60)
    assert float(hs.min()) >= 0.0 and float(hs.max()) <= 1.0
