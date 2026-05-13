# Civil Toolbox

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A comprehensive civil engineering toolkit for solving **overland drainage flow problems**. This toolbox provides industry-standard computational methods for stormwater management, hydraulic analysis, and drainage design.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Methods & Calculations](#methods--calculations)
  - [Rational Method](#rational-method)
  - [TR-55 Method](#tr-55-method)
  - [Kinematic Wave (Sheet Flow)](#kinematic-wave-sheet-flow)
  - [Time of Concentration (Tc)](#time-of-concentration-tc)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Civil Toolbox addresses the core calculations required for overland drainage flow analysis. Whether you're designing stormwater management systems, conducting flood risk assessments, or sizing drainage infrastructure, this toolkit provides reliable implementations of proven hydrological methods.

### Who Is This For?

- **Civil Engineers** designing drainage systems and stormwater infrastructure
- **Hydrologists** performing watershed analysis and runoff calculations
- **Environmental Consultants** conducting stormwater impact assessments
- **Students** learning hydrology and hydraulic engineering principles
- **Municipalities** evaluating drainage capacity and flood mitigation

---

## Features

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
pip install -r requirements.txt
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

Technical Release 55 (TR-55) is an NRCS (Natural Resources Conservation Service) methodology for estimating runoff from urban and developing watersheds. It uses the Curve Number (CN) method to estimate runoff volume.

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

| Cover Description | Hydrologic Soil Group |
|-------------------|---------------------|
| | A | B | C | D |
| Impervious surfaces | 98 | 98 | 98 | 98 |
| Open space (good condition) | 39 | 61 | 74 | 80 |
| Residential (1/4 acre) | 54 | 70 | 80 | 85 |
| Commercial | 89 | 92 | 94 | 95 |
| Woods (good condition) | 30 | 55 | 70 | 77 |

---

### Kinematic Wave (Sheet Flow)

The Kinematic Wave equation calculates travel time for sheet flow, which is the thin layer of water flowing over land surfaces during the initial phase of runoff.

**Formula:**
```
Tt = (0.007 × (n × L)^0.8) / (P2^0.5 × S^0.4)
```

| Parameter | Description | Units |
|-----------|-------------|-------|
| Tt | Travel time | hours |
| n | Manning's roughness coefficient | dimensionless |
| L | Flow length | feet (max 100 ft) |
| P2 | 2-year, 24-hour rainfall | inches |
| S | Slope | ft/ft |

**Manning's n for Sheet Flow:**

| Surface | n Value |
|---------|---------|
| Smooth asphalt | 0.011 |
| Smooth concrete | 0.012 |
| Fallow (no residue) | 0.05 |
| Short grass prairie | 0.15 |
| Dense grass | 0.24 |
| Woods (light underbrush) | 0.40 |
| Woods (dense underbrush) | 0.80 |

---

### Time of Concentration (Tc)

Time of Concentration is the time required for runoff to travel from the hydraulically most distant point in the watershed to the outlet. Civil Toolbox provides three methods:

#### Kirpich Formula

Best for rural and agricultural watersheds with well-defined channels.

```
Tc = 0.0078 × L^0.77 × S^(-0.385)
```

| Parameter | Description | Units |
|-----------|-------------|-------|
| Tc | Time of concentration | minutes |
| L | Channel length | feet |
| S | Average watershed slope | ft/ft |

#### Kerby Equation

Designed for overland sheet flow on small watersheds (< 10 acres).

```
Tc = 0.83 × (L × n)^0.467 × S^(-0.235)
```

| Parameter | Description | Units |
|-----------|-------------|-------|
| Tc | Time of concentration | minutes |
| L | Flow length | feet |
| n | Retardance coefficient | dimensionless |
| S | Slope | ft/ft |

**Kerby Retardance Coefficients:**

| Surface | n |
|---------|---|
| Smooth pavement | 0.02 |
| Poor grass/cultivated | 0.30 |
| Average grass | 0.40 |
| Dense grass | 0.80 |

#### NRCS Lag Method

Uses watershed lag time to estimate Tc. Suitable for urban and suburban watersheds.

```
Tc = L / 0.6

Where L (Lag) = (l^0.8 × (S + 1)^0.7) / (1900 × Y^0.5)
```

| Parameter | Description | Units |
|-----------|-------------|-------|
| L | Lag time | hours |
| l | Hydraulic length | feet |
| S | (1000/CN) - 10 | inches |
| Y | Average watershed slope | percent |

---

## Usage Examples

### Example 1: Storm Sewer Design

Calculate peak runoff for a 15-acre commercial development:

```python
from civil_toolbox import RationalMethod, TimeOfConcentration

# Calculate Time of Concentration
tc = TimeOfConcentration.kirpich(
    length=2500,      # feet
    slope=0.02        # ft/ft
)
print(f"Time of Concentration: {tc:.1f} minutes")

# Get rainfall intensity from IDF curve for your location
# Assuming i = 5.2 in/hr for Tc duration

# Calculate Peak Runoff
Q = RationalMethod.calculate(
    C=0.85,           # Commercial development
    i=5.2,            # in/hr
    A=15              # acres
)
print(f"Peak Runoff: {Q:.1f} cfs")
```

### Example 2: TR-55 Detention Pond Sizing

Estimate runoff volume for a 50-acre mixed-use development:

```python
from civil_toolbox import TR55

# Composite Curve Number calculation
areas = [
    (20, 98),    # 20 acres impervious, CN=98
    (15, 74),    # 15 acres open space, CN=74
    (15, 80)     # 15 acres residential, CN=80
]

cn_composite = TR55.composite_cn(areas)
print(f"Composite CN: {cn_composite:.0f}")

# Calculate runoff depth for 5-inch storm
runoff_depth = TR55.runoff_depth(
    precipitation=5.0,
    curve_number=cn_composite
)
print(f"Runoff Depth: {runoff_depth:.2f} inches")

# Calculate runoff volume
volume = TR55.runoff_volume(
    runoff_depth=runoff_depth,
    area_acres=50
)
print(f"Runoff Volume: {volume:,.0f} cubic feet")
```

### Example 3: Sheet Flow Analysis

Calculate travel time across a parking lot:

```python
from civil_toolbox import KinematicWave

tt = KinematicWave.travel_time(
    n=0.011,          # Smooth asphalt
    length=100,       # feet (max for sheet flow)
    P2=3.5,           # 2-year, 24-hour rainfall (inches)
    slope=0.01        # ft/ft
)
print(f"Sheet Flow Travel Time: {tt:.2f} hours ({tt*60:.1f} minutes)")
```

---

## API Reference

### RationalMethod

| Method | Parameters | Returns |
|--------|------------|---------|
| `calculate(C, i, A)` | C: coefficient, i: intensity (in/hr), A: area (acres) | Q (cfs) |
| `get_coefficient(land_use)` | land_use: string descriptor | C value |

### TR55

| Method | Parameters | Returns |
|--------|------------|---------|
| `runoff_depth(precipitation, curve_number)` | P (in), CN | Q (in) |
| `runoff_volume(runoff_depth, area_acres)` | Q (in), A (acres) | Volume (cf) |
| `composite_cn(area_cn_pairs)` | List of (area, CN) tuples | Weighted CN |
| `get_cn(cover, soil_group)` | cover: string, soil_group: A/B/C/D | CN value |

### TimeOfConcentration

| Method | Parameters | Returns |
|--------|------------|---------|
| `kirpich(length, slope)` | L (ft), S (ft/ft) | Tc (min) |
| `kerby(length, n, slope)` | L (ft), n, S (ft/ft) | Tc (min) |
| `nrcs_lag(length, cn, slope)` | L (ft), CN, Y (%) | Tc (min) |

### KinematicWave

| Method | Parameters | Returns |
|--------|------------|---------|
| `travel_time(n, length, P2, slope)` | n, L (ft), P2 (in), S (ft/ft) | Tt (hr) |

---

## Project Roadmap

- [ ] Core calculation modules
- [ ] Input validation and unit conversions
- [ ] IDF curve integration
- [ ] Hydrograph generation (SCS Unit Hydrograph)
- [ ] Channel flow calculations (Manning's equation)
- [ ] GUI/Web interface
- [ ] Export to engineering report formats
- [ ] Integration with GIS data

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/HanzoRazer/civil-toolbox.git
cd civil-toolbox
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

---

## References

- NRCS TR-55: Urban Hydrology for Small Watersheds
- FHWA HEC-22: Urban Drainage Design Manual
- ASCE Manual of Practice No. 77
- Chow, V.T., Maidment, D.R., & Mays, L.W. (1988). Applied Hydrology

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Natural Resources Conservation Service (NRCS) for TR-55 methodology
- Federal Highway Administration (FHWA) for hydraulic engineering guidelines
- The civil engineering community for continued development of these methods

---

<p align="center">
  <b>Civil Toolbox</b> - Engineering Solutions for Drainage Design
</p>
