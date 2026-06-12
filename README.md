# Structura — Workflow App

Workflow application for the **vectorisation step** of the Structura excavation
pipeline: it ingests photogrammetric raster products and produces **georeferenced
vector geometry** for an excavation database.

> Research context, goals and the full idea: see
> [`../paper/input/description/project-description.md`](../paper/input/description/project-description.md).

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
              │ — direct write OR via API: TBD   │
              └─────────────────────────────────┘
                               │
                               ▼
              Interactive stratum annotation (webview, polygon)
              → per-stratum / combined excavation plans
```

## Tracks

| Track | Input | Method (to evaluate) | Output geometry |
|-------|-------|----------------------|-----------------|
| **2D** stones & surfaces | orthophoto | SAM, Cellpose, classical CV | closed polygons |
| **2.5D** walls & edges | DEM | relief/ridge detection, learned models | polylines |
| **Profile** strata | section image | colour/texture segmentation | section vectors |
| **Temporal** progress | daily vector layers | PostGIS overlay / intersect | reconciled layers |

## Key constraints

- **Everything is georeferenced** — vectors carry the raster CRS.
- **Stratified, complex scenes** — many superimposed layers, not a singular wall;
  walls may be **partially destroyed / discontinuous**.
- **Daily captures** — results across days are overlaid/intersected.
- **Stratum attribution is downstream & interactive** — the archaeologist marks a
  feature's area as a polygon in the DB webview; this app produces the vectors.

## Open decisions

- **DB integration:** write vectors **directly to PostGIS** vs. **via the Django
  API**. (Undecided.)
- **2D model choice:** SAM vs. Cellpose vs. classical CV — to be decided by the
  comparative evaluation in the paper.
- **App tech stack:** Python is the natural fit (SAM/Cellpose, GDAL/rasterio,
  Shapely, psycopg/SQLAlchemy + PostGIS). Orchestration/UI layer TBD.

## Status

Scaffolding stage. See the research project under [`../paper/`](../paper/) for the
methodology, evaluation plan, and literature.
