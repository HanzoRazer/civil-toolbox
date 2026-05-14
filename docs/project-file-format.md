# Civil Toolbox Project File Format

This document describes the `.ctbx.json` project file format used by Civil Toolbox for saving and loading drainage analysis projects.

---

## Overview

Civil Toolbox uses a transparent JSON-based file format for project persistence. This approach provides:

- Human-readable project files
- Easy version control diffing
- Simple debugging and inspection
- Cross-platform compatibility
- Future migration support

---

## File Extension

```
.ctbx.json
```

The double extension indicates:
- `.ctbx` — Civil Toolbox project
- `.json` — JSON format

---

## Top-Level Structure

Every project file contains three required top-level fields:

```json
{
  "file_type": "civil_toolbox_project",
  "schema_version": "1.0.0",
  "project": { ... }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `file_type` | string | Must be `"civil_toolbox_project"` |
| `schema_version` | string | Semantic version of the file schema |
| `project` | object | The serialized project data |

---

## Schema Version

The `schema_version` field uses semantic versioning (e.g., `"1.0.0"`).

**Current version:** `1.0.0`

The schema version identifies the file format structure, not the Civil Toolbox application version. This allows:

- Detecting incompatible files before loading
- Migrating older files to current format
- Providing clear error messages for unsupported versions

---

## Project Payload

The `project` object contains the serialized `Project` domain entity:

```json
{
  "project": {
    "id": "uuid-string",
    "created_at": "2026-01-01T00:00:00+00:00",
    "updated_at": "2026-01-02T00:00:00+00:00",
    "name": "Project Name",
    "client": "Client Name",
    "description": "Project description",
    "jurisdiction": "harris_county",
    "design_criteria": { ... },
    "scenarios": [ ... ]
  }
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique project identifier |
| `created_at` | string | ISO 8601 timestamp |
| `updated_at` | string | ISO 8601 timestamp |
| `name` | string | Project name |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `client` | string | Client name |
| `description` | string | Project description |
| `jurisdiction` | string | Governing jurisdiction |
| `design_criteria` | object | Design criteria settings |
| `scenarios` | array | List of scenario objects |

---

## Example File

```json
{
  "file_type": "civil_toolbox_project",
  "schema_version": "1.0.0",
  "project": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "created_at": "2026-05-14T10:30:00+00:00",
    "updated_at": "2026-05-14T14:45:00+00:00",
    "name": "Downtown Drainage Study",
    "client": "City of Houston",
    "description": "Drainage analysis for downtown redevelopment",
    "jurisdiction": "harris_county",
    "design_criteria": {
      "design_storm_years": 100,
      "rainfall_distribution": "Type III",
      "jurisdiction": "harris_county",
      "allowed_methods": ["Rational", "TR-55"],
      "notes": null
    },
    "scenarios": [
      {
        "id": "scenario-uuid",
        "created_at": "2026-05-14T10:30:00+00:00",
        "updated_at": "2026-05-14T10:30:00+00:00",
        "name": "Existing Conditions",
        "description": null,
        "project_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "drainage_areas": [
          {
            "id": "area-uuid",
            "created_at": "2026-05-14T10:30:00+00:00",
            "updated_at": "2026-05-14T10:30:00+00:00",
            "name": "Basin A",
            "scenario_id": "scenario-uuid",
            "area_acres": 50.0,
            "runoff_coefficient": 0.65,
            "curve_number": 80,
            "soil_group": "B",
            "land_use": "commercial",
            "description": null
          }
        ],
        "storm_events": [],
        "flow_paths": [],
        "infrastructure": [],
        "calculation_results": []
      }
    ]
  }
}
```

---

## Validation Rules

When loading a project file, Civil Toolbox validates:

1. **File structure** — Must be valid JSON
2. **File type** — `file_type` must equal `"civil_toolbox_project"`
3. **Schema version** — `schema_version` must be supported
4. **Project payload** — `project` must be a valid object
5. **Domain entities** — All nested entities must pass validation

Invalid files produce clear error messages identifying the problem.

---

## Compatibility Policy

### Forward Compatibility

Files created with older schema versions may be loaded if a migration path exists. Civil Toolbox will automatically migrate the data to the current schema.

### Backward Compatibility

Files created with newer schema versions cannot be loaded by older Civil Toolbox versions. The application will report an unsupported schema error.

### Schema Changes

Schema changes follow semantic versioning:

- **Patch** (1.0.x) — Bug fixes, no structural changes
- **Minor** (1.x.0) — Additive changes, backward compatible
- **Major** (x.0.0) — Breaking changes, migration required

---

## Current Limitations

Version 1.0.0 has the following limitations:

- No binary attachments (drawings, images)
- No file compression
- No encryption
- No multi-file projects
- No collaborative editing support

These capabilities may be added in future versions.

---

## Usage

### Saving a Project

```python
from civil_toolbox.domain import Project
from civil_toolbox.persistence import save_project

project = Project(name="My Project")
save_project(project, "my-project.ctbx.json")
```

### Loading a Project

```python
from civil_toolbox.persistence import load_project

project = load_project("my-project.ctbx.json")
print(project.name)
```

---

## Related Documentation

- [Domain Model](domain-model.md) — Domain entity definitions
- [Architecture](../ARCHITECTURE.md) — System architecture
