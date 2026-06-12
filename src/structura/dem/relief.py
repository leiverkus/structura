"""Relief derivatives from a DEM — the signal a wall course stands out in.

A wall protrudes slightly from its surroundings, so it shows up in local relief
/ curvature far better than in the orthophoto. These derivatives feed the
``WallTracer``.
"""

from __future__ import annotations

from typing import Any


def hillshade(dem: Any, azimuth: float = 315.0, altitude: float = 45.0) -> Any:
    raise NotImplementedError


def slope(dem: Any) -> Any:
    raise NotImplementedError


def curvature(dem: Any) -> Any:
    raise NotImplementedError


def local_relief_model(dem: Any, kernel: int = 25) -> Any:
    """Residual relief (DEM minus smoothed DEM) — isolates small protrusions."""
    raise NotImplementedError
