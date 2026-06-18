# SPDX-License-Identifier: AGPL-3.0-or-later

"""File sink: write features to a GeoPackage or GeoJSON (requires the ``geo`` extra).

The testable default sink — lets the pipeline run end-to-end and the output be
inspected in QGIS before the PostGIS-vs-API decision (see ROADMAP). The output
format is chosen from the file extension.
"""

from __future__ import annotations

from pathlib import Path

from ..models import Feature


class FileSink:
    """Write features to a single GeoPackage (``.gpkg``) or GeoJSON file.

    All features must share one CRS — the sink never reprojects (consistent with
    the project's georeferencing doctrine). ``properties`` are serialised to a
    JSON string column, mirroring the PostGIS JSONB intent.
    """

    name = "file"

    def __init__(self, output_path: str | Path, layer: str = "features") -> None:
        self.output_path = Path(output_path)
        self.layer = layer  # GeoPackage layer name; ignored for GeoJSON

    def write(self, features: list[Feature]) -> int:
        if not features:
            return 0  # nothing to write (geopandas can't infer CRS from 0 rows)

        import json  # noqa: PLC0415

        import geopandas as gpd  # noqa: PLC0415

        crs_set = {f.crs for f in features}
        if len(crs_set) != 1:
            raise AssertionError(f"FileSink requires a single CRS, got {crs_set}")
        crs = crs_set.pop()

        records = [
            {
                "geometry": f.geometry,
                "feature_type": f.feature_type.value,
                "track": f.track.value,
                "captured_on": f.captured_on.isoformat() if f.captured_on else None,
                "stratum": f.stratum,
                "properties": json.dumps(f.properties, sort_keys=True, default=str),
            }
            for f in features
        ]
        gdf = gpd.GeoDataFrame(records, geometry="geometry", crs=crs)

        suffix = self.output_path.suffix.lower()
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        if suffix == ".gpkg":
            gdf.to_file(self.output_path, driver="GPKG", layer=self.layer)
        elif suffix in (".geojson", ".json"):
            gdf.to_file(self.output_path, driver="GeoJSON")
        else:
            raise ValueError(f"Unsupported output extension: {self.output_path.suffix!r}")

        return len(features)
