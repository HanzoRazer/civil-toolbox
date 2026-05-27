"""Example design criteria for testing and documentation.

These are SYNTHETIC data for demonstration purposes only.
Do not use for engineering design or permitting.
"""

from civil_toolbox.design_criteria.criteria import (
    DesignCriteria,
    DesignStormDefinition,
    RunoffCoefficientTable,
    RunoffCoefficientEntry,
    CurveNumberTable,
    CurveNumberEntry,
)
from civil_toolbox.design_criteria.libraries import DesignCriteriaLibrary
from civil_toolbox.rainfall.examples import create_example_idf_curve


def create_example_runoff_coefficient_table() -> RunoffCoefficientTable:
    """Create a synthetic example runoff coefficient table.

    This table is for TESTING AND DEMONSTRATION ONLY.
    It does not represent official engineering standards.

    Returns:
        RunoffCoefficientTable with common land use categories.
    """
    return RunoffCoefficientTable(
        entries=[
            RunoffCoefficientEntry(
                land_use="asphalt",
                min=0.70,
                max=0.95,
                typical=0.85,
                description="Asphalt or concrete pavement",
            ),
            RunoffCoefficientEntry(
                land_use="concrete",
                min=0.80,
                max=0.95,
                typical=0.90,
                description="Concrete surfaces",
            ),
            RunoffCoefficientEntry(
                land_use="roof",
                min=0.75,
                max=0.95,
                typical=0.85,
                description="Roofs (various materials)",
            ),
            RunoffCoefficientEntry(
                land_use="lawn_sandy",
                min=0.05,
                max=0.20,
                typical=0.10,
                description="Lawns on sandy soil",
            ),
            RunoffCoefficientEntry(
                land_use="lawn_clay",
                min=0.15,
                max=0.35,
                typical=0.25,
                description="Lawns on clay soil",
            ),
            RunoffCoefficientEntry(
                land_use="park",
                min=0.10,
                max=0.25,
                typical=0.15,
                description="Parks and cemeteries",
            ),
            RunoffCoefficientEntry(
                land_use="commercial",
                min=0.70,
                max=0.95,
                typical=0.85,
                description="Commercial/downtown areas",
            ),
            RunoffCoefficientEntry(
                land_use="residential_half_acre",
                min=0.25,
                max=0.40,
                typical=0.35,
                description="Residential (1/2 acre lots)",
            ),
            RunoffCoefficientEntry(
                land_use="residential_quarter_acre",
                min=0.40,
                max=0.60,
                typical=0.50,
                description="Residential (1/4 acre lots)",
            ),
            RunoffCoefficientEntry(
                land_use="industrial",
                min=0.50,
                max=0.80,
                typical=0.70,
                description="Industrial areas",
            ),
        ],
        source="Synthetic Example (Civil Toolbox Demo)",
        metadata={
            "synthetic": True,
            "for_testing_only": True,
        },
    )


