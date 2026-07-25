"""Week 6 greedy full-recharge station insertion.

Implementation step 5
---------------------
1. Find the first arc whose arrival battery is negative.
2. Test each station between the arc endpoints.
3. If none works, inspect earlier arcs before the failing customer.
4. Choose the feasible insertion with minimum added distance.
5. Re-run the complete evaluator because charging may delay later customers.
6. Stop after the configured insertion budget to prevent repair cycles.
"""

from __future__ import annotations

from .config import Week6Config
from .evaluator import evaluate_route
from .models import EVRPTWInstance, Solution
from .solution_utils import (
    partial_solution_is_feasible,
    strip_stations,
)


def repair_charging_stations(
    instance: EVRPTWInstance,
    solution: Solution,
    config: Week6Config,
) -> Solution | None:
    """Return a repaired clone, or ``None`` when no feasible repair exists."""

    if not config.evaluator.battery_constraints_enabled:
        stationless = strip_stations(instance, solution)
        return (
            stationless
            if partial_solution_is_feasible(
                instance,
                stationless,
                config.evaluator,
            )
            else None
        )

    repaired = solution.clone()
    tolerance = config.evaluator.feasibility_tolerance

    for _ in range(config.operators.station_repair_max_insertions + 1):
        failure: tuple[int, int] | None = None
        for route_index, route in enumerate(repaired.routes):
            metrics = evaluate_route(instance, route, config.evaluator)
            if (
                metrics.route_structure_violation
                or metrics.capacity_violation > tolerance
                or metrics.time_window_violation > tolerance
            ):
                return None
            if metrics.first_energy_failure_index is not None:
                failure = (
                    route_index,
                    metrics.first_energy_failure_index,
                )
                break

        if failure is None:
            return (
                repaired
                if partial_solution_is_feasible(
                    instance,
                    repaired,
                    config.evaluator,
                )
                else None
            )

        route_index, failure_index = failure
        route = repaired.routes[route_index]
        original_distance = evaluate_route(
            instance,
            route,
            config.evaluator,
        ).total_distance
        best_route: list[str] | None = None
        best_score: tuple[float, float] | None = None

        # GSI first tries the failing arc, then progressively earlier arcs.
        for insertion_index in range(failure_index, 0, -1):
            predecessor = route[insertion_index - 1]
            successor = route[insertion_index]
            for station_id in instance.station_ids:
                if station_id in {predecessor, successor}:
                    continue

                candidate_route = (
                    route[:insertion_index]
                    + [station_id]
                    + route[insertion_index:]
                )
                metrics = evaluate_route(
                    instance,
                    candidate_route,
                    config.evaluator,
                )
                if (
                    metrics.route_structure_violation
                    or metrics.capacity_violation > tolerance
                    or metrics.time_window_violation > tolerance
                ):
                    continue

                # The inserted station must be reachable and must resolve the
                # original failing prefix. A later failure can be repaired by
                # the next outer iteration.
                if (
                    metrics.first_energy_failure_index is not None
                    and metrics.first_energy_failure_index
                    <= failure_index + 1
                ):
                    continue

                score = (
                    metrics.total_distance - original_distance,
                    metrics.total_charging_time,
                )
                if best_score is None or score < best_score:
                    best_score = score
                    best_route = candidate_route

        if best_route is None:
            return None
        repaired.routes[route_index] = best_route

    return None
