# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2026-06-18

### Changed
- **License changed from MIT to GNU AGPL v3 or later** (`AGPL-3.0-or-later`).
  Updated `LICENSE`, `pyproject.toml`, `CITATION.cff`, `.zenodo.json`, and the
  README badge/footer, added source-file SPDX identifiers, and documented
  third-party dependency license notes.
- Version metadata bumped to `0.4.1` for the licensing patch release.

### Removed
- Removed the stale v0.2.0 version DOI from `CITATION.cff`; the concept DOI
  remains listed until a new archive-specific version DOI is minted.

## [0.4.0] - 2026-06-16

Adds the 2.5D track (Sub-study B): DEMs are traced into wall and edge polylines.

### Added
- `dem.relief` derivatives (self-implemented, numpy/scikit-image): `hillshade`,
  `slope`, `curvature`, `local_relief_model`, and `multiscale_relief` (RVT-style
  multiscale blend).
- `geo.skeleton_to_polylines` — skeletonise → junction-clustered trace → spur
  prune → simplify → georeferenced Shapely LineStrings.
- `WallTracer` — multiscale local-relief ridges → `WALL` polylines, with
  dilation-based **gap bridging** for partially destroyed walls.
- `EdgeTracer` — slope discontinuities → `EDGE` polylines.
- `dem._common.relief_response_to_features` — shared response→polyline-features
  wrapper (parallel to `segmentation._common`).
- `STRUCTURA_GAP_BRIDGE_M` setting; the pipeline DEM branch now runs both tracers.
- Tests: `test_relief`, `test_skeleton`, `test_wall_tracing` (incl. gap bridging),
  `test_edge_tracing`; end-to-end test extended to DEM→polyline output.

### Changed
- `pipeline.run` DEM branch implemented (was a stub); version → `0.4.0`.

## [0.3.0] - 2026-06-16

Completes the 2D track (Sub-study A): two learned segmentation backends, a
config-selectable backend, and geometry-metric utilities.

### Added
- **SAM backend** via samgeo (`segment-geospatial`): automatic mask generation
  on the (tiled) georeferenced ortho → label raster → shared vectorisation path.
- **Cellpose backend** targeting **Cellpose-SAM (v4)** (`CellposeModel.eval`).
- `segmentation._common.label_mask_to_features` — shared label-mask → `Feature`
  wrapper used by the classical, SAM, and Cellpose backends.
- `pipeline.make_segmenter` factory + `STRUCTURA_2D_BACKEND` / `STRUCTURA_GPU`
  settings for config-selectable backends.
- `structura.metrics` — geometry metrics for Sub-study A: `iou`,
  `match_instances`, `precision_recall_f1`, `segmentation_rates`
  (coverage-based over-/under-segmentation), `axis_error` (a/b-axis).
- Tests: `test_metrics`, `test_make_segmenter`, `test_common`; heavy backend
  tests (`test_sam`, `test_cellpose`) guarded with `pytest.importorskip`.
- Zenodo archival: DOI badge in the README and the concept DOI
  (`10.5281/zenodo.20716606`) + v0.2.0 version DOI recorded in `CITATION.cff`.

### Changed
- `sam` extra → `segment-geospatial` (was segment-anything/torch/opencv);
  `cellpose` extra → `cellpose>=4` (was `>=3`).
- `ClassicalSegmenter` refactored to delegate its wrapping step to `_common`.
- mypy skip-follows `samgeo` / `cellpose` / `torch` / `cv2`; version → `0.3.0`.

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

[Unreleased]: https://github.com/leiverkus/structura/compare/v0.4.1...HEAD
[0.4.1]: https://github.com/leiverkus/structura/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/leiverkus/structura/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/leiverkus/structura/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/leiverkus/structura/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/leiverkus/structura/releases/tag/v0.1.0
