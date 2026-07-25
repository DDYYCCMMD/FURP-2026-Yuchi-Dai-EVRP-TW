"""Week 6 destroy, repair, and local-search operators.

Implementation steps 4 and 6
----------------------------
Minimum operator set:
    random removal + greedy insertion + relocate + 2-opt

Adaptive extension:
    worst/related removal + regret-2 insertion

Every repair/local-search candidate must be checked by the unified evaluator.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from math import ceil

from .charging_repair import repair_charging_stations
from .config import Week6Config
from .evaluator import evaluate_solution
from .models import EVRPTWInstance, NodeType, Solution
from .solution_utils import (
    partial_objective,
    partial_solution_is_feasible,
    remove_empty_routes,
    strip_stations,
)


DestroyOperator = Callable[
    [EVRPTWInstance, Solution, random.Random, Week6Config],
    tuple[Solution, list[str]],
]
RepairOperator = Callable[
    [EVRPTWInstance, Solution, list[str], random.Random, Week6Config],
    Solution | None,
]


def _removal_count(
    customer_count: int,
    config: Week6Config,
) -> int:
    requested = ceil(
        customer_count * config.operators.removal_fraction
    )
    return min(
        customer_count,
        config.operators.removal_max,
        max(config.operators.removal_min, requested),
    )


def _customer_positions(
    instance: EVRPTWInstance,
    solution: Solution,
) -> list[tuple[int, int, str]]:
    return [
        (route_index, node_index, node_id)
        for route_index, route in enumerate(solution.routes)
        for node_index, node_id in enumerate(route)
        if instance.nodes[node_id].node_type is NodeType.CUSTOMER
    ]


def _remove_selected(
    instance: EVRPTWInstance,
    solution: Solution,
    selected: list[str],
) -> tuple[Solution, list[str]]:
    selected_set = set(selected)
    partial = strip_stations(instance, solution)
    partial.routes = [
        [
            node_id
            for node_id in route
            if node_id not in selected_set
        ]
        for route in partial.routes
    ]
    return remove_empty_routes(instance, partial), selected.copy()


def _route_open_penalty(instance: EVRPTWInstance) -> float:
    node_ids = tuple(instance.nodes)
    maximum_distance = max(
        (
            instance.distance(source_id, target_id)
            for source_id in node_ids
            for target_id in node_ids
        ),
        default=1.0,
    )
    return maximum_distance * (len(instance.customer_ids) + 2)


def _insertion_options(
    instance: EVRPTWInstance,
    partial: Solution,
    customer_id: str,
    config: Week6Config,
) -> list[tuple[float, Solution]]:
    """Return feasible options as scalarised vehicle-first costs."""

    depot_id = instance.depot_id
    base = remove_empty_routes(
        instance,
        strip_stations(instance, partial),
    )
    raw_candidates: list[Solution] = []

    for route_index, route in enumerate(base.routes):
        for insertion_index in range(1, len(route)):
            candidate = base.clone()
            candidate.routes[route_index].insert(
                insertion_index,
                customer_id,
            )
            raw_candidates.append(candidate)

    new_route = base.clone()
    new_route.routes.append([depot_id, customer_id, depot_id])
    raw_candidates.append(new_route)

    penalty = _route_open_penalty(instance)
    options: list[tuple[float, Solution]] = []
    for candidate in raw_candidates:
        repaired = repair_charging_stations(instance, candidate, config)
        if repaired is None or not partial_solution_is_feasible(
            instance,
            repaired,
            config.evaluator,
        ):
            continue
        vehicles, distance = partial_objective(
            instance,
            repaired,
            config.evaluator,
        )
        options.append((vehicles * penalty + distance, repaired))
    options.sort(key=lambda item: item[0])
    return options


def random_removal(
    instance: EVRPTWInstance,
    solution: Solution,
    rng: random.Random,
    config: Week6Config,
) -> tuple[Solution, list[str]]:
    """Remove a bounded random sample of customers from a cloned solution."""

    customers = [
        customer_id
        for _, _, customer_id in _customer_positions(instance, solution)
    ]
    count = _removal_count(len(customers), config)
    selected = rng.sample(customers, count) if count else []
    return _remove_selected(instance, solution, selected)


def worst_removal(
    instance: EVRPTWInstance,
    solution: Solution,
    rng: random.Random,
    config: Week6Config,
) -> tuple[Solution, list[str]]:
    """Remove customers with the largest direct distance-saving potential."""

    stationless = strip_stations(instance, solution)
    savings: list[tuple[float, float, str]] = []
    for route in stationless.routes:
        for node_index in range(1, len(route) - 1):
            customer_id = route[node_index]
            if instance.nodes[customer_id].node_type is not NodeType.CUSTOMER:
                continue
            predecessor = route[node_index - 1]
            successor = route[node_index + 1]
            saving = (
                instance.distance(predecessor, customer_id)
                + instance.distance(customer_id, successor)
                - instance.distance(predecessor, successor)
            )
            savings.append((saving, rng.random(), customer_id))

    count = _removal_count(len(savings), config)
    savings.sort(reverse=True)
    selected = [customer_id for _, _, customer_id in savings[:count]]
    return _remove_selected(instance, solution, selected)


def related_removal(
    instance: EVRPTWInstance,
    solution: Solution,
    rng: random.Random,
    config: Week6Config,
) -> tuple[Solution, list[str]]:
    """Remove a spatially and temporally related customer neighbourhood."""

    customers = [
        customer_id
        for _, _, customer_id in _customer_positions(instance, solution)
    ]
    count = _removal_count(len(customers), config)
    if not customers or not count:
        return solution.clone(), []

    seed_id = rng.choice(customers)
    seed = instance.nodes[seed_id]
    related = []
    for customer_id in customers:
        if customer_id == seed_id:
            continue
        customer = instance.nodes[customer_id]
        score = (
            instance.distance(seed_id, customer_id)
            + abs(seed.ready_time - customer.ready_time)
            + abs(seed.due_time - customer.due_time)
        )
        related.append((score, rng.random(), customer_id))
    related.sort()
    selected = [seed_id] + [
        customer_id for _, _, customer_id in related[: count - 1]
    ]
    return _remove_selected(instance, solution, selected)


def greedy_insertion(
    instance: EVRPTWInstance,
    partial: Solution,
    removed_customers: list[str],
    rng: random.Random,
    config: Week6Config,
) -> Solution | None:
    """Reinsert customers at minimum-cost feasible positions."""

    current = partial.clone()
    remaining = removed_customers.copy()

    while remaining:
        choices: list[tuple[float, float, str, Solution]] = []
        for customer_id in remaining:
            options = _insertion_options(
                instance,
                current,
                customer_id,
                config,
            )
            if options:
                cost, candidate = options[0]
                choices.append(
                    (cost, rng.random(), customer_id, candidate)
                )
        if not choices:
            return None
        _, _, inserted_customer, current = min(choices)
        remaining.remove(inserted_customer)

    return current


def regret_2_insertion(
    instance: EVRPTWInstance,
    partial: Solution,
    removed_customers: list[str],
    rng: random.Random,
    config: Week6Config,
) -> Solution | None:
    """Prioritise the customer with the largest second-best insertion regret."""

    current = partial.clone()
    remaining = removed_customers.copy()
    fallback_regret = _route_open_penalty(instance)

    while remaining:
        choices: list[tuple[float, float, str, Solution]] = []
        for customer_id in remaining:
            options = _insertion_options(
                instance,
                current,
                customer_id,
                config,
            )
            if not options:
                continue
            best_cost, best_candidate = options[0]
            comparison_index = min(
                config.operators.regret_k - 1,
                len(options) - 1,
            )
            regret = (
                options[comparison_index][0] - best_cost
                if len(options) > 1
                else fallback_regret
            )
            choices.append(
                (
                    -regret,
                    rng.random(),
                    customer_id,
                    best_candidate,
                )
            )
        if not choices:
            return None
        _, _, inserted_customer, current = min(choices)
        remaining.remove(inserted_customer)

    return current


def relocate_local_search(
    instance: EVRPTWInstance,
    solution: Solution,
    config: Week6Config,
) -> Solution:
    """Apply improving customer relocations within the configured budget."""

    current = solution.clone()
    current_evaluation = evaluate_solution(
        instance,
        current,
        config.evaluator,
    )
    if not current_evaluation.feasible:
        return current

    for _ in range(config.operators.relocate_budget):
        stationless = strip_stations(instance, current)
        best_solution: Solution | None = None
        best_evaluation = current_evaluation

        for _, _, customer_id in _customer_positions(
            instance,
            stationless,
        ):
            partial, _ = _remove_selected(
                instance,
                stationless,
                [customer_id],
            )
            for _, candidate in _insertion_options(
                instance,
                partial,
                customer_id,
                config,
            ):
                candidate_evaluation = evaluate_solution(
                    instance,
                    candidate,
                    config.evaluator,
                )
                if (
                    candidate_evaluation.feasible
                    and candidate_evaluation.objective_key()
                    < best_evaluation.objective_key()
                ):
                    best_solution = candidate
                    best_evaluation = candidate_evaluation

        if best_solution is None:
            break
        current = best_solution
        current_evaluation = best_evaluation

    return current


def two_opt_local_search(
    instance: EVRPTWInstance,
    solution: Solution,
    config: Week6Config,
) -> Solution:
    """Apply improving intra-route segment reversals."""

    current = solution.clone()
    current_evaluation = evaluate_solution(
        instance,
        current,
        config.evaluator,
    )
    if not current_evaluation.feasible:
        return current

    for _ in range(config.operators.two_opt_budget):
        stationless = strip_stations(instance, current)
        best_solution: Solution | None = None
        best_evaluation = current_evaluation

        for route_index, route in enumerate(stationless.routes):
            for start in range(1, len(route) - 2):
                for end in range(start + 1, len(route) - 1):
                    candidate = stationless.clone()
                    candidate.routes[route_index][start : end + 1] = reversed(
                        candidate.routes[route_index][start : end + 1]
                    )
                    repaired = repair_charging_stations(
                        instance,
                        candidate,
                        config,
                    )
                    if repaired is None:
                        continue
                    candidate_evaluation = evaluate_solution(
                        instance,
                        repaired,
                        config.evaluator,
                    )
                    if (
                        candidate_evaluation.feasible
                        and candidate_evaluation.objective_key()
                        < best_evaluation.objective_key()
                    ):
                        best_solution = repaired
                        best_evaluation = candidate_evaluation

        if best_solution is None:
            break
        current = best_solution
        current_evaluation = best_evaluation

    return current
