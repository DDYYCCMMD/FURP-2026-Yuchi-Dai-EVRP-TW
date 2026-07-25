"""Week 6 feasibility-first simulated annealing acceptance.

Implementation step 7
---------------------
- Always accept a feasible solution with fewer vehicles.
- Reject a solution with more vehicles or any infeasibility.
- With equal vehicle count, accept shorter distance deterministically.
- Accept a longer route with probability exp(-delta / temperature).
"""

from __future__ import annotations

import math
import random
from enum import Enum

from .config import SimulatedAnnealingConfig
from .models import Evaluation


class AcceptanceOutcome(str, Enum):
    """Reason associated with one accepted or rejected candidate."""

    IMPROVING = "improving"
    NEUTRAL = "neutral"
    WORSE_ACCEPTED = "worse_accepted"
    REJECTED = "rejected"

    @property
    def accepted(self) -> bool:
        return self is not AcceptanceOutcome.REJECTED


def acceptance_outcome(
    current: Evaluation,
    candidate: Evaluation,
    temperature: float,
    rng: random.Random,
    config: SimulatedAnnealingConfig,
    *,
    distance_tolerance: float = 1e-9,
) -> AcceptanceOutcome:
    """Classify a feasibility-first candidate acceptance decision."""

    if not candidate.feasible:
        return AcceptanceOutcome.REJECTED
    if not current.feasible:
        return AcceptanceOutcome.IMPROVING
    if candidate.vehicle_count < current.vehicle_count:
        return AcceptanceOutcome.IMPROVING
    if candidate.vehicle_count > current.vehicle_count:
        return AcceptanceOutcome.REJECTED

    distance_delta = candidate.total_distance - current.total_distance
    if distance_delta < -distance_tolerance:
        return AcceptanceOutcome.IMPROVING
    if abs(distance_delta) <= distance_tolerance:
        return AcceptanceOutcome.NEUTRAL
    if not config.enabled:
        return AcceptanceOutcome.REJECTED

    safe_temperature = max(temperature, config.minimum_temperature)
    probability = math.exp(-distance_delta / safe_temperature)
    if rng.random() < probability:
        return AcceptanceOutcome.WORSE_ACCEPTED
    return AcceptanceOutcome.REJECTED


def accept_candidate(
    current: Evaluation,
    candidate: Evaluation,
    temperature: float,
    rng: random.Random,
    config: SimulatedAnnealingConfig,
) -> bool:
    """Backward-compatible boolean wrapper around ``acceptance_outcome``."""

    return acceptance_outcome(
        current,
        candidate,
        temperature,
        rng,
        config,
    ).accepted


def cool_temperature(
    temperature: float,
    config: SimulatedAnnealingConfig,
) -> float:
    return max(
        config.minimum_temperature,
        temperature * config.cooling_rate,
    )
