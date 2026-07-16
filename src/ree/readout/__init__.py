"""Finite-resolution readout and RRIP-style comparison utilities."""

from .maps import ReadoutComparison, ReadoutSpec, apply_readout, block_mean, compare

__all__ = ["ReadoutComparison", "ReadoutSpec", "apply_readout", "block_mean", "compare"]
