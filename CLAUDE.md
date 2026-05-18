# Project Instructions

## Overview

Civil Toolbox — drainage analysis workstation for civil engineers. Pure Python calculation kernels with scenario comparison and engineering report generation.

## Code Style

- Python: PEP 8, type hints, dataclasses for data models
- Tests: pytest with comprehensive coverage
- No side effects in calculation kernels

## Architecture

### Domain Layer (`civil_toolbox/domain/`)

Project-centered model for drainage analysis:

```text
Project
 ├── Scenario[]
 │    ├── DrainageArea[]
 │    ├── StormEvent[]
 │    ├── FlowPath[]
 │    ├── InfrastructureElement[]
 │    └── CalculationResult[]
 └── Reports[]
```

### Calculation Kernels (`civil_toolbox/calculators/`)

Pure calculation functions — no I/O, no state:

- `rational_method.py` — Rational Method (Q = CiA)
- `tr55.py` — TR-55 runoff calculations
- `time_of_concentration.py` — Tc methods (Kirpich, FAA, etc.)
- `kinematic_wave.py` — Kinematic wave travel time

### Adapters Layer (`civil_toolbox/adapters/`)

Bridge between domain models and calculation kernels:

- Domain → calculator input extraction
- Calculator output → CalculationResult construction
- Scenario-level orchestration

### Comparison Layer (`civil_toolbox/comparison/`)

Scenario-to-scenario analysis:

- **Match strategies**: auto, id, name, explicit
- **Metrics**: peak_flow_cfs, runoff_depth_in, runoff_volume_cuft, time_of_concentration_min
- **Aggregation**: Additive metrics sum at scenario level
- **Missing data**: Status flags (missing_baseline, missing_comparison)

### Reporting Layer (`civil_toolbox/reporting/`)

Engineering document generation:

- **Output**: Markdown (PDF planned)
- **Report types**: Project summary, scenario comparison, calculation appendix
- **Principle**: No calculations — only formats existing data

### Persistence Layer (`civil_toolbox/persistence/`)

Project storage:

- **Format**: JSON with `.ctbx.json` extension
- **Schema versioning**: Migration support via `schema_version`
- **Validation**: Envelope validation before domain reconstruction

## Key Principles

1. **Calculation kernels are pure** — No I/O, no state, no UI concerns
2. **Units are explicit** — Never pass bare floats without unit context
3. **Results are auditable** — Every output traces to inputs and method
4. **Scenarios are comparable** — Same project, different assumptions
5. **Reporting does not calculate** — Only formats existing data

## Development Guidelines

- Run `pytest` from repository root
- Use absolute paths when working alongside other repositories
- See `docs/` for detailed documentation on each layer

## Testing

```bash
pytest                           # Run all tests
pytest tests/comparison/         # Comparison layer only
pytest tests/reporting/          # Reporting layer only
pytest -v --tb=short             # Verbose with short tracebacks
```

## Documentation

- `docs/comparison.md` — Scenario comparison API
- `docs/reporting.md` — Reporting engine API
- `docs/project-file-format.md` — Persistence format
- `ARCHITECTURE.md` — Full architecture overview
