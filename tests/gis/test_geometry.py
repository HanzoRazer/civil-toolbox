"""Tests for GIS geometry model."""

import pytest

from civil_toolbox.gis.errors import InvalidGeometryError
from civil_toolbox.gis.geometry import Geometry, geometry_bounds, _flatten_coordinates


class TestGeometryCreation:
    """Tests for Geometry creation."""

    def test_create_point(self):
        """Creates Point geometry."""
        geom = Geometry(geometry_type="Point", coordinates=[100.0, 50.0])
        assert geom.geometry_type == "Point"
        assert geom.coordinates == [100.0, 50.0]

    def test_create_point_3d(self):
        """Creates 3D Point geometry."""
        geom = Geometry(geometry_type="Point", coordinates=[100.0, 50.0, 10.0])
        assert geom.coordinates == [100.0, 50.0, 10.0]

    def test_create_linestring(self):
        """Creates LineString geometry."""
        coords = [[0.0, 0.0], [10.0, 10.0], [20.0, 0.0]]
        geom = Geometry(geometry_type="LineString", coordinates=coords)
        assert geom.geometry_type == "LineString"
        assert len(geom.coordinates) == 3

    def test_create_polygon(self):
        """Creates Polygon geometry."""
        coords = [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]]
        geom = Geometry(geometry_type="Polygon", coordinates=coords)
        assert geom.geometry_type == "Polygon"
        assert len(geom.coordinates) == 1
        assert len(geom.coordinates[0]) == 5

    def test_invalid_geometry_type_fails(self):
        """Invalid geometry type raises error."""
        with pytest.raises(InvalidGeometryError, match="must be one of"):
            Geometry(geometry_type="MultiPoint", coordinates=[[0, 0], [1, 1]])

    def test_invalid_point_coordinates_fails(self):
        """Invalid Point coordinates raise error."""
        with pytest.raises(InvalidGeometryError, match="at least 2 values"):
            Geometry(geometry_type="Point", coordinates=[100.0])

    def test_invalid_linestring_coordinates_fails(self):
        """Invalid LineString coordinates raise error."""
        with pytest.raises(InvalidGeometryError, match="at least 2 points"):
            Geometry(geometry_type="LineString", coordinates=[[0.0, 0.0]])

    def test_invalid_polygon_coordinates_fails(self):
        """Invalid Polygon coordinates raise error."""
        coords = [[[0.0, 0.0], [10.0, 0.0], [5.0, 10.0], [1.0, 1.0]]]
        with pytest.raises(InvalidGeometryError, match="not closed"):
            Geometry(geometry_type="Polygon", coordinates=coords)


class TestGeometryGeoJSON:
    """Tests for GeoJSON serialization."""

    def test_point_to_geojson(self):
        """Point serializes to GeoJSON."""
        geom = Geometry(geometry_type="Point", coordinates=[100.0, 50.0])
        result = geom.to_geojson()
        assert result == {
            "type": "Point",
            "coordinates": [100.0, 50.0],
        }

    def test_linestring_to_geojson(self):
        """LineString serializes to GeoJSON."""
        geom = Geometry(geometry_type="LineString", coordinates=[[0.0, 0.0], [10.0, 10.0]])
        result = geom.to_geojson()
        assert result["type"] == "LineString"
        assert len(result["coordinates"]) == 2

    def test_polygon_to_geojson(self):
        """Polygon serializes to GeoJSON."""
        coords = [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]]
        geom = Geometry(geometry_type="Polygon", coordinates=coords)
        result = geom.to_geojson()
        assert result["type"] == "Polygon"
        assert len(result["coordinates"]) == 1

    def test_from_geojson_point(self):
        """Point deserializes from GeoJSON."""
        data = {"type": "Point", "coordinates": [100.0, 50.0]}
        geom = Geometry.from_geojson(data)
        assert geom.geometry_type == "Point"
        assert geom.coordinates == [100.0, 50.0]

    def test_from_geojson_linestring(self):
        """LineString deserializes from GeoJSON."""
        data = {"type": "LineString", "coordinates": [[0, 0], [10, 10]]}
        geom = Geometry.from_geojson(data)
        assert geom.geometry_type == "LineString"

    def test_from_geojson_polygon(self):
        """Polygon deserializes from GeoJSON."""
        data = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]],
        }
        geom = Geometry.from_geojson(data)
        assert geom.geometry_type == "Polygon"

    def test_from_geojson_missing_type_fails(self):
        """Missing type raises error."""
        with pytest.raises(InvalidGeometryError, match="missing 'type'"):
            Geometry.from_geojson({"coordinates": [0, 0]})

    def test_from_geojson_missing_coordinates_fails(self):
        """Missing coordinates raises error."""
        with pytest.raises(InvalidGeometryError, match="missing 'coordinates'"):
            Geometry.from_geojson({"type": "Point"})

    def test_from_geojson_non_dict_fails(self):
        """Non-dict input raises error."""
        with pytest.raises(InvalidGeometryError, match="must be a dict"):
            Geometry.from_geojson("invalid")

    def test_geojson_round_trip(self):
        """Geometry round-trips through GeoJSON."""
        original = Geometry(geometry_type="Point", coordinates=[100.0, 50.0])
        restored = Geometry.from_geojson(original.to_geojson())
        assert restored.geometry_type == original.geometry_type
        assert restored.coordinates == original.coordinates


