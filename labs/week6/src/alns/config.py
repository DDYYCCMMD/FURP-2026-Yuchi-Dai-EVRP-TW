"""Central configuration for the Week 6 ALNS-EVRPTW vertical slice.

Implementation order
--------------------
1. Keep benchmark parameters (Q, C, r, g, v) inside each loaded instance.
2. Put evaluator tolerances and algorithm-control parameters in this module.
3. Pass one ``Week6Config`` object through construction, operators, and solver.
4. Override values from the CLI only in ``labs/week6/src/run_week6_alns.py``.

The defaults deliberately describe a small, reproducible full-recharge run.
They are starting values for verification, not tuned research parameters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True, slots=True)
class EvaluatorConfig:
    """Numerical and modeling choices shared by every route evaluation.

    Week 6 uses Schneider-style full recharge. Partial charging would require
    an additional departure-battery decision variable and is intentionally
    outside this configuration.
    """

    feasibility_tolerance: float = 1e-6
    full_recharge: bool = True
    battery_constraints_enabled: bool = True

    def __post_init__(self) -> None:
        if self.feasibility_tolerance <= 0:
            raise ValueError("feasibility_tolerance must be positive")
        if not self.full_recharge:
            raise ValueError("Week 6 supports full recharge only")


@dataclass(frozen=True, slots=True)
class OperatorConfig:
    """Destroy, repair, and local-search budgets."""

    removal_min: int = 1
    removal_max: int = 3
    removal_fraction: float = 0.20
    regret_k: int = 2
    relocate_budget: int = 20
    two_opt_budget: int = 20
    local_search_probability: float = 0.20
    station_repair_max_insertions: int = 8

    def __post_init__(self) -> None:
        if self.removal_min < 1:
            raise ValueError("removal_min must be at least 1")
        if self.removal_max < self.removal_min:
            raise ValueError("removal_max must be >= removal_min")
        if not 0 < self.removal_fraction <= 1:
            raise ValueError("removal_fraction must be in (0, 1]")
        if self.regret_k < 2:
            raise ValueError("regret_k must be at least 2")
        if self.relocate_budget < 0 or self.two_opt_budget < 0:
            raise ValueError("local-search budgets cannot be negative")
        if not 0 <= self.local_search_probability <= 1:
            raise ValueError("local_search_probability must be in [0, 1]")
        if self.station_repair_max_insertions < 1:
            raise ValueError("station repair must allow at least one insertion")


@dataclass(frozen=True, slots=True)
class AdaptiveWeightConfig:
    """Roulette-wheel operator selection and segment-based weight updates."""

    enabled: bool = True
    initial_weight: float = 1.0
    segment_length: int = 50
    reaction_factor: float = 0.20
    reward_new_best: float = 5.0
    reward_improved: float = 3.0
    reward_accepted: float = 1.0
    reward_neutral: float = 0.0
    reward_rejected: float = 0.0
    minimum_weight: float = 1e-3

    def __post_init__(self) -> None:
        if self.initial_weight <= 0 or self.minimum_weight <= 0:
            raise ValueError("operator weights must be positive")
        if self.segment_length < 1:
            raise ValueError("segment_length must be at least 1")
        if not 0 < self.reaction_factor <= 1:
            raise ValueError("reaction_factor must be in (0, 1]")
        rewards = (
            self.reward_new_best,
            self.reward_improved,
            self.reward_accepted,
            self.reward_neutral,
            self.reward_rejected,
        )
        if any(reward < 0 for reward in rewards):
            raise ValueError("operator rewards cannot be negative")


@dataclass(frozen=True, slots=True)
class SimulatedAnnealingConfig:
    """Acceptance settings for feasible candidates with equal vehicle count."""

    enabled: bool = True
    initial_temperature: float = 10.0
    cooling_rate: float = 0.995
    minimum_temperature: float = 0.01

    def __post_init__(self) -> None:
        if self.initial_temperature <= 0 or self.minimum_temperature <= 0:
            raise ValueError("SA temperatures must be positive")
        if self.minimum_temperature > self.initial_temperature:
            raise ValueError("minimum_temperature cannot exceed initial_temperature")
        if not 0 < self.cooling_rate < 1:
            raise ValueError("cooling_rate must be in (0, 1)")


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    """Reproducible Week 6 run and output settings."""

    data_dir: Path = PROJECT_ROOT / "data" / "schneider_instances"
    output_dir: Path = PROJECT_ROOT / "results" / "week6"
    instance_names: tuple[str, ...] = ("c101C5", "r105C5", "rc105C5")
    seeds: tuple[int, ...] = (64, 65, 66)
    iterations: int = 1_000
    # Formal comparisons use a fixed iteration budget by default. A wall-clock
    # limit remains available from the CLI for smoke tests and scalability runs.
    time_limit_s: float | None = None
    log_every: int = 100

    def __post_init__(self) -> None:
        if not self.instance_names:
            raise ValueError("at least one instance is required")
        if not self.seeds:
            raise ValueError("at least one seed is required")
        if self.iterations < 1:
            raise ValueError("iterations must be at least 1")
        if self.time_limit_s is not None and self.time_limit_s <= 0:
            raise ValueError("time_limit_s must be positive or None")
        if self.log_every < 1:
            raise ValueError("log_every must be at least 1")


@dataclass(frozen=True, slots=True)
class Week6Config:
    """Single configuration object passed to the Week 6 pipeline."""

    evaluator: EvaluatorConfig = field(default_factory=EvaluatorConfig)
    operators: OperatorConfig = field(default_factory=OperatorConfig)
    adaptive_weights: AdaptiveWeightConfig = field(
        default_factory=AdaptiveWeightConfig
    )
    simulated_annealing: SimulatedAnnealingConfig = field(
        default_factory=SimulatedAnnealingConfig
    )
    experiment: ExperimentConfig = field(default_factory=ExperimentConfig)


DEFAULT_CONFIG = Week6Config()
