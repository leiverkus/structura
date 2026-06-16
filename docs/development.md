# Development

## Setup

Requires Python ≥ 3.11.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"          # pytest, ruff, mypy
```

Install additional extras as you work on the corresponding track:

| Extra | For |
|-------|-----|
| `geo` | raster I/O & raster→vector (`structura.geo`) — needed by every track |
| `sam` | the SAM 2D backend |
| `cellpose` | the Cellpose 2D backend |
| `db` | the direct PostGIS sink |
| `api` | the Django-API sink |

## Quality gates

```bash
ruff check .        # lint (line-length 100, target py311)
mypy src            # type-check
pytest              # tests
```

Run all three before opening a pull request.

## Project layout

```
src/structura/
├── cli.py            # CLI entry point
├── config.py         # Settings (env / .env)
├── intake.py         # raster discovery
├── models.py         # Feature, Track, FeatureType
├── geo.py            # raster I/O, raster→vector
├── pipeline.py       # orchestration
├── segmentation/     # 2D track (sam, cellpose, classical) + Segmenter protocol
├── dem/              # 2.5D track (relief, wall_tracing)
├── profile.py        # profile/section track
├── temporal.py       # temporal overlay/intersect
└── db/               # sinks (postgis, api) + VectorSink protocol
tests/
└── test_smoke.py
```

The package uses a **src-layout**; heavy imports (`rasterio`, `torch`,
`cellpose`, `psycopg`, …) are done **locally inside functions**, never at module
top level, so `import structura` works with only the core dependency installed.

## Adding a 2D segmentation backend

1. Create `src/structura/segmentation/<name>.py`.
2. Implement a class with a `name: str` attribute and a
   `segment(self, ortho_path: Path) -> list[Feature]` method — that satisfies
   the `Segmenter` protocol in `segmentation/base.py` (no inheritance needed).
3. Return georeferenced `Feature`s: vectorise your masks via
   `geo.mask_to_polygons(mask, transform, crs)` so geometry lands in the raster
   CRS, and set `feature_type` / `track` / `properties`.
4. Wire it into backend selection in `pipeline.py` (and, if user-selectable, a
   config switch in `config.py`).
5. Add a test.

The same shape applies to a new **sink** (implement `VectorSink.write`) or a new
**DEM tracer**.

## Conventions

- Type annotations everywhere; `from __future__ import annotations` at the top.
- Keep the core import light — guard optional-stack imports locally.
- Coordinates are always in the source raster CRS; never silently reproject.
- Unimplemented behaviour raises `NotImplementedError` with a one-line hint of
  the intended implementation, so stubs are self-documenting.
