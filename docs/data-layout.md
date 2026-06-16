# Data layout, configuration & output

## Configuration

Structura reads configuration from the environment, with an optional `.env`
file loaded by `structura.config`. Copy the template and edit:

```bash
cp .env.example .env
```

| Variable | Meaning | Default |
|----------|---------|---------|
| `STRUCTURA_INPUT_DIR` | Directory WebODM raster products land in | `./data/incoming` |
| `STRUCTURA_2D_BACKEND` | 2D segmenter: `classical`, `sam`, or `cellpose` (latter two need their extra) | `classical` |
| `STRUCTURA_GPU` | Use GPU for the `sam`/`cellpose` backends | `false` |
| `STRUCTURA_GAP_BRIDGE_M` | 2.5D wall-tracing gap-bridging tolerance (world units) | `0.3` |
| `STRUCTURA_SINK` | Output sink: `file`, `postgis`, or `api` | `file` |
| `STRUCTURA_OUTPUT_PATH` | File-sink output (format from extension: `.gpkg` / `.geojson`) | `./data/output/features.gpkg` |
| `PGHOST` / `PGPORT` / `PGDATABASE` / `PGUSER` / `PGPASSWORD` | PostGIS connection | `localhost` / `5432` / `excavation` / `structura` / — |
| `STRUCTURA_PG_SCHEMA` / `STRUCTURA_PG_TABLE` | Target schema / table | `public` / `features` |
| `STRUCTURA_API_BASE_URL` | Django API base URL (when `sink=api`) | — |
| `STRUCTURA_API_TOKEN` | Django API token (when `sink=api`) | — |

`.env` is git-ignored; never commit credentials.

## Input rasters

Structura consumes **georeferenced** raster products from an upstream WebODM /
OpenDroneMap survey:

- **Orthophoto** — RGB, georeferenced → drives the 2D segmentation track.
- **DEM** (DSM/DTM) — elevation, georeferenced → drives the 2.5D track.

`structura.intake.discover_inputs` scans `STRUCTURA_INPUT_DIR` recursively for
`*.tif` and tags each file by a filename heuristic:

- name contains `ortho` → `ORTHO`
- name contains `dem` / `dsm` / `dtm` → `DEM`

> The heuristic is a placeholder. Refine it to the actual WebODM delivery
> layout, e.g. `odm_orthophoto/odm_orthophoto.tif` and `odm_dem/dsm.tif`.

Large rasters are **not** versioned in git — `data/`, `*.tif`, `*.tiff`,
`*.laz`, `*.las`, `*.ply` are ignored (see `.gitignore`). Keep capture data in
external storage (e.g. a synced share), not in the repository.

### Daily captures

For the temporal track, deliver one orthophoto + DEM per excavation day. Encode
the capture date so `Feature.captured_on` can be populated (e.g.
`orthophoto_2026-07-14.tif`) and days can be overlaid / intersected.

## Coordinate reference systems

Every feature carries the **source raster's CRS** (`Feature.crs`, e.g.
`EPSG:32636`). The affine transform read with the raster maps pixel `(col, row)`
to world `(x, y)`. Structura does **not** silently reproject — keep all inputs in
one CRS, or reproject upstream before intake.

## Output

The pipeline produces a list of georeferenced `Feature`s and hands them to the
configured sink. Orthophotos yield `stone`/`surface` **polygons** (2D track);
DEMs yield `wall`/`edge` **polylines** (2.5D track). The sinks:

- **File** (`STRUCTURA_SINK=file`, the default) — features are written to
  `STRUCTURA_OUTPUT_PATH`. The format follows the extension: `.gpkg` →
  GeoPackage (single file, QGIS-native), `.geojson` / `.json` → GeoJSON.
  Attributes are `feature_type`, `track`, `captured_on` (ISO date), `stratum`,
  and `properties` (serialised as a JSON string). All features must share one
  CRS — the sink never reprojects.
- **PostGIS** (`STRUCTURA_SINK=postgis`) — features are inserted into
  `STRUCTURA_PG_SCHEMA.STRUCTURA_PG_TABLE` with a geometry column (feature CRS
  SRID) plus attributes (`feature_type`, `track`, `captured_on`, `stratum`, and
  `properties` as JSONB).
- **Django API** (`STRUCTURA_SINK=api`) — features are POSTed as GeoJSON to
  `STRUCTURA_API_BASE_URL` with token authentication.

`structura run --dry-run` runs the full pipeline but skips the sink write, which
is useful for inspecting feature counts without touching the database.

**Stratum attribution is downstream.** Structura emits geometry; the
archaeologist assigns each feature to a stratum interactively in the database
webview. `Feature.stratum` is therefore usually `None` at this stage.
