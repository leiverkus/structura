"""Orchestration: intake -> tracks -> sink.

This is the glue. It is intentionally backend-agnostic: tracks and sinks are
swapped per configuration so the comparative evaluation (SAM vs. Cellpose vs.
classical; PostGIS vs. API) is a config change, not a code change.
"""

from __future__ import annotations

from .config import Settings
from .db.api import DjangoApiSink
from .db.base import VectorSink
from .db.postgis import PostGISSink
from .intake import RasterKind, discover_inputs
from .models import Feature


def make_sink(settings: Settings) -> VectorSink:
    if settings.sink == "postgis":
        assert settings.pg_dsn is not None
        return PostGISSink(settings.pg_dsn, settings.pg_schema, settings.pg_table)
    if settings.sink == "api":
        assert settings.api_base_url is not None
        return DjangoApiSink(settings.api_base_url, settings.api_token)
    raise ValueError(f"Unknown sink: {settings.sink!r}")


def run(settings: Settings, *, write: bool = True) -> list[Feature]:
    """Run the vectorisation pipeline over all discovered inputs.

    Currently wires intake + sink selection; the per-track segmenters/tracers
    are stubs (see their NotImplementedError). Returns the produced features.
    """
    products = discover_inputs(settings.input_dir)
    features: list[Feature] = []

    for product in products:
        if product.kind is RasterKind.ORTHO:
            # TODO: features += SamSegmenter().segment(product.path)
            pass
        elif product.kind is RasterKind.DEM:
            # TODO: features += WallTracer().trace(product.path)
            pass

    if write and features:
        make_sink(settings).write(features)
    return features
