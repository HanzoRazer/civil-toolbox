# Inlet Capacity

First-pass inlet capture and capacity analysis. Given an `Inlet`, a design flow,
and a head, it estimates the interception **capacity**, the **captured** and
**bypass** flow, and the **capture efficiency**, using simplified,
benchmark-tested equations.

This is **screening-level** analysis — not the full FHWA HEC-22 procedure (no
gutter spread, cross-slope, or sag/grade distinction).

## Quick start

```python
from civil_toolbox.inlets import analyze_inlet_capacity
from civil_toolbox.inlets.examples import run_example_grate_inlet_check

result = run_example_grate_inlet_check()
print(result.status)              # 'pass' | 'fail' | 'warning' | 'not_evaluated'
print(result.captured_flow_cfs)   # intercepted flow
print(result.bypass_flow_cfs)     # flow that bypasses
print(result.capture_efficiency)  # captured / design (or None if design is 0)
```

`analyze_inlet_capacity(inlet, design_flow_cfs, head_ft)` dispatches by
`inlet.inlet_type` to the matching method below.

## Inlet types and methods

Supported types match the domain `Inlet` model: `grate`, `curb_opening`,
`combination`, `slotted`.

> Note: the original handoff named a `drop` inlet, but the domain model validates
> only `{grate, curb_opening, combination, slotted}`. `slotted` is the real
> supported fourth type, so the foundation models it rather than adding a new
> domain type.

### Grate inlet — submerged orifice

```text
Q = C · A · sqrt(2 · g · H)
```

- `C` = discharge coefficient (default 0.6)
- `A` = **gross** grate opening area = `grate_length_in × grate_width_in / 144` (sq ft)
- `H` = head over the grate (ft)

Gross area is used; bar blockage / open-area ratio are not modeled.

### Curb-opening inlet — weir

```text
Q = Cw · L · H^(3/2)
```

- `Cw` = weir coefficient (default 3.0)
- `L` = `opening_length_ft`
- `H` = head (ft)

### Combination inlet — grate + curb

```text
Q = Q_grate + Q_curb
```

Each present component (grate and/or curb opening) is computed and summed.
Interaction effects are not modeled.

### Slotted inlet — equivalent curb-opening weir

```text
Q = Cw · L · H^(3/2)
```

with `L = opening_length_ft` (slot length). Per HEC-22, slotted inlets are
treated like equivalent-length curb-opening inlets.

## Capture, bypass, efficiency, status

```text
captured  = min(capacity, design_flow)
bypass    = max(design_flow - captured, 0)
efficiency = captured / design_flow   (None if design_flow == 0)
status    = "pass" if captured >= design_flow else "fail"
```

## Clogging

Capacity is multiplied by the inlet's `effective_clogging_factor`
(`1 − clogging_factor`). When the factor is below 1.0 a
`capacity_reduced_by_clogging_factor` warning is recorded. This **uses** the
domain model's existing field rather than ignoring it.

## Worked benchmarks (asserted in tests)

| Method | Geometry | Head | Capacity |
|--------|----------|------|----------|
| Grate | 24 in × 24 in | 0.5 ft | 13.619 cfs |
| Curb | 5 ft opening | 0.5 ft | 5.303 cfs |
| Combination | grate + 5 ft curb | 0.5 ft | 18.922 cfs |
| Slotted | 10 ft slot | 0.4 ft | 7.590 cfs |

## Assumptions & limitations

- Simplified orifice (grate) / weir (curb, slotted) equations
- Gross grate area; no open-area ratio or bar blockage
- No roadway gutter spread or cross-slope interception
- No sag vs. grade inlet distinction (beyond metadata)
- Combination capacities are summed (no interaction effects)
- Design flow is explicit — runoff is not derived here
- Use the full FHWA HEC-22 procedure (or HydroCAD / equivalent) for design

## Result model

`InletCapacityResult` is a **standalone** dataclass with `to_dict`/`from_dict`,
`list[str]` references/assumptions, shaped so a later adapter can emit a domain
`CalculationResult`. Statuses: `pass`, `fail`, `warning`, `not_evaluated`.

## Future work

- FHWA HEC-22 gutter-spread / cross-slope interception
- Sag vs. grade inlet behavior
- Open-area ratio for grates
- HGL integration and storm-sewer system capture chains

## References

- FHWA HEC-22 (3rd ed., 2009), *Urban Drainage Design Manual* — grate, curb,
  combination, and slotted inlet interception.
