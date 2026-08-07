#!/usr/bin/env python3
"""Build the canonical Markdown report and a matching deterministic PDF."""

from __future__ import annotations

import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
FIXED_TIME = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)

CANDIDATES = [
    (
        "A",
        "Half-profile constrained reconstruction",
        "REJECTED_PRE_IMAGE",
        "Activation and measurement checks failed before a valid real-image run.",
    ),
    (
        "B",
        "Monotone local shoulder remapping",
        "REAL_NEAR_NO_OP",
        "Limited dark-side movement; bright and total directions failed and native output remained near identity.",
    ),
    (
        "C",
        "PSF and continuous coverage",
        "SYNTHETIC_REJECT",
        "Halo, angular bias and an invalid output-measurement harness closed the branch.",
    ),
    (
        "D3",
        "Geometry-guided contour reconstruction",
        "REAL_EXACT_NO_OP",
        "Extensive synthetic success did not transfer; the fixed real-data smoke output was identical to baseline.",
    ),
    (
        "Oracle",
        "Human-labelled feasibility study",
        "ORACLE_NEAR_NO_OP",
        "Local nonzero changes were not visible in 50/50 native blind panels.",
    ),
]

SECTIONS = [
    (
        "Executive summary",
        [
            "RetroZ S1 tested whether a constrained local raster operator could move selected modern ink-edge profiles toward broader, asymmetric reference characteristics without shifting the perceived contour or damaging protected pixels. The stage was deliberately isolated from color grading, grain, halation, scan texture and temporal effects.",
            "Five lineages were evaluated: analytical half-profile reconstruction, monotone shoulder remapping, PSF/coverage reconstruction, geometry-guided contour reconstruction and a final human-labelled Oracle. None produced a clearly visible, production-worthy improvement. The practical production decision is therefore identity/bypass, represented by the machine-readable status PROVISIONAL_NO_OP.",
            "This is a bounded negative result. It applies to the evaluated data, metrics, safety gates, operator families and review protocol. It does not rule out vector reconstruction, learned contour semantics, temporal models or a different perceptual target.",
        ],
    ),
    (
        "Problem and scope",
        [
            "The target was the spatial transition across an ink contour, not an entire retro-animation style. The main measurements were p10, p50 and p90 positions on an edge-spread profile. Dark half-width was defined as p10 to p50, bright half-width as p50 to p90 and total width as p10 to p90.",
            "p50 served as a practical proxy for perceived contour location. A candidate was not allowed to broaden an edge by moving the contour, blurring the core, damaging color plateaus or introducing halo outside the intended support. Junctions, end caps, backgrounds and hard masks were treated as protected contexts.",
            "Success required activation, technical safety and visible utility. A nonzero pixel delta or a favorable synthetic metric was not enough. This distinction became central: several branches were technically active but not useful, while another passed synthetic contracts and was exactly inactive on the fixed real-data smoke test.",
        ],
    ),
    (
        "Evidence and asset boundary",
        [
            "Historical real-data experiments used protected source frames in a private environment. The public repository contains no frames, crops, contact sheets, videos, private contour coordinates or exact private M0 masks. Public visuals are generated from original procedural fixtures.",
            "The package can reproduce its own tests, synthetic failures, generated figures, documentation, report and integrity manifests. Candidate B and D3 can also be exercised on user-owned images using documented public mask approximations. Those runs expose the operator but are not described as exact historical replay.",
            "Private findings are retained as bounded summaries and provenance records. This preserves the decision history without implying that unavailable source material has been turned into an open dataset.",
        ],
    ),
    (
        "Evaluation protocol",
        [
            "Measurements were aggregated from frame to episode to fold across five separated folds. This prevented episodes with more eligible pixels from dominating the result and made directional stability part of the advancement decision.",
            "Candidates had to pass deterministic-output and non-mutation checks, activation checks, midpoint and halo limits, protected-region passthrough and fold-level direction gates. Missing evidence, provenance drift or an invalid measurement path stopped the branch rather than being interpreted optimistically.",
            "Synthetic fixtures covered controlled angles, junctions, end caps and color plateaus. They were used to validate implementation contracts. Real-data activation and native visual review remained separate requirements because synthetic behavior did not reliably predict real-image behavior.",
        ],
    ),
    (
        "Candidate results",
        [
            "Candidate A attempted centered half-profile reconstruction. Its eligibility proxy removed nearly all actionable support before a valid real-image test, and a follow-up measurement route failed its own accuracy contract. The honest public interface is therefore a synthetic self-blocking reproducer rather than an arbitrary-image renderer.",
            "Candidate B used a frozen monotone local shoulder remap. On the fixed real-data smoke it supplied limited directional evidence on the dark half, but the bright and total widths did not move as required, fold stability was insufficient and native output stayed close to identity. It remains runnable only as a clearly labelled historical research artifact.",
            "Candidate C explored PSF and continuous-coverage reconstruction. Synthetic results exposed halo and angular bias. One harness also inferred success from requested parameters instead of independently measuring raster output, which invalidated that evidence. The branch was closed before a valid real-image claim.",
            "Candidate D3 combined source-fixed contour estimation with subpixel cell coverage. Its synthetic contracts were extensive and successful, but the fixed real-data smoke returned outputs identical to baseline. D3 is the clearest example of the synthetic-to-real activation gap.",
            "The final Oracle replaced automatic localization with human-verified contour segments. Three methods and multiple tiers produced local, technically nonzero changes. A frozen native blind review nevertheless returned 50 out of 50 judgements of no visible difference, weakening the idea that localization alone explained the earlier no-ops.",
        ],
    ),
    (
        "Cross-candidate findings",
        [
            "The branches did not share one simple failure. A was self-blocking, B moved an incomplete subset of the target, C exposed spatial artifacts and invalid measurement, D3 failed to activate on real samples and the Oracle changed pixels without creating visible utility.",
            "This matters for future work. Increasing strength cannot repair an invalid harness, an angle-dependent renderer or a target that remains invisible even with perfect labels. Each failure class points to a different research change.",
            "The common lesson is that local correctness does not imply useful system behavior. Eligibility, independent measurement, real-distribution activation and native perception have to remain separate gates.",
        ],
    ),
    (
        "Engineering controls",
        [
            "The public package fails closed. Rejected candidates require an explicit command-line acknowledgement. Candidate A and C are excluded from normal image rendering and exposed only through synthetic failure reproduction. Output images receive JSON provenance sidecars.",
            "Candidate registry entries record status, expected behavior, actual result, known failure, public capability and provenance hashes. Repository-level and packaged registry copies are tested for equality. Generated source and evidence manifests use SHA-256 and are refreshed after provenance updates.",
            "CI installs the package through its declared metadata, runs tests across supported Python versions, smoke-tests the console entry point, builds wheel and source distributions, regenerates public artifacts and fails if committed generated files are stale.",
        ],
    ),
    (
        "Interpretation of the Oracle",
        [
            "The Oracle was designed to answer a specific question: were previous candidates failing mainly because they could not find the correct contour support? Human-labelled segments removed that uncertainty for the tested locations.",
            "The renderer then produced nonzero, local changes, so the experiment did not fail because of an empty mask. The native blind panels still showed no visible difference. Under the tested widths and renderer family, better localization did not rescue useful perception.",
            "The result does not establish a universal perceptual ceiling. It does justify closing the tested local renderer family and requiring a materially different representation or objective before reopening S1.",
        ],
    ),
    (
        "Limitations and future work",
        [
            "The real-data evidence cannot be independently replayed from the public repository because protected source frames and private labels are not distributed. The public package is reproducible at the code, synthetic-evidence and generated-artifact level.",
            "Edge-spread widths do not capture every aspect of drawn line style. They omit semantics, authorship, temporal consistency and some display-dependent perception. Human review was bounded to the frozen panels and conditions used for the decision.",
            "A future attempt should not repeat strength searches inside the closed families. Plausible new directions include vector contour reconstruction, learned semantic support, temporal information or a different perceptual target with independent review. Those are proposals, not evidence that S1 succeeded.",
        ],
    ),
    (
        "Conclusion",
        [
            "RetroZ S1 did not produce a production filter. It did produce a defensible answer: the evaluated deterministic contour operators did not justify activation, and the final human-labelled Oracle did not reveal a useful visible effect.",
            "The retained value is an inspectable research system and a narrower search space. Production should remain identity/bypass until materially new evidence changes that decision.",
        ],
    ),
]


