"""Infrastructure network model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator, Union

from civil_toolbox.infrastructure.base import (
    InfrastructureCheckResult,
    InfrastructureValidationWarning,
)
from civil_toolbox.infrastructure.errors import (
    NodeNotFoundError,
    ElementNotFoundError,
    NetworkValidationError,
)
from civil_toolbox.infrastructure.nodes import InfrastructureNode
from civil_toolbox.infrastructure.pipes import Pipe
from civil_toolbox.infrastructure.inlets import Inlet
from civil_toolbox.infrastructure.culverts import Culvert
from civil_toolbox.infrastructure.channels import OpenChannel
from civil_toolbox.infrastructure.detention import DetentionFacility
from civil_toolbox.infrastructure.outlets import OutletStructure
from civil_toolbox.infrastructure.swales import Swale

NetworkElement = Union[
    Pipe, Inlet, Culvert, OpenChannel, DetentionFacility, OutletStructure, Swale
]


@dataclass
class InfrastructureNetwork:
    """A network of interconnected infrastructure elements.

    Manages nodes and elements with connectivity tracking.
    """

    id: str
    name: str
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    nodes: dict[str, InfrastructureNode] = field(default_factory=dict)
    elements: dict[str, NetworkElement] = field(default_factory=dict)

    def add_node(self, node: InfrastructureNode) -> None:
        """Add a node to the network."""
        self.nodes[node.id] = node

    def get_node(self, node_id: str) -> InfrastructureNode:
        """Get a node by ID.

        Raises:
            NodeNotFoundError: If node does not exist.
        """
        if node_id not in self.nodes:
            raise NodeNotFoundError(f"Node '{node_id}' not found in network")
        return self.nodes[node_id]

    def has_node(self, node_id: str) -> bool:
        """Check if a node exists."""
        return node_id in self.nodes

    def remove_node(self, node_id: str) -> InfrastructureNode:
        """Remove and return a node.

        Raises:
            NodeNotFoundError: If node does not exist.
        """
        if node_id not in self.nodes:
            raise NodeNotFoundError(f"Node '{node_id}' not found in network")
        return self.nodes.pop(node_id)

    def add_element(self, element: NetworkElement) -> None:
        """Add an element to the network."""
        self.elements[element.id] = element

    def get_element(self, element_id: str) -> NetworkElement:
        """Get an element by ID.

        Raises:
            ElementNotFoundError: If element does not exist.
        """
        if element_id not in self.elements:
            raise ElementNotFoundError(f"Element '{element_id}' not found in network")
        return self.elements[element_id]

    def has_element(self, element_id: str) -> bool:
        """Check if an element exists."""
        return element_id in self.elements

    def remove_element(self, element_id: str) -> NetworkElement:
        """Remove and return an element.

        Raises:
            ElementNotFoundError: If element does not exist.
        """
        if element_id not in self.elements:
            raise ElementNotFoundError(f"Element '{element_id}' not found in network")
        return self.elements.pop(element_id)

    def iter_nodes(self) -> Iterator[InfrastructureNode]:
        """Iterate over all nodes."""
        return iter(self.nodes.values())

    def iter_elements(self) -> Iterator[NetworkElement]:
        """Iterate over all elements."""
        return iter(self.elements.values())

    def iter_pipes(self) -> Iterator[Pipe]:
        """Iterate over pipe elements only."""
        for element in self.elements.values():
            if isinstance(element, Pipe):
                yield element

    def iter_inlets(self) -> Iterator[Inlet]:
        """Iterate over inlet elements only."""
        for element in self.elements.values():
            if isinstance(element, Inlet):
                yield element

    def iter_culverts(self) -> Iterator[Culvert]:
        """Iterate over culvert elements only."""
        for element in self.elements.values():
            if isinstance(element, Culvert):
                yield element

    def iter_channels(self) -> Iterator[OpenChannel]:
        """Iterate over open channel elements only."""
        for element in self.elements.values():
            if isinstance(element, OpenChannel):
                yield element

    def iter_detention(self) -> Iterator[DetentionFacility]:
        """Iterate over detention facility elements only."""
        for element in self.elements.values():
            if isinstance(element, DetentionFacility):
                yield element

    def iter_outlets(self) -> Iterator[OutletStructure]:
        """Iterate over outlet structure elements only."""
        for element in self.elements.values():
            if isinstance(element, OutletStructure):
                yield element

    def iter_swales(self) -> Iterator[Swale]:
        """Iterate over swale elements only."""
        for element in self.elements.values():
            if isinstance(element, Swale):
                yield element

    def validate(self) -> InfrastructureCheckResult:
        """Validate network connectivity and element references.

        Returns:
            InfrastructureCheckResult with warnings and errors.
        """
        warnings: list[InfrastructureValidationWarning] = []
        errors: list[str] = []

        for element in self.elements.values():
            upstream_id = getattr(element, "upstream_node_id", None)
            downstream_id = getattr(element, "downstream_node_id", None)
            node_id = getattr(element, "node_id", None)

            if upstream_id and upstream_id not in self.nodes:
                errors.append(
                    f"Element '{element.name}' references missing upstream node "
                    f"'{upstream_id}'"
                )
            if downstream_id and downstream_id not in self.nodes:
                errors.append(
                    f"Element '{element.name}' references missing downstream node "
                    f"'{downstream_id}'"
                )
            if node_id and node_id not in self.nodes:
                errors.append(
                    f"Element '{element.name}' references missing node '{node_id}'"
                )

        for node in self.nodes.values():
            connected = False
            for element in self.elements.values():
                upstream_id = getattr(element, "upstream_node_id", None)
                downstream_id = getattr(element, "downstream_node_id", None)
                element_node_id = getattr(element, "node_id", None)
                if node.id in (upstream_id, downstream_id, element_node_id):
                    connected = True
                    break
            if not connected:
                warnings.append(
                    InfrastructureValidationWarning(
                        element_id=node.id,
                        element_name=node.name,
                        warning_code="DISCONNECTED_NODE",
                        message=f"Node '{node.name}' is not connected to any elements",
                    )
                )

        return InfrastructureCheckResult(
            is_valid=len(errors) == 0,
            warnings=warnings,
            errors=errors,
        )

    def __len__(self) -> int:
        """Total count of nodes and elements."""
        return len(self.nodes) + len(self.elements)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        elements_list = []
        for element in self.elements.values():
            elem_dict = element.to_dict()
            elem_dict["_type"] = type(element).__name__
            elements_list.append(elem_dict)

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata.copy(),
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "elements": elements_list,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InfrastructureNetwork:
        """Deserialize from dictionary."""
        type_map: dict[str, type] = {
            "Pipe": Pipe,
            "Inlet": Inlet,
            "Culvert": Culvert,
            "OpenChannel": OpenChannel,
            "DetentionFacility": DetentionFacility,
            "OutletStructure": OutletStructure,
            "Swale": Swale,
        }

        nodes = {
            n["id"]: InfrastructureNode.from_dict(n) for n in data.get("nodes", [])
        }

        elements: dict[str, NetworkElement] = {}
        for elem_data in data.get("elements", []):
            elem_type = elem_data.pop("_type", None)
            if elem_type and elem_type in type_map:
                element = type_map[elem_type].from_dict(elem_data)
                elements[element.id] = element

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            metadata=data.get("metadata", {}),
            nodes=nodes,
            elements=elements,
        )
