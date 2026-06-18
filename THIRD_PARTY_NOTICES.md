# Third-Party Notices

Structura itself is licensed under `AGPL-3.0-or-later`; see [`LICENSE`](LICENSE).
This file summarizes license metadata for the direct dependencies declared in
[`pyproject.toml`](pyproject.toml). It is a compliance aid for releases, not a
substitute for checking the full transitive dependency graph of an installed
environment.

## Direct Runtime Dependencies

| Dependency | Declared use | License metadata |
|------------|--------------|------------------|
| `numpy` | Core numerical arrays | BSD-3-Clause / permissive bundled notices |
| `rasterio` | Optional `geo` raster I/O | BSD-3-Clause |
| `shapely` | Optional `geo` geometry operations | BSD-3-Clause; bundles/uses GEOS under LGPL-2.1 |
| `geopandas` | Optional `geo` vector data handling | BSD-3-Clause |
| `scikit-image` | Optional `geo` image processing | BSD-3-Clause with some BSD-2-Clause and MIT notices |
| `pyogrio` | Optional `geo` vector file I/O | MIT |
| `segment-geospatial` | Optional `sam` segmentation backend | MIT |
| `cellpose` | Optional `cellpose` segmentation backend | BSD |
| `psycopg[binary]` | Optional `db` PostGIS sink | LGPL-3.0-only |
| `SQLAlchemy` | Optional `db` SQL layer | MIT |
| `GeoAlchemy2` | Optional `db` spatial SQL helpers | MIT |
| `httpx` | Optional `api` sink client | BSD-3-Clause |

## Development Dependencies

| Dependency | Declared use | License metadata |
|------------|--------------|------------------|
| `pytest` | Tests | MIT |
| `ruff` | Linting | MIT |
| `mypy` | Type checking | MIT |

## Model And Checkpoint Notes

The optional SAM and Cellpose backends may download or load model weights at
runtime. Those weights can have terms that are separate from the Python package
license. In particular, `segment-geospatial` depends on Meta's
`segment-anything` package, whose PyPI metadata does not currently expose a
license expression. Release builds that bundle checkpoints, containers, or
preloaded model caches should verify and preserve the relevant upstream model
terms before distribution.
