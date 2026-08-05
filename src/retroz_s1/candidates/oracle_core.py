"""Pure, file-I/O-free renderer for the frozen manual S1 ink oracle.

All numeric values originate in the bound S1 final-renderer and D3-E0/D3-R0
research.  The module never discovers geometry from RGB: geometry, polarity,
safe endpoints, and exclusions are supplied by the frozen human oracle.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from types import MappingProxyType
from typing import Mapping, Sequence

import numpy as np


RENDERER_ID = "s1_manual_ink_oracle_renderer_v1"
LOG9 = 2.1972245773362196
R1_CAPS_540 = MappingProxyType({
    0: 0.03639833,
    1: 0.04030379,
    2: 0.03639833,
    3: 0.03639833,
    4: 0.05176423,
})


@dataclass(frozen=True)
class OracleRendererParams:
    dark_half_scale: float = 1.206
    bright_half_scale: float = 1.137
    dark_target_width_540px: float = 0.9865
    bright_target_width_540px: float = 1.0417
    support_radius_720px: float = 2.25
    subsamples_per_axis: int = 4
    minimum_plateau_samples_each: int = 4
    projection_denominator_min: float = 1e-10
    hard_rgb_epsilon: float = 1e-7

    def validate(self) -> None:
        expected = {
            "dark_half_scale": 1.206,
            "bright_half_scale": 1.137,
            "dark_target_width_540px": 0.9865,
            "bright_target_width_540px": 1.0417,
            "support_radius_720px": 2.25,
            "subsamples_per_axis": 4,
            "minimum_plateau_samples_each": 4,
            "projection_denominator_min": 1e-10,
            "hard_rgb_epsilon": 1e-7,
        }
        if type(self) is not OracleRendererParams or asdict(self) != expected:
            raise ValueError("Oracle renderer parameters differ from preregistration")


def _readonly(value: np.ndarray) -> np.ndarray:
    result = np.ascontiguousarray(value)
    result.setflags(write=False)
    return result


def _srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    value = np.asarray(rgb, np.float64)
    return np.where(value <= 0.04045, value / 12.92, ((value + 0.055) / 1.055) ** 2.4)


def _linear_to_srgb(rgb: np.ndarray) -> np.ndarray:
    value = np.asarray(rgb, np.float64)
    return np.where(value <= 0.0031308, 12.92 * value, 1.055 * np.maximum(value, 0.0) ** (1.0 / 2.4) - 0.055)


def _sigmoid(value: np.ndarray) -> np.ndarray:
    x = np.asarray(value, np.float64)
    result = np.empty_like(x)
    positive = x >= 0.0
    result[positive] = 1.0 / (1.0 + np.exp(-x[positive]))
    exp_value = np.exp(x[~positive])
    result[~positive] = exp_value / (1.0 + exp_value)
    return result


def _p1_transport(alpha: np.ndarray, params: OracleRendererParams) -> np.ndarray:
    source = np.clip(np.asarray(alpha, np.float64), 0.0, 1.0)
    result = source.copy()
    interior = (source > 0.0) & (source < 1.0) & (source != 0.5)
    if np.any(interior):
        clipped = np.clip(source[interior], 1e-12, 1.0 - 1e-12)
        logit = np.log(clipped / (1.0 - clipped))
        scale = np.where(clipped < 0.5, params.dark_half_scale, params.bright_half_scale)
        result[interior] = _sigmoid(logit / scale)
    result[source == 0.0] = 0.0
    result[source == 0.5] = 0.5
    result[source == 1.0] = 1.0
    return result


def _project_monotone(values: np.ndarray) -> np.ndarray:
    flat = np.clip(np.asarray(values, np.float64).reshape(-1), 0.0, 1.0)
    blocks: list[list[float]] = []
    for value in flat:
        blocks.append([float(value), 1.0])
        while len(blocks) >= 2 and blocks[-2][0] / blocks[-2][1] > blocks[-1][0] / blocks[-1][1]:
            right = blocks.pop()
            left = blocks.pop()
            blocks.append([left[0] + right[0], left[1] + right[1]])
    result = np.empty_like(flat)
    cursor = 0
    for total, count in blocks:
        length = int(count)
        result[cursor:cursor + length] = total / count
        cursor += length
    return result


def _trim_polyline(points: np.ndarray, trim_start: float, trim_end: float) -> np.ndarray:
    points = np.asarray(points, np.float64)
    delta = np.diff(points, axis=0)
    lengths = np.linalg.norm(delta, axis=1)
    if np.any(lengths <= 0.0) or len(points) < 2:
        raise ValueError("polyline must contain distinct consecutive points")
    cumulative = np.concatenate(([0.0], np.cumsum(lengths)))
    total = float(cumulative[-1])
    start = float(trim_start)
    end = total - float(trim_end)
    if not (0.0 <= start < end <= total):
        raise ValueError("endpoint exclusions consume the complete polyline")

    def at(distance: float) -> np.ndarray:
        index = min(int(np.searchsorted(cumulative, distance, side="right") - 1), len(delta) - 1)
        fraction = (distance - cumulative[index]) / lengths[index]
        return points[index] + fraction * delta[index]

    output = [at(start)]
    for index in range(1, len(points) - 1):
        if start < cumulative[index] < end:
            output.append(points[index])
    output.append(at(end))
    return np.vstack(output)


def _signed_distance(points_xy: np.ndarray, polyline_xy: np.ndarray, direction_xy: np.ndarray) -> np.ndarray:
    points = np.asarray(points_xy, np.float64)
    polyline = np.asarray(polyline_xy, np.float64)
    direction = np.asarray(direction_xy, np.float64)
    norm = float(np.linalg.norm(direction))
    if norm <= 0.0 or not math.isfinite(norm):
        raise ValueError("dark_to_bright_vector must be finite and nonzero")
    direction /= norm
    best_distance2 = np.full(len(points), np.inf, np.float64)
    best_sign_source = np.zeros(len(points), np.float64)
    for start, end in zip(polyline[:-1], polyline[1:], strict=True):
        delta = end - start
        length2 = float(np.dot(delta, delta))
        if length2 <= 0.0:
            raise ValueError("degenerate polyline segment")
        relative = points - start
        fraction = np.clip((relative @ delta) / length2, 0.0, 1.0)
        nearest = start + fraction[:, None] * delta
        residual = points - nearest
        distance2 = np.einsum("ij,ij->i", residual, residual)
        improve = distance2 < best_distance2
        best_distance2[improve] = distance2[improve]
        best_sign_source[improve] = residual[improve] @ direction
    sign = np.sign(best_sign_source)
    sign[sign == 0.0] = 1.0
    return np.sqrt(np.maximum(best_distance2, 0.0)) * sign


def _subpixel_offsets(count: int) -> np.ndarray:
    positions = (np.arange(count, dtype=np.float64) + 0.5) / float(count) - 0.5
    yy, xx = np.meshgrid(positions, positions, indexing="ij")
    return np.column_stack((xx.ravel(), yy.ravel()))


def _target_coverage(
    points_xy: np.ndarray,
    polyline: np.ndarray,
    direction: np.ndarray,
    dark_width: float,
    bright_width: float,
    p50_offset: float,
    offsets: np.ndarray,
) -> np.ndarray:
    samples = (points_xy[:, None, :] + offsets[None, :, :]).reshape(-1, 2)
    signed = _signed_distance(samples, polyline, direction) - p50_offset
    slope = np.where(signed <= 0.0, LOG9 / dark_width, LOG9 / bright_width)
    coverage = _sigmoid(slope * signed)
    return coverage.reshape(len(points_xy), len(offsets)).mean(axis=1)


def _segment_pixels(
    shape: tuple[int, int],
    polyline: np.ndarray,
    direction: np.ndarray,
    radius: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    height, width = shape
    minimum_x = max(0, int(math.floor(float(np.min(polyline[:, 0])) - radius)))
    maximum_x = min(width - 1, int(math.ceil(float(np.max(polyline[:, 0])) + radius)))
    minimum_y = max(0, int(math.floor(float(np.min(polyline[:, 1])) - radius)))
    maximum_y = min(height - 1, int(math.ceil(float(np.max(polyline[:, 1])) + radius)))
    yy, xx = np.mgrid[minimum_y:maximum_y + 1, minimum_x:maximum_x + 1]
    points = np.column_stack((xx.ravel(), yy.ravel())).astype(np.float64)
    signed = _signed_distance(points, polyline, direction)
    keep = np.abs(signed) <= radius + 1e-12
    return yy.ravel()[keep], xx.ravel()[keep], signed[keep]


def _plateaus(
    linear: np.ndarray,
    y: np.ndarray,
    x: np.ndarray,
    signed: np.ndarray,
    hard: np.ndarray,
    dark_width: float,
    bright_width: float,
    minimum: int,
    denominator_min: float,
) -> tuple[np.ndarray, np.ndarray] | None:
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
    return dark, bright


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
    """Render one frozen method/tier combination inside manual oracle tubes."""

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
    linear = _srgb_to_linear(source)
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
    offsets = _subpixel_offsets(params.subsamples_per_axis)
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
            trimmed = _trim_polyline(
                polyline,
                float(raw["end_exclusion_radius_px"]),
                float(raw["end_exclusion_radius_px"]),
            )
            local_radius = min(support_radius, float(raw["no_edit_margin_px"]))
            y, x, signed = _segment_pixels(source.shape[:2], trimmed, direction, local_radius)
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
        plateau = _plateaus(
            linear, y, x, signed, hard, dark_width, bright_width,
            params.minimum_plateau_samples_each, params.projection_denominator_min,
        )
        if plateau is None:
            records.append({"segment_id": segment_id, "status": "NOOP", "reason": "plateau_evidence"})
            continue
        dark, bright = plateau
        axis = bright - dark
        denominator = float(np.dot(axis, axis))
        rgb = linear[y, x]
        alpha_source = np.clip(((rgb - dark) @ axis) / denominator, 0.0, 1.0)
        residual = rgb - (dark + alpha_source[:, None] * axis)
        points = np.column_stack((x.astype(np.float64), y.astype(np.float64)))

        if method == "P1":
            alpha_target = _p1_transport(alpha_source, params)
        else:
            coverage = _target_coverage(
                points, trimmed, direction, dark_width, bright_width, p50_offset, offsets
            )
            if method == "P2":
                alpha_target = coverage
            else:
                order = np.argsort(signed, kind="stable")
                monotone = np.empty_like(alpha_source)
                monotone[order] = _project_monotone(alpha_source[order])
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
            "dark_plateau_linear_rgb": [float(value) for value in dark],
            "bright_plateau_linear_rgb": [float(value) for value in bright],
        })

    output = np.clip(_linear_to_srgb(output_linear), 0.0, 1.0).astype(np.float32)
    # Restore exact input values for every untouched or hard pixel.
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
    return _readonly(output), _readonly(occupied), diagnostics


__all__ = [
    "OracleRendererParams",
    "R1_CAPS_540",
    "RENDERER_ID",
    "render_oracle",
]
