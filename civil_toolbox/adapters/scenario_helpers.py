"""Scenario attachment helpers.

Convenience functions for running calculations and attaching
results to Scenario entities.
"""

from typing import Optional

from civil_toolbox.domain.scenario import Scenario
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.storm import StormEvent
from civil_toolbox.domain.flow_path import FlowPath
from civil_toolbox.domain.calculation import CalculationResult

from civil_toolbox.adapters.rational_method import RationalMethodAdapter
from civil_toolbox.adapters.tr55 import TR55Adapter
from civil_toolbox.adapters.time_of_concentration import TimeOfConcentrationAdapter


def run_rational_method(
    scenario: Scenario,
    drainage_area: DrainageArea,
    storm_event: StormEvent,
    attach: bool = True,
) -> CalculationResult:
    """Run Rational Method and optionally attach result to scenario.

    Args:
        scenario: Scenario to attach result to
        drainage_area: DrainageArea with area_acres and runoff_coefficient
        storm_event: StormEvent with rainfall_intensity_in_per_hr
        attach: If True, add result to scenario.calculation_results

    Returns:
        CalculationResult with peak_runoff_cfs
    """
    result = RationalMethodAdapter.calculate(drainage_area, storm_event)

    if attach:
        scenario.add_calculation_result(result)

    return result


def run_rational_method_composite(
    scenario: Scenario,
    drainage_areas: list[DrainageArea],
    storm_event: StormEvent,
    attach: bool = True,
) -> CalculationResult:
    """Run composite Rational Method and optionally attach result.

    Args:
        scenario: Scenario to attach result to
        drainage_areas: List of DrainageArea entities
        storm_event: StormEvent with rainfall_intensity_in_per_hr
        attach: If True, add result to scenario.calculation_results

    Returns:
        CalculationResult with composite peak_runoff_cfs
    """
    result = RationalMethodAdapter.calculate_composite(drainage_areas, storm_event)

    if attach:
        scenario.add_calculation_result(result)

    return result


def run_tr55_runoff_depth(
    scenario: Scenario,
    drainage_area: DrainageArea,
    storm_event: StormEvent,
    ia_ratio: float = 0.2,
    attach: bool = True,
) -> CalculationResult:
    """Run TR-55 runoff depth and optionally attach result.

    Args:
        scenario: Scenario to attach result to
        drainage_area: DrainageArea with curve_number
        storm_event: StormEvent with rainfall_depth_in
        ia_ratio: Initial abstraction ratio (default 0.2)
        attach: If True, add result to scenario.calculation_results

    Returns:
        CalculationResult with runoff_depth_in
    """
    result = TR55Adapter.calculate_runoff_depth(
        drainage_area, storm_event, ia_ratio=ia_ratio
    )

    if attach:
        scenario.add_calculation_result(result)

    return result


def run_tr55_runoff_volume(
    scenario: Scenario,
    drainage_area: DrainageArea,
    storm_event: StormEvent,
    ia_ratio: float = 0.2,
    attach: bool = True,
) -> CalculationResult:
    """Run TR-55 runoff volume and optionally attach result.

    Args:
        scenario: Scenario to attach result to
        drainage_area: DrainageArea with curve_number and area_acres
        storm_event: StormEvent with rainfall_depth_in
        ia_ratio: Initial abstraction ratio (default 0.2)
        attach: If True, add result to scenario.calculation_results

    Returns:
        CalculationResult with runoff_volume_cf and runoff_volume_ac_ft
    """
    result = TR55Adapter.calculate_runoff_volume(
        drainage_area, storm_event, ia_ratio=ia_ratio
    )

    if attach:
        scenario.add_calculation_result(result)

    return result


def run_tc_kirpich(
    scenario: Scenario,
    flow_path: FlowPath,
    attach: bool = True,
) -> CalculationResult:
    """Run Kirpich Tc calculation and optionally attach result.

    Args:
        scenario: Scenario to attach result to
        flow_path: FlowPath with segments
        attach: If True, add result to scenario.calculation_results

    Returns:
        CalculationResult with tc_minutes
    """
    result = TimeOfConcentrationAdapter.calculate_kirpich(flow_path)

    if attach:
        scenario.add_calculation_result(result)

    return result


def run_tc_composite(
    scenario: Scenario,
    flow_path: FlowPath,
    rainfall_2yr_24hr_in: Optional[float] = None,
    attach: bool = True,
) -> CalculationResult:
    """Run composite Tc calculation and optionally attach result.

    Args:
        scenario: Scenario to attach result to
        flow_path: FlowPath with typed segments
        rainfall_2yr_24hr_in: Required for sheet flow segments
        attach: If True, add result to scenario.calculation_results

    Returns:
        CalculationResult with total tc_minutes
    """
    result = TimeOfConcentrationAdapter.calculate_composite(
        flow_path, rainfall_2yr_24hr_in=rainfall_2yr_24hr_in
    )

    if attach:
        scenario.add_calculation_result(result)

    return result


def run_all_drainage_areas(
    scenario: Scenario,
    storm_event: StormEvent,
    method: str = "rational",
    attach: bool = True,
) -> list[CalculationResult]:
    """Run calculations for all drainage areas in a scenario.

    Args:
        scenario: Scenario containing drainage areas
        storm_event: StormEvent to use for all calculations
        method: "rational" or "tr55"
        attach: If True, add results to scenario.calculation_results

    Returns:
        List of CalculationResult objects
    """
    results = []

    for area in scenario.drainage_areas:
        if method == "rational":
            result = RationalMethodAdapter.calculate(area, storm_event)
        elif method == "tr55":
            result = TR55Adapter.calculate_runoff_depth(area, storm_event)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'rational' or 'tr55'.")

        if attach:
            scenario.add_calculation_result(result)

        results.append(result)

    return results
