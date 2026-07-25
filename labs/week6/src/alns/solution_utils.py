"""Small, dependency-free helpers shared by Week 6 operators."""

from __future__ import annotations

from .config import EvaluatorConfig
from .evaluator import evaluate_route
from .models import EVRPTWInstance, NodeType, Solution


def strip_stations(
    instance: EVRPTWInstance,
    solution: Solution,
) -> Solution:
    """Remove station visits while preserving depot/customer order."""

    return Solution(
        routes=[
            [
                node_id
                for node_id in route
                if node_id in instance.nodes
                and instance.nodes[node_id].node_type is not NodeType.STATION
            ]
            for route in solution.routes
        ]
    )


def remove_empty_routes(
    instance: EVRPTWInstance,
    solution: Solution,
) -> Solution:
    """Drop routes containing no customers."""

    routes = []
    for route in solution.routes:
        has_customer = any(
            node_id in instance.nodes
            and instance.nodes[node_id].node_type is NodeType.CUSTOMER
            for node_id in route
        )
        if has_customer:
            routes.append(route.copy())
    return Solution(routes=routes)


def partial_solution_is_feasible(
    instance: EVRPTWInstance,
    solution: Solution,
    config: EvaluatorConfig,
) -> bool:
    """Check every present route without enforcing global customer coverage."""

    return all(
        evaluate_route(instance, route, config).feasible
        for route in solution.routes
    )


def partial_objective(
    instance: EVRPTWInstance,
    solution: Solution,
    config: EvaluatorConfig,
) -> tuple[int, float]:
    """Vehicle/distance objective for a partial or complete solution."""

    metrics = [
        evaluate_route(instance, route, config) for route in solution.routes
    ]
    return (
        len(solution.routes),
        sum(metric.total_distance for metric in metrics),
    )

