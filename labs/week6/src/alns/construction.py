"""Week 6 initial-solution construction for full-recharge EVRPTW.

Implementation step 3
---------------------
1. Start with all customers unassigned.
2. Evaluate every insertion position in the current routes.
3. Choose the feasible insertion with the smallest distance increase.
4. Open a new depot-customer-depot route if no insertion is feasible.
5. Invoke charging repair whenever an insertion is battery-infeasible.
"""

from __future__ import annotations

from .charging_repair import repair_charging_stations
from .config import Week6Config
from .models import EVRPTWInstance, Solution
from .solution_utils import (
    partial_objective,
    partial_solution_is_feasible,
    strip_stations,
)


def build_initial_solution(
    instance: EVRPTWInstance,
    config: Week6Config,
) -> Solution:
    """Construct one customer-complete starting solution."""

    depot_id = instance.depot_id
    ordered_customers = sorted(
        instance.customer_ids,
        key=lambda node_id: (
            instance.nodes[node_id].due_time,
            instance.nodes[node_id].ready_time,
            node_id,
        ),
    )
    current = Solution(routes=[])

    for customer_id in ordered_customers:
        stationless = strip_stations(instance, current)
        candidates: list[tuple[tuple[int, float], Solution]] = []

        for route_index, route in enumerate(stationless.routes):
            for insertion_index in range(1, len(route)):
                candidate = stationless.clone()
                candidate.routes[route_index].insert(
                    insertion_index,
                    customer_id,
                )
                repaired = repair_charging_stations(
                    instance,
                    candidate,
                    config,
                )
                if repaired is None or not partial_solution_is_feasible(
                    instance,
                    repaired,
                    config.evaluator,
                ):
                    continue
                candidates.append(
                    (
                        partial_objective(
                            instance,
                            repaired,
                            config.evaluator,
                        ),
                        repaired,
                    )
                )

        new_route_candidate = stationless.clone()
        new_route_candidate.routes.append(
            [depot_id, customer_id, depot_id]
        )
        repaired_new_route = repair_charging_stations(
            instance,
            new_route_candidate,
            config,
        )
        if (
            repaired_new_route is not None
            and partial_solution_is_feasible(
                instance,
                repaired_new_route,
                config.evaluator,
            )
        ):
            candidates.append(
                (
                    partial_objective(
                        instance,
                        repaired_new_route,
                        config.evaluator,
                    ),
                    repaired_new_route,
                )
            )

        if not candidates:
            raise RuntimeError(
                f"could not construct a feasible route for {customer_id} "
                f"in instance {instance.name}"
            )
        _, current = min(candidates, key=lambda item: item[0])

    return current