class TestGeometryDict:
    """Tests for dict serialization."""

    def test_to_dict(self):
        """Geometry serializes to dict."""
        geom = Geometry(geometry_type="Point", coordinates=[100.0, 50.0])
        result = geom.to_dict()
        assert result == {
            "geometry_type": "Point",
            "coordinates": [100.0, 50.0],
        }

    def test_from_dict(self):
        """Geometry deserializes from dict."""
        data = {"geometry_type": "Point", "coordinates": [100.0, 50.0]}
        geom = Geometry.from_dict(data)
        assert geom.geometry_type == "Point"
        assert geom.coordinates == [100.0, 50.0]

    def test_dict_round_trip(self):
        """Geometry round-trips through dict."""
        original = Geometry(
            geometry_type="LineString",
            coordinates=[[0.0, 0.0], [10.0, 10.0]],
        )
        restored = Geometry.from_dict(original.to_dict())
        assert restored.geometry_type == original.geometry_type
        assert restored.coordinates == original.coordinates


class TestGeometryBounds:
    """Tests for geometry_bounds."""

    def test_point_bounds(self):
        """Point bounds are the point itself."""
        geom = Geometry(geometry_type="Point", coordinates=[100.0, 50.0])
        bounds = geometry_bounds(geom)
        assert bounds == (100.0, 50.0, 100.0, 50.0)

    def test_linestring_bounds(self):
        """LineString bounds span all points."""
        geom = Geometry(
            geometry_type="LineString",
            coordinates=[[0.0, 0.0], [10.0, 5.0], [20.0, 2.0]],
        )
        bounds = geometry_bounds(geom)
        assert bounds == (0.0, 0.0, 20.0, 5.0)

    def test_polygon_bounds(self):
        """Polygon bounds span all vertices."""
        coords = [[[0.0, 0.0], [15.0, 0.0], [15.0, 10.0], [0.0, 10.0], [0.0, 0.0]]]
        geom = Geometry(geometry_type="Polygon", coordinates=coords)
        bounds = geometry_bounds(geom)
        assert bounds == (0.0, 0.0, 15.0, 10.0)

    def test_polygon_with_hole_bounds(self):
        """Polygon with hole bounds span all rings."""
        outer = [[0.0, 0.0], [20.0, 0.0], [20.0, 20.0], [0.0, 20.0], [0.0, 0.0]]
        inner = [[5.0, 5.0], [15.0, 5.0], [15.0, 15.0], [5.0, 15.0], [5.0, 5.0]]
        geom = Geometry(geometry_type="Polygon", coordinates=[outer, inner])
        bounds = geometry_bounds(geom)
        assert bounds == (0.0, 0.0, 20.0, 20.0)


class TestFlattenCoordinates:
    """Tests for _flatten_coordinates helper."""

    def test_flatten_point(self):
        """Flattens point to single-element list."""
        result = _flatten_coordinates([100.0, 50.0])
        assert result == [[100.0, 50.0]]

    def test_flatten_linestring(self):
        """Flattens linestring to list of points."""
        result = _flatten_coordinates([[0.0, 0.0], [10.0, 10.0]])
        assert result == [[0.0, 0.0], [10.0, 10.0]]

    def test_flatten_polygon(self):
        """Flattens polygon rings to list of points."""
        coords = [[[0.0, 0.0], [10.0, 0.0], [0.0, 0.0]]]
        result = _flatten_coordinates(coords)
        assert len(result) == 3

    def test_flatten_empty(self):
        """Empty list returns empty."""
        assert _flatten_coordinates([]) == []
