# Architecture

Civil Toolbox is transitioning from a calculator collection to a project-centered drainage analysis workstation.

---

## Current State

The repository currently contains:

- Hydrologic calculators (Rational Method, TR-55, Tc methods)
- Basic test coverage
- FastAPI backend scaffold
- Package structure for future expansion

### Current Package Structure

```text
packages/
  hydro-kernel/        # Hydrology: rainfall → runoff → peak Q
  hydraulic-kernel/    # Open channel hydraulics
  floodplain-kernel/   # BFE comparison, no-rise math
  fema-integration/    # NFHL REST API client
  petition/            # Petition document model
  civil-shared/        # Shared utilities
  server/              # FastAPI backend
```

---

## Target State

Civil Toolbox will become a workstation where:

- Calculations belong to projects
- Projects organize drainage systems
- Systems contain infrastructure objects
- Infrastructure participates in scenarios
- Scenarios produce reports and decisions

---

## Domain Model

```text
Project
 ├── Metadata
 │    ├── name
 │    ├── client
 │    ├── jurisdiction
 │    └── created_at
 │
 ├── DesignCriteria
 │    ├── design_storm
 │    ├── rainfall_data
 │    └── jurisdiction_rules
 │
 ├── Scenario[]
 │    ├── name (e.g., "Existing", "Proposed", "With Detention")
 │    │
 │    ├── DrainageArea[]
 │    │    ├── geometry
 │    │    ├── area_acres
 │    │    ├── runoff_coefficient
 │    │    ├── curve_number
 │    │    ├── soil_group
 │    │    ├── land_use_composition
 │    │    └── tc_segments[]
 │    │
 │    ├── StormEvent[]
 │    │    ├── return_period
 │    │    ├── duration
 │    │    ├── depth_inches
 │    │    └── distribution
 │    │
 │    ├── FlowPath[]
 │    │    ├── segments[]
 │    │    ├── total_length_ft
 │    │    └── tc_minutes
 │    │
 │    ├── InfrastructureElement[]
 │    │    ├── type (pipe, culvert, channel, inlet, pond)
 │    │    ├── geometry
 │    │    ├── hydraulic_properties
 │    │    └── capacity_cfs
 │    │
 │    └── CalculationResult[]
 │         ├── method
 │         ├── inputs
 │         ├── outputs
 │         ├── warnings
 │         └── timestamp
 │
 ├── Reports[]
 │    ├── type
 │    ├── generated_at
 │    └── content
 │
 └── Attachments[]
      ├── filename
      ├── type
      └── content
```

---

## Separation of Concerns

### Calculation Engine

The calculation engine must remain independent of:

- UI frameworks
- Persistence mechanisms
- Network protocols
- Presentation logic

```text
┌─────────────────────────────────────────────────────────┐
│                     Applications                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │   Web   │  │ Desktop │  │   CLI   │  │   API   │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘    │
│       │            │            │            │          │
│       └────────────┴─────┬──────┴────────────┘          │
│                          │                              │
│  ┌───────────────────────▼───────────────────────────┐  │
│  │              Service Layer                         │  │
│  │   (orchestration, validation, persistence)         │  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────▼───────────────────────────┐  │
│  │            Calculation Kernels                     │  │
│  │   hydro-kernel │ hydraulic-kernel │ floodplain    │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Kernel Requirements

Calculation kernels must be:

- **Pure**: No side effects, no I/O
- **Deterministic**: Same inputs → same outputs
- **Typed**: Explicit parameter and return types
- **Documented**: Equations, units, references
- **Tested**: Validation against known benchmarks

---

## Calculation Engine Direction

### CalcResult Pattern

All calculations return a structured result:

```python
@dataclass
class CalcResult:
    value: float
    units: str
    formula_id: str
    references: tuple[Reference, ...]
    inputs: dict[str, Any]
    applicability_warnings: tuple[str, ...]
    derivation: str
