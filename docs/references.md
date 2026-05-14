# Engineering References

Authoritative sources for methods implemented in Civil Toolbox.

---

## Hydrology

### NRCS TR-55

**Full Citation:**
USDA Natural Resources Conservation Service. (1986). *Urban Hydrology for Small Watersheds*. Technical Release 55, 2nd Edition.

**Covers:**
- Curve Number runoff estimation
- Time of concentration methods
- Graphical peak discharge method
- Tabular hydrograph method

**URL:** https://www.nrcs.usda.gov/wps/portal/nrcs/detailfull/national/water/?cid=stelprdb1042901

---

### NRCS National Engineering Handbook

**Full Citation:**
USDA Natural Resources Conservation Service. *National Engineering Handbook*, Part 630: Hydrology.

**Covers:**
- Rainfall-runoff relationships
- Hydrograph development
- Flood routing
- Watershed yield

**URL:** https://www.nrcs.usda.gov/wps/portal/nrcs/detailfull/national/water/manage/hydrology/?cid=stelprdb1043063

---

### Applied Hydrology

**Full Citation:**
Chow, V.T., Maidment, D.R., & Mays, L.W. (1988). *Applied Hydrology*. McGraw-Hill.

**Covers:**
- Precipitation analysis
- Hydrologic processes
- Runoff analysis
- Flood routing
- Statistical hydrology

---

## Hydraulics

### Open Channel Hydraulics

**Full Citation:**
Chow, V.T. (1959). *Open-Channel Hydraulics*. McGraw-Hill.

**Covers:**
- Manning equation
- Uniform flow
- Gradually varied flow
- Rapidly varied flow
- Unsteady flow

---

### FHWA HEC-22

**Full Citation:**
Federal Highway Administration. (2009). *Urban Drainage Design Manual*. Hydraulic Engineering Circular No. 22, 3rd Edition. FHWA-NHI-10-009.

**Covers:**
- Storm drain design
- Inlet design
- Pavement drainage
- Pump stations

**URL:** https://www.fhwa.dot.gov/engineering/hydraulics/pubs/10009/10009.pdf

---

### FHWA HDS-5

**Full Citation:**
Federal Highway Administration. (2012). *Hydraulic Design of Highway Culverts*. Hydraulic Design Series No. 5, 3rd Edition. FHWA-HIF-12-026.

**Covers:**
- Culvert hydraulics
- Inlet control
- Outlet control
- Improved inlets

**URL:** https://www.fhwa.dot.gov/engineering/hydraulics/pubs/12026/hif12026.pdf

---

## Time of Concentration

### Kirpich Formula

**Full Citation:**
Kirpich, Z.P. (1940). Time of concentration of small agricultural watersheds. *Civil Engineering*, 10(6), 362.

**Equation:**
```
Tc = 0.0078 × L^0.77 × S^(-0.385)
```

**Applicability:**
- Rural watersheds
- Well-defined channels
- Length < 10,000 ft

---

### Kerby Equation

**Full Citation:**
Kerby, W.S. (1959). Time of concentration for overland flow. *Civil Engineering*, 29(3), 174.

**Equation:**
```
Tc = 0.83 × (L × n)^0.467 × S^(-0.235)
```

**Applicability:**
- Overland sheet flow
- Drainage areas < 10 acres
- Flow lengths < 1,200 ft

---

### Kinematic Wave

**Full Citation:**
As documented in NRCS TR-55, Appendix F.

**Equation:**
```
Tt = (0.007 × (n × L)^0.8) / (P2^0.5 × S^0.4)
```

**Applicability:**
- Sheet flow segment
- Flow length ≤ 100 ft

---

## Standards and Manuals

### ASCE Manual of Practice No. 77

**Full Citation:**
American Society of Civil Engineers. (2017). *Design and Construction of Urban Stormwater Management Systems*. ASCE Manuals and Reports on Engineering Practice No. 77.

**Covers:**
- Storm sewer design
- Detention design
- Water quality
- Construction practices

---

### FEMA Guidelines

**Full Citation:**
Federal Emergency Management Agency. *Guidelines and Specifications for Flood Hazard Mapping Partners*.

**Covers:**
- Floodplain mapping standards
- Hydraulic modeling requirements
- LOMR/LOMA procedures

**URL:** https://www.fema.gov/flood-maps/guidance-partners/guidelines-standards

---

## Jurisdiction-Specific

### Harris County Flood Control District

**Full Citation:**
Harris County Flood Control District. *Policy, Criteria and Procedure Manual for Approval and Acceptance of Infrastructure*.

**URL:** https://www.hcfcd.org/

---

### TxDOT Hydraulic Design Manual

**Full Citation:**
Texas Department of Transportation. *Hydraulic Design Manual*.

**URL:** https://onlinemanuals.txdot.gov/txdotmanuals/hyd/index.htm

---

## Adding References

When adding a new engineering method, include:

1. **Short name** — For code references (e.g., `TR55_REF`)
2. **Full citation** — Author, year, title, publisher
3. **Section** — Specific chapter or page range
4. **URL** — If publicly available

Example in code:

```python
TR55_REF = Reference(
    short_name="TR-55",
    full_citation="USDA NRCS. (1986). Urban Hydrology for Small Watersheds. Technical Release 55.",
    section="Chapter 2",
    url="https://www.nrcs.usda.gov/..."
)
```
