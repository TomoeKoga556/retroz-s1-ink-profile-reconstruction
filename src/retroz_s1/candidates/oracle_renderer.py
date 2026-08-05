"""V2 manual-oracle renderer: V1 plus D3-bound read-only plateau radius.

V1's plateau colors were estimated only from the writable 2.25 px tube.  On a
clean raster edge that collapses observed alpha to 0/0.5/1 and makes P1 an
accidental no-op.  V2 preserves the exact write tube and every optical value,
but estimates plateaus from D3-R0's preregistered read-only neighborhood:
``max(3 px, 2.5 * max(target side width))``.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping, Sequence

import numpy as np

from retroz_s1.candidates import oracle_core as v1


RENDERER_ID = "s1_manual_ink_oracle_renderer_v2"
OracleRendererParams = v1.OracleRendererParams
R1_CAPS_540 = v1.R1_CAPS_540


def _plateaus_from_read_neighborhood(
    linear: np.ndarray,
    hard: np.ndarray,
    polyline: np.ndarray,
    direction: np.ndarray,
    dark_width: float,
    bright_width: float,
    minimum: int,
    denominator_min: float,
) -> tuple[np.ndarray, np.ndarray, float] | None:
    radius = max(3.0, 2.5 * max(dark_width, bright_width))
    y, x, signed = v1._segment_pixels(linear.shape[:2], polyline, direction, radius)
    allowed = ~hard[y, x]
    dark_values = linear[y, x][allowed & (signed <= -0.5 * dark_width)]
    bright_values = linear[y, x][allowed & (signed >= 0.5 * bright_width)]
    if len(dark_values) < minimum or len(bright_values) < minimum:
        return None
    dark = np.median(dark_values, axis=0)
    bright = np.median(bright_values, axis=0)
    axis = bright - dark
    if not np.all(np.isfinite(dark)) or not np.all(np.isfinite(bright)):
        return None
    if float(np.dot(axis, axis)) < denominator_min:
        return None
    return dark, bright, radius


def render_oracle(
    source_rgb: np.ndarray,
    segments: Sequence[Mapping[str, object]],
    hard_mask: np.ndarray,
    *,
    method: str,
    tier: str,
    fold: int,
    params: OracleRendererParams | None = None,
) -> tuple[np.ndarray, np.ndarray, Mapping[str, object]]:
    params = OracleRendererParams() if params is None else params
    params.validate()
    if method not in {"P1", "P2", "P3"}:
        raise ValueError("method must be P1, P2, or P3")
    if tier not in {"R0", "R1", "R3"}:
        raise ValueError("R2 is evidence-gated disabled; executable tiers are R0/R1/R3")
    if method == "P1" and tier != "R0":
        raise ValueError("P1 has no preregistered spatial p50-offset formula beyond R0")
    if fold not in R1_CAPS_540:
        raise ValueError("fold must be 0..4")
    source = np.asarray(source_rgb)
    if source.dtype != np.float32 or source.ndim != 3 or source.shape[2] != 3:
        raise TypeError("source_rgb must be HxWx3 float32")
    if not np.all(np.isfinite(source)) or np.any((source < 0.0) | (source > 1.0)):
        raise ValueError("source_rgb must be finite [0,1]")
    hard = np.asarray(hard_mask)
    if hard.shape != source.shape[:2] or hard.dtype != np.bool_:
        raise TypeError("hard_mask must be HxW bool")
    source_before = source.copy()
    hard_before = hard.copy()
    linear = v1._srgb_to_linear(source)
    output_linear = linear.copy()
    changed_support = np.zeros(source.shape[:2], dtype=bool)
    occupied = np.zeros(source.shape[:2], dtype=bool)
    height = source.shape[0]
    target_scale = float(height) / 540.0
    support_scale = float(height) / 720.0
    dark_width = params.dark_target_width_540px * target_scale
    bright_width = params.bright_target_width_540px * target_scale
    support_radius = params.support_radius_720px * support_scale
    p50_offset = 0.0 if tier == "R0" else -float(R1_CAPS_540[fold]) * target_scale
    offsets = v1._subpixel_offsets(params.subsamples_per_axis)
    records: list[dict[str, object]] = []

    for raw in sorted(segments, key=lambda row: str(row["segment_id"])):
        segment_id = str(raw["segment_id"])
        klass = str(raw["class"])
        if klass not in {"outer_ink", "inner_ink_fold"}:
            records.append({"segment_id": segment_id, "status": "NOOP", "reason": "semantic_class"})
            continue
        polyline = np.asarray(raw["polyline"], np.float64)
        direction = np.asarray(raw["dark_to_bright_vector"], np.float64)
        try:
            trimmed = v1._trim_polyline(
                polyline,
                float(raw["end_exclusion_radius_px"]),
                float(raw["end_exclusion_radius_px"]),
            )
            local_radius = min(support_radius, float(raw["no_edit_margin_px"]))
            y, x, signed = v1._segment_pixels(source.shape[:2], trimmed, direction, local_radius)
        except (KeyError, TypeError, ValueError) as error:
            records.append({"segment_id": segment_id, "status": "NOOP", "reason": f"geometry:{error}"})
            continue
        if len(y) == 0:
            records.append({"segment_id": segment_id, "status": "NOOP", "reason": "empty_support"})
            continue
        allowed = ~hard[y, x]
        if np.any(occupied[y[allowed], x[allowed]]):
            records.append({"segment_id": segment_id, "status": "NOOP", "reason": "support_overlap"})
            continue
        plateau = _plateaus_from_read_neighborhood(
            linear, hard, trimmed, direction, dark_width, bright_width,
            params.minimum_plateau_samples_each, params.projection_denominator_min,
        )
        if plateau is None:
            records.append({"segment_id": segment_id, "status": "NOOP", "reason": "plateau_evidence"})
            continue
        dark, bright, plateau_radius = plateau
        axis = bright - dark
        denominator = float(np.dot(axis, axis))
        rgb = linear[y, x]
        alpha_source = np.clip(((rgb - dark) @ axis) / denominator, 0.0, 1.0)
        residual = rgb - (dark + alpha_source[:, None] * axis)
        points = np.column_stack((x.astype(np.float64), y.astype(np.float64)))
        if method == "P1":
            alpha_target = v1._p1_transport(alpha_source, params)
        else:
            coverage = v1._target_coverage(
                points, trimmed, direction, dark_width, bright_width, p50_offset, offsets
            )
            if method == "P2":
                alpha_target = coverage
            else:
                order = np.argsort(signed, kind="stable")
                monotone = np.empty_like(alpha_source)
                monotone[order] = v1._project_monotone(alpha_source[order])
                alpha_target = np.clip(alpha_source + (coverage - monotone), 0.0, 1.0)
        candidate = dark + alpha_target[:, None] * axis + residual
        write = allowed
        if not np.any(write):
            records.append({"segment_id": segment_id, "status": "NOOP", "reason": "hard_mask"})
            continue
        if not np.all(np.isfinite(candidate[write])):
            records.append({"segment_id": segment_id, "status": "NOOP", "reason": "nonfinite"})
            continue
        if np.any((candidate[write] < -params.hard_rgb_epsilon) | (candidate[write] > 1.0 + params.hard_rgb_epsilon)):
            records.append({"segment_id": segment_id, "status": "NOOP", "reason": "gamut"})
            continue
        output_linear[y[write], x[write]] = np.clip(candidate[write], 0.0, 1.0)
        occupied[y[write], x[write]] = True
        delta = np.max(np.abs(candidate[write] - rgb[write]), axis=1)
        materially_changed = delta > 1e-12
        if np.any(materially_changed):
            changed_support[y[write][materially_changed], x[write][materially_changed]] = True
        records.append({
            "segment_id": segment_id,
            "class": klass,
            "status": "APPLIED",
            "support_pixels": int(np.count_nonzero(write)),
            "changed_pixels_linear": int(np.count_nonzero(materially_changed)),
            "mean_abs_linear_rgb": float(np.mean(np.abs(candidate[write] - rgb[write]))),
            "max_abs_linear_rgb": float(np.max(np.abs(candidate[write] - rgb[write]))),
            "plateau_read_radius_px": float(plateau_radius),
            "dark_plateau_linear_rgb": [float(value) for value in dark],
            "bright_plateau_linear_rgb": [float(value) for value in bright],
        })

    output = np.clip(v1._linear_to_srgb(output_linear), 0.0, 1.0).astype(np.float32)
    output[~occupied] = source[~occupied]
    output[hard] = source[hard]
    if not np.array_equal(source, source_before) or not np.array_equal(hard, hard_before):
        raise RuntimeError("renderer mutated an input")
    if np.any(output[hard] != source[hard]) or np.any(output[~occupied] != source[~occupied]):
        raise RuntimeError("renderer violated exact passthrough")
    if not np.all(np.isfinite(output)):
        raise RuntimeError("renderer produced nonfinite RGB")
    applied = sum(record["status"] == "APPLIED" for record in records)
    diagnostics = MappingProxyType({
        "renderer_id": RENDERER_ID,
        "supersedes_renderer_id": v1.RENDERER_ID,
        "v1_failure": "plateau_read_neighborhood_was_incorrectly_limited_to_write_tube",
        "method": method,
        "tier": tier,
        "fold": int(fold),
        "native_shape_hw": [int(source.shape[0]), int(source.shape[1])],
        "dark_target_width_px": dark_width,
        "bright_target_width_px": bright_width,
        "support_radius_px": support_radius,
        "p50_offset_px": p50_offset,
        "segment_count": len(segments),
        "applied_segment_count": applied,
        "noop_segment_count": len(records) - applied,
        "occupied_pixel_count": int(np.count_nonzero(occupied)),
        "changed_pixel_count": int(np.count_nonzero(changed_support)),
        "outside_oracle_changed_pixel_count": int(np.count_nonzero((output != source).any(axis=2) & ~occupied)),
        "hard_changed_pixel_count": int(np.count_nonzero((output != source).any(axis=2) & hard)),
        "segment_records": tuple(records),
    })
    return v1._readonly(output), v1._readonly(occupied), diagnostics


__all__ = ["OracleRendererParams", "R1_CAPS_540", "RENDERER_ID", "render_oracle"]
