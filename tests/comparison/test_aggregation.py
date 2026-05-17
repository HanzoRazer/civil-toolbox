"""Tests for scenario aggregation."""

import pytest

from civil_toolbox.comparison.aggregation import (
    compute_delta,
    compute_percent_delta,
    aggregate_totals,
)
from civil_toolbox.comparison.models import (
    ComparisonMetric,
    ComparisonStatus,
    PercentDeltaStatus,
    MetricComparisonResult,
    EntityComparisonResult,
)


class TestComputeDelta:
    """Tests for compute_delta."""

    def test_computes_positive_delta(self):
        """Computes positive delta when comparison > baseline."""
        assert compute_delta(100.0, 120.0) == 20.0

    def test_computes_negative_delta(self):
        """Computes negative delta when comparison < baseline."""
        assert compute_delta(100.0, 80.0) == -20.0

    def test_computes_zero_delta(self):
        """Computes zero delta when values equal."""
        assert compute_delta(100.0, 100.0) == 0.0

    def test_returns_none_for_none_baseline(self):
        """Returns None when baseline is None."""
        assert compute_delta(None, 100.0) is None

    def test_returns_none_for_none_comparison(self):
        """Returns None when comparison is None."""
        assert compute_delta(100.0, None) is None

    def test_returns_none_for_both_none(self):
        """Returns None when both values are None."""
        assert compute_delta(None, None) is None


class TestComputePercentDelta:
    """Tests for compute_percent_delta."""

    def test_computes_positive_percent(self):
        """Computes positive percent for increase."""
        percent, status = compute_percent_delta(100.0, 120.0)
        assert percent == 20.0
        assert status == PercentDeltaStatus.OK

    def test_computes_negative_percent(self):
        """Computes negative percent for decrease."""
        percent, status = compute_percent_delta(100.0, 80.0)
        assert percent == -20.0
        assert status == PercentDeltaStatus.OK

    def test_computes_zero_percent(self):
        """Computes zero percent for no change."""
        percent, status = compute_percent_delta(100.0, 100.0)
        assert percent == 0.0
        assert status == PercentDeltaStatus.OK

    def test_returns_none_for_zero_baseline(self):
        """Returns None with undefined status for zero baseline."""
        percent, status = compute_percent_delta(0.0, 50.0)
        assert percent is None
        assert status == PercentDeltaStatus.UNDEFINED_ZERO_BASELINE

    def test_returns_none_for_none_baseline(self):
        """Returns None with not applicable status for None baseline."""
        percent, status = compute_percent_delta(None, 100.0)
        assert percent is None
        assert status == PercentDeltaStatus.NOT_APPLICABLE

    def test_returns_none_for_none_comparison(self):
        """Returns None with not applicable status for None comparison."""
        percent, status = compute_percent_delta(100.0, None)
        assert percent is None
        assert status == PercentDeltaStatus.NOT_APPLICABLE