def create_example_curve_number_table() -> CurveNumberTable:
    """Create a synthetic example curve number table.

    This table is for TESTING AND DEMONSTRATION ONLY.
    It does not represent official NRCS curve numbers.

    Returns:
        CurveNumberTable with common land use categories.
    """
    return CurveNumberTable(
        entries=[
            CurveNumberEntry(
                land_use="impervious",
                soil_groups={"A": 98, "B": 98, "C": 98, "D": 98},
                description="Impervious surfaces (pavement, roofs)",
            ),
            CurveNumberEntry(
                land_use="open_space_good",
                soil_groups={"A": 39, "B": 61, "C": 74, "D": 80},
                description="Open space, good condition",
            ),
            CurveNumberEntry(
                land_use="open_space_fair",
                soil_groups={"A": 49, "B": 69, "C": 79, "D": 84},
                description="Open space, fair condition",
            ),
            CurveNumberEntry(
                land_use="open_space_poor",
                soil_groups={"A": 68, "B": 79, "C": 86, "D": 89},
                description="Open space, poor condition",
            ),
            CurveNumberEntry(
                land_use="residential_1_acre",
                soil_groups={"A": 51, "B": 68, "C": 79, "D": 84},
                description="Residential (1 acre lots)",
            ),
            CurveNumberEntry(
                land_use="residential_half_acre",
                soil_groups={"A": 54, "B": 70, "C": 80, "D": 85},
                description="Residential (1/2 acre lots)",
            ),
            CurveNumberEntry(
                land_use="residential_quarter_acre",
                soil_groups={"A": 61, "B": 75, "C": 83, "D": 87},
                description="Residential (1/4 acre lots)",
            ),
            CurveNumberEntry(
                land_use="commercial",
                soil_groups={"A": 89, "B": 92, "C": 94, "D": 95},
                description="Commercial/business areas",
            ),
            CurveNumberEntry(
                land_use="industrial",
                soil_groups={"A": 81, "B": 88, "C": 91, "D": 93},
                description="Industrial areas",
            ),
            CurveNumberEntry(
                land_use="woods_good",
                soil_groups={"A": 30, "B": 55, "C": 70, "D": 77},
                description="Woods, good condition",
            ),
            CurveNumberEntry(
                land_use="woods_fair",
                soil_groups={"A": 36, "B": 60, "C": 73, "D": 79},
                description="Woods, fair condition",
            ),
            CurveNumberEntry(
                land_use="woods_poor",
                soil_groups={"A": 45, "B": 66, "C": 77, "D": 83},
                description="Woods, poor condition",
            ),
            CurveNumberEntry(
                land_use="row_crops_good",
                soil_groups={"A": 67, "B": 78, "C": 85, "D": 89},
                description="Row crops, contoured, good condition",
            ),
            CurveNumberEntry(
                land_use="pasture_good",
                soil_groups={"A": 39, "B": 61, "C": 74, "D": 80},
                description="Pasture/range, good condition",
            ),
        ],
        source="Synthetic Example (Civil Toolbox Demo)",
        metadata={
            "synthetic": True,
            "for_testing_only": True,
        },
    )


def create_example_design_criteria() -> DesignCriteria:
    """Create a synthetic example design criteria set.

    This criteria is for TESTING AND DEMONSTRATION ONLY.
    It does not represent official jurisdiction standards.

    Returns:
        DesignCriteria with example IDF curve, coefficients, and design storms.
    """
    return DesignCriteria(
        id="example-synthetic",
        name="Example Design Criteria",
        jurisdiction="Example County (Synthetic)",
        source="Civil Toolbox Demo Data",
        idf_curve=create_example_idf_curve(),
        runoff_coefficients=create_example_runoff_coefficient_table(),
        curve_numbers=create_example_curve_number_table(),
        design_storms=[
            DesignStormDefinition(
                name="2-year 24-hour",
                return_period_years=2,
                duration_minutes=1440,
                description="Minor drainage design storm",
            ),
            DesignStormDefinition(
                name="10-year 24-hour",
                return_period_years=10,
                duration_minutes=1440,
                description="Primary drainage design storm",
            ),
            DesignStormDefinition(
                name="25-year 24-hour",
                return_period_years=25,
                duration_minutes=1440,
                description="Secondary drainage design storm",
            ),
            DesignStormDefinition(
                name="100-year 24-hour",
                return_period_years=100,
                duration_minutes=1440,
                description="Major flood event",
            ),
            DesignStormDefinition(
                name="10-year 15-minute",
                return_period_years=10,
                duration_minutes=15,
                description="Inlet design storm",
            ),
            DesignStormDefinition(
                name="100-year 15-minute",
                return_period_years=100,
                duration_minutes=15,
                description="Inlet check storm",
            ),
        ],
        metadata={
            "synthetic": True,
            "for_testing_only": True,
            "warning": "This criteria is for demonstration purposes only. "
            "Do not use for engineering design or permitting.",
        },
    )


def create_example_design_criteria_library() -> DesignCriteriaLibrary:
    """Create a synthetic example design criteria library.

    This library is for TESTING AND DEMONSTRATION ONLY.
    It does not represent official jurisdiction standards.

    Returns:
        DesignCriteriaLibrary containing the example synthetic criteria.
    """
    library = DesignCriteriaLibrary(
        name="Example Criteria Library",
        metadata={
            "synthetic": True,
            "for_testing_only": True,
            "warning": "This library is for demonstration purposes only. "
            "Do not use for engineering design or permitting.",
        },
    )
    library.register(create_example_design_criteria())
    return library
