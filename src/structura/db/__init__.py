# SPDX-License-Identifier: AGPL-3.0-or-later

"""Output sinks: write georeferenced features to disk or the excavation database.

Strategies (the DB choice is still open — see ROADMAP v0.5):
- :class:`~structura.db.file.FileSink` — write a GeoPackage / GeoJSON (default).
- :class:`~structura.db.postgis.PostGISSink` — write directly to PostGIS.
- :class:`~structura.db.api.DjangoApiSink` — POST to the Django app's API.
"""

from .base import VectorSink
from .file import FileSink

__all__ = ["FileSink", "VectorSink"]
