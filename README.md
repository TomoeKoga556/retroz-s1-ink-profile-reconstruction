# RetroZ S1 — Ink Profile Reconstruction

A reproducible research framework for analyzing and transforming anime ink-edge profiles while preserving local geometry, color structure, and protected image regions.

S1 investigates whether modern digitally rendered line work can be shifted toward the broader and more asymmetric contour characteristics observed in selected traditional cel-animation references.

## Current Status

**Provisional No-Op under the evaluated constraints**

The tested analytical, geometric, semantic, and manually guided methods did not produce a clearly useful production-worthy visible improvement. The repository preserves the implementations, evaluation infrastructure, experimental evidence, and negative results required to reproduce that conclusion. This is not a universal impossibility claim.

## Project Motivation

The wider RetroZ Lab studies efficient, deterministic methods for translating selected visual properties of traditional cel animation into offline and eventually real-time processing. S1 isolates ink-edge profile reconstruction from color, grain, halation, scan tonality, and temporal behavior.

## Research Question

Can a constrained local operator broaden or reshape modern digital ink profiles toward selected cel-era references without moving the perceived contour, damaging color plateaus, creating halo, or altering protected regions?

## Core Contributions

- A fail-closed evaluation methodology with frame-to-episode-to-fold aggregation.
- Clean-room analytical, PSF, coverage, and geometry-guided candidate implementations.
- Process isolation, provenance binding, and synthetic-versus-real failure analysis.
- A final human-verified Oracle experiment that separated localization failure from renderer utility.
- Public-safe synthetic reproducers and a standalone research CLI.

## Candidate Lineages

| Candidate | Public name | Final evidence |
|---|---|---|
| A | Half-Profile Constrained Reconstruction | Rejected before real images: activation/measurement failure |
| B | Monotone Local Shoulder Remapping | Real near-no-op; bright and total direction failed |
| C | PSF and Continuous-Coverage Reconstruction | Synthetic reject: halo, angular bias, invalid harness |
| D3 | Geometry-Guided Contour Reconstruction | Real exact no-op after extensive synthetic success |
| Oracle | Human-Verified Contour Feasibility Study | 50/50 native blind panels showed no visible difference |

## Results

No S1 candidate earned a Full PASS or production activation. Candidate B supplied limited directional evidence on the dark side, D3 supplied reusable geometry and sandbox infrastructure, and the Manual Oracle established a soft ceiling for the evaluated contour-renderer family.

## What Worked

Preregistration, independent measurement, hard-mask passthrough, provenance, runtime attestation, deterministic synthetic fixtures, and fail-closed decisions worked as intended. These components remain reusable for later RetroZ stages.

## What Did Not Work

Local correctness did not imply useful real activation. Several operators were self-blocking, directionally incomplete, halo-prone, angle-dependent, or exactly inactive on real samples. Perfect manual labels did not make the tested renderer family perceptually useful.

## Quickstart

```bash
python -m pip install -e . --no-deps
python -m retroz_s1 list-candidates
python -m retroz_s1 inspect --candidate B
make synthetic-demo
```

## CLI

Rejected candidates always require explicit acknowledgement:

```bash
python -m retroz_s1 render --candidate B --input ./my_image.png --output ./output_b.png --allow-rejected-research-candidate
python -m retroz_s1 reproduce-failure --candidate A --output ./failure_a --allow-rejected-research-candidate
python -m retroz_s1 compare --input ./my_image.png --candidates B,D3 --output ./comparison --allow-rejected-research-candidate
python -m retroz_s1 oracle-render --input ./my_image.png --labels ./examples/synthetic/oracle_labels.json --method P1 --tier R0 --output ./oracle.png --allow-rejected-research-candidate
```

Every image output receives a provenance sidecar. The public B and D3 demonstrations use documented mask approximations and are not exact replays of private TRAIN experiments.

## Synthetic Demonstrations

`make synthetic-demo` creates geometric edge profiles, failure cases, and an Oracle example without protected media.

## Reproducing Candidate Failures

Candidate A and C are deliberately excluded from the normal image render path. Their strongest honest public interface is `reproduce-failure`.

## Oracle Rendering with User Labels

The Oracle command accepts user-owned imagery and explicit contour polylines. No protected labels or source frames are bundled or downloaded.

## Research Report

See [the long-form report](reports/RETROZ_S1_INK_PROFILE_RECONSTRUCTION_REPORT.md) and the locally generated PDF.

## Repository Structure

`src/` contains the package, `configs/` the candidate registry, `examples/` public-safe fixtures, `docs/` the research site, `reports/` reports, and `manifests/` provenance.

## Limitations

The evidence is bounded to the evaluated sources, folds, formulas, safety constraints, and human blind review. It does not prove mathematical or creative impossibility and does not exclude materially different learned methods.

## Future Work

Future S1 work requires materially new evidence or architecture, such as learned contour semantics or a different spatial hypothesis. S2–S6 may reuse the evaluator without inheriting S1 formulas.

## Relation to RetroZ Lab

This is the standalone S1 research package, not a monorepo. Other RetroZ stages remain separate future projects.

## Citation

Use `CITATION.cff`.

## Asset Policy

No protected anime frames, crops, contact sheets, videos, or private labels are included. See `docs/PUBLIC_ASSET_POLICY.md`.

## License Status

No final license has been selected. See `LICENSE_REVIEW_REQUIRED.md` and `SOURCE_OWNERSHIP_AUDIT.md` before publication.
