"""Greedy full-recharge station insertion coverage."""

from labs.week6.src.alns.charging_repair import (
    repair_charging_stations,
)
from labs.week6.src.alns.config import Week6Config
from labs.week6.src.alns.evaluator import evaluate_solution
from labs.week6.src.alns.models import Solution
from labs.week6.tests.helpers import line_instance


def test_station_insertion_repairs_energy_violation() -> None:
    instance = line_instance(battery_capacity=16.0)
    config = Week6Config()
    original = Solution([["D0", "C1", "D0"]])

    repaired = repair_charging_stations(instance, original, config)

    assert repaired is not None
    assert "S1" in repaired.routes[0]
    assert evaluate_solution(
        instance,
        repaired,
        config.evaluator,
    ).feasible


def test_station_insertion_rejected_when_it_breaks_time_window() -> None:
    instance = line_instance(
        battery_capacity=16.0,
        depot_due_time=20.0,
        customer_due_time=12.0,
    )
    config = Week6Config()

    repaired = repair_charging_stations(
        instance,
        Solution([["D0", "C1", "D0"]]),
        config,
    )

    assert repaired is None
