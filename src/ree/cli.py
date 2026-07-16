"""Command-line interface for the initial REE code package."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .algorithm_a import AlgorithmAConfig, initialize_gaussian, run, summarize
from .discriminators import list_discriminators, p7_residual_target
from .null_compute import run_demo
from .readout import ReadoutSpec, compare
from .reproducibility import write_manifest


def _shape(value: str) -> tuple[int, ...]:
    try:
        parsed = tuple(int(item.strip()) for item in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("shape must be comma-separated integers") from exc
    if not parsed:
        raise argparse.ArgumentTypeError("shape cannot be empty")
    return parsed


def _front_demo(args: argparse.Namespace) -> int:
    config = AlgorithmAConfig(
        shape=args.shape,
        dx=args.dx,
        dt=args.dt,
        signal_speed=args.speed,
        damping=args.damping,
        boundary=args.boundary,
    )
    state = initialize_gaussian(config, width=args.width)
    final, _ = run(state, config, args.steps)
    print(json.dumps(asdict(summarize(final, config)), indent=2, sort_keys=True))
    return 0


def _ledger_demo(args: argparse.Namespace) -> int:
    _, ledger, records = run_demo(
        cells=args.cells,
        steps=args.steps,
        speed=args.speed,
        courant=args.courant,
        sample_every=max(1, args.steps),
    )
    final = records[-1]
    payload = asdict(final)
    payload["initial_quantity"] = ledger.initial_quantity
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _rrip_demo(_: argparse.Namespace) -> int:
    left = np.zeros((8, 8), dtype=np.float64)
    right = left.copy()
    right[2:4, 2:4] = 0.02
    spec = ReadoutSpec(block=2, resolution=0.05, tolerance=0.0, norm="linf")
    print(json.dumps(asdict(compare(left, right, spec)), indent=2, sort_keys=True))
    return 0


def _registry(args: argparse.Namespace) -> int:
    entries = list_discriminators(status=args.status, regime=args.regime)
    if args.json:
        print(json.dumps([item.to_dict() for item in entries], indent=2, sort_keys=True))
    else:
        for item in entries:
            print(f"{item.label:4}  {item.programme_status:20}  {item.title}")
    return 0


def _p7(args: argparse.Namespace) -> int:
    frequencies = np.asarray(args.frequency, dtype=np.float64)
    targets = p7_residual_target(frequencies, h0=args.h0, f0_hz=args.f0)
    for frequency, target in zip(frequencies, targets, strict=True):
        print(f"{frequency:g} Hz\t{target:.12e}")
    return 0


def _manifest(args: argparse.Namespace) -> int:
    destination = write_manifest(args.output, args.files, metadata_fields={"release": "0.1.0"})
    print(destination)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ree", description="REE reference and reproducibility tools"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    front = subparsers.add_parser("front-demo", help="run the finite-speed front demonstration")
    front.add_argument("--shape", type=_shape, default=(24, 24, 24))
    front.add_argument("--steps", type=int, default=20)
    front.add_argument("--dx", type=float, default=1.0)
    front.add_argument("--dt", type=float, default=0.25)
    front.add_argument("--speed", type=float, default=1.0)
    front.add_argument("--damping", type=float, default=0.05)
    front.add_argument("--width", type=float, default=3.0)
    front.add_argument("--boundary", choices=("periodic", "reflecting"), default="periodic")
    front.set_defaults(func=_front_demo)

    ledger = subparsers.add_parser("ledger-demo", help="run the conservative boundary ledger")
    ledger.add_argument("--cells", type=int, default=256)
    ledger.add_argument("--steps", type=int, default=220)
    ledger.add_argument("--speed", type=float, default=1.0)
    ledger.add_argument("--courant", type=float, default=0.8)
    ledger.set_defaults(func=_ledger_demo)

    rrip = subparsers.add_parser("rrip-demo", help="run a finite-resolution comparison")
    rrip.set_defaults(func=_rrip_demo)

    registry = subparsers.add_parser("registry", help="list discriminator metadata")
    registry.add_argument("--status")
    registry.add_argument("--regime")
    registry.add_argument("--json", action="store_true")
    registry.set_defaults(func=_registry)

    p7 = subparsers.add_parser("p7", help="evaluate the P7 strain-amplitude target")
    p7.add_argument("--frequency", type=float, nargs="+", required=True)
    p7.add_argument("--h0", type=float, default=1e-24)
    p7.add_argument("--f0", type=float, default=1000.0)
    p7.set_defaults(func=_p7)

    manifest = subparsers.add_parser("manifest", help="create a SHA-256 reproducibility manifest")
    manifest.add_argument("files", nargs="+")
    manifest.add_argument("--output", type=Path, default=Path("ree-manifest.json"))
    manifest.set_defaults(func=_manifest)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
