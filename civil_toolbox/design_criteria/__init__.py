"""Design criteria library for managing jurisdiction-specific design standards.

Provides data models and registry for runoff coefficients, curve numbers,
design storms, and IDF curves.

Example:
    >>> from civil_toolbox.design_criteria import (
    ...     DesignCriteria,
    ...     DesignCriteriaLibrary,
    ...     create_example_design_criteria,
    ... )
    >>> criteria = create_example_design_criteria()
    >>> library = DesignCriteriaLibrary()
    >>> library.register(criteria)
    >>> c = library.get("example-synthetic")
    >>> coeff = c.lookup_runoff_coefficient("asphalt")
"""

from civil_toolbox.design_criteria.criteria import (
    CurveNumberEntry,
    CurveNumberTable,
    DesignCriteria,
    DesignStormDefinition,
    RunoffCoefficientEntry,
    RunoffCoefficientTable,
)
from civil_toolbox.design_criteria.errors import (
    CriteriaNotFoundError,
    DesignCriteriaError,
    DesignCriteriaLookupError,
    InvalidDesignCriteriaError,
)
from civil_toolbox.design_criteria.examples import (
    create_example_curve_number_table,
    create_example_design_criteria,
    create_example_design_criteria_library,
    create_example_runoff_coefficient_table,
)
from civil_toolbox.design_criteria.libraries import DesignCriteriaLibrary
from civil_toolbox.design_criteria.validation import (
    VALID_SOIL_GROUPS,
    normalize_land_use_key,
    validate_curve_number,
    validate_duration_minutes,
    validate_return_period,
    validate_runoff_coefficient,
    validate_soil_group,
)

__all__ = [
    # Core data models
    "RunoffCoefficientEntry",
    "RunoffCoefficientTable",
    "CurveNumberEntry",
    "CurveNumberTable",
    "DesignStormDefinition",
    "DesignCriteria",
    # Library/registry
    "DesignCriteriaLibrary",
    # Errors
    "DesignCriteriaError",
    "InvalidDesignCriteriaError",
    "DesignCriteriaLookupError",
    "CriteriaNotFoundError",
    # Validation
    "VALID_SOIL_GROUPS",
    "normalize_land_use_key",
    "validate_runoff_coefficient",
    "validate_curve_number",
    "validate_soil_group",
    "validate_return_period",
    "validate_duration_minutes",
    # Examples
    "create_example_runoff_coefficient_table",
    "create_example_curve_number_table",
    "create_example_design_criteria",
    "create_example_design_criteria_library",
]
