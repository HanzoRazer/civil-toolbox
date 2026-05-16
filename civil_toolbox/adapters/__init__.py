"""Calculator domain adapters for Civil Toolbox.

Adapters connect the calculation engine to domain entities, producing
auditable CalculationResult objects that can be attached to Scenarios.

Adapters:
- RationalMethodAdapter: Peak runoff from DrainageArea + StormEvent
- TR55Adapter: Runoff depth from DrainageArea + StormEvent
- TimeOfConcentrationAdapter: Tc from FlowPath segments

Scenario Helpers:
- run_rational_method, run_rational_method_composite
- run_tr55_runoff_depth, run_tr55_runoff_volume
- run_tc_kirpich, run_tc_composite
- run_all_drainage_areas

All adapters raise MissingFieldError when domain entities lack required
fields. They never infer engineering assumptions silently.
"""

from civil_toolbox.adapters.errors import (
    AdapterError,
    MissingFieldError,
    IncompatibleEntityError,
    CalculationNotApplicableError,
)

from civil_toolbox.adapters.result_builder import (
    ResultBuilder,
    RATIONAL_METHOD_REFERENCE,
    TR55_REFERENCE,
    KIRPICH_REFERENCE,
    KERBY_REFERENCE,
    KINEMATIC_WAVE_REFERENCE,
)

from civil_toolbox.adapters.rational_method import RationalMethodAdapter
from civil_toolbox.adapters.tr55 import TR55Adapter
from civil_toolbox.adapters.time_of_concentration import TimeOfConcentrationAdapter

from civil_toolbox.adapters.scenario_helpers import (
    run_rational_method,
    run_rational_method_composite,
    run_tr55_runoff_depth,
    run_tr55_runoff_volume,
    run_tc_kirpich,
    run_tc_composite,
    run_all_drainage_areas,
)

__all__ = [
    # Errors
    "AdapterError",
    "MissingFieldError",
    "IncompatibleEntityError",
    "CalculationNotApplicableError",
    # Result Builder
    "ResultBuilder",
    "RATIONAL_METHOD_REFERENCE",
    "TR55_REFERENCE",
    "KIRPICH_REFERENCE",
    "KERBY_REFERENCE",
    "KINEMATIC_WAVE_REFERENCE",
    # Adapters
    "RationalMethodAdapter",
    "TR55Adapter",
    "TimeOfConcentrationAdapter",
    # Scenario Helpers
    "run_rational_method",
    "run_rational_method_composite",
    "run_tr55_runoff_depth",
    "run_tr55_runoff_volume",
    "run_tc_kirpich",
    "run_tc_composite",
    "run_all_drainage_areas",
]
