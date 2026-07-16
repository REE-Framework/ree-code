# Reproducibility guide

For every reported result, record:

1. Exact release tag and commit hash.
2. Python and dependency versions.
3. Input and configuration checksums.
4. Random seed, if any.
5. Grid, timestep, boundary condition, and stopping rule.
6. Tolerance, norm, estimator, and nuisance controls.
7. Command used and expected output.

The command

```bash
ree manifest FILE [FILE ...] --output ree-manifest.json
```

creates a sorted JSON manifest with SHA-256 hashes. The manifest is deterministic
for the same environment, metadata, paths, and file contents.

Large datasets should be referenced by stable source, version, checksum,
licence, and preprocessing procedure rather than committed directly.
