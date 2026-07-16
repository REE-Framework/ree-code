# ree-code

Reference implementations, toy models, diagnostic tools, and reproducibility materials for Recursive Epistemic Economy (REE), a finite-c framework for testing structured-efficiency cosmology under explicit runtime, readout, and admissibility constraints.

Project website: www.ree-framework.org

[b]Status[/b]

This repository is research software under active development.

Unless a release is explicitly marked otherwise:

implementations should be treated as provisional;
interfaces, configuration formats, and numerical defaults may change;
toy models are demonstrations of declared mechanisms, not full cosmological simulations;
exploratory results are not part of the canonical REE claim set;
the manuscript and release notes remain authoritative for scientific scope.

For reproducible work, use a numbered release rather than the moving main branch.

Project context

Recursive Epistemic Economy begins from a simple operational constraint: a physical law must remain executable and verifiable under finite signal speed, finite resolution, finite runtime, and finite institutional or observational windows, without hidden supertasks.

The wider REE programme examines whether familiar continuum laws can arise as stable coarse-grained limits of constructive finite-resource dynamics, and whether any finite-resolution remainders produce registered empirical signatures.

This repository contains the executable side of that programme. It is intended to make assumptions, update rules, tolerances, readout maps, nuisance controls, and numerical tests inspectable and reproducible.

It does not convert an interpretive claim into an established physical result merely because code can instantiate it.

Three-layer discipline

REE distinguishes three levels:

Epistemic level — what embedded observers can certify under finite-c, finite-window conditions.
Constructive level — explicit update schemes and reduced descriptions satisfying declared admissibility rules.
Ontological level — proposed physical interpretations of the regularities generated or captured by the constructive level.

The code in this repository belongs primarily to the constructive level and, where it implements registered observables or readout procedures, to the epistemic level.

A successful numerical run at level 2 does not by itself establish a level-3 interpretation. Promotion of any interpretation requires independent empirical discrimination under the registered REE protocol.

Repository scope

The repository is organised to support the following classes of material:

constructive update schemes and toy implementations;
finite-c runtime and admissibility checks;
readout maps and Runtime-Readout Indistinguishability Principle (RRIP) tests;
registered discriminator calculations;
boundary-ledger and null-compute demonstrations;
numerical conservation and convergence tests;
scripts used to reproduce selected figures, tables, or reference outputs;
configuration files defining declared parameter choices and tolerances;
documentation connecting code components to the relevant manuscript sections.

Only components actually present in a numbered release should be treated as implemented. Planned modules, commented stubs, issue discussions, and development branches are non-canonical.

Repository layout
ree-code/
├── README.md
├── LICENSE
├── CITATION.cff
├── CHANGELOG.md
├── pyproject.toml
├── src/
│   └── ree/
├── configs/
├── examples/
├── tests/
├── docs/
├── notebooks/
├── data/
│   └── README.md
├── results/
│   └── reference/
└── .github/
    ├── workflows/
    └── ISSUE_TEMPLATE/

The exact contents may differ between releases. Each implemented component should include:

its purpose;
scientific status;
governing assumptions;
input and output definitions;
units and sign conventions;
the command needed to run it;
expected reference behaviour;
known limitations;
the manuscript section or discriminator to which it corresponds.
Quick start
1. Clone the repository
git clone https://github.com/REE-Framework/ree-code.git
cd ree-code
2. Create a virtual environment

Windows:

python -m venv .venv
.venv\Scripts\Activate.ps1

macOS or Linux:

python3 -m venv .venv
source .venv/bin/activate
3. Install the package
python -m pip install --upgrade pip
python -m pip install -e .

For development and testing:

python -m pip install -e ".[dev]"

The supported Python version and dependency constraints are defined in pyproject.toml. That file is authoritative.

4. Run the tests
python -m pytest
5. Run an example

Executable examples are stored in examples/. Each example should state its exact command, configuration file, expected runtime class, and expected output.

python examples/<example_name>.py

Do not assume that an example uses canonical or preregistered settings unless its documentation says so explicitly.

Reproducibility contract

A result should be described as reproducible from this repository only when the following are recorded:

repository release or commit identifier;
Python and dependency versions;
configuration file;
input data version or checksum;
random seed, where applicable;
hardware or accelerator assumptions, where materially relevant;
numerical resolution and timestep;
stopping rule;
admissibility and convergence tolerances;
nuisance model and control settings;
output statistic and uncertainty convention;
command used to generate the result.

Reference outputs belong in results/reference/ or in a release archive. Large external datasets should not be committed directly unless their licence and size make that appropriate. Instead, data/README.md should identify the source, version, checksum, preprocessing procedure, and access conditions.

A changed numerical default is a scientific change when it can alter a registered conclusion. Such changes must be recorded in CHANGELOG.md and, where applicable, in the release notes.

