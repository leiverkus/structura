"""Profile (section) track: vectorise stratum boundaries from a section image.

Unlike the plan view, sections are driven by fine colour/texture differences
between strata rather than relief. Input is a rectified, georeferenced section
image of the excavation wall.
"""

from __future__ import annotations

from pathlib import Path

from .models import Feature


class ProfileSegmenter:
    """Segment stratum boundaries in a section image -> polyline features.

    TODO: colour/texture segmentation (e.g. superpixels + clustering, or a
    learned model) tuned for subtle boundaries; vectorise boundaries.
    """

    name = "profile-segmenter"

    def segment(self, section_image_path: Path) -> list[Feature]:
        raise NotImplementedError("Implement colour/texture section segmentation.")
