#!/usr/bin/env python3
"""Goal4924 columnar reprojection/sort probe.

This is an internal experiment around the already proven Goal4886 public
RTDL primitives route. It does not modify RTDL core and does not import the
bundled RayJoin overlay helper.

The probe replaces two app-layer functions:

- intersection_rows_from_pairs: avoid fractions.Fraction object materialization
  while preserving the integer/rational data needed for sorting.
- sort_xsects_for_map: test a fast scaled-integer key or an exact rational
  comparator without Fraction objects.

Usage mirrors goal4886_section57_public_primitives_overlay_numba_harness.py.
Set GOAL4924_SORT_MODE to "scaled_int" or "exact_cmp"; default is "scaled_int".
"""

from __future__ import annotations

import importlib.util
import json
import math
import os
import sys
import time
from functools import cmp_to_key
from pathlib import Path

import numpy as np


THIS_DIR = Path(__file__).resolve().parent
GOAL4886 = THIS_DIR / "goal4886_section57_public_primitives_overlay_numba_harness.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


wrapper = _load_module(GOAL4886, "goal4886_section57_public_primitives_overlay_numba_harness")
base = wrapper.base
kernels = wrapper.kernels
midpoint_points_numba_enabled = wrapper.midpoint_points_numba_enabled
dedupe_point_pairs_numba_enabled = wrapper.dedupe_point_pairs_numba_enabled
write_output_chains_streaming_numba_skip = wrapper.write_output_chains_streaming_numba_skip


def _normalize_fraction_parts(num: int, den: int) -> tuple[int, int]:
    if den == 0:
        raise ZeroDivisionError("zero denominator in intersection rational")
    if den < 0:
        num = -int(num)
        den = -int(den)
    else:
        num = int(num)
        den = int(den)
    gcd = math.gcd(num, den)
    if gcd > 1:
        num //= gcd
        den //= gcd
    return num, den


def _clamp_rational_to_int_range(num: int, den: int, lo: int, hi: int) -> tuple[int, int]:
    num, den = _normalize_fraction_parts(num, den)
    if num < int(lo) * den:
        return int(lo), 1
    if num > int(hi) * den:
        return int(hi), 1
    return num, den


def _author_rational_parts_to_internal(num: int, den: int) -> int:
    num, den = _normalize_fraction_parts(num, den)
    if den == 1:
        return int(num)
    return int(float(int(num)) / float(int(den)))


def _unscale_rational_parts(num: int, den: int, reciprocal_scale: float, delta: float) -> float:
    num, den = _normalize_fraction_parts(num, den)
    if den == 1:
        scaled = float(int(num))
    else:
        scaled = float(int(num)) / float(int(den))
    return scaled * reciprocal_scale + delta


