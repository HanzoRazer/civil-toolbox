# Culvert Analysis

First-pass culvert hydraulic analysis. Given a `Culvert` and a design flow, it
estimates the **controlling headwater** by comparing a simplified inlet-control
headwater against a simplified outlet-control headwater, reusing the barrel
capacity screening from the infrastructure sizing layer.

This is **screening-level** analysis — a transparent, auditable first pass — not
a substitute for FHWA HY-8 or HEC-RAS.

## Quick start

```python
from civil_toolbox.culverts import analyze_culvert
from civil_toolbox.culverts.examples import create_single_circular_culvert

culvert = create_single_circular_culvert()
result = analyze_culvert(culvert, design_flow_cfs=50.0)

print(result.governing_control)        # 'inlet' or 'outlet'
print(result.headwater_depth_ft)       # governing headwater depth above inlet invert
print(result.headwater_elevation_ft)   # absolute elevation (if inlet invert known)
print(result.inlet_control_status)     # 'passes' | 'exceeds' | 'not_evaluated' | 'unknown'
```

## How it works

The analysis evaluates two controls and takes the one that requires the greater
headwater — the standard FHWA HDS-5 approach.

### Barrel capacity (reused)

Full-barrel Manning capacity is **reused** from
`infrastructure_sizing.culverts.estimate_culvert_barrel_capacity_cfs` — it is not
reimplemented here. If the barrel capacity cannot be computed (e.g. zero slope),
a `BARREL_CAPACITY_UNAVAILABLE` warning is recorded and analysis continues.

### Inlet control (submerged orifice approximation)

When the inlet is submerged it behaves like an orifice:

```text
Q = Cd · A · sqrt(2 · g · h)   →   HW = (Q / (Cd · A))² / (2g) + D/2
```

with `Cd = 0.6`, `A` the full-barrel area, and `D` the barrel rise. Valid in the
submerged regime (HW/D ≥ ~1.2); below that the inlet acts as a weir and an
`UNSUBMERGED_INLET` info warning flags that the estimate is approximate.

### Outlet control (full-flow energy)

```text
HW = ho + H_L − ΔZ
H_L = (Ke + Kexit) · V²/2g + Sf · L
Sf  = (n · V / (1.49 · R^(2/3)))²
```

- `ho` — outlet hydraulic grade above the outlet invert. Tailwater profiles are
  out of scope, so `ho = max(tailwater, D)` (HGL assumed at the crown when
  tailwater is unknown).
- `Ke` — entrance loss coefficient by inlet type (FHWA HDS-5), or an explicit
  `culvert.inlet_coefficient` override.
- `ΔZ` — invert drop from inlet to outlet (from inverts, or slope × length).

### Governing headwater

```text
governing_headwater = max(inlet_control_HW, outlet_control_HW)
```

## Entrance loss coefficients (Ke)

| Inlet type | Ke  |
|------------|-----|
| projecting | 0.9 |
| mitered    | 0.7 |
| headwall   | 0.5 |
| wingwall   | 0.5 |
| beveled    | 0.2 |
| (default)  | 0.5 |

A non-null `culvert.inlet_coefficient` overrides the table.

## Result model

`CulvertAnalysisResult` is a **standalone** dataclass (mirroring the hydraulics
foundation's `HydraulicProfileResult`), with `to_dict`/`from_dict`. References
and assumptions are `list[str]`. The model is deliberately shaped so a future
adapter can map it onto the domain `CalculationResult` audit type without
rework.

Key fields: `barrel_capacity_cfs`, `headwater_depth_ft`, `headwater_elevation_ft`,
`inlet_control_headwater_ft`, `outlet_control_headwater_ft`, `governing_control`,
`inlet_control_status`, `outlet_control_status`, `barrel_velocity_fps`,
`warnings`, `assumptions`, `references`.

## Worked benchmark

36-inch circular barrel, Q = 50 cfs, L = 100 ft, n = 0.024, inverts 101/100
(ΔZ = 1.0 ft), projecting inlet (Ke = 0.9), tailwater unknown (ho = D = 3.0):

| Quantity | Value |
|----------|-------|
| Inlet-control HW | 3.658 ft |
| Outlet-control HW | 5.381 ft |
| Governing | outlet, 5.381 ft |

These values are asserted in the test suite as hand-computed benchmarks.

## Limitations

Out of scope for this foundation (later series):

- FHWA HDS-5 full chart-coefficient implementation
- Tailwater rating curves / tailwater profiles
- Multiple-barrel interaction
- Road overtopping
- Sediment blockage, debris accumulation, fish passage
- HGL integration

For detailed design, use FHWA HY-8 or HEC-RAS.

## References

- FHWA HDS-5 (2012), *Hydraulic Design of Highway Culverts*, 3rd ed. — inlet/outlet control
- Chow (1959), *Open Channel Hydraulics* — Manning's equation (barrel capacity)
