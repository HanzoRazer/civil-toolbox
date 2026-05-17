# Civil Toolbox

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Drainage Analysis & Infrastructure Planning Workstation

Civil Toolbox is evolving from a collection of hydrologic calculators into a **project-centered workstation** for drainage analysis, stormwater infrastructure design, and infrastructure planning.

The platform is intended to support the complete engineering workflow:

- Site drainage evaluation
- Watershed characterization
- Hydrologic and hydraulic analysis
- Stormwater infrastructure sizing
- Scenario comparison
- Design documentation
- Engineering report generation

---

## Vision

Civil Toolbox aims to become a modern civil engineering workstation that combines:

- Hydrologic calculators
- Infrastructure modeling
- GIS-linked workflows
- Scenario planning
- Engineering documentation
- Project management

The long-term goal is to provide engineers, designers, municipalities, and developers with a unified environment for stormwater and drainage planning.

---

## Core Philosophy

### From Calculators to Workflows

Traditional engineering calculators are isolated and disposable. Civil Toolbox is being designed so that:

- Calculations belong to **projects**
- Projects contain **drainage systems**
- Systems contain **infrastructure**
- Infrastructure participates in **scenarios**
- Scenarios produce **reports and decisions**

This architecture allows engineers to preserve assumptions, compare alternatives, and maintain traceability throughout the design process.

---

## Who Is This For?

- **Civil Engineers** designing drainage systems and stormwater infrastructure
- **Hydrologists** performing watershed analysis and runoff calculations
- **Environmental Consultants** conducting stormwater impact assessments
- **Students** learning hydrology and hydraulic engineering principles
- **Municipalities** evaluating drainage capacity and flood mitigation

---

## Current Capabilities

| Method | Description | Use Case |
|--------|-------------|----------|
| **Rational Method** | Peak runoff calculation for small watersheds | Storm sewer design, inlet sizing |
| **TR-55** | NRCS urban hydrology for runoff estimation | Detention pond design, SWM facilities |
| **Kinematic Wave** | Sheet flow travel time analysis | Overland flow modeling |
| **Kirpich Formula** | Time of concentration for rural areas | Agricultural drainage |
| **Kerby Equation** | Tc for overland sheet flow | Small watershed analysis |
| **NRCS Lag Method** | Tc using watershed lag time | Urban/suburban watersheds |

---

## Installation

### From Source

```bash
git clone https://github.com/HanzoRazer/civil-toolbox.git
cd civil-toolbox
python -m venv .venv
.venv\Scripts\activate        # Windows
# or: source .venv/bin/activate  # Unix
pip install -e ".[dev]"
```

### Quick Start

```python
from civil_toolbox.calculators import RationalMethod, TimeOfConcentration

# Calculate peak runoff using Rational Method
result = RationalMethod.calculate(
    runoff_coefficient=0.65,
    rainfall_intensity_in_per_hr=4.5,
    area_acres=25.0,
)
print(f"Peak Runoff: {result.peak_runoff_cfs:.2f} cfs")

# Calculate time of concentration
tc_result = TimeOfConcentration.kirpich(
    flow_length_ft=5000,
    elevation_diff_ft=100,
)
print(f"Time of Concentration: {tc_result.tc_minutes:.1f} minutes")
```

---

## Methods & Calculations

### Rational Method

The Rational Method estimates peak runoff discharge for small drainage areas (typically < 200 acres). It is the most widely used method for storm sewer and inlet design.

**Formula:**
```
Q = C × i × A
```

| Parameter | Description | Units |
|-----------|-------------|-------|
| Q | Peak runoff rate | cfs (cubic feet per second) |
| C | Runoff coefficient | dimensionless (0.0 - 1.0) |
| i | Rainfall intensity | inches per hour |
| A | Drainage area | acres |

**Runoff Coefficients (C):**

| Land Use | C Value Range |
|----------|---------------|
| Asphalt/Concrete | 0.70 - 0.95 |
| Roofs | 0.75 - 0.95 |
| Lawns (sandy soil) | 0.05 - 0.20 |
| Lawns (clay soil) | 0.15 - 0.35 |
| Parks/Cemeteries | 0.10 - 0.25 |
| Commercial/Downtown | 0.70 - 0.95 |
| Residential (1/2 acre lots) | 0.25 - 0.40 |