```

### Method Registry

Methods should be registered with metadata:

```python
@register_method(
    id="RATIONAL",
    name="Rational Method",
    category="hydrology",
    references=[RATIONAL_REF],
)
def rational_q(c: float, i_in_per_hr: float, a_acres: float) -> CalcResult:
    ...
```

---

## Infrastructure Elements

Infrastructure objects are first-class entities with hydraulic properties.

### Planned Types

| Type | Properties |
|------|------------|
| Pipe | diameter, material, slope, length, Manning's n |
| Culvert | shape, dimensions, inlet type, outlet type |
| Channel | cross-section, slope, lining, Manning's n |
| Inlet | type, efficiency curve, spread |
| Detention Pond | stage-storage, outlet structure |
| Outlet Structure | weir, orifice, riser configuration |

### Hydraulic Analysis

Each element supports:

- Capacity calculation
- Headloss calculation
- Surcharge analysis (where applicable)
- Connection to upstream/downstream elements

---

## Persistence Strategy

### Requirements

- Projects must be serializable
- Calculation history must be preserved
- Scenarios must be comparable
- Attachments must be manageable

### Planned Approach

```text
┌─────────────────────────────────────┐
│         Project Storage             │
├─────────────────────────────────────┤
│  Local: SQLite + file attachments   │
│  Cloud: PostgreSQL + object storage │
└─────────────────────────────────────┘
```

### Project File Format

Projects serialize to JSON for portability:

```json
{
  "version": "1.0",
  "project": {
    "name": "Example Site Drainage",
    "client": "ABC Development",
    "jurisdiction": "harris_county"
  },
  "scenarios": [...],
  "calculations": [...],
  "attachments": [...]
}
```

---

## Reporting Pipeline

### Requirements

- Generate engineering-ready reports
- Include calculation audit trails
- Support jurisdiction-specific formats
- Export to PDF, Word, HTML

### Pipeline

```text
Project + Scenario
       │
       ▼
┌──────────────┐
│  Report      │
│  Template    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Renderer    │
│  (Jinja2)    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Exporter    │
│  (PDF/DOCX)  │
└──────────────┘
```

---

## Jurisdiction Profiles

Different jurisdictions have different requirements.

### Profile Contents

```python
@dataclass
class JurisdictionProfile:
    name: str
    design_storms: dict[str, StormDefinition]
    allowed_methods: list[str]
    report_requirements: list[str]
    review_checklist: list[str]
```

### Planned Profiles

| Profile | Description |
|---------|-------------|
| `generic` | Vanilla TR-55/Rational |
| `hcfcd` | Harris County Flood Control District |
| `txdot` | Texas DOT drainage criteria |

---

## Future Package Structure

```text
civil-toolbox/
│
├── apps/
│   ├── web/              # Vue 3 + TypeScript frontend
│   ├── desktop/          # Electron wrapper (future)
│   └── cli/              # Command-line interface
│
├── packages/
│   ├── hydro-kernel/     # Hydrology calculations
│   ├── hydraulic-kernel/ # Hydraulics calculations
│   ├── floodplain/       # Floodplain analysis
│   ├── infrastructure/   # Pipe, culvert, pond models
│   ├── gis/              # Spatial workflows
│   ├── reporting/        # Report generation
│   ├── persistence/      # Project storage
│   └── shared/           # Common utilities
│
├── server/               # FastAPI backend
│
├── docs/
│   ├── architecture/
│   ├── methods/
│   └── api/
│
└── tests/
    ├── unit/
    ├── integration/
    └── validation/
```

---

## Key Architectural Principles

1. **Calculation kernels are pure** — No I/O, no state, no UI concerns
2. **Units are explicit** — Never pass bare floats without unit context
3. **Results are auditable** — Every output traces to inputs and method
4. **Scenarios are comparable** — Same project, different assumptions
5. **Persistence is pluggable** — Local files, SQLite, cloud storage
6. **UI is separate** — Web, desktop, CLI share the same engine
7. **Jurisdiction rules are data** — Profiles, not hardcoded logic
