"""Unified evaluator coverage for capacity, time, battery, and customers."""

from dataclasses import replace

from labs.week6.src.alns.config import EvaluatorConfig
from labs.week6.src.alns.evaluator import evaluate_solution
from labs.week6.src.alns.models import Solution
from labs.week6.tests.helpers import line_instance


def test_sufficient_battery_route_is_feasible() -> None:
    instance = line_instance(
        battery_capacity=25.0,
        include_station=False,
    )
    evaluation = evaluate_solution(
        instance,
        Solution([["D0", "C1", "D0"]]),
        EvaluatorConfig(),
    )

    assert evaluation.feasible
    assert evaluation.total_distance == 20.0
    assert evaluation.minimum_battery == 5.0
    assert evaluation.energy_violation == 0.0


def test_energy_violation_is_recorded_before_recharge() -> None:
    instance = line_instance(
        battery_capacity=9.0,
        include_station=False,
    )
    evaluation = evaluate_solution(
        instance,
        Solution([["D0", "C1", "D0"]]),
        EvaluatorConfig(),
    )

    assert not evaluation.feasible
    assert evaluation.energy_violation > 0
    assert evaluation.minimum_battery < 0


def test_time_window_and_energy_are_checked_together() -> None:
    instance = line_instance(
        battery_capacity=9.0,
        customer_due_time=8.0,
        include_station=False,
    )
    evaluation = evaluate_solution(
        instance,
        Solution([["D0", "C1", "D0"]]),
        EvaluatorConfig(),
    )

    assert evaluation.energy_violation > 0
    assert evaluation.time_window_violation > 0
    assert evaluation.late_customer_count == 1


def test_customer_coverage_detects_missing_and_duplicates() -> None:
    instance = line_instance(include_station=False)
    energy_ablation = replace(
        EvaluatorConfig(),
        battery_constraints_enabled=False,
    )

    missing = evaluate_solution(instance, Solution([]), energy_ablation)
    duplicate = evaluate_solution(
        instance,
        Solution(
            [
                ["D0", "C1", "D0"],
                ["D0", "C1", "D0"],
            ]
        ),
        energy_ablation,
    )

    assert missing.missing_customers == ("C1",)
    assert duplicate.duplicate_customers == ("C1",)
    assert not missing.feasible
    assert not duplicate.feasible

