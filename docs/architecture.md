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
| `structura.segmentation` | 2D track — stones & surfaces (SAM / Cellpose / classical). |
| `structura.dem` | 2.5D track — relief derivatives + wall / edge tracing. |
| `structura.profile` | Profile track — section stratum segmentation. |
| `structura.temporal` | Temporal track — overlay / intersect of daily layers. |
| `structura.db` | Output sinks — direct PostGIS or Django API. |
| `structura.pipeline` | Orchestration: intake → tracks → sink. |

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

- `SamSegmenter` — Segment Anything (baseline).
- `CellposeSegmenter` — Cellpose instance masks (dense, roundish stones).
- `ClassicalSegmenter` — watershed / contour baseline (cheap, deterministic).

Masks become georeferenced polygons via `geo.mask_to_polygons`.

### 2.5D — walls & edges (`structura.dem`)
A wall protrudes slightly from its surroundings, so it shows up in local relief
far better than in the orthophoto. `dem.relief` computes derivatives (hillshade,
slope, curvature, local relief model); `WallTracer` turns the ridge/edge
response into polylines via `geo.skeleton_to_polylines`. Must **bridge gaps**
from partially destroyed walls and keep edges as separate polylines.

### Profile — section strata (`structura.profile`)
Sections are driven by fine **colour / texture** differences between strata
rather than relief. Input is a rectified, georeferenced section image;
`ProfileSegmenter` vectorises stratum boundaries.

### Temporal — daily integration (`structura.temporal`)
Daily captures document excavation progress; vectors from different days are
overlaid and intersected so features stay consistent across the series. Heavy
set operations are best delegated to PostGIS once vectors are stored.

## Sinks (`structura.db`)
Both implement the `VectorSink` protocol (`write(features) -> int`):

- `PostGISSink` — insert straight into a PostGIS table (geometry column with the
  feature CRS SRID; attributes incl. `properties` as JSONB).
- `DjangoApiSink` — POST features as GeoJSON to the Django app's API.

The active sink is chosen by `STRUCTURA_SINK` (`postgis` | `api`).

## Open decisions

- **DB integration:** write vectors **directly to PostGIS** vs. **via the Django
  API**. Both sinks exist behind one interface; the default is unresolved.
- **2D model choice:** SAM vs. Cellpose vs. classical CV — to be decided by the
  comparative evaluation (blocked on real excavation data).
- **Intake layout:** the discovery heuristic in `intake.discover_inputs` is
  filename-based and must be refined to the actual WebODM delivery layout
  (e.g. `odm_orthophoto/odm_orthophoto.tif`, `odm_dem/dsm.tif`).
