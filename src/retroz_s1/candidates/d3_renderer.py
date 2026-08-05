"""D3-R0 implicit-contour cell-coverage renderer.

This module implements only the formula preregistered in
``D3_R0_RENDERER_PREREGISTRATION.json``.  It performs no file I/O, opens no
media, and does not contain a Common-Evaluator adapter.  Geometry is taken only
from the bound D3-E0 source/M0 contour estimator.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from types import MappingProxyType
from typing import Mapping

import numpy as np

from retroz_s1.geometry.contour_estimator import D3E0EstimatorResult, estimate_d3_e0


RENDERER_ID = "s1_candidate_d3_r0_contour_cell_coverage_renderer_v1"
BOUND_ESTIMATOR_ID = "s1_candidate_d3_e0_contour_estimator_v2"


@dataclass(frozen=True)
class D3R0Params:
    """Exact renderer parameters bound by the R0 preregistration."""

    low_dark_p10_to_p50_width_720px: float = 0.9865
    high_recipient_p50_to_p90_width_720px: float = 1.0417
    subsamples_per_axis: int = 4
    dark_plateau_ink_min: float = 0.90
    recipient_plateau_ink_max: float = 0.10
    minimum_plateau_samples_each: int = 4
    hard_rgb_epsilon: float = 1e-7
    projection_denominator_min: float = 1e-10

    def validate(self) -> None:
        if type(self) is not D3R0Params:
            raise TypeError("D3-R0 params must use the exact D3R0Params type")
        actual = asdict(self)
        if set(actual) != set(FROZEN_PARAMETER_VALUES):
            raise ValueError("D3-R0 parameter schema differs from preregistration")
        for name, expected in FROZEN_PARAMETER_VALUES.items():
            value = actual[name]
            if isinstance(value, (bool, np.bool_)) or not isinstance(
                value, (int, float, np.integer, np.floating)
            ):
                raise TypeError(f"D3-R0 parameter {name!r} must be real numeric")
            if type(value) is not type(expected):
                raise TypeError(f"D3-R0 parameter {name!r} type drift")
            if not math.isfinite(float(value)):
                raise ValueError(f"D3-R0 parameter {name!r} must be finite")
            if value != expected:
                raise ValueError(
                    f"D3-R0 parameter drift: {name}={value!r}, "
                    f"preregistered={expected!r}"
                )


FROZEN_PARAMETER_VALUES: Mapping[str, float | int] = MappingProxyType({
    "low_dark_p10_to_p50_width_720px": 0.9865,
    "high_recipient_p50_to_p90_width_720px": 1.0417,
    "subsamples_per_axis": 4,
    "dark_plateau_ink_min": 0.90,
    "recipient_plateau_ink_max": 0.10,
    "minimum_plateau_samples_each": 4,
    "hard_rgb_epsilon": 1e-7,
    "projection_denominator_min": 1e-10,
})


def _readonly(array: np.ndarray) -> np.ndarray:
    result = np.ascontiguousarray(array)
    result.setflags(write=False)
    return result


def _validate_renderer_inputs(
    source_rgb: np.ndarray,
    native_masks: Mapping[str, np.ndarray],
) -> tuple[tuple[int, int], dict[str, np.ndarray]]:
    if not isinstance(source_rgb, np.ndarray):
        raise TypeError("D3-R0 source_rgb must be a numpy ndarray")
    if source_rgb.ndim != 3 or source_rgb.shape[2] != 3:
        raise ValueError(f"D3-R0 expected HxWx3 source RGB, got {source_rgb.shape}")
    if source_rgb.dtype != np.float32:
        raise TypeError("D3-R0 source RGB must have exact float32 dtype")
    if source_rgb.shape[0] < 2 or source_rgb.shape[1] < 2:
        raise ValueError("D3-R0 source matrix must contain at least one cell")
    if not np.all(np.isfinite(source_rgb)):
        raise ValueError("D3-R0 source RGB contains non-finite values")
    if np.any((source_rgb < 0.0) | (source_rgb > 1.0)):
        raise ValueError("D3-R0 source RGB must stay within [0, 1]")
    if not isinstance(native_masks, Mapping):
        raise TypeError("D3-R0 native_masks must be a mapping")

    shape = source_rgb.shape[:2]
    copied: dict[str, np.ndarray] = {}
    for name in ("ink", "fx", "background", "flat"):
        if name not in native_masks:
            raise KeyError(f"D3-R0 native masks omit {name!r}")
        raw = native_masks[name]
        if not isinstance(raw, np.ndarray):
            raise TypeError(f"D3-R0 mask {name!r} must be a numpy ndarray")
        if raw.shape != shape:
            raise ValueError(
                f"D3-R0 mask {name!r} has shape {raw.shape}, expected {shape}"
            )
        if raw.dtype != np.float32:
            raise TypeError(f"D3-R0 mask {name!r} must have exact float32 dtype")
        if raw.flags.writeable:
            raise ValueError(f"D3-R0 mask {name!r} must be read-only")
        if not np.all(np.isfinite(raw)):
            raise ValueError(f"D3-R0 mask {name!r} contains non-finite values")
        if np.any((raw < 0.0) | (raw > 1.0)):
            raise ValueError(f"D3-R0 mask {name!r} must stay within [0, 1]")
        copied[name] = np.array(raw, dtype=np.float32, order="C", copy=True)
    return shape, copied


def _hard_mask(masks: Mapping[str, np.ndarray]) -> np.ndarray:
    return (
        (masks["fx"] >= 0.55)
        | (masks["background"] >= 0.82)
        | (masks["flat"] >= 0.72)
    )


def _subpixel_offsets(count: int) -> np.ndarray:
    positions = (np.arange(count, dtype=np.float64) + 0.5) / float(count) - 0.5
    yy, xx = np.meshgrid(positions, positions, indexing="ij")
    return np.column_stack((xx.ravel(), yy.ravel()))


def _signed_distance_to_polyline(points_xy: np.ndarray, polyline_xy: np.ndarray) -> np.ndarray:
    points = np.asarray(points_xy, dtype=np.float64)
    polyline = np.asarray(polyline_xy, dtype=np.float64)
    if polyline.ndim != 2 or polyline.shape[1] != 2 or len(polyline) < 2:
        raise ValueError("D3-R0 patch polyline must contain at least two points")

    best_distance2 = np.full(len(points), np.inf, dtype=np.float64)
    best_signed = np.zeros(len(points), dtype=np.float64)
    for start, end in zip(polyline[:-1], polyline[1:], strict=True):
        delta = end - start
        length2 = float(np.dot(delta, delta))
        if length2 <= 0.0 or not math.isfinite(length2):
            raise ValueError("D3-R0 patch polyline contains a degenerate segment")
        relative = points - start
        fraction = np.clip((relative @ delta) / length2, 0.0, 1.0)
        nearest = start + fraction[:, None] * delta
        residual = points - nearest
        distance2 = np.einsum("ij,ij->i", residual, residual)
        length = math.sqrt(length2)
        left_normal = np.array([delta[1] / length, -delta[0] / length], dtype=np.float64)
        signed = -(residual @ left_normal)
        improve = distance2 < best_distance2
        best_distance2[improve] = distance2[improve]
        best_signed[improve] = signed[improve]
    return best_signed


def _alpha_from_signed_distance(
    signed_distance_px: np.ndarray,
    low_width_px: float,
    high_width_px: float,
) -> np.ndarray:
    log9 = 2.1972245773362196
    signed = np.asarray(signed_distance_px, dtype=np.float64)
    result = np.empty_like(signed)
    low = signed <= 0.0
    result[low] = 1.0 / (1.0 + np.exp(-(log9 / low_width_px) * signed[low]))
    result[~low] = 1.0 / (1.0 + np.exp(-(log9 / high_width_px) * signed[~low]))
    return np.clip(result, 0.0, 1.0)


def _patch_plateaus(
    source_rgb: np.ndarray,
    ink: np.ndarray,
    hard: np.ndarray,
    patch_coordinates_xy: np.ndarray,
    low_width_px: float,
    high_width_px: float,
    params: D3R0Params,
) -> tuple[np.ndarray, np.ndarray] | None:
    height, width = ink.shape
    radius = max(3.0, 2.5 * max(low_width_px, high_width_px))
    minimum_x = max(0, int(math.floor(float(np.min(patch_coordinates_xy[:, 0])) - radius)))
    maximum_x = min(width - 1, int(math.ceil(float(np.max(patch_coordinates_xy[:, 0])) + radius)))
    minimum_y = max(0, int(math.floor(float(np.min(patch_coordinates_xy[:, 1])) - radius)))
    maximum_y = min(height - 1, int(math.ceil(float(np.max(patch_coordinates_xy[:, 1])) + radius)))
    if minimum_x > maximum_x or minimum_y > maximum_y:
        return None
    yy, xx = np.mgrid[minimum_y:maximum_y + 1, minimum_x:maximum_x + 1]
    candidate_points = np.column_stack((xx.ravel(), yy.ravel())).astype(np.float64)
    candidate_y = yy.ravel()
    candidate_x = xx.ravel()
    try:
        signed = _signed_distance_to_polyline(candidate_points, patch_coordinates_xy)
    except ValueError:
        return None
    local_hard = hard[candidate_y, candidate_x]
    local_ink = ink[candidate_y, candidate_x]
    local_rgb = source_rgb[candidate_y, candidate_x].astype(np.float64, copy=False)
    dark_mask = (
        (~local_hard)
        & (signed <= -0.5 * low_width_px)
        & (local_ink >= params.dark_plateau_ink_min)
    )
    recipient_mask = (
        (~local_hard)
        & (signed >= 0.5 * high_width_px)
        & (local_ink <= params.recipient_plateau_ink_max)
    )
    dark_values = local_rgb[dark_mask]
    recipient_values = local_rgb[recipient_mask]
    if (
        len(dark_values) < params.minimum_plateau_samples_each
        or len(recipient_values) < params.minimum_plateau_samples_each
    ):
        return None
    dark = np.median(dark_values, axis=0)
    recipient = np.median(recipient_values, axis=0)
    axis = recipient - dark
    if float(np.dot(axis, axis)) < params.projection_denominator_min:
        return None
    if not np.all(np.isfinite(dark)) or not np.all(np.isfinite(recipient)):
        return None
    return dark, recipient


def _project_alpha_and_residual(
    rgb: np.ndarray,
    dark: np.ndarray,
    recipient: np.ndarray,
    denominator_min: float,
) -> tuple[np.ndarray, np.ndarray] | None:
    axis = recipient - dark
    denominator = float(np.dot(axis, axis))
    if denominator < denominator_min:
        return None
    alpha = ((rgb.astype(np.float64, copy=False) - dark) @ axis) / denominator
    alpha = np.clip(alpha, 0.0, 1.0)
    residual = rgb.astype(np.float64, copy=False) - (dark + alpha[:, None] * axis)
    return alpha, residual


def render_d3_r0(
    source_rgb: np.ndarray,
    native_masks: Mapping[str, np.ndarray],
    *,
    estimator_result: D3E0EstimatorResult | None = None,
    params: D3R0Params | None = None,
) -> tuple[np.ndarray, Mapping[str, object]]:
    """Render D3-R0 candidate RGB from source-fixed D3-E0 geometry.

    The return image is a new read-only float32 array.  If no patch is accepted
    by every renderer check, the corresponding pixels remain bit-exact copies
    of ``source_rgb``.
    """

    params = D3R0Params() if params is None else params
    params.validate()
    shape, masks = _validate_renderer_inputs(source_rgb, native_masks)
    if estimator_result is None:
        estimator_result = estimate_d3_e0(source_rgb, native_masks)
    if not isinstance(estimator_result, D3E0EstimatorResult):
        raise TypeError("D3-R0 estimator_result must be a D3E0EstimatorResult")
    if estimator_result.estimator_id != BOUND_ESTIMATOR_ID:
        raise ValueError("D3-R0 estimator_result is not from the bound E0 estimator")
    if estimator_result.accepted_support_mask.shape != shape:
        raise ValueError("D3-R0 estimator_result shape differs from source")

    hard = _hard_mask(masks)
    if np.any(estimator_result.accepted_support_mask & hard):
        raise ValueError("D3-R0 estimator_result support intersects hard mask")

    output = np.array(source_rgb, dtype=np.float64, order="C", copy=True)
    flat_source = source_rgb.reshape(-1, 3)
    flat_output = output.reshape(-1, 3)
    height = shape[0]
    scale = float(height) / 540.0
    low_width = params.low_dark_p10_to_p50_width_720px * scale
    high_width = params.high_recipient_p50_to_p90_width_720px * scale
    offsets = _subpixel_offsets(params.subsamples_per_axis)

    accepted = 0
    noop_reasons: dict[str, int] = {}
    modified_pixels: set[int] = set()

    for patch in estimator_result.local_patches:
        indices = np.asarray(patch.support_linear_indices, dtype=np.int64)
        if len(indices) == 0:
            noop_reasons["empty_support"] = noop_reasons.get("empty_support", 0) + 1
            continue
        if np.any(hard.reshape(-1)[indices]):
            noop_reasons["hard_mask"] = noop_reasons.get("hard_mask", 0) + 1
            continue
        if any(int(index) in modified_pixels for index in indices):
            noop_reasons["support_overlap"] = noop_reasons.get("support_overlap", 0) + 1
            continue
        plateaus = _patch_plateaus(
            source_rgb,
            masks["ink"],
            hard,
            patch.coordinates_xy,
            low_width,
            high_width,
            params,
        )
        if plateaus is None:
            noop_reasons["plateau_estimation"] = (
                noop_reasons.get("plateau_estimation", 0) + 1
            )
            continue
        dark, recipient = plateaus
        projected = _project_alpha_and_residual(
            flat_source[indices],
            dark,
            recipient,
            params.projection_denominator_min,
        )
        if projected is None:
            noop_reasons["projection"] = noop_reasons.get("projection", 0) + 1
            continue
        _, residual = projected
        yy, xx = np.divmod(indices, shape[1])
        sample_points = (
            np.column_stack((xx.astype(np.float64), yy.astype(np.float64)))[:, None, :]
            + offsets[None, :, :]
        ).reshape(-1, 2)
        try:
            signed = _signed_distance_to_polyline(sample_points, patch.coordinates_xy)
        except ValueError:
            noop_reasons["degenerate_patch"] = (
                noop_reasons.get("degenerate_patch", 0) + 1
            )
            continue
        alpha_samples = _alpha_from_signed_distance(signed, low_width, high_width)
        alpha_target = alpha_samples.reshape(len(indices), -1).mean(axis=1)
        candidate = dark + alpha_target[:, None] * (recipient - dark) + residual
        if not np.all(np.isfinite(candidate)):
            noop_reasons["nonfinite"] = noop_reasons.get("nonfinite", 0) + 1
            continue
        if np.any((candidate < -params.hard_rgb_epsilon) | (candidate > 1.0 + params.hard_rgb_epsilon)):
            noop_reasons["gamut"] = noop_reasons.get("gamut", 0) + 1
            continue
        flat_output[indices] = np.clip(candidate, 0.0, 1.0)
        modified_pixels.update(int(index) for index in indices)
        accepted += 1

    if np.any(output.reshape(-1, 3)[hard.reshape(-1)] != flat_source[hard.reshape(-1)]):
        raise RuntimeError("D3-R0 hard passthrough was not exact")

    result = np.asarray(output, dtype=np.float32)
    diagnostics = MappingProxyType({
        "renderer_id": RENDERER_ID,
        "bound_estimator_id": BOUND_ESTIMATOR_ID,
        "native_shape_hw": tuple(int(value) for value in shape),
        "native_width_scale_from_540": scale,
        "input_patch_count": len(estimator_result.local_patches),
        "accepted_patch_count": accepted,
        "noop_patch_count": len(estimator_result.local_patches) - accepted,
        "noop_reasons": MappingProxyType(dict(sorted(noop_reasons.items()))),
        "modified_pixel_count": len(modified_pixels),
        "real_images_opened": 0,
        "candidate_output_dependent_geometry": False,
    })
    return _readonly(result), diagnostics


__all__ = [
    "BOUND_ESTIMATOR_ID",
    "D3R0Params",
    "FROZEN_PARAMETER_VALUES",
    "RENDERER_ID",
    "render_d3_r0",
]
