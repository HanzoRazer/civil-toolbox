"""Detention facility storage checking.

Simplified storage adequacy check comparing required volume to available volume.
This does not perform routing or outflow analysis.
"""

from __future__ import annotations

from civil_toolbox.infrastructure import DetentionFacility
from civil_toolbox.infrastructure_sizing.errors import InvalidSizingInputError
from civil_toolbox.infrastructure_sizing.models import InfrastructureCheckResult


def check_detention_storage(
    facility: DetentionFacility,
    required_storage_cuft: float,
) -> InfrastructureCheckResult:
    """Check if detention facility has adequate storage.

    Args:
        facility: The DetentionFacility object to check.
        required_storage_cuft: Required storage volume in cubic feet.

    Returns:
        InfrastructureCheckResult with storage comparison and pass/fail.

    Note:
        This is a simple volume comparison.
        It does not perform:
        - Inflow/outflow routing
        - Peak reduction analysis
        - Outlet sizing
        - Stage calculations

        Use detention routing software for detailed analysis.
    """
    if required_storage_cuft < 0:
        raise InvalidSizingInputError(
            f"required_storage_cuft cannot be negative, got {required_storage_cuft}"
        )

    result = InfrastructureCheckResult(
        element_id=facility.id,
        element_name=facility.name,
        element_type="detention",
        passes=False,
        required_storage_cuft=required_storage_cuft,
        method="Storage volume comparison",
    )

    result.add_assumption("Simple volume comparison only")
    result.add_assumption("No inflow/outflow routing performed")
    result.add_assumption("Peak reduction not calculated")
    result.add_assumption("Outlet sizing not evaluated")

    available_storage = facility.total_storage_cuft

    if available_storage is None:
        if facility.pond_bottom_area_sqft and facility.maximum_depth_ft:
            if facility.side_slope is not None:
                avg_area = (
                    facility.pond_bottom_area_sqft
                    + (facility.pond_bottom_area_sqft ** 0.5 +
                       facility.side_slope * facility.maximum_depth_ft) ** 2
                ) / 2
                available_storage = avg_area * facility.maximum_depth_ft
                result.add_assumption(
                    "Storage estimated from bottom area, depth, and side slope"
                )
            else:
                available_storage = (
                    facility.pond_bottom_area_sqft * facility.maximum_depth_ft
                )
                result.add_assumption(
                    "Storage estimated from bottom area × depth (vertical sides assumed)"
                )
        else:
            result.add_warning(
                "NO_STORAGE_DATA",
                "Facility has no stage-storage curve and insufficient geometry "
                "to estimate storage volume",
                severity="error",
            )
            return result

    result.storage_cuft = available_storage

    if required_storage_cuft == 0:
        result.passes = True
        return result

    result.utilization_ratio = required_storage_cuft / available_storage
    result.passes = required_storage_cuft <= available_storage

    if result.utilization_ratio > 0.9 and result.passes:
        result.add_warning(
            "HIGH_UTILIZATION",
            f"Storage utilization {result.utilization_ratio:.1%} is above 90%, "
            "limited margin for uncertainty",
        )

    if facility.spillway_elevation_ft is not None:
        if facility.stage_storage:
            max_stage = max(p.stage_ft for p in facility.stage_storage)
            if facility.spillway_elevation_ft < max_stage:
                usable_storage = facility.storage_at_stage(
                    facility.spillway_elevation_ft
                )
                if usable_storage and usable_storage < available_storage:
                    result.add_warning(
                        "SPILLWAY_LIMITS_STORAGE",
                        f"Spillway at elevation {facility.spillway_elevation_ft} ft "
                        f"limits usable storage to {usable_storage:,.0f} cu ft",
                        severity="info",
                    )
                    if required_storage_cuft > usable_storage:
                        result.passes = False
                        result.storage_cuft = usable_storage
                        result.utilization_ratio = required_storage_cuft / usable_storage

    if facility.permanent_pool_depth_ft:
        result.add_warning(
            "PERMANENT_POOL",
            f"Facility has {facility.permanent_pool_depth_ft} ft permanent pool. "
            "Verify storage volume excludes permanent pool.",
            severity="info",
        )

    result.add_warning(
        "ROUTING_REQUIRED",
        "This is a simple volume check. Perform inflow/outflow routing "
        "to verify peak reduction and outlet sizing.",
        severity="info",
    )

    return result
