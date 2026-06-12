"""Segment Anything (SAM) backend for the 2D track. Baseline approach."""

from __future__ import annotations

from pathlib import Path

from ..models import Feature


class SamSegmenter:
    """Stone/surface segmentation via Segment Anything.

    TODO: load checkpoint; run automatic mask generation (or prompted); filter
    masks by area/shape; vectorise via ``geo.mask_to_polygons``; classify
    stone vs. surface.
    """

    name = "sam"

    def __init__(self, checkpoint: Path | None = None, model_type: str = "vit_h") -> None:
        self.checkpoint = checkpoint
        self.model_type = model_type

    def segment(self, ortho_path: Path) -> list[Feature]:
        raise NotImplementedError("Implement SAM mask generation -> Feature polygons.")
