# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `LICENSE` (MIT).
- `CITATION.cff` (Citation File Format 1.2.0) for machine-readable software
  citation — enables GitHub's "Cite this repository" and a Zenodo archival
  record. DOI is left as a placeholder until the first Zenodo deposit.
- `.zenodo.json` archival metadata (software upload, MIT, ORCID, keywords).
- `CHANGELOG.md` (this file).
- `docs/` folder: `architecture.md` (design, tracks, data model, sinks),
  `development.md` (dev setup, testing, adding a backend), and
  `data-layout.md` (expected inputs, CRS handling, output).
- GitHub-ready `README.md` (badges, install/usage, status, citation, license).
- GitHub Actions CI (`.github/workflows/ci.yml`): ruff + mypy + pytest on
  Python 3.11 and 3.12.

### Changed
- `pyproject.toml`: `license` set to `MIT` (was `TBD`); author normalised to
  `Patrick Leiverkus` with the institutional e-mail.

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

[Unreleased]: https://github.com/leiverkus/structura/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/leiverkus/structura/releases/tag/v0.1.0
