"""Registered or explicitly parameterised detector-domain targets."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray


def p7_residual_target(
    frequency_hz: ArrayLike,
    *,
    h0: float = 1e-24,
    f0_hz: float = 1_000.0,
) -> NDArray[np.float64]:
    """Return the P7 detector-domain strain-amplitude target.

    The registered scaling is

        h_res(f) = h0 * (f / f0)^2,

    with the default reference frequency f0 = 1 kHz. The output is a
    dimensionless strain amplitude, not an amplitude spectral density, residual
    power, or signal-to-noise ratio.
    """

    frequency = np.asarray(frequency_hz, dtype=np.float64)
    if np.any(~np.isfinite(frequency)) or np.any(frequency < 0):
        raise ValueError("frequency_hz must contain finite non-negative values")
    if h0 <= 0 or f0_hz <= 0:
        raise ValueError("h0 and f0_hz must be strictly positive")
    return h0 * (frequency / f0_hz) ** 2
