"""Week 6 step 0: central configuration must reject invalid controls."""

import pytest

from labs.week6.src.alns.config import OperatorConfig, Week6Config


def test_default_config_is_valid() -> None:
    config = Week6Config()
    assert config.evaluator.full_recharge
    assert config.operators.regret_k == 2
    assert config.adaptive_weights.enabled
    assert config.adaptive_weights.reward_neutral == 0
    assert config.simulated_annealing.enabled
    assert config.experiment.time_limit_s is None


def test_invalid_removal_range_is_rejected() -> None:
    with pytest.raises(ValueError, match="removal_max"):
        OperatorConfig(removal_min=3, removal_max=2)
