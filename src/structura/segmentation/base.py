# SPDX-License-Identifier: AGPL-3.0-or-later

"""Common interface for 2D orthophoto segmenters."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from ..models import Feature


@runtime_checkable
class Segmenter(Protocol):
    """Segment an orthophoto into stone/surface polygon features.

    Implementations: :class:`~structura.segmentation.sam.SamSegmenter`,
    :class:`~structura.segmentation.cellpose.CellposeSegmenter`,
    :class:`~structura.segmentation.classical.ClassicalSegmenter`.
    """

    name: str

    def segment(self, ortho_path: Path) -> list[Feature]:
        """Return georeferenced stone/surface polygons for one orthophoto."""
        ...
