"""Tests for the 2D backend factory and lazy-import safety (no heavy deps)."""

from pathlib import Path

import pytest

from structura.config import Settings
from structura.pipeline import make_segmenter
from structura.segmentation.cellpose import CellposeSegmenter
from structura.segmentation.classical import ClassicalSegmenter
from structura.segmentation.sam import SamSegmenter


def _settings(backend: str) -> Settings:
    return Settings(
        input_dir=Path("."),
        sink="file",
        segmentation_backend=backend,
        gpu=False,
        output_path=Path("out.gpkg"),
        pg_dsn=None,
        pg_schema="public",
        pg_table="features",
        api_base_url=None,
        api_token=None,
    )


def test_factory_returns_correct_backend() -> None:
    assert isinstance(make_segmenter(_settings("classical")), ClassicalSegmenter)
    assert isinstance(make_segmenter(_settings("sam")), SamSegmenter)
    assert isinstance(make_segmenter(_settings("cellpose")), CellposeSegmenter)


def test_factory_unknown_backend_raises() -> None:
    with pytest.raises(ValueError, match="2D backend"):
        make_segmenter(_settings("nope"))


def test_backends_construct_without_heavy_deps() -> None:
    # Constructing must not import samgeo/cellpose/torch — proven by this running
    # in CI where those extras are not installed.
    assert SamSegmenter().name == "sam"
    assert CellposeSegmenter().name == "cellpose"