class TestAggregateTotals:
    """Tests for aggregate_totals."""

    def test_sums_additive_metrics(self):
        """Sums additive metrics across entities."""
        entities = [
            EntityComparisonResult(
                baseline_entity_id="area-1",
                comparison_entity_id="area-1",
                entity_name="Area A",
                entity_type="DrainageArea",
                metrics={
                    ComparisonMetric.PEAK_FLOW_CFS: MetricComparisonResult(
                        metric=ComparisonMetric.PEAK_FLOW_CFS,
                        baseline_value=100.0,
                        comparison_value=120.0,
                        delta=20.0,
                        percent_delta=20.0,
                        unit="cfs",
                    ),
                },
            ),
            EntityComparisonResult(
                baseline_entity_id="area-2",
                comparison_entity_id="area-2",
                entity_name="Area B",
                entity_type="DrainageArea",
                metrics={
                    ComparisonMetric.PEAK_FLOW_CFS: MetricComparisonResult(
                        metric=ComparisonMetric.PEAK_FLOW_CFS,
                        baseline_value=200.0,
                        comparison_value=250.0,
                        delta=50.0,
                        percent_delta=25.0,
                        unit="cfs",
                    ),
                },
            ),
        ]

        totals = aggregate_totals(entities)

        assert ComparisonMetric.PEAK_FLOW_CFS in totals
        peak_total = totals[ComparisonMetric.PEAK_FLOW_CFS]
        assert peak_total.baseline_total == 300.0
        assert peak_total.comparison_total == 370.0
        assert peak_total.delta == 70.0
        assert peak_total.entity_count == 2

    def test_does_not_sum_non_additive_metrics(self):
        """Does not sum non-additive metrics."""
        entities = [
            EntityComparisonResult(
                baseline_entity_id="area-1",
                comparison_entity_id="area-1",
                entity_name="Area A",
                entity_type="DrainageArea",
                metrics={
                    ComparisonMetric.RUNOFF_DEPTH_IN: MetricComparisonResult(
                        metric=ComparisonMetric.RUNOFF_DEPTH_IN,
                        baseline_value=2.5,
                        comparison_value=3.0,
                        delta=0.5,
                        percent_delta=20.0,
                        unit="in",
                    ),
                    ComparisonMetric.TIME_OF_CONCENTRATION_MIN: MetricComparisonResult(
                        metric=ComparisonMetric.TIME_OF_CONCENTRATION_MIN,
                        baseline_value=15.0,
                        comparison_value=12.0,
                        delta=-3.0,
                        percent_delta=-20.0,
                        unit="min",
                    ),
                },
            ),
        ]

        totals = aggregate_totals(entities)

        assert ComparisonMetric.RUNOFF_DEPTH_IN not in totals
        assert ComparisonMetric.TIME_OF_CONCENTRATION_MIN not in totals

    def test_handles_missing_comparison_values(self):
        """Handles entities with missing comparison values."""
        entities = [
            EntityComparisonResult(
                baseline_entity_id="area-1",
                comparison_entity_id="area-1",
                entity_name="Area A",
                entity_type="DrainageArea",
                metrics={
                    ComparisonMetric.PEAK_FLOW_CFS: MetricComparisonResult(
                        metric=ComparisonMetric.PEAK_FLOW_CFS,
                        baseline_value=100.0,
                        comparison_value=120.0,
                        delta=20.0,
                        percent_delta=20.0,
                        unit="cfs",
                    ),
                },
            ),
            EntityComparisonResult(
                baseline_entity_id="area-2",
                comparison_entity_id="area-2",
                entity_name="Area B",
                entity_type="DrainageArea",
                metrics={
                    ComparisonMetric.PEAK_FLOW_CFS: MetricComparisonResult(
                        metric=ComparisonMetric.PEAK_FLOW_CFS,
                        baseline_value=200.0,
                        comparison_value=None,
                        delta=None,
                        percent_delta=None,
                        unit="cfs",
                        status=ComparisonStatus.MISSING_COMPARISON,
                    ),
                },
            ),
        ]

        totals = aggregate_totals(entities)

        peak_total = totals[ComparisonMetric.PEAK_FLOW_CFS]
        assert peak_total.baseline_total == 300.0
        assert peak_total.comparison_total == 120.0

    def test_handles_missing_baseline_values(self):
        """Handles entities with missing baseline values."""
        entities = [
            EntityComparisonResult(
                baseline_entity_id="area-1",
                comparison_entity_id="area-1",
                entity_name="Area A",
                entity_type="DrainageArea",
                metrics={
                    ComparisonMetric.RUNOFF_VOLUME_CUFT: MetricComparisonResult(
                        metric=ComparisonMetric.RUNOFF_VOLUME_CUFT,
                        baseline_value=None,
                        comparison_value=50000.0,
                        delta=None,
                        percent_delta=None,
                        unit="cf",
                        status=ComparisonStatus.MISSING_BASELINE,
                    ),
                },
            ),
        ]

        totals = aggregate_totals(entities)

        volume_total = totals[ComparisonMetric.RUNOFF_VOLUME_CUFT]
        assert volume_total.baseline_total is None
        assert volume_total.comparison_total == 50000.0
        assert volume_total.delta is None

    def test_computes_percent_delta(self):
        """Computes percent delta for totals."""
        entities = [
            EntityComparisonResult(
                baseline_entity_id="area-1",
                comparison_entity_id="area-1",
                entity_name="Area A",
                entity_type="DrainageArea",
                metrics={
                    ComparisonMetric.PEAK_FLOW_CFS: MetricComparisonResult(
                        metric=ComparisonMetric.PEAK_FLOW_CFS,
                        baseline_value=100.0,
                        comparison_value=125.0,
                        delta=25.0,
                        percent_delta=25.0,
                        unit="cfs",
                    ),
                },
            ),
        ]

        totals = aggregate_totals(entities)

        peak_total = totals[ComparisonMetric.PEAK_FLOW_CFS]
        assert peak_total.percent_delta == 25.0
        assert peak_total.percent_delta_status == PercentDeltaStatus.OK

    def test_handles_zero_baseline_total(self):
        """Handles zero baseline total for percent delta."""
        entities = [
            EntityComparisonResult(
                baseline_entity_id="area-1",
                comparison_entity_id="area-1",
                entity_name="Area A",
                entity_type="DrainageArea",
                metrics={
                    ComparisonMetric.PEAK_FLOW_CFS: MetricComparisonResult(
                        metric=ComparisonMetric.PEAK_FLOW_CFS,
                        baseline_value=0.0,
                        comparison_value=100.0,
                        delta=100.0,
                        percent_delta=None,
                        unit="cfs",
                    ),
                },
            ),
        ]

        totals = aggregate_totals(entities)

        peak_total = totals[ComparisonMetric.PEAK_FLOW_CFS]
        assert peak_total.baseline_total == 0.0
        assert peak_total.comparison_total == 100.0
        assert peak_total.percent_delta is None
        assert peak_total.percent_delta_status == PercentDeltaStatus.UNDEFINED_ZERO_BASELINE

    def test_empty_entities(self):
        """Returns empty dict for empty entities list."""
        totals = aggregate_totals([])
        assert totals == {}

    def test_entities_without_metrics(self):
        """Handles entities with no metrics."""
        entities = [
            EntityComparisonResult(
                baseline_entity_id="area-1",
                comparison_entity_id="area-1",
                entity_name="Area A",
                entity_type="DrainageArea",
                metrics={},
            ),
        ]

        totals = aggregate_totals(entities)

        assert totals == {}

    def test_includes_correct_unit(self):
        """Includes correct unit in totals."""
        entities = [
            EntityComparisonResult(
                baseline_entity_id="area-1",
                comparison_entity_id="area-1",
                entity_name="Area A",
                entity_type="DrainageArea",
                metrics={
                    ComparisonMetric.RUNOFF_VOLUME_CUFT: MetricComparisonResult(
                        metric=ComparisonMetric.RUNOFF_VOLUME_CUFT,
                        baseline_value=50000.0,
                        comparison_value=60000.0,
                        delta=10000.0,
                        percent_delta=20.0,
                        unit="cf",
                    ),
                },
            ),
        ]

        totals = aggregate_totals(entities)

        assert totals[ComparisonMetric.RUNOFF_VOLUME_CUFT].unit == "cf"
