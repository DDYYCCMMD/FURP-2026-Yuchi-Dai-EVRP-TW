"""Week 6 top-level ALNS orchestration.

Implementation steps 4-7
------------------------
1. Build and evaluate an initial solution.
2. Select one destroy and one repair operator.
3. Destroy, reinsert customers, and repair charging stations.
4. Apply bounded relocate/2-opt improvement.
5. Evaluate once through the shared evaluator.
6. Accept/reject with the feasibility-first SA rule.
7. Reward operators, update segment weights, and cool temperature.
8. Preserve and return the best feasible solution plus diagnostics.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .acceptance import (
    AcceptanceOutcome,
    acceptance_outcome,
    cool_temperature,
)
from .adaptive_weights import AdaptiveWeights
from .config import Week6Config
from .construction import build_initial_solution
from .evaluator import evaluate_solution
from .models import EVRPTWInstance, Evaluation, Solution
from .operators import (
    DestroyOperator,
    RepairOperator,
    greedy_insertion,
    random_removal,
    regret_2_insertion,
    related_removal,
    relocate_local_search,
    two_opt_local_search,
    worst_removal,
)


@dataclass(frozen=True, slots=True)
class ALNSResult:
    best_solution: Solution
    best_evaluation: Evaluation
    iterations_completed: int
    runtime_s: float
    destroy_weights: dict[str, float]
    repair_weights: dict[str, float]
    accepted_moves: int
    improving_moves: int
    neutral_moves: int
    accepted_worse_moves: int
    best_iteration: int
    termination_reason: str
    time_limit_hit: bool


def _strictly_better(
    candidate: Evaluation,
    incumbent: Evaluation,
    tolerance: float,
) -> bool:
    """Compare feasible solutions by vehicles, then distance."""

    if not candidate.feasible:
        return False
    if not incumbent.feasible:
        return True
    if candidate.vehicle_count != incumbent.vehicle_count:
        return candidate.vehicle_count < incumbent.vehicle_count
    return candidate.total_distance < incumbent.total_distance - tolerance


def solve(
    instance: EVRPTWInstance,
    config: Week6Config,
    seed: int,
) -> ALNSResult:
    """Run one reproducible ALNS solve."""

    rng = random.Random(seed)
    destroy_operators: dict[str, DestroyOperator] = {
        "random_removal": random_removal,
        "worst_removal": worst_removal,
        "related_removal": related_removal,
    }
    repair_operators: dict[str, RepairOperator] = {
        "greedy_insertion": greedy_insertion,
        "regret_2_insertion": regret_2_insertion,
    }
    destroy_weights = AdaptiveWeights(
        tuple(destroy_operators),
        config.adaptive_weights,
    )
    repair_weights = AdaptiveWeights(
        tuple(repair_operators),
        config.adaptive_weights,
    )

    started = time.perf_counter()
    current_solution = build_initial_solution(instance, config)
    current_evaluation = evaluate_solution(
        instance,
        current_solution,
        config.evaluator,
    )
    if not current_evaluation.feasible:
        raise RuntimeError(
            f"initial solution for {instance.name} is infeasible: "
            f"{current_evaluation.feasibility_key()}"
        )

    best_solution = current_solution.clone()
    best_evaluation = current_evaluation
    temperature = config.simulated_annealing.initial_temperature
    accepted_moves = 0
    improving_moves = 0
    neutral_moves = 0
    accepted_worse_moves = 0
    best_iteration = 0
    iterations_completed = 0
    segment_dirty = False
    termination_reason = "iteration_limit"
    time_limit_hit = False
    tolerance = config.evaluator.feasibility_tolerance

    for iteration in range(1, config.experiment.iterations + 1):
        elapsed = time.perf_counter() - started
        if (
            config.experiment.time_limit_s is not None
            and elapsed >= config.experiment.time_limit_s
        ):
            termination_reason = "time_limit"
            time_limit_hit = True
            break

        if config.adaptive_weights.enabled:
            destroy_name = destroy_weights.choose(rng)
            repair_name = repair_weights.choose(rng)
        else:
            destroy_name = rng.choice(tuple(destroy_operators))
            repair_name = rng.choice(tuple(repair_operators))

        partial, removed_customers = destroy_operators[destroy_name](
            instance,
            current_solution,
            rng,
            config,
        )
        candidate_solution = repair_operators[repair_name](
            instance,
            partial,
            removed_customers,
            rng,
            config,
        )

        reward = config.adaptive_weights.reward_rejected
        if candidate_solution is not None:
            if (
                config.operators.local_search_probability > 0
                and rng.random()
                < config.operators.local_search_probability
            ):
                candidate_solution = relocate_local_search(
                    instance,
                    candidate_solution,
                    config,
                )
                candidate_solution = two_opt_local_search(
                    instance,
                    candidate_solution,
                    config,
                )

            candidate_evaluation = evaluate_solution(
                instance,
                candidate_solution,
                config.evaluator,
            )
            previous_evaluation = current_evaluation
            outcome = acceptance_outcome(
                previous_evaluation,
                candidate_evaluation,
                temperature,
                rng,
                config.simulated_annealing,
                distance_tolerance=tolerance,
            )
            is_new_best = _strictly_better(
                candidate_evaluation,
                best_evaluation,
                tolerance,
            )

            if outcome.accepted:
                accepted_moves += 1
                if outcome is AcceptanceOutcome.IMPROVING:
                    improving_moves += 1
                elif outcome is AcceptanceOutcome.NEUTRAL:
                    neutral_moves += 1
                elif outcome is AcceptanceOutcome.WORSE_ACCEPTED:
                    accepted_worse_moves += 1
                current_solution = candidate_solution
                current_evaluation = candidate_evaluation

            if is_new_best:
                best_solution = candidate_solution.clone()
                best_evaluation = candidate_evaluation
                best_iteration = iteration
                reward = config.adaptive_weights.reward_new_best
            elif outcome is AcceptanceOutcome.IMPROVING:
                reward = config.adaptive_weights.reward_improved
            elif outcome is AcceptanceOutcome.WORSE_ACCEPTED:
                reward = config.adaptive_weights.reward_accepted
            elif outcome is AcceptanceOutcome.NEUTRAL:
                reward = config.adaptive_weights.reward_neutral

        destroy_weights.record(destroy_name, reward)
        repair_weights.record(repair_name, reward)
        segment_dirty = True
        iterations_completed = iteration
        temperature = cool_temperature(
            temperature,
            config.simulated_annealing,
        )

        if (
            config.adaptive_weights.enabled
            and iteration % config.adaptive_weights.segment_length == 0
        ):
            destroy_weights.update_segment()
            repair_weights.update_segment()
            segment_dirty = False

        if iteration % config.experiment.log_every == 0:
            print(
                f"  iter={iteration} "
                f"best=({best_evaluation.vehicle_count}, "
                f"{best_evaluation.total_distance:.3f}) "
                f"current=({current_evaluation.vehicle_count}, "
                f"{current_evaluation.total_distance:.3f}) "
                f"T={temperature:.4f}"
            )

    if config.adaptive_weights.enabled and segment_dirty:
        destroy_weights.update_segment()
        repair_weights.update_segment()

    runtime_s = time.perf_counter() - started
    return ALNSResult(
        best_solution=best_solution,
        best_evaluation=best_evaluation,
        iterations_completed=iterations_completed,
        runtime_s=runtime_s,
        destroy_weights=destroy_weights.weights.copy(),
        repair_weights=repair_weights.weights.copy(),
        accepted_moves=accepted_moves,
        improving_moves=improving_moves,
        neutral_moves=neutral_moves,
        accepted_worse_moves=accepted_worse_moves,
        best_iteration=best_iteration,
        termination_reason=termination_reason,
        time_limit_hit=time_limit_hit,
    )
