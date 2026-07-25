"""Feasibility-first simulated annealing rules."""

import random

from labs.week6.src.alns.acceptance import (
    AcceptanceOutcome,
    accept_candidate,
    acceptance_outcome,
)
from labs.week6.src.alns.config import SimulatedAnnealingConfig
from labs.week6.src.alns.models import Evaluation


def test_infeasible_candidate_is_always_rejected() -> None:
    current = Evaluation(
        feasible=True,
        vehicle_count=1,
        total_distance=10,
    )
    candidate = Evaluation(
        feasible=False,
        vehicle_count=1,
        total_distance=5,
    )

    assert not accept_candidate(
        current,
        candidate,
        temperature=100,
        rng=random.Random(1),
        config=SimulatedAnnealingConfig(),
    )


def test_fewer_vehicles_is_always_accepted() -> None:
    current = Evaluation(
        feasible=True,
        vehicle_count=2,
        total_distance=10,
    )
    candidate = Evaluation(
        feasible=True,
        vehicle_count=1,
        total_distance=100,
    )

    assert accept_candidate(
        current,
        candidate,
        temperature=0.01,
        rng=random.Random(1),
        config=SimulatedAnnealingConfig(),
    )


def test_equal_objective_is_classified_as_neutral() -> None:
    current = Evaluation(
        feasible=True,
        vehicle_count=1,
        total_distance=10,
    )
    candidate = Evaluation(
        feasible=True,
        vehicle_count=1,
        total_distance=10,
    )

    outcome = acceptance_outcome(
        current,
        candidate,
        temperature=1,
        rng=random.Random(1),
        config=SimulatedAnnealingConfig(),
    )

    assert outcome is AcceptanceOutcome.NEUTRAL
    assert outcome.accepted


def test_worse_candidate_can_be_accepted_by_sa() -> None:
    current = Evaluation(
        feasible=True,
        vehicle_count=1,
        total_distance=10,
    )
    candidate = Evaluation(
        feasible=True,
        vehicle_count=1,
        total_distance=11,
    )

    outcome = acceptance_outcome(
        current,
        candidate,
        temperature=100,
        rng=random.Random(1),
        config=SimulatedAnnealingConfig(),
    )

    assert outcome is AcceptanceOutcome.WORSE_ACCEPTED
