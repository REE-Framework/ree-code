#!/usr/bin/env python3
"""
Appendix J code: structured_efficiency_toy3d.py

Pedagogical 3-D structured-efficiency prototype.

This script is a constructive toy model only. It is intended to be copy-executable,
deterministic under a declared seed, and suitable for audit of the manuscript's
Appendix J demonstration. It does not claim empirical validation or ontological
uniqueness.

Example smoke run:
    python structured_efficiency_toy3d.py --nx 16 --ny 16 --nz 16 \
        --n-steps 4 --poisson-iters 20 --save-every 2 --outdir out_3d_smoke
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from scipy.fft import fftfreq, fftn, ifftn


Array = np.ndarray


# -----------------------------------------------------------------------------
# Utilities, 3-D periodic grid
# -----------------------------------------------------------------------------

def gaussian_blur_fft_3d(field: Array, sigma: float) -> Array:
    """Return a periodic 3-D Gaussian blur computed by FFT."""
    if sigma <= 0:
        return field.copy()
    dtype = field.dtype
    nx, ny, nz = field.shape
    kx = fftfreq(nx)[:, None, None]
    ky = fftfreq(ny)[None, :, None]
    kz = fftfreq(nz)[None, None, :]
    kk = (2.0 * np.pi) ** 2 * (kx ** 2 + ky ** 2 + kz ** 2)
    filt = np.exp(-0.5 * sigma ** 2 * kk).astype(dtype, copy=False)
    complex_dtype = np.complex64 if dtype == np.float32 else np.complex128
    transformed = fftn(field.astype(complex_dtype, copy=False))
    return ifftn(transformed * filt).real.astype(dtype, copy=False)


def grad_3d(field: Array, dx: float, dy: float, dz: float) -> tuple[Array, Array, Array]:
    """Centered periodic finite-difference gradient."""
    gx = (np.roll(field, -1, 0) - np.roll(field, 1, 0)) / (2.0 * dx)
    gy = (np.roll(field, -1, 1) - np.roll(field, 1, 1)) / (2.0 * dy)
    gz = (np.roll(field, -1, 2) - np.roll(field, 1, 2)) / (2.0 * dz)
    return (
        gx.astype(field.dtype, copy=False),
        gy.astype(field.dtype, copy=False),
        gz.astype(field.dtype, copy=False),
    )


def power_spectrum_3d(field: Array, dx: float, dy: float, dz: float) -> tuple[Array, Array]:
    """Spherically averaged toy P(k) estimate with simple binning."""
    dtype = field.dtype
    centered = field - field.mean(dtype=dtype)
    volume = max(float(field.size) * dx * dy * dz, 1e-30)
    transformed = fftn(centered)
    power_grid = (transformed * np.conj(transformed)).real / volume

    nx, ny, nz = field.shape
    kx = fftfreq(nx, d=dx)
    ky = fftfreq(ny, d=dy)
    kz = fftfreq(nz, d=dz)
    kxg, kyg, kzg = np.meshgrid(kx, ky, kz, indexing="ij")
    radii = np.sqrt(kxg ** 2 + kyg ** 2 + kzg ** 2)

    nbins = max(min(nx, ny, nz) // 2, 2)
    bins = np.linspace(0.0, float(radii.max()), nbins + 1)
    which = np.digitize(radii.ravel(), bins) - 1

    pk = np.zeros(nbins, dtype=dtype)
    flat_power = power_grid.ravel()
    for idx in range(1, nbins):  # skip DC bin
        selected = which == idx
        if np.any(selected):
            pk[idx] = flat_power[selected].mean().astype(dtype, copy=False)

    kcenters = (0.5 * (bins[:-1] + bins[1:])).astype(dtype, copy=False)
    return kcenters, pk


# -----------------------------------------------------------------------------
# Model blocks
# -----------------------------------------------------------------------------

def switching_s(a: float, a_star: float, m: float) -> float:
    """Smooth activation gate."""
    return 1.0 / (1.0 + (a_star / max(a, 1e-12)) ** m)


def info_metric_i(rho: Array, smooth_passes: int = 2) -> Array:
    """Local roughness proxy normalised to [0, 1]."""
    eps = np.finfo(rho.dtype).eps
    log_rho = np.log(rho + eps)
    smooth = log_rho.copy()
    for _ in range(smooth_passes):
        smooth = gaussian_blur_fft_3d(smooth, 1.0)
    rough = np.abs(log_rho - smooth)
    rough -= rough.min()
    rng = rough.max()
    if rng > 0:
        rough /= rng
    return rough.astype(rho.dtype, copy=False)


def redundancy_rbar(rho: Array) -> tuple[float, Array]:
    """Return a scalar redundancy proxy and the local roughness field."""
    i_field = info_metric_i(rho, smooth_passes=2)
    variance = float(np.var(i_field, dtype=np.float64))
    rbar = 1.0 / (1.0 + 5.0 * variance)
    return rbar, i_field


def multiscale_rho_rec(rho_b: Array, sigmas: list[float], i_field: Array, nu: float, i0: float) -> Array:
    """Complexity-weighted blend of small-scale and large-scale blur fields."""
    if not sigmas:
        return rho_b.copy()
    blurs = [gaussian_blur_fft_3d(rho_b, float(sigma)) for sigma in sigmas]
    i_weight = np.power(np.clip(i_field / max(i0, 1e-6), 0.0, 1.0), nu)
    small = blurs[0]
    large = blurs[-1]
    rho_rec = (1.0 - i_weight) * small + i_weight * large
    return rho_rec.astype(rho_b.dtype, copy=False)


def mu_coefficient(i_field: Array, mu0: float, eta: float, i0: float, s_gate: float) -> Array:
    """Variable coefficient for the toy Poisson solve."""
    coeff = 1.0 + mu0 * s_gate * np.power(np.clip(i_field / max(i0, 1e-6), 0.0, 1.0), eta)
    return coeff.astype(i_field.dtype, copy=False)


def solve_variable_poisson_3d(
    coeff: Array,
    rhs: Array,
    dx: float,
    dy: float,
    dz: float,
    iters: int = 600,
    omega: float = 0.6,
    tol: float = 1e-5,
    check_every: int = 10,
) -> Array:
    """Damped Jacobi/SOR-like solve for div(mu grad Phi) = rhs on a periodic grid."""
    phi = np.zeros_like(rhs)
    invdx2 = 1.0 / dx ** 2
    invdy2 = 1.0 / dy ** 2
    invdz2 = 1.0 / dz ** 2
    eps = np.finfo(rhs.dtype).eps
    rhs = (rhs - rhs.mean(dtype=np.float64)).astype(rhs.dtype, copy=False)
    rhs_norm = max(float(np.linalg.norm(rhs.astype(np.float64))), 1.0) 
    for iteration in range(max(int(iters), 1)):
        kxp = 2.0 * coeff * np.roll(coeff, -1, 0) / (coeff + np.roll(coeff, -1, 0) + eps)
        kxm = 2.0 * coeff * np.roll(coeff, 1, 0) / (coeff + np.roll(coeff, 1, 0) + eps)
        kyp = 2.0 * coeff * np.roll(coeff, -1, 1) / (coeff + np.roll(coeff, -1, 1) + eps)
        kym = 2.0 * coeff * np.roll(coeff, 1, 1) / (coeff + np.roll(coeff, 1, 1) + eps)
        kzp = 2.0 * coeff * np.roll(coeff, -1, 2) / (coeff + np.roll(coeff, -1, 2) + eps)
        kzm = 2.0 * coeff * np.roll(coeff, 1, 2) / (coeff + np.roll(coeff, 1, 2) + eps)

        diagonal = (
            (kxp + kxm) * invdx2
            + (kyp + kym) * invdy2
            + (kzp + kzm) * invdz2
            + eps
        )

        ax = (kxp * np.roll(phi, -1, 0) - (kxp + kxm) * phi + kxm * np.roll(phi, 1, 0)) * invdx2
        ay = (kyp * np.roll(phi, -1, 1) - (kyp + kym) * phi + kym * np.roll(phi, 1, 1)) * invdy2
        az = (kzp * np.roll(phi, -1, 2) - (kzp + kzm) * phi + kzm * np.roll(phi, 1, 2)) * invdz2

        residual = rhs - (ax + ay + az)
        phi -= omega * residual / diagonal
        phi -= phi.mean(dtype=np.float64)

        if iteration % max(int(check_every), 1) == 0:
            relative_residual = float(np.linalg.norm(residual.astype(np.float64)) / rhs_norm)
            if relative_residual < tol:
                break

    return phi.astype(rhs.dtype, copy=False)


def advect_semi_lagrangian_3d(rho: Array, vx: Array, vy: Array, vz: Array, dt: float, dx: float, dy: float, dz: float) -> Array:
    """Trilinear semi-Lagrangian advection with periodic wrapping."""
    dtype = rho.dtype
    nx, ny, nz = rho.shape
    x, y, z = np.meshgrid(np.arange(nx), np.arange(ny), np.arange(nz), indexing="ij")

    xb = (x - vx * dt / dx) % nx
    yb = (y - vy * dt / dy) % ny
    zb = (z - vz * dt / dz) % nz

    x0 = np.floor(xb).astype(np.int64)
    y0 = np.floor(yb).astype(np.int64)
    z0 = np.floor(zb).astype(np.int64)
    x1 = (x0 + 1) % nx
    y1 = (y0 + 1) % ny
    z1 = (z0 + 1) % nz

    sx = (xb - x0).astype(dtype, copy=False)
    sy = (yb - y0).astype(dtype, copy=False)
    sz = (zb - z0).astype(dtype, copy=False)

    out = (
        (1.0 - sx) * (1.0 - sy) * (1.0 - sz) * rho[x0, y0, z0]
        + sx * (1.0 - sy) * (1.0 - sz) * rho[x1, y0, z0]
        + (1.0 - sx) * sy * (1.0 - sz) * rho[x0, y1, z0]
        + (1.0 - sx) * (1.0 - sy) * sz * rho[x0, y0, z1]
        + sx * sy * (1.0 - sz) * rho[x1, y1, z0]
        + sx * (1.0 - sy) * sz * rho[x1, y0, z1]
        + (1.0 - sx) * sy * sz * rho[x0, y1, z1]
        + sx * sy * sz * rho[x1, y1, z1]
    )
    return out.astype(dtype, copy=False)


def project_convergence(delta: Array, chi_max: float) -> Array:
    """Toy convergence map kappa proportional to integral W(chi) delta(chi) dchi.

    The line of sight is axis 0. The output has shape (ny, nz).
    """
    nx, _, _ = delta.shape
    chi = np.linspace(0.0, chi_max, nx, dtype=delta.dtype)
    kernel = (chi * (chi_max - chi)) / max(chi_max, 1e-12)
    kernel = kernel.reshape(nx, 1, 1)
    kappa = np.sum(delta * kernel, axis=0)
    max_abs = float(np.max(np.abs(kappa)))
    if max_abs > 0:
        kappa = kappa / max_abs
    return kappa.astype(delta.dtype, copy=False)


# -----------------------------------------------------------------------------
# Main simulation
# -----------------------------------------------------------------------------

def make_initial_density(cfg: dict[str, Any], rng: np.random.Generator, dtype: np.dtype) -> Array:
    nx, ny, nz = int(cfg["nx"]), int(cfg["ny"]), int(cfg["nz"])
    lx, ly, lz = float(cfg["lx"]), float(cfg["ly"]), float(cfg["lz"])
    x = np.linspace(0.0, lx, nx, endpoint=False, dtype=dtype) 
    y = np.linspace(0.0, ly, ny, endpoint=False, dtype=dtype) 
    z = np.linspace(0.0, lz, nz, endpoint=False, dtype=dtype)
    xg, yg, zg = np.meshgrid(x, y, z, indexing="ij")

    rho_b = np.zeros((nx, ny, nz), dtype=dtype)
    if cfg["baryon_profile"] == "blobs":
        for _ in range(int(cfg["n_blobs"])):
            cx, cy, cz = rng.uniform(0.0, lx), rng.uniform(0.0, ly), rng.uniform(0.0, lz)
            sigma = rng.uniform(3.0, 10.0)
            amplitude = rng.uniform(0.5, 1.5)
            rho_b += amplitude * np.exp(-((xg - cx) ** 2 + (yg - cy) ** 2 + (zg - cz) ** 2) / (2.0 * sigma ** 2))
        rho_b += 0.05 * np.exp(-((xg - lx / 2.0) ** 2 + (yg - ly / 2.0) ** 2 + (zg - lz / 2.0) ** 2) / (2.0 * 30.0 ** 2))
    else:
        radius = np.sqrt((xg - lx / 2.0) ** 2 + (yg - ly / 2.0) ** 2 + (zg - lz / 2.0) ** 2)
        rho_b = np.exp(-(radius / 20.0) ** 2) + 0.05 * np.exp(-(radius / 5.0) ** 2)

    return np.maximum(rho_b.astype(dtype, copy=False), np.finfo(dtype).tiny)


def save_slice(path: Path, field: Array, title: str, extent: list[float]) -> None:
    plt.figure(figsize=(6, 5))
    plt.imshow(field.T, origin="lower", extent=extent)
    plt.title(title)
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()


def run(cfg: dict[str, Any]) -> dict[str, list[float]]:
    dtype = np.float32
    nx, ny, nz = int(cfg["nx"]), int(cfg["ny"]), int(cfg["nz"])
    lx, ly, lz = float(cfg["lx"]), float(cfg["ly"]), float(cfg["lz"])
    dx, dy, dz = lx / nx, ly / ny, lz / nz
    outdir = Path(cfg["outdir"])
    outdir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(int(cfg["rng_seed"]))
    rho_b = make_initial_density(cfg, rng, dtype)
    vx = np.zeros_like(rho_b)
    vy = np.zeros_like(rho_b)
    vz = np.zeros_like(rho_b)

    omega_b0 = float(cfg["Omega_b0"])
    omega_l0 = float(cfg["Omega_L0"])
    h0 = float(cfg["H0"])
    rho_l = float(omega_l0)
    a = float(cfg["a_start"])
    a_end = float(cfg["a_end"])
    dt_phys = float(cfg["dt_phys"])

    history: dict[str, list[float]] = {"a": [], "H": [], "w": [], "Rbar": [], "Pk_amp": []}

    for step in range(int(cfg["n_steps"]) + 1):
        rbar, i_field = redundancy_rbar(rho_b)
        xi = 0.0 if not history["Rbar"] else abs(rbar - history["Rbar"][-1]) / max(dt_phys, 1e-12)
        w = -1.0 + float(cfg["alpha"]) * rbar + float(cfg["beta"]) * xi

        h = h0 * np.sqrt(omega_b0 * max(a, 1e-12) ** (-3.0) + max(rho_l, 0.0))
        a_next = min(a + a * h * dt_phys, a_end)
        dln_a = np.log(max(a_next, 1e-12)) - np.log(max(a, 1e-12))
        rho_l *= np.exp(-3.0 * (1.0 + w) * dln_a)

        s_gate = switching_s(a, float(cfg["a_star"]), float(cfg["gate_m"]))
        rho_rec = multiscale_rho_rec(rho_b, list(cfg["ell_sigmas"]), i_field, float(cfg["nu"]), float(cfg["I0"]))
        coeff = mu_coefficient(i_field, float(cfg["mu0"]), float(cfg["eta"]), float(cfg["I0"]), s_gate)
        rhs = (float(cfg["G4pi"]) * (rho_b + rho_rec)).astype(dtype, copy=False)

        phi = solve_variable_poisson_3d(
            coeff,
            rhs,
            dx,
            dy,
            dz,
            iters=int(cfg["poisson_iters"]),
            omega=float(cfg["poisson_omega"]),
            tol=float(cfg["poisson_tol"]),
            check_every=int(cfg["poisson_check_every"]),
        )

        gx, gy, gz = grad_3d(phi, dx, dy, dz)
        ax = -gx / max(a, 1e-12)
        ay = -gy / max(a, 1e-12)
        az = -gz / max(a, 1e-12)
        hfac = 1.0 + h * dt_phys 
        vx = (vx + ax * dt_phys) / hfac 
        vy = (vy + ay * dt_phys) / hfac 
        vz = (vz + az * dt_phys) / hfac 

        v_cap = (
            float(cfg.get("courant_cap", 0.5))
            * min(dx, dy, dz)
            / max(dt_phys, 1.0e-12)
        )
        speed = np.sqrt(vx * vx + vy * vy + vz * vz)
        scale = np.minimum(
            1.0,
            v_cap / (speed + np.finfo(dtype).tiny),
        ) 
        vx *= scale 
        vy *= scale 
        vz *= scale 

        rho_b = advect_semi_lagrangian_3d(rho_b, vx, vy, vz, dt_phys, dx, dy, dz)        
        rho_b = np.maximum(rho_b, np.finfo(dtype).tiny)

        kcenters, pk = power_spectrum_3d(rho_b, dx, dy, dz)
        pk_amp = float(np.trapezoid(pk.astype(np.float64), kcenters.astype(np.float64)))

        history["a"].append(float(a))
        history["H"].append(float(h))
        history["w"].append(float(w))
        history["Rbar"].append(float(rbar))
        history["Pk_amp"].append(pk_amp)

        if step % max(int(cfg["save_every"]), 1) == 0:
            mid = nz // 2
            save_slice(outdir / f"rho_b_{step:04d}.png", rho_b[:, :, mid], f"rho_b midplane step {step} a={a:.3f}", [0, lx, 0, ly])
            save_slice(outdir / f"phi_{step:04d}.png", phi[:, :, mid], f"Phi midplane step {step}", [0, lx, 0, ly])
            delta = (rho_b / max(float(rho_b.mean()), 1e-12) - 1.0).astype(dtype, copy=False)
            kappa = project_convergence(delta, lz)
            save_slice(outdir / f"kappa_{step:04d}.png", kappa, f"kappa proxy step {step}", [0, ly, 0, lz])

        a = a_next
        if a >= a_end:
            break

    with (outdir / "history_3d.json").open("w", encoding="utf-8") as handle:
        json.dump(history, handle, indent=2)

    for key, ylabel, filename, title in [
        ("w", "w(a)", "history_w.png", "Overhead-rebate equation of state"),
        ("H", "H(a) [code units]", "history_H.png", "Background expansion"),
        ("Pk_amp", "P(k) amplitude proxy", "history_Pk.png", "Structure growth proxy"),
    ]:
        plt.figure(figsize=(7, 5))
        plt.plot(history["a"], history[key])
        plt.xlabel("a")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(outdir / filename, dpi=140)
        plt.close()

    print(f"Done. Outputs written to {outdir}")
    return history


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="3-D structured-efficiency pedagogical prototype")
    parser.add_argument("--nx", type=int, default=64)
    parser.add_argument("--ny", type=int, default=64)
    parser.add_argument("--nz", type=int, default=64)
    parser.add_argument("--lx", type=float, default=200.0)
    parser.add_argument("--ly", type=float, default=200.0)
    parser.add_argument("--lz", type=float, default=200.0)
    parser.add_argument("--G4pi", type=float, default=1.0)
    parser.add_argument("--a-start", dest="a_start", type=float, default=0.02)
    parser.add_argument("--a-end", dest="a_end", type=float, default=1.0)
    parser.add_argument("--n-steps", dest="n_steps", type=int, default=120) 
    parser.add_argument("--dt-phys", dest="dt_phys", type=float, default=0.5)
    parser.add_argument("--courant-cap", dest="courant_cap", type=float, default=0.5)    
    parser.add_argument("--a-star", dest="a_star", type=float, default=9.0e-4)
    parser.add_argument("--gate-m", dest="gate_m", type=float, default=8.0)
    parser.add_argument("--mu0", type=float, default=2.0)
    parser.add_argument("--eta", type=float, default=0.35)
    parser.add_argument("--I0", type=float, default=0.5)
    parser.add_argument("--nu", type=float, default=0.35)
    parser.add_argument("--ell-sigmas", dest="ell_sigmas", type=float, nargs="+", default=[1.5, 4.0, 8.0, 16.0])
    parser.add_argument("--poisson-iters", dest="poisson_iters", type=int, default=600)
    parser.add_argument("--poisson-omega", dest="poisson_omega", type=float, default=0.6)
    parser.add_argument("--poisson-tol", dest="poisson_tol", type=float, default=1e-5)
    parser.add_argument("--poisson-check-every", dest="poisson_check_every", type=int, default=10)
    parser.add_argument("--alpha", type=float, default=0.2)
    parser.add_argument("--beta", type=float, default=0.1)
    parser.add_argument("--Omega-b0", dest="Omega_b0", type=float, default=0.05)
    parser.add_argument("--Omega-L0", dest="Omega_L0", type=float, default=0.7)
    parser.add_argument("--H0", type=float, default=1.0)
    parser.add_argument("--rng-seed", dest="rng_seed", type=int, default=7)
    parser.add_argument("--baryon-profile", dest="baryon_profile", choices=["blobs", "sphere"], default="blobs")
    parser.add_argument("--n-blobs", dest="n_blobs", type=int, default=10)
    parser.add_argument("--save-every", dest="save_every", type=int, default=20)
    parser.add_argument("--outdir", type=str, default="out_3d_stable")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    cfg = vars(args)
    run(cfg)


if __name__ == "__main__":
    main()
