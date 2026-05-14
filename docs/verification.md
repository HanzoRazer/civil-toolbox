# Verification Standards

Engineering calculations must be verified before merging.

---

## Verification Levels

### Level 1 — Unit Tests

Basic functional verification.

- Function returns expected type
- Handles edge cases without crashing
- Input validation works correctly

### Level 2 — Benchmark Validation

Compare against known correct values.

- At least one textbook or manual example
- Document source, inputs, expected output
- Tolerance matches reference precision

### Level 3 — Cross-Validation

Compare against independent implementations.

- HEC-RAS, HEC-HMS, or commercial software
- Published calculator results
- Hand calculations by a second reviewer

---

## Required Verification by Method Type

| Method Type | Minimum Level |
|-------------|---------------|
| Simple formula (Q = CiA) | Level 2 |
| Multi-step calculation | Level 2 |
| Iterative solution | Level 3 |
| Complex hydraulics | Level 3 |

---

## Verification Documentation

Every method must document:

### Source References

```markdown
**Primary Reference:**
USDA NRCS. (1986). Urban Hydrology for Small Watersheds.
Technical Release 55, Chapter 2.
```

### Benchmark Example

```markdown
**Benchmark Case:**
- Source: TR-55 Example 2-1, p. 2-6
- Inputs: P = 5.0 in, CN = 75
- Expected: Q = 2.45 in
- Tolerance: ±0.01 in
```

### Validation Test

```python
def test_tr55_example_2_1():
    """TR-55 Example 2-1, p. 2-6"""
    result = tr55_runoff(precipitation_in=5.0, curve_number=75)
    assert abs(result - 2.45) < 0.01
```

---

## Hand Calculation Template

For methods without published examples, document a hand calculation:

```markdown
## Rational Method Verification

### Inputs
- C = 0.65 (commercial development)
- i = 4.5 in/hr (10-year, 15-minute)
- A = 25 acres

### Calculation
Q = C × i × A
Q = 0.65 × 4.5 × 25
Q = 73.125 cfs

### Verification
- Intermediate: 0.65 × 4.5 = 2.925
- Final: 2.925 × 25 = 73.125 cfs ✓
```

---

## Reviewer Checklist

Before approving an engineering method PR:

- [ ] Governing equation matches reference
- [ ] Units are explicit and consistent
- [ ] Input bounds are validated
- [ ] At least one benchmark test exists
- [ ] Tolerance is documented and reasonable
- [ ] Assumptions are documented
- [ ] Limitations are documented
- [ ] Reference is cited with enough detail to locate

---

## Common Verification Issues

### Issue: Tolerance Too Loose

```python
# Bad: hides potential errors
assert abs(result - 73.125) < 5.0

# Good: matches reference precision
assert abs(result - 73.125) < 0.01
```

### Issue: Missing Units

```python
# Bad: what are the units?
def calculate_flow(c, i, a):
    return c * i * a

# Good: units explicit
def calculate_flow_cfs(c: float, i_in_per_hr: float, a_acres: float) -> float:
    """Returns Q in cfs."""
    return c * i_in_per_hr * a_acres
```

### Issue: No Reference

```python
# Bad: where does 0.0078 come from?
def tc(length, slope):
    return 0.0078 * length**0.77 * slope**-0.385

# Good: reference provided
def kirpich_tc(length_ft: float, slope_ft_per_ft: float) -> float:
    """
    Kirpich formula for time of concentration.
    
    Reference: Kirpich (1940), Civil Engineering 10(6), p. 362
    """
    return 0.0078 * length_ft**0.77 * slope_ft_per_ft**-0.385
```

---

## Independent Verification Resources

### Software

- HEC-RAS (USACE)
- HEC-HMS (USACE)
- StormCAD (Bentley)
- SWMM (EPA)

### Online Calculators

- NRCS Web Soil Survey
- NOAA Atlas 14 Precipitation Frequency

### Manual Calculations

- Textbook examples with worked solutions
- Jurisdiction design manual examples
- Peer hand calculations
