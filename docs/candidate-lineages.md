# Candidate lineages

## A — Half-profile constrained reconstruction

A attempted to reconstruct the two sides of a contour around a stable midpoint.
Its eligibility proxy collapsed below the activation threshold before a valid
real-image run. A follow-up measurement path also failed its accuracy contract.
The public package keeps a synthetic self-blocking reproducer rather than a
misleading image filter.

**Status:** `REJECTED_PRE_IMAGE`

## B — Monotone local shoulder remapping

B applied a source-locked monotone remap to selected shoulder regions. It is the
main public arbitrary-image renderer, but only as a rejected research artifact.
The fixed real-data smoke test showed limited movement on the dark half while the
bright and total directions failed, fold stability was insufficient and native
output remained close to identity.

**Status:** `REAL_NEAR_NO_OP`

## C — PSF and continuous-coverage reconstruction

C tested whether a point-spread or continuous-coverage model could avoid the
limitations of direct remapping. Synthetic evaluation exposed halo and
angle-dependent behavior. One harness also measured requested parameters rather
than the rasterized output, making the evidence invalid. The lineage is exposed
through a controlled synthetic failure example.

**Status:** `SYNTHETIC_REJECT`

## D3 — Geometry-guided contour reconstruction

D3 combined a source-fixed contour estimator with subpixel cell coverage. It
passed a broad synthetic contract but did not activate on the fixed real-data
smoke test: the evaluated outputs were bit-identical to baseline. The geometry
and sandbox work remain useful, but the candidate did not solve S1.

**Status:** `REAL_EXACT_NO_OP`

## Oracle — Human-labelled feasibility study

The Oracle used human-verified contour segments and several rendering methods to
separate localization failure from renderer utility. Changes were local and
nonzero, yet the frozen native blind review returned 50/50 “no visible
difference” judgements with high confidence.

**Status:** `ORACLE_NEAR_NO_OP`

## Consolidated decision

No candidate earned a Full PASS. Production behavior remains identity/bypass,
and reopening S1 requires a materially different representation or target rather
than another strength sweep inside these closed families.
