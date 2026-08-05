"""Resolve frozen exclusion regions with explicit Oracle-tube exceptions."""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np

from retroz_s1.candidates import oracle_core as v1


def allow_explicit_segment_tubes(
    exclusion_mask: np.ndarray,
    segments: Sequence[Mapping[str, object]],
    shape: tuple[int, int],
) -> np.ndarray:
    """Return exclusion mask minus only the frozen, endpoint-trimmed tubes.

    This implements label text such as "whole frame excluded; only explicit
    character segment tubes may be considered".  It never expands the tube and
    does not alter any label geometry.
    """

    mask = np.asarray(exclusion_mask)
    if mask.dtype != np.bool_ or mask.shape != shape:
        raise TypeError("exclusion_mask must be HxW bool")
    result = mask.copy()
    support_radius = 2.25 * (float(shape[0]) / 720.0)
    for raw in segments:
        polyline = np.asarray(raw["polyline"], np.float64)
        direction = np.asarray(raw["dark_to_bright_vector"], np.float64)
        trimmed = v1._trim_polyline(
            polyline,
            float(raw["end_exclusion_radius_px"]),
            float(raw["end_exclusion_radius_px"]),
        )
        radius = min(support_radius, float(raw["no_edit_margin_px"]))
        y, x, _ = v1._segment_pixels(shape, trimmed, direction, radius)
        result[y, x] = False
    return result


__all__ = ["allow_explicit_segment_tubes"]
