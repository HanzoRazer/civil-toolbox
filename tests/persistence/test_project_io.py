"""Tests for project file save and load utilities."""

import json
import pytest
from pathlib import Path

from civil_toolbox.domain.project import Project, DesignCriteria
from civil_toolbox.domain.scenario import Scenario
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.persistence.constants import (
    PROJECT_FILE_TYPE,
    PROJECT_SCHEMA_VERSION,
)
from civil_toolbox.persistence.errors import (
    InvalidProjectFileError,
    ProjectFileReadError,
    ProjectFileWriteError,
    UnsupportedProjectSchemaError,
)
from civil_toolbox.persistence.project_io import (
    project_to_file_data,
    project_from_file_data,
    save_project,
    load_project,
)


class TestProjectToFileData:
    """Tests for project_to_file_data."""

    def test_creates_envelope_with_file_type(self):
        project = Project(name="Test")
        data = project_to_file_data(project)
        assert data["file_type"] == PROJECT_FILE_TYPE

    def test_creates_envelope_with_schema_version(self):
        project = Project(name="Test")
        data = project_to_file_data(project)
        assert data["schema_version"] == PROJECT_SCHEMA_VERSION

    def test_creates_envelope_with_project(self):
        project = Project(name="Test Project")
        data = project_to_file_data(project)
        assert "project" in data
        assert data["project"]["name"] == "Test Project"

    def test_project_includes_id(self):
        project = Project(name="Test")
        data = project_to_file_data(project)
        assert "id" in data["project"]
        assert data["project"]["id"] == project.id

    def test_project_includes_metadata(self):
        project = Project(
            name="Full Project",
            client="Test Client",
            jurisdiction="harris_county",
        )
        data = project_to_file_data(project)
        assert data["project"]["client"] == "Test Client"
        assert data["project"]["jurisdiction"] == "harris_county"

    def test_project_includes_scenarios(self):
        project = Project(name="Test")
        scenario = Scenario(name="Existing")
        project.add_scenario(scenario)
        data = project_to_file_data(project)
        assert len(data["project"]["scenarios"]) == 1
        assert data["project"]["scenarios"][0]["name"] == "Existing"


class TestSaveProject:
    """Tests for save_project."""

    def test_saves_to_file(self, tmp_path: Path):
        project = Project(name="Save Test")
        file_path = tmp_path / "test.ctbx.json"
        result = save_project(project, file_path)
        assert result == file_path
        assert file_path.exists()

    def test_saved_file_is_valid_json(self, tmp_path: Path):
        project = Project(name="JSON Test")
        file_path = tmp_path / "test.ctbx.json"
        save_project(project, file_path)

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        assert data["file_type"] == PROJECT_FILE_TYPE

    def test_saved_file_contains_project_name(self, tmp_path: Path):
        project = Project(name="Named Project")
        file_path = tmp_path / "test.ctbx.json"
        save_project(project, file_path)

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        assert data["project"]["name"] == "Named Project"

    def test_accepts_string_path(self, tmp_path: Path):
        project = Project(name="String Path Test")
        file_path = str(tmp_path / "test.ctbx.json")
        result = save_project(project, file_path)
        assert isinstance(result, Path)
        assert result.exists()

    def test_accepts_path_object(self, tmp_path: Path):
        project = Project(name="Path Object Test")
        file_path = tmp_path / "test.ctbx.json"
        result = save_project(project, file_path)
        assert result == file_path

    def test_saved_file_is_utf8(self, tmp_path: Path):
        project = Project(name="UTF-8 Test: éàü")
        file_path = tmp_path / "test.ctbx.json"
        save_project(project, file_path)

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        assert "éàü" in content

    def test_saved_file_is_indented(self, tmp_path: Path):
        project = Project(name="Indent Test")
        file_path = tmp_path / "test.ctbx.json"
        save_project(project, file_path)

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Indented JSON will have newlines and spaces
        assert "\n" in content
        assert "  " in content

    def test_does_not_mutate_project(self, tmp_path: Path):
        project = Project(name="Original Name")
        original_id = project.id
        file_path = tmp_path / "test.ctbx.json"
        save_project(project, file_path)
        assert project.name == "Original Name"
        assert project.id == original_id

    def test_saves_project_with_scenario(self, tmp_path: Path):
        project = Project(name="With Scenario")
        scenario = Scenario(name="Existing Conditions")
        area = DrainageArea(name="Basin A", area_acres=50.0)
        scenario.add_drainage_area(area)
        project.add_scenario(scenario)

        file_path = tmp_path / "test.ctbx.json"
        save_project(project, file_path)

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data["project"]["scenarios"]) == 1
        assert len(data["project"]["scenarios"][0]["drainage_areas"]) == 1


