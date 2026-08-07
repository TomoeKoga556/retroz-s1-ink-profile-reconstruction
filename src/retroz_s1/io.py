"""Image and provenance I/O for user-owned public inputs."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

import numpy as np
from PIL import Image


def load_rgb(path: Path) -> np.ndarray:
    if not path.is_file():
        raise FileNotFoundError(path)
    with Image.open(path) as image:
        rgb = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.size == 0:
        raise ValueError("input must decode to a non-empty RGB image")
    if not np.all(np.isfinite(rgb)):
        raise ValueError("input must contain only finite RGB values")
    return np.ascontiguousarray(rgb, dtype=np.float32)


def save_rgb(path: Path, rgb: np.ndarray) -> None:
    array = np.asarray(rgb, dtype=np.float32)
    if array.ndim != 3 or array.shape[2] != 3 or array.size == 0:
        raise ValueError("output must be a non-empty HxWx3 RGB array")
    if not np.all(np.isfinite(array)):
        raise ValueError("output must contain only finite RGB values")
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.fromarray(
        np.uint8(np.clip(array, 0.0, 1.0) * 255.0 + 0.5),
        "RGB",
    )
    image.save(path)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _jsonable(value: object) -> object:
    """Convert immutable diagnostics and NumPy values into plain JSON data."""
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def write_provenance(output: Path, payload: dict[str, object]) -> Path:
    path = output.with_suffix(output.suffix + ".provenance.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path
