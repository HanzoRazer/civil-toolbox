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

### Implemented Types

| Type | Properties |
|------|------------|
| Pipe | shape (circular/box/arch), diameter/width/height, slope, length, Manning's n |
| Culvert | shape, dimensions, inlet/outlet type, embankment, headwater |
| OpenChannel | shape (rectangular/trapezoidal/triangular), width, depth, side slopes |
| Inlet | type (grate/curb/combination/slotted), dimensions, clogging factor |
| DetentionFacility | stage-storage curve, spillway, outlet reference |
| OutletStructure | type (orifice/weir/riser/combined), coefficients, dimensions |
| Swale | type (grass/bioswale/rock), width, depth, side slope, infiltration |

### Network Model

Elements connect via InfrastructureNode references:

- Pipes, culverts, channels: upstream_node_id, downstream_node_id
- Inlets: node_id
- Detention: outlet_node_id

### Hydraulic Analysis (Future)

Capacity, headloss, and surcharge calculations will be added in infrastructure-sizing-foundation

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

## Persistence Layer

The persistence layer provides transparent project storage using JSON files.

```text
Domain Models → Project Persistence → Reports / UI / CLI / Future APIs
```

### Current Implementation

- **Format**: JSON with `.ctbx.json` extension
- **Schema versioning**: Explicit `schema_version` field
- **Migration support**: Entry point for future schema migrations
- **Validation**: Envelope validation before domain reconstruction

### Persistence Principles

1. **Transparent format** — Human-readable, diffable JSON
2. **Schema-aware** — Version metadata enables future migrations
3. **Validation-first** — Invalid files fail clearly before reconstruction
4. **No side effects** — Persistence does not run calculations

See [Project File Format](docs/project-file-format.md) for details.

---

## Comparison Layer

The comparison layer enables scenario-to-scenario analysis.

```text
Scenario A + Scenario B → Entity Matching → Metric Comparison → Aggregated Results
```

### Current Implementation

- **Match strategies**: auto (explicit > ID > name), id, name, explicit
- **Recognized metrics**: peak_flow_cfs, runoff_depth_in, runoff_volume_cuft, time_of_concentration_min
- **Aggregation**: Additive metrics (peak flow, volume) sum at scenario level
- **Missing data**: Tracked with status (missing_baseline, missing_comparison)
- **Zero baseline**: percent_delta=None with undefined_zero_baseline status
- **Serialization**: Full round-trip support, ephemeral results (not persisted)

### Comparison Principles

1. **Data-first** — Comparison results are data structures, not reports
2. **Explicit matching** — Entity pairing is controllable and auditable
3. **Missing is visible** — Incomplete data produces status flags, not errors
4. **Additive vs non-additive** — Only appropriate metrics aggregate at scenario level

See [Scenario Comparison](docs/comparison.md) for details.

### Storm Sensitivity Comparison

Analyze how metrics change across storm intensities for a single scenario.

```text
Scenario + Multiple Storms → Per-Entity Per-Storm Metrics → Storm Totals
```

- **Baseline selection**: Lowest return period storm (or explicit)
- **Storm linking**: Via `storm_event_id` (priority) or `storm_event_name` (fallback)
- **Flat list metrics**: Entity + storm + metric per row
- **Additive totals**: Peak flow, runoff volume summed per storm

See [Storm Sensitivity Comparison](docs/storm-sensitivity-comparison.md) for details.

---

## Rainfall Layer

The rainfall layer provides structured IDF curve data for storm event generation.

```text
IDF Curve Data → Intensity/Depth Lookup → StormEvent Generation → Calculators
```

### Current Implementation

- **IDF data models**: IDFPoint, IDFCurve
- **Lookup**: Intensity and depth with optional duration interpolation
- **Storm generation**: Create domain StormEvent objects from IDF data
- **No extrapolation**: Lookups outside data range fail clearly
- **Serialization**: Full round-trip support

### Rainfall Principles

1. **Deterministic** — Same inputs always produce same outputs
2. **No external calls** — Static data, no live API dependencies
3. **Explicit interpolation** — Duration interpolation enabled by default, return period interpolation not implemented
4. **No silent extrapolation** — Out-of-range lookups fail with clear errors
5. **Units are explicit** — Field names include units (duration_minutes, rainfall_intensity_in_per_hr)

See [IDF Curves](docs/idf-curves.md) for details.

---

## Design Criteria Layer

The design criteria layer provides structured storage for jurisdiction-specific design standards.

```text
Design Criteria → Coefficient/CN Lookup → Storm Definitions → StormEvent Generation
```

### Current Implementation

- **RunoffCoefficientTable**: Land use to coefficient lookup (min/max/typical)
- **CurveNumberTable**: Nested lookup by land use and soil group (A/B/C/D)
- **DesignStormDefinition**: Named design storms with return period and duration
- **DesignCriteria**: Complete criteria set for a jurisdiction/project
- **DesignCriteriaLibrary**: Registry for managing multiple criteria sets
- **Validation**: Coefficients (0-1), CNs (0-100), soil groups (A/B/C/D)
- **Serialization**: Full round-trip support

### Design Criteria Principles

1. **Static reference data** — Plain dataclasses, not entities
2. **Deterministic lookup** — No external API calls
3. **Explicit validation** — Invalid data fails immediately
4. **IDF integration** — Design storms derive intensity/depth from IDF curves
5. **Registry pattern** — Multiple criteria sets managed in libraries

