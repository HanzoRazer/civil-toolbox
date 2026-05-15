"""Rational Method domain adapter.

Adapts DrainageArea and StormEvent domain entities to the
RationalMethod calculator, producing auditable CalculationResult.
"""

from civil_toolbox.calculators import RationalMethod
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.storm import StormEvent
from civil_toolbox.domain.calculation import CalculationResult

from civil_toolbox.adapters.errors import (
    MissingFieldError,
    IncompatibleEntityError,
    CalculationNotApplicableError,
)
from civil_toolbox.adapters.result_builder import (
    ResultBuilder,
    RATIONAL_METHOD_REFERENCE,
)


RATIONAL_METHOD_AREA_LIMIT_ACRES = 200.0


class RationalMethodAdapter:
    """Adapter for Rational Method calculations.

    Extracts required fields from domain entities, validates
    completeness, calls the calculator, and returns an auditable
    CalculationResult.
    """

    @staticmethod
    def calculate(
        drainage_area: DrainageArea,
        storm_event: StormEvent,
        warn_on_large_area: bool = True,
    ) -> CalculationResult:
        """Calculate peak runoff using the Rational Method.

        Args:
            drainage_area: DrainageArea with area_acres and runoff_coefficient
            storm_event: StormEvent with rainfall_intensity_in_per_hr
            warn_on_large_area: Add warning if area > 200 acres

        Returns:
            CalculationResult with peak_runoff_cfs

        Raises:
            MissingFieldError: If required fields are None
            IncompatibleEntityError: If entities lack compatible data
        """
        if drainage_area.area_acres is None:
            raise MissingFieldError(
                f"DrainageArea '{drainage_area.name}' is missing area_acres",
                entity_type="DrainageArea",
                entity_id=drainage_area.id,
                field_name="area_acres",
            )

        if drainage_area.runoff_coefficient is None:
            raise MissingFieldError(
                f"DrainageArea '{drainage_area.name}' is missing runoff_coefficient",
                entity_type="DrainageArea",
                entity_id=drainage_area.id,
                field_name="runoff_coefficient",
            )

        if storm_event.rainfall_intensity_in_per_hr is None:
            raise MissingFieldError(
                f"StormEvent '{storm_event.name}' is missing rainfall_intensity_in_per_hr",
                entity_type="StormEvent",
                entity_id=storm_event.id,
                field_name="rainfall_intensity_in_per_hr",
            )

        calc_result = RationalMethod.calculate(
            runoff_coefficient=drainage_area.runoff_coefficient,
            rainfall_intensity_in_per_hr=storm_event.rainfall_intensity_in_per_hr,
            area_acres=drainage_area.area_acres,
        )

        builder = (
            ResultBuilder("rational_method")
            .for_entity(drainage_area.id, "DrainageArea")
            .with_input("area_acres", drainage_area.area_acres, "acres")
            .with_input("runoff_coefficient", drainage_area.runoff_coefficient)
            .with_input(
                "rainfall_intensity_in_per_hr",
                storm_event.rainfall_intensity_in_per_hr,
                "in/hr",
            )
            .with_output("peak_runoff_cfs", calc_result.peak_runoff_cfs, "cfs")
            .with_reference(
                RATIONAL_METHOD_REFERENCE.title,
                RATIONAL_METHOD_REFERENCE.source,
                year=RATIONAL_METHOD_REFERENCE.year,
                section=RATIONAL_METHOD_REFERENCE.section,
            )
            .with_metadata("drainage_area_name", drainage_area.name)
            .with_metadata("storm_event_name", storm_event.name)
            .with_metadata("storm_event_id", storm_event.id)
        )

        if (
            warn_on_large_area
            and drainage_area.area_acres > RATIONAL_METHOD_AREA_LIMIT_ACRES
        ):
            builder.with_warning(
                f"Drainage area ({drainage_area.area_acres:.1f} acres) exceeds "
                f"recommended limit of {RATIONAL_METHOD_AREA_LIMIT_ACRES} acres "
                "for Rational Method",
                field="area_acres",
            )

        if storm_event.return_period_years:
            builder.with_metadata("return_period_years", storm_event.return_period_years)

        return builder.build()

    @staticmethod
    def calculate_composite(
        drainage_areas: list[DrainageArea],
        storm_event: StormEvent,
    ) -> CalculationResult:
        """Calculate peak runoff for multiple drainage areas.

        Computes area-weighted runoff coefficient and total area.

        Args:
            drainage_areas: List of DrainageArea entities
            storm_event: StormEvent with rainfall_intensity_in_per_hr

        Returns:
            CalculationResult with composite peak_runoff_cfs

        Raises:
            MissingFieldError: If any area lacks required fields
            IncompatibleEntityError: If no drainage areas provided
        """
        if not drainage_areas:
            raise IncompatibleEntityError(
                "At least one DrainageArea is required",
                reason="Cannot calculate composite runoff without drainage areas",
            )

        if storm_event.rainfall_intensity_in_per_hr is None:
            raise MissingFieldError(
                f"StormEvent '{storm_event.name}' is missing rainfall_intensity_in_per_hr",
                entity_type="StormEvent",
                entity_id=storm_event.id,
                field_name="rainfall_intensity_in_per_hr",
            )

        sub_areas: list[tuple[float, float]] = []

        for area in drainage_areas:
            if area.area_acres is None:
                raise MissingFieldError(
                    f"DrainageArea '{area.name}' is missing area_acres",
                    entity_type="DrainageArea",
                    entity_id=area.id,
                    field_name="area_acres",
                )
            if area.runoff_coefficient is None:
                raise MissingFieldError(
                    f"DrainageArea '{area.name}' is missing runoff_coefficient",
                    entity_type="DrainageArea",
                    entity_id=area.id,
                    field_name="runoff_coefficient",
                )
            sub_areas.append((area.runoff_coefficient, area.area_acres))

        calc_result = RationalMethod.calculate_composite(
            sub_areas=sub_areas,
            rainfall_intensity_in_per_hr=storm_event.rainfall_intensity_in_per_hr,
        )

        builder = (
            ResultBuilder("rational_method_composite")
            .with_input("sub_area_count", len(drainage_areas))
            .with_input("total_area_acres", calc_result.area_acres, "acres")
            .with_input("composite_runoff_coefficient", calc_result.runoff_coefficient)
            .with_input(
                "rainfall_intensity_in_per_hr",
                storm_event.rainfall_intensity_in_per_hr,
                "in/hr",
            )
            .with_output("peak_runoff_cfs", calc_result.peak_runoff_cfs, "cfs")
            .with_reference(
                RATIONAL_METHOD_REFERENCE.title,
                RATIONAL_METHOD_REFERENCE.source,
                year=RATIONAL_METHOD_REFERENCE.year,
                section=RATIONAL_METHOD_REFERENCE.section,
            )
            .with_assumption(
                "Area-weighted runoff coefficient computed from sub-areas",
                category="composite",
            )
            .with_metadata("storm_event_name", storm_event.name)
            .with_metadata("storm_event_id", storm_event.id)
            .with_metadata(
                "drainage_area_ids",
                [area.id for area in drainage_areas],
            )
        )

        if calc_result.area_acres > RATIONAL_METHOD_AREA_LIMIT_ACRES:
            builder.with_warning(
                f"Total area ({calc_result.area_acres:.1f} acres) exceeds "
                f"recommended limit of {RATIONAL_METHOD_AREA_LIMIT_ACRES} acres "
                "for Rational Method",
                field="total_area_acres",
            )

        return builder.build()
