# SPDX-License-Identifier: AGPL-3.0-or-later

"""Common interface for vector output sinks."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..models import Feature


@runtime_checkable
class VectorSink(Protocol):
    """Persist georeferenced features to the excavation database."""

    def write(self, features: list[Feature]) -> int:
        """Write features; return the number persisted."""
        ...
