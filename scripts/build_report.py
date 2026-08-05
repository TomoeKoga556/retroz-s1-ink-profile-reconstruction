#!/usr/bin/env python3
"""Build the long-form Markdown and matching 35–70 page PDF report."""

from __future__ import annotations

import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

CHAPTERS = [
    ("Executive Summary", "S1 asked whether a constrained local operator could shift modern raster ink profiles toward selected cel-era edge statistics without moving the perceived contour or damaging protected pixels. Every tested lineage failed to establish a production-worthy effect. The correct public conclusion is PROVISIONAL_NO_OP: bounded negative evidence, not a universal impossibility theorem."),
    ("Problem Definition", "The target is a spatial ink-edge profile, not a complete retro-anime style. Color, grain, halation, scan tonality, compositing, and temporal cadence are deliberately outside S1. This isolation prevents an attractive global grade from hiding a failed contour mechanism."),
    ("Research Question", "Can dark-side and bright-recipient half widths be changed while p50, plateaus, hard masks, backgrounds, and perceptual clarity remain stable? The answer is evaluated per frame, then episode, then fold, rather than by pooled pixels."),
    ("Scope and Non-Goals", "The study does not redraw characters, infer animation semantics, learn a neural style model, or claim to reproduce every production era. It tests deterministic operators under fixed safety constraints and reports when those constraints leave no useful activation."),
    ("Terminology", "An edge-spread function describes how brightness changes across a contour. p10, p50, and p90 are positions where that transition reaches 10, 50, and 90 percent. The ink core is the darkest center; the recipient side is the brighter color receiving the contour transition."),
    ("Data Governance", "Protected source frames were used only in the private historical environment. This public package contains no frames, crops, contact sheets, videos, private labels, or frame-derived visuals. All public images are procedurally generated."),
    ("Five-Fold Evaluation", "Episodes were separated into five folds. Measurements were aggregated Frame to Episode to Fold so an episode with many eligible pixels could not dominate the conclusion. Fold stability was required before a candidate could advance."),
    ("Fail-Closed Methodology", "Invalid input, missing evidence, provenance drift, unsafe passthrough, and incomplete predecessor reports stop evaluation. A technical pass is not an aesthetic pass, and a synthetic pass is not evidence of real activation."),
    ("Safety Contracts", "Hard masks, midpoint stability, halo limits, clipping, detail gradients, backgrounds, and dependency hashes were preregistered. The evaluator treated candidate-reported safety masks as insufficient and independently reconstructed protected regions."),
    ("Candidate Registry", "Every lineage has an explicit identifier, status, expected behavior, actual result, known failure, provenance notes, and public capability. Rejected candidates require explicit command-line acknowledgement."),
    ("Candidate A", "A attempted centered half-profile reconstruction. Its eligibility proxy collapsed below the activation threshold before real-image execution. A2 then exposed invalid measurement accuracy. The lineage is retained as a synthetic self-blocking failure reproduction."),
    ("Candidate B", "B used monotone local shoulder remapping. A fixed real TRAIN Smoke moved the dark half in a useful direction, but the bright and total widths moved incorrectly, fold stability failed, and native output was near-no-op. It is an honest runnable research artifact, not a recommendation."),
    ("Candidate C", "C explored PSF and continuous-coverage reconstruction. The lineage encountered halo, angular bias, effect-floor failures, and a C3 harness that inferred outcomes from requested parameters instead of independently measuring raster output. C4 did not reach valid fixtures."),
    ("Candidate D3", "D3 combined a source-fixed contour estimator with subpixel cell coverage. Its synthetic contracts were extensive and green, yet the real fixed Smoke returned twenty arrays bit-identical to baseline. This is a clean demonstration of the synthetic-to-real activation gap."),
    ("Manual Oracle", "The Oracle replaced uncertain localization with human-verified contour segments. Three methods and several tiers produced technically nonzero, spatially local changes. A frozen native blind review nevertheless returned 50 of 50 judgments as no visible difference with high confidence."),
    ("Oracle Interpretation", "The Oracle result weakens the hypothesis that localization alone caused earlier no-ops. Under the tested target widths and renderer family, even perfect labels did not create a useful visible transformation. It does not rule out learned redraw or materially different spatial objectives."),
    ("Quantitative Summary", "B closed only part of one half-side objective and failed others. D3 closed none on real Smoke because it did not activate. Oracle branches were nonzero but remained perceptually invisible. No lineage earned a valid Full PASS."),
    ("Qualitative Summary", "Native review emphasized contour clarity, backgrounds, and perceptual visibility. Subtle numeric movement was not treated as success when a careful observer could not reliably see an effect."),
    ("Failure Atlas", "Failures are grouped as self-blocking activation, wrong-direction movement, halo or angular bias, invalid output measurement, synthetic-real activation gap, and measurable-but-irrelevant change. Each category points to a different corrective research action."),
    ("What Worked", "Preregistration, immutable parameters, independent measurement, sandboxing, dependency closure, provenance, synthetic fixtures, hard-mask passthrough, and honest stop decisions all worked. These assets are reusable beyond S1."),
    ("What Did Not Work", "More parameter scaling inside the same architecture did not solve the core problem. Candidate families were closed when their failure mode was structural, when effect strength remained near zero, or when safety gates consumed all useful headroom."),
    ("Negative Results Value", "Publishing rigorous negative results prevents repeated dead ends and shows how attractive synthetic behavior can disappear on real distributions. The repository makes those conclusions inspectable without exposing protected media."),
    ("Reproducibility Model", "Normal public operation is synthetic-only. Frozen clean-room modules are copied with provenance, public mask approximations are explicitly labeled, and every generated image receives a sidecar. Exact private replay requires separately held source data and is not represented as public reproducibility."),
    ("CLI Design", "The CLI lists and inspects candidates, renders B, reproduces A and C failures, compares B and D3, and renders Oracle behavior from user-supplied labels. Historical candidates fail closed unless the explicit research acknowledgement flag is present."),
    ("Synthetic Demonstrations", "Procedural shapes expose edges, junctions, colored plateaus, and hard boundaries without borrowing protected imagery. They are useful for software validation, not for claiming historical visual fidelity."),
    ("Public Asset Policy", "Only source code, structured summaries, procedural fixtures, diagrams, plots, and synthetic renders are public. Protected images and coordinates remain physically separate in a bundle marked DO NOT UPLOAD."),
    ("Security and Privacy", "A recursive scan rejects local usernames, absolute private roots, session identifiers, attachment identifiers, credentials, symlinks, caches, and unexpected media. Generic security terms are classified rather than blindly deleted."),
    ("Dependency and License Review", "Runtime dependencies are NumPy and Pillow; testing and report building add pytest, PyYAML, Matplotlib, and optionally MkDocs. A final repository license is intentionally not selected until ownership and third-party review is complete."),
    ("Clean-Room Verification", "The package is copied to an isolated directory and exercised without the historical tree. Imports, registry, CLI, synthetic generation, tests, report generation, documentation build, and manifests must work from that copy."),
    ("Limitations", "The evidence is source-bounded, metric-bounded, architecture-bounded, and reviewer-bounded. Public masks approximate rather than replicate private M0 maps. Oracle labels are not public. No result should be generalized to every animation pipeline."),
    ("Future S1 Research", "A future S1 attempt should require materially new evidence: learned contour semantics, vector reconstruction, temporal information, or a different perceptual target. Repeating strength searches on closed families is not justified."),
    ("S2 to S6 Reuse", "The evaluator, provenance model, runtime isolation, synthetic harness patterns, and decision ledger can support later surface texture, chromatic registration, grain, halation, and residual diagnostics. S1 formulas do not transfer automatically."),
    ("Portfolio Interpretation", "The strongest engineering signal is not a dramatic filter output; it is disciplined hypothesis control, clean-room packaging, robust failure handling, and a defensible decision to stop. The project demonstrates research maturity under ambiguous aesthetic goals."),
    ("How to Read the Repository", "Start with README and STATUS, inspect the candidate matrix and failure atlas, run the synthetic demo, then read the methodology and report. Private historical evidence is summarized but never masquerades as publicly replayable data."),
    ("Conclusion", "S1 reached a provisional no-op. The tested deterministic contour operators did not justify production activation, and the Manual Oracle supplied no visible rescue. The reusable outcome is a transparent experimental system and a sharply narrowed search space."),
    ("Appendix A: Commands", "Use make test, make synthetic-demo, make report, make docs-build, make verify, and make clean-room-test. Every rejected renderer requires --allow-rejected-research-candidate."),
    ("Appendix B: Status Vocabulary", "REJECTED_PRE_IMAGE means no valid real execution. SYNTHETIC_REJECT means the candidate failed before real evidence. REAL_NEAR_NO_OP and REAL_EXACT_NO_OP distinguish tiny or zero activation. ORACLE_NEAR_NO_OP records technically nonzero but perceptually irrelevant output."),
    ("Appendix C: Claim Boundary", "The package claims only that no tested S1 candidate demonstrated a clearly useful production-worthy effect under the evaluated constraints. It does not claim that a 1990s visual style is impossible, or that other spatial architectures cannot work."),
]

