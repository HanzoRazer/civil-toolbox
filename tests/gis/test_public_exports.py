"""Tests for GIS module public exports."""

import pytest


class TestGISPublicExports:
    """Tests for public API exports."""

    def test_imports_geometry(self):
        """Imports Geometry."""
        from civil_toolbox.gis import Geometry

        geom = Geometry(geometry_type="Point", coordinates=[0.0, 0.0])
        assert geom.geometry_type == "Point"

    def test_imports_geometry_bounds(self):
        """Imports geometry_bounds."""
        from civil_toolbox.gis import Geometry, geometry_bounds

        geom = Geometry(geometry_type="Point", coordinates=[100.0, 50.0])
        bounds = geometry_bounds(geom)
        assert bounds == (100.0, 50.0, 100.0, 50.0)

    def test_imports_spatial_feature(self):
        """Imports SpatialFeature."""
        from civil_toolbox.gis import Geometry, SpatialFeature

        feature = SpatialFeature(
            id="test",
            geometry=Geometry(geometry_type="Point", coordinates=[0.0, 0.0]),
        )
        assert feature.id == "test"

    def test_imports_spatial_feature_collection(self):
        """Imports SpatialFeatureCollection."""
        from civil_toolbox.gis import SpatialFeatureCollection

        collection = SpatialFeatureCollection(name="Test")
        assert collection.name == "Test"

    def test_imports_collection_bounds(self):
        """Imports collection_bounds."""
        from civil_toolbox.gis import (
            Geometry,
            SpatialFeature,
            SpatialFeatureCollection,
            collection_bounds,
        )

        collection = SpatialFeatureCollection(
            features=[
                SpatialFeature(
                    id="p1",
                    geometry=Geometry(geometry_type="Point", coordinates=[0.0, 0.0]),
                )
            ]
        )
        bounds = collection_bounds(collection)
        assert bounds is not None

    def test_imports_export_function(self):
        """Imports export_feature_collection_to_geojson."""
        from civil_toolbox.gis import (
            SpatialFeatureCollection,
            export_feature_collection_to_geojson,
        )

        collection = SpatialFeatureCollection(name="Test")
        geojson = export_feature_collection_to_geojson(collection)
        assert geojson["type"] == "FeatureCollection"

    def test_imports_import_function(self):
        """Imports import_feature_collection_from_geojson."""
        from civil_toolbox.gis import import_feature_collection_from_geojson

        data = {"type": "FeatureCollection", "features": []}
        collection = import_feature_collection_from_geojson(data)
        assert collection.features == []

    def test_imports_save_geojson(self):
        """Imports save_geojson."""
        from civil_toolbox.gis import save_geojson

        assert callable(save_geojson)

    def test_imports_load_geojson(self):
        """Imports load_geojson."""
        from civil_toolbox.gis import load_geojson

        assert callable(load_geojson)

    def test_imports_feature_for_drainage_area(self):
        """Imports feature_for_drainage_area."""
        from civil_toolbox.gis import feature_for_drainage_area

        assert callable(feature_for_drainage_area)

    def test_imports_feature_for_infrastructure_node(self):
        """Imports feature_for_infrastructure_node."""
        from civil_toolbox.gis import feature_for_infrastructure_node

        assert callable(feature_for_infrastructure_node)

    def test_imports_feature_for_pipe(self):
        """Imports feature_for_pipe."""
        from civil_toolbox.gis import feature_for_pipe

        assert callable(feature_for_pipe)

    def test_imports_feature_for_flow_path(self):
        """Imports feature_for_flow_path."""
        from civil_toolbox.gis import feature_for_flow_path

        assert callable(feature_for_flow_path)

    def test_imports_create_example_collection(self):
        """Imports create_example_spatial_feature_collection."""
        from civil_toolbox.gis import create_example_spatial_feature_collection

        collection = create_example_spatial_feature_collection()
        assert len(collection.features) > 0

    def test_imports_gis_error(self):
        """Imports GISError."""
        from civil_toolbox.gis import GISError

        assert issubclass(GISError, ValueError)

    def test_imports_invalid_geometry_error(self):
        """Imports InvalidGeometryError."""
        from civil_toolbox.gis import InvalidGeometryError, GISError

        assert issubclass(InvalidGeometryError, GISError)

    def test_imports_invalid_geojson_error(self):
        """Imports InvalidGeoJSONError."""
        from civil_toolbox.gis import InvalidGeoJSONError, GISError

        assert issubclass(InvalidGeoJSONError, GISError)

    def test_imports_spatial_link_error(self):
        """Imports SpatialLinkError."""
        from civil_toolbox.gis import SpatialLinkError, GISError

        assert issubclass(SpatialLinkError, GISError)


class TestGISModuleImport:
    """Tests for module-level import."""

    def test_imports_module(self):
        """Imports gis module."""
        from civil_toolbox import gis

        assert hasattr(gis, "Geometry")
        assert hasattr(gis, "SpatialFeature")
        assert hasattr(gis, "SpatialFeatureCollection")

    def test_all_exports_defined(self):
        """__all__ contains expected exports."""
        from civil_toolbox import gis

        expected = [
            "Geometry",
            "geometry_bounds",
            "SpatialFeature",
            "SpatialFeatureCollection",
            "collection_bounds",
            "export_feature_collection_to_geojson",
            "import_feature_collection_from_geojson",
            "save_geojson",
            "load_geojson",
            "feature_for_drainage_area",
            "feature_for_infrastructure_node",
            "feature_for_pipe",
            "feature_for_flow_path",
            "create_example_spatial_feature_collection",
            "GISError",
            "InvalidGeometryError",
            "InvalidGeoJSONError",
            "SpatialLinkError",
        ]

        for name in expected:
            assert name in gis.__all__, f"{name} not in __all__"
            assert hasattr(gis, name), f"{name} not accessible on module"
