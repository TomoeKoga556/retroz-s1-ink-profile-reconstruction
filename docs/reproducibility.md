# Reproducibility

## Publicly reproducible

A clean environment can install the package, run the tests, regenerate synthetic
visuals, rebuild the report and documentation, refresh hashes and verify the
public tree.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,reproduce]"
make synthetic-demo
make report
make docs-build
make verify
```

The CLI can also run B and D3 on user-owned images with public mask
approximations, or run the Oracle renderer with user-supplied labels.

The `reproduce` extra fixes the NumPy, Pillow, Matplotlib, PyYAML and MkDocs
versions used to regenerate committed evidence. The normal runtime dependency
ranges remain broader so the package can still be tested against newer releases.

## Not publicly replayable

The repository does not include the protected frames, exact private M0 masks,
private Oracle coordinates or raw historical sessions used in the real-data
experiments. Those results are summarized and bound to public provenance, but
they cannot be independently replayed from this repository alone.

## Determinism and integrity

Generated images use fixed synthetic fixtures. Report metadata uses a fixed
build timestamp. SHA-256 manifests cover source and evidence files, while CI
regenerates artifacts and fails if the committed output is stale.

This is reproducibility of the public package and its synthetic evidence, not a
claim that unavailable private data has been made public.
