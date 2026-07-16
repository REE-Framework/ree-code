import numpy as np
import pytest

from ree.algorithm_a import AlgorithmAConfig, initialize_gaussian, run, summarize


def test_cfl_rejects_inadmissible_timestep() -> None:
    with pytest.raises(ValueError, match="Courant|timestep|scheme"):
        AlgorithmAConfig(shape=(8, 8, 8), dx=1.0, dt=0.7, signal_speed=1.0)


def test_front_run_is_deterministic_and_finite() -> None:
    config = AlgorithmAConfig(shape=(12, 12), dt=0.25, damping=0.05)
    first, _ = run(initialize_gaussian(config, width=2.0), config, 8)
    second, _ = run(initialize_gaussian(config, width=2.0), config, 8)
    assert np.array_equal(first.current, second.current)
    assert np.all(np.isfinite(first.current))
    summary = summarize(first, config)
    assert summary.step_index == 8
    assert summary.energy >= 0
