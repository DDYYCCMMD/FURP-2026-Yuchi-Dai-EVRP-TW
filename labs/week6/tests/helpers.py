"""Hand-built instances used by Week 6 unit tests."""

from labs.week6.src.alns.models import (
    EVRPTWInstance,
    Node,
    NodeType,
)


def line_instance(
    *,
    battery_capacity: float = 20.0,
    depot_due_time: float = 100.0,
    customer_due_time: float = 100.0,
    include_station: bool = True,
    inverse_refuel_rate: float = 1.0,
) -> EVRPTWInstance:
    nodes = {
        "D0": Node(
            "D0",
            NodeType.DEPOT,
            0.0,
            0.0,
            0.0,
            0.0,
            depot_due_time,
            0.0,
        ),
        "C1": Node(
            "C1",
            NodeType.CUSTOMER,
            10.0,
            0.0,
            1.0,
            0.0,
            customer_due_time,
            0.0,
        ),
    }
    if include_station:
        nodes["S1"] = Node(
            "S1",
            NodeType.STATION,
            5.0,
            0.0,
            0.0,
            0.0,
            depot_due_time,
            0.0,
        )
    return EVRPTWInstance(
        name="line",
        nodes=nodes,
        battery_capacity=battery_capacity,
        vehicle_capacity=10.0,
        energy_rate=1.0,
        inverse_refuel_rate=inverse_refuel_rate,
        vehicle_speed=1.0,
    )

