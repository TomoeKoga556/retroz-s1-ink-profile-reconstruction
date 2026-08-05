#!/usr/bin/env python3
"""Pure-array clean-room runtime for historical S1 Candidate B v2 (MLSR).

The optical map and active parameter set reproduce the manifest-pinned
historical ``candidate_b_mlsr.py``.  A separate audit records that its imported
helper bytes were not closed by the historical package manifest.  The only
integration refactor is that the seven canonical source-derived M0 masks are
supplied as immutable arrays by the caller instead of being reconstructed
through project imports.

This module performs no file, network, environment, process, or global-state
I/O.  Import defines constants, types, and functions only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np


CANDIDATE_ID = "cursor_s1_candidate_b_mlsr_recipe"
CANDIDATE_FAMILY = "B"
FAMILY_NAME = "mlsr_monotone_local_shoulder_reconstruction"
STAGE = "post_e8b_native"
EXTERNAL_IO = False
SIDE_EFFECTS = False
TRANSITIVE_CANDIDATE_SOURCES = ("candidate_b_runtime.py",)

_LUMA_WEIGHTS = (0.2126, 0.7152, 0.0722)
_FAMILIES = (
    "ink",
    "neutral",
    "skin",
    "red_orange",
    "yellow",
    "green",
    "cyan",
    "blue",
    "purple",
)
_SQRT_HALF = 0.7071067811865476
_AXES = (
    (1.0, 0.0),
    (0.0, 1.0),
    (_SQRT_HALF, _SQRT_HALF),
    (_SQRT_HALF, -_SQRT_HALF),
)
_NATIVE_MASK_NAMES = (
    "flat",
    "ink",
    "ink_recipient",
    "fx",
    "background",
    "local_min_luma",
    "local_max_luma",
)
_FROZEN_FLOAT_FIELDS = (
    ("shoulder_factor", 1.30),
    ("mix", 1.0),
    ("gradient_radius_at_720p", 1.0),
    ("tensor_radius_at_720p", 0.75),
    ("support_radius_at_720p", 2.0),
    ("plateau_radius_at_720p", 1.25),
    ("fx_expand_radius_at_720p", 0.75),
    ("skin_context_radius_at_720p", 1.5),
    ("orientation_power", 4.0),
    ("recipient_weight", 0.45),
    ("line_gate_low", 0.06),
    ("line_gate_high", 0.45),
    ("edge_range_low", 0.03),
    ("edge_range_high", 0.12),
    ("shoulder_inner", 0.10),
    ("shoulder_outer", 0.42),
    ("core_protect_halfwidth", 0.08),
    ("core_protect_floor", 0.15),
    ("coherence_low", 0.35),
    ("coherence_high", 0.70),
    ("support_low", 0.08),
    ("support_high", 0.30),
    ("protected_width_low_at_720p", 1.20),
    ("protected_width_high_at_720p", 1.80),
    ("skin_context_low", 0.30),
    ("skin_context_high", 0.65),
    ("protected_detail_hard_min", 0.80),
    ("fx_gate_low", 0.10),
    ("fx_gate_high", 0.55),
    ("flat_gate_low", 0.20),
    ("flat_gate_high", 0.72),
    ("background_gate_low", 0.45),
    ("background_gate_high", 0.82),
    ("black_protect_luma", 0.125),
)
_RECIPE_KEYS = (
    "schema_version",
    "artifact",
    "status",
    "candidate_id",
    "candidate_family",
    "stage",
    "parameters",
    "historical_binding",
    "alternate_parameter_sets",
    "strength_search_allowed",
)
_HISTORICAL_BINDING = (
    ("historical_package", "cursor_s1_candidate_b_2026-07-18_v2"),
    (
        "historical_candidate_runtime_sha256",
        "64fa65c2f7796bb353a54cf31db183d88bf3fd08c43c561320fc3d2882facefa",
    ),
    (
        "historical_package_sha256",
        "4f4590c0b6b2ec7bdfe19a332b0e5655f36a9383f65af6bc58f7fda67c295d1d",
    ),
    (
        "historical_m0_profile_sha256",
        "97c90f6e61e8305e79bcbbe943f368eaeb78cff0dc9f982beadfb8af13963e31",
    ),
    ("operation_family", FAMILY_NAME),
)


@dataclass(frozen=True)
class CandidateBParams:
    """Exactly one historical optical parameter set plus a test-only switch."""

    enabled: bool
    shoulder_factor: float
    mix: float
    gradient_radius_at_720p: float
    tensor_radius_at_720p: float
    support_radius_at_720p: float
    plateau_radius_at_720p: float
    fx_expand_radius_at_720p: float
    skin_context_radius_at_720p: float
    orientation_power: float
    recipient_weight: float
    line_gate_low: float
    line_gate_high: float
    edge_range_low: float
    edge_range_high: float
    shoulder_inner: float
    shoulder_outer: float
    core_protect_halfwidth: float
    core_protect_floor: float
    coherence_low: float
    coherence_high: float
    support_low: float
    support_high: float
    protected_width_low_at_720p: float
    protected_width_high_at_720p: float
    skin_context_low: float
    skin_context_high: float
    protected_detail_hard_min: float
    fx_gate_low: float
    fx_gate_high: float
    flat_gate_low: float
    flat_gate_high: float
    background_gate_low: float
    background_gate_high: float
    black_protect_luma: float

    def __post_init__(self) -> None:
        _validate_params_instance(self)


def _validate_params_instance(params: CandidateBParams) -> None:
    """Close direct-constructor and ``object.__setattr__`` bypasses."""

    if type(params) is not CandidateBParams:
        raise TypeError("params must be an exact CandidateBParams instance")
    if type(params.enabled) is not bool:
        raise TypeError("CandidateBParams.enabled must be an exact bool")
    for name, expected in _FROZEN_FLOAT_FIELDS:
        actual = getattr(params, name)
        if type(actual) is not float:
            raise TypeError(f"CandidateBParams.{name} must be an exact float")
        if not np.isfinite(actual):
            raise ValueError(f"CandidateBParams.{name} must be finite")
        if actual != expected:
            raise ValueError(f"CandidateBParams.{name} differs from historical v2")


def _require_exact_keys(
    value: object,
    expected_names: tuple[str, ...],
    context: str,
) -> dict[str, Any]:
    if type(value) is not dict:
        raise TypeError(f"{context} must be an exact built-in dict")
    result = value
    actual = set(result)
    expected = set(expected_names)
    if actual != expected:
        raise ValueError(
            f"{context} fields differ; "
            f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
        )
    return result


def params_from_dict(values: object) -> CandidateBParams:
    """Reject omissions, extras, coercions, NaN/Inf, and parameter drift."""

    names = ("enabled",) + tuple(name for name, _ in _FROZEN_FLOAT_FIELDS)
    document = _require_exact_keys(values, names, "Candidate B parameters")
    if type(document["enabled"]) is not bool:
        raise TypeError("Candidate B parameters.enabled must be an exact bool")
    resolved: dict[str, float] = {}
    for name, expected in _FROZEN_FLOAT_FIELDS:
        actual = document[name]
        if type(actual) is not float:
            raise TypeError(f"Candidate B parameters.{name} must be an exact float")
        if not np.isfinite(actual):
            raise ValueError(f"Candidate B parameters.{name} must be finite")
        if actual != expected:
            raise ValueError(
                f"Candidate B parameters.{name} differs from historical v2"
            )
        resolved[name] = actual
    return CandidateBParams(enabled=document["enabled"], **resolved)


def recipe_parameters(recipe: object) -> CandidateBParams:
    """Validate the complete finite, single-set recipe without reading a file."""

    document = _require_exact_keys(recipe, _RECIPE_KEYS, "Candidate B recipe")
    fixed_scalars = (
        ("schema_version", 1),
        ("artifact", "candidate_b_cleanroom_recipe"),
        ("status", "historical_v2_formula_fixed_no_search"),
        ("candidate_id", CANDIDATE_ID),
        ("candidate_family", CANDIDATE_FAMILY),
        ("stage", STAGE),
        ("strength_search_allowed", False),
    )
    for name, expected in fixed_scalars:
        actual = document[name]
        if type(actual) is not type(expected):
            raise TypeError(f"Candidate B recipe.{name} has the wrong exact type")
        if actual != expected:
            raise ValueError(f"Candidate B recipe.{name} mismatch")
    alternatives = document["alternate_parameter_sets"]
    if type(alternatives) is not list:
        raise TypeError(
            "Candidate B recipe.alternate_parameter_sets must be an exact list"
        )
    if alternatives:
        raise ValueError("Candidate B recipe contains an alternate parameter set")
    binding_names = tuple(name for name, _ in _HISTORICAL_BINDING)
    binding = _require_exact_keys(
        document["historical_binding"],
        binding_names,
        "Candidate B recipe.historical_binding",
    )
    for name, expected in _HISTORICAL_BINDING:
        actual = binding[name]
        if type(actual) is not str:
            raise TypeError(
                f"Candidate B recipe.historical_binding.{name} must be a string"
            )
        if actual != expected:
            raise ValueError(
                f"Candidate B recipe.historical_binding.{name} mismatch"
            )
    return params_from_dict(document["parameters"])


def architecture_contract() -> dict[str, Any]:
    """Return finite plain metadata; no parameter object is built at import."""

    return {
        "schema_version": 1,
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "family_name": FAMILY_NAME,
        "stage": STAGE,
        "classification_input": "immutable original source RGB and canonical M0 masks",
        "radiometric_input": "frozen E8B RGB",
        "operation": (
            "z'=tanh(atanh(z)/1.30), Hermite-blended only in historical "
            "source-locked shoulder lobes"
        ),
        "external_io": EXTERNAL_IO,
        "side_effects": SIDE_EFFECTS,
        "input_mutation": False,
        "output_shape_equals_input": True,
        "source_fixed_masks": True,
        "hard_mask_role": "candidate_diagnostic_only",
        "transitive_candidate_sources": list(TRANSITIVE_CANDIDATE_SOURCES),
    }


def _luma_weights() -> np.ndarray:
    return np.asarray(_LUMA_WEIGHTS, dtype=np.float32)


def _smoothstep(edge0: float, edge1: float, values: np.ndarray) -> np.ndarray:
    position = np.clip((values - edge0) / max(edge1 - edge0, 1e-7), 0, 1)
    return position * position * (3 - 2 * position)


def _family_smoothstep(
    edge0: float,
    edge1: float,
    values: np.ndarray,
) -> np.ndarray:
    position = np.clip((values - edge0) / max(edge1 - edge0, 1e-6), 0, 1)
    return position * position * (3 - 2 * position)


def _spatial_scale(values: np.ndarray) -> float:
    return float(np.clip(float(values.shape[0]) / 720.0, 0.5, 3.0))


def _native_shift(
    values: np.ndarray,
    dx: float = 0.0,
    dy: float = 0.0,
) -> np.ndarray:
    result = values
    if abs(dx) > 1e-7:
        width = result.shape[1]
        coordinates = np.arange(width, dtype=np.float32) + float(dx)
        lower = np.floor(coordinates).astype(np.int64)
        fraction = coordinates - lower
        upper = lower + 1
        lower = np.clip(lower, 0, width - 1)
        upper = np.clip(upper, 0, width - 1)
        weight_shape = (1, width) + (1,) * (result.ndim - 2)
        weight = fraction.reshape(weight_shape)
        result = result[:, lower] * (1 - weight) + result[:, upper] * weight
    if abs(dy) > 1e-7:
        height = result.shape[0]
        coordinates = np.arange(height, dtype=np.float32) + float(dy)
        lower = np.floor(coordinates).astype(np.int64)
        fraction = coordinates - lower
        upper = lower + 1
        lower = np.clip(lower, 0, height - 1)
        upper = np.clip(upper, 0, height - 1)
        weight_shape = (height, 1) + (1,) * (result.ndim - 2)
        weight = fraction.reshape(weight_shape)
        result = result[lower] * (1 - weight) + result[upper] * weight
    return np.asarray(result, dtype=np.float32)


def _rgb_to_hsv_flat(
    rgb: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    flat = np.asarray(rgb, dtype=np.float32).reshape(-1, 3)
    maximum, minimum = flat.max(axis=1), flat.min(axis=1)
    delta = maximum - minimum
    saturation = np.divide(
        delta,
        maximum,
        out=np.zeros_like(maximum),
        where=maximum > 1e-8,
    )
    hue = np.zeros_like(maximum)
    mask = delta > 1e-8
    red, green, blue = [
        (maximum == flat[:, index]) & mask for index in range(3)
    ]
    hue[red] = ((flat[:, 1][red] - flat[:, 2][red]) / delta[red]) % 6
    hue[green] = (flat[:, 2][green] - flat[:, 0][green]) / delta[green] + 2
    hue[blue] = (flat[:, 0][blue] - flat[:, 1][blue]) / delta[blue] + 4
    return hue / 6, saturation, maximum


def _family_weights(rgb: np.ndarray) -> np.ndarray:
    flat = np.asarray(rgb, dtype=np.float32).reshape(-1, 3)
    hue, saturation, _ = _rgb_to_hsv_flat(flat)
    luma = flat @ _luma_weights()
    ink = 1 - _family_smoothstep(0.075, 0.18, luma)
    neutral_gate = 1 - _family_smoothstep(0.075, 0.235, saturation)
    neutral = neutral_gate * (1 - ink)
    chromatic = np.clip(1 - ink - neutral, 0, 1)

    def circular(distance_center: float, sigma: float) -> np.ndarray:
        distance = np.abs((hue - distance_center + 0.5) % 1 - 0.5)
        return np.exp(-0.5 * (distance / sigma) ** 2)

    skin = (
        circular(0.065, 0.058)
        * _family_smoothstep(0.10, 0.22, saturation)
        * (1 - _family_smoothstep(0.56, 0.74, saturation))
        * _family_smoothstep(0.18, 0.34, luma)
        * 1.30
    )
    chroma_raw = np.stack(
        (
            skin,
            circular(0.035, 0.075),
            circular(0.17, 0.070),
            circular(0.35, 0.115),
            circular(0.51, 0.075),
            circular(0.63, 0.090),
            circular(0.82, 0.120),
        ),
        axis=1,
    )
    chroma_raw /= np.maximum(chroma_raw.sum(axis=1, keepdims=True), 1e-7)
    weights = np.zeros((len(flat), len(_FAMILIES)), dtype=np.float32)
    weights[:, 0] = ink
    weights[:, 1] = neutral
    weights[:, 2:] = chroma_raw * chromatic[:, None]
    return weights


def shoulder_weight_scalar(
    t: np.ndarray,
    *,
    shoulder_inner: float = 0.10,
    shoulder_outer: float = 0.42,
    core_protect_halfwidth: float = 0.08,
    core_protect_floor: float = 0.15,
) -> np.ndarray:
    t = np.asarray(t, dtype=np.float64)
    dark = _smoothstep(shoulder_inner, shoulder_inner + 0.06, t) * (
        1.0 - _smoothstep(shoulder_outer - 0.06, shoulder_outer, t)
    )
    bright = _smoothstep(shoulder_inner, shoulder_inner + 0.06, 1.0 - t) * (
        1.0
        - _smoothstep(shoulder_outer - 0.06, shoulder_outer, 1.0 - t)
    )
    lobe = np.maximum(dark, bright)
    dist_mid = np.abs(t - 0.5)
    core = 1.0 - _smoothstep(
        float(core_protect_halfwidth),
        float(core_protect_halfwidth) + 0.06,
        dist_mid,
    )
    floor = float(core_protect_floor)
    protect = floor + (1.0 - floor) * (1.0 - core)
    return np.clip(lobe * protect, 0.0, 1.0).astype(np.float64)


def odd_shoulder_soften_z(
    z: np.ndarray,
    shoulder_factor: float,
) -> np.ndarray:
    z = np.asarray(z, dtype=np.float64)
    s = float(shoulder_factor)
    if abs(s - 1.0) < 1e-15:
        return z.copy()
    eps = 1e-7
    zc = np.clip(z, -1.0 + eps, 1.0 - eps)
    soft = np.tanh(np.arctanh(zc) / s)
    out = soft.copy()
    out = np.where(z <= -1.0 + eps, -1.0, out)
    out = np.where(z >= 1.0 - eps, 1.0, out)
    return out


def mlsr_soften_scalar(
    t: np.ndarray,
    shoulder_factor: float,
    *,
    shoulder_inner: float = 0.10,
    shoulder_outer: float = 0.42,
    core_protect_halfwidth: float = 0.08,
    core_protect_floor: float = 0.15,
) -> np.ndarray:
    t = np.asarray(t, dtype=np.float64)
    if abs(float(shoulder_factor) - 1.0) < 1e-15:
        return t.astype(np.float64)
    tc = np.clip(t, 0.0, 1.0)
    z = 2.0 * tc - 1.0
    z_soft = odd_shoulder_soften_z(z, shoulder_factor)
    t_soft = 0.5 * (z_soft + 1.0)
    weight = shoulder_weight_scalar(
        tc,
        shoulder_inner=shoulder_inner,
        shoulder_outer=shoulder_outer,
        core_protect_halfwidth=core_protect_halfwidth,
        core_protect_floor=core_protect_floor,
    )
    out = (1.0 - weight) * tc + weight * t_soft
    out = np.clip(out, 0.0, 1.0)
    out = np.where(t <= 0.0, 0.0, out)
    out = np.where(t >= 1.0, 1.0, out)
    return out


def mlsr_soften_profile(
    esf: np.ndarray,
    shoulder_factor: float,
    *,
    idark: float | None = None,
    ibright: float | None = None,
    shoulder_inner: float = 0.10,
    shoulder_outer: float = 0.42,
    core_protect_halfwidth: float = 0.08,
    core_protect_floor: float = 0.15,
) -> np.ndarray:
    y = np.asarray(esf, dtype=np.float64)
    if abs(float(shoulder_factor) - 1.0) < 1e-15:
        return y.copy()
    if idark is None:
        idark = float(np.median(y[: max(3, len(y) // 5)]))
    if ibright is None:
        ibright = float(np.median(y[-max(3, len(y) // 5) :]))
    span = max(ibright - idark, 1e-12)
    t = np.clip((y - idark) / span, 0.0, 1.0)
    tp = mlsr_soften_scalar(
        t,
        shoulder_factor,
        shoulder_inner=shoulder_inner,
        shoulder_outer=shoulder_outer,
        core_protect_halfwidth=core_protect_halfwidth,
        core_protect_floor=core_protect_floor,
    )
    return idark + tp * span


def _axis_pairs(
    values: np.ndarray,
    radius: float,
) -> tuple[tuple[np.ndarray, np.ndarray], ...]:
    return tuple(
        (
            _native_shift(values, dx=radius * dx, dy=radius * dy),
            _native_shift(values, dx=-radius * dx, dy=-radius * dy),
        )
        for dx, dy in _AXES
    )


def _eight_tap_mean(values: np.ndarray, radius: float) -> np.ndarray:
    total = np.asarray(values, dtype=np.float32)
    for positive, negative in _axis_pairs(values, radius):
        total = total + positive + negative
    return np.asarray(total / 9.0, dtype=np.float32)


def _eight_tap_max(values: np.ndarray, radius: float) -> np.ndarray:
    samples: list[np.ndarray] = [np.asarray(values, dtype=np.float32)]
    for positive, negative in _axis_pairs(values, radius):
        samples.extend((positive, negative))
    return np.asarray(np.maximum.reduce(samples), dtype=np.float32)


def _validate_rgb_inputs(
    e8b_rgb: np.ndarray,
    source_rgb: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    if type(e8b_rgb) is not np.ndarray or type(source_rgb) is not np.ndarray:
        raise TypeError("Candidate B RGB inputs must be exact numpy.ndarray objects")
    if e8b_rgb.dtype != np.float32 or source_rgb.dtype != np.float32:
        raise TypeError("Candidate B requires float32 RGB inputs")
    if (
        e8b_rgb.shape != source_rgb.shape
        or e8b_rgb.ndim != 3
        or e8b_rgb.shape[2] != 3
        or e8b_rgb.shape[0] <= 0
        or e8b_rgb.shape[1] <= 0
    ):
        raise ValueError("e8b_rgb and source_rgb must be matching nonempty HxWx3")
    if not np.all(np.isfinite(e8b_rgb)) or not np.all(np.isfinite(source_rgb)):
        raise ValueError("Candidate B RGB inputs must be finite")
    minimum = min(float(e8b_rgb.min()), float(source_rgb.min()))
    maximum = max(float(e8b_rgb.max()), float(source_rgb.max()))
    if minimum < -1e-6 or maximum > 1.0 + 1e-6:
        raise ValueError("Candidate B RGB inputs must be in [0, 1]")
    return e8b_rgb, source_rgb


def _validated_native_masks(
    native_masks: Mapping[str, np.ndarray],
    shape: tuple[int, int],
) -> dict[str, np.ndarray]:
    if not isinstance(native_masks, Mapping):
        raise TypeError("native_masks must be a mapping")
    actual = set(native_masks)
    expected = set(_NATIVE_MASK_NAMES)
    if actual != expected:
        raise ValueError(
            "native_masks fields differ; "
            f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
        )
    result: dict[str, np.ndarray] = {}
    for name in _NATIVE_MASK_NAMES:
        values = native_masks[name]
        if type(values) is not np.ndarray:
            raise TypeError(f"native_masks[{name!r}] must be an exact numpy.ndarray")
        if values.dtype != np.float32:
            raise TypeError(f"native_masks[{name!r}] must have dtype float32")
        if values.shape != shape:
            raise ValueError(
                f"native_masks[{name!r}] shape {values.shape} differs from {shape}"
            )
        if not np.all(np.isfinite(values)):
            raise ValueError(f"native_masks[{name!r}] contains NaN or Inf")
        if np.any((values < 0.0) | (values > 1.0)):
            raise ValueError(f"native_masks[{name!r}] must remain in [0, 1]")
        result[name] = values
    return result


def _compose_gamut_safe_luma_chroma(
    target_luma: np.ndarray,
    chroma: np.ndarray,
) -> np.ndarray:
    positive_limit = np.divide(
        (1 - target_luma)[..., None],
        np.maximum(chroma, 1e-9),
        out=np.full_like(chroma, np.inf),
        where=chroma > 0,
    )
    negative_limit = np.divide(
        target_luma[..., None],
        np.maximum(-chroma, 1e-9),
        out=np.full_like(chroma, np.inf),
        where=chroma < 0,
    )
    scale = np.minimum(
        1,
        np.minimum(positive_limit, negative_limit).min(axis=2),
    )
    return np.asarray(
        target_luma[..., None] + chroma * scale[..., None],
        dtype=np.float32,
    )


def _mlsr_masks(
    source_rgb: np.ndarray,
    e8b_rgb: np.ndarray,
    native_masks: Mapping[str, np.ndarray],
    params: CandidateBParams,
) -> dict[str, np.ndarray]:
    e8b, source = _validate_rgb_inputs(e8b_rgb, source_rgb)
    base = _validated_native_masks(native_masks, source.shape[:2])
    source_luma = np.asarray(source @ _luma_weights(), np.float32)
    scale = float(_spatial_scale(source))

    gradient_radius = float(params.gradient_radius_at_720p * scale)
    gx = (
        _native_shift(source_luma, dx=gradient_radius)
        - _native_shift(source_luma, dx=-gradient_radius)
    ) / max(2 * gradient_radius, 1e-7)
    gy = (
        _native_shift(source_luma, dy=gradient_radius)
        - _native_shift(source_luma, dy=-gradient_radius)
    ) / max(2 * gradient_radius, 1e-7)
    gradient = np.sqrt(gx * gx + gy * gy)

    local_min = np.asarray(base["local_min_luma"], np.float32)
    local_max = np.asarray(base["local_max_luma"], np.float32)
    plateau_radius = float(params.plateau_radius_at_720p * scale)
    local_min = np.minimum(
        local_min,
        _eight_tap_mean(local_min, plateau_radius),
    )
    local_max = np.maximum(
        local_max,
        _eight_tap_mean(local_max, plateau_radius),
    )
    local_range = np.maximum(local_max - local_min, 0.0)

    edge_confidence = _smoothstep(
        params.edge_range_low,
        params.edge_range_high,
        local_range,
    )
    source_position = np.divide(
        source_luma - local_min,
        np.maximum(local_range, 1e-7),
    )
    source_position = np.clip(source_position, 0, 1).astype(np.float32)

    lobe = shoulder_weight_scalar(
        source_position,
        shoulder_inner=params.shoulder_inner,
        shoulder_outer=params.shoulder_outer,
        core_protect_halfwidth=params.core_protect_halfwidth,
        core_protect_floor=params.core_protect_floor,
    ).astype(np.float32)
    half_split = _smoothstep(0.46, 0.54, source_position)
    low_half_support = lobe * (1.0 - half_split)
    high_half_support = lobe * half_split

    tensor_radius = float(params.tensor_radius_at_720p * scale)
    jxx = _eight_tap_mean(gx * gx, tensor_radius)
    jxy = _eight_tap_mean(gx * gy, tensor_radius)
    jyy = _eight_tap_mean(gy * gy, tensor_radius)
    tensor_trace = jxx + jyy
    coherence_raw = np.divide(
        np.sqrt((jxx - jyy) ** 2 + 4 * jxy * jxy),
        np.maximum(tensor_trace, 1e-9),
    )
    coherence = _smoothstep(
        params.coherence_low,
        params.coherence_high,
        coherence_raw,
    )

    line_raw = np.maximum(
        base["ink"],
        params.recipient_weight * base["ink_recipient"],
    )
    line = _smoothstep(params.line_gate_low, params.line_gate_high, line_raw)
    support_pairs = _axis_pairs(
        line,
        float(params.support_radius_at_720p * scale),
    )
    support_raw = np.maximum.reduce(
        [(positive + negative) * 0.5 for positive, negative in support_pairs]
    )
    support = _smoothstep(params.support_low, params.support_high, support_raw)

    width_at_720p = np.divide(
        local_range,
        np.maximum(2 * gradient, 1e-5),
    ) / max(scale, 1e-7)
    width_at_720p = np.clip(width_at_720p, 0, 12).astype(np.float32)
    narrow_edge = (
        1.0
        - _smoothstep(
            params.protected_width_low_at_720p,
            params.protected_width_high_at_720p,
            width_at_720p,
        )
    ) * edge_confidence

    source_family = _family_weights(source).reshape(
        source.shape[0],
        source.shape[1],
        len(_FAMILIES),
    )
    skin = source_family[..., _FAMILIES.index("skin")]
    skin_context = _eight_tap_max(
        skin,
        float(params.skin_context_radius_at_720p * scale),
    )
    face_detail = (
        _smoothstep(
            params.skin_context_low,
            params.skin_context_high,
            skin_context,
        )
        * _eight_tap_max(narrow_edge, tensor_radius)
    )

    fx_expanded = _eight_tap_max(
        base["fx"],
        float(params.fx_expand_radius_at_720p * scale),
    )
    fx_guard = _smoothstep(params.fx_gate_low, params.fx_gate_high, fx_expanded)
    flat_guard = _smoothstep(
        params.flat_gate_low,
        params.flat_gate_high,
        base["flat"],
    )
    background_guard = _smoothstep(
        params.background_gate_low,
        params.background_gate_high,
        base["background"],
    )
    hard_detail = (
        (coherence_raw <= params.coherence_low)
        | (support_raw <= params.support_low)
        | (face_detail >= params.protected_detail_hard_min)
    )
    plateau = (source_position <= params.shoulder_inner * 0.5) | (
        source_position >= 1.0 - params.shoulder_inner * 0.5
    )
    insufficient = local_range < params.edge_range_low
    hard_protection = (
        (source_luma <= params.black_protect_luma)
        | (fx_expanded >= params.fx_gate_high)
        | (base["flat"] >= params.flat_gate_high)
        | (base["background"] >= params.background_gate_high)
        | hard_detail
        | plateau
        | insufficient
    )
    soft_safety = (
        (1.0 - fx_guard)
        * (1.0 - flat_guard)
        * (1.0 - background_guard)
        * (1.0 - face_detail)
        * (~hard_protection).astype(np.float32)
    )
    action = np.clip(
        lobe
        * line
        * edge_confidence
        * coherence
        * support
        * soft_safety
        * float(params.mix),
        0.0,
        1.0,
    ).astype(np.float32)

    return {
        "local_min_luma": local_min.astype(np.float32),
        "local_max_luma": local_max.astype(np.float32),
        "source_position": source_position,
        "shoulder_lobe": lobe.astype(np.float32),
        "low_half_support": np.asarray(low_half_support, np.float32),
        "high_half_support": np.asarray(high_half_support, np.float32),
        "mlsr_action": action,
        "hard_protection": hard_protection.astype(np.float32),
        "edge_confidence": np.asarray(edge_confidence, np.float32),
    }


def apply_candidate_b(
    e8b_rgb: np.ndarray,
    source_rgb: np.ndarray,
    native_masks: Mapping[str, np.ndarray],
    params: CandidateBParams,
    *,
    return_diagnostics: bool = False,
) -> np.ndarray | tuple[np.ndarray, dict[str, np.ndarray]]:
    """Apply the historical MLSR v2 pixel map at unchanged native shape."""

    _validate_params_instance(params)
    if type(return_diagnostics) is not bool:
        raise TypeError("return_diagnostics must be an exact bool")
    e8b, source = _validate_rgb_inputs(e8b_rgb, source_rgb)
    diagnostics = _mlsr_masks(source, e8b, native_masks, params)
    if not params.enabled:
        output = e8b.copy()
        diagnostics["luma_delta"] = np.zeros(e8b.shape[:2], dtype=np.float32)
        return (output, diagnostics) if return_diagnostics else output

    luma = np.asarray(e8b @ _luma_weights(), np.float32)
    chroma = np.asarray(e8b - luma[..., None], np.float32)
    idark = diagnostics["local_min_luma"]
    ibright = diagnostics["local_max_luma"]
    span = np.maximum(ibright - idark, 1e-7)
    t = np.clip((luma - idark) / span, 0.0, 1.0)
    tp = mlsr_soften_scalar(
        t,
        params.shoulder_factor,
        shoulder_inner=params.shoulder_inner,
        shoulder_outer=params.shoulder_outer,
        core_protect_halfwidth=params.core_protect_halfwidth,
        core_protect_floor=params.core_protect_floor,
    ).astype(np.float32)
    softened = idark + tp * span
    action = diagnostics["mlsr_action"]
    hard = diagnostics["hard_protection"] >= 0.5
    inactive = action <= 0
    target_luma = luma * (1.0 - action) + softened * action
    target_luma = np.asarray(target_luma, np.float32)
    output = _compose_gamut_safe_luma_chroma(target_luma, chroma)
    output[hard | inactive] = e8b[hard | inactive]
    output = np.clip(output, 0, 1).astype(np.float32)
    if output.shape != e8b.shape:
        raise RuntimeError("Candidate B changed native frame dimensions")
    if not np.all(np.isfinite(output)):
        raise RuntimeError("Candidate B produced non-finite RGB values")
    diagnostics["luma_delta"] = np.asarray(
        output @ _luma_weights() - luma,
        np.float32,
    )
    return (output, diagnostics) if return_diagnostics else output
