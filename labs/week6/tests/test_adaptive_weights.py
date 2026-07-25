"""Segment-based adaptive operator weight updates."""

from labs.week6.src.alns.adaptive_weights import AdaptiveWeights
from labs.week6.src.alns.config import AdaptiveWeightConfig


def test_rewarded_operator_receives_higher_weight() -> None:
    weights = AdaptiveWeights(
        ("random", "worst"),
        AdaptiveWeightConfig(reaction_factor=0.5),
    )
    weights.record("random", 5.0)
    weights.record("worst", 0.0)
    weights.update_segment()

    assert weights.weights["random"] > weights.weights["worst"]

