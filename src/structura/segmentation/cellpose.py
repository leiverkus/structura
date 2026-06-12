"""Cellpose backend for the 2D track. Candidate for dense, roundish stones."""

from __future__ import annotations

from pathlib import Path

from ..models import Feature


class CellposeSegmenter:
    """Stone segmentation via Cellpose (instance masks -> polygons).

    TODO: run Cellpose model on tiled orthophoto; stitch; vectorise instances.
    """

    name = "cellpose"

    def __init__(self, model_type: str = "cyto3", diameter: float | None = None) -> None:
        self.model_type = model_type
        self.diameter = diameter

    def segment(self, ortho_path: Path) -> list[Feature]:
        raise NotImplementedError("Implement Cellpose instance seg -> Feature polygons.")