def intersection_rows_from_pairs_no_fraction(
    pairs: np.ndarray,
    left,
    right,
    *,
    scale_bounds: tuple[float, float, float, float],
):
    pairs = np.asarray(pairs, dtype=np.uint32).reshape((-1, 2))
    left_index = pairs[:, 0].astype(np.int64, copy=False) - 1
    right_index = pairs[:, 1].astype(np.int64, copy=False) - 1

    lx0 = left.x0[left_index]
    ly0 = left.y0[left_index]
    lx1 = left.x1[left_index]
    ly1 = left.y1[left_index]
    rx0 = right.x0[right_index]
    ry0 = right.y0[right_index]
    rx1 = right.x1[right_index]
    ry1 = right.y1[right_index]

    rx_scale, ry_scale, deltax, deltay, rrx, rry, ddeltax, ddeltay = base._rayjoin_scaling_constants(scale_bounds)
    slx0 = base._scale_array(lx0, rx_scale, deltax)
    sly0 = base._scale_array(ly0, ry_scale, deltay)
    slx1 = base._scale_array(lx1, rx_scale, deltax)
    sly1 = base._scale_array(ly1, ry_scale, deltay)
    srx0 = base._scale_array(rx0, rx_scale, deltax)
    sry0 = base._scale_array(ry0, ry_scale, deltay)
    srx1 = base._scale_array(rx1, rx_scale, deltax)
    sry1 = base._scale_array(ry1, ry_scale, deltay)

    fallback_x, fallback_y = base._overlap_midpoint_fallback(lx0, ly0, lx1, ly1, rx0, ry0, rx1, ry1)
    fallback_sx = base._scale_array(fallback_x, rx_scale, deltax)
    fallback_sy = base._scale_array(fallback_y, ry_scale, deltay)

    rows = []
    for index in range(int(pairs.shape[0])):
        left_a = int(sly0[index]) - int(sly1[index])
        left_b = int(slx1[index]) - int(slx0[index])
        left_c = -int(slx0[index]) * left_a - int(sly0[index]) * left_b
        if left_b < 0:
            left_a = -left_a
            left_b = -left_b
            left_c = -left_c

        right_a = int(sry0[index]) - int(sry1[index])
        right_b = int(srx1[index]) - int(srx0[index])
        right_c = -int(srx0[index]) * right_a - int(sry0[index]) * right_b
        if right_b < 0:
            right_a = -right_a
            right_b = -right_b
            right_c = -right_c

        denom = left_a * right_b - right_a * left_b
        if denom == 0:
            sx = int(fallback_sx[index])
            sy = int(fallback_sy[index])
            rx_num, rx_den = sx, 1
            ry_num, ry_den = sy, 1
            world_x = sx * rrx + ddeltax
            world_y = sy * rry + ddeltay
        else:
            rx_num, rx_den = _normalize_fraction_parts(right_c * left_b - left_c * right_b, denom)
            ry_num, ry_den = _normalize_fraction_parts(right_a * left_c - left_a * right_c, denom)

            min_sx = min(int(srx0[index]), int(srx1[index]), int(slx0[index]), int(slx1[index]))
            max_sx = max(int(srx0[index]), int(srx1[index]), int(slx0[index]), int(slx1[index]))
            min_sy = min(int(sry0[index]), int(sry1[index]), int(sly0[index]), int(sly1[index]))
            max_sy = max(int(sry0[index]), int(sry1[index]), int(sly0[index]), int(sly1[index]))

            rx_num, rx_den = _clamp_rational_to_int_range(rx_num, rx_den, min_sx, max_sx)
            ry_num, ry_den = _clamp_rational_to_int_range(ry_num, ry_den, min_sy, max_sy)

            sx = _author_rational_parts_to_internal(rx_num, rx_den)
            sy = _author_rational_parts_to_internal(ry_num, ry_den)
            world_x = _unscale_rational_parts(rx_num, rx_den, rrx, ddeltax)
            world_y = _unscale_rational_parts(ry_num, ry_den, rry, ddeltay)

        row = base.OverlayIntersection(
            eid0=int(pairs[index, 0]) - 1,
            eid1=int(pairs[index, 1]) - 1,
            x=float(world_x),
            y=float(world_y),
            display_x=base._display_coordinate(sx * rrx + ddeltax),
            display_y=base._display_coordinate(sy * rry + ddeltay),
            scaled_x=float(sx),
            scaled_y=float(sy),
            scaled_x_rational=None,
            scaled_y_rational=None,
        )
        row._goal4924_scaled_x_num = int(rx_num)
        row._goal4924_scaled_x_den = int(rx_den)
        row._goal4924_scaled_y_num = int(ry_num)
        row._goal4924_scaled_y_den = int(ry_den)
        rows.append(row)
    return rows


def _distance_compare(row_a, row_b, start_sx: int, start_sy: int, tie_attr: str) -> int:
    ax_num = int(row_a._goal4924_scaled_x_num) - int(start_sx) * int(row_a._goal4924_scaled_x_den)
    ax_den = int(row_a._goal4924_scaled_x_den)
    ay_num = int(row_a._goal4924_scaled_y_num) - int(start_sy) * int(row_a._goal4924_scaled_y_den)
    ay_den = int(row_a._goal4924_scaled_y_den)

    bx_num = int(row_b._goal4924_scaled_x_num) - int(start_sx) * int(row_b._goal4924_scaled_x_den)
    bx_den = int(row_b._goal4924_scaled_x_den)
    by_num = int(row_b._goal4924_scaled_y_num) - int(start_sy) * int(row_b._goal4924_scaled_y_den)
    by_den = int(row_b._goal4924_scaled_y_den)

    left_value = (
        ax_num * ax_num * ay_den * ay_den * bx_den * bx_den * by_den * by_den
        + ay_num * ay_num * ax_den * ax_den * bx_den * bx_den * by_den * by_den
    )
    right_value = (
        bx_num * bx_num * by_den * by_den * ax_den * ax_den * ay_den * ay_den
        + by_num * by_num * bx_den * bx_den * ax_den * ax_den * ay_den * ay_den
    )
    if left_value < right_value:
        return -1
    if left_value > right_value:
        return 1
    tie_a = int(getattr(row_a, tie_attr))
    tie_b = int(getattr(row_b, tie_attr))
    return (tie_a > tie_b) - (tie_a < tie_b)


