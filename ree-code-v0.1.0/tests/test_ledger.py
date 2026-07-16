import numpy as np
import pytest

from ree.null_compute import advance_upwind, run_demo


def test_upwind_rejects_unstable_timestep() -> None:
    with pytest.raises(ValueError, match="stability"):
        advance_upwind(np.ones(8), speed=1.0, dx=1.0, dt=1.1)


def test_boundary_ledger_closes() -> None:
    _, _, records = run_demo(cells=128, steps=180, sample_every=30)
    assert records[-1].normalized_residual < 1e-12
    assert records[-1].cumulative_outflow > 0