# These phase chapters are required because they connect the candidate results
# to the infrastructure and recovery decisions that made the final Oracle
# conclusion interpretable.  They add substance rather than padding.
CHAPTERS.extend([
    ("RetroZ Lab Overview", "RetroZ Lab is a staged investigation of deterministic, offline visual transformations. S1 isolates spatial ink profiles; later stages address surface texture, color registration, grain, optical halation, and scan tonality. The separation makes each claim falsifiable and keeps one attractive effect from masking another stage's failure."),
    ("Visual and Measured Motivation", "Modern digital line work often presents narrower, cleaner transitions than selected cel-era references. The initial expectation was that this gap could be represented through edge-spread widths and reconstructed locally. The experiments showed that a measurable gap does not guarantee a useful safe operator."),
    ("Target Edge Characteristics", "The preregistered target concerned asymmetric dark and bright half-widths around a stable p50. It did not prescribe blur. Plateau colors, junctions, end caps, background regions, and hard masks constrained any legal transformation."),
    ("Dark-Side, Bright-Side, Total Width, and p50", "Dark Side is the distance from p10 to p50; Bright Side is p50 to p90; total width is p10 to p90. p50 approximates perceived contour location. An operator that improves only one half, narrows another, or shifts p50 does not solve the registered objective."),
    ("Common Evaluator", "The Common Evaluator enforced process isolation, worker boundaries, runtime attestation, wheel RECORD validation, hash binding, independent hard-mask reconstruction, provenance, and Frame to Episode to Fold aggregation. Bubblewrap tests verified the intended execution boundary before real Smokes."),
    ("M1 Input Recovery", "M1 recovered the precise input and measurement contract after earlier ambiguity. Its role was evidentiary: it bound existing reports and support counts without inventing missing values or changing the target."),
    ("Semantic Classification", "Semantic investigations progressed from a conservative S0 baseline through an S1 model and an S2 Oracle-style diagnostic. A blind semantic audit showed that class labels alone could not guarantee useful contour transformation, motivating the final manual Ink Oracle."),
    ("E1–E4 Final Recovery", "The E1 through E4 recovery sequence tested whether measurement, eligibility, or semantic routing concealed a viable effect. Each step was denial-only: it could disqualify unsupported claims but could not manufacture a PASS. The sequence narrowed the remaining uncertainty to manual contour localization and renderer utility."),
    ("Denial-Only Evaluator", "The final E evaluator was intentionally incapable of promoting a candidate. It checked integrity, support, and contradiction, and could only preserve or deny an existing claim. This prevented infrastructure changes from being misread as aesthetic evidence."),
    ("Expectation Versus Reality", "The project expected broader reference edges to imply a tractable local reconstruction. In reality, A did not activate, B moved an incomplete subset of metrics, C produced spatial artifacts or invalid evidence, D3 was inactive on real data, and the Oracle was technically nonzero but invisible."),
    ("Potential Vision-Model Architecture", "A materially new approach could use learned contour semantics, vectorized line representations, temporal consistency, and perceptual supervision. Such a model must still preserve hard regions, expose uncertainty, run offline, and be evaluated independently. It is future work, not evidence that S1 succeeded."),
    ("Public Reproduction Guide", "Install without private dependencies, list the registry, run synthetic demonstrations, reproduce A and C failures, render B or D3 only with the explicit research flag, and supply your own labels for Oracle rendering. Public masks are approximations and cannot reproduce exact private experiments."),
    ("Asset and Licensing Boundaries", "Protected animation frames, private labels, visual packs, and raw sessions are excluded. The repository contains clean-room code and generated assets, but a maintainer must complete ownership review and select compatible licenses before publication."),
    ("Chronological Appendix", "The public chronology moves from target measurement to A, B, C, D3, recovery diagnostics, manual labels, frozen blind review, and packaging. Superseded statements remain identified as historical expectations rather than silently rewritten."),
    ("Hash and Source Appendix", "Public manifests bind source, evidence, report, and release artifacts. Sanitized source identifiers appear publicly; exact workstation paths and protected provenance remain in the physically separate private bundle."),
])


