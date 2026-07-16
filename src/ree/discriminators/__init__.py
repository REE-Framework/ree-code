"""REE discriminator metadata and selected numerical helpers."""

from .phase import effective_snr_for_precision, stack_count_for_precision
from .registry import Discriminator, get_discriminator, list_discriminators
from .targets import p7_residual_target

__all__ = [
    "Discriminator",
    "effective_snr_for_precision",
    "get_discriminator",
    "list_discriminators",
    "p7_residual_target",
    "stack_count_for_precision",
]
