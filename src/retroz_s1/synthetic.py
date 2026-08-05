"""Public-safe synthetic reproducers for the S1 candidate lineages."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def edge_fixture(size: int = 256, angle: float = 0.0) -> np.ndarray:
    yy, xx = np.mgrid[:size, :size]
    radians = np.deg2rad(angle)
    signed = (xx - size / 2) * np.cos(radians) + (yy - size / 2) * np.sin(radians)
    alpha = np.clip(0.5 + signed / 3.0, 0.0, 1.0)
    dark = np.array([0.06, 0.07, 0.09], dtype=np.float32)
    bright = np.array([0.82, 0.63, 0.38], dtype=np.float32)
    return dark + alpha[..., None] * (bright - dark)


def reproduce_a(output: Path) -> dict:
    x = np.linspace(-4.0, 4.0, 512)
    edge = 1.0 / (1.0 + np.exp(-x * 3.0))
    confidence = np.zeros_like(edge)
    data = {"candidate": "A", "failure": "self-blocking activation", "activated_samples": int(np.count_nonzero(confidence)), "total_samples": len(confidence)}
    output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output / "activation_failure.npz", x=x, edge=edge, confidence=confidence)
    (output / "result.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def reproduce_c(output: Path) -> dict:
    fixture = edge_fixture(256, 33.0)
    blurred = fixture.copy()
    for _ in range(3):
        padded = np.pad(blurred, ((1, 1), (1, 1), (0, 0)), mode="edge")
        blurred = sum(padded[y:y+256, x:x+256] for y in range(3) for x in range(3)) / 9.0
    halo = float(np.mean(np.abs(blurred - fixture)))
    output.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.uint8(fixture * 255 + 0.5), "RGB").save(output / "source.png")
    Image.fromarray(np.uint8(np.clip(blurred, 0, 1) * 255 + 0.5), "RGB").save(output / "psf_output.png")
    data = {"candidate": "C", "failure": "raster halo and angular bias", "mean_absolute_halo_energy": halo}
    (output / "result.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def synthetic_oracle_labels(size: int = 256) -> dict:
    return {"fold": 0, "segments": [{"segment_id": "SYN-001", "class": "outer_ink", "polyline": [[size/2, 30], [size/2, size-30]], "dark_to_bright_vector": [1.0, 0.0], "end_exclusion_radius_px": 4.0, "no_edit_margin_px": 2.25}], "hard_mask": None}


def draw_social_preview(path: Path) -> None:
    width, height = 1280, 640
    image = Image.new("RGB", (width, height), "#08111f")
    draw = ImageDraw.Draw(image)
    draw.rectangle((56, 54, 78, 586), fill="#e94b5f")
    draw.text((120, 110), "RetroZ S1", fill="#f5f7fb", font=None)
    draw.text((120, 165), "INK PROFILE RECONSTRUCTION", fill="#75d4d2", font=None)
    draw.text((120, 220), "Reproducible line-transformation research", fill="#c5ccd8", font=None)
    draw.rounded_rectangle((120, 300, 505, 360), radius=18, fill="#263349")
    draw.text((145, 322), "PROVISIONAL NO-OP", fill="#ffcb69", font=None)
    for offset, color in ((0, "#75d4d2"), (42, "#e94b5f"), (84, "#ffcb69")):
        points = []
        for x in range(650, 1190, 8):
            y = 220 + offset + int(70 * np.tanh((x - 910) / (28 + offset / 4)))
            points.append((x, y))
        draw.line(points, fill=color, width=5)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
