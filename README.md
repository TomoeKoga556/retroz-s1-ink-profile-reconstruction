# RetroZ S1 — Ink Profile Reconstruction

[![CI](https://github.com/TomoeKoga556/retroz-s1-ink-profile-reconstruction/actions/workflows/ci.yml/badge.svg)](https://github.com/TomoeKoga556/retroz-s1-ink-profile-reconstruction/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB)](https://www.python.org/)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

RetroZ S1 is a Python research package for one narrow question: can a local,
deterministic image operator broaden selected ink-edge profiles without moving
the perceived contour or damaging protected regions?

> **Result:** none of the five evaluated lineages produced a clearly visible,
> production-worthy improvement. S1 therefore remains **identity/bypass**. This
> is a bounded negative result, not a claim that line reconstruction is
> impossible in general.

![Synthetic comparison of the evaluated render paths](docs/assets/generated/candidate-comparison.png)

The comparison above is generated from a synthetic fixture. It is intentionally
subtle: several candidates changed measurements or internal masks without
creating a useful visible difference.

## What is in the repository

- deterministic implementations for the surviving public candidate paths;
- synthetic reproducers for failure modes that should not be run on user images;
- a candidate registry with status, scope, known failure and provenance fields;
- fail-closed CLI behavior for rejected research candidates;
- generated visual fixtures, integrity manifests and a reproducible report;
- tests for determinism, non-mutation, local passthrough and public-asset rules.

## Study outcome

| Lineage | Approach | Final result |
|---|---|---|
| A | Half-profile constrained reconstruction | Rejected before real-image evaluation because activation and measurement checks failed |
| B | Monotone local shoulder remapping | Real near-no-op; limited dark-side movement, but the bright and total directions failed |
| C | PSF and continuous-coverage reconstruction | Rejected on synthetic fixtures because of halo, angular bias and an invalid measurement harness |
| D3 | Geometry-guided contour reconstruction | Exact no-op on the fixed real-data smoke test after passing synthetic contracts |
| Oracle | Human-labelled contour feasibility study | Technically nonzero output, but 50/50 native blind panels showed no visible difference |

No lineage received a Full PASS or production activation. The useful output of
S1 is the evaluation framework, the documented failure modes and a smaller
search space for later work.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,reproduce]"

retroz-s1 list-candidates
retroz-s1 inspect --candidate B
make synthetic-demo
make test
```

On Windows, activate the environment with `.venv\\Scripts\\activate`.

The `reproduce` extra pins the image and report-generation stack used for the
committed artifacts. Install `.[dev,docs]` instead when you only need the latest
compatible documentation toolchain.

## CLI safety behavior

Every historical or rejected candidate requires an explicit acknowledgement:

```bash
retroz-s1 render \
  --candidate B \
  --input ./my_image.png \
  --output ./output_b.png \
  --allow-rejected-research-candidate
```

Candidate A and C are exposed only through synthetic failure reproduction:

```bash
retroz-s1 reproduce-failure \
  --candidate A \
  --output ./failure_a \
  --allow-rejected-research-candidate
```

Image outputs receive a JSON provenance sidecar. Public B and D3 runs use
explicitly documented mask approximations; they are not presented as exact
replays of the private real-frame experiments.

## Common commands

| Command | Purpose |
|---|---|
| `make test` | Run the test suite |
| `make lint` | Run the repository's static checks |
| `make synthetic-demo` | Regenerate all public images and synthetic failures |
| `make report` | Regenerate the Markdown report and PDF |
| `make docs-build` | Build the MkDocs site into `site-preview/` |
| `make verify` | Refresh provenance and manifests, then verify the public tree |
| `make release` | Build a deterministic local source archive and report bundle |

## Reproducibility boundary

| Component | Publicly reproducible? |
|---|---|
| Package installation, CLI and tests | Yes |
| Synthetic fixtures and failure reproducers | Yes |
| Generated documentation, report and manifests | Yes |
| Candidate B and D3 on user-owned images | Yes, with public mask approximations |
| Historical real-frame experiments | No; source media is not distributed |
| Historical private labels and exact M0 masks | No |

The private evidence is summarized and provenance-bound, but the repository does
not imply that protected source material is publicly replayable.

## Repository map

- `src/retroz_s1/` — package and command-line interface
- `configs/` — candidate registry and frozen recipes
- `tests/` — behavioral and repository-policy tests
- `examples/synthetic/` — public-safe fixtures and failure examples
- `docs/` — study design, results and reference documentation
- `reports/` — canonical generated report and build metadata
- `manifests/` — public integrity and provenance records

## Documentation

Start with the [project overview](docs/project-overview.md), then read the
[methodology](docs/methodology.md), [candidate results](docs/candidate-lineages.md)
and [reproducibility boundary](docs/reproducibility.md). The longer technical
account is generated at
[`reports/RETROZ_S1_INK_PROFILE_RECONSTRUCTION_REPORT.md`](reports/RETROZ_S1_INK_PROFILE_RECONSTRUCTION_REPORT.md).

## Project status

The machine-readable status remains `PROVISIONAL_NO_OP`. In practical terms,
production code should treat S1 as identity/bypass unless a materially different
architecture produces new evidence. See [STATUS.md](STATUS.md) for the exact
claim boundary.

## Assets, license and citation

No protected animation frames, crops, videos or private contour labels are
included. Public images are synthetic or generated from synthetic fixtures. See
[the asset policy](docs/PUBLIC_ASSET_POLICY.md) and
[source/asset boundaries](SOURCE_AND_ASSET_BOUNDARIES.md).

Project code, documentation and project-generated assets are distributed under
the [Apache License 2.0](LICENSE), unless a file says otherwise. Third-party
packages keep their own licenses; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
Citation metadata is available in [CITATION.cff](CITATION.cff).