Numerical and scientific safeguards

Implemented numerical models should include, where relevant:

scheme-specific CFL or stability checks;
finite-speed propagation constraints;
convergence tests across declared resolutions;
normalized energy or ledger residuals;
explicit boundary-flux sign conventions;
deterministic tests for limiting cases;
dimensional checks;
regression tests against frozen reference outputs;
failure on inadmissible parameter combinations rather than silent correction;
separation of detector-domain thresholds from underlying model amplitudes.

Passing a software test means that the implementation behaves as declared. It does not mean that the physical hypothesis has been empirically confirmed.

Registered versus exploratory material

Repository content should be labelled using the following categories:

Registered — implements a frozen discriminator, threshold, readout rule, or analysis path tied to a numbered REE release.
Validation — tests numerical correctness, convergence, conservation, dimensional consistency, or recovery of known limits.
Demonstration — illustrates a mechanism or constructive possibility without claiming a realistic physical model.
Exploratory — investigates an unregistered extension, alternative parameterization, or candidate discriminator.
Retired — preserved for provenance but no longer active in the current framework.

Exploratory material must not be presented as a prediction of REE until it has passed the framework’s declared promotion procedure.

Relation to the REE publications

The principal work is:

Recursive Epistemic Economy — A framework for cosmic reproduction: Structured-efficiency cosmology in a finite-c information universe
Mats J Lundqvist

The REE project also includes a narrative companion and technical companion appendices.

The project website provides publication information, current release status, and links:

https://www.ree-framework.org/

Where code corresponds to a publication section, the local documentation should identify:

volume;
part, chapter, section, or appendix;
equation, proposition, algorithm, or discriminator label;
manuscript version;
code release first implementing it.

Code and manuscript versions may develop at different rates. A result should therefore cite both when the correspondence matters.

Versioning

This repository uses semantic versioning where practical:

Patch release — corrections that do not intentionally change scientific scope.
Minor release — new components, new diagnostics, or backward-compatible scientific extensions.
Major release — incompatible interfaces, material restructuring, or changes to the declared implementation scope.

A Git tag identifies a code state. A GitHub release identifies the citable public package associated with that state.

For scientific citation, prefer a release DOI or immutable release tag over main.

Citation

Citation metadata is provided in CITATION.cff. GitHub should display a Cite this repository option when that file is present.

Until a software DOI has been assigned, cite the numbered GitHub release and the relevant REE publication. Once Zenodo or another archive has issued a DOI, use the DOI associated with the exact release used in the analysis.

Suggested software citation format:

Lundqvist, Mats J. REE Code: Reference implementations and reproducibility materials for Recursive Epistemic Economy. Version X.Y.Z, year. GitHub release and archived DOI.

Do not cite the repository landing page alone when the result depends on a specific code state.

Contributing

Contributions are welcome when they improve correctness, reproducibility, documentation, testing, or clearly labelled exploration.

Before opening a pull request:

open or identify an issue describing the proposed change;
state whether the change is corrective, validating, demonstrative, exploratory, or canonical;
identify affected manuscript references and configuration files;
add or update tests;
record any changed numerical output;
update documentation and CHANGELOG.md where required.

A merged contribution does not automatically become part of the canonical REE framework. Canonical promotion requires explicit review against the relevant admissibility, readout, discriminator, notation, and cross-document consistency rules.

See CONTRIBUTING.md for the full contribution protocol.

Reporting problems

Please use GitHub Issues for:

reproducibility failures;
numerical or logical errors;
unit, sign, or notation inconsistencies;
manuscript-to-code mismatches;
unclear documentation;
proposed tests or extensions.

A useful bug report should include the release or commit, environment, configuration, command, observed output, expected output, and the smallest reproducible example available.

Security-sensitive reports should follow SECURITY.md rather than being posted publicly.

Licence

Unless otherwise stated, source code in this repository is licensed under the BSD 3-Clause License. See LICENSE.

The software licence does not automatically apply to:

the REE books or manuscript text;
diagrams reproduced from the publications;
website content;
project names, logos, or visual identity;
third-party data or software;
separately identified reference material.

Those materials retain their own copyright or licence status.

Author and maintenance

Author: Mats J Lundqvist
Project: Recursive Epistemic Economy
Website: www.ree-framework.org
Repository: github.com/REE-Framework/ree-code

For scientific questions, first consult the relevant publication section and the component-specific documentation. For implementation problems, use GitHub Issues so the discussion remains traceable.

Disclaimer

This repository contains research software and conceptual or numerical models. It is provided without warranty and should not be treated as independently validated physical theory, production infrastructure, or a substitute for domain-specific verification.

The evidential status of REE depends on registered empirical discrimination, not on the existence, complexity, or apparent success of a simulation.
