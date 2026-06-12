"""Django-API sink (requires the ``api`` extra)."""

from __future__ import annotations

from ..models import Feature


class DjangoApiSink:
    """POST features to the Django excavation app's API as GeoJSON.

    TODO: serialise each Feature to GeoJSON (geometry + properties); POST to the
    features endpoint with token auth; handle batching and idempotency.
    """

    def __init__(self, base_url: str, token: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token

    def write(self, features: list[Feature]) -> int:
        raise NotImplementedError("POST GeoJSON features to the Django API.")
