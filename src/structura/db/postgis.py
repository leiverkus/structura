"""Direct PostGIS sink (requires the ``db`` extra)."""

from __future__ import annotations

from ..models import Feature


class PostGISSink:
    """Write features straight into a PostGIS table.

    TODO: connect via psycopg; ensure a geometry column (with the feature CRS
    SRID); insert geometry (WKB/WKT) + attributes (feature_type, track,
    captured_on, stratum, properties as JSONB).
    """

    def __init__(self, dsn: str, schema: str = "public", table: str = "features") -> None:
        self.dsn = dsn
        self.schema = schema
        self.table = table

    def write(self, features: list[Feature]) -> int:
        raise NotImplementedError("Insert features into PostGIS via psycopg.")
