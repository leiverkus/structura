"""Core data model shared across all tracks.

A ``Feature`` is one georeferenced vector object produced by a track. Geometry
is kept as a Shapely object (imported lazily so the package imports without the
``geo`` extra installed). All coordinates are in the raster CRS.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any


class Track(str, Enum):
    """Which processing track produced a feature."""

    SEG_2D = "2d"          # orthophoto segmentation (stones, surfaces)
    DEM_25D = "2.5d"       # DEM edge / wall-course tracing
    PROFILE = "profile"    # section (vertical) segmentation
    TEMPORAL = "temporal"  # overlay / intersect of multiple days


class FeatureType(str, Enum):
    """Archaeological geometry class (Befund-Geometrie)."""

    STONE = "stone"        # polygon
    SURFACE = "surface"    # polygon
    WALL = "wall"          # polyline (course of a multi-stone wall)
    EDGE = "edge"          # polyline (terrace edge, cut, pit rim, ...)
    SECTION = "section"    # section/stratum boundary vector


@dataclass(slots=True)
class Feature:
    """One georeferenced vector feature.

    Attributes:
        feature_type: archaeological class (drives polygon vs. polyline).
        geometry: a Shapely geometry in CRS ``crs`` (Polygon / LineString / ...).
        crs: CRS identifier inherited from the source raster (e.g. "EPSG:32636").
        track: which track produced it.
        captured_on: excavation day this geometry belongs to (temporal series).
        stratum: optional stratum/layer id — usually assigned downstream by the
            archaeologist in the DB webview, may be ``None`` here.
        properties: free-form attributes (confidence, model name, source raster).
    """

    feature_type: FeatureType
    geometry: Any  # shapely.geometry.base.BaseGeometry
    crs: str
    track: Track
    captured_on: date | None = None
    stratum: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