def markdown() -> str:
    lines = [
        "# RetroZ S1: Ink Profile Reconstruction",
        "",
        "**Evaluation of constrained local contour operators and their practical limits**",
        "",
        "**Author:** Saif Shafique",
        "**Version:** 0.1.0",
        "**Scientific status:** `PROVISIONAL_NO_OP`",
        "",
        "> The public report contains no protected source imagery. Visuals are generated from synthetic fixtures.",
        "",
        "## Candidate summary",
        "",
        "| ID | Approach | Status | Result |",
        "|---|---|---|---|",
    ]
    for candidate_id, approach, status, result in CANDIDATES:
        lines.append(f"| {candidate_id} | {approach} | `{status}` | {result} |")

    lines.extend(["", "## Contents", ""])
    for index, (title, _) in enumerate(SECTIONS, 1):
        anchor = title.lower().replace(" ", "-")
        lines.append(f"{index}. [{title}](#{index}-{anchor})")

    for index, (title, paragraphs) in enumerate(SECTIONS, 1):
        lines.extend(["", f"## {index}. {title}", ""])
        for paragraph in paragraphs:
            lines.extend([paragraph, ""])

    lines.extend(
        [
            "## Appendix A: public commands",
            "",
            "```bash",
            "make test",
            "make synthetic-demo",
            "make report",
            "make docs-build",
            "make verify",
            "```",
            "",
            "Rejected or historical render paths require `--allow-rejected-research-candidate`.",
            "",
            "## Appendix B: claim boundary",
            "",
            "The package claims only that no tested S1 candidate demonstrated a clearly useful, production-worthy effect under the evaluated constraints. It does not claim that a retro line style is impossible or that materially different architectures cannot work.",
            "",
            "---",
            "",
            "Generated by `scripts/build_report.py`.",
        ]
    )
    return "\n".join(lines) + "\n"


