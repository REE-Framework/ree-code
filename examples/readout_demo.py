"""Compare distinct fine-grained states under a finite readout map."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from ree.readout import ReadoutSpec, compare

config = json.loads(Path("configs/readout_demo.json").read_text(encoding="utf-8"))
left = np.zeros((8, 8))
right = left.copy()
right[2:4, 2:4] = 0.02
spec = ReadoutSpec(
    block=config["block"],
    resolution=config["resolution"],
    tolerance=config["tolerance"],
    norm=config["norm"],
)
print(json.dumps(asdict(compare(left, right, spec)), indent=2))
