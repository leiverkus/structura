# SPDX-License-Identifier: AGPL-3.0-or-later

"""Relief derivatives from a DEM — the signal a wall course stands out in.

A wall protrudes slightly from its surroundings, so it shows up in local relief
/ curvature far better than in the orthophoto. These derivatives feed the
``WallTracer`` (ridge response) and ``EdgeTracer`` (slope response).

All functions take a 2D float DEM array; ``resolution`` is the pixel size in
world units (CRS), used where the gradient must be in real units. numpy/skimage
only — scipy stays a transitive dependency.
"""

from __future__ import annotations

from typing import Any


def _gradients(dem: Any, resolution: float) -> tuple[Any, Any]:
    import numpy as np  # noqa: PLC0415

    dzdy, dzdx = np.gradient(np.asarray(dem, dtype=float), resolution)
    return dzdx, dzdy


def slope(dem: Any, resolution: float = 1.0) -> Any:
    """Slope as the gradient magnitude (rise over run, in world units)."""
    import numpy as np  # noqa: PLC0415

    dzdx, dzdy = _gradients(dem, resolution)
    return np.hypot(dzdx, dzdy)


def hillshade(
    dem: Any, azimuth: float = 315.0, altitude: float = 45.0, resolution: float = 1.0
) -> Any:
    """Analytical hillshade in [0, 1] for a light source at (azimuth, altitude)."""
    import numpy as np  # noqa: PLC0415

    dzdx, dzdy = _gradients(dem, resolution)
    slope_rad = np.arctan(np.hypot(dzdx, dzdy))
    # Aspect measured clockwise from north.
    aspect = np.arctan2(dzdy, -dzdx)
    az = np.radians(360.0 - azimuth + 90.0)
    alt = np.radians(altitude)
    shaded = np.sin(alt) * np.cos(slope_rad) + np.cos(alt) * np.sin(slope_rad) * np.cos(
        az - aspect
    )
    return np.clip(shaded, 0.0, 1.0)


def curvature(dem: Any, resolution: float = 1.0) -> Any:
    """Laplacian curvature (sum of second derivatives); ridges are negative."""
    import numpy as np  # noqa: PLC0415

    dzdx, dzdy = _gradients(dem, resolution)
    dxx = np.gradient(dzdx, resolution, axis=1)
    dyy = np.gradient(dzdy, resolution, axis=0)
    return dxx + dyy


def local_relief_model(dem: Any, kernel: int = 25) -> Any:
    """Residual relief (DEM minus a smoothed DEM) — isolates small protrusions.

    Walls show up as positive residual. ``kernel`` is the smoothing scale in
    pixels (converted to a Gaussian sigma).
    """
    import numpy as np  # noqa: PLC0415
    from skimage.filters import gaussian  # noqa: PLC0415

    arr = np.asarray(dem, dtype=float)
    sigma = max(kernel / 6.0, 0.5)
    smoothed = gaussian(arr, sigma=sigma, preserve_range=True)
    return arr - smoothed


def multiscale_relief(dem: Any, kernels: tuple[int, ...] = (9, 25, 51)) -> Any:
    """RVT-style multiscale blend: mean of z-normalised local relief models.

    Combining several smoothing scales makes wall courses stand out across both
    fine and coarse structure. Returns a z-normalised residual field.
    """
    import numpy as np  # noqa: PLC0415

    stacked = []
    for k in kernels:
        lrm = local_relief_model(dem, kernel=k)
        std = float(np.std(lrm))
        stacked.append((lrm - float(np.mean(lrm))) / std if std > 0 else lrm)
    return np.mean(np.stack(stacked, axis=0), axis=0)
