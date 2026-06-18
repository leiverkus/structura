# Structura

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/License-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.11-blue.svg)](pyproject.toml)
[![Status: 2.5D track](https://img.shields.io/badge/status-2.5D--track-orange.svg)](#status)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20716606.svg)](https://doi.org/10.5281/zenodo.20716606)

**AI-assisted vectorisation of photogrammetric excavation data.**

Structura is the workflow application for the **vectorisation step** of an
archaeological excavation pipeline. It ingests georeferenced photogrammetric
raster products (orthophoto, DEM) from an upstream WebODM / OpenDroneMap survey
and produces **georeferenced vector geometry** — stone outlines, surfaces, wall
courses, edges, section vectors — for a PostGIS excavation database.

> **Research context.** Structura is the software side of a research project on
> automated excavation plans. The methodology, evaluation plan, and literature
> live in a companion research repository (`paper/`). This repository is the
> code only.

## Pipeline overview

```
                ┌──────────────┐
   WebODM  ───► │  Raster      │   orthophoto (RGB, georef)
 (upstream)     │  intake      │   DEM (elevation, georef)
                └──────┬───────┘
                       │
        ┌──────────────┼───────────────┬─────────────────┐
        ▼              ▼                ▼                 ▼
  ┌───────────┐  ┌───────────┐   ┌───────────┐    ┌─────────────┐
  │ 2D track  │  │ 2.5D track│   │ Profile   │    │ Temporal    │
  │ orthophoto│  │ DEM edge/ │   │ track     │    │ integration │
  │ segment.  │  │ wall trace│   │ section   │    │ overlay /   │
  │ (SAM /    │  │ (relief,  │   │ colour    │    │ intersect   │
  │ Cellpose /│  │ ridge,    │   │ segment.  │    │ (PostGIS)   │
  │ classic)  │  │ learned)  │   │           │    │             │
  └─────┬─────┘  └─────┬─────┘   └─────┬─────┘    └──────┬──────┘
        │ polygons     │ polylines     │ section          │
        │ (stones,     │ (wall course, │ vectors          │
        │  surfaces)   │  edges)       │                  │
        └──────────────┴───────┬───────┴──────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Georeferenced        │
                    │ vector output        │
                    └──────────┬──────────┘
                               ▼
              ┌─────────────────────────────────┐
              │ Excavation database              │
              │ PostgreSQL / PostGIS             │
              │ (Django app; Flutter mobile      │
              │  client via API)                 │
              └─────────────────────────────────┘
                               │
                               ▼
              Interactive stratum annotation (webview, polygon)
              → per-stratum / combined excavation plans
```

See [`docs/architecture.md`](docs/architecture.md) for the detailed design.

## Tracks

| Track | Input | Method (under evaluation) | Output geometry |
|-------|-------|---------------------------|-----------------|
| **2D** stones & surfaces | orthophoto | SAM, Cellpose, classical CV | closed polygons |
| **2.5D** walls & edges | DEM | relief / ridge detection, learned models | polylines |
| **Profile** strata | section image | colour / texture segmentation | section vectors |
| **Temporal** progress | daily vector layers | PostGIS overlay / intersect | reconciled layers |

## Install

Requires Python ≥ 3.11.

```bash
git clone https://github.com/leiverkus/structura.git
cd structura
python -m venv .venv && source .venv/bin/activate
pip install -e .            # core (light)
```

The heavy model and geospatial stacks are **optional extras**, installed only
when you need them:

```bash
pip install -e ".[geo]"      # rasterio, shapely, geopandas, scikit-image
pip install -e ".[sam]"      # segment-anything, torch, opencv
pip install -e ".[cellpose]" # cellpose
pip install -e ".[db]"       # psycopg, SQLAlchemy, GeoAlchemy2 (PostGIS sink)
pip install -e ".[api]"      # httpx (Django-API sink)
pip install -e ".[dev]"      # pytest, ruff, mypy
```

## Usage

Running the pipeline needs the `geo` extra (`pip install -e ".[geo]"`). Copy the
environment template and fill it in:

```bash
cp .env.example .env         # set input dir, sink (file|postgis|api), output path
```

The package exposes a `structura` CLI:

```bash
structura --version
structura intake             # discover & list WebODM raster products
structura run --dry-run      # run the pipeline without writing to the sink
structura run                # run and persist features to the configured sink
```

Out of the box the default sink is **`file`** and the default 2D backend is
**`classical`**: `structura run` segments each orthophoto with the classical
backend (no GPU, no model, no database) and writes georeferenced polygons to
`./data/output/features.gpkg`, ready to open in QGIS.

Switch the 2D backend with `STRUCTURA_2D_BACKEND` (`classical` | `sam` |
`cellpose`). The learned backends need their extra installed:

```bash
pip install -e ".[sam]"        # SAM via samgeo (segment-geospatial)
pip install -e ".[cellpose]"   # Cellpose-SAM (v4)
STRUCTURA_2D_BACKEND=cellpose structura run
```

Configuration is read from the environment / `.env` (see
[`.env.example`](.env.example) and [`docs/data-layout.md`](docs/data-layout.md)).

## Status

**2.5D track (v0.4).** Two tracks run end-to-end now:
- **2D** (orthophoto → polygons) with three selectable backends — **classical**
  (default, GPU-free), **SAM** (via samgeo), **Cellpose-SAM**.
- **2.5D** (DEM → polylines): self-implemented relief derivatives feed a
  **`WallTracer`** (multiscale local-relief ridges → WALL, with gap bridging for
  discontinuous walls) and an **`EdgeTracer`** (slope discontinuities → EDGE).

Plus geometry-metric utilities (`structura.metrics`). The profile / temporal
tracks and the PostGIS / Django-API sinks are still stubs. The learned 2D
backends are integrated but their comparative evaluation is **blocked on
excavation data** that does not exist yet — see the research repository.

The planned milestones are in [`ROADMAP.md`](ROADMAP.md); open architectural
decisions are tracked in
[`docs/architecture.md`](docs/architecture.md#open-decisions).

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — design, tracks, data model, sinks
- [`docs/development.md`](docs/development.md) — dev setup, testing, adding a backend
- [`docs/data-layout.md`](docs/data-layout.md) — expected inputs, CRS handling, output

## Contributing

This is a research project under active design. Issues and pull requests are
welcome. Please run the dev tooling before submitting:

```bash
ruff check . && mypy src && pytest
```

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md). This project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Citation

If you use Structura, please cite it. The archived versions are on Zenodo —
cite the **concept DOI** [10.5281/zenodo.20716606](https://doi.org/10.5281/zenodo.20716606),
which always resolves to the latest release. Citation metadata is in
[`CITATION.cff`](CITATION.cff) (and [`.zenodo.json`](.zenodo.json) for archival);
GitHub's "Cite this repository" reads the `CITATION.cff` directly.

## License

Structura is licensed under [AGPL-3.0-or-later](LICENSE) © 2026 Patrick Leiverkus.
Third-party dependency notes are tracked in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
