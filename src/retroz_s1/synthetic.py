"""Public-safe synthetic reproducers for the S1 candidate lineages."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def edge_fixture(size: int = 256, angle: float = 0.0) -> np.ndarray:
    if size < 8:
        raise ValueError("size must be at least 8 pixels")
    yy, xx = np.mgrid[:size, :size]
    radians = np.deg2rad(angle)
    signed = (xx - size / 2) * np.cos(radians) + (yy - size / 2) * np.sin(
        radians
    )
    alpha = np.clip(0.5 + signed / 3.0, 0.0, 1.0)
    dark = np.array([0.06, 0.07, 0.09], dtype=np.float32)
    bright = np.array([0.82, 0.63, 0.38], dtype=np.float32)
    return dark + alpha[..., None] * (bright - dark)


def reproduce_a(output: Path) -> dict[str, object]:
    raw_x = np.linspace(-4.0, 4.0, 512, dtype=np.float64)
    raw_edge = 1.0 / (1.0 + np.exp(-raw_x * 3.0))

    # Normalize insignificant libm/SIMD differences before serialization.
    x = np.ascontiguousarray(np.round(raw_x, 12), dtype="<f8")
    edge = np.ascontiguousarray(np.round(raw_edge, 12), dtype="<f8")
    confidence = np.zeros(edge.shape, dtype="<f8")
    data = {
        "candidate": "A",
        "failure": "self-blocking activation",
        "activated_samples": int(np.count_nonzero(confidence)),
        "total_samples": len(confidence),
    }
    output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output / "activation_failure.npz",
        x=x,
        edge=edge,
        confidence=confidence,
    )
    (output / "result.json").write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8",
    )
    return data


def reproduce_c(output: Path) -> dict[str, object]:
    fixture = edge_fixture(256, 33.0)
    blurred = fixture.copy()
    for _ in range(3):
        padded = np.pad(blurred, ((1, 1), (1, 1), (0, 0)), mode="edge")
        blurred = sum(
            padded[y : y + 256, x : x + 256]
            for y in range(3)
            for x in range(3)
        ) / 9.0

    halo = float(np.mean(np.abs(blurred - fixture)))
    output.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.uint8(fixture * 255 + 0.5), "RGB").save(
        output / "source.png"
    )
    Image.fromarray(
        np.uint8(np.clip(blurred, 0, 1) * 255 + 0.5),
        "RGB",
    ).save(output / "psf_output.png")
    data = {
        "candidate": "C",
        "failure": "raster halo and angular bias",
        "mean_absolute_halo_energy": halo,
    }
    (output / "result.json").write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8",
    )
    return data


def synthetic_oracle_labels(size: int = 256) -> dict[str, object]:
    return {
        "fold": 0,
        "segments": [
            {
                "segment_id": "SYN-001",
                "class": "outer_ink",
                "polyline": [[size / 2, 30], [size / 2, size - 30]],
                "dark_to_bright_vector": [1.0, 0.0],
                "end_exclusion_radius_px": 4.0,
                "no_edit_margin_px": 2.25,
            }
        ],
        "hard_mask": None,
    }


def _font(size: int, *, bold: bool = False) -> ImageFont.ImageFont:
    filename = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        import matplotlib

        font_path = Path(matplotlib.get_data_path()) / "fonts" / "ttf" / filename
        return ImageFont.truetype(str(font_path), size=size)
    except (ImportError, OSError):
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()


def draw_social_preview(path: Path) -> None:
    width, height = 1280, 640
    image = Image.new("RGB", (width, height), "#0a1322")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, 20, height), fill="#d85062")
    draw.text((78, 82), "RETROZ S1", fill="#75d4d2", font=_font(27, bold=True))
    draw.text(
        (78, 132),
        "Ink Profile Reconstruction",
        fill="#f4f7fb",
        font=_font(50, bold=True),
    )
    draw.text(
        (80, 205),
        "Reproducible evaluation · bounded negative result",
        fill="#b9c4d4",
        font=_font(23),
    )

    draw.rounded_rectangle((80, 288, 500, 364), radius=18, fill="#26364f")
    draw.text(
        (108, 309),
        "RESULT: IDENTITY / BYPASS",
        fill="#f5c566",
        font=_font(23, bold=True),
    )
    draw.text(
        (80, 420),
        "Five candidate lineages tested. None qualified for production activation.",
        fill="#d8e0eb",
        font=_font(22),
    )
    draw.text(
        (80, 470),
        "What remains: the evaluator, provenance records and documented failure cases.",
        fill="#9eacbf",
        font=_font(19),
    )

    for offset, color in ((0, "#75d4d2"), (54, "#d85062"), (108, "#f5c566")):
        points = []
        for x in range(890, 1210, 5):
            y = 200 + offset + int(86 * np.tanh((x - 1050) / (32 + offset / 5)))
            points.append((x, y))
        draw.line(points, fill=color, width=6)

    draw.line((700, 510, 1210, 510), fill="#31425a", width=2)
    draw.text((720, 538), "measurable change ≠ useful visible change", fill="#9eacbf", font=_font(18))

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
