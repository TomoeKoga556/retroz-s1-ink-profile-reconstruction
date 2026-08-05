"""D3-E0 source-only continuous contour estimator.

This module implements only the estimator frozen by
``D3_E0_PREREGISTRATION.json``.  It has no renderer and produces no RGB.
Numerical geometry comes exclusively from the native M0 ``ink`` confidence;
``source_rgb`` is validated and used only to bind native shape.  The other M0
maps are used only for the preregistered independent hard protections.

Implementation choices which are not scientific tuning parameters are fixed
here before the binding synthetic suite:

* native scale is ``height / 720.0``;
* Marching-Squares vertices are keyed by their native grid edge, so adjacent
  cells share vertices without tolerance-based welding;
* cases 5/10 and any cell containing an isovalue tie are unsafe and emit no
  segment;
* only closed degree-two graph components can reach patch certification;
* separation, frame, ambiguity, and hard-seed safety are evaluated directly
  on the emitted finite contour segments; nonlocal self-distance is minimized
  exactly inside the allowed cyclic-arclength bands;
* support masks use exact point-to-segment distance at native pixel centres.
* ordered contour ``left`` is visual/image-space left: for a tangent
  ``(dx, dy)`` on the native grid where y grows downward, its left normal is
  exactly ``(dy, -dx)``.

Forbidden D/D2 mechanisms (thinning, skeletons, ridges, centerline pairing,
paired midpoints, signed-distance warps, point warps, RGB-dependent geometry,
or candidate-output-dependent geometry) are deliberately absent.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from types import MappingProxyType
from typing import Iterable, Mapping, Sequence

import numpy as np


ESTIMATOR_ID = "s1_candidate_d3_e0_contour_estimator_v2"


@dataclass(frozen=True)
class D3E0Params:
    """Exact estimator parameters bound by the D3-E0 preregistration."""

    ink_iso: float = 0.50
    exact_vertex_tie_abs_tolerance: float = 1e-7
    fx_hard_min: float = 0.55
    background_hard_min: float = 0.82
    flat_hard_min: float = 0.72
    support_radius_720px: float = 2.25
    hard_footprint_margin_720px: float = 0.75
    minimum_opposite_contour_separation_720px: float = 4.55
    different_component_separation_guard_720px: float = 8.0
    ambiguity_guard_720px: float = 3.0
    frame_guard_720px: float = 7.0
    curvature_measurement_half_window_720px: float = 2.5
    minimum_safe_curvature_radius_720px: float = 12.0
    sharp_concave_component_reject_radius_720px: float = 8.0
    nonlocal_self_arc_exclusion_720px: float = 6.0
    minimum_closed_contour_length_720px: float = 64.0
    minimum_safe_run_length_720px: float = 24.0
    patch_endpoint_guard_720px: float = 4.0
    minimum_active_patch_arc_length_720px: float = 16.0
    polarity_probe_720px: float = 0.25
    polarity_minimum_delta: float = 1e-4

    def validate(self) -> None:
        if type(self) is not D3E0Params:
            raise TypeError("D3-E0 params must use the exact D3E0Params type")
        actual = asdict(self)
        if set(actual) != set(FROZEN_PARAMETER_VALUES):
            raise ValueError("D3-E0 parameter schema differs from preregistration")
        for name, expected in FROZEN_PARAMETER_VALUES.items():
            value = actual[name]
            if isinstance(value, (bool, np.bool_)) or not isinstance(
                value, (int, float, np.integer, np.floating)
            ):
                raise TypeError(f"D3-E0 parameter {name!r} must be real numeric")
            if type(value) is not type(expected):
                raise TypeError(
                    f"D3-E0 parameter {name!r} has a non-preregistered type"
                )
            if not math.isfinite(float(value)):
                raise ValueError(f"D3-E0 parameter {name!r} must be finite")
            if value != expected:
                raise ValueError(
                    f"D3-E0 parameter drift: {name}={value!r}, "
                    f"preregistered={expected!r}"
                )


FROZEN_PARAMETER_VALUES: Mapping[str, float] = MappingProxyType({
    "ink_iso": 0.50,
    "exact_vertex_tie_abs_tolerance": 1e-7,
    "fx_hard_min": 0.55,
    "background_hard_min": 0.82,
    "flat_hard_min": 0.72,
    "support_radius_720px": 2.25,
    "hard_footprint_margin_720px": 0.75,
    "minimum_opposite_contour_separation_720px": 4.55,
    "different_component_separation_guard_720px": 8.0,
    "ambiguity_guard_720px": 3.0,
    "frame_guard_720px": 7.0,
    "curvature_measurement_half_window_720px": 2.5,
    "minimum_safe_curvature_radius_720px": 12.0,
    "sharp_concave_component_reject_radius_720px": 8.0,
    "nonlocal_self_arc_exclusion_720px": 6.0,
    "minimum_closed_contour_length_720px": 64.0,
    "minimum_safe_run_length_720px": 24.0,
    "patch_endpoint_guard_720px": 4.0,
    "minimum_active_patch_arc_length_720px": 16.0,
    "polarity_probe_720px": 0.25,
    "polarity_minimum_delta": 1e-4,
})


@dataclass(frozen=True)
class D3E0ContourComponent:
    """One accepted, polarity-oriented, closed contour component.

    ``ink_greater_is_left`` uses visual/image-space left ``(dy, -dx)`` for
    the ordered coordinate sequence; native y increases downward.
    """

    geometry_sha256: str
    coordinates_xy: np.ndarray
    total_arclength_native_px: float
    signed_area_native_px2: float
    polarity_median_delta: float
    ink_greater_is_left: bool
    accepted_patch_count: int


@dataclass(frozen=True)
class D3E0LocalPatch:
    """One maximal safe arc after the preregistered endpoint trimming.

    Its ordering inherits the component's visual/image-space left convention.
    """

    component_geometry_sha256: str
    patch_geometry_sha256: str
    start_arclength_native_px: float
    end_arclength_native_px: float
    arclength_native_px: float
    coordinates_xy: np.ndarray
    support_linear_indices: np.ndarray
    ink_greater_is_left: bool


@dataclass(frozen=True)
class D3E0RejectedComponent:
    """Deterministic summary of an extracted component that failed closed."""

    provisional_sha256: str
    graph_vertex_count: int
    graph_edge_count: int
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class D3E0EstimatorResult:
    """Geometry-only result.  No field is or contains an RGB output."""

    estimator_id: str
    native_scale_from_720: float
    contour_components: tuple[D3E0ContourComponent, ...]
    local_patches: tuple[D3E0LocalPatch, ...]
    accepted_support_mask: np.ndarray
    hard_protection_mask: np.ndarray
    rejected_components: tuple[D3E0RejectedComponent, ...]
    source_geometry_sha256: str
    diagnostics: Mapping[str, object]


@dataclass
class _RawComponent:
    keys: tuple[tuple[str, int, int], ...]
    points: np.ndarray
    total: float
    cumulative: np.ndarray
    provisional_hash: str
    polarity_delta: float = 0.0
    reject_reasons: tuple[str, ...] = ()
    safe_segments: np.ndarray | None = None
    patches: list[tuple[float, float, np.ndarray, np.ndarray]] | None = None


# Edge numbers use corners TL, TR, BR, BL and edges top, right, bottom, left.
_CASE_EDGE_PAIRS: Mapping[int, tuple[int, int]] = MappingProxyType({
    1: (3, 0),
    2: (0, 1),
    3: (3, 1),
    4: (1, 2),
    6: (0, 2),
    7: (3, 2),
    8: (2, 3),
    9: (0, 2),
    11: (1, 2),
    12: (3, 1),
    13: (0, 1),
    14: (3, 0),
})


def _readonly(array: np.ndarray) -> np.ndarray:
    result = np.ascontiguousarray(array)
    result.setflags(write=False)
    return result


def _validate_inputs(
    source_rgb: np.ndarray,
    native_masks: Mapping[str, np.ndarray],
) -> tuple[tuple[int, int], dict[str, np.ndarray]]:
    if not isinstance(source_rgb, np.ndarray):
        raise TypeError("D3-E0 source_rgb must be a numpy ndarray")
    if source_rgb.ndim != 3 or source_rgb.shape[2] != 3:
        raise ValueError(
            f"D3-E0 expected HxWx3 source RGB, got {source_rgb.shape}"
        )
    if source_rgb.dtype != np.float32:
        raise TypeError("D3-E0 source RGB must have exact float32 dtype")
    if source_rgb.shape[0] < 2 or source_rgb.shape[1] < 2:
        raise ValueError("D3-E0 source matrix must contain at least one cell")
    if not np.all(np.isfinite(source_rgb)):
        raise ValueError("D3-E0 source RGB contains non-finite values")
    if np.any((source_rgb < 0.0) | (source_rgb > 1.0)):
        raise ValueError("D3-E0 source RGB must stay within [0, 1]")
    if not isinstance(native_masks, Mapping):
        raise TypeError("D3-E0 native_masks must be a mapping")

    shape = source_rgb.shape[:2]
    copied: dict[str, np.ndarray] = {}
    for name in ("ink", "fx", "background", "flat"):
        if name not in native_masks:
            raise KeyError(f"D3-E0 native masks omit {name!r}")
        raw = native_masks[name]
        if not isinstance(raw, np.ndarray):
            raise TypeError(f"D3-E0 mask {name!r} must be a numpy ndarray")
        if raw.shape != shape:
            raise ValueError(
                f"D3-E0 mask {name!r} has shape {raw.shape}, expected {shape}"
            )
        if raw.dtype != np.float32:
            raise TypeError(
                f"D3-E0 mask {name!r} must have exact float32 dtype"
            )
        if raw.flags.writeable:
            raise ValueError(f"D3-E0 mask {name!r} must be read-only")
        if not np.all(np.isfinite(raw)):
            raise ValueError(f"D3-E0 mask {name!r} contains non-finite values")
        if np.any((raw < 0.0) | (raw > 1.0)):
            raise ValueError(f"D3-E0 mask {name!r} must stay within [0, 1]")
        copied[name] = np.array(raw, dtype=np.float32, order="C", copy=True)
    return shape, copied


def _edge_key(edge: int, y: int, x: int) -> tuple[str, int, int]:
    if edge == 0:
        return ("h", y, x)
    if edge == 1:
        return ("v", y, x + 1)
    if edge == 2:
        return ("h", y + 1, x)
    if edge == 3:
        return ("v", y, x)
    raise ValueError(f"invalid Marching-Squares edge {edge}")


def _edge_coordinate(
    key: tuple[str, int, int],
    ink: np.ndarray,
    iso: float,
) -> np.ndarray:
    kind, y, x = key
    if kind == "h":
        left = float(ink[y, x])
        right = float(ink[y, x + 1])
        denominator = right - left
        if denominator == 0.0:
            raise RuntimeError("D3-E0 horizontal crossing has zero denominator")
        fraction = (iso - left) / denominator
        point = np.array([x + fraction, y], dtype=np.float64)
    elif kind == "v":
        top = float(ink[y, x])
        bottom = float(ink[y + 1, x])
        denominator = bottom - top
        if denominator == 0.0:
            raise RuntimeError("D3-E0 vertical crossing has zero denominator")
        fraction = (iso - top) / denominator
        point = np.array([x, y + fraction], dtype=np.float64)
    else:
        raise RuntimeError(f"D3-E0 unknown graph edge kind {kind!r}")
    if not np.all(np.isfinite(point)) or np.any(
        (point < -1e-12)
        | (point > np.array([ink.shape[1] - 1, ink.shape[0] - 1]) + 1e-12)
    ):
        raise RuntimeError("D3-E0 generated an invalid edge crossing")
    return point


def _marching_graph(
    ink: np.ndarray,
    params: D3E0Params,
) -> tuple[
    dict[tuple[str, int, int], set[tuple[str, int, int]]],
    dict[tuple[str, int, int], np.ndarray],
    np.ndarray,
    dict[str, int],
]:
    height, width = ink.shape
    adjacency: dict[tuple[str, int, int], set[tuple[str, int, int]]] = {}
    coordinates: dict[tuple[str, int, int], np.ndarray] = {}
    unsafe_cells = np.zeros((height - 1, width - 1), dtype=bool)
    counts = {
        "empty_or_full_cells": 0,
        "tie_cells": 0,
        "ambiguous_cells": 0,
        "segment_cells": 0,
    }
    iso = params.ink_iso
    tolerance = params.exact_vertex_tie_abs_tolerance

    for y in range(height - 1):
        for x in range(width - 1):
            values = np.array(
                [ink[y, x], ink[y, x + 1], ink[y + 1, x + 1], ink[y + 1, x]],
                dtype=np.float64,
            )
            if np.any(np.abs(values - iso) <= tolerance):
                unsafe_cells[y, x] = True
                counts["tie_cells"] += 1
                continue
            inside = values > iso
            case = int(inside[0]) | (int(inside[1]) << 1) | (
                int(inside[2]) << 2
            ) | (int(inside[3]) << 3)
            if case in (0, 15):
                counts["empty_or_full_cells"] += 1
                continue
            if case in (5, 10):
                unsafe_cells[y, x] = True
                counts["ambiguous_cells"] += 1
                continue
            pair = _CASE_EDGE_PAIRS.get(case)
            if pair is None:
                raise RuntimeError(f"D3-E0 unhandled Marching-Squares case {case}")
            first = _edge_key(pair[0], y, x)
            second = _edge_key(pair[1], y, x)
            if first == second:
                raise RuntimeError("D3-E0 emitted a degenerate graph segment")
            for key in (first, second):
                if key not in coordinates:
                    coordinates[key] = _edge_coordinate(key, ink, iso)
                adjacency.setdefault(key, set())
            adjacency[first].add(second)
            adjacency[second].add(first)
            counts["segment_cells"] += 1
    return adjacency, coordinates, unsafe_cells, counts


def _provisional_hash(keys: Iterable[tuple[str, int, int]]) -> str:
    digest = hashlib.sha256()
    digest.update(ESTIMATOR_ID.encode("ascii"))
    for kind, y, x in sorted(keys):
        digest.update(kind.encode("ascii"))
        digest.update(np.asarray([y, x], dtype="<i8").tobytes())
    return digest.hexdigest()


def _graph_components(
    adjacency: Mapping[tuple[str, int, int], set[tuple[str, int, int]]],
    coordinates: Mapping[tuple[str, int, int], np.ndarray],
) -> tuple[list[_RawComponent], list[D3E0RejectedComponent]]:
    remaining = set(adjacency)
    accepted_graphs: list[_RawComponent] = []
    rejected: list[D3E0RejectedComponent] = []
    while remaining:
        seed = min(remaining)
        stack = [seed]
        component_keys: set[tuple[str, int, int]] = set()
        while stack:
            key = stack.pop()
            if key in component_keys:
                continue
            component_keys.add(key)
            remaining.discard(key)
            stack.extend(sorted(adjacency[key] - component_keys, reverse=True))
        edge_count = sum(len(adjacency[key]) for key in component_keys) // 2
        provisional = _provisional_hash(component_keys)
        if any(len(adjacency[key]) != 2 for key in component_keys):
            rejected.append(D3E0RejectedComponent(
                provisional,
                len(component_keys),
                edge_count,
                ("graph_not_closed_degree_two",),
            ))
            continue

        start = min(component_keys)
        first = min(adjacency[start])
        ordered = [start]
        previous = start
        current = first
        while current != start and len(ordered) <= len(component_keys):
            ordered.append(current)
            next_keys = sorted(adjacency[current] - {previous})
            if len(next_keys) != 1:
                break
            previous, current = current, next_keys[0]
        if current != start or len(ordered) != len(component_keys):
            rejected.append(D3E0RejectedComponent(
                provisional,
                len(component_keys),
                edge_count,
                ("graph_cycle_traversal_failed",),
            ))
            continue
        points = np.vstack([coordinates[key] for key in ordered]).astype(
            np.float64, copy=False
        )
        lengths = np.linalg.norm(np.roll(points, -1, axis=0) - points, axis=1)
        if np.any(~np.isfinite(lengths)) or np.any(lengths <= 0.0):
            rejected.append(D3E0RejectedComponent(
                provisional,
                len(component_keys),
                edge_count,
                ("nonfinite_or_degenerate_segment",),
            ))
            continue
        cumulative = np.concatenate(([0.0], np.cumsum(lengths)))
        accepted_graphs.append(_RawComponent(
            keys=tuple(ordered),
            points=points,
            total=float(cumulative[-1]),
            cumulative=cumulative,
            provisional_hash=provisional,
        ))
    accepted_graphs.sort(key=lambda component: component.provisional_hash)
    rejected.sort(key=lambda component: component.provisional_sha256)
    return accepted_graphs, rejected


def _bilinear_scalar(field: np.ndarray, points_xy: np.ndarray) -> np.ndarray:
    points = np.asarray(points_xy, dtype=np.float64)
    x = np.clip(points[:, 0], 0.0, field.shape[1] - 1.0)
    y = np.clip(points[:, 1], 0.0, field.shape[0] - 1.0)
    x0 = np.floor(x).astype(np.int64)
    y0 = np.floor(y).astype(np.int64)
    x1 = np.minimum(x0 + 1, field.shape[1] - 1)
    y1 = np.minimum(y0 + 1, field.shape[0] - 1)
    wx = x - x0
    wy = y - y0
    return (
        field[y0, x0] * (1.0 - wx) * (1.0 - wy)
        + field[y0, x1] * wx * (1.0 - wy)
        + field[y1, x0] * (1.0 - wx) * wy
        + field[y1, x1] * wx * wy
    ).astype(np.float64, copy=False)


def _signed_area(points: np.ndarray) -> float:
    following = np.roll(points, -1, axis=0)
    return float(
        0.5 * np.sum(points[:, 0] * following[:, 1] - following[:, 0] * points[:, 1])
    )


def _rotate_cycle(
    keys: Sequence[tuple[str, int, int]],
    points: np.ndarray,
) -> tuple[tuple[tuple[str, int, int], ...], np.ndarray]:
    index = min(range(len(keys)), key=lambda value: keys[value])
    rotated_keys = tuple(keys[index:]) + tuple(keys[:index])
    rotated_points = np.concatenate((points[index:], points[:index]), axis=0)
    return rotated_keys, rotated_points


def _orient_ink_left(
    component: _RawComponent,
    ink: np.ndarray,
    probe_native: float,
    minimum_delta: float,
) -> bool:
    points = component.points
    following = np.roll(points, -1, axis=0)
    tangent = following - points
    lengths = np.linalg.norm(tangent, axis=1)
    unit = tangent / lengths[:, None]
    # In native image coordinates y increases downward; image-space left is
    # therefore (dy, -dx).
    left_normal = np.column_stack((unit[:, 1], -unit[:, 0]))
    midpoint = 0.5 * (points + following)
    left = _bilinear_scalar(ink, midpoint + probe_native * left_normal)
    right = _bilinear_scalar(ink, midpoint - probe_native * left_normal)
    delta = float(np.median(left - right))
    if not math.isfinite(delta) or abs(delta) < minimum_delta:
        component.reject_reasons = tuple(sorted(set(
            component.reject_reasons + ("ambiguous_polarity",)
        )))
        return False
    keys: Sequence[tuple[str, int, int]] = component.keys
    if delta < 0.0:
        keys = tuple(reversed(keys))
        points = component.points[::-1].copy()
    keys, points = _rotate_cycle(keys, points)
    component.keys = keys
    component.points = points
    lengths = np.linalg.norm(np.roll(points, -1, axis=0) - points, axis=1)
    component.cumulative = np.concatenate(([0.0], np.cumsum(lengths)))
    component.total = float(component.cumulative[-1])

    following = np.roll(points, -1, axis=0)
    tangent = following - points
    lengths = np.linalg.norm(tangent, axis=1)
    unit = tangent / lengths[:, None]
    left_normal = np.column_stack((unit[:, 1], -unit[:, 0]))
    midpoint = 0.5 * (points + following)
    oriented_delta = float(np.median(
        _bilinear_scalar(ink, midpoint + probe_native * left_normal)
        - _bilinear_scalar(ink, midpoint - probe_native * left_normal)
    ))
    if not math.isfinite(oriented_delta) or oriented_delta < minimum_delta:
        component.reject_reasons = tuple(sorted(set(
            component.reject_reasons + ("polarity_orientation_failed",)
        )))
        return False
    component.polarity_delta = oriented_delta
    return True


def _point_at_arclength(component: _RawComponent, arclength: float) -> np.ndarray:
    value = float(arclength) % component.total
    index = int(np.searchsorted(component.cumulative, value, side="right") - 1)
    index = min(max(index, 0), len(component.points) - 1)
    start = component.points[index]
    end = component.points[(index + 1) % len(component.points)]
    segment_start = component.cumulative[index]
    segment_length = component.cumulative[index + 1] - segment_start
    fraction = (value - segment_start) / segment_length
    return start + fraction * (end - start)


def _cross_2d(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    return first[..., 0] * second[..., 1] - first[..., 1] * second[..., 0]


def _point_to_segments_squared(
    points: np.ndarray,
    starts: np.ndarray,
    ends: np.ndarray,
) -> np.ndarray:
    """Pairwise exact point-to-closed-segment squared distances."""
    delta = ends - starts
    length2 = np.sum(delta * delta, axis=-1)
    relative = points - starts
    numerator = np.sum(relative * delta, axis=-1)
    fraction = np.divide(
        numerator,
        length2,
        out=np.zeros_like(numerator, dtype=np.float64),
        where=length2 > 0.0,
    )
    fraction = np.clip(fraction, 0.0, 1.0)
    closest = starts + fraction[..., None] * delta
    return np.sum((points - closest) ** 2, axis=-1)


def _segment_pair_distance_matrix(
    first_starts: np.ndarray,
    first_ends: np.ndarray,
    second_starts: np.ndarray,
    second_ends: np.ndarray,
) -> np.ndarray:
    """Return exact pairwise distances between finite 2-D segments."""
    p = first_starts[:, None, :]
    p2 = first_ends[:, None, :]
    q = second_starts[None, :, :]
    q2 = second_ends[None, :, :]
    r = p2 - p
    s = q2 - q
    q_minus_p = q - p
    denominator = _cross_2d(r, s)
    numerator_t = _cross_2d(q_minus_p, s)
    numerator_u = _cross_2d(q_minus_p, r)
    nonparallel = np.abs(denominator) > 1e-14
    t = np.divide(
        numerator_t,
        denominator,
        out=np.zeros_like(denominator),
        where=nonparallel,
    )
    u = np.divide(
        numerator_u,
        denominator,
        out=np.zeros_like(denominator),
        where=nonparallel,
    )
    intersects = (
        nonparallel
        & (t >= -1e-14)
        & (t <= 1.0 + 1e-14)
        & (u >= -1e-14)
        & (u <= 1.0 + 1e-14)
    )
    distances2 = np.minimum.reduce((
        _point_to_segments_squared(p, q, q2),
        _point_to_segments_squared(p2, q, q2),
        _point_to_segments_squared(q, p, p2),
        _point_to_segments_squared(q2, p, p2),
    ))
    distances2[intersects] = 0.0
    return np.sqrt(np.maximum(distances2, 0.0))


def _minimum_exact_polyline_distance(
    first: _RawComponent,
    second: _RawComponent,
) -> float:
    """Exact minimum over every segment pair of two closed contours."""
    first_starts = first.points
    first_ends = np.roll(first.points, -1, axis=0)
    second_starts = second.points
    second_ends = np.roll(second.points, -1, axis=0)
    minimum = math.inf
    chunk = 128
    for left in range(0, len(first_starts), chunk):
        distances = _segment_pair_distance_matrix(
            first_starts[left : left + chunk],
            first_ends[left : left + chunk],
            second_starts,
            second_ends,
        )
        if distances.size:
            minimum = min(minimum, float(np.min(distances)))
    return minimum


def _minimum_exact_nonlocal_self_distance(
    component: _RawComponent,
    exclusion: float,
) -> float:
    """Exact nonlocal segment distance under a cyclic arc exclusion."""
    starts = component.points
    ends = np.roll(component.points, -1, axis=0)
    lengths = np.diff(component.cumulative)
    arc_starts = component.cumulative[:-1]
    arc_ends = component.cumulative[1:]
    if exclusion > 0.5 * component.total:
        return math.inf
    positive_band = (exclusion, component.total - exclusion)
    negative_band = (-component.total + exclusion, -exclusion)
    minimum = math.inf
    chunk = 128
    for left in range(0, len(starts), chunk):
        stop = min(left + chunk, len(starts))
        distances = _segment_pair_distance_matrix(
            starts[left:stop], ends[left:stop], starts, ends
        )
        difference_min = (
            arc_starts[left:stop, None] - arc_ends[None, :]
        )
        difference_max = (
            arc_ends[left:stop, None] - arc_starts[None, :]
        )
        intersects_positive = (
            (difference_max >= positive_band[0])
            & (difference_min <= positive_band[1])
        )
        intersects_negative = (
            (difference_max >= negative_band[0])
            & (difference_min <= negative_band[1])
        )
        fully_positive = (
            (difference_min >= positive_band[0])
            & (difference_max <= positive_band[1])
        )
        fully_negative = (
            (difference_min >= negative_band[0])
            & (difference_max <= negative_band[1])
        )
        eligible = intersects_positive | intersects_negative
        fully_eligible = fully_positive | fully_negative
        distances[~eligible] = np.inf

        straddling = np.argwhere(eligible & ~fully_eligible)
        for local_index, right_index in straddling:
            left_index = left + int(local_index)
            distances[local_index, right_index] = (
                _minimum_segment_pair_distance_in_arc_bands(
                    starts[left_index],
                    ends[left_index],
                    float(arc_starts[left_index]),
                    float(lengths[left_index]),
                    starts[right_index],
                    ends[right_index],
                    float(arc_starts[right_index]),
                    float(lengths[right_index]),
                    (positive_band, negative_band),
                )
            )
        if np.any(np.isfinite(distances)):
            minimum = min(minimum, float(np.min(distances)))
    return minimum


def _clip_unit_square_by_linear_band(
    offset: float,
    first_length: float,
    second_length: float,
    lower: float,
    upper: float,
) -> list[np.ndarray]:
    """Clip the (u,v) unit square by lower<=offset+Lu-Mv<=upper."""
    polygon = [
        np.array((0.0, 0.0), dtype=np.float64),
        np.array((1.0, 0.0), dtype=np.float64),
        np.array((1.0, 1.0), dtype=np.float64),
        np.array((0.0, 1.0), dtype=np.float64),
    ]

    def value(point: np.ndarray) -> float:
        return offset + first_length * point[0] - second_length * point[1]

    def clip(
        values: list[np.ndarray], threshold: float, keep_above: bool
    ) -> list[np.ndarray]:
        if not values:
            return []
        output: list[np.ndarray] = []
        previous = values[-1]
        previous_value = value(previous)
        previous_inside = (
            previous_value >= threshold if keep_above
            else previous_value <= threshold
        )
        for current in values:
            current_value = value(current)
            current_inside = (
                current_value >= threshold if keep_above
                else current_value <= threshold
            )
            if current_inside != previous_inside:
                denominator = current_value - previous_value
                if abs(denominator) <= 1e-15:
                    intersection = 0.5 * (previous + current)
                else:
                    fraction = (threshold - previous_value) / denominator
                    intersection = previous + fraction * (current - previous)
                output.append(intersection)
            if current_inside:
                output.append(current)
            previous = current
            previous_value = current_value
            previous_inside = current_inside
        return output

    polygon = clip(polygon, lower, True)
    return clip(polygon, upper, False)


def _minimum_segment_pair_distance_in_arc_bands(
    first_start: np.ndarray,
    first_end: np.ndarray,
    first_arc_start: float,
    first_length: float,
    second_start: np.ndarray,
    second_end: np.ndarray,
    second_arc_start: float,
    second_length: float,
    bands: Sequence[tuple[float, float]],
) -> float:
    """Exact quadratic minimum over allowed cyclic-arclength bands."""
    first_delta = first_end - first_start
    second_delta = second_end - second_start
    base = first_start - second_start
    matrix = np.column_stack((first_delta, -second_delta))
    minimum2 = math.inf
    offset = first_arc_start - second_arc_start

    for lower, upper in bands:
        polygon = _clip_unit_square_by_linear_band(
            offset,
            first_length,
            second_length,
            lower,
            upper,
        )
        if not polygon:
            continue

        solution, _residuals, _rank, _singular = np.linalg.lstsq(
            matrix, -base, rcond=None
        )
        difference = (
            offset + first_length * solution[0] - second_length * solution[1]
        )
        if (
            -1e-12 <= solution[0] <= 1.0 + 1e-12
            and -1e-12 <= solution[1] <= 1.0 + 1e-12
            and lower - 1e-12 <= difference <= upper + 1e-12
        ):
            residual = base + matrix @ solution
            minimum2 = min(minimum2, float(np.dot(residual, residual)))

        for first, second in zip(polygon, polygon[1:] + polygon[:1]):
            direction = second - first
            spatial_start = base + matrix @ first
            spatial_delta = matrix @ direction
            denominator = float(np.dot(spatial_delta, spatial_delta))
            if denominator <= 1e-30:
                fraction = 0.0
            else:
                fraction = float(np.clip(
                    -np.dot(spatial_start, spatial_delta) / denominator,
                    0.0,
                    1.0,
                ))
            residual = spatial_start + fraction * spatial_delta
            minimum2 = min(minimum2, float(np.dot(residual, residual)))
    return math.sqrt(max(minimum2, 0.0)) if math.isfinite(minimum2) else math.inf


def _point_to_rectangle_distance(
    point: np.ndarray,
    minimum: np.ndarray,
    maximum: np.ndarray,
) -> float:
    delta = np.maximum(np.maximum(minimum - point, point - maximum), 0.0)
    return float(np.linalg.norm(delta))


def _segment_to_rectangle_distance(
    start: np.ndarray,
    end: np.ndarray,
    minimum: np.ndarray,
    maximum: np.ndarray,
) -> float:
    """Exact distance between a segment and a closed axis-aligned rectangle."""
    if np.all(start >= minimum) and np.all(start <= maximum):
        return 0.0
    if np.all(end >= minimum) and np.all(end <= maximum):
        return 0.0
    corners = np.array([
        [minimum[0], minimum[1]],
        [maximum[0], minimum[1]],
        [maximum[0], maximum[1]],
        [minimum[0], maximum[1]],
    ], dtype=np.float64)
    edge_ends = np.roll(corners, -1, axis=0)
    segment_distance = _segment_pair_distance_matrix(
        np.asarray(start, dtype=np.float64)[None, :],
        np.asarray(end, dtype=np.float64)[None, :],
        corners,
        edge_ends,
    )
    return min(
        float(np.min(segment_distance)),
        _point_to_rectangle_distance(start, minimum, maximum),
        _point_to_rectangle_distance(end, minimum, maximum),
    )


def _segment_to_unsafe_cells_distance(
    start: np.ndarray,
    end: np.ndarray,
    unsafe_cell_yx: np.ndarray,
    clearance: float,
) -> float:
    """Exact distance to the union of all unsafe native unit cells."""
    if len(unsafe_cell_yx) == 0:
        return math.inf
    ys = unsafe_cell_yx[:, 0]
    xs = unsafe_cell_yx[:, 1]
    minimum_x = min(float(start[0]), float(end[0])) - clearance
    maximum_x = max(float(start[0]), float(end[0])) + clearance
    minimum_y = min(float(start[1]), float(end[1])) - clearance
    maximum_y = max(float(start[1]), float(end[1])) + clearance
    possible = (
        (xs + 1.0 >= minimum_x)
        & (xs <= maximum_x)
        & (ys + 1.0 >= minimum_y)
        & (ys <= maximum_y)
    )
    minimum_distance = math.inf
    for y, x in zip(ys[possible], xs[possible], strict=True):
        distance = _segment_to_rectangle_distance(
            start,
            end,
            np.array([float(x), float(y)], dtype=np.float64),
            np.array([float(x + 1), float(y + 1)], dtype=np.float64),
        )
        minimum_distance = min(minimum_distance, distance)
        if minimum_distance <= clearance:
            return minimum_distance
    return minimum_distance


def _segment_to_true_pixel_centres_distance(
    start: np.ndarray,
    end: np.ndarray,
    true_pixel_yx: np.ndarray,
    clearance: float,
) -> float:
    """Exact distance from one segment to preregistered true pixel centres."""
    if len(true_pixel_yx) == 0:
        return math.inf
    ys = true_pixel_yx[:, 0]
    xs = true_pixel_yx[:, 1]
    minimum_x = min(float(start[0]), float(end[0])) - clearance
    maximum_x = max(float(start[0]), float(end[0])) + clearance
    minimum_y = min(float(start[1]), float(end[1])) - clearance
    maximum_y = max(float(start[1]), float(end[1])) + clearance
    possible = (
        (xs >= minimum_x)
        & (xs <= maximum_x)
        & (ys >= minimum_y)
        & (ys <= maximum_y)
    )
    if not np.any(possible):
        return math.inf
    points = np.column_stack((xs[possible], ys[possible])).astype(
        np.float64, copy=False
    )
    distances2 = _point_to_segments_squared(
        points,
        np.broadcast_to(np.asarray(start, dtype=np.float64), points.shape),
        np.broadcast_to(np.asarray(end, dtype=np.float64), points.shape),
    )
    return float(np.sqrt(np.min(np.maximum(distances2, 0.0))))


def _circumradius_and_cross(
    before: np.ndarray,
    centre: np.ndarray,
    after: np.ndarray,
) -> tuple[float, float]:
    first = centre - before
    second = after - centre
    chord = after - before
    cross = float(first[0] * second[1] - first[1] * second[0])
    denominator = 2.0 * abs(cross)
    if denominator <= 1e-14:
        return math.inf, cross
    radius = (
        float(np.linalg.norm(first))
        * float(np.linalg.norm(second))
        * float(np.linalg.norm(chord))
        / denominator
    )
    return radius, cross


def _segment_safety(
    component: _RawComponent,
    shape: tuple[int, int],
    scale: float,
    hard_seed_yx: np.ndarray,
    unsafe_cell_yx: np.ndarray,
    params: D3E0Params,
) -> tuple[np.ndarray, bool, bool, bool]:
    segment_count = len(component.points)
    safe = np.ones(segment_count, dtype=bool)
    half_window = params.curvature_measurement_half_window_720px * scale
    minimum_radius = params.minimum_safe_curvature_radius_720px * scale
    concave_reject_radius = (
        params.sharp_concave_component_reject_radius_720px * scale
    )
    frame_guard = params.frame_guard_720px * scale
    hard_clearance = (
        params.support_radius_720px + params.hard_footprint_margin_720px
    ) * scale
    ambiguity_clearance = params.ambiguity_guard_720px * scale
    signed_area = _signed_area(component.points)
    sharp_concavity = False
    frame_violation = False
    ambiguity_violation = False

    for index in range(segment_count):
        start = component.points[index]
        end = component.points[(index + 1) % segment_count]
        midpoint_s = 0.5 * (
            component.cumulative[index] + component.cumulative[index + 1]
        )
        point = _point_at_arclength(component, midpoint_s)
        before = _point_at_arclength(component, midpoint_s - half_window)
        after = _point_at_arclength(component, midpoint_s + half_window)
        radius, cross = _circumradius_and_cross(before, point, after)
        if radius < minimum_radius:
            safe[index] = False
        if signed_area != 0.0 and cross * signed_area < 0.0 and (
            radius < concave_reject_radius
        ):
            sharp_concavity = True

        frame_distance = min(
            float(start[0]),
            float(start[1]),
            shape[1] - 1.0 - float(start[0]),
            shape[0] - 1.0 - float(start[1]),
            float(end[0]),
            float(end[1]),
            shape[1] - 1.0 - float(end[0]),
            shape[0] - 1.0 - float(end[1]),
        )
        if frame_distance < frame_guard:
            safe[index] = False
            frame_violation = True
        if _segment_to_true_pixel_centres_distance(
            start, end, hard_seed_yx, hard_clearance
        ) <= hard_clearance:
            safe[index] = False
        if _segment_to_unsafe_cells_distance(
            start, end, unsafe_cell_yx, ambiguity_clearance
        ) <= ambiguity_clearance:
            safe[index] = False
            ambiguity_violation = True
    return safe, sharp_concavity, frame_violation, ambiguity_violation


def _global_component_safety(
    components: list[_RawComponent],
    scale: float,
    params: D3E0Params,
) -> None:
    for component in components:
        if component.total < params.minimum_closed_contour_length_720px * scale:
            component.reject_reasons += ("closed_contour_too_short",)
        minimum_self = _minimum_exact_nonlocal_self_distance(
            component,
            params.nonlocal_self_arc_exclusion_720px * scale,
        )
        if minimum_self < (
            params.minimum_opposite_contour_separation_720px * scale
        ):
            component.reject_reasons += ("opposite_contour_separation_failed",)

    conflicting: set[int] = set()
    separation = params.different_component_separation_guard_720px * scale
    for left_index in range(len(components)):
        for right_index in range(left_index + 1, len(components)):
            distance = _minimum_exact_polyline_distance(
                components[left_index], components[right_index]
            )
            if distance < separation:
                conflicting.add(left_index)
                conflicting.add(right_index)
    for index in sorted(conflicting):
        components[index].reject_reasons += (
            "different_component_separation_guard_failed",
        )


def _circular_true_runs(values: np.ndarray, lengths: np.ndarray) -> list[tuple[float, float]]:
    count = len(values)
    if count == 0 or not np.any(values):
        return []
    cumulative = np.concatenate(([0.0], np.cumsum(lengths)))
    total = float(cumulative[-1])
    if np.all(values):
        return [(0.0, total)]
    first_false = int(np.flatnonzero(~values)[0])
    runs: list[tuple[float, float]] = []
    run_start: float | None = None
    for offset in range(1, count + 1):
        index = (first_false + offset) % count
        absolute_start = cumulative[index]
        if index <= first_false:
            absolute_start += total
        if values[index] and run_start is None:
            run_start = absolute_start
        if not values[index] and run_start is not None:
            runs.append((run_start, absolute_start))
            run_start = None
    if run_start is not None:
        runs.append((run_start, total + cumulative[first_false + 1]))
    return runs


def _extract_patch_polyline(
    component: _RawComponent,
    start: float,
    end: float,
) -> np.ndarray:
    if end <= start:
        raise ValueError("D3-E0 patch end must follow start")
    values: list[float] = [start]
    base = math.floor(start / component.total) * component.total
    for offset in (base, base + component.total, base + 2.0 * component.total):
        for value in component.cumulative[1:-1]:
            absolute = offset + float(value)
            if start < absolute < end:
                values.append(absolute)
    values.append(end)
    values = sorted(set(values))
    return np.vstack([_point_at_arclength(component, value) for value in values])


def _polyline_support_mask(
    points: np.ndarray,
    shape: tuple[int, int],
    radius: float,
) -> np.ndarray:
    result = np.zeros(shape, dtype=bool)
    for first, second in zip(points[:-1], points[1:]):
        minimum_x = max(0, int(math.floor(min(first[0], second[0]) - radius)))
        maximum_x = min(
            shape[1] - 1,
            int(math.ceil(max(first[0], second[0]) + radius)),
        )
        minimum_y = max(0, int(math.floor(min(first[1], second[1]) - radius)))
        maximum_y = min(
            shape[0] - 1,
            int(math.ceil(max(first[1], second[1]) + radius)),
        )
        if maximum_x < minimum_x or maximum_y < minimum_y:
            continue
        ys, xs = np.mgrid[
            minimum_y : maximum_y + 1,
            minimum_x : maximum_x + 1,
        ]
        vector = second - first
        squared_length = float(np.dot(vector, vector))
        if squared_length <= 0.0:
            continue
        fraction = np.clip(
            ((xs - first[0]) * vector[0] + (ys - first[1]) * vector[1])
            / squared_length,
            0.0,
            1.0,
        )
        closest_x = first[0] + fraction * vector[0]
        closest_y = first[1] + fraction * vector[1]
        local = (xs - closest_x) ** 2 + (ys - closest_y) ** 2 <= (
            radius * radius + 1e-12
        )
        result[minimum_y : maximum_y + 1, minimum_x : maximum_x + 1] |= local
    return result


def _build_patches(
    component: _RawComponent,
    shape: tuple[int, int],
    scale: float,
    hard_mask: np.ndarray,
    params: D3E0Params,
) -> list[tuple[float, float, np.ndarray, np.ndarray]]:
    if component.safe_segments is None:
        return []
    lengths = np.diff(component.cumulative)
    runs = _circular_true_runs(component.safe_segments, lengths)
    minimum_run = params.minimum_safe_run_length_720px * scale
    endpoint_guard = params.patch_endpoint_guard_720px * scale
    minimum_active = params.minimum_active_patch_arc_length_720px * scale
    support_radius = params.support_radius_720px * scale
    hard_radius = (
        params.support_radius_720px + params.hard_footprint_margin_720px
    ) * scale
    patches: list[tuple[float, float, np.ndarray, np.ndarray]] = []
    all_safe = bool(np.all(component.safe_segments))
    for run_start, run_end in runs:
        run_length = run_end - run_start
        if run_length < minimum_run:
            continue
        if all_safe:
            start, end = 0.0, component.total
        else:
            start = run_start + endpoint_guard
            end = run_end - endpoint_guard
        if end - start < minimum_active:
            continue
        points = _extract_patch_polyline(component, start, end)
        hard_footprint = _polyline_support_mask(points, shape, hard_radius)
        if np.any(hard_footprint & hard_mask):
            continue
        support = _polyline_support_mask(points, shape, support_radius)
        normalized_start = start % component.total
        normalized_unwrapped_end = normalized_start + (end - start)
        patches.append((
            normalized_start,
            normalized_unwrapped_end,
            points,
            support,
        ))
        if all_safe:
            break
    patches.sort(key=lambda item: item[0])
    return patches


def _geometry_hash(points: np.ndarray, *, prefix: str) -> str:
    digest = hashlib.sha256()
    digest.update(ESTIMATOR_ID.encode("ascii"))
    digest.update(prefix.encode("ascii"))
    digest.update(np.asarray(points.shape, dtype="<i8").tobytes())
    digest.update(np.asarray(points, dtype="<f8", order="C").tobytes())
    return digest.hexdigest()


def _source_hash(
    shape: tuple[int, int],
    masks: Mapping[str, np.ndarray],
    params: D3E0Params,
    component_hashes: Sequence[str],
    patch_hashes: Sequence[str],
) -> str:
    digest = hashlib.sha256()
    digest.update(ESTIMATOR_ID.encode("ascii"))
    digest.update(np.asarray(shape, dtype="<i8").tobytes())
    parameter_json = json.dumps(
        asdict(params),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")
    digest.update(parameter_json)
    for name in ("ink", "fx", "background", "flat"):
        digest.update(name.encode("ascii"))
        digest.update(np.asarray(masks[name], dtype="<f4", order="C").tobytes())
    for value in component_hashes:
        digest.update(value.encode("ascii"))
    for value in patch_hashes:
        digest.update(value.encode("ascii"))
    return digest.hexdigest()


def estimate_d3_e0(
    source_rgb: np.ndarray,
    native_masks: Mapping[str, np.ndarray],
    params: D3E0Params | None = None,
) -> D3E0EstimatorResult:
    """Estimate safe, ordered ``ink=0.50`` contour patches from source M0.

    The function is deterministic, performs no I/O, does not mutate inputs,
    and cannot produce an image.  Any uncertainty rejects the affected whole
    component or whole local patch rather than repairing or imputing geometry.
    """

    params = D3E0Params() if params is None else params
    params.validate()
    shape, masks = _validate_inputs(source_rgb, native_masks)
    scale = float(shape[0]) / 720.0
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError("D3-E0 native scale must be finite and positive")

    hard_mask = (
        (masks["fx"] >= params.fx_hard_min)
        | (masks["background"] >= params.background_hard_min)
        | (masks["flat"] >= params.flat_hard_min)
    )
    adjacency, vertex_coordinates, unsafe_cells, marching_counts = (
        _marching_graph(masks["ink"], params)
    )
    components, graph_rejected = _graph_components(
        adjacency, vertex_coordinates
    )
    _global_component_safety(components, scale, params)
    hard_seed_yx = np.argwhere(hard_mask)
    unsafe_cell_yx = np.argwhere(unsafe_cells)

    rejected: list[D3E0RejectedComponent] = list(graph_rejected)

    for component in components:
        if not _orient_ink_left(
            component,
            masks["ink"],
            params.polarity_probe_720px * scale,
            params.polarity_minimum_delta,
        ):
            continue
        safe, sharp_concavity, frame_violation, ambiguity_violation = (
            _segment_safety(
                component,
                shape,
                scale,
                hard_seed_yx,
                unsafe_cell_yx,
                params,
            )
        )
        component.safe_segments = safe
        if sharp_concavity:
            component.reject_reasons += ("sharp_concave_component",)
        if frame_violation:
            component.reject_reasons += ("frame_guard_failed",)
        if ambiguity_violation:
            component.reject_reasons += ("ambiguous_cell_guard_failed",)
        component.reject_reasons = tuple(sorted(set(component.reject_reasons)))

    eligible = [component for component in components if not component.reject_reasons]
    for component in eligible:
        component.patches = _build_patches(
            component, shape, scale, hard_mask, params
        )
        if not component.patches:
            component.reject_reasons = ("no_minimum_active_safe_patch",)

    # Reject all components whose accepted support overlaps.  This happens
    # after local patch certification and before any result is exposed.
    support_by_component: dict[int, np.ndarray] = {}
    for index, component in enumerate(components):
        if component.reject_reasons or not component.patches:
            continue
        union = np.zeros(shape, dtype=bool)
        internal_overlap = False
        for _, _, _, support in component.patches:
            if np.any(union & support):
                internal_overlap = True
            union |= support
        if internal_overlap:
            component.reject_reasons = ("patch_support_overlap",)
        else:
            support_by_component[index] = union

    overlap_indices: set[int] = set()
    support_items = sorted(support_by_component.items())
    for left_position, (left_index, left_support) in enumerate(support_items):
        for right_index, right_support in support_items[left_position + 1 :]:
            if np.any(left_support & right_support):
                overlap_indices.add(left_index)
                overlap_indices.add(right_index)
    for index in sorted(overlap_indices):
        components[index].reject_reasons = ("patch_support_overlap",)

    accepted_records: list[tuple[_RawComponent, str]] = []
    for component in components:
        component.reject_reasons = tuple(sorted(set(component.reject_reasons)))
        if component.reject_reasons:
            rejected.append(D3E0RejectedComponent(
                component.provisional_hash,
                len(component.keys),
                len(component.keys),
                component.reject_reasons,
            ))
            continue
        geometry_hash = _geometry_hash(component.points, prefix="component")
        accepted_records.append((component, geometry_hash))
    accepted_records.sort(key=lambda item: item[1])

    result_components: list[D3E0ContourComponent] = []
    patch_records: list[
        tuple[str, float, D3E0LocalPatch, np.ndarray]
    ] = []
    for component, component_hash in accepted_records:
        assert component.patches is not None
        result_components.append(D3E0ContourComponent(
            geometry_sha256=component_hash,
            coordinates_xy=_readonly(component.points.astype(np.float64, copy=True)),
            total_arclength_native_px=float(component.total),
            signed_area_native_px2=_signed_area(component.points),
            polarity_median_delta=float(component.polarity_delta),
            ink_greater_is_left=True,
            accepted_patch_count=len(component.patches),
        ))
        for start, end, points, support in component.patches:
            patch_hash = _geometry_hash(points, prefix=f"patch:{component_hash}")
            indices = np.flatnonzero(support).astype(np.int64, copy=False)
            patch = D3E0LocalPatch(
                component_geometry_sha256=component_hash,
                patch_geometry_sha256=patch_hash,
                start_arclength_native_px=float(start),
                end_arclength_native_px=float(end),
                arclength_native_px=float(end - start),
                coordinates_xy=_readonly(points.astype(np.float64, copy=True)),
                support_linear_indices=_readonly(indices.copy()),
                ink_greater_is_left=True,
            )
            patch_records.append((component_hash, float(start), patch, support))
    patch_records.sort(key=lambda item: (item[0], item[1], item[2].patch_geometry_sha256))

    accepted_support = np.zeros(shape, dtype=bool)
    for _, _, _, support in patch_records:
        if np.any(accepted_support & support):
            raise RuntimeError("D3-E0 exposed overlapping accepted support")
        accepted_support |= support
    if np.any(accepted_support & hard_mask):
        raise RuntimeError("D3-E0 exposed support intersecting a hard seed")

    result_patches = tuple(item[2] for item in patch_records)
    component_hashes = [item.geometry_sha256 for item in result_components]
    patch_hashes = [item.patch_geometry_sha256 for item in result_patches]
    source_hash = _source_hash(
        shape, masks, params, component_hashes, patch_hashes
    )
    rejected.sort(key=lambda item: (item.provisional_sha256, item.reasons))
    reason_counts: dict[str, int] = {}
    for item in rejected:
        for reason in item.reasons:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
    diagnostics = MappingProxyType({
        "native_shape_hw": tuple(int(value) for value in shape),
        "native_scale_from_720": scale,
        "marching_counts": MappingProxyType(dict(marching_counts)),
        "unsafe_cell_count": int(np.count_nonzero(unsafe_cells)),
        "graph_vertex_count": len(adjacency),
        "accepted_component_count": len(result_components),
        "accepted_patch_count": len(result_patches),
        "accepted_support_pixel_count": int(np.count_nonzero(accepted_support)),
        "hard_support_intersection_count": int(np.count_nonzero(
            accepted_support & hard_mask
        )),
        "rejected_component_count": len(rejected),
        "rejection_reason_counts": MappingProxyType(dict(sorted(reason_counts.items()))),
        "rgb_geometry_reads": 0,
        "renderer_present": False,
    })
    return D3E0EstimatorResult(
        estimator_id=ESTIMATOR_ID,
        native_scale_from_720=scale,
        contour_components=tuple(result_components),
        local_patches=result_patches,
        accepted_support_mask=_readonly(accepted_support),
        hard_protection_mask=_readonly(hard_mask.astype(bool, copy=True)),
        rejected_components=tuple(rejected),
        source_geometry_sha256=source_hash,
        diagnostics=diagnostics,
    )


__all__ = [
    "D3E0ContourComponent",
    "D3E0EstimatorResult",
    "D3E0LocalPatch",
    "D3E0Params",
    "D3E0RejectedComponent",
    "ESTIMATOR_ID",
    "FROZEN_PARAMETER_VALUES",
    "estimate_d3_e0",
]
