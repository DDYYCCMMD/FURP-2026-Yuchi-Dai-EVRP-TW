"""Week 6 adaptive roulette-wheel weights for destroy/repair operators.

Implementation step 6
---------------------
Record a reward after each operator use. At the end of each segment:

    w_new = (1 - reaction) * w_old
            + reaction * (segment_reward / segment_uses)

Destroy and repair pools should use separate instances of this class.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .config import AdaptiveWeightConfig


@dataclass(slots=True)
class AdaptiveWeights:
    operator_names: tuple[str, ...]
    config: AdaptiveWeightConfig
    weights: dict[str, float] = field(init=False)
    segment_rewards: dict[str, float] = field(init=False)
    segment_uses: dict[str, int] = field(init=False)

    def __post_init__(self) -> None:
        if not self.operator_names:
            raise ValueError("at least one operator name is required")
        self.weights = {
            name: self.config.initial_weight for name in self.operator_names
        }
        self.segment_rewards = {name: 0.0 for name in self.operator_names}
        self.segment_uses = {name: 0 for name in self.operator_names}

    def choose(self, rng: random.Random) -> str:
        """Select one operator proportionally to its current weight."""

        return rng.choices(
            population=self.operator_names,
            weights=[self.weights[name] for name in self.operator_names],
            k=1,
        )[0]

    def record(self, operator_name: str, reward: float) -> None:
        self.segment_rewards[operator_name] += reward
        self.segment_uses[operator_name] += 1

    def update_segment(self) -> None:
        """Update used operators, then clear segment statistics."""

        reaction = self.config.reaction_factor
        for name in self.operator_names:
            uses = self.segment_uses[name]
            if uses:
                average_reward = self.segment_rewards[name] / uses
                updated = (
                    (1 - reaction) * self.weights[name]
                    + reaction * average_reward
                )
                self.weights[name] = max(
                    self.config.minimum_weight,
                    updated,
                )
            self.segment_rewards[name] = 0.0
            self.segment_uses[name] = 0
