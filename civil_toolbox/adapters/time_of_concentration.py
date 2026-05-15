"""Time of concentration domain adapter.

Adapts FlowPath domain entities to the TimeOfConcentration and
KinematicWave calculators, producing auditable CalculationResult.
"""

from typing import Optional

from civil_toolbox.calculators import TimeOfConcentration, KinematicWave
from civil_toolbox.domain.flow_path import FlowPath, FlowPathSegment
from civil_toolbox.domain.calculation import CalculationResult

from civil_toolbox.adapters.errors import (
    MissingFieldError,
    IncompatibleEntityError,
    CalculationNotApplicableError,
)
from civil_toolbox.adapters.result_builder import (
    ResultBuilder,
    KIRPICH_REFERENCE,
    KERBY_REFERENCE,
    KINEMATIC_WAVE_REFERENCE,
)


class TimeOfConcentrationAdapter:
    """Adapter for time of concentration calculations.

    Extracts segment data from FlowPath entities, validates
    completeness, calls the appropriate calculator, and returns
    auditable CalculationResult objects.

    All methods return time in MINUTES.
    """

    @staticmethod
    def calculate_kirpich(
        flow_path: FlowPath,
    ) -> CalculationResult:
        """Calculate Tc using Kirpich formula from total flow path.

        Requires total length and total elevation drop. Best for
        rural watersheds with defined channels.

        Args:
            flow_path: FlowPath with segments defining length and slope

        Returns:
            CalculationResult with tc_minutes

        Raises:
            MissingFieldError: If segments lack required data
            IncompatibleEntityError: If flow path has no segments
        """
        if not flow_path.segments:
            raise IncompatibleEntityError(
                f"FlowPath '{flow_path.name}' has no segments",
                reason="Kirpich formula requires flow path geometry",
            )

        total_length_ft = 0.0
        total_drop_ft = 0.0

        for i, seg in enumerate(flow_path.segments):
            if seg.length_ft <= 0:
                raise MissingFieldError(
                    f"Segment {i} in FlowPath '{flow_path.name}' has invalid length",
                    entity_type="FlowPathSegment",
                    field_name="length_ft",
                )
            if seg.slope_ft_per_ft <= 0:
                raise MissingFieldError(
                    f"Segment {i} in FlowPath '{flow_path.name}' has invalid slope",
                    entity_type="FlowPathSegment",
                    field_name="slope_ft_per_ft",
                )
            total_length_ft += seg.length_ft
            total_drop_ft += seg.length_ft * seg.slope_ft_per_ft

        calc_result = TimeOfConcentration.kirpich(
            flow_length_ft=total_length_ft,
            elevation_diff_ft=total_drop_ft,
        )

        builder = (
            ResultBuilder("tc_kirpich")
            .for_entity(flow_path.id, "FlowPath")
            .with_input("flow_length_ft", total_length_ft, "ft")
            .with_input("elevation_diff_ft", total_drop_ft, "ft")
            .with_input("segment_count", len(flow_path.segments))
            .with_output("tc_minutes", calc_result.tc_minutes, "min")
            .with_output("slope_percent", calc_result.slope_percent, "%")
            .with_reference(
                KIRPICH_REFERENCE.title,
                KIRPICH_REFERENCE.source,
                year=KIRPICH_REFERENCE.year,
                section=KIRPICH_REFERENCE.section,
            )
            .with_metadata("flow_path_name", flow_path.name)
        )

        return builder.build()

    @staticmethod
    def calculate_kerby(
        flow_path: FlowPath,
    ) -> CalculationResult:
        """Calculate Tc using Kerby formula from total flow path.

        Best for overland sheet flow on small watersheds.
        Uses roughness_n from segments.

        Args:
            flow_path: FlowPath with segments having roughness_n

        Returns:
            CalculationResult with tc_minutes

        Raises:
            MissingFieldError: If segments lack required data
        """
        if not flow_path.segments:
            raise IncompatibleEntityError(
                f"FlowPath '{flow_path.name}' has no segments",
                reason="Kerby formula requires flow path geometry",
            )

        total_length_ft = 0.0
        weighted_n_sum = 0.0
        avg_slope_sum = 0.0

        for i, seg in enumerate(flow_path.segments):
            if seg.length_ft <= 0:
                raise MissingFieldError(
                    f"Segment {i} has invalid length",
                    entity_type="FlowPathSegment",
                    field_name="length_ft",
                )
            if seg.slope_ft_per_ft <= 0:
                raise MissingFieldError(
                    f"Segment {i} has invalid slope",
                    entity_type="FlowPathSegment",
                    field_name="slope_ft_per_ft",
                )
            if seg.roughness_n is None:
                raise MissingFieldError(
                    f"Segment {i} in FlowPath '{flow_path.name}' is missing roughness_n",
                    entity_type="FlowPathSegment",
                    field_name="roughness_n",
                )
            total_length_ft += seg.length_ft
            weighted_n_sum += seg.roughness_n * seg.length_ft
            avg_slope_sum += seg.slope_ft_per_ft * seg.length_ft

        weighted_n = weighted_n_sum / total_length_ft
        avg_slope_pct = (avg_slope_sum / total_length_ft) * 100

        calc_result = TimeOfConcentration.kerby(
            flow_length_ft=total_length_ft,
            slope_percent=avg_slope_pct,
            retardance_n=weighted_n,
        )

        builder = (
            ResultBuilder("tc_kerby")
            .for_entity(flow_path.id, "FlowPath")
            .with_input("flow_length_ft", total_length_ft, "ft")
            .with_input("slope_percent", avg_slope_pct, "%")
            .with_input("retardance_n", weighted_n)
            .with_input("segment_count", len(flow_path.segments))
            .with_output("tc_minutes", calc_result.tc_minutes, "min")
            .with_reference(
                KERBY_REFERENCE.title,
                KERBY_REFERENCE.source,
                year=KERBY_REFERENCE.year,
                section=KERBY_REFERENCE.section,
            )
            .with_assumption(
                "Length-weighted average roughness computed from segments",
                category="roughness",
            )
            .with_metadata("flow_path_name", flow_path.name)
        )

        if total_length_ft > 1000:
            builder.with_warning(
                f"Flow length ({total_length_ft:.0f} ft) exceeds recommended "
                "1000 ft limit for Kerby formula",
                field="flow_length_ft",
            )

        return builder.build()

    @staticmethod
    def calculate_composite(
        flow_path: FlowPath,
        rainfall_2yr_24hr_in: Optional[float] = None,
    ) -> CalculationResult:
        """Calculate composite Tc by summing segment travel times.

        Selects appropriate method for each segment based on type:
        - sheet: KinematicWave (requires rainfall_2yr_24hr_in)
        - shallow_concentrated or channel: Kirpich

        Args:
            flow_path: FlowPath with typed segments
            rainfall_2yr_24hr_in: Required for sheet flow segments

        Returns:
            CalculationResult with total tc_minutes

        Raises:
            MissingFieldError: If segment data is incomplete
            IncompatibleEntityError: If sheet flow lacks rainfall data
        """
        if not flow_path.segments:
            raise IncompatibleEntityError(
                f"FlowPath '{flow_path.name}' has no segments",
                reason="Composite Tc requires flow path segments",
            )

        has_sheet_flow = any(s.segment_type == "sheet" for s in flow_path.segments)

        if has_sheet_flow and rainfall_2yr_24hr_in is None:
            raise IncompatibleEntityError(
                "Sheet flow segments require rainfall_2yr_24hr_in parameter",
                reason="Kinematic wave equation requires 2-year, 24-hour rainfall",
            )

        total_tc_minutes = 0.0
        segment_results: list[dict] = []

        for i, seg in enumerate(flow_path.segments):
            if seg.length_ft <= 0:
                raise MissingFieldError(
                    f"Segment {i} has invalid length",
                    entity_type="FlowPathSegment",
                    field_name="length_ft",
                )
            if seg.slope_ft_per_ft <= 0:
                raise MissingFieldError(
                    f"Segment {i} has invalid slope",
                    entity_type="FlowPathSegment",
                    field_name="slope_ft_per_ft",
                )

            slope_pct = seg.slope_ft_per_ft * 100

            if seg.segment_type == "sheet":
                if seg.roughness_n is None:
                    raise MissingFieldError(
                        f"Sheet flow segment {i} is missing roughness_n",
                        entity_type="FlowPathSegment",
                        field_name="roughness_n",
                    )
                kw_result = KinematicWave.sheet_flow_time(
                    flow_length_ft=seg.length_ft,
                    slope_percent=slope_pct,
                    mannings_n=seg.roughness_n,
                    rainfall_2yr_24hr_in=rainfall_2yr_24hr_in,
                )
                seg_tc_min = kw_result.travel_time_hours * 60
                method = "kinematic_wave"
            else:
                elevation_diff = seg.length_ft * seg.slope_ft_per_ft
                kirpich_result = TimeOfConcentration.kirpich(
                    flow_length_ft=seg.length_ft,
                    elevation_diff_ft=elevation_diff,
                )
                seg_tc_min = kirpich_result.tc_minutes
                method = "kirpich"

            total_tc_minutes += seg_tc_min
            segment_results.append({
                "segment_index": i,
                "segment_type": seg.segment_type,
                "method": method,
                "tc_minutes": seg_tc_min,
                "length_ft": seg.length_ft,
            })

        builder = (
            ResultBuilder("tc_composite")
            .for_entity(flow_path.id, "FlowPath")
            .with_input("segment_count", len(flow_path.segments))
            .with_input("total_length_ft", flow_path.total_length_ft, "ft")
            .with_output("tc_minutes", total_tc_minutes, "min")
            .with_assumption(
                "Composite Tc computed by summing individual segment travel times",
                category="method",
            )
            .with_metadata("flow_path_name", flow_path.name)
            .with_metadata("segment_results", segment_results)
        )

        if rainfall_2yr_24hr_in is not None:
            builder.with_input("rainfall_2yr_24hr_in", rainfall_2yr_24hr_in, "in")

        return builder.build()