class TestProjectFromFileData:
    """Tests for project_from_file_data."""

    def test_reconstructs_minimal_project(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": PROJECT_SCHEMA_VERSION,
            "project": {
                "id": "proj-123",
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-02T00:00:00",
                "name": "Test Project",
                "client": None,
                "description": None,
                "jurisdiction": None,
                "design_criteria": {},
                "scenarios": [],
            },
        }
        project = project_from_file_data(data)
        assert project.id == "proj-123"
        assert project.name == "Test Project"

    def test_reconstructs_project_with_scenario(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": PROJECT_SCHEMA_VERSION,
            "project": {
                "id": "proj-456",
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-02T00:00:00",
                "name": "With Scenario",
                "client": None,
                "description": None,
                "jurisdiction": None,
                "design_criteria": {},
                "scenarios": [
                    {
                        "id": "scen-789",
                        "created_at": "2026-01-01T00:00:00",
                        "updated_at": "2026-01-01T00:00:00",
                        "name": "Existing",
                        "description": None,
                        "project_id": "proj-456",
                        "drainage_areas": [],
                        "storm_events": [],
                        "flow_paths": [],
                        "infrastructure": [],
                        "calculation_results": [],
                    }
                ],
            },
        }
        project = project_from_file_data(data)
        assert len(project.scenarios) == 1
        assert project.scenarios[0].name == "Existing"


class TestLoadProject:
    """Tests for load_project."""

    def test_loads_minimal_project(self, tmp_path: Path):
        project = Project(name="Load Test")
        file_path = tmp_path / "test.ctbx.json"
        save_project(project, file_path)

        loaded = load_project(file_path)
        assert loaded.name == "Load Test"

    def test_loads_project_with_metadata(self, tmp_path: Path):
        project = Project(
            name="Metadata Test",
            client="Test Client",
            jurisdiction="harris_county",
        )
        file_path = tmp_path / "test.ctbx.json"
        save_project(project, file_path)

        loaded = load_project(file_path)
        assert loaded.client == "Test Client"
        assert loaded.jurisdiction == "harris_county"

    def test_loads_project_with_scenario(self, tmp_path: Path):
        project = Project(name="Scenario Test")
        scenario = Scenario(name="Existing Conditions")
        project.add_scenario(scenario)

        file_path = tmp_path / "test.ctbx.json"
        save_project(project, file_path)

        loaded = load_project(file_path)
        assert len(loaded.scenarios) == 1
        assert loaded.scenarios[0].name == "Existing Conditions"

    def test_loads_project_with_drainage_area(self, tmp_path: Path):
        project = Project(name="Drainage Test")
        scenario = Scenario(name="Existing")
        area = DrainageArea(name="Basin A", area_acres=50.0)
        scenario.add_drainage_area(area)
        project.add_scenario(scenario)

        file_path = tmp_path / "test.ctbx.json"
        save_project(project, file_path)

        loaded = load_project(file_path)
        assert len(loaded.scenarios[0].drainage_areas) == 1
        assert loaded.scenarios[0].drainage_areas[0].area_acres == 50.0

    def test_accepts_string_path(self, tmp_path: Path):
        project = Project(name="String Test")
        file_path = tmp_path / "test.ctbx.json"
        save_project(project, file_path)

        loaded = load_project(str(file_path))
        assert loaded.name == "String Test"

    def test_nonexistent_file_raises(self, tmp_path: Path):
        file_path = tmp_path / "nonexistent.ctbx.json"
        with pytest.raises(ProjectFileReadError) as exc_info:
            load_project(file_path)
        assert "not found" in str(exc_info.value)

    def test_invalid_json_raises(self, tmp_path: Path):
        file_path = tmp_path / "invalid.ctbx.json"
        file_path.write_text("not valid json {{{", encoding="utf-8")

        with pytest.raises(ProjectFileReadError) as exc_info:
            load_project(file_path)
        assert "Invalid JSON" in str(exc_info.value)

    def test_wrong_file_type_raises(self, tmp_path: Path):
        file_path = tmp_path / "wrong_type.ctbx.json"
        data = {
            "file_type": "wrong_type",
            "schema_version": PROJECT_SCHEMA_VERSION,
            "project": {},
        }
        file_path.write_text(json.dumps(data), encoding="utf-8")

        with pytest.raises(InvalidProjectFileError):
            load_project(file_path)

    def test_unsupported_schema_raises(self, tmp_path: Path):
        file_path = tmp_path / "old_schema.ctbx.json"
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": "0.1.0",
            "project": {},
        }
        file_path.write_text(json.dumps(data), encoding="utf-8")

        with pytest.raises(UnsupportedProjectSchemaError) as exc_info:
            load_project(file_path)
        assert exc_info.value.version == "0.1.0"

    def test_missing_project_raises(self, tmp_path: Path):
        file_path = tmp_path / "no_project.ctbx.json"
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": PROJECT_SCHEMA_VERSION,
        }
        file_path.write_text(json.dumps(data), encoding="utf-8")

        with pytest.raises(InvalidProjectFileError):
            load_project(file_path)


