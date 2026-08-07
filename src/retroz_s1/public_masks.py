"""Public mask approximations for user-owned demonstration images.

These masks are not the private M0 maps used in the historical TRAIN runs.
Outputs using them demonstrate the frozen operator, not exact historical replay.
"""

from __future__ import annotations

import numpy as np


LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def _neighbors(values: np.ndarray) -> list[np.ndarray]:
    height, width = values.shape
    padded = np.pad(values, 1, mode="edge")
    return [
        padded[y : y + height, x : x + width]
        for y in range(3)
        for x in range(3)
    ]


def public_masks(rgb: np.ndarray, *, for_d3: bool = False) -> dict[str, np.ndarray]:
    image = np.asarray(rgb, dtype=np.float32)
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("rgb must be an HxWx3 array")

    luma = image @ LUMA
    neighbors = _neighbors(luma)
    local_min = np.minimum.reduce(neighbors).astype(np.float32)
    local_max = np.maximum.reduce(neighbors).astype(np.float32)
    local_range = local_max - local_min

    ink = np.clip((0.38 - luma) / 0.28, 0.0, 1.0).astype(np.float32)
    flat = np.clip((0.025 - local_range) / 0.025, 0.0, 1.0).astype(np.float32)
    background = np.zeros_like(luma, dtype=np.float32)
    effects = np.zeros_like(luma, dtype=np.float32)

    if for_d3:
        result = {
            "ink": ink,
            "flat": flat,
            "background": background,
            "fx": effects,
        }
        for value in result.values():
            value.setflags(write=False)
        return result

    recipient = np.clip((local_max - luma - 0.02) / 0.18, 0.0, 1.0).astype(
        np.float32
    )
    return {
        "flat": flat,
        "ink": ink,
        "ink_recipient": recipient,
        "fx": effects,
        "background": background,
        "local_min_luma": local_min,
        "local_max_luma": local_max,
    }
