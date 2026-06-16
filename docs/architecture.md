# Architecture

Structura turns georeferenced photogrammetric rasters into georeferenced vector
features for an excavation database. The package is deliberately
**backend-agnostic**: tracks and sinks sit behind small interfaces so the
comparative evaluation (which segmenter? which sink?) is a *configuration*
change, not a code change.

```
intake  ──►  tracks  ──►  Feature[]  ──►  sink
(rasters)    (per geometry kind)          (PostGIS | Django API)
```

## Modules

| Module | Responsibility |
|--------|----------------|
| `structura.cli` | `structura` command-line entry point (`intake`, `run`). |
| `structura.config` | `Settings` loaded from environment / `.env`. |
| `structura.intake` | Discover WebODM rasters, tag each as `ORTHO` or `DEM`. |
| `structura.models` | `Feature` (the shared vector object), `Track`, `FeatureType`. |
| `structura.geo` | Raster I/O and raster→vector conversion (georeferencing core). |
| `structura.segmentation` | 2D track — stones & surfaces (classical / SAM / Cellpose) behind a `Segmenter` protocol; `_common` shares the mask→Feature step. |
| `structura.metrics` | Geometry metrics for Sub-study A (IoU, matching, over-/under-seg, a/b-axis). |
| `structura.dem` | 2.5D track — relief derivatives + wall / edge tracing. |
| `structura.profile` | Profile track — section stratum segmentation. |
| `structura.temporal` | Temporal track — overlay / intersect of daily layers. |
| `structura.db` | Output sinks — file (GeoPackage/GeoJSON), PostGIS, or Django API. |
| `structura.pipeline` | Orchestration: intake → tracks → sink; `make_segmenter` / `make_sink` factories. |

## The data model

Everything a track produces is a `Feature` (`structura.models`):

- `feature_type` — `STONE`, `SURFACE` (polygons); `WALL`, `EDGE` (polylines);
  `SECTION` (section/stratum boundary).
- `geometry` — a Shapely geometry **in the source raster's CRS**. Shapely is
  imported lazily so the package imports without the `geo` extra.
- `crs` — CRS identifier inherited from the source raster (e.g. `EPSG:32636`).
- `track` — which track produced it (`2d`, `2.5d`, `profile`, `temporal`).
- `captured_on` — the excavation day this geometry belongs to (for the series).
- `stratum` — usually assigned **downstream** by the archaeologist in the DB
  webview; may be `None` here.
- `properties` — free-form attributes (confidence, model name, source raster).

**Everything is georeferenced.** The affine transform + CRS read with the raster
are what make every derived vector world-referenced: pixel `(col, row)` → world
`(x, y)` via `transform * (col, row)`. See `structura.geo.read_raster`.

## Tracks

### 2D — stones & surfaces (`structura.segmentation`)
Segments the orthophoto into polygon features. Three interchangeable backends
implement the `Segmenter` protocol (`segment(ortho_path) -> list[Feature]`):

- `ClassicalSegmenter` — watershed baseline (cheap, deterministic, GPU-free).
  Otsu thresholding drives the markers, watershed runs on the Sobel gradient,
  connected foreground components become labels. The default backend.
- `SamSegmenter` — SAM automatic mask generation via **samgeo**
  (`segment-geospatial`): runs on the (tiled) georeferenced ortho and writes a
  label raster, which is read back through the shared path.
- `CellposeSegmenter` — **Cellpose-SAM (v4)** instance masks
  (`CellposeModel.eval`).

All three end the same way: an integer instance-label mask →
`segmentation._common.label_mask_to_features` → `geo.mask_to_polygons` →
`Feature`s. The active backend is chosen by `make_segmenter(settings)` from
`STRUCTURA_2D_BACKEND`. The learned backends import their heavy deps lazily, so
they need the matching extra (`.[sam]` / `.[cellpose]`) only when actually run.

## Metrics (`structura.metrics`)
Pure-Shapely geometry metrics for Sub-study A: `iou`, `match_instances`,
`precision_recall_f1`, `segmentation_rates` (coverage-based over-/under-seg), and
`axis_error` (a/b axes from the minimum rotated rectangle). They take lists of
geometries (`geoms_of(features)` adapts `Feature`s). AP@IoU and effort accounting
are deferred to the v0.9 evaluation harness.

### 2.5D — walls & edges (`structura.dem`) — implemented
A wall protrudes slightly from its surroundings, so it shows up in local relief
far better than in the orthophoto. `dem.relief` provides the derivatives
(`hillshade`, `slope`, `curvature`, `local_relief_model`, `multiscale_relief` —
an RVT-style blend), self-implemented in numpy/scikit-image.

- **`WallTracer`** — multiscale local-relief ridge response → threshold (walls
  protrude) → **gap bridging** (dilation, for partially destroyed walls) →
  `WALL` polylines.
- **`EdgeTracer`** — slope response (terrace/cut discontinuities) → `EDGE`
  polylines (no gap bridging — edges are continuous).

Both thresholds use a deterministic `mean + k·std` rule and funnel through
`dem._common.relief_response_to_features` → `geo.skeleton_to_polylines`
(skeletonise → junction-clustered trace → spur prune → simplify) →
`Feature`s (`Track.DEM_25D`). The pipeline runs both tracers on each DEM.

### Profile — section strata (`structura.profile`)
Sections are driven by fine **colour / texture** differences between strata
rather than relief. Input is a rectified, georeferenced section image;
`ProfileSegmenter` vectorises stratum boundaries.

### Temporal — daily integration (`structura.temporal`)
Daily captures document excavation progress; vectors from different days are
overlaid and intersected so features stay consistent across the series. Heavy
set operations are best delegated to PostGIS once vectors are stored.

## Sinks (`structura.db`)
All implement the `VectorSink` protocol (`write(features) -> int`):

- `FileSink` — write a GeoPackage or GeoJSON (format from the file extension;
  **implemented**, the testable default — inspect output in QGIS before the
  PostGIS-vs-API decision). Asserts a single CRS; never reprojects.
- `PostGISSink` — insert straight into a PostGIS table (geometry column with the
  feature CRS SRID; attributes incl. `properties` as JSONB). Stub (ROADMAP v0.5).
- `DjangoApiSink` — POST features as GeoJSON to the Django app's API. Stub (v0.5).

The active sink is chosen by `STRUCTURA_SINK` (`file` | `postgis` | `api`).

## Open decisions

- **DB integration:** write vectors **directly to PostGIS** vs. **via the Django
  API**. Both sinks exist behind one interface; the default is unresolved.
- **2D model choice:** SAM vs. Cellpose vs. classical CV — to be decided by the
  comparative evaluation (blocked on real excavation data).
- **Intake layout:** the discovery heuristic in `intake.discover_inputs` is
  filename-based and must be refined to the actual WebODM delivery layout
  (e.g. `odm_orthophoto/odm_orthophoto.tif`, `odm_dem/dsm.tif`).