See [Design Criteria Libraries](docs/design-criteria-libraries.md) for details.

---

## Infrastructure Modeling Layer

The infrastructure layer provides data models for drainage infrastructure elements.

```text
InfrastructureNetwork
 ├── InfrastructureNode[]
 │    ├── id, name, node_type
 │    └── elevations (invert, rim, ground)
 │
 └── NetworkElement[]
      ├── Pipe (circular, box, arch, elliptical)
      ├── Inlet (grate, curb_opening, combination, slotted)
      ├── Culvert (with inlet/outlet control)
      ├── OpenChannel (rectangular, trapezoidal, triangular)
      ├── DetentionFacility (stage-storage curves)
      ├── OutletStructure (orifice, weir, riser, combined)
      └── Swale (grass, bioswale, rock, concrete)
```

### Current Implementation

- **InfrastructureNode**: Junction points (manholes, junctions, outfalls)
- **Pipe**: Conduits with shape-specific dimensions (circular: diameter; box/arch: width+height)
- **Inlet**: Surface collection with clogging factors
- **Culvert**: Road crossings with inlet type and headwater limits
- **OpenChannel**: Open conveyances with shape-specific geometry
- **DetentionFacility**: Storage ponds with stage-storage interpolation
- **OutletStructure**: Discharge control with orifice/weir properties
- **Swale**: Vegetated channels with infiltration support
- **InfrastructureNetwork**: Connected networks with validation
- **InfrastructureSchedule**: Tabular output for reporting

### Infrastructure Principles

1. **Plain dataclasses** — Static models, not BaseEntity
2. **Explicit dimensions** — Separate fields for different shapes
3. **Network validation** — Connectivity checks, disconnected node warnings
4. **Serialization** — Full round-trip support for all element types
5. **Unit conversions** — Properties convert inches to feet

See [Infrastructure Modeling](docs/infrastructure-modeling.md) for details.

---

## Infrastructure Sizing Layer

The infrastructure sizing layer provides simplified capacity checks for drainage elements.

```text
Infrastructure Element + Design Flow → Manning's Equation → InfrastructureCheckResult
```

### Current Implementation

- **Manning's equation**: Q = (1.49/n) * A * R^(2/3) * S^(1/2)
- **Pipe capacity**: Full-flow capacity using circular/box geometry
- **Culvert barrel capacity**: Not inlet/outlet controlled
- **Channel capacity**: Uniform flow at specified depth
- **Swale capacity**: Trapezoidal section, conveyance only
- **Detention storage**: Volume comparison, no routing
- **Structured results**: InfrastructureCheckResult with warnings and assumptions

### Sizing Principles

1. **Screening-level only** — Not detailed hydraulic analysis
2. **Design flow is explicit** — Must be passed as parameter
3. **No mutations** — Infrastructure objects are not modified
4. **Warnings and assumptions** — Transparent about limitations
5. **Structured output** — Consistent InfrastructureCheckResult format

See [Infrastructure Sizing](docs/infrastructure-sizing.md) for details.

---

## Reporting Layer

The reporting layer generates engineering documents from domain objects.

```text
Domain Objects + Comparison Results → Report Builder → Markdown/PDF
```

### Current Implementation

- **Output formats**: Markdown, PDF (via WeasyPrint)
- **Report types**: Project summary, scenario comparison, calculation appendix
- **Components**: ReportSection, ReportTable, formatters
- **Deterministic**: Same input produces identical output
- **Testable**: Tables render to plain strings

### Report Templates

Templates define report structure, section ordering, and formatting intent:

```text
Project / Scenario / Comparison Data
        ↓
Report Template
        ↓
Template Builder
        ↓
Structured Report
        ↓
Markdown Renderer
        ↓
PDF Export
```

Template features:
- Reusable report definitions
- Configurable sections and appendices
- Built-in templates (project_summary, scenario_comparison, infrastructure_summary_report, etc.)
- Infrastructure schedule tables (pipes, inlets, detention)
- Sizing check summaries with warnings and assumptions
- Serializable for sharing and versioning
- Validation before building

### PDF Export Pipeline

```text
Report → HTML Templates → CSS Styling → WeasyPrint → PDF
```

PDF export features:
- Professional page layout (letter size, headers/footers)
- All section types render (tables, warnings, references)
- Optional: graceful fallback to Markdown when WeasyPrint unavailable
- Deterministic output where practical

### Reporting Principles

1. **No calculations** — Reporting only formats existing data
2. **Composable** — Sections combine into reports
3. **Format-agnostic** — Report data separates from rendering
4. **Deterministic output** — Reproducible for engineering review
5. **Templates are data** — Templates define structure, not logic

See [Reporting Engine](docs/reporting.md), [Report Templates](docs/report-templates.md), [Infrastructure Reporting](docs/infrastructure-reporting.md), and [PDF Export](docs/pdf-report-export.md) for details.

---

## Key Architectural Principles

1. **Calculation kernels are pure** — No I/O, no state, no UI concerns
2. **Units are explicit** — Never pass bare floats without unit context
3. **Results are auditable** — Every output traces to inputs and method
4. **Scenarios are comparable** — Same project, different assumptions
5. **Persistence is pluggable** — Local files, SQLite, cloud storage
6. **UI is separate** — Web, desktop, CLI share the same engine
7. **Jurisdiction rules are data** — Profiles, not hardcoded logic
