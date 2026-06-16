# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Zenodo archival: DOI badge in the README and the concept DOI
  (`10.5281/zenodo.20716606`) + v0.2.0 version DOI recorded in `CITATION.cff`.

## [0.2.0] - 2026-06-16

The "walking skeleton": the pipeline now produces real georeferenced vector
output end-to-end with no GPU, model download, or database.

### Added
- `geo.mask_to_polygons` — vectorise a label mask into georeferenced Shapely
  polygons (rasterio `features.shapes`, world-unit `min_area` filter).
- `ClassicalSegmenter` implementation — deterministic watershed 2D backend
  (Otsu markers → Sobel-gradient watershed → connected components → polygons).
- `FileSink` (`structura.db.file`) — write features to GeoPackage / GeoJSON
  (format from extension); single-CRS assertion; `properties` as a JSON string.
- `STRUCTURA_OUTPUT_PATH` setting for the file sink.
- Geo-path tests on a synthetic GeoTIFF (`tests/conftest.py` fixture +
  `test_geo`, `test_classical`, `test_file_sink`, `test_pipeline`), guarded with
  `pytest.importorskip` so they skip without the `geo` extra.
- `pyogrio` added to the `geo` extra (guarantees a geopandas I/O engine).
- Project-citation / GitHub-readiness scaffolding folded into this release:
  `LICENSE` (MIT), `CITATION.cff`, `.zenodo.json`, `CHANGELOG.md`, the `docs/`
  folder, a GitHub-ready `README.md`, GitHub Actions CI, and `ROADMAP.md`.

### Changed
- **Default `STRUCTURA_SINK` is now `file`** (was `postgis`) — `structura run`
  works out of the box, writing `./data/output/features.gpkg`.
- `pipeline.run` ORTHO branch now runs the classical segmenter (was a stub).
- CI installs the `geo` extra (`pip install -e ".[dev,geo]"`) so the geo path is
  exercised; mypy skips following into the geospatial/imaging stacks.
- `pyproject.toml`: `license` set to `MIT` (was `TBD`); author normalised to
  `Patrick Leiverkus`; version → `0.2.0`.

## [0.1.0] - 2026-06-16

### Added
- Initial scaffold of the Structura workflow app (Python, src-layout).
  - `structura` CLI (`intake`, `run`) with `--version` and `--dry-run`.
  - Environment / `.env` configuration loader (`structura.config`).
  - Core data model: `Feature`, `Track`, `FeatureType` (`structura.models`).
  - Raster intake (`structura.intake`) tagging WebODM products by kind.
  - Georeferencing helpers (`structura.geo`) — raster I/O, mask→polygon,
    skeleton→polyline (interfaces; vectorisation pending).
  - 2D segmentation track with swappable backends — SAM, Cellpose, classical CV
    (`structura.segmentation`, behind a common `Segmenter` protocol).
  - 2.5D DEM track — relief derivatives + wall/edge tracing (`structura.dem`).
  - Profile / section track stub (`structura.profile`).
  - Temporal integration stub — overlay / intersect (`structura.temporal`).
  - Output sinks behind a `VectorSink` protocol — direct PostGIS and Django-API
    (`structura.db`).
  - Pipeline orchestration wiring intake → tracks → sink (`structura.pipeline`).
  - Optional dependency extras: `geo`, `sam`, `cellpose`, `db`, `api`, `dev`.
  - Smoke test (`tests/test_smoke.py`).

[Unreleased]: https://github.com/leiverkus/structura/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/leiverkus/structura/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/leiverkus/structura/releases/tag/v0.1.0