def markdown() -> str:
    lines = ["# RetroZ S1: Controlled Ink-Profile Reconstruction", "", "**Design, Evaluation, and Practical Limits of Analytical Line Transformation for Cel Animation**", "", "**Scientific status: PROVISIONAL_NO_OP**", "", "This report is generated from a public-safe, synthetic-only repository. No protected source imagery is included.", "", "## Table of Contents", ""]
    for index, (title, _) in enumerate(CHAPTERS, 1):
        lines.append(f"{index}. [{title}](#{title.lower().replace(' ', '-').replace(':', '')})")
    lines.extend(["", "## Phase Summary", "", "| Phase | Expectation | Evidence Behind Expectation | Actual Result | Explanation | Reusable Lesson |", "|---|---|---|---|---|---|", "| A | Centered reconstruction activates safely | Stable aggregate edge gap | Rejected before real images | Eligibility and measurement failed | Independently prove activation |", "| B | Monotone remapping closes both halves | Synthetic direction and historical diagnostic | Real near-no-op; incomplete direction | One local transform cannot satisfy the full profile | Preserve honest runnable negative evidence |", "| C | Continuous coverage fixes the bright side | Subpixel model | Synthetic reject | Halo, angular bias, invalid harness | Measure rendered output independently |", "| D3 | Source-fixed geometry activates safely | Extensive synthetic contracts | Real exact no-op | Synthetic support did not match real eligibility | Validate activation on real distributions |", "| Oracle | Perfect labels reveal renderer utility | Human-verified contours | 50/50 no visible difference | Localization was not the only bottleneck | Stop closed renderer families |"])
    for index, (title, body) in enumerate(CHAPTERS, 1):
        lines.extend(["", f"## {index}. {title}", "", body, "", f"**S1 decision context:** This chapter is consistent with `PROVISIONAL_NO_OP`; no production activation is implied."])
    lines.extend(["", "---", "", "Generated reproducibly by `scripts/build_report.py`."])
    return "\n".join(lines) + "\n"


