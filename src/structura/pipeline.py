"""Orchestration: intake -> tracks -> sink.

This is the glue. It is intentionally backend-agnostic: tracks and sinks are
swapped per configuration so the comparative evaluation (SAM vs. Cellpose vs.
classical; PostGIS vs. API) is a config change, not a code change.
"""

from __future__ import annotations

from .config import Settings
from .db.api import DjangoApiSink
from .db.base import VectorSink
from .db.file import FileSink
from .db.postgis import PostGISSink
from .dem.edge_tracing import EdgeTracer
from .dem.wall_tracing import WallTracer
from .intake import RasterKind, discover_inputs
from .models import Feature
from .segmentation.base import Segmenter
from .segmentation.cellpose import CellposeSegmenter
from .segmentation.classical import ClassicalSegmenter
from .segmentation.sam import SamSegmenter


def make_segmenter(settings: Settings) -> Segmenter:
    backend = settings.segmentation_backend
    if backend == "classical":
        return ClassicalSegmenter()
    if backend == "sam":
        return SamSegmenter()
    if backend == "cellpose":
        return CellposeSegmenter(gpu=settings.gpu)
    raise ValueError(f"Unknown 2D backend: {backend!r}")


def make_sink(settings: Settings) -> VectorSink:
    if settings.sink == "file":
        return FileSink(settings.output_path)
    if settings.sink == "postgis":
        assert settings.pg_dsn is not None
        return PostGISSink(settings.pg_dsn, settings.pg_schema, settings.pg_table)
    if settings.sink == "api":
        assert settings.api_base_url is not None
        return DjangoApiSink(settings.api_base_url, settings.api_token)
    raise ValueError(f"Unknown sink: {settings.sink!r}")


def run(settings: Settings, *, write: bool = True) -> list[Feature]:
    """Run the vectorisation pipeline over all discovered inputs.

    Orthophotos are segmented with the configured 2D backend (``make_segmenter``);
    DEMs are traced into wall + edge polylines (2.5D track). Returns the produced
    features, and writes them to the configured sink unless ``write`` is False.
    """
    products = discover_inputs(settings.input_dir)
    features: list[Feature] = []
    segmenter = make_segmenter(settings)

    for product in products:
        if product.kind is RasterKind.ORTHO:
            features += segmenter.segment(product.path)
        elif product.kind is RasterKind.DEM:
            features += WallTracer(gap_bridge_m=settings.gap_bridge_m).trace(product.path)
            features += EdgeTracer().trace(product.path)

    if write and features:
        make_sink(settings).write(features)
    return features
