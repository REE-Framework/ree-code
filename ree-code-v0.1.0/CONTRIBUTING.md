# Contributing

Contributions should improve correctness, reproducibility, documentation,
testing, or clearly labelled exploration.

Before opening a pull request:

1. Identify the issue or purpose of the change.
2. Label it as corrective, validation, demonstration, exploratory, or proposed canonical work.
3. Identify affected manuscript references, configuration files, and outputs.
4. Add or update tests.
5. Record changed numerical outputs and their cause.
6. Update documentation and `CHANGELOG.md` where appropriate.

A merged contribution does not automatically become canonical REE. Canonical
promotion requires explicit review against the relevant admissibility, readout,
discriminator, notation, and cross-document consistency rules.

## Code style

- Python 3.11 or later.
- Type annotations for public functions.
- Clear docstrings stating scientific status and assumptions.
- No silent correction of inadmissible numerical settings.
- Deterministic tests where practical.
- `ruff check .` and `pytest` should pass.
