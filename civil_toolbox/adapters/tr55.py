"""TR-55 domain adapter.

Adapts DrainageArea and StormEvent domain entities to the TR55
calculator, producing auditable CalculationResult.
"""

from civil_toolbox.calculators import TR55
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.storm import StormEvent
from civil_toolbox.domain.calculation import CalculationResult

from civil_toolbox.adapters.errors import (
    MissingFieldError,
    IncompatibleEntityError,
)
from civil_toolbox.adapters.result_builder import (
    ResultBuilder,
    TR55_REFERENCE,
)


class TR55Adapter:
    """Adapter for TR-55 runoff depth calculations.

    Extracts required fields from domain entities, validates
    completeness, calls the calculator, and returns an auditable
    CalculationResult.
    """

    @staticmethod
    def calculate_runoff_depth(
        drainage_area: DrainageArea,
        storm_event: StormEvent,
        ia_ratio: float = 0.2,
    ) -> CalculationResult:
        """Calculate runoff depth using TR-55 curve number method.

        Args:
            drainage_area: DrainageArea with curve_number
            storm_event: StormEvent with rainfall_depth_in
            ia_ratio: Initial abstraction ratio (default 0.2)

        Returns:
            CalculationResult with runoff_depth_in

        Raises:
            MissingFieldError: If required fields are None
        """
        if drainage_area.curve_number is None:
            raise MissingFieldError(
                f"DrainageArea '{drainage_area.name}' is missing curve_number",
                entity_type="DrainageArea",
                entity_id=drainage_area.id,
                field_name="curve_number",
            )

        if storm_event.rainfall_depth_in is None:
            raise MissingFieldError(
                f"StormEvent '{storm_event.name}' is missing rainfall_depth_in",
                entity_type="StormEvent",
                entity_id=storm_event.id,
                field_name="rainfall_depth_in",
            )

        calc_result = TR55.runoff_depth(
            rainfall_depth_in=storm_event.rainfall_depth_in,
            curve_number=drainage_area.curve_number,
            ia_ratio=ia_ratio,
        )

        builder = (
            ResultBuilder("tr55_runoff_depth")
            .for_entity(drainage_area.id, "DrainageArea")
            .with_input("rainfall_depth_in", storm_event.rainfall_depth_in, "in")
            .with_input("curve_number", drainage_area.curve_number)
            .with_input("ia_ratio", ia_ratio)
            .with_output("runoff_depth_in", calc_result.runoff_depth_in, "in")
            .with_output(
                "potential_retention_in",
                calc_result.potential_retention_in,
                "in",
            )
            .with_output(
                "initial_abstraction_in",
                calc_result.initial_abstraction_in,
                "in",
            )
            .with_reference(
                TR55_REFERENCE.title,
                TR55_REFERENCE.source,
                year=TR55_REFERENCE.year,
                section=TR55_REFERENCE.section,
            )
            .with_metadata("drainage_area_name", drainage_area.name)
            .with_metadata("storm_event_name", storm_event.name)
            .with_metadata("storm_event_id", storm_event.id)
        )

        if ia_ratio != 0.2:
            builder.with_assumption(
                f"Non-standard initial abstraction ratio: Ia = {ia_ratio}S",
                category="initial_abstraction",
            )

        if storm_event.return_period_years:
            builder.with_metadata(
                "return_period_years",
                storm_event.return_period_years,
            )

        return builder.build()

    @staticmethod
    def calculate_weighted_cn(
        drainage_areas: list[DrainageArea],
    ) -> CalculationResult:
        """Calculate area-weighted curve number for multiple areas.

        Args:
            drainage_areas: List of DrainageArea entities with
                           curve_number and area_acres

        Returns:
            CalculationResult with weighted_curve_number

        Raises:
            MissingFieldError: If any area lacks required fields
            IncompatibleEntityError: If no drainage areas provided
        """
        if not drainage_areas:
            raise IncompatibleEntityError(
                "At least one DrainageArea is required",
                reason="Cannot calculate weighted CN without drainage areas",
            )

        sub_areas: list[tuple[float, float]] = []

        for area in drainage_areas:
            if area.curve_number is None:
                raise MissingFieldError(
                    f"DrainageArea '{area.name}' is missing curve_number",
                    entity_type="DrainageArea",
                    entity_id=area.id,
                    field_name="curve_number",
                )
            if area.area_acres is None:
                raise MissingFieldError(
                    f"DrainageArea '{area.name}' is missing area_acres",
                    entity_type="DrainageArea",
                    entity_id=area.id,
                    field_name="area_acres",
                )
            sub_areas.append((float(area.curve_number), area.area_acres))

        weighted_cn = TR55.weighted_curve_number(sub_areas)
        total_area = sum(area.area_acres for area in drainage_areas)

        builder = (
            ResultBuilder("tr55_weighted_cn")
            .with_input("sub_area_count", len(drainage_areas))
            .with_input("total_area_acres", total_area, "acres")
            .with_output("weighted_curve_number", weighted_cn)
            .with_reference(
                TR55_REFERENCE.title,
                TR55_REFERENCE.source,
                year=TR55_REFERENCE.year,
                section=TR55_REFERENCE.section,
            )
            .with_assumption(
                "Area-weighted curve number computed from sub-areas",
                category="composite",
            )
            .with_metadata(
                "drainage_area_ids",
                [area.id for area in drainage_areas],
            )
        )

        return builder.build()

    @staticmethod
    def calculate_runoff_volume(
        drainage_area: DrainageArea,
        storm_event: StormEvent,
        ia_ratio: float = 0.2,
    ) -> CalculationResult:
        """Calculate runoff volume from depth and area.

        Args:
            drainage_area: DrainageArea with curve_number and area_acres
            storm_event: StormEvent with rainfall_depth_in
            ia_ratio: Initial abstraction ratio (default 0.2)

        Returns:
            CalculationResult with runoff_volume_cf and runoff_volume_ac_ft

        Raises:
            MissingFieldError: If required fields are None
        """
        if drainage_area.curve_number is None:
            raise MissingFieldError(
                f"DrainageArea '{drainage_area.name}' is missing curve_number",
                entity_type="DrainageArea",
                entity_id=drainage_area.id,
                field_name="curve_number",
            )

        if drainage_area.area_acres is None:
            raise MissingFieldError(
                f"DrainageArea '{drainage_area.name}' is missing area_acres",
                entity_type="DrainageArea",
                entity_id=drainage_area.id,
                field_name="area_acres",
            )

        if storm_event.rainfall_depth_in is None:
            raise MissingFieldError(
                f"StormEvent '{storm_event.name}' is missing rainfall_depth_in",
                entity_type="StormEvent",
                entity_id=storm_event.id,
                field_name="rainfall_depth_in",
            )

        calc_result = TR55.runoff_depth(
            rainfall_depth_in=storm_event.rainfall_depth_in,
            curve_number=drainage_area.curve_number,
            ia_ratio=ia_ratio,
        )

        runoff_depth_ft = calc_result.runoff_depth_in / 12.0
        area_sf = drainage_area.area_acres * 43560.0
        volume_cf = runoff_depth_ft * area_sf
        volume_ac_ft = volume_cf / 43560.0

        builder = (
            ResultBuilder("tr55_runoff_volume")
            .for_entity(drainage_area.id, "DrainageArea")
            .with_input("rainfall_depth_in", storm_event.rainfall_depth_in, "in")
            .with_input("curve_number", drainage_area.curve_number)
            .with_input("area_acres", drainage_area.area_acres, "acres")
            .with_input("ia_ratio", ia_ratio)
            .with_output("runoff_depth_in", calc_result.runoff_depth_in, "in")
            .with_output("runoff_volume_cf", volume_cf, "cf")
            .with_output("runoff_volume_ac_ft", volume_ac_ft, "ac-ft")
            .with_reference(
                TR55_REFERENCE.title,
                TR55_REFERENCE.source,
                year=TR55_REFERENCE.year,
                section=TR55_REFERENCE.section,
            )
            .with_metadata("drainage_area_name", drainage_area.name)
            .with_metadata("storm_event_name", storm_event.name)
            .with_metadata("storm_event_id", storm_event.id)
        )

        return builder.build()
