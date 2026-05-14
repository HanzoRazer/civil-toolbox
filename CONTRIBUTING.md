# Contributing to Civil Toolbox

Civil Toolbox is a drainage analysis and infrastructure planning workstation. Contributions should support transparent, verifiable engineering calculations.

---

## Project Direction

Civil Toolbox is transitioning from standalone calculators to a project-centered workstation. Contributions should align with this direction:

- Calculations belong to projects
- Projects contain drainage systems
- Systems contain infrastructure
- Infrastructure participates in scenarios
- Scenarios produce reports and decisions

---

## Ways to Contribute

### Bug Fixes

Fix calculation errors, input validation issues, or documentation mistakes.

### Engineering Methods

Add new hydrologic or hydraulic methods with proper references and validation.

### Documentation

Improve explanations, add examples, or clarify assumptions and limitations.

### Tests

Add validation cases, regression tests, or edge case coverage.

### Infrastructure

Improve build tooling, CI/CD, or development workflows.

---

## Development Setup

```bash
git clone https://github.com/HanzoRazer/civil-toolbox.git
cd civil-toolbox
python -m venv .venv
.venv\Scripts\activate        # Windows
# or: source .venv/bin/activate  # Unix
pip install -e ".[dev]"
pytest
```

---

## Branch Naming

Use descriptive branch names:

```text
feature/rational-method-validation
fix/tr55-curve-number-bounds
docs/manning-equation-examples
refactor/time-of-concentration-api
```

---

## Commit Messages

Write clear, concise commit messages:

```text
Add NRCS lag method for time of concentration

- Implement lag-based Tc calculation
- Add validation for watershed slope bounds
- Include reference to TR-55 Chapter 3
```

---

## Pull Request Requirements

Every PR should include:

1. **Summary** — What changed and why
2. **Engineering Impact** — How this affects calculations or workflows
3. **Assumptions** — Any engineering assumptions made
4. **Validation** — Test evidence or hand calculation verification
5. **Units** — Explicit units for all engineering quantities
6. **References** — Citations for engineering methods

---

## Engineering Calculation Contributions

Adding a new engineering method requires:

### Required Documentation

- Governing equation with variable definitions
- Input parameters with units and valid ranges
- Output parameters with units
- Assumptions and limitations
- At least one authoritative reference

### Required Tests

- Unit tests for core calculations
- Validation tests against known examples
- Input validation tests for bounds and edge cases
- Dimensional consistency checks

### Example

When adding a new Tc method:

```python
def kirpich_tc(length_ft: float, slope_ft_per_ft: float) -> float:
    """
    Kirpich formula for time of concentration.
    
    Tc = 0.0078 × L^0.77 × S^(-0.385)
    
    Args:
        length_ft: Channel length in feet
        slope_ft_per_ft: Average slope in ft/ft
    
    Returns:
        Time of concentration in minutes
    
    Reference:
        Kirpich, Z.P. (1940). Time of concentration of small
        agricultural watersheds. Civil Engineering, 10(6), 362.
    
    Limitations:
        - Best for rural watersheds with well-defined channels
        - Length should be < 10,000 ft
        - Slope should be 0.003 to 0.10 ft/ft
    """
```

---

## Testing Requirements

### Test Categories

| Category | Purpose |
|----------|---------|
| Unit tests | Verify function behavior |
| Validation tests | Compare against known benchmark values |
| Regression tests | Prevent reintroduction of fixed bugs |
| Input validation | Verify bounds checking and error handling |

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=packages --cov-report=html

# Run specific test file
pytest tests/test_rational.py -v
```

---

## Documentation Requirements

### Code Documentation

- Docstrings for all public functions
- Governing equations in docstrings
- Units for all parameters
- References for engineering methods

### User Documentation

- Update relevant docs when changing behavior
- Add examples for new methods
- Document limitations and edge cases

---

## Review Process

1. **Automated checks** — Tests must pass
2. **Engineering review** — Calculations verified against references
3. **Code review** — Style, structure, and maintainability
4. **Documentation review** — Assumptions and limitations documented

---

## Professional Responsibility

Civil Toolbox assists engineering analysis but does not replace professional judgment.

Contributors should:

- Document assumptions clearly
- State limitations explicitly
- Avoid implying guaranteed accuracy
- Recognize that users bear responsibility for applying results appropriately

Engineering calculations require licensed professional review before use in actual design or construction.
