# Roadmap

This roadmap tracks the **engineering** milestones for Structura. It follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) (pre-1.0, so the API
may change between minor versions).

## Guiding principle: decouple code from the data blocker

Most of Structura can be built and tested **without** real excavation data:
implementations run on synthetic / sample rasters and are covered in CI. Only
the *comparative evaluation* and the *quality verdicts* (research hypotheses
H_A–H_C) genuinely require a captured trench. That work is isolated to the last
two milestones; everything before is buildable today.

The track letters (A–E) cross-reference the sub-studies in the companion
research plan, so the two repositories stay aligned.

## Milestones

### v0.1.0 — Scaffolding ✅ *(released 2026-06-16)*
Package, CLI, configuration, data model, track/sink interfaces (stubs),
packaging, docs, MIT license, citation metadata, CI.

### v0.2.0 — Walking skeleton *(end-to-end on sample data)*
The first milestone where the pipeline actually produces georeferenced output —
no GPU, no model download, no database required.
- [ ] `geo.read_raster` hardened; `geo.mask_to_polygons` implemented
      (rasterio `features.shapes` → Shapely, applying the affine transform).
- [ ] `ClassicalSegmenter` implemented (watershed / contour) — deterministic,
      CI-testable, the reference backend.
- [ ] **New `FileSink`** (GeoPackage / GeoJSON) — inspect output in QGIS before
      the PostGIS-vs-API decision is made; becomes the testable default sink.
- [ ] `structura run` produces real polygons from a sample orthophoto.
- [ ] Tests on a tiny synthetic GeoTIFF; CI green end-to-end.

### v0.3.0 — 2D track complete *(Sub-study A)*
- [ ] `SamSegmenter` implemented (automatic / prompted mask generation).
- [ ] `CellposeSegmenter` implemented (tiled instance segmentation + stitch).
- [ ] Backend selection via configuration.
- [ ] Geometry metric utilities (over-/under-segmentation rate, a/b-axis error).
- Data-dependent: model fine-tuning and the SAM-vs-Cellpose verdict belong to
  the evaluation milestone, not here.

### v0.4.0 — 2.5D track *(Sub-study B)*
- [ ] `dem.relief` derivatives (hillshade, slope, curvature, local relief model;
      RVT-style multiscale blend).
- [ ] `geo.skeleton_to_polylines` implemented.
- [ ] `WallTracer` (relief → ridge/edge response → skeleton → polyline) with
      **gap bridging** for partially destroyed walls; edges kept separate.

### v0.5.0 — Persistence *(resolve the DB decision)*
- [ ] `PostGISSink` (psycopg; geometry column with feature CRS SRID; attributes
      incl. `properties` as JSONB).
- [ ] `DjangoApiSink` (serialise to GeoJSON; token-auth POST; batching).
- [ ] **Decide the default sink** (direct PostGIS vs. Django API) and document it.
- [ ] Schema / table bootstrap helper.

### v0.6.0 — Temporal / 4D track *(Sub-study C)*
- [ ] `temporal.overlay` / `temporal.intersect` over per-day layers.
- [ ] Per-stratum `ST_Intersection` / difference in PostGIS over the time series.
- [ ] `captured_on` propagated through intake → features → sink.
- [ ] Daily-series CLI ergonomics.

### v0.7.0 — Profile track *(Sub-study D)*
- [ ] Spatial (per-region) colour calibration of a rectified section image.
- [ ] Colour / texture stratum segmentation → section boundary polylines.

### v0.8.0 — Semantic-field bridge *(Sub-study E / Effigies)*
- [ ] Consume `orthophoto_semantic.tif` (material-class field) as a prior /
      input channel for the vector tracks.
- [ ] Implement the field-vs-object contract (Structura owns vector objects;
      the upstream engine owns the geometry-space field).
- Depends on the upstream Effigies `--semantic` output.

### v0.9.0 — Evaluation harness  ⛔ *needs real trench data*
- [ ] Reproducible evaluation scripts producing the paper's metrics
      (AP@IoU; completeness/correctness/quality + clDice/APLS; LoD95%).
- [ ] Wire results into `paper/output/data-analysis/`.

### v1.0.0 — Production release  ⛔ *needs real trench data*
- [ ] One full trench processed end-to-end.
- [ ] DB default locked; stable public API.
- [ ] Documentation complete; first Zenodo DOI minted.

## Cross-cutting (every milestone)
- Keep CI green (ruff + mypy + pytest).
- Keep `CHANGELOG.md` `[Unreleased]` current.
- Update `docs/` alongside the code it describes.

## Open decisions
Tracked in [`docs/architecture.md`](docs/architecture.md#open-decisions): the DB
sink default (v0.5), the 2D model default (decided by the v0.9 evaluation), and
the intake layout heuristic.

> This is a living document. Milestone scope and ordering may shift as the
> research plan and the upstream Effigies engine evolve.
