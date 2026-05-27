"""Tests for GIS validation utilities."""

import pytest

from civil_toolbox.gis.errors import InvalidGeometryError
from civil_toolbox.gis.validation import (
    SUPPORTED_GEOMETRY_TYPES,
    SUPPORTED_FEATURE_ROLES,
    validate_non_empty_string,
    validate_geometry_type,
    validate_feature_role,
    validate_point_coordinates,
    validate_linestring_coordinates,
    validate_polygon_coordinates,
)


class TestSupportedConstants:
    """Tests for supported type constants."""

    def test_supported_geometry_types(self):
        """Expected geometry types are supported."""
        assert "Point" in SUPPORTED_GEOMETRY_TYPES
        assert "LineString" in SUPPORTED_GEOMETRY_TYPES
        assert "Polygon" in SUPPORTED_GEOMETRY_TYPES
        assert len(SUPPORTED_GEOMETRY_TYPES) == 3

    def test_supported_feature_roles(self):
        """Expected feature roles are supported."""
        expected = {
            "drainage_area",
            "flow_path",
            "infrastructure_node",
            "infrastructure_link",
            "project_boundary",
            "reference",
            "other",
        }
        assert SUPPORTED_FEATURE_ROLES == expected


class TestValidateNonEmptyString:
    """Tests for validate_non_empty_string."""

    def test_valid_string(self):
        """Non-empty string passes."""
        assert validate_non_empty_string("hello", "field") == "hello"

    def test_strips_whitespace(self):
        """Whitespace is stripped."""
        assert validate_non_empty_string("  hello  ", "field") == "hello"

    def test_empty_string_fails(self):
        """Empty string raises error."""
        with pytest.raises(InvalidGeometryError, match="cannot be empty"):
            validate_non_empty_string("", "field")

    def test_whitespace_only_fails(self):
        """Whitespace-only string raises error."""
        with pytest.raises(InvalidGeometryError, match="cannot be empty"):
            validate_non_empty_string("   ", "field")

    def test_non_string_fails(self):
        """Non-string value raises error."""
        with pytest.raises(InvalidGeometryError, match="must be a string"):
            validate_non_empty_string(123, "field")


class TestValidateGeometryType:
    """Tests for validate_geometry_type."""

    def test_point_valid(self):
        """Point is valid."""
        assert validate_geometry_type("Point") == "Point"

    def test_linestring_valid(self):
        """LineString is valid."""
        assert validate_geometry_type("LineString") == "LineString"

    def test_polygon_valid(self):
        """Polygon is valid."""
        assert validate_geometry_type("Polygon") == "Polygon"

    def test_unsupported_type_fails(self):
        """Unsupported geometry type raises error."""
        with pytest.raises(InvalidGeometryError, match="must be one of"):
            validate_geometry_type("MultiPoint")

    def test_case_sensitive(self):
        """Geometry type is case-sensitive."""
        with pytest.raises(InvalidGeometryError, match="must be one of"):
            validate_geometry_type("point")


class TestValidateFeatureRole:
    """Tests for validate_feature_role."""

    def test_drainage_area_valid(self):
        """drainage_area is valid."""
        assert validate_feature_role("drainage_area") == "drainage_area"

    def test_infrastructure_node_valid(self):
        """infrastructure_node is valid."""
        assert validate_feature_role("infrastructure_node") == "infrastructure_node"

    def test_all_roles_valid(self):
        """All supported roles pass validation."""
        for role in SUPPORTED_FEATURE_ROLES:
            assert validate_feature_role(role) == role

    def test_unsupported_role_fails(self):
        """Unsupported feature role raises error."""
        with pytest.raises(InvalidGeometryError, match="must be one of"):
            validate_feature_role("custom_role")


class TestValidatePointCoordinates:
    """Tests for validate_point_coordinates."""

    def test_valid_2d_point(self):
        """2D point coordinates pass."""
        result = validate_point_coordinates([100.0, 50.0])
        assert result == [100.0, 50.0]

    def test_valid_3d_point(self):
        """3D point coordinates pass."""
        result = validate_point_coordinates([100.0, 50.0, 10.0])
        assert result == [100.0, 50.0, 10.0]

    def test_tuple_accepted(self):
        """Tuple coordinates accepted."""
        result = validate_point_coordinates((100.0, 50.0))
        assert result == [100.0, 50.0]

    def test_integers_converted(self):
        """Integer coordinates converted to float."""
        result = validate_point_coordinates([100, 50])
        assert result == [100.0, 50.0]
        assert all(isinstance(c, float) for c in result)

    def test_single_value_fails(self):
        """Single coordinate value fails."""
        with pytest.raises(InvalidGeometryError, match="at least 2 values"):
            validate_point_coordinates([100.0])

    def test_empty_list_fails(self):
        """Empty list fails."""
        with pytest.raises(InvalidGeometryError, match="at least 2 values"):
            validate_point_coordinates([])

    def test_non_list_fails(self):
        """Non-list coordinates fail."""
        with pytest.raises(InvalidGeometryError, match="must be a list or tuple"):
            validate_point_coordinates("100,50")

    def test_non_numeric_fails(self):
        """Non-numeric coordinates fail."""
        with pytest.raises(InvalidGeometryError, match="must be numeric"):
            validate_point_coordinates(["x", "y"])


