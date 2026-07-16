"""Finite-speed damped-wave front demonstration.

Scientific status
-----------------
This module is a transparent constructive demonstration and validation scaffold.
It is not presented as the complete canonical REE dynamics. Its purpose is to
make finite-speed propagation, scheme-specific CFL validation, deterministic
initialisation, and convergence tests executable.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from math import sqrt
from typing import Literal

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]
Boundary = Literal["periodic", "reflecting"]


@dataclass(frozen=True, slots=True)
class AlgorithmAConfig:
    """Numerical configuration for the front demonstration."""

    shape: tuple[int, ...] = (64, 64, 64)
    dx: float = 1.0
    dt: float = 0.25
    signal_speed: float = 1.0
    damping: float = 0.05
    mass: float = 0.0
    boundary: Boundary = "periodic"

    def __post_init__(self) -> None:
        if not 1 <= len(self.shape) <= 3:
            raise ValueError("shape must describe a one-, two-, or three-dimensional grid")
        if any(n < 3 for n in self.shape):
            raise ValueError("each grid dimension must contain at least three cells")
        if self.dx <= 0 or self.dt <= 0:
            raise ValueError("dx and dt must be strictly positive")
        if self.signal_speed <= 0:
            raise ValueError("signal_speed must be strictly positive")
        if self.damping < 0 or self.mass < 0:
            raise ValueError("damping and mass must be non-negative")
        if self.boundary not in {"periodic", "reflecting"}:
            raise ValueError("boundary must be 'periodic' or 'reflecting'")
        if self.courant_number > 1.0 + 1e-12:
            raise ValueError(
                "inadmissible timestep: the explicit multidimensional wave scheme requires "
                "sqrt(ndim) * c * dt / dx <= 1"
            )

    @property
    def courant_number(self) -> float:
        """Return the scheme-specific multidimensional Courant number."""

        return sqrt(len(self.shape)) * self.signal_speed * self.dt / self.dx


@dataclass(slots=True)
class AlgorithmAState:
    """Two-level state required by the explicit second-order update."""

    previous: Array
    current: Array
    step_index: int = 0

    def __post_init__(self) -> None:
        self.previous = np.asarray(self.previous, dtype=np.float64)
        self.current = np.asarray(self.current, dtype=np.float64)
        if self.previous.shape != self.current.shape:
            raise ValueError("previous and current arrays must have identical shapes")
        if not np.all(np.isfinite(self.previous)) or not np.all(np.isfinite(self.current)):
            raise ValueError("state arrays must contain only finite values")


@dataclass(frozen=True, slots=True)
class FrontSummary:
    step_index: int
    minimum: float
    maximum: float
    mean: float
    l2_norm: float
    energy: float
    courant_number: float


def initialize_gaussian(
    config: AlgorithmAConfig,
    *,
    amplitude: float = 1.0,
    width: float | None = None,
    center: Iterable[float] | None = None,
    initial_velocity: float = 0.0,
) -> AlgorithmAState:
    """Create a Gaussian seed with a uniform initial velocity.

    Coordinates are expressed in grid-cell units. Zero initial velocity is
    represented by identical previous and current fields.
    """

    if width is None:
        width = max(config.shape) / 10.0
    if width <= 0:
        raise ValueError("width must be strictly positive")

    if center is None:
        centre_tuple = tuple((n - 1) / 2.0 for n in config.shape)
    else:
        centre_tuple = tuple(float(value) for value in center)
        if len(centre_tuple) != len(config.shape):
            raise ValueError("center dimensionality must match shape")

    axes = np.ogrid[tuple(slice(0, n) for n in config.shape)]
    radius_sq = np.zeros(config.shape, dtype=np.float64)
    for axis, coordinate in enumerate(axes):
        radius_sq += (coordinate - centre_tuple[axis]) ** 2

    current = amplitude * np.exp(-radius_sq / (2.0 * width**2))
    previous = current - config.dt * float(initial_velocity)
    return AlgorithmAState(previous=previous, current=current, step_index=0)


def _laplacian(field: Array, dx: float, boundary: Boundary) -> Array:
    result = np.zeros_like(field)
    if boundary == "periodic":
        for axis in range(field.ndim):
            result += np.roll(field, 1, axis=axis)
            result += np.roll(field, -1, axis=axis)
            result -= 2.0 * field
    else:
        padded = np.pad(field, 1, mode="edge")
        centre = tuple(slice(1, -1) for _ in range(field.ndim))
        result -= 2.0 * field * field.ndim
        for axis in range(field.ndim):
            lower = list(centre)
            upper = list(centre)
            lower[axis] = slice(0, -2)
            upper[axis] = slice(2, None)
            result += padded[tuple(lower)] + padded[tuple(upper)]
    return result / dx**2


def step(state: AlgorithmAState, config: AlgorithmAConfig) -> AlgorithmAState:
    """Advance the damped wave field by one explicit timestep."""

    if state.current.shape != config.shape:
        raise ValueError("state shape does not match configuration")

    velocity = (state.current - state.previous) / config.dt
    acceleration = (
        config.signal_speed**2 * _laplacian(state.current, config.dx, config.boundary)
        - config.damping * velocity
        - config.mass**2 * state.current
    )
    next_field = 2.0 * state.current - state.previous + config.dt**2 * acceleration

    if not np.all(np.isfinite(next_field)):
        raise FloatingPointError("front update produced non-finite values")

    return AlgorithmAState(
        previous=state.current.copy(),
        current=next_field,
        step_index=state.step_index + 1,
    )


def run(
    state: AlgorithmAState,
    config: AlgorithmAConfig,
    steps: int,
    *,
    sample_every: int | None = None,
) -> tuple[AlgorithmAState, list[FrontSummary]]:
    """Run the demonstration and optionally collect summaries."""

    if steps < 0:
        raise ValueError("steps must be non-negative")
    if sample_every is not None and sample_every <= 0:
        raise ValueError("sample_every must be positive when supplied")

    summaries: list[FrontSummary] = []
    current_state = state
    if sample_every is not None:
        summaries.append(summarize(current_state, config))

    for _ in range(steps):
        current_state = step(current_state, config)
        if sample_every is not None and current_state.step_index % sample_every == 0:
            summaries.append(summarize(current_state, config))

    return current_state, summaries


def energy(state: AlgorithmAState, config: AlgorithmAConfig) -> float:
    """Return the discrete field energy used for validation diagnostics."""

    velocity = (state.current - state.previous) / config.dt
    kinetic = 0.5 * np.sum(velocity**2)
    gradient = 0.0
    for axis in range(state.current.ndim):
        if config.boundary == "periodic":
            difference = (np.roll(state.current, -1, axis=axis) - state.current) / config.dx
        else:
            difference = (
                np.diff(state.current, axis=axis, append=np.take(state.current, [-1], axis=axis))
                / config.dx
            )
        gradient += 0.5 * config.signal_speed**2 * np.sum(difference**2)
    potential = 0.5 * config.mass**2 * np.sum(state.current**2)
    cell_volume = config.dx**state.current.ndim
    return float((kinetic + gradient + potential) * cell_volume)


def summarize(state: AlgorithmAState, config: AlgorithmAConfig) -> FrontSummary:
    """Create a compact, JSON-friendly state summary."""

    field = state.current
    return FrontSummary(
        step_index=state.step_index,
        minimum=float(np.min(field)),
        maximum=float(np.max(field)),
        mean=float(np.mean(field)),
        l2_norm=float(np.linalg.norm(field.ravel())),
        energy=energy(state, config),
        courant_number=config.courant_number,
    )
