# RetroZ S1: Ink Profile Reconstruction

**Evaluation of constrained local contour operators and their practical limits**

**Author:** Saif Shafique
**Version:** 0.1.0
**Scientific status:** `PROVISIONAL_NO_OP`

> The public report contains no protected source imagery. Visuals are generated from synthetic fixtures.

## Candidate summary

| ID | Approach | Status | Result |
|---|---|---|---|
| A | Half-profile constrained reconstruction | `REJECTED_PRE_IMAGE` | Activation and measurement checks failed before a valid real-image run. |
| B | Monotone local shoulder remapping | `REAL_NEAR_NO_OP` | Limited dark-side movement; bright and total directions failed and native output remained near identity. |
| C | PSF and continuous coverage | `SYNTHETIC_REJECT` | Halo, angular bias and an invalid output-measurement harness closed the branch. |
| D3 | Geometry-guided contour reconstruction | `REAL_EXACT_NO_OP` | Extensive synthetic success did not transfer; the fixed real-data smoke output was identical to baseline. |
| Oracle | Human-labelled feasibility study | `ORACLE_NEAR_NO_OP` | Local nonzero changes were not visible in 50/50 native blind panels. |

## Contents

1. [Executive summary](#1-executive-summary)
2. [Problem and scope](#2-problem-and-scope)
3. [Evidence and asset boundary](#3-evidence-and-asset-boundary)
4. [Evaluation protocol](#4-evaluation-protocol)
5. [Candidate results](#5-candidate-results)
6. [Cross-candidate findings](#6-cross-candidate-findings)
7. [Engineering controls](#7-engineering-controls)
8. [Interpretation of the Oracle](#8-interpretation-of-the-oracle)
9. [Limitations and future work](#9-limitations-and-future-work)
10. [Conclusion](#10-conclusion)

## 1. Executive summary

RetroZ S1 tested whether a constrained local raster operator could move selected modern ink-edge profiles toward broader, asymmetric reference characteristics without shifting the perceived contour or damaging protected pixels. The stage was deliberately isolated from color grading, grain, halation, scan texture and temporal effects.

Five lineages were evaluated: analytical half-profile reconstruction, monotone shoulder remapping, PSF/coverage reconstruction, geometry-guided contour reconstruction and a final human-labelled Oracle. None produced a clearly visible, production-worthy improvement. The practical production decision is therefore identity/bypass, represented by the machine-readable status PROVISIONAL_NO_OP.

This is a bounded negative result. It applies to the evaluated data, metrics, safety gates, operator families and review protocol. It does not rule out vector reconstruction, learned contour semantics, temporal models or a different perceptual target.


## 2. Problem and scope

The target was the spatial transition across an ink contour, not an entire retro-animation style. The main measurements were p10, p50 and p90 positions on an edge-spread profile. Dark half-width was defined as p10 to p50, bright half-width as p50 to p90 and total width as p10 to p90.

p50 served as a practical proxy for perceived contour location. A candidate was not allowed to broaden an edge by moving the contour, blurring the core, damaging color plateaus or introducing halo outside the intended support. Junctions, end caps, backgrounds and hard masks were treated as protected contexts.

Success required activation, technical safety and visible utility. A nonzero pixel delta or a favorable synthetic metric was not enough. This distinction became central: several branches were technically active but not useful, while another passed synthetic contracts and was exactly inactive on the fixed real-data smoke test.


## 3. Evidence and asset boundary

Historical real-data experiments used protected source frames in a private environment. The public repository contains no frames, crops, contact sheets, videos, private contour coordinates or exact private M0 masks. Public visuals are generated from original procedural fixtures.

The package can reproduce its own tests, synthetic failures, generated figures, documentation, report and integrity manifests. Candidate B and D3 can also be exercised on user-owned images using documented public mask approximations. Those runs expose the operator but are not described as exact historical replay.

Private findings are retained as bounded summaries and provenance records. This preserves the decision history without implying that unavailable source material has been turned into an open dataset.


## 4. Evaluation protocol

Measurements were aggregated from frame to episode to fold across five separated folds. This prevented episodes with more eligible pixels from dominating the result and made directional stability part of the advancement decision.

Candidates had to pass deterministic-output and non-mutation checks, activation checks, midpoint and halo limits, protected-region passthrough and fold-level direction gates. Missing evidence, provenance drift or an invalid measurement path stopped the branch rather than being interpreted optimistically.

Synthetic fixtures covered controlled angles, junctions, end caps and color plateaus. They were used to validate implementation contracts. Real-data activation and native visual review remained separate requirements because synthetic behavior did not reliably predict real-image behavior.


## 5. Candidate results

Candidate A attempted centered half-profile reconstruction. Its eligibility proxy removed nearly all actionable support before a valid real-image test, and a follow-up measurement route failed its own accuracy contract. The honest public interface is therefore a synthetic self-blocking reproducer rather than an arbitrary-image renderer.

Candidate B used a frozen monotone local shoulder remap. On the fixed real-data smoke it supplied limited directional evidence on the dark half, but the bright and total widths did not move as required, fold stability was insufficient and native output stayed close to identity. It remains runnable only as a clearly labelled historical research artifact.

Candidate C explored PSF and continuous-coverage reconstruction. Synthetic results exposed halo and angular bias. One harness also inferred success from requested parameters instead of independently measuring raster output, which invalidated that evidence. The branch was closed before a valid real-image claim.

Candidate D3 combined source-fixed contour estimation with subpixel cell coverage. Its synthetic contracts were extensive and successful, but the fixed real-data smoke returned outputs identical to baseline. D3 is the clearest example of the synthetic-to-real activation gap.

The final Oracle replaced automatic localization with human-verified contour segments. Three methods and multiple tiers produced local, technically nonzero changes. A frozen native blind review nevertheless returned 50 out of 50 judgements of no visible difference, weakening the idea that localization alone explained the earlier no-ops.


## 6. Cross-candidate findings

The branches did not share one simple failure. A was self-blocking, B moved an incomplete subset of the target, C exposed spatial artifacts and invalid measurement, D3 failed to activate on real samples and the Oracle changed pixels without creating visible utility.

This matters for future work. Increasing strength cannot repair an invalid harness, an angle-dependent renderer or a target that remains invisible even with perfect labels. Each failure class points to a different research change.

The common lesson is that local correctness does not imply useful system behavior. Eligibility, independent measurement, real-distribution activation and native perception have to remain separate gates.


## 7. Engineering controls

The public package fails closed. Rejected candidates require an explicit command-line acknowledgement. Candidate A and C are excluded from normal image rendering and exposed only through synthetic failure reproduction. Output images receive JSON provenance sidecars.

Candidate registry entries record status, expected behavior, actual result, known failure, public capability and provenance hashes. Repository-level and packaged registry copies are tested for equality. Generated source and evidence manifests use SHA-256 and are refreshed after provenance updates.

CI installs the package through its declared metadata, runs tests across supported Python versions, smoke-tests the console entry point, builds wheel and source distributions, regenerates public artifacts and fails if committed generated files are stale.


## 8. Interpretation of the Oracle

The Oracle was designed to answer a specific question: were previous candidates failing mainly because they could not find the correct contour support? Human-labelled segments removed that uncertainty for the tested locations.

The renderer then produced nonzero, local changes, so the experiment did not fail because of an empty mask. The native blind panels still showed no visible difference. Under the tested widths and renderer family, better localization did not rescue useful perception.

The result does not establish a universal perceptual ceiling. It does justify closing the tested local renderer family and requiring a materially different representation or objective before reopening S1.


## 9. Limitations and future work

The real-data evidence cannot be independently replayed from the public repository because protected source frames and private labels are not distributed. The public package is reproducible at the code, synthetic-evidence and generated-artifact level.

Edge-spread widths do not capture every aspect of drawn line style. They omit semantics, authorship, temporal consistency and some display-dependent perception. Human review was bounded to the frozen panels and conditions used for the decision.

A future attempt should not repeat strength searches inside the closed families. Plausible new directions include vector contour reconstruction, learned semantic support, temporal information or a different perceptual target with independent review. Those are proposals, not evidence that S1 succeeded.


## 10. Conclusion

RetroZ S1 did not produce a production filter. It did produce a defensible answer: the evaluated deterministic contour operators did not justify activation, and the final human-labelled Oracle did not reveal a useful visible effect.

The retained value is an inspectable research system and a narrower search space. Production should remain identity/bypass until materially new evidence changes that decision.

## Appendix A: public commands

```bash
make test
make synthetic-demo
make report
make docs-build
make verify
```

Rejected or historical render paths require `--allow-rejected-research-candidate`.

## Appendix B: claim boundary

The package claims only that no tested S1 candidate demonstrated a clearly useful, production-worthy effect under the evaluated constraints. It does not claim that a retro line style is impossible or that materially different architectures cannot work.

---

Generated by `scripts/build_report.py`.
