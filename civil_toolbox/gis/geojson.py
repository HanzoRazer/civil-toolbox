"""GeoJSON import and export utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from civil_toolbox.gis.errors import InvalidGeoJSONError
from civil_toolbox.gis.collections import SpatialFeatureCollection


def export_feature_collection_to_geojson(
    collection: SpatialFeatureCollection,
) -> dict[str, Any]:
    """Export a feature collection to GeoJSON dict.

    Args:
        collection: The collection to export.

    Returns:
        GeoJSON FeatureCollection dictionary.
    """
    return collection.to_geojson()


def import_feature_collection_from_geojson(
    data: dict[str, Any],
) -> SpatialFeatureCollection:
    """Import a feature collection from GeoJSON dict.

    Args:
        data: GeoJSON FeatureCollection dictionary.

    Returns:
        SpatialFeatureCollection instance.

    Raises:
        InvalidGeoJSONError: If data is invalid.
    """
    return SpatialFeatureCollection.from_geojson(data)


def save_geojson(
    collection: SpatialFeatureCollection,
    path: str | Path,
) -> Path:
    """Save a feature collection to a GeoJSON file.

    Creates parent directories if they don't exist.

    Args:
        collection: The collection to save.
        path: File path to write.

    Returns:
        The Path where the file was saved.

    Raises:
        InvalidGeoJSONError: If the file cannot be written.
    """
    path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)

    geojson_data = collection.to_geojson()

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(geojson_data, f, indent=2, ensure_ascii=False)
    except OSError as e:
        raise InvalidGeoJSONError(f"Failed to write GeoJSON file: {e}") from e

    return path


def load_geojson(path: str | Path) -> SpatialFeatureCollection:
    """Load a feature collection from a GeoJSON file.

    Args:
        path: File path to read.

    Returns:
        SpatialFeatureCollection instance.

    Raises:
        InvalidGeoJSONError: If the file cannot be read or contains invalid GeoJSON.
    """
    path = Path(path)

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError as e:
        raise InvalidGeoJSONError(f"GeoJSON file not found: {path}") from e
    except OSError as e:
        raise InvalidGeoJSONError(f"Failed to read GeoJSON file: {e}") from e

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise InvalidGeoJSONError(f"Invalid JSON in file: {e}") from e

    return SpatialFeatureCollection.from_geojson(data)
