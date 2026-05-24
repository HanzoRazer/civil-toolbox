"""Tests for infrastructure schedules."""

import pytest

from civil_toolbox.infrastructure import (
    InfrastructureSchedule,
    InfrastructureScheduleRow,
)


class TestInfrastructureScheduleRow:
    """Tests for InfrastructureScheduleRow."""

    def test_basic_creation(self):
        """Create a basic schedule row."""
        row = InfrastructureScheduleRow(
            element_id="p1",
            element_name="P-1",
            element_type="pipe",
            size="18\" RCP",
            length_ft=200.0,
        )
        assert row.element_id == "p1"
        assert row.element_name == "P-1"
        assert row.size == "18\" RCP"
        assert row.length_ft == 200.0

    def test_optional_fields(self):
        """Optional fields default to None."""
        row = InfrastructureScheduleRow(
            element_id="p1",
            element_name="P-1",
            element_type="pipe",
        )
        assert row.station is None
        assert row.material is None
        assert row.capacity_cfs is None

    def test_serialization_roundtrip(self):
        """to_dict/from_dict roundtrip preserves data."""
        original = InfrastructureScheduleRow(
            element_id="p1",
            element_name="P-1",
            element_type="pipe",
            station="10+00",
            description="Storm drain",
            size="18\" RCP",
            material="RCP",
            length_ft=200.0,
            slope_percent=0.5,
            invert_in_ft=95.0,
            invert_out_ft=94.0,
            capacity_cfs=15.5,
            velocity_fps=5.2,
            notes="Test pipe",
            metadata={"test": True},
        )
        restored = InfrastructureScheduleRow.from_dict(original.to_dict())
        assert restored.element_id == original.element_id
        assert restored.size == original.size
        assert restored.slope_percent == original.slope_percent
        assert restored.capacity_cfs == original.capacity_cfs


class TestInfrastructureSchedule:
    """Tests for InfrastructureSchedule."""

    def test_basic_creation(self):
        """Create a basic schedule."""
        schedule = InfrastructureSchedule(
            name="Pipe Schedule",
            schedule_type="pipe",
        )
        assert schedule.name == "Pipe Schedule"
        assert schedule.schedule_type == "pipe"
        assert len(schedule) == 0

    def test_add_row(self):
        """Add rows to schedule."""
        schedule = InfrastructureSchedule(
            name="Pipe Schedule",
            schedule_type="pipe",
        )
        row = InfrastructureScheduleRow(
            element_id="p1",
            element_name="P-1",
            element_type="pipe",
        )
        schedule.add_row(row)
        assert len(schedule) == 1

    def test_iteration(self):
        """Iterate over schedule rows."""
        schedule = InfrastructureSchedule(
            name="Pipe Schedule",
            schedule_type="pipe",
        )
        schedule.add_row(InfrastructureScheduleRow(
            element_id="p1", element_name="P-1", element_type="pipe"
        ))
        schedule.add_row(InfrastructureScheduleRow(
            element_id="p2", element_name="P-2", element_type="pipe"
        ))
        rows = list(schedule)
        assert len(rows) == 2
        assert rows[0].element_id == "p1"
        assert rows[1].element_id == "p2"

    def test_serialization_roundtrip(self):
        """to_dict/from_dict roundtrip preserves data."""
        original = InfrastructureSchedule(
            name="Pipe Schedule",
            schedule_type="pipe",
            metadata={"project": "Test"},
        )
        original.add_row(InfrastructureScheduleRow(
            element_id="p1",
            element_name="P-1",
            element_type="pipe",
            size="18\" RCP",
        ))
        original.add_row(InfrastructureScheduleRow(
            element_id="p2",
            element_name="P-2",
            element_type="pipe",
            size="24\" RCP",
        ))
        restored = InfrastructureSchedule.from_dict(original.to_dict())
        assert restored.name == original.name
        assert restored.schedule_type == original.schedule_type
        assert len(restored) == 2
        assert restored.rows[0].size == "18\" RCP"
