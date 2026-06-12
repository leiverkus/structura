"""Runtime configuration, read from environment / .env (see ``.env.example``)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (no external dependency)."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(slots=True)
class Settings:
    input_dir: Path
    sink: str  # "postgis" | "api"
    # PostGIS
    pg_dsn: str | None
    pg_schema: str
    pg_table: str
    # Django API
    api_base_url: str | None
    api_token: str | None

    @classmethod
    def from_env(cls, dotenv: str | Path = ".env") -> "Settings":
        _load_dotenv(Path(dotenv))
        host = os.environ.get("PGHOST", "localhost")
        port = os.environ.get("PGPORT", "5432")
        db = os.environ.get("PGDATABASE", "excavation")
        user = os.environ.get("PGUSER", "structura")
        pw = os.environ.get("PGPASSWORD", "")
        dsn = f"host={host} port={port} dbname={db} user={user} password={pw}"
        return cls(
            input_dir=Path(os.environ.get("STRUCTURA_INPUT_DIR", "./data/incoming")),
            sink=os.environ.get("STRUCTURA_SINK", "postgis"),
            pg_dsn=dsn,
            pg_schema=os.environ.get("STRUCTURA_PG_SCHEMA", "public"),
            pg_table=os.environ.get("STRUCTURA_PG_TABLE", "features"),
            api_base_url=os.environ.get("STRUCTURA_API_BASE_URL"),
            api_token=os.environ.get("STRUCTURA_API_TOKEN"),
        )