def wrap_paragraphs(paragraphs: list[str], width: int = 92) -> list[str]:
    lines: list[str] = []
    for paragraph in paragraphs:
        lines.extend(textwrap.wrap(paragraph, width=width))
        lines.append("")
    return lines


def add_text_pages(
    pdf: PdfPages,
    title: str,
    paragraphs: list[str],
    page_number: int,
) -> int:
    lines = wrap_paragraphs(paragraphs)
    page_capacity = 38
    chunks = [lines[index : index + page_capacity] for index in range(0, len(lines), page_capacity)]
    for part, chunk in enumerate(chunks, 1):
        fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
        shown_title = title if len(chunks) == 1 else f"{title} ({part}/{len(chunks)})"
        fig.text(0.09, 0.92, shown_title, fontsize=18, fontweight="bold", color="#162033")
        fig.text(
            0.09,
            0.85,
            "\n".join(chunk),
            fontsize=10.4,
            va="top",
            family="DejaVu Sans",
            linespacing=1.35,
            color="#253247",
        )
        fig.text(0.09, 0.04, "RetroZ S1 · public-safe report", fontsize=8, color="#687386")
        fig.text(0.91, 0.04, str(page_number), fontsize=8, ha="right", color="#687386")
        plt.axis("off")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)
        page_number += 1
    return page_number


