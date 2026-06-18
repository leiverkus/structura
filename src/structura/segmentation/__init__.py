# SPDX-License-Identifier: AGPL-3.0-or-later

"""2D orthophoto segmentation track (stones & surfaces).

Backends to compare: SAM, Cellpose, classical CV. All implement ``Segmenter``.
"""

from .base import Segmenter

__all__ = ["Segmenter"]
