"""Trace wall courses and edges from a DEM as polylines (2.5D track)."""

from __future__ import annotations

from pathlib import Path

from ..models import Feature


class WallTracer:
    """Detect wall courses / edges from DEM relief and emit polyline features.

    Pipeline (TODO): compute relief derivatives (``relief``) -> ridge/edge
    response -> threshold -> ``geo.skeleton_to_polylines``. Must bridge gaps
    from partially destroyed walls and keep edges as separate polylines.
    """

    name = "dem-wall-tracer"

    def __init__(self, gap_bridge_m: float = 0.3) -> None:
        self.gap_bridge_m = gap_bridge_m

    def trace(self, dem_path: Path) -> list[Feature]:
        raise NotImplementedError("Implement relief -> ridge -> polyline tracing.")
