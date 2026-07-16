"""Print the registered P7 frequency scaling at representative frequencies."""

from __future__ import annotations

from ree.discriminators import p7_residual_target

frequencies = [1000.0, 100.0, 10.0, 0.001]
for frequency, target in zip(frequencies, p7_residual_target(frequencies), strict=True):
    print(f"{frequency:g} Hz: {target:.3e}")
