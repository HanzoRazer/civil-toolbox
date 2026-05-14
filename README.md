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
from civil_toolbox import RationalMethod, TimeOfConcentration

# Calculate peak runoff using Rational Method
Q = RationalMethod.calculate(
    C=0.65,           # Runoff coefficient
    i=4.5,            # Rainfall intensity (in/hr)
    A=25              # Drainage area (acres)
)
print(f"Peak Runoff: {Q:.2f} cfs")
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
from civil_toolbox import RationalMethod, TimeOfConcentration

# Calculate Time of Concentration
tc = TimeOfConcentration.kirpich(
    length=2500,      # feet
    slope=0.02        # ft/ft
)
print(f"Time of Concentration: {tc:.1f} minutes")

# Calculate Peak Runoff
Q = RationalMethod.calculate(
    C=0.85,           # Commercial development
    i=5.2,            # in/hr
    A=15              # acres
)
print(f"Peak Runoff: {Q:.1f} cfs")
```

### Example 2: TR-55 Detention Pond Sizing

```python
from civil_toolbox import TR55

# Composite Curve Number calculation
areas = [
    (20, 98),    # 20 acres impervious, CN=98
    (15, 74),    # 15 acres open space, CN=74
    (15, 80)     # 15 acres residential, CN=80
]

cn_composite = TR55.composite_cn(areas)
runoff_depth = TR55.runoff_depth(precipitation=5.0, curve_number=cn_composite)
volume = TR55.runoff_volume(runoff_depth=runoff_depth, area_acres=50)

print(f"Composite CN: {cn_composite:.0f}")
print(f"Runoff Volume: {volume:,.0f} cubic feet")
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

- Scenario comparison (existing vs proposed, with/without detention)
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
