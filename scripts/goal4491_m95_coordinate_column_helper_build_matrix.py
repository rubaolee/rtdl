from __future__ import annotations

import json
from pathlib import Path
import statistics
import subprocess
import time

import cupy

from examples.current.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    make_rt_dbscan_points,
)

import rtdsl as rt


POINT_COUNT = 1_048_576
REPEAT = 3
BASELINE_JSON = Path("docs/reports/goal4490_v3_0_m94_rtdbscan_point_column_app_mode_2026-06-17.json")
OUT_JSON = Path("docs/reports/goal4491_v3_0_m95_coordinate_column_helper_build_2026-06-17.json")
OUT_JSONL = Path("docs/reports/goal4491_v3_0_m95_coordinate_column_helper_build_2026-06-17.jsonl")


def _gpu_info() -> str:
    try:
        return subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,pci.bus_id",
                "--format=csv,noheader",
            ],
            text=True,
        ).strip()
    except Exception as exc:  # pragma: no cover - pod evidence helper
        return f"unavailable: {exc}"


def _baseline_build_times() -> dict[str, float]:
    packet = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
    baseline: dict[str, float] = {}
    for row in packet["comparisons"]:
        if row["protocol"] == "one_shot":
            baseline[str(row["dataset"])] = float(row["column_coordinate_build_sec"])
    return baseline


def _case(dataset: str, baseline_build_sec: float) -> dict[str, object]:
    points = make_rt_dbscan_points(dataset, point_count=POINT_COUNT, seed=20260519)
    times: list[float] = []
    for _iteration in range(REPEAT):
        start = time.perf_counter()
        columns = rt.point_rows_to_partner_coordinate_columns_3d(points, partner="cupy")
        cupy.cuda.get_current_stream().synchronize()
        times.append(time.perf_counter() - start)
        del columns
        cupy.get_default_memory_pool().free_all_blocks()
    median_sec = float(statistics.median(times))
    return {
        "status": "ok",
        "dataset": dataset,
        "point_count": POINT_COUNT,
        "repeat": REPEAT,
        "baseline_goal4490_one_shot_coordinate_build_sec": float(baseline_build_sec),
        "optimized_coordinate_build_times_sec": times,
        "optimized_coordinate_build_median_sec": median_sec,
        "build_speedup_vs_goal4490": (
            float(baseline_build_sec) / median_sec if median_sec > 0.0 else None
        ),
        "optimization": "remove_redundant_all_hasattr_prescan_and_support_mapping_sequence_rows",
        "claim_boundary": "coordinate-column build only; does not promote app-constructed columns as a default route",
    }


def run_matrix() -> dict[str, object]:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSONL.write_text("", encoding="utf-8")
    baseline = _baseline_build_times()
    rows: list[dict[str, object]] = []
    for dataset in ("clustered3d", "road3d", "ngsim_dense"):
        start = time.perf_counter()
        try:
            row = _case(dataset, baseline[dataset])
            row["wall_sec"] = time.perf_counter() - start
        except Exception as exc:  # pragma: no cover - pod evidence helper
            row = {
                "status": "error",
                "dataset": dataset,
                "point_count": POINT_COUNT,
                "error": repr(exc),
                "wall_sec": time.perf_counter() - start,
            }
        rows.append(row)
        with OUT_JSONL.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        print(
            json.dumps(
                {
                    "dataset": dataset,
                    "status": row["status"],
                    "median_sec": row.get("optimized_coordinate_build_median_sec"),
                    "speedup": row.get("build_speedup_vs_goal4490"),
                },
                sort_keys=True,
            ),
            flush=True,
        )
    ok_rows = [row for row in rows if row["status"] == "ok"]
    packet = {
        "version": "rtdl.v3_0.coordinate_column_helper_build.goal4491.v1",
        "goal": "Goal4491 / V3 M95",
        "point_count": POINT_COUNT,
        "repeat": REPEAT,
        "case_count": len(rows),
        "ok_count": len(ok_rows),
        "error_count": len(rows) - len(ok_rows),
        "hardware": _gpu_info(),
        "baseline": str(BASELINE_JSON),
        "summary": {
            "min_speedup": min(float(row["build_speedup_vs_goal4490"]) for row in ok_rows),
            "max_speedup": max(float(row["build_speedup_vs_goal4490"]) for row in ok_rows),
            "speedups": {
                row["dataset"]: row["build_speedup_vs_goal4490"]
                for row in ok_rows
            },
        },
        "claim_boundary": (
            "This is a coordinate-column build micro-matrix only. It removes avoidable "
            "host scanning, but it does not make app-constructed columns a default route."
        ),
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(packet["summary"], indent=2, sort_keys=True), flush=True)
    return packet


if __name__ == "__main__":
    run_matrix()
