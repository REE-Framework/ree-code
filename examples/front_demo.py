"""Run the finite-speed front demonstration from the frozen example config."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from ree.algorithm_a import AlgorithmAConfig, initialize_gaussian, run, summarize

config_data = json.loads(Path("configs/algorithm_a_demo.json").read_text(encoding="utf-8"))
config = AlgorithmAConfig(
    shape=tuple(config_data["shape"]),
    dx=config_data["dx"],
    dt=config_data["dt"],
    signal_speed=config_data["signal_speed"],
    damping=config_data["damping"],
    mass=config_data["mass"],
    boundary=config_data["boundary"],
)
state = initialize_gaussian(
    config,
    amplitude=config_data["seed_amplitude"],
    width=config_data["seed_width"],
)
final, history = run(state, config, config_data["steps"], sample_every=5)
print(
    json.dumps(
        {"final": asdict(summarize(final, config)), "history": [asdict(item) for item in history]},
        indent=2,
    )
)
