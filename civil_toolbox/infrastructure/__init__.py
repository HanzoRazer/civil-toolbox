"""Infrastructure modeling for Civil Toolbox.

Provides data models for drainage infrastructure elements including pipes,
culverts, channels, inlets, detention facilities, and outlet structures.

Example:
    >>> from civil_toolbox.infrastructure import (
    ...     Pipe,
    ...     InfrastructureNode,
    ...     InfrastructureNetwork,
    ...     create_example_network,
    ... )
    >>> network = create_example_network()
    >>> for pipe in network.iter_pipes():
    ...     print(f"{pipe.name}: {pipe.diameter_in}in")
"""

from civil_toolbox.infrastructure.base import (
    ElementType,
    InfrastructureCheckResult,
    InfrastructureElementBase,
    InfrastructureValidationWarning,
)
from civil_toolbox.infrastructure.channels import OpenChannel
from civil_toolbox.infrastructure.culverts import Culvert
from civil_toolbox.infrastructure.detention import (
    DetentionFacility,
    StageStoragePoint,
)
from civil_toolbox.infrastructure.errors import (
    ElementNotFoundError,
    InfrastructureError,
    InfrastructureValidationError,
    InvalidInfrastructureError,
    NetworkValidationError,
    NodeNotFoundError,
)
from civil_toolbox.infrastructure.examples import (
    create_example_box_culvert,
    create_example_channel,
    create_example_detention,
    create_example_inlet,
    create_example_network,
    create_example_node,
    create_example_outlet,
    create_example_pipe,
    create_example_swale,
)
from civil_toolbox.infrastructure.inlets import Inlet
from civil_toolbox.infrastructure.networks import InfrastructureNetwork, NetworkElement
from civil_toolbox.infrastructure.nodes import InfrastructureNode
from civil_toolbox.infrastructure.outlets import OutletStructure
from civil_toolbox.infrastructure.pipes import Pipe
from civil_toolbox.infrastructure.schedules import (
    InfrastructureSchedule,
    InfrastructureScheduleRow,
)
from civil_toolbox.infrastructure.swales import Swale
from civil_toolbox.infrastructure.validation import (
    validate_channel_shape,
    validate_inlet_type,
    validate_mannings_n,
    validate_non_negative,
    validate_outlet_type,
    validate_pipe_shape,
    validate_positive,
    validate_slope,
)

__all__ = [
    # Base
    "ElementType",
    "InfrastructureElementBase",
    "InfrastructureCheckResult",
    "InfrastructureValidationWarning",
    # Elements
    "InfrastructureNode",
    "Pipe",
    "Inlet",
    "Culvert",
    "OpenChannel",
    "DetentionFacility",
    "StageStoragePoint",
    "OutletStructure",
    "Swale",
    # Network
    "InfrastructureNetwork",
    "NetworkElement",
    # Schedules
    "InfrastructureSchedule",
    "InfrastructureScheduleRow",
    # Errors
    "InfrastructureError",
    "InvalidInfrastructureError",
    "InfrastructureValidationError",
    "NodeNotFoundError",
    "ElementNotFoundError",
    "NetworkValidationError",
    # Validation
    "validate_positive",
    "validate_non_negative",
    "validate_mannings_n",
    "validate_slope",
    "validate_pipe_shape",
    "validate_inlet_type",
    "validate_channel_shape",
    "validate_outlet_type",
    # Examples
    "create_example_node",
    "create_example_pipe",
    "create_example_box_culvert",
    "create_example_inlet",
    "create_example_channel",
    "create_example_detention",
    "create_example_outlet",
    "create_example_swale",
    "create_example_network",
]
