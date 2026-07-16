import numpy as np
import pytest

from ree.readout import ReadoutSpec, block_mean, compare


def test_block_mean_exact() -> None:
    values = np.arange(16.0).reshape(4, 4)
    result = block_mean(values, 2)
    expected = np.array([[2.5, 4.5], [10.5, 12.5]])
    assert np.allclose(result, expected)


def test_block_mean_refuses_silent_trimming() -> None:
    with pytest.raises(ValueError, match="divisible"):
        block_mean(np.zeros((5, 4)), 2)


def test_distinct_states_can_share_declared_readout() -> None:
    left = np.zeros((4, 4))
    right = left.copy()
    right[0:2, 0:2] = 0.02
    spec = ReadoutSpec(block=2, resolution=0.05, tolerance=0.0)
    comparison = compare(left, right, spec)
    assert comparison.indistinguishable
    assert comparison.distance == 0.0