class TestValidateLinestringCoordinates:
    """Tests for validate_linestring_coordinates."""

    def test_valid_linestring(self):
        """Valid LineString coordinates pass."""
        coords = [[0.0, 0.0], [10.0, 10.0]]
        result = validate_linestring_coordinates(coords)
        assert result == [[0.0, 0.0], [10.0, 10.0]]

    def test_multi_point_linestring(self):
        """Multi-point LineString passes."""
        coords = [[0.0, 0.0], [5.0, 5.0], [10.0, 10.0]]
        result = validate_linestring_coordinates(coords)
        assert len(result) == 3

    def test_single_point_fails(self):
        """Single point LineString fails."""
        with pytest.raises(InvalidGeometryError, match="at least 2 points"):
            validate_linestring_coordinates([[0.0, 0.0]])

    def test_empty_list_fails(self):
        """Empty LineString fails."""
        with pytest.raises(InvalidGeometryError, match="at least 2 points"):
            validate_linestring_coordinates([])

    def test_invalid_point_fails(self):
        """Invalid point in LineString fails."""
        with pytest.raises(InvalidGeometryError, match="LineString point 1"):
            validate_linestring_coordinates([[0.0, 0.0], [10.0]])

    def test_non_list_fails(self):
        """Non-list coordinates fail."""
        with pytest.raises(InvalidGeometryError, match="must be a list"):
            validate_linestring_coordinates("invalid")


class TestValidatePolygonCoordinates:
    """Tests for validate_polygon_coordinates."""

    def test_valid_triangle(self):
        """Valid closed triangle passes."""
        coords = [[[0.0, 0.0], [10.0, 0.0], [5.0, 10.0], [0.0, 0.0]]]
        result = validate_polygon_coordinates(coords)
        assert len(result) == 1
        assert len(result[0]) == 4

    def test_valid_square(self):
        """Valid closed square passes."""
        coords = [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]]
        result = validate_polygon_coordinates(coords)
        assert len(result) == 1
        assert len(result[0]) == 5

    def test_polygon_with_hole(self):
        """Polygon with hole (multiple rings) passes."""
        outer = [[0.0, 0.0], [20.0, 0.0], [20.0, 20.0], [0.0, 20.0], [0.0, 0.0]]
        inner = [[5.0, 5.0], [15.0, 5.0], [15.0, 15.0], [5.0, 15.0], [5.0, 5.0]]
        result = validate_polygon_coordinates([outer, inner])
        assert len(result) == 2

    def test_unclosed_ring_fails(self):
        """Unclosed ring fails."""
        coords = [[[0.0, 0.0], [10.0, 0.0], [5.0, 10.0], [1.0, 1.0]]]
        with pytest.raises(InvalidGeometryError, match="not closed"):
            validate_polygon_coordinates(coords)

    def test_too_few_points_fails(self):
        """Ring with fewer than 4 points fails."""
        coords = [[[0.0, 0.0], [10.0, 0.0], [0.0, 0.0]]]
        with pytest.raises(InvalidGeometryError, match="at least 4 points"):
            validate_polygon_coordinates(coords)

    def test_empty_polygon_fails(self):
        """Empty polygon fails."""
        with pytest.raises(InvalidGeometryError, match="at least one ring"):
            validate_polygon_coordinates([])

    def test_invalid_ring_type_fails(self):
        """Invalid ring type fails."""
        with pytest.raises(InvalidGeometryError, match="ring 0 must be a list"):
            validate_polygon_coordinates(["invalid"])

    def test_invalid_point_in_ring_fails(self):
        """Invalid point in ring fails."""
        coords = [[[0.0, 0.0], [10.0], [5.0, 10.0], [0.0, 0.0]]]
        with pytest.raises(InvalidGeometryError, match="ring 0 point 1"):
            validate_polygon_coordinates(coords)

    def test_non_list_fails(self):
        """Non-list polygon fails."""
        with pytest.raises(InvalidGeometryError, match="must be a list of rings"):
            validate_polygon_coordinates("invalid")


class TestGISErrorInheritance:
    """Tests for GIS error inheritance."""

    def test_invalid_geometry_error_is_gis_error(self):
        """InvalidGeometryError inherits from GISError."""
        from civil_toolbox.gis.errors import GISError, InvalidGeometryError

        assert issubclass(InvalidGeometryError, GISError)

    def test_gis_error_is_value_error(self):
        """GISError inherits from ValueError."""
        from civil_toolbox.gis.errors import GISError

        assert issubclass(GISError, ValueError)

    def test_invalid_geojson_error_is_gis_error(self):
        """InvalidGeoJSONError inherits from GISError."""
        from civil_toolbox.gis.errors import GISError, InvalidGeoJSONError

        assert issubclass(InvalidGeoJSONError, GISError)

    def test_spatial_link_error_is_gis_error(self):
        """SpatialLinkError inherits from GISError."""
        from civil_toolbox.gis.errors import GISError, SpatialLinkError

        assert issubclass(SpatialLinkError, GISError)
