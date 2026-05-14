# Roadmap

Civil Toolbox development is organized into phases, progressing from foundational calculators to a full drainage analysis workstation.

---

## Status Labels

| Label | Meaning |
|-------|---------|
| **Stable** | Production-ready, tested, documented |
| **In Progress** | Active development |
| **Planned** | Committed to roadmap, not yet started |
| **Proposed** | Under consideration |
| **Experimental** | Available but not production-ready |
| **Deferred** | Postponed indefinitely |

---

## Phase 1 — Foundation

**Status: In Progress**

Establish the core calculation engine and project architecture.

### Objectives

- Convert calculators into reusable kernel modules
- Implement CalcResult contract for auditable outputs
- Establish project persistence foundation
- Define jurisdiction profile system
- Build report generation pipeline

### Deliverables

| Deliverable | Status |
|-------------|--------|
| Rational Method calculator | Stable |
| TR-55 Curve Number method | Stable |
| Time of Concentration methods | Stable |
| CalcResult pattern | In Progress |
| Project data model | Planned |
| Basic report export | Planned |

### Current Focus

- MVP: No-Rise Certification workflow
- Rational + normal depth + petition document generation
- Harris County Flood Control District jurisdiction profile

---

## Phase 2 — Planning Workflows

**Status: Planned**

Enable scenario-based analysis and design comparison.

### Objectives

- Implement scenario management
- Build design criteria libraries
- Create calculation audit trails
- Add review and approval workflows

### Deliverables

| Deliverable | Status |
|-------------|--------|
| Scenario comparison | Planned |
| Existing vs proposed analysis | Planned |
| With/without detention comparison | Planned |
| Design criteria libraries | Planned |
| Calculation history | Planned |
| Review workflows | Proposed |

### Use Cases

- Compare pre-development and post-development runoff
- Evaluate detention vs no detention alternatives
- Document design iteration history
- Support multi-reviewer approval

---

## Phase 3 — Infrastructure Modeling

**Status: Planned**

Add first-class infrastructure objects with hydraulic analysis.

### Objectives

- Model storm sewer networks
- Implement detention pond sizing
- Add culvert analysis
- Support hydraulic grading

### Deliverables

| Deliverable | Status |
|-------------|--------|
| Pipe network model | Planned |
| Manning equation workflows | Planned |
| Detention pond sizing | Planned |
| Stage-storage-discharge | Planned |
| Culvert hydraulics | Planned |
| Inlet capacity | Planned |
| Infrastructure schedules | Planned |

### Analysis Capabilities

- Pipe capacity and surcharge analysis
- Pond routing and outlet sizing
- Inlet spread calculations
- Energy grade line computation

---

## Phase 4 — Spatial Analysis

**Status: Proposed**

Integrate GIS workflows and map-based analysis.

### Objectives

- Support drainage area delineation
- Enable flow path tracing
- Integrate terrain data
- Provide map-based visualization

### Deliverables

| Deliverable | Status |
|-------------|--------|
| GeoJSON import/export | Proposed |
| Drainage area delineation | Proposed |
| Flow path tracing | Proposed |
| Terrain integration | Proposed |
| Contour visualization | Proposed |
| Aerial imagery overlays | Proposed |

### Integration Points

- USGS elevation data
- FEMA NFHL flood zones
- Municipal parcel data
- Aerial imagery services

---

## Phase 5 — Reporting and Review

**Status: Proposed**

Generate comprehensive engineering deliverables.

### Objectives

- Produce jurisdiction-ready reports
- Support multiple output formats
- Enable collaborative review
- Maintain version history

### Deliverables

| Deliverable | Status |
|-------------|--------|
| Drainage report generation | Proposed |
| Detention report generation | Proposed |
| Calculation appendices | Proposed |
| Compliance summaries | Proposed |
| PDF/Word export | Proposed |
| Collaborative review | Proposed |

### Report Types

- Drainage analysis report
- Detention facility report
- No-rise certification
- LOMA/LOMR-F petition package
- HCFCD waiver application

---

## Jurisdiction Support

### Current

| Jurisdiction | Status |
|--------------|--------|
| Generic (TR-55/Rational) | In Progress |
| Harris County FCD | Planned |

### Future

| Jurisdiction | Status |
|--------------|--------|
| TxDOT | Proposed |
| City of Houston | Proposed |
| Fort Bend County | Proposed |

---

## FEMA Integration

### Phase 1 — NFHL Data

| Feature | Status |
|---------|--------|
| Flood zone lookup | Planned |
| BFE retrieval | Planned |
| FIRM panel metadata | Planned |

### Phase 2 — Petition Workflows

| Feature | Status |
|---------|--------|
| No-Rise certification | In Progress |
| LOMA preparation | Planned |
| LOMR-F preparation | Planned |
| CLOMR support | Proposed |

---

## Non-Goals

The following are explicitly **not** planned:

- **Full HEC-RAS replacement** — Civil Toolbox complements, not replaces, HEC-RAS for complex modeling
- **2D flood modeling** — Focus remains on planning-level 1D analysis
- **Real-time monitoring** — Not a SCADA or telemetry system
- **Construction management** — Design tool, not construction administration
- **Full GIS platform** — Spatial features support drainage analysis, not general GIS

---

## Contributing to the Roadmap

Roadmap items come from:

- User feedback
- Contributor proposals
- Maintainer planning

To propose a roadmap item:

1. Open a GitHub Issue using the **Feature Request** template
2. Describe the problem and proposed solution
3. Explain how it fits the workstation vision
4. Indicate which phase it belongs to

Maintainers will review and assign status labels.

---

## Version Milestones

| Version | Phase | Target |
|---------|-------|--------|
| 0.1.x | Phase 1 foundation | Q2 2026 |
| 0.2.x | Phase 1 complete | Q3 2026 |
| 0.3.x | Phase 2 scenarios | Q4 2026 |
| 0.4.x | Phase 3 infrastructure | 2027 |
| 0.5.x | Phase 4 spatial | TBD |
| 1.0.0 | Production release | TBD |

Dates are estimates and subject to change based on contributor capacity and user priorities.
