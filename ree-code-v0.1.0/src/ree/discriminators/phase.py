"""Phase-resolution helpers for high-SNR or stacked regimes."""

from __future__ import annotations

import math


def effective_snr_for_precision(phase_precision_rad: float) -> float:
    """Return the idealised effective SNR from sigma_phi approximately 1/rho."""

    if phase_precision_rad <= 0 or not math.isfinite(phase_precision_rad):
        raise ValueError("phase_precision_rad must be finite and strictly positive")
    return 1.0 / phase_precision_rad


def stack_count_for_precision(
    per_event_snr: float,
    phase_precision_rad: float,
) -> int:
    """Return ideal coherent-event count needed for a target phase precision.

    This uses rho_eff = sqrt(N) * rho_event and sigma_phi approximately 1/rho_eff.
    It is an optimistic scaling helper, not a detector forecast; calibration,
    waveform, population, and coherence losses must be handled separately.
    """

    if per_event_snr <= 0 or not math.isfinite(per_event_snr):
        raise ValueError("per_event_snr must be finite and strictly positive")
    target_snr = effective_snr_for_precision(phase_precision_rad)
    return max(1, math.ceil((target_snr / per_event_snr) ** 2))
