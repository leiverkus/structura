"""Temporal integration of per-day vector layers.

Daily captures document excavation progress; vectors from different days must be
overlaid and intersected (verschnitten) so features stay consistent across the
series. Heavy set ops are best delegated to PostGIS once vectors are stored.
"""

from __future__ import annotations

from collections.abc import Iterable

from .models import Feature


def overlay(layers: Iterable[list[Feature]]) -> list[Feature]:
    """Stack vector layers from successive days into one set (with provenance)."""
    raise NotImplementedError("Combine per-day Feature layers, tagging captured_on.")


def intersect(earlier: list[Feature], later: list[Feature]) -> list[Feature]:
    """Intersect two days' geometries (e.g. what persisted vs. was removed)."""
    raise NotImplementedError("Geometric intersection across two excavation days.")
