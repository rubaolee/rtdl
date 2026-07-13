#!/usr/bin/env python3
"""Goal5013 probe: point-location locator prepare cost.

This probe asks whether the left-side point-location locator prepare cost in the
prepared-base / same-domain query-many route is a first-call artifact, a
per-input locator build floor, or something that existing prepared assets can
reuse away.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np


def _load_goal5012(repo: Path):
    path = repo / "history" / "internal_docs" / "goal5012_overlay_shared_point_query_probe.py"
    spec = importlib.util.spec_from_file_location("goal5012_overlay_shared_point_query_probe", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _compact_native(locator) -> dict[str, float | None]:
    native = locator.last_phase_timings() or {}
    extended = native.get("extended", {}) if isinstance(native, dict) else {}
    if not isinstance(extended, dict):
        extended = {}
    out: dict[str, float | None] = {
        "bvh": native.get("bvh") if isinstance(native, dict) else None,
        "trav": native.get("trav") if isinstance(native, dict) else None,
        "copy": native.get("copy") if isinstance(native, dict) else None,
    }
    for key, value in extended.items():
        if isinstance(value, (int, float)):
            out[key] = float(value)
    return out


def _prepare_locator_once(base, cdb_segments, bounds, *, query_map_id: int) -> dict[str, object]:
    locator = None
    start = time.perf_counter()
    try:
        locator = base.prepare_planar_map_point_location_2d_optix(
            cdb_segments,
            query_map_id=query_map_id,
            scale_bounds=bounds,
        )
        elapsed = time.perf_counter() - start
        return {
            "elapsed_sec": float(elapsed),
            "native_timings": _compact_native(locator),
        }
    finally:
        if locator is not None:
            locator.close()


def _pack_prefix_cdb_segments(base, dataset, count: int):
    count = int(max(1, min(count, int(dataset.seg_ids.shape[0]))))
    return base.pack_cdb_segments_from_arrays(
        dataset.seg_ids[:count],
        dataset.x0[:count],
        dataset.y0[:count],
        dataset.x1[:count],
        dataset.y1[:count],
        dataset.left_face_ids[:count],
        dataset.right_face_ids[:count],
    )


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return float((ordered[mid - 1] + ordered[mid]) / 2.0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeat", type=int, default=4)
    args = parser.parse_args()

    goal5012 = _load_goal5012(args.repo)
    app = goal5012._load_app(args.repo)
    base = app.base

    result: dict[str, object] = {
        "schema": "rtdl.goal5013.point_location_locator_prepare_probe.v1",
        "left": str(args.left),
        "right": str(args.right),
        "repeat": int(args.repeat),
        "question": "can_prepare_left_point_location_locator_be_reused_or_prepared_away_generically",
    }

    load_start = time.perf_counter()
    left = base.load_dataset_arrays(args.left)
    right = base.load_dataset_arrays(args.right)
    bounds = base.shared_bounds(left, right)
    result["load_dataset_arrays_sec"] = float(time.perf_counter() - load_start)
    result["shared_bounds"] = [float(value) for value in bounds]
    result["input_counts"] = {
        "left_segments": int(left.seg_ids.shape[0]),
        "right_segments": int(right.seg_ids.shape[0]),
        "left_points": int(left.point_count),
        "right_points": int(right.point_count),
    }

    variants = []
    for batch_id in (1, 2, 3):
        variant, changed_points = goal5012._make_distinct_dataset_variant(app, left, batch_id=batch_id)
        variants.append((batch_id, variant, changed_points))

    same_variant_rows = []
    for index in range(int(args.repeat)):
        row = _prepare_locator_once(base, variants[0][1].cdb_segments, bounds, query_map_id=1)
        row["iteration"] = int(index + 1)
        same_variant_rows.append(row)
    result["same_variant_reprepare_rows"] = same_variant_rows

    distinct_rows = []
    for batch_id, variant, changed_points in variants:
        row = _prepare_locator_once(base, variant.cdb_segments, bounds, query_map_id=1)
        row["batch_id"] = int(batch_id)
        row["changed_point_count"] = int(len(changed_points))
        distinct_rows.append(row)
    result["distinct_same_domain_prepare_rows"] = distinct_rows

    scaling_rows = []
    total_segments = int(left.seg_ids.shape[0])
    for fraction in (0.125, 0.25, 0.5, 1.0):
        count = max(1, int(round(total_segments * fraction)))
        cdb_segments = _pack_prefix_cdb_segments(base, left, count)
        repeats = []
        for iteration in range(2):
            row = _prepare_locator_once(base, cdb_segments, bounds, query_map_id=1)
            row["iteration"] = int(iteration + 1)
            repeats.append(row)
        scaling_rows.append(
            {
                "fraction": float(fraction),
                "segment_count": int(count),
                "rows": repeats,
                "median_elapsed_sec": _median([float(row["elapsed_sec"]) for row in repeats]),
            }
        )
    result["segment_count_scaling_rows"] = scaling_rows

    same_times = [float(row["elapsed_sec"]) for row in same_variant_rows]
    distinct_times = [float(row["elapsed_sec"]) for row in distinct_rows]
    result["derived"] = {
        "same_variant_first_sec": same_times[0] if same_times else None,
        "same_variant_after_first_median_sec": _median(same_times[1:]),
        "distinct_same_domain_median_sec": _median(distinct_times),
        "full_size_prefix_median_sec": scaling_rows[-1]["median_elapsed_sec"] if scaling_rows else None,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
