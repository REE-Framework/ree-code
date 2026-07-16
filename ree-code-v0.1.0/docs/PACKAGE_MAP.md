# Package map

## `ree.algorithm_a`

A deterministic finite-speed damped-wave front. It validates explicit
multidimensional CFL handling and provides a small constructive scaffold. The
implemented PDE is documented in the source and must not be substituted for a
more specific manuscript equation without an explicit versioned change.

## `ree.readout`

Applies exact block averaging, optional finite quantisation, and a declared norm
and tolerance. It supports RRIP-style operational comparison while preserving
the distinction between readout indistinguishability and ontological identity.

## `ree.null_compute`

Implements conservative one-dimensional upwind transport with a signed boundary
ledger. It demonstrates retained-domain accounting. It is not a model of a real
black-hole interior or Hawking flux.

## `ree.discriminators`

Contains a readable software mirror of the register labels plus selected
calculations whose form is frozen in the current project material: the P7
frequency scaling and idealised phase-resolution stacking relations. Other
entries are metadata only.

## `ree.reproducibility`

Creates SHA-256 manifests and captures core environment information. Manifests
intentionally omit volatile timestamps unless the user adds them as metadata.
