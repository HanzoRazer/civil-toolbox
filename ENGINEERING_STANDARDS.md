# Engineering Standards

Civil Toolbox is engineering software. Every calculation must be transparent, traceable, and verifiable.

---

## Calculation Transparency

Engineering software should never function as a black box.

### Requirements

- Every method must document its governing equation
- Variable names must be clear and consistent with references
- Intermediate calculations should be traceable
- Output should include enough context to verify correctness

### CalcResult Contract

All calculations should return structured results with audit trails:

```python
CalcResult(
    value=100.0,
    units="cfs",
    formula_id="RATIONAL",
    references=(RATIONAL_REF,),
    inputs={"C": 0.5, "i": 4.0, "A": 50.0},
    applicability_warnings=(),
    derivation="Q = 0.5 × 4.0 × 50.0 = 100.0 cfs"
)
```

---

## Units and Dimensional Consistency

### Requirements

- All inputs and outputs must have explicit units
- Use standard suffixes in variable names: `_ft`, `_acres`, `_in_per_hr`, `_cfs`
- No bare floats in API responses
- Unit conversions must be explicit, not implicit

### Internal Standard

Civil Toolbox uses **Imperial units internally**:

| Quantity | Unit | Suffix |
|----------|------|--------|
| Length | feet | `_ft` |
| Area | acres | `_acres` |
| Rainfall intensity | inches per hour | `_in_per_hr` |
| Flow rate | cubic feet per second | `_cfs` |
| Volume | cubic feet | `_cf` |
| Slope | ft/ft | `_ft_per_ft` |
| Time | minutes or hours | `_min`, `_hr` |

### Dimensional Analysis

Functions should validate dimensional consistency:

```python
# Good: explicit units prevent errors
def rational_q(c: float, i_in_per_hr: float, a_acres: float) -> float:
    """Returns Q in cfs."""
    return c * i_in_per_hr * a_acres

# Bad: ambiguous units
def rational_q(c, i, a):
    return c * i * a
```

---

## Assumptions and Limitations

### Requirements

Every method must document:

1. **Applicability range** — When the method is valid
2. **Input bounds** — Valid ranges for parameters
3. **Limitations** — Known restrictions or simplifications
4. **Failure modes** — What happens outside valid ranges

### Example

```python
"""
Rational Method for peak runoff.

Applicability:
    - Drainage areas < 200 acres
    - Time of concentration < 20 minutes for best accuracy
    - Assumes uniform rainfall over the drainage area

Limitations:
    - Does not account for storage effects
    - Assumes steady-state conditions
    - Not suitable for complex watersheds with multiple sub-basins

Input bounds:
    - C: 0.0 to 1.0
    - i: > 0 in/hr
    - A: > 0 acres, typically < 200 acres
"""
```

---

## References

### Requirements

- Every engineering method must cite at least one authoritative reference
- References must include enough detail to locate the source
- Prefer primary sources (original publications, official manuals)
- Pin reference editions — use "TR-55 (1986)" not "current TR-55"

### Standard Reference Format

```python
Reference(
    short_name="TR-55",
    full_citation="USDA NRCS. (1986). Urban Hydrology for Small Watersheds. Technical Release 55.",
    section="Chapter 2: Estimating Runoff",
    url="https://www.nrcs.usda.gov/..."
)
```

### Core References

| Method | Primary Reference |
|--------|-------------------|
| Rational Method | ASCE Manual of Practice No. 77 |
| TR-55 / Curve Number | USDA NRCS TR-55 (1986) |
| Manning Equation | Chow (1959), Open Channel Hydraulics |
| Kirpich Tc | Kirpich (1940), Civil Engineering 10(6) |
| Kinematic Wave | FHWA HEC-22 |

---

## Validation Requirements

### Required Tests

Every calculation module must include:

| Test Type | Purpose |
|-----------|---------|
| **Benchmark tests** | Compare against textbook examples |
| **Validation tests** | Verify against hand calculations |
| **Boundary tests** | Check behavior at input limits |
| **Regression tests** | Prevent reintroduction of fixed bugs |

### Validation Example

```python
def test_rational_method_textbook_example():
    """
    Validate against Applied Hydrology, Chow et al., Example 5.4.1
    
    Given:
        C = 0.65
        i = 4.5 in/hr
        A = 25 acres
    
    Expected:
        Q = 73.125 cfs
    """
    result = rational_q(c=0.65, i_in_per_hr=4.5, a_acres=25)
    assert abs(result - 73.125) < 0.01
```

### Tolerance Policy

- Tolerance should match the precision of the reference
- Document why a tolerance was chosen
- Tighter tolerance is better when achievable

---

## Input Validation

### Requirements

- Validate inputs before calculation
- Return clear error messages for invalid inputs
- Distinguish between errors and warnings

### Error vs Warning

| Condition | Response |
|-----------|----------|
| Input outside valid range | Error — refuse to calculate |
| Input at edge of applicability | Warning — calculate with caution flag |
| Input valid but unusual | Info — note for user awareness |

### Example

```python
def rational_q(c: float, i_in_per_hr: float, a_acres: float) -> CalcResult:
    warnings = []
    
    if not 0 <= c <= 1:
        raise ValueError(f"Runoff coefficient C must be 0-1, got {c}")
    
    if a_acres > 200:
        warnings.append("Rational method accuracy decreases for areas > 200 acres")
    
    if a_acres > 640:
        raise ValueError("Rational method not applicable for areas > 1 sq mi")
    
    q = c * i_in_per_hr * a_acres
    
    return CalcResult(
        value=q,
        units="cfs",
        applicability_warnings=tuple(warnings),
        ...
    )
```

---

## Warning Conditions

### Applicability Warnings

Flag calculations that are valid but near the edge of method applicability:

- Area approaching method limits
- Slope outside typical range
- Unusual parameter combinations

### Consistency Warnings

Flag inputs that may indicate user error:

- Very low runoff coefficient for impervious area
- Very high curve number for wooded land
- Tc longer than storm duration

---

## Reproducibility

### Requirements

- Calculations must be deterministic
- Same inputs must produce same outputs
- No hidden state that affects results
- Random number generation (if any) must be seeded

### Pure Functions

Prefer pure functions for calculations:

```python
# Good: pure function, no side effects
def calculate_tc(length_ft: float, slope: float) -> float:
    return 0.0078 * (length_ft ** 0.77) * (slope ** -0.385)

# Bad: depends on external state
def calculate_tc(length_ft: float, slope: float) -> float:
    method = global_config.tc_method  # Hidden dependency
    ...
```

---

## Professional Judgment Disclaimer

Civil Toolbox provides engineering calculations for analysis and planning purposes.

**Results require review by a licensed professional engineer before use in actual design or construction.**

The software:

- Implements published engineering methods
- Documents assumptions and limitations
- Provides traceable calculations

The software does not:

- Replace professional engineering judgment
- Account for site-specific conditions not captured in inputs
- Guarantee fitness for any particular purpose
- Eliminate the need for independent verification

---

## Engineering Method Checklist

Before adding or modifying a calculation method:

- [ ] Governing equation documented
- [ ] All inputs and outputs include units
- [ ] Variable naming follows conventions
- [ ] Assumptions documented
- [ ] Limitations documented
- [ ] Input bounds defined
- [ ] At least one reference cited
- [ ] Benchmark test included
- [ ] Edge case tests included
- [ ] Applicability warnings implemented
