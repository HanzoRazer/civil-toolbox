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
from civil_toolbox.persistence.errors import ProjectFileWriteError
from civil_toolbox.persistence.project_io import (
    project_to_file_data,
    save_project,
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
