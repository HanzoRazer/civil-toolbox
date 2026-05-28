"""Tests for GeoJSON import/export utilities."""

import json
import pytest
from pathlib import Path

from civil_toolbox.gis.errors import InvalidGeoJSONError
from civil_toolbox.gis.geometry import Geometry
from civil_toolbox.gis.features import SpatialFeature
from civil_toolbox.gis.collections import SpatialFeatureCollection
from civil_toolbox.gis.geojson import (
    export_feature_collection_to_geojson,
    import_feature_collection_from_geojson,
    save_geojson,
    load_geojson,
)


def make_test_collection() -> SpatialFeatureCollection:
    """Create a test collection."""
    return SpatialFeatureCollection(
        id="test_collection",
        name="Test Collection",
        features=[
            SpatialFeature(
                id="node_001",
                geometry=Geometry(geometry_type="Point", coordinates=[100.0, 50.0]),
                feature_role="infrastructure_node",
                entity_id="mh_001",
                entity_type="InfrastructureNode",
            ),
            SpatialFeature(
                id="area_001",
                geometry=Geometry(
                    geometry_type="Polygon",
                    coordinates=[[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]],
                ),
                feature_role="drainage_area",
            ),
        ],
        coordinate_reference="EPSG:4326",
    )


class TestExportFeatureCollectionToGeojson:
    """Tests for export_feature_collection_to_geojson."""

    def test_exports_to_dict(self):
        """Exports collection to GeoJSON dict."""
        collection = make_test_collection()
        result = export_feature_collection_to_geojson(collection)

        assert result["type"] == "FeatureCollection"
        assert len(result["features"]) == 2
        assert result["properties"]["collection_id"] == "test_collection"

    def test_exports_empty_collection(self):
        """Exports empty collection."""
        collection = SpatialFeatureCollection(id="empty", name="Empty")
        result = export_feature_collection_to_geojson(collection)

        assert result["type"] == "FeatureCollection"
        assert result["features"] == []


class TestImportFeatureCollectionFromGeojson:
    """Tests for import_feature_collection_from_geojson."""

    def test_imports_from_dict(self):
        """Imports collection from GeoJSON dict."""
        data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "feat_001",
                    "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
                    "properties": {"feature_role": "other"},
                }
            ],
            "properties": {"collection_id": "imported"},
        }
        collection = import_feature_collection_from_geojson(data)

        assert collection.id == "imported"
        assert len(collection.features) == 1

    def test_invalid_geojson_fails(self):
        """Invalid GeoJSON raises error."""
        with pytest.raises(InvalidGeoJSONError):
            import_feature_collection_from_geojson({"type": "Invalid"})


class TestSaveGeojson:
    """Tests for save_geojson."""

    def test_saves_geojson_file(self, tmp_path):
        """Saves GeoJSON to file."""
        collection = make_test_collection()
        output_path = tmp_path / "test.geojson"

        result = save_geojson(collection, output_path)

        assert result == output_path
        assert output_path.exists()

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 2

    def test_creates_parent_directories(self, tmp_path):
        """Creates parent directories if needed."""
        collection = make_test_collection()
        output_path = tmp_path / "nested" / "dirs" / "test.geojson"

        result = save_geojson(collection, output_path)

        assert result == output_path
        assert output_path.exists()

    def test_overwrites_existing_file(self, tmp_path):
        """Overwrites existing file."""
        output_path = tmp_path / "test.geojson"
        output_path.write_text('{"old": "data"}')

        collection = make_test_collection()
        save_geojson(collection, output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["type"] == "FeatureCollection"

    def test_accepts_string_path(self, tmp_path):
        """Accepts string path."""
        collection = make_test_collection()
        output_path = str(tmp_path / "test.geojson")

        result = save_geojson(collection, output_path)

        assert isinstance(result, Path)
        assert result.exists()

    def test_utf8_encoding(self, tmp_path):
        """File uses UTF-8 encoding."""
        collection = SpatialFeatureCollection(
            id="unicode_test",
            name="Test äöü 中文",
            features=[
                SpatialFeature(
                    id="feat_001",
                    geometry=Geometry(geometry_type="Point", coordinates=[0.0, 0.0]),
                    properties={"name": "Ñoño Creek"},
                )
            ],
        )
        output_path = tmp_path / "unicode.geojson"

        save_geojson(collection, output_path)

        content = output_path.read_text(encoding="utf-8")
        assert "äöü" in content
        assert "中文" in content
        assert "Ñoño" in content


class TestLoadGeojson:
    """Tests for load_geojson."""

    def test_loads_geojson_file(self, tmp_path):
        """Loads GeoJSON from file."""
        collection = make_test_collection()
        file_path = tmp_path / "test.geojson"
        save_geojson(collection, file_path)

        loaded = load_geojson(file_path)

        assert loaded.id == "test_collection"
        assert len(loaded.features) == 2

    def test_file_not_found_fails(self, tmp_path):
        """Missing file raises error."""
        with pytest.raises(InvalidGeoJSONError, match="not found"):
            load_geojson(tmp_path / "nonexistent.geojson")

    def test_invalid_json_fails(self, tmp_path):
        """Invalid JSON raises error."""
        file_path = tmp_path / "invalid.geojson"
        file_path.write_text("not valid json {{{")

        with pytest.raises(InvalidGeoJSONError, match="Invalid JSON"):
            load_geojson(file_path)

    def test_invalid_geojson_structure_fails(self, tmp_path):
        """Invalid GeoJSON structure raises error."""
        file_path = tmp_path / "bad.geojson"
        file_path.write_text('{"type": "NotFeatureCollection"}')

        with pytest.raises(InvalidGeoJSONError, match="FeatureCollection"):
            load_geojson(file_path)

    def test_accepts_string_path(self, tmp_path):
        """Accepts string path."""
        collection = make_test_collection()
        file_path = tmp_path / "test.geojson"
        save_geojson(collection, file_path)

        loaded = load_geojson(str(file_path))

        assert loaded.id == "test_collection"


class TestRoundTrip:
    """Tests for save/load round-trip."""

    def test_full_round_trip(self, tmp_path):
        """Collection survives save/load round-trip."""
        original = make_test_collection()
        file_path = tmp_path / "roundtrip.geojson"

        save_geojson(original, file_path)
        restored = load_geojson(file_path)

        assert restored.id == original.id
        assert restored.name == original.name
        assert len(restored.features) == len(original.features)
        assert restored.coordinate_reference == original.coordinate_reference

        original_node = original.get_feature("node_001")
        restored_node = restored.get_feature("node_001")
        assert restored_node is not None
        assert restored_node.entity_id == original_node.entity_id
        assert restored_node.entity_type == original_node.entity_type