def sort_xsects_for_map_goal4924(
    xsects,
    dataset,
    map_index: int,
    scale_bounds: tuple[float, float, float, float],
):
    mode = os.environ.get("GOAL4924_SORT_MODE", "scaled_int").strip().lower()
    if mode not in {"scaled_int", "exact_cmp"}:
        raise ValueError(f"unsupported GOAL4924_SORT_MODE={mode!r}")

    edge_attr = "eid0" if map_index == 0 else "eid1"
    tie_attr = "eid1" if map_index == 0 else "eid0"
    grouped: dict[int, list[object]] = {}
    for xsect in xsects:
        grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)

    rx_scale, ry_scale, deltax, deltay, *_ = base._rayjoin_scaling_constants(scale_bounds)
    sorted_eids = sorted(grouped)
    eid_array = np.asarray(sorted_eids, dtype=np.int64)
    if eid_array.size:
        start_sx_values = base._scale_array(dataset.x0[eid_array], rx_scale, deltax)
        start_sy_values = base._scale_array(dataset.y0[eid_array], ry_scale, deltay)
    else:
        start_sx_values = np.empty(0, dtype=np.int64)
        start_sy_values = np.empty(0, dtype=np.int64)

    sorted_rows = []
    for offset, eid in enumerate(sorted_eids):
        group = grouped[eid]
        start_sx = int(start_sx_values[offset])
        start_sy = int(start_sy_values[offset])
        if mode == "scaled_int":
            group.sort(
                key=lambda row, _sx=start_sx, _sy=start_sy: (
                    (int(row.scaled_x) - _sx) * (int(row.scaled_x) - _sx)
                    + (int(row.scaled_y) - _sy) * (int(row.scaled_y) - _sy),
                    int(getattr(row, tie_attr)),
                )
            )
        else:
            group.sort(key=cmp_to_key(lambda a, b, _sx=start_sx, _sy=start_sy: _distance_compare(a, b, _sx, _sy, tie_attr)))
        sorted_rows.extend(group)
    return sorted_rows


def main() -> None:
    if "rtdsl.rayjoin_overlay" in sys.modules:
        raise RuntimeError("forbidden import detected before Goal4924 wrapper start")

    start = time.perf_counter()
    base.intersection_rows_from_pairs = intersection_rows_from_pairs_no_fraction
    base.sort_xsects_for_map = sort_xsects_for_map_goal4924
    wrapper.main()

    summary_path = None
    argv = sys.argv[1:]
    for index, value in enumerate(argv):
        if value == "--summary" and index + 1 < len(argv):
            summary_path = Path(argv[index + 1])
        elif value.startswith("--summary="):
            summary_path = Path(value.split("=", 1)[1])
    if summary_path is not None and summary_path.exists():
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        payload["schema"] = "rtdl.goal4924.columnar_reprojection_sort_probe.v1"
        payload.setdefault("claim_boundary", {})
        payload["claim_boundary"]["goal4924_internal_probe_only"] = True
        payload["claim_boundary"]["goal4924_rtdl_core_modified"] = False
        payload["claim_boundary"]["goal4924_sort_mode"] = os.environ.get("GOAL4924_SORT_MODE", "scaled_int").strip().lower()
        payload["phase_seconds"]["goal4924_wrapper_total_sec"] = time.perf_counter() - start
        phase = payload.get("phase_seconds", {})
        reproj_sort = (
            float(phase.get("intersection_reprojection_sec", 0.0))
            + float(phase.get("sort_map0_sec", 0.0))
            + float(phase.get("sort_map1_sec", 0.0))
        )
        payload["goal4924_result"] = {
            "reprojection_sort_sec": reproj_sort,
            "reprojection_sort_bar_sec": 0.45,
            "hot_body_bar_sec": 3.45,
            "byte_equal_required": True,
            "passes_reprojection_sort_bar": reproj_sort <= 0.45,
            "passes_hot_body_bar": float(payload.get("elapsed_sec", 999999.0)) <= 3.45,
            "passes_byte_equal_bar": bool(payload.get("byte_equal_to_author")),
        }
        summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
