"""Versioned public metadata for the REE Prediction Register.

This module is a readable software mirror, not the immutable scientific
registration archive. Exact estimators, priors, nuisance classes, and retirement
rules remain controlled by the canonical manuscript and registration record.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class Discriminator:
    label: str
    title: str
    programme_status: str
    regime: str
    implementation_status: str
    canonical_source: str
    note: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


_REGISTER: tuple[Discriminator, ...] = (
    Discriminator(
        "P1a",
        "Lawing-phase / dynamic-lambda discriminator",
        "conditional",
        "cosmology",
        "metadata only",
        "Main Part II; Appendix R′",
    ),
    Discriminator(
        "P1b",
        "Low-ell dark-energy quadrupole",
        "conditional",
        "cosmology",
        "metadata only",
        "Main Part II; Appendix R′",
    ),
    Discriminator(
        "P2a",
        "Rogue-mode energy path-invariance",
        "active / tiered",
        "gravitational-wave",
        "metadata only",
        "Main Part II; Appendix R′",
        "Tier thresholds belong to the canonical register.",
    ),
    Discriminator(
        "P2b",
        "Phase-work invariance",
        "prospective",
        "gravitational-wave",
        "phase helper implemented",
        "Main Part II; Appendix R′",
        "The 10^-3 rad regime requires high effective SNR and full controls.",
    ),
    Discriminator(
        "P2c",
        "Entropy rebound / overshoot",
        "active",
        "cosmology",
        "metadata only",
        "Main Part II; Appendix R′",
    ),
    Discriminator(
        "P3",
        "Inner-slope universality",
        "active",
        "galaxy dynamics",
        "metadata only",
        "Main Part II; Appendix R′",
    ),
    Discriminator(
        "P4",
        "Wide-binary heating floor",
        "active",
        "stellar dynamics",
        "metadata only",
        "Main Part II; Appendix R′",
    ),
    Discriminator(
        "P5",
        "Front-phase symmetry under RRIP",
        "active",
        "simulation / bridge",
        "readout utility available",
        "Main Part II; Appendix R′",
    ),
    Discriminator(
        "P6",
        "Front regularity in WL and RSD observables",
        "active",
        "cosmology",
        "metadata only",
        "Main Part II; Appendix R′",
    ),
    Discriminator(
        "P7",
        "Computational-structure detector residual",
        "prospective",
        "gravitational-wave",
        "frequency target implemented",
        "Main Part II; Appendix R′",
    ),
    Discriminator(
        "P8",
        "Horizon-only readout / boundary-ledger closure",
        "prospective",
        "black-hole",
        "toy ledger only",
        "Main Part II; Appendices H′ and R′",
        "The included ledger is not a black-hole simulation.",
    ),
    Discriminator(
        "P8b",
        "Clean-vacuum black-hole merger jet silence",
        "conditional branch",
        "black-hole",
        "metadata only",
        "Main Part II; Appendices H′ and R′",
        "A definitive clean jet falsifies P8b only.",
    ),
    Discriminator(
        "P9",
        "Primordial-black-hole ignition candidate",
        "under development",
        "early universe",
        "metadata only",
        "Candidate / future registration",
        "Not promoted to the active register.",
    ),
)


def list_discriminators(
    *, status: str | None = None, regime: str | None = None
) -> list[Discriminator]:
    """Return register entries, optionally filtered case-insensitively."""

    entries: Iterable[Discriminator] = _REGISTER
    if status is not None:
        needle = status.casefold()
        entries = (item for item in entries if needle in item.programme_status.casefold())
    if regime is not None:
        needle = regime.casefold()
        entries = (item for item in entries if needle in item.regime.casefold())
    return list(entries)


def get_discriminator(label: str) -> Discriminator:
    """Return a register entry by exact label, case-insensitively."""

    target = label.casefold()
    for item in _REGISTER:
        if item.label.casefold() == target:
            return item
    raise KeyError(f"unknown discriminator label: {label}")
