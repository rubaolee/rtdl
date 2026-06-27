#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import rtdsl as rt
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference
from goal15_compare_embree import build_lsi_dataset
from goal15_compare_embree import build_pip_dataset
from goal15_compare_embree import compare_goal15


def _time_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def _median_repeat(fn, *, repeats: int) -> float:
    timings = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        timings.append(time.perf_counter() - start)
    return statistics.median(timings)


def _median_repeat_raw_dict(fn, *, repeats: int) -> float:
    timings = []
    for _ in range(repeats):
        start = time.perf_counter()
        rows = fn()
        try:
            rows.to_dict_rows()
        finally:
            rows.close()
        timings.append(time.perf_counter() - start)
    return statistics.median(timings)


def _pack_lsi(left, right):
    left_packed = rt.pack_segments(records=left)
    right_packed = rt.pack_segments(records=right)
    return left_packed, right_packed


def _pack_pip(points, polygons):
    points_packed = rt.pack_points(records=points)
    ids = [polygon.id for polygon in polygons]
    offsets = []
    counts = []
    vertices_xy = []
    offset = 0
    for polygon in polygons:
        offsets.append(offset)
        counts.append(len(polygon.vertices))
        for x, y in polygon.vertices:
            vertices_xy.extend((x, y))
        offset += len(polygon.vertices)
    polygons_packed = rt.pack_polygons(
        ids=ids,
        vertex_offsets=offsets,
        vertex_counts=counts,
        vertices_xy=vertices_xy,
    )
    return points_packed, polygons_packed


def compare_goal17(output_dir: Path | None = None, repeats: int = 25) -> dict[str, object]:
    out = Path(output_dir or ROOT / "build" / "goal17_compare")
    out.mkdir(parents=True, exist_ok=True)

    goal15_payload = compare_goal15(out / "goal15_native_baseline")
    results: dict[str, object] = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repeats": repeats,
        "workloads": {},
    }

    left, right = build_lsi_dataset(build_count=200, probe_count=120, distribution="uniform")
    current_rows, current_sec = _time_call(rt.run_embree, county_zip_join_reference, left=left, right=right)
    prepared_kernel, prepare_kernel_sec = _time_call(rt.prepare_embree, county_zip_join_reference)
    packed_inputs, pack_inputs_sec = _time_call(_pack_lsi, left, right)
    prepared_execution, bind_sec = _time_call(prepared_kernel.bind, left=packed_inputs[0], right=packed_inputs[1])
    prepared_rows, prepared_first_run_sec = _time_call(prepared_execution.run)
    prepared_hot_median_sec = _median_repeat(prepared_execution.run, repeats=repeats)
    prepared_raw_hot_median_sec = _median_repeat(prepared_execution.run_raw, repeats=repeats)
    prepared_raw_dict_hot_median_sec = _median_repeat_raw_dict(prepared_execution.run_raw, repeats=repeats)
    results["workloads"]["lsi"] = {
        "current_pair_count": len(current_rows),
        "prepared_pair_count": len(prepared_rows),
        "prepared_matches_current": current_rows == prepared_rows,
        "current_rtdl_embree_total_sec": current_sec,
        "prepare_kernel_sec": prepare_kernel_sec,
        "pack_inputs_sec": pack_inputs_sec,
        "bind_sec": bind_sec,
        "prepared_first_run_sec": prepared_first_run_sec,
        "prepared_hot_median_sec": prepared_hot_median_sec,
        "prepared_raw_hot_median_sec": prepared_raw_hot_median_sec,
        "prepared_raw_dict_hot_median_sec": prepared_raw_dict_hot_median_sec,
        "speedup_vs_current_hot": current_sec / prepared_hot_median_sec if prepared_hot_median_sec > 0 else None,
        "speedup_vs_current_raw_hot": current_sec / prepared_raw_hot_median_sec if prepared_raw_hot_median_sec > 0 else None,
        "gap_to_goal15_native_hot": prepared_hot_median_sec / goal15_payload["workloads"]["lsi"]["native_total_sec"],
        "gap_to_goal15_native_raw_hot": prepared_raw_hot_median_sec / goal15_payload["workloads"]["lsi"]["native_total_sec"],
        "goal15_native_total_sec": goal15_payload["workloads"]["lsi"]["native_total_sec"],
    }

    points, polygons = build_pip_dataset(build_count=200, probe_count=120, distribution="uniform")
    current_rows, current_sec = _time_call(rt.run_embree, point_in_counties_reference, points=points, polygons=polygons)
    prepared_kernel, prepare_kernel_sec = _time_call(rt.prepare_embree, point_in_counties_reference)
    packed_inputs, pack_inputs_sec = _time_call(_pack_pip, points, polygons)
    prepared_execution, bind_sec = _time_call(prepared_kernel.bind, points=packed_inputs[0], polygons=packed_inputs[1])
    prepared_rows, prepared_first_run_sec = _time_call(prepared_execution.run)
    prepared_hot_median_sec = _median_repeat(prepared_execution.run, repeats=repeats)
    prepared_raw_hot_median_sec = _median_repeat(prepared_execution.run_raw, repeats=repeats)
    prepared_raw_dict_hot_median_sec = _median_repeat_raw_dict(prepared_execution.run_raw, repeats=repeats)
    results["workloads"]["pip"] = {
        "current_pair_count": len(current_rows),
        "prepared_pair_count": len(prepared_rows),
        "prepared_matches_current": current_rows == prepared_rows,
        "current_rtdl_embree_total_sec": current_sec,
        "prepare_kernel_sec": prepare_kernel_sec,
        "pack_inputs_sec": pack_inputs_sec,
        "bind_sec": bind_sec,
        "prepared_first_run_sec": prepared_first_run_sec,
        "prepared_hot_median_sec": prepared_hot_median_sec,
        "prepared_raw_hot_median_sec": prepared_raw_hot_median_sec,
        "prepared_raw_dict_hot_median_sec": prepared_raw_dict_hot_median_sec,
        "speedup_vs_current_hot": current_sec / prepared_hot_median_sec if prepared_hot_median_sec > 0 else None,
        "speedup_vs_current_raw_hot": current_sec / prepared_raw_hot_median_sec if prepared_raw_hot_median_sec > 0 else None,
        "gap_to_goal15_native_hot": prepared_hot_median_sec / goal15_payload["workloads"]["pip"]["native_total_sec"],
        "gap_to_goal15_native_raw_hot": prepared_raw_hot_median_sec / goal15_payload["workloads"]["pip"]["native_total_sec"],
        "goal15_native_total_sec": goal15_payload["workloads"]["pip"]["native_total_sec"],
    }

    report_path = out / "goal17_compare.json"
    report_path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    return results


def main() -> int:
    payload = compare_goal17()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
