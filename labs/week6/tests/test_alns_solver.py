"""Small deterministic end-to-end ALNS coverage."""

from dataclasses import replace

from labs.week6.src.alns.alns_solver import solve
from labs.week6.src.alns.config import Week6Config
from labs.week6.src.alns.models import (
    EVRPTWInstance,
    Node,
    NodeType,
)


def test_alns_solution_serves_each_customer_once() -> None:
    nodes = {
        "D0": Node(
            "D0", NodeType.DEPOT, 0, 0, 0, 0, 100, 0
        ),
        "C1": Node(
            "C1", NodeType.CUSTOMER, 2, 0, 1, 0, 100, 0
        ),
        "C2": Node(
            "C2", NodeType.CUSTOMER, 4, 0, 1, 0, 100, 0
        ),
        "C3": Node(
            "C3", NodeType.CUSTOMER, 6, 0, 1, 0, 100, 0
        ),
    }
    instance = EVRPTWInstance(
        name="tiny",
        nodes=nodes,
        battery_capacity=30.0,
        vehicle_capacity=10.0,
        energy_rate=1.0,
        inverse_refuel_rate=1.0,
        vehicle_speed=1.0,
    )
    base = Week6Config()
    config = replace(
        base,
        operators=replace(
            base.operators,
            removal_max=1,
            relocate_budget=0,
            two_opt_budget=0,
            local_search_probability=0.0,
        ),
        experiment=replace(
            base.experiment,
            iterations=5,
            time_limit_s=None,
            log_every=100,
        ),
    )

    result = solve(instance, config, seed=64)
    served = [
        node_id
        for route in result.best_solution.routes
        for node_id in route
        if node_id.startswith("C")
    ]

    assert result.best_evaluation.feasible
    assert sorted(served) == ["C1", "C2", "C3"]
    assert result.termination_reason == "iteration_limit"
    assert not result.time_limit_hit
    assert (
        result.improving_moves
        + result.neutral_moves
        + result.accepted_worse_moves
        == result.accepted_moves
    )