class TestSaveLoadRoundTrip:
    """Tests for save/load round trip."""

    def test_minimal_project_round_trip(self, tmp_path: Path):
        original = Project(name="Round Trip")
        file_path = tmp_path / "roundtrip.ctbx.json"
        save_project(original, file_path)
        loaded = load_project(file_path)

        assert loaded.id == original.id
        assert loaded.name == original.name

    def test_project_with_metadata_round_trip(self, tmp_path: Path):
        original = Project(
            name="Full Metadata",
            client="Test Client",
            description="Test description",
            jurisdiction="harris_county",
            design_criteria=DesignCriteria(
                design_storm_years=100,
                rainfall_distribution="Type III",
            ),
        )
        file_path = tmp_path / "metadata.ctbx.json"
        save_project(original, file_path)
        loaded = load_project(file_path)

        assert loaded.client == original.client
        assert loaded.description == original.description
        assert loaded.design_criteria.design_storm_years == 100

    def test_project_with_scenario_round_trip(self, tmp_path: Path):
        original = Project(name="Scenario Project")
        scenario = Scenario(name="Existing Conditions")
        original.add_scenario(scenario)

        file_path = tmp_path / "scenario.ctbx.json"
        save_project(original, file_path)
        loaded = load_project(file_path)

        assert len(loaded.scenarios) == 1
        assert loaded.scenarios[0].id == scenario.id
        assert loaded.scenarios[0].name == scenario.name

    def test_project_with_nested_entities_round_trip(self, tmp_path: Path):
        original = Project(name="Nested Entities")
        scenario = Scenario(name="Full Scenario")
        area = DrainageArea(
            name="Basin A",
            area_acres=50.0,
            runoff_coefficient=0.65,
            curve_number=80,
        )
        scenario.add_drainage_area(area)
        original.add_scenario(scenario)

        file_path = tmp_path / "nested.ctbx.json"
        save_project(original, file_path)
        loaded = load_project(file_path)

        loaded_area = loaded.scenarios[0].drainage_areas[0]
        assert loaded_area.id == area.id
        assert loaded_area.name == area.name
        assert loaded_area.area_acres == area.area_acres
        assert loaded_area.runoff_coefficient == area.runoff_coefficient
        assert loaded_area.curve_number == area.curve_number

    def test_multiple_scenarios_round_trip(self, tmp_path: Path):
        original = Project(name="Multi Scenario")
        original.add_scenario(Scenario(name="Existing"))
        original.add_scenario(Scenario(name="Proposed"))
        original.add_scenario(Scenario(name="With Detention"))

        file_path = tmp_path / "multi.ctbx.json"
        save_project(original, file_path)
        loaded = load_project(file_path)

        assert len(loaded.scenarios) == 3
        names = [s.name for s in loaded.scenarios]
        assert "Existing" in names
        assert "Proposed" in names
        assert "With Detention" in names
