#!/usr/bin/env python3
"""
Appendix N code: appendixN_horizon_policies.py

Unified 1-D horizon-policy toy model.

Modes:
    project  - null-compute interior projection with a thin damping buffer
    reflect  - horizon-cell Robin-like boundary update without interior projection

The script records an operational ledger:
E_int(t), E_ext(t), E_tot(t), cumulative horizon flux Phi_H(t),
dimensional closure residual
R_E(t) = E_tot - (E_int + E_ext + Phi_H),
reference energy E_ref, and normalized residual
R_norm(t) = |R_E(t)| / E_ref.
Only R_norm, not R_E, is compared with dimensionless tolerance thresholds.

Example smoke runs:
    python appendixN_horizon_policies.py --mode project \
        --steps 800 --outdir out_N_project
    python appendixN_horizon_policies.py --mode reflect \
        --steps 800 --outdir out_N_reflect
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

plt.switch_backend("Agg")


Array = np.ndarray


def laplacian_neumann(u: Array, dx: float) -> Array:
    """Second derivative with Neumann conditions at the outer domain edges."""
    lap = np.empty_like(u)
    lap[1:-1] = (u[2:] - 2.0 * u[1:-1] + u[:-2]) / dx ** 2
    lap[0] = (u[1] - 2.0 * u[0] + u[1]) / dx ** 2
    lap[-1] = (u[-2] - 2.0 * u[-1] + u[-2]) / dx ** 2
    return lap


def compute_energy(
    phi: Array,
    phi_old: Array,
    dx: float,
    dt: float,
    c: float,
    mask: Array | None = None,
) -> float:
    """Return the discrete wave energy in the selected region."""
    velocity = (phi - phi_old) / dt
    gradient = np.gradient(phi, dx)
    density = 0.5 * (velocity ** 2 + c ** 2 * gradient ** 2)
    if mask is not None:
        density = density[mask]
    return float(np.sum(density) * dx)


def run(args: argparse.Namespace) -> dict[str, list[float]]:
    c = float(args.c)
    dx = float(args.dx)
    dt = float(args.dtCFL) * dx / c
    x = np.arange(-float(args.xmax), float(args.xmax) + dx, dx)
    horizon_radius = float(args.L)
    buffer_cells = int(args.buffer_cells)
    damp_rate = float(args.damp_rate)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    mask_core = np.abs(x) < horizon_radius - buffer_cells * dx
    mask_buf = (np.abs(x) >= horizon_radius - buffer_cells * dx) & (
        np.abs(x) < horizon_radius + buffer_cells * dx
    )
    # Ledger masks partition the full domain. The numerical buffer is not excluded
    # from the accounting split.
    mask_int = np.abs(x) < horizon_radius
    mask_ext = ~mask_int
    left_horizon_index = int(np.argmin(np.abs(x + horizon_radius)))
    right_horizon_index = int(np.argmin(np.abs(x - horizon_radius)))

    phi = np.exp(-((x - 2.0) ** 2) / (0.2 ** 2))
    phi_old = phi.copy()

    ledger: dict[str, list[float]] = {
        "E_int": [],
        "E_ext": [],
        "E_tot": [],
        "Phi_H_cumulative": [],
        "R_E": [],
        "E_ref": [],
        "R_norm": [],
    }

    alpha = float(args.alpha)
    beta = float(args.beta)

    for _step in range(int(args.steps)):
        lap = laplacian_neumann(phi, dx)
        phi_new = 2.0 * phi - phi_old + (c * dt) ** 2 * lap

        if args.mode == "project":
            damping_factor = max(0.0, 1.0 - damp_rate * dt)
            phi_new[mask_buf] *= damping_factor
            phi_new[mask_core] = 0.0
            phi_old[mask_core] = phi_new[mask_core]
        elif args.mode == "reflect":
            if beta != 0.0:
                robin_factor = 1.0 + dx * alpha / beta
                if abs(robin_factor) < 1e-12:
                    raise ValueError(
                        "Robin denominator too close to zero; adjust alpha, beta, or dx."
                    )
                # Right horizon, outward normal in +x direction.
                phi_new[right_horizon_index] = (
                    phi_new[right_horizon_index - 1] / robin_factor
                )
                # Left horizon, outward normal in -x direction, same scalar toy update.
                phi_new[left_horizon_index] = (
                    phi_new[left_horizon_index + 1] / robin_factor
                )
        else:
            raise ValueError(f"Unknown mode: {args.mode}")

        phi_old, phi = phi, phi_new

        velocity = (phi - phi_old) / dt
        e_tot = compute_energy(phi, phi_old, dx, dt, c)
        e_int = compute_energy(phi, phi_old, dx, dt, c, mask_int)
        e_ext = compute_energy(phi, phi_old, dx, dt, c, mask_ext)

        grad_right = (phi[right_horizon_index] - phi[right_horizon_index - 1]) / dx
        grad_left = (phi[left_horizon_index + 1] - phi[left_horizon_index]) / dx
        flux_right = -c ** 2 * velocity[right_horizon_index] * grad_right
        flux_left = -c ** 2 * velocity[left_horizon_index] * grad_left
        phi_h_increment = (flux_right - flux_left) * dt
        previous_flux = (
            ledger["Phi_H_cumulative"][-1] if ledger["Phi_H_cumulative"] else 0.0
        )
        phi_h_cumulative = previous_flux + float(phi_h_increment)

        ledger["E_tot"].append(e_tot)
        ledger["E_int"].append(e_int)
        ledger["E_ext"].append(e_ext)
        ledger["Phi_H_cumulative"].append(phi_h_cumulative)
        r_e = e_tot - (e_int + e_ext + phi_h_cumulative)
        peak_energy = max(abs(value) for value in ledger["E_tot"])
        e_ref = max(abs(e_tot), peak_energy, 1e-300)
        r_norm = abs(r_e) / e_ref

        ledger["R_E"].append(float(r_e))
        ledger["E_ref"].append(float(e_ref))
        ledger["R_norm"].append(float(r_norm))

    with (outdir / "ledger.json").open("w", encoding="utf-8") as handle:
        json.dump(ledger, handle, indent=2)

    fig, axes = plt.subplots(2, 2, figsize=(10, 6))
    axes[0, 0].plot(ledger["E_int"], label="E_int")
    axes[0, 0].plot(ledger["E_ext"], label="E_ext")
    axes[0, 0].plot(ledger["E_tot"], label="E_tot")
    axes[0, 0].set_title(f"Energy ledger ({args.mode})")
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    axes[0, 1].plot(ledger["Phi_H_cumulative"])
    axes[0, 1].set_title("Cumulative horizon flux Phi_H")
    axes[0, 1].grid(True)

    axes[1, 0].plot(ledger["R_E"], label="R_E")
    axes[1, 0].plot(ledger["R_norm"], label="R_norm")
    axes[1, 0].set_title("Ledger residual and normalised residual")
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    axes[1, 1].plot(x, phi, label="phi")
    axes[1, 1].axvline(horizon_radius, linestyle="--", color="black")
    axes[1, 1].axvline(-horizon_radius, linestyle="--", color="black")
    axes[1, 1].set_title("Final field with horizons")
    axes[1, 1].grid(True)
    axes[1, 1].legend()

    fig.tight_layout()
    fig.savefig(outdir / "horizon_policy_summary.png", dpi=140)
    plt.close(fig)

    print(f"Done. Outputs written to {outdir}")
    return ledger


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Appendix N horizon-policy toy model")
    parser.add_argument(
        "--mode",
        type=str,
        default="project",
        choices=["project", "reflect"],
    )
    parser.add_argument("--c", type=float, default=1.0)
    parser.add_argument("--dx", type=float, default=0.01)
    parser.add_argument("--dtCFL", type=float, default=0.5, help="dt = dtCFL * dx / c")
    parser.add_argument("--xmax", type=float, default=5.0)
    parser.add_argument(
        "--L",
        type=float,
        default=1.0,
        help="horizon radius: |x| < L is interior",
    )
    parser.add_argument("--steps", type=int, default=4000)
    parser.add_argument("--buffer-cells", dest="buffer_cells", type=int, default=3)
    parser.add_argument("--damp-rate", dest="damp_rate", type=float, default=6.0)
    parser.add_argument("--alpha", type=float, default=0.0, help="Robin parameter alpha")
    parser.add_argument("--beta", type=float, default=1.0, help="Robin parameter beta")
    parser.add_argument("--outdir", type=str, default="out_appendixN")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
