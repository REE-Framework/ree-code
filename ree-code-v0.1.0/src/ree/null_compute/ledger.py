"""Conservative one-dimensional boundary-ledger demonstration.

Scientific status
-----------------
This module demonstrates accounting of a conserved scalar crossing a retained
boundary. It is not a black-hole interior simulation. The scalar may be read as
an energy-like quantity only within the declared toy model.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

Array = NDArray[np.float64]


@dataclass(slots=True)
class BoundaryLedger:
    initial_quantity: float
    cumulative_inflow: float = 0.0
    cumulative_outflow: float = 0.0

    def residual(self, retained_quantity: float) -> float:
        """Return retained + outflow - inflow - initial."""

        return (
            float(retained_quantity)
            + self.cumulative_outflow
            - self.cumulative_inflow
            - self.initial_quantity
        )

    def normalized_residual(self, retained_quantity: float) -> float:
        scale = max(abs(self.initial_quantity), np.finfo(float).eps)
        return abs(self.residual(retained_quantity)) / scale


@dataclass(frozen=True, slots=True)
class LedgerRecord:
    step_index: int
    retained_quantity: float
    cumulative_inflow: float
    cumulative_outflow: float
    residual: float
    normalized_residual: float


def advance_upwind(
    density: ArrayLike,
    *,
    speed: float,
    dx: float,
    dt: float,
    left_boundary: float = 0.0,
    right_boundary: float = 0.0,
) -> tuple[Array, float, float]:
    """Advance a conservative scalar advection equation by one timestep.

    Returns `(new_density, inflow_rate, outflow_rate)`, where rates are signed
    positive into and out of the retained interval respectively.
    """

    field = np.asarray(density, dtype=np.float64)
    if field.ndim != 1 or field.size < 2:
        raise ValueError("density must be a one-dimensional array with at least two cells")
    if not np.all(np.isfinite(field)):
        raise ValueError("density must contain only finite values")
    if dx <= 0 or dt <= 0:
        raise ValueError("dx and dt must be strictly positive")
    courant = abs(speed) * dt / dx
    if courant > 1.0 + 1e-12:
        raise ValueError("upwind stability requires |speed| * dt / dx <= 1")

    interfaces = np.empty(field.size + 1, dtype=np.float64)
    if speed >= 0:
        interfaces[0] = speed * left_boundary
        interfaces[1:] = speed * field
        inflow_rate = max(interfaces[0], 0.0)
        outflow_rate = max(interfaces[-1], 0.0)
    else:
        interfaces[:-1] = speed * field
        interfaces[-1] = speed * right_boundary
        inflow_rate = max(-interfaces[-1], 0.0)
        outflow_rate = max(-interfaces[0], 0.0)

    updated = field - (dt / dx) * (interfaces[1:] - interfaces[:-1])
    return updated, float(inflow_rate), float(outflow_rate)


def run_demo(
    *,
    cells: int = 256,
    steps: int = 220,
    speed: float = 1.0,
    length: float = 1.0,
    courant: float = 0.8,
    sample_every: int = 20,
) -> tuple[Array, BoundaryLedger, list[LedgerRecord]]:
    """Move a Gaussian packet through the retained interval and record flux."""

    if cells < 8:
        raise ValueError("cells must be at least 8")
    if steps < 0:
        raise ValueError("steps must be non-negative")
    if not 0 < courant <= 1:
        raise ValueError("courant must lie in (0, 1]")
    if sample_every <= 0:
        raise ValueError("sample_every must be positive")

    dx = length / cells
    dt = courant * dx / abs(speed)
    x = (np.arange(cells) + 0.5) * dx
    density = np.exp(-0.5 * ((x - 0.25 * length) / (0.06 * length)) ** 2)
    initial = float(np.sum(density) * dx)
    ledger = BoundaryLedger(initial_quantity=initial)
    records: list[LedgerRecord] = []

    def record(index: int) -> None:
        retained = float(np.sum(density) * dx)
        residual = ledger.residual(retained)
        records.append(
            LedgerRecord(
                step_index=index,
                retained_quantity=retained,
                cumulative_inflow=ledger.cumulative_inflow,
                cumulative_outflow=ledger.cumulative_outflow,
                residual=residual,
                normalized_residual=ledger.normalized_residual(retained),
            )
        )

    record(0)
    for index in range(1, steps + 1):
        density, inflow_rate, outflow_rate = advance_upwind(density, speed=speed, dx=dx, dt=dt)
        ledger.cumulative_inflow += dt * inflow_rate
        ledger.cumulative_outflow += dt * outflow_rate
        if index % sample_every == 0 or index == steps:
            record(index)

    return density, ledger, records
