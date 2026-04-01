#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import rtdsl as rt
from examples.rtdl_goal10_reference import point_nearest_segment_reference
from examples.rtdl_goal10_reference import segment_polygon_hitcount_reference
from examples.rtdl_language_reference import county_soil_overlay_reference
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference
from examples.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference
from goal15_compare_embree import compare_goal15
from rtdsl.baseline_runner import load_representative_case


WORKLOADS = {
    "lsi": (county_zip_join_reference, "authored_lsi_minimal"),
    "pip": (point_in_counties_reference, "authored_pip_minimal"),
    "overlay": (county_soil_overlay_reference, "authored_overlay_minimal"),
    "ray_tri_hitcount": (ray_triangle_hitcount_reference, "authored_ray_tri_minimal"),
    "segment_polygon_hitcount": (segment_polygon_hitcount_reference, "authored_segment_polygon_minimal"),
    "point_nearest_segment": (point_nearest_segment_reference, "authored_point_nearest_segment_minimal"),
}

NATIVE_BASELINE_WORKLOADS = {"lsi", "pip"}


def _median_repeat(fn, *, repeats: int) -> float:
    timings = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        timings.append(time.perf_counter() - start)
    return statistics.median(timings)


def _run_and_close_raw(kernel, inputs) -> tuple[tuple[dict[str, object], ...], float]:
    start = time.perf_counter()
    rows = rt.run_embree(kernel, result_mode="raw", **inputs)
    try:
        payload = rows.to_dict_rows()
    finally:
        rows.close()
    return payload, time.perf_counter() - start


def _prepared_raw_hot(prepared, inputs, *, repeats: int) -> float:
    execution = prepared.bind(**inputs)

    def _one_run():
        rows = execution.run_raw()
        rows.close()

    return _median_repeat(_one_run, repeats=repeats)


def _prepared_dict_hot(prepared, inputs, *, repeats: int) -> float:
    execution = prepared.bind(**inputs)
    return _median_repeat(execution.run, repeats=repeats)


def compare_goal18(output_dir: Path | None = None, repeats: int = 25) -> dict[str, object]:
    out = Path(output_dir or ROOT / "build" / "goal18_compare")
    out.mkdir(parents=True, exist_ok=True)

    goal15_payload = compare_goal15(out / "goal15_native_baseline")
    results: dict[str, object] = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repeats": repeats,
        "workloads": {},
    }

    for workload, (kernel, dataset) in WORKLOADS.items():
        case = load_representative_case(workload, dataset)
        prepared = rt.prepare_embree(kernel)

        dict_rows_start = time.perf_counter()
        dict_rows = rt.run_embree(kernel, **case.inputs)
        dict_sec = time.perf_counter() - dict_rows_start

        raw_rows, raw_sec = _run_and_close_raw(kernel, case.inputs)
        prepared_dict_hot = _prepared_dict_hot(prepared, case.inputs, repeats=repeats)
        prepared_raw_hot = _prepared_raw_hot(prepared, case.inputs, repeats=repeats)

        payload = {
            "dataset": dataset,
            "row_count": len(dict_rows),
            "raw_matches_dict": raw_rows == dict_rows,
            "current_dict_total_sec": dict_sec,
            "run_embree_raw_total_sec": raw_sec,
            "prepared_dict_hot_median_sec": prepared_dict_hot,
            "prepared_raw_hot_median_sec": prepared_raw_hot,
            "speedup_raw_vs_current": (dict_sec / raw_sec) if raw_sec > 0 else None,
            "speedup_prepared_raw_vs_current": (dict_sec / prepared_raw_hot) if prepared_raw_hot > 0 else None,
        }
        if workload in NATIVE_BASELINE_WORKLOADS:
            native_sec = goal15_payload["workloads"][workload]["native_total_sec"]
            payload["goal15_native_total_sec"] = native_sec
            payload["gap_raw_vs_native"] = raw_sec / native_sec if native_sec > 0 else None
            payload["gap_prepared_raw_vs_native"] = prepared_raw_hot / native_sec if native_sec > 0 else None
        results["workloads"][workload] = payload

    (out / "goal18_compare.json").write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    return results


def format_goal18_report(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 18 Report: Low-Overhead Runtime Continuation",
        "",
        "## Scope",
        "",
        "Goal 18 continues the Goal 17 low-overhead Embree work.",
        "",
        "This slice makes `run_embree(..., result_mode=\"raw\")` a first-class path and extends the prepared/raw runtime across the currently supported local Embree workloads.",
        "",
        "## Result Summary",
        "",
    ]
    for workload, stats in payload["workloads"].items():
        lines.extend([
            f"### {workload}",
            "",
            f"- dataset: `{stats['dataset']}`",
            f"- row count: `{stats['row_count']}`",
            f"- raw matches dict: `{stats['raw_matches_dict']}`",
            f"- current dict total: `{stats['current_dict_total_sec']:.9f} s`",
            f"- first-class raw total: `{stats['run_embree_raw_total_sec']:.9f} s`",
            f"- prepared dict hot median: `{stats['prepared_dict_hot_median_sec']:.9f} s`",
            f"- prepared raw hot median: `{stats['prepared_raw_hot_median_sec']:.9f} s`",
            f"- raw speedup vs current dict: `{stats['speedup_raw_vs_current']:.2f}x`",
            f"- prepared raw speedup vs current dict: `{stats['speedup_prepared_raw_vs_current']:.2f}x`",
        ])
        if "goal15_native_total_sec" in stats:
            lines.extend([
                f"- Goal 15 native lower-bound: `{stats['goal15_native_total_sec']:.9f} s`",
                f"- raw gap vs native lower-bound: `{stats['gap_raw_vs_native']:.2f}x`",
                f"- prepared raw gap vs native lower-bound: `{stats['gap_prepared_raw_vs_native']:.2f}x`",
            ])
        lines.append("")

    lines.extend([
        "## Interpretation",
        "",
        "Goal 18 does not change the DSL surface. The gain comes from making the low-overhead data path directly available from `run_embree(...)` and from extending packed/prepared execution beyond the original Goal 17 pair.",
        "",
        "Native-comparison numbers are only reported for `lsi` and `pip`, because those are the only workloads with the Goal 15 native C++ comparison baseline.",
        "",
        "## Main Files",
        "",
        "- [embree_runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py)",
        "- [__init__.py](/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py)",
        "- [goal18_compare_result_modes.py](/Users/rl2025/rtdl_python_only/scripts/goal18_compare_result_modes.py)",
        "- [goal18_result_mode_test.py](/Users/rl2025/rtdl_python_only/tests/goal18_result_mode_test.py)",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    out = ROOT / "build" / "goal18_compare"
    payload = compare_goal18(out)
    report = format_goal18_report(payload)
    report_path = ROOT / "docs" / "reports" / "goal18_low_overhead_runtime_continuation_2026-04-01.md"
    report_path.write_text(report, encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
