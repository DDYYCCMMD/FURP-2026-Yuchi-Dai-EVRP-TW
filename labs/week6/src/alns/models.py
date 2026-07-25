"""Shared data structures for the ``labs/week6`` ALNS implementation.

Step 1: load a raw Schneider instance into ``EVRPTWInstance``.
Step 2: represent each candidate as ``Solution.routes``.
Step 3: return every constraint metric in one ``Evaluation`` object.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import hypot


class NodeType(str, Enum):
    DEPOT = "d"
    STATION = "f"
    CUSTOMER = "c"


@dataclass(frozen=True, slots=True)
class Node:
    node_id: str
    node_type: NodeType
    x: float
    y: float
    demand: float
    ready_time: float
    due_time: float
    service_time: float


@dataclass(frozen=True, slots=True)
class EVRPTWInstance:
    """One benchmark instance in its original physical units."""

    name: str
    nodes: dict[str, Node]
    battery_capacity: float
    vehicle_capacity: float
    energy_rate: float
    inverse_refuel_rate: float
    vehicle_speed: float

    def __post_init__(self) -> None:
        if self.battery_capacity <= 0:
            raise ValueError("battery_capacity must be positive")
        if self.vehicle_capacity <= 0:
            raise ValueError("vehicle_capacity must be positive")
        if self.energy_rate <= 0:
            raise ValueError("energy_rate must be positive")
        if self.inverse_refuel_rate < 0:
            raise ValueError("inverse_refuel_rate cannot be negative")
        if self.vehicle_speed <= 0:
            raise ValueError("vehicle_speed must be positive")
        if any(key != node.node_id for key, node in self.nodes.items()):
            raise ValueError("node dictionary keys must match node_id values")

    @property
    def depot_id(self) -> str:
        depots = [
            node.node_id
            for node in self.nodes.values()
            if node.node_type is NodeType.DEPOT
        ]
        if len(depots) != 1:
            raise ValueError(f"{self.name} must contain exactly one depot")
        return depots[0]

    @property
    def customer_ids(self) -> tuple[str, ...]:
        return tuple(
            node.node_id
            for node in self.nodes.values()
            if node.node_type is NodeType.CUSTOMER
        )

    @property
    def station_ids(self) -> tuple[str, ...]:
        return tuple(
            node.node_id
            for node in self.nodes.values()
            if node.node_type is NodeType.STATION
        )

    def distance(self, source_id: str, target_id: str) -> float:
        source = self.nodes[source_id]
        target = self.nodes[target_id]
        return hypot(source.x - target.x, source.y - target.y)


@dataclass(slots=True)
class Solution:
    """Vehicle routes, each explicitly starting and ending at the depot."""

    routes: list[list[str]]

    def clone(self) -> "Solution":
        return Solution(routes=[route.copy() for route in self.routes])


@dataclass(frozen=True, slots=True)
class RouteEvaluation:
    """State-propagation metrics for one explicit vehicle route."""

    total_distance: float = 0.0
    total_travel_time: float = 0.0
    total_waiting_time: float = 0.0
    total_charging_time: float = 0.0
    station_visits: int = 0
    capacity_violation: float = 0.0
    time_window_violation: float = 0.0
    energy_violation: float = 0.0
    late_customer_count: int = 0
    minimum_battery: float = 0.0
    first_energy_failure_index: int | None = None
    route_structure_violation: bool = False
    feasible: bool = False


@dataclass(frozen=True, slots=True)
class Evaluation:
    """Complete evaluator output used by every ALNS decision."""

    total_distance: float = 0.0
    total_travel_time: float = 0.0
    total_waiting_time: float = 0.0
    total_charging_time: float = 0.0
    vehicle_count: int = 0
    station_visits: int = 0
    capacity_violation: float = 0.0
    time_window_violation: float = 0.0
    energy_violation: float = 0.0
    late_customer_count: int = 0
    minimum_battery: float = 0.0
    missing_customers: tuple[str, ...] = field(default_factory=tuple)
    duplicate_customers: tuple[str, ...] = field(default_factory=tuple)
    route_structure_violation: bool = False
    feasible: bool = False

    def feasibility_key(self) -> tuple[float | int | bool, ...]:
        """Lexicographic key: feasibility first, vehicles then distance."""

        return (
            len(self.missing_customers) + len(self.duplicate_customers),
            self.route_structure_violation,
            self.capacity_violation,
            self.energy_violation,
            self.time_window_violation,
            self.vehicle_count,
            self.total_distance,
        )

    def objective_key(self) -> tuple[int, float]:
        """Schneider objective: number of vehicles, then total distance."""

        return (self.vehicle_count, self.total_distance)
