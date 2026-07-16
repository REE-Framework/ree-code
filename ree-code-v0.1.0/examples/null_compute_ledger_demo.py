"""Run the conservative retained-domain boundary-ledger demonstration."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from ree.null_compute import run_demo

config = json.loads(Path("configs/null_compute_demo.json").read_text(encoding="utf-8"))
_, ledger, records = run_demo(
    cells=config["cells"],
    steps=config["steps"],
    speed=config["speed"],
    length=config["length"],
    courant=config["courant"],
    sample_every=config["sample_every"],
)
print(
    json.dumps(
        {
            "initial_quantity": ledger.initial_quantity,
            "records": [asdict(item) for item in records],
        },
        indent=2,
    )
)
