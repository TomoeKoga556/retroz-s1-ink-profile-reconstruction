#!/usr/bin/env python3
"""Generate every public visual from original geometric fixtures."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from retroz_s1.cli import render_b, render_d3
from retroz_s1.candidates.oracle_renderer import render_oracle
from retroz_s1.io import save_rgb
from retroz_s1.synthetic import draw_social_preview, reproduce_a, reproduce_c


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples/synthetic"
FIGURES = ROOT / "docs/assets/generated"


def original_fixture(size: int = 320) -> np.ndarray:
    image = Image.new("RGB", (size, size), (207, 222, 225))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 205, size, size), fill=(210, 173, 104))
    draw.ellipse(
        (28, 35, 177, 184),
        fill=(231, 174, 128),
        outline=(20, 22, 29),
        width=7,
    )
    draw.polygon(
        [(88, 40), (132, 4), (152, 55), (191, 17), (180, 86)],
        fill=(22, 24, 31),
        outline=(15, 16, 20),
    )
    draw.arc((65, 92, 140, 145), 20, 160, fill=(22, 24, 31), width=5)
    draw.ellipse((72, 91, 86, 105), fill=(14, 16, 20))
    draw.ellipse((126, 91, 140, 105), fill=(14, 16, 20))
    draw.rounded_rectangle(
        (54, 170, 260, 285),
        24,
        fill=(41, 99, 142),
        outline=(17, 20, 27),
        width=8,
    )
    draw.polygon(
        [(195, 77), (277, 116), (247, 185), (174, 156)],
        fill=(220, 85, 67),
        outline=(17, 20, 27),
    )
    draw.line((18, 298, 302, 298), fill=(25, 28, 34), width=6)
    return np.asarray(image, dtype=np.float32) / np.float32(255.0)


def panel(images: list[tuple[str, np.ndarray]], path: Path) -> None:
    height, width = images[0][1].shape[:2]
    canvas = Image.new("RGB", (width * len(images), height + 34), "#08111f")
    draw = ImageDraw.Draw(canvas)
    for index, (label, values) in enumerate(images):
        tile = Image.fromarray(
            np.uint8(np.clip(values, 0, 1) * 255 + 0.5),
            "RGB",
        )
        canvas.paste(tile, (index * width, 34))
        draw.text((index * width + 9, 10), label, fill="#f5f7fb")
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def _stable_json_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _stable_json_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_stable_json_value(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, (float, np.floating)):
        number = float(value)
        if not np.isfinite(number):
            raise ValueError("demo summary contains a non-finite value")
        if abs(number) < 1e-15:
            return 0.0
        return float(f"{number:.15g}")
    return value


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    source = original_fixture()
    save_rgb(OUT / "original_fixture.png", source)

    candidate_b, b_diagnostics = render_b(source)
    candidate_d3, d3_diagnostics = render_d3(source)
    save_rgb(OUT / "candidate_b.png", candidate_b)
    save_rgb(OUT / "candidate_d3.png", candidate_d3)

    labels = {
        "fold": 0,
        "segments": [
            {
                "segment_id": "SYN-001",
                "class": "outer_ink",
                "polyline": [[176.0, 88.0], [183.0, 145.0]],
                "dark_to_bright_vector": [1.0, 0.0],
                "end_exclusion_radius_px": 4.0,
                "no_edit_margin_px": 2.25,
            }
        ],
    }
    (OUT / "oracle_labels.json").write_text(
        json.dumps(labels, indent=2) + "\n",
        encoding="utf-8",
    )
    oracle, changed, oracle_diagnostics = render_oracle(
        source,
        labels["segments"],
        np.zeros(source.shape[:2], bool),
        method="P1",
        tier="R0",
        fold=0,
    )
    save_rgb(OUT / "oracle_p1_r0.png", oracle)

    panel(
        [
            ("INPUT", source),
            ("B", candidate_b),
            ("D3", candidate_d3),
            ("ORACLE", oracle),
        ],
        FIGURES / "candidate-comparison.png",
    )
    delta = np.max(np.abs(oracle - source), axis=2)
    heat = np.zeros_like(source)
    heat[..., 0] = np.clip(delta * 32.0, 0.0, 1.0)
    heat[..., 2] = 0.10
    panel(
        [("ORACLE OUTPUT", oracle), ("32x DELTA", heat)],
        FIGURES / "oracle-delta.png",
    )

    reproduce_a(OUT / "failure_a")
    reproduce_c(OUT / "failure_c")
    draw_social_preview(ROOT / "docs/figures/github-social-preview.png")

    summary = {
        "asset_policy": "synthetic_only",
        "candidate_b": b_diagnostics,
        "candidate_d3": dict(d3_diagnostics),
        "oracle_changed_pixels": int(np.count_nonzero(changed)),
        "oracle_diagnostics": dict(oracle_diagnostics),
    }
    (OUT / "demo_summary.json").write_text(
        json.dumps(_stable_json_value(summary), indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"generated_assets": 10, "protected_assets": 0}, indent=2))


if __name__ == "__main__":
    main()