---

### TR-55 Method

Technical Release 55 (TR-55) is an NRCS methodology for estimating runoff from urban and developing watersheds using the Curve Number (CN) method.

**Runoff Equation:**
```
Q = (P - Ia)² / (P - Ia + S)

Where:
  S = (1000 / CN) - 10
  Ia = 0.2 × S (Initial abstraction)
```

| Parameter | Description | Units |
|-----------|-------------|-------|
| Q | Runoff depth | inches |
| P | Precipitation | inches |
| CN | Curve Number | dimensionless (0-100) |
| S | Potential maximum retention | inches |
| Ia | Initial abstraction | inches |

**Common Curve Numbers:**

| Cover Description | A | B | C | D |
|-------------------|---|---|---|---|
| Impervious surfaces | 98 | 98 | 98 | 98 |
| Open space (good condition) | 39 | 61 | 74 | 80 |
| Residential (1/4 acre) | 54 | 70 | 80 | 85 |
| Commercial | 89 | 92 | 94 | 95 |
| Woods (good condition) | 30 | 55 | 70 | 77 |

---

### Time of Concentration (Tc)

Time of Concentration is the time required for runoff to travel from the hydraulically most distant point in the watershed to the outlet.

#### Kirpich Formula

Best for rural and agricultural watersheds with well-defined channels.

```
Tc = 0.0078 × L^0.77 × S^(-0.385)
```

#### Kerby Equation

Designed for overland sheet flow on small watersheds (< 10 acres).

```
Tc = 0.83 × (L × n)^0.467 × S^(-0.235)
```

#### NRCS Lag Method

Uses watershed lag time to estimate Tc. Suitable for urban and suburban watersheds.

```
Tc = L / 0.6

Where L (Lag) = (l^0.8 × (S + 1)^0.7) / (1900 × Y^0.5)
```

---

### Kinematic Wave (Sheet Flow)

Calculates travel time for sheet flow over land surfaces.

```
Tt = (0.007 × (n × L)^0.8) / (P2^0.5 × S^0.4)
```

---

## Usage Examples

### Example 1: Storm Sewer Design

```python
from civil_toolbox.calculators import RationalMethod, TimeOfConcentration

# Calculate Time of Concentration (returns MINUTES)
tc_result = TimeOfConcentration.kirpich(
    flow_length_ft=2500,
    elevation_diff_ft=50,
)
print(f"Time of Concentration: {tc_result.tc_minutes:.1f} minutes")

# Calculate Peak Runoff
result = RationalMethod.calculate(
    runoff_coefficient=0.85,
    rainfall_intensity_in_per_hr=5.2,
    area_acres=15.0,
)
print(f"Peak Runoff: {result.peak_runoff_cfs:.1f} cfs")
```

### Example 2: TR-55 Runoff Depth

```python
from civil_toolbox.calculators import TR55

# Calculate weighted curve number for composite area
cn_composite = TR55.weighted_curve_number([
    (98, 20.0),   # CN=98, 20 acres impervious
    (74, 15.0),   # CN=74, 15 acres open space
    (80, 15.0),   # CN=80, 15 acres residential
])
print(f"Composite CN: {cn_composite:.0f}")

# Calculate runoff depth
result = TR55.runoff_depth(
    rainfall_depth_in=5.0,
    curve_number=cn_composite,
)
print(f"Runoff Depth: {result.runoff_depth_in:.2f} inches")
```

### Example 3: Composite Time of Concentration

```python
from civil_toolbox.calculators import TimeOfConcentration, KinematicWave

# Multi-segment flow path: sheet flow + channel flow
# Sheet flow (returns HOURS)
sheet_result = KinematicWave.sheet_flow_time(
    flow_length_ft=100,
    slope_percent=2.0,
    mannings_n=0.15,
    rainfall_2yr_24hr_in=3.5,
)

# Use composite for multiple Tc segments
tc_total = TimeOfConcentration.composite([
    ("kerby", {"flow_length_ft": 200, "slope_percent": 2.0, "retardance_n": 0.40}),
    ("kirpich", {"flow_length_ft": 3000, "elevation_diff_ft": 60}),
])
print(f"Total Tc: {tc_total:.1f} minutes")
```

