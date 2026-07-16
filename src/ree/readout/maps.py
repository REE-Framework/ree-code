"""Readout maps for finite spatial resolution and declared tolerance.

These utilities implement an operational comparison: two underlying arrays are
indistinguishable only relative to a specified readout map, norm, and tolerance.
They do not assert that the arrays are ontologically identical.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray

Array = NDArray[np.float64]
Norm = Literal["l2", "linf", "mean_abs"]


@dataclass(frozen=True, slots=True)
class ReadoutSpec:
    """Declared finite-resolution readout map."""

    block: int | tuple[int, ...] = 1
    resolution: float | None = None
    tolerance: float = 0.0
    norm: Norm = "linf"

    def __post_init__(self) -> None:
        if isinstance(self.block, int):
            if self.block <= 0:
                raise ValueError("block must be positive")
        elif any(value <= 0 for value in self.block):
            raise ValueError("all block factors must be positive")
        if self.resolution is not None and self.resolution <= 0:
            raise ValueError("resolution must be positive when supplied")
        if self.tolerance < 0:
            raise ValueError("tolerance must be non-negative")
        if self.norm not in {"l2", "linf", "mean_abs"}:
            raise ValueError("unsupported norm")


@dataclass(frozen=True, slots=True)
class ReadoutComparison:
    distance: float
    tolerance: float
    indistinguishable: bool
    norm: Norm
    readout_shape: tuple[int, ...]


def _normalise_block(block: int | tuple[int, ...], ndim: int) -> tuple[int, ...]:
    if isinstance(block, int):
        return (block,) * ndim
    if len(block) != ndim:
        raise ValueError("block dimensionality must match the array")
    return block


def block_mean(values: ArrayLike, block: int | tuple[int, ...]) -> Array:
    """Average non-overlapping blocks without silently trimming cells."""

    array = np.asarray(values, dtype=np.float64)
    factors = _normalise_block(block, array.ndim)
    if any(size % factor for size, factor in zip(array.shape, factors, strict=True)):
        raise ValueError("each array dimension must be exactly divisible by its block factor")

    reshape: list[int] = []
    for size, factor in zip(array.shape, factors, strict=True):
        reshape.extend([size // factor, factor])
    reduced = array.reshape(tuple(reshape))
    mean_axes = tuple(range(1, 2 * array.ndim, 2))
    return reduced.mean(axis=mean_axes)


def apply_readout(values: ArrayLike, spec: ReadoutSpec) -> Array:
    """Apply spatial block averaging and optional quantisation."""

    array = np.asarray(values, dtype=np.float64)
    if not np.all(np.isfinite(array)):
        raise ValueError("readout input must contain only finite values")

    output = block_mean(array, spec.block)
    if spec.resolution is not None:
        output = np.rint(output / spec.resolution) * spec.resolution
    return output


def compare(left: ArrayLike, right: ArrayLike, spec: ReadoutSpec) -> ReadoutComparison:
    """Compare two states after the same declared readout map."""

    left_readout = apply_readout(left, spec)
    right_readout = apply_readout(right, spec)
    if left_readout.shape != right_readout.shape:
        raise ValueError("readout arrays must have identical shapes")

    difference = left_readout - right_readout
    if spec.norm == "linf":
        distance = float(np.max(np.abs(difference)))
    elif spec.norm == "l2":
        distance = float(np.linalg.norm(difference.ravel()))
    else:
        distance = float(np.mean(np.abs(difference)))

    return ReadoutComparison(
        distance=distance,
        tolerance=spec.tolerance,
        indistinguishable=distance <= spec.tolerance,
        norm=spec.norm,
        readout_shape=left_readout.shape,
    )