def add_candidate_table(pdf: PdfPages, page_number: int) -> int:
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    fig.text(0.09, 0.92, "Candidate summary", fontsize=18, fontweight="bold", color="#162033")
    ax = fig.add_axes([0.08, 0.18, 0.84, 0.64])
    ax.axis("off")
    cell_text = [[row[0], row[2], textwrap.fill(row[3], 42)] for row in CANDIDATES]
    table = ax.table(
        cellText=cell_text,
        colLabels=["ID", "Status", "Result"],
        colWidths=[0.10, 0.25, 0.65],
        cellLoc="left",
        loc="upper left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)
    fig.text(0.09, 0.04, "RetroZ S1 · public-safe report", fontsize=8, color="#687386")
    fig.text(0.91, 0.04, str(page_number), fontsize=8, ha="right", color="#687386")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)
    return page_number + 1


def add_image_page(pdf: PdfPages, title: str, image_path: Path, page_number: int) -> int:
    if not image_path.is_file():
        return page_number
    image = mpimg.imread(image_path)
    fig = plt.figure(figsize=(11.69, 8.27), facecolor="white")
    fig.text(0.06, 0.93, title, fontsize=18, fontweight="bold", color="#162033")
    ax = fig.add_axes([0.05, 0.12, 0.90, 0.74])
    ax.imshow(image)
    ax.axis("off")
    fig.text(0.06, 0.04, "Synthetic fixture; no protected source imagery", fontsize=8, color="#687386")
    fig.text(0.94, 0.04, str(page_number), fontsize=8, ha="right", color="#687386")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)
    return page_number + 1


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    markdown_path = REPORTS / "RETROZ_S1_INK_PROFILE_RECONSTRUCTION_REPORT.md"
    pdf_path = REPORTS / "RETROZ_S1_INK_PROFILE_RECONSTRUCTION_REPORT.pdf"
    markdown_path.write_text(markdown(), encoding="utf-8")

    metadata = {
        "Title": "RetroZ S1: Ink Profile Reconstruction",
        "Author": "Saif Shafique",
        "Subject": "Constrained contour reconstruction and negative-results analysis",
        "Keywords": "computer vision, image processing, reproducible research, negative results",
        "CreationDate": FIXED_TIME,
        "ModDate": FIXED_TIME,
    }

    page_number = 1
    with PdfPages(pdf_path, metadata=metadata) as pdf:
        fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
        fig.text(0.10, 0.78, "RetroZ S1", fontsize=34, fontweight="bold", color="#162033")
        fig.text(0.10, 0.70, "INK PROFILE RECONSTRUCTION", fontsize=16, color="#266a76")
        fig.text(
            0.10,
            0.58,
            "Evaluation of constrained local contour operators\nand their practical limits",
            fontsize=17,
            linespacing=1.5,
            color="#253247",
        )
        fig.text(0.10, 0.40, "Scientific status: PROVISIONAL_NO_OP", fontsize=13, color="#8a5a00")
        fig.text(0.10, 0.32, "Saif Shafique · version 0.1.0", fontsize=11, color="#687386")
        fig.text(0.10, 0.08, "Public-safe report · synthetic visuals only", fontsize=9, color="#687386")
        plt.axis("off")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)
        page_number += 1

        page_number = add_candidate_table(pdf, page_number)
        for title, paragraphs in SECTIONS:
            page_number = add_text_pages(pdf, title, paragraphs, page_number)
            if title == "Candidate results":
                page_number = add_image_page(
                    pdf,
                    "Synthetic candidate comparison",
                    ROOT / "docs/assets/generated/candidate-comparison.png",
                    page_number,
                )
            if title == "Interpretation of the Oracle":
                page_number = add_image_page(
                    pdf,
                    "Oracle output and amplified delta",
                    ROOT / "docs/assets/generated/oracle-delta.png",
                    page_number,
                )

    page_count = page_number - 1
    build_metadata = {
        "markdown": markdown_path.name,
        "pdf": pdf_path.name,
        "pdf_pages": page_count,
        "author": "Saif Shafique",
        "version": "0.1.0",
        "scientific_status": "PROVISIONAL_NO_OP",
        "protected_assets": 0,
    }
    (REPORTS / "REPORT_BUILD_METADATA.json").write_text(
        json.dumps(build_metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(build_metadata, indent=2))


if __name__ == "__main__":
    main()