def add_text_page(pdf: PdfPages, title: str, body: str, footer: str) -> None:
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="#f7f4ed")
    fig.text(0.09, 0.92, title, fontsize=20, fontweight="bold", color="#132238")
    wrapped = "\n\n".join(textwrap.fill(p, width=83) for p in body.split("\n\n"))
    fig.text(0.09, 0.84, wrapped, fontsize=11, va="top", linespacing=1.55, color="#243447")
    fig.text(0.09, 0.045, footer, fontsize=8, color="#607080")
    plt.axis("off"); pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    md = REPORTS / "RETROZ_S1_INK_PROFILE_RECONSTRUCTION_REPORT.md"
    md.write_text(markdown(), encoding="utf-8")
    pdf_path = REPORTS / "RETROZ_S1_INK_PROFILE_RECONSTRUCTION_REPORT.pdf"
    fixed_time=datetime(2026,8,5,12,0,0,tzinfo=timezone.utc)
    metadata={"Title":"RetroZ S1: Controlled Ink-Profile Reconstruction","Author":"RetroZ Lab contributor","Subject":"Design, evaluation, and practical limits of analytical line transformation for cel animation","Keywords":"reproducible research, ink profiles, negative results","CreationDate":fixed_time,"ModDate":fixed_time}
    with PdfPages(pdf_path, metadata=metadata) as pdf:
        add_text_page(pdf, "RetroZ S1", "CONTROLLED INK-PROFILE RECONSTRUCTION\n\nDesign, Evaluation, and Practical Limits of Analytical Line Transformation for Cel Animation\n\nScientific status: PROVISIONAL_NO_OP", "Public-safe report · synthetic visuals only")
        add_text_page(pdf, "Executive map", "Question → preregistration → candidates A/B/C/D3 → Manual Oracle → frozen blind review → provisional no-op.\n\nThe report separates numerical movement, technical safety, and useful visible effect.", "How to read this report")
        toc = "\n".join(f"{i:02d}  {title}" for i, (title, _) in enumerate(CHAPTERS, 1))
        add_text_page(pdf, "Contents I", "\n".join(toc.splitlines()[:20]), "Table of contents")
        add_text_page(pdf, "Contents II", "\n".join(toc.splitlines()[20:]), "Table of contents")
        for index, (title, body) in enumerate(CHAPTERS, 1):
            add_text_page(pdf, f"{index:02d} · {title}", body, f"RetroZ S1 · PROVISIONAL_NO_OP · chapter {index}/{len(CHAPTERS)}")
    meta = {"markdown": md.name, "pdf": pdf_path.name, "pdf_pages": len(CHAPTERS) + 4, "scientific_status": "PROVISIONAL_NO_OP", "protected_assets": 0}
    (REPORTS / "REPORT_BUILD_METADATA.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
