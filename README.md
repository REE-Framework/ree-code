# REE Code

[![Tests](https://github.com/REE-Framework/ree-code/actions/workflows/tests.yml/badge.svg)](https://github.com/REE-Framework/ree-code/actions/workflows/tests.yml)
[![License: BSD 3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](LICENSE)
[![Project website](https://img.shields.io/badge/website-ree--framework.org-informational.svg)](https://www.ree-framework.org/)

Reference implementations, toy models, diagnostic tools, and reproducibility materials for **Recursive Epistemic Economy (REE)**, a finite-*c* framework for testing structured-efficiency cosmology under explicit runtime, readout, and admissibility constraints.

**Project website:** [www.ree-framework.org](https://www.ree-framework.org/)  
**Repository:** [github.com/REE-Framework/ree-code](https://github.com/REE-Framework/ree-code)

## Release status

This is **v0.1.0**, the initial public code package. It provides functional demonstrations and reusable analysis utilities, not a claim that the full REE physical programme has been numerically completed.

The package separates:

- **registered metadata**, which mirrors declared REE discriminator labels and status;
- **validation utilities**, which test numerical and readout behaviour;
- **demonstrations**, which instantiate finite-speed fronts and boundary ledgers;
- **exploratory code**, which must not be represented as canonical prediction code without explicit promotion.

A successful run shows that the implementation behaves as declared. It does not establish an ontological interpretation or empirical confirmation of REE.

## Included packages

| Package | Purpose | Scientific status in v0.1.0 |
|---|---|---|
| `ree.algorithm_a` | Finite-speed damped-wave front demonstration with scheme-specific CFL validation | Demonstration / validation scaffold |
| `ree.readout` | Coarse-graining, quantized finite-resolution readout, and RRIP-style comparison | General validation utility |
| `ree.null_compute` | Conservative one-dimensional boundary-ledger demonstration | Demonstration / accounting utility |
| `ree.discriminators` | Versioned register metadata plus P7 and phase-resolution helpers | Metadata and selected registered formulae |
| `ree.reproducibility` | SHA-256 manifests and environment capture | Reproducibility utility |

The package map and limitations are described in [`docs/PACKAGE_MAP.md`](docs/PACKAGE_MAP.md) and [`docs/SCIENTIFIC_SCOPE.md`](docs/SCIENTIFIC_SCOPE.md).

## Installation

Python 3.11 or later is required.

```bash
git clone https://github.com/REE-Framework/ree-code.git
cd ree-code
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS or Linux
source .venv/bin/activate
```

Install:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

For tests and development tools:

```bash
python -m pip install -e ".[dev]"
```

## Quick checks

Run the complete test suite:

```bash
python -m pytest
```

List the REE discriminator metadata:

```bash
ree registry
```

Evaluate the registered P7 frequency scaling:

```bash
ree p7 --frequency 1000 100 10 0.001
```

Run a finite-speed front demonstration:

```bash
ree front-demo --shape 24,24,24 --steps 20
```

Run the conservative boundary-ledger demonstration:

```bash
ree ledger-demo --cells 256 --steps 220
```

Run a finite-resolution readout comparison:

```bash
ree rrip-demo
```

## Examples

Standalone examples are in [`examples/`](examples/):

```bash
python examples/front_demo.py
python examples/readout_demo.py
python examples/null_compute_ledger_demo.py
python examples/p7_target_demo.py
python examples/registry_demo.py
```

Example configurations are stored in [`configs/`](configs/). Frozen small reference outputs are stored in [`results/reference/`](results/reference/).

## Three-layer discipline

REE distinguishes:

1. **Epistemic:** what embedded observers can certify under finite-*c*, finite-window conditions.
2. **Constructive:** explicit update schemes and reduced descriptions satisfying declared admissibility rules.
3. **Ontological:** proposed physical interpretations of the regularities generated or captured by the constructive layer.

Most code in this repository belongs to the constructive layer. The readout package also supports epistemic comparisons. Neither automatically establishes an ontological conclusion.

## Reproducibility contract

A reproducible result should record:

- repository release or commit identifier;
- Python and dependency versions;
- configuration file;
- input version or checksum;
- random seed, where applicable;
- numerical resolution and timestep;
- stopping rule;
- admissibility and convergence tolerances;
- output statistic and command used.

Create a manifest for files used in an analysis:

```bash
ree manifest configs/algorithm_a_demo.json results/reference/front_demo_summary.json
```

See [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

## Registered versus exploratory material

Code or results should be labelled as one of:

- **Registered** — tied to a frozen REE discriminator, threshold, or readout rule.
- **Validation** — checks numerical correctness, convergence, conservation, or known limits.
- **Demonstration** — illustrates a declared mechanism without claiming a realistic full model.
- **Exploratory** — investigates an unregistered extension or candidate discriminator.
- **Retired** — retained for provenance but not active in the current framework.

Exploratory material must not be presented as an REE prediction merely because it resides in this repository.

## Citation

Citation metadata is provided in [`CITATION.cff`](CITATION.cff). Until an archived software DOI is assigned, cite the numbered GitHub release and the relevant REE publication.

Suggested form:

> Lundqvist, Mats J. *REE Code: Reference implementations and reproducibility materials for Recursive Epistemic Economy*. Version 0.1.0, 2026. GitHub release.

## Contributing

Corrections, tests, reproducibility improvements, and clearly labelled exploratory contributions are welcome. A merged contribution does not automatically become canonical REE. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licence

Source code is licensed under the **BSD 3-Clause License**. See [`LICENSE`](LICENSE).

The licence does not automatically cover REE book text, diagrams, website content, project identity, or third-party material.

## Author

**Mats J Lundqvist**  
Recursive Epistemic Economy  
[www.ree-framework.org](https://www.ree-framework.org/)

## Disclaimer

This repository contains research software, conceptual models, and numerical demonstrations. It is supplied without warranty and is not independently validated physical theory, production infrastructure, or a substitute for domain-specific verification.
