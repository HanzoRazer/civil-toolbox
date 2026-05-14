# Testing Guide

Civil Toolbox tests verify both code correctness and engineering accuracy.

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=packages --cov-report=html

# Run specific test file
pytest tests/test_rational.py -v

# Run tests matching a pattern
pytest -k "rational" -v
```

---

## Test Categories

### Unit Tests

Verify individual functions behave correctly.

```python
def test_rational_basic():
    result = rational_q(c=0.5, i_in_per_hr=4.0, a_acres=50.0)
    assert result == 100.0
```

### Validation Tests

Compare calculations against known benchmark values from references.

```python
def test_rational_textbook_example():
    """
    Validate against Applied Hydrology, Chow et al., Example 5.4.1
    """
    result = rational_q(c=0.65, i_in_per_hr=4.5, a_acres=25)
    assert abs(result - 73.125) < 0.01
```

### Regression Tests

Prevent reintroduction of previously fixed bugs.

```python
def test_tr55_zero_rainfall_regression():
    """
    Issue #42: Zero rainfall should return zero runoff, not error.
    """
    result = tr55_runoff(precipitation_in=0.0, curve_number=75)
    assert result == 0.0
```

### Input Validation Tests

Verify bounds checking and error handling.

```python
def test_rational_invalid_coefficient():
    with pytest.raises(ValueError, match="must be 0-1"):
        rational_q(c=1.5, i_in_per_hr=4.0, a_acres=50.0)
```

### Dimensional Consistency Tests

Verify units are handled correctly.

```python
def test_tc_units_minutes():
    result = kirpich_tc(length_ft=2500, slope_ft_per_ft=0.02)
    assert result > 0  # Must be positive
    assert result < 120  # Reasonable range for Tc in minutes
```

---

## Test File Organization

```text
tests/
├── conftest.py              # Shared fixtures
├── test_rational.py         # Rational Method tests
├── test_tr55.py             # TR-55 tests
├── test_time_of_concentration.py
├── fixtures/                # Validation data (future)
│   ├── rational_cases.json
│   └── tr55_cases.json
└── README.md                # This file
```

---

## Writing Validation Tests

### Requirements

Every engineering method should have validation tests that:

1. Reference a known source (textbook, manual, hand calculation)
2. Document the expected value and tolerance
3. Explain why the tolerance was chosen

### Example Structure

```python
def test_kirpich_fhwa_example():
    """
    Validate Kirpich Tc against FHWA HEC-22 Example 3.1.
    
    Given:
        L = 2,500 ft (channel length)
        S = 0.02 ft/ft (average slope)
    
    Expected:
        Tc = 12.7 minutes
    
    Tolerance:
        0.1 minutes (matches precision in reference)
    
    Reference:
        FHWA HEC-22, 3rd Edition, Example 3.1, p. 3-5
    """
    result = kirpich_tc(length_ft=2500, slope_ft_per_ft=0.02)
    assert abs(result - 12.7) < 0.1
```

---

## Tolerance Policy

### General Guidelines

| Situation | Tolerance |
|-----------|-----------|
| Reference shows 2 decimal places | ±0.01 |
| Reference shows 1 decimal place | ±0.1 |
| Reference shows integer | ±0.5 |
| Hand calculation | Match intermediate precision |

### Documenting Tolerance

Always explain why a tolerance was chosen:

```python
# Good: tolerance explained
assert abs(result - 73.125) < 0.01  # Reference shows 3 decimals

# Bad: arbitrary tolerance
assert abs(result - 73.125) < 0.5
```

---

## Fixture Pattern (Future)

For methods with many validation cases, use JSON fixtures:

```json
{
  "method": "rational_method",
  "cases": [
    {
      "description": "Commercial area example",
      "inputs": {
        "c": 0.85,
        "i_in_per_hr": 5.2,
        "a_acres": 15
      },
      "expected": {
        "q_cfs": 66.3
      },
      "tolerance": 0.1,
      "reference": "Hand calculation"
    }
  ]
}
```

Load and run:

```python
import json
import pytest

with open("tests/fixtures/rational_cases.json") as f:
    CASES = json.load(f)["cases"]

@pytest.mark.parametrize("case", CASES, ids=lambda c: c["description"])
def test_rational_fixtures(case):
    result = rational_q(**case["inputs"])
    assert abs(result - case["expected"]["q_cfs"]) < case["tolerance"]
```

---

## Coverage Goals

| Category | Target |
|----------|--------|
| Overall | 80% |
| Calculation kernels | 95% |
| Input validation | 100% |
| API endpoints | 80% |

Focus coverage on calculation correctness, not boilerplate.
