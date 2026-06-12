"""Classical CV baseline for the 2D track (watershed / contour-based)."""

from __future__ import annotations

from pathlib import Path

from ..models import Feature


class ClassicalSegmenter:
    """Edge/watershed segmentation baseline — no learned model.

    TODO: pre-process; gradient/edge; marker-controlled watershed; vectorise.
    Useful as a cheap, deterministic comparison point in the evaluation.
    """

    name = "classical"

    def segment(self, ortho_path: Path) -> list[Feature]:
        raise NotImplementedError("Implement watershed/contour baseline -> polygons.")
