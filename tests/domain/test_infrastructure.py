"""Tests for InfrastructureElement domain entity."""

import pytest

from civil_toolbox.domain.infrastructure import InfrastructureElement


class TestInfrastructureElement:
    """Tests for InfrastructureElement."""

    def test_creates_with_name(self):
        element = InfrastructureElement(name="Pipe 1")
        assert element.name == "Pipe 1"
        assert element.id is not None
        assert element.element_type == "pipe"

    def test_raises_on_missing_name(self):
        with pytest.raises(ValueError, match="requires a name"):
            InfrastructureElement(name="")

    def test_valid_element_types(self):
        valid_types = ("pipe", "culvert", "channel", "inlet", "detention", "outlet")
        for elem_type in valid_types:
            element = InfrastructureElement(name="Test", element_type=elem_type)
            assert element.element_type == elem_type

    def test_raises_on_invalid_element_type(self):
        with pytest.raises(ValueError, match="element_type must be one of"):
            InfrastructureElement(name="Test", element_type="invalid")

    def test_creates_pipe_with_properties(self):
        pipe = InfrastructureElement(
            name="Storm Drain",
            element_type="pipe",
            length_ft=500.0,
            slope_ft_per_ft=0.005,
            diameter_in=24.0,
            material="RCP",
            mannings_n=0.013,
        )
        assert pipe.length_ft == 500.0
        assert pipe.diameter_in == 24.0
        assert pipe.material == "RCP"
        assert pipe.mannings_n == 0.013

    def test_creates_channel_with_properties(self):
        channel = InfrastructureElement(
            name="Outfall Channel",
            element_type="channel",
            length_ft=1000.0,
            slope_ft_per_ft=0.002,
            bottom_width_ft=10.0,
            side_slope=2.0,
            depth_ft=3.0,
            mannings_n=0.035,
        )
        assert channel.bottom_width_ft == 10.0
        assert channel.side_slope == 2.0
        assert channel.depth_ft == 3.0

    def test_creates_with_capacity(self):
        element = InfrastructureElement(
            name="Test",
            capacity_cfs=150.0,
        )
        assert element.capacity_cfs == 150.0

    def test_raises_on_negative_length(self):
        with pytest.raises(ValueError, match="length_ft cannot be negative"):
            InfrastructureElement(name="Test", length_ft=-100)

    def test_raises_on_negative_slope(self):
        with pytest.raises(ValueError, match="slope_ft_per_ft cannot be negative"):
            InfrastructureElement(name="Test", slope_ft_per_ft=-0.01)

    def test_raises_on_non_positive_diameter(self):
        with pytest.raises(ValueError, match="diameter_in must be positive"):
            InfrastructureElement(name="Test", diameter_in=0)
        with pytest.raises(ValueError, match="diameter_in must be positive"):
            InfrastructureElement(name="Test", diameter_in=-12)

    def test_raises_on_non_positive_mannings_n(self):
        with pytest.raises(ValueError, match="mannings_n must be positive"):
            InfrastructureElement(name="Test", mannings_n=0)

    def test_to_dict_serialization(self):
        element = InfrastructureElement(
            name="Serialize Test",
            element_type="culvert",
            length_ft=100.0,
            diameter_in=36.0,
        )
        data = element.to_dict()
        assert data["name"] == "Serialize Test"
        assert data["element_type"] == "culvert"
        assert data["diameter_in"] == 36.0

    def test_from_dict_deserialization(self):
        data = {
            "id": "elem-123",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-02T00:00:00",
            "name": "Restored Element",
            "element_type": "detention",
            "length_ft": None,
            "capacity_cfs": 500.0,
        }
        element = InfrastructureElement.from_dict(data)
        assert element.id == "elem-123"
        assert element.name == "Restored Element"
        assert element.element_type == "detention"
        assert element.capacity_cfs == 500.0

    def test_round_trip_serialization(self):
        element = InfrastructureElement(
            name="Round Trip Pipe",
            element_type="pipe",
            length_ft=250.0,
            slope_ft_per_ft=0.008,
            diameter_in=18.0,
            material="HDPE",
            mannings_n=0.012,
            capacity_cfs=45.0,
        )
        data = element.to_dict()
        restored = InfrastructureElement.from_dict(data)
        assert restored.id == element.id
        assert restored.name == element.name
        assert restored.element_type == element.element_type
        assert restored.diameter_in == element.diameter_in
        assert restored.mannings_n == element.mannings_n
        assert restored.capacity_cfs == element.capacity_cfs
