---
name: Engineering Method Proposal
about: Propose a new hydrologic or hydraulic calculation method
title: "[METHOD] "
labels: "type: engineering-method"
assignees: ""
---

## Method Name

<!-- Official name of the method -->

## Engineering Purpose

<!-- What problem does this method solve? When would an engineer use it? -->

## Governing Equation

<!-- The primary equation(s). Use LaTeX or plaintext math notation. -->

```
Example: Q = C × i × A
```

## Inputs

| Parameter | Description | Units | Valid Range |
|-----------|-------------|-------|-------------|
|           |             |       |             |

## Outputs

| Parameter | Description | Units |
|-----------|-------------|-------|
|           |             |       |

## Assumptions

<!-- What assumptions does this method make? -->

- 

## Limitations

<!-- When should this method NOT be used? -->

- 

## References

<!-- At least one authoritative source required -->

1. 

## Validation Examples

<!-- Provide at least one example with known correct output -->

### Example 1

**Inputs:**

| Parameter | Value |
|-----------|-------|
|           |       |

**Expected Output:**

| Parameter | Value |
|-----------|-------|
|           |       |

**Source:** <!-- Where did this example come from? -->

## Suggested API

<!-- How should this be called in code? -->

```python
# Example function signature
def method_name(param1: float, param2: float) -> float:
    """Brief description."""
    pass
```
