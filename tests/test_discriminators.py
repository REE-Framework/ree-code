import numpy as np
import pytest

from ree.discriminators import (
    get_discriminator,
    p7_residual_target,
    stack_count_for_precision,
)


def test_p7_scaling() -> None:
    result = p7_residual_target([1000.0, 100.0, 10.0, 0.001])
    expected = np.array([1e-24, 1e-26, 1e-28, 1e-36])
    assert np.allclose(result / expected, 1.0)


def test_phase_stack_examples() -> None:
    assert stack_count_for_precision(100.0, 1e-3) == 100
    assert stack_count_for_precision(30.0, 1e-3) == 1112


def test_registry_lookup() -> None:
    assert get_discriminator("p8b").label == "P8b"
    with pytest.raises(KeyError):
        get_discriminator("P999")