---

## Product Roadmap

### Phase 1 — Foundation

- Establish project architecture
- Convert calculators into reusable modules
- Implement project persistence
- Project workspace with saved calculations
- Rational Method workflows
- Report export foundation

### Phase 2 — Planning Workflows

- ✅ Scenario comparison (existing vs proposed, with/without detention)
- Design criteria libraries
- Calculation audit trails
- Review workflows

### Phase 3 — Infrastructure Modeling

- Pipe networks and storm sewers
- Detention systems
- Culvert analysis
- Hydraulic grading
- Infrastructure schedules

### Phase 4 — Spatial Analysis

- GIS integration
- Map-based drainage area delineation
- Terrain analysis
- Flow path tracing
- Spatial reporting

---

## Engineering Reliability

Civil Toolbox calculations are designed to:

- Identify governing equations
- Cite engineering references
- Include units explicitly
- Define assumptions clearly
- Support reproducibility
- Include verification tests

Engineering software should never function as a black box.

---

## Governance & Standards

Civil Toolbox is governed by engineering reliability and transparent computation principles.

- [Contributing Guide](CONTRIBUTING.md) — How to contribute code and methods
- [Engineering Standards](ENGINEERING_STANDARDS.md) — Calculation transparency requirements
- [Architecture](ARCHITECTURE.md) — Domain model and system design
- [Roadmap](ROADMAP.md) — Development phases and milestones
- [Security Policy](SECURITY.md) — Reporting vulnerabilities and calculation defects
- [Code of Conduct](CODE_OF_CONDUCT.md) — Community standards

### Additional Documentation

- [Calculation Engine](docs/calculation-engine.md) — Hydrology calculator reference
- [Domain Adapters](docs/adapters.md) — Connect domain entities to calculators
- [Scenario Comparison](docs/comparison.md) — Compare results between scenarios
- [Domain Model](docs/domain-model.md) — Typed entities for drainage analysis
- [Project File Format](docs/project-file-format.md) — Project persistence specification
- [Verification Standards](docs/verification.md) — How calculations are validated
- [Engineering References](docs/references.md) — Authoritative sources
- [Testing Guide](tests/README.md) — Test organization and patterns

---

## Project Persistence

Civil Toolbox project data can be saved and loaded using a transparent JSON-based project file format.

```python
from civil_toolbox.domain import Project
from civil_toolbox.persistence import save_project, load_project

# Create and save a project
project = Project(name="Downtown Drainage Study")
save_project(project, "downtown.ctbx.json")

# Load a project
loaded = load_project("downtown.ctbx.json")
```

Project files use the `.ctbx.json` extension and include schema metadata for future compatibility.

See [Project File Format](docs/project-file-format.md) for details.

---
## Contributing

Contributions are welcome! All contributions should follow repository standards and verification requirements.

### Contributors May:

- Submit bug fixes
- Propose new calculators
- Improve documentation
- Add engineering references
- Contribute test cases

### Development Setup

```bash
git clone https://github.com/HanzoRazer/civil-toolbox.git
cd civil-toolbox
python -m venv .venv
.venv\Scripts\activate  # Windows
# or: source .venv/bin/activate  # Unix
pip install -e ".[dev]"
pytest
```

### Coding Standards

- Modular architecture
- Deterministic calculations
- Strong typing where possible
- Unit-aware computation
- Test-first engineering logic
- Separation of UI and calculation logic

---

## References

- NRCS TR-55: Urban Hydrology for Small Watersheds
- FHWA HEC-22: Urban Drainage Design Manual
- ASCE Manual of Practice No. 77
- Chow, V.T., Maidment, D.R., & Mays, L.W. (1988). Applied Hydrology

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Future governance updates may introduce additional engineering disclaimers and professional-use guidance.

---

<p align="center">
  <b>Civil Toolbox</b> — Drainage Analysis & Infrastructure Planning Workstation
</p>
