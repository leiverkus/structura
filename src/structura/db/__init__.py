"""Output sinks: write georeferenced features to the excavation database.

Two strategies (architectural decision still open):
- :class:`~structura.db.postgis.PostGISSink` — write directly to PostGIS.
- :class:`~structura.db.api.DjangoApiSink` — POST to the Django app's API.
"""

from .base import VectorSink

__all__ = ["VectorSink"]
