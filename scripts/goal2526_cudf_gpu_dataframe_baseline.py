from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import statistics
import time
from typing import Any


GOAL = "goal2526_cudf_gpu_dataframe_baseline"
CLAIM_BOUNDARY = (
    "cuDF is used as a lightweight GPU dataframe baseline for the tiny RayDB-style "
    "synthetic fixture only. Timings are diagnostic and do not authorize public speedup, "
    "whole-DBMS, authors-code, RayDB reproduction, true zero-copy, or SQL-engine claims."
)


def make_fixture() -> dict[str, Any]:
    return {
        "row_ids": (1, 2, 3, 4, 5, 6, 7, 8),
        "columns": {
            "region_id": (0, 1, 0, 1, 2, 2, 1, 0),
            "ship_year": (1994, 1994, 1995, 1996, 1994, 1995, 1995, 1994),
            "discount": (5, 6, 3, 5, 7, 4, 5, 6),
            "quantity": (10, 20, 15, 9, 30, 18, 28, 12),
            "revenue": (100, 200, 150, 50, 300, 80, 120, 90),
        },
    }


def expected_rows() -> dict[str, list[dict[str, int]]]:
    grouped: dict[int, list[int]] = {}
    fixture = make_fixture()
    columns = fixture["columns"]
    for index in range(len(fixture["row_ids"])):
        if not (1994 <= int(columns["ship_year"][index]) <= 1995):
            continue
        if not (4 <= int(columns["discount"][index]) <= 6):
            continue
        if not (int(columns["quantity"][index]) < 25):
            continue
        grouped.setdefault(int(columns["region_id"][index]), []).append(int(columns["revenue"][index]))
    return {
        "count": [{"region_id": region_id, "count": len(values)} for region_id, values in sorted(grouped.items())],
        "sum": [{"region_id": region_id, "sum": sum(values)} for region_id, values in sorted(grouped.items())],
        "min": [{"region_id": region_id, "min": min(values)} for region_id, values in sorted(grouped.items())],
        "max": [{"region_id": region_id, "max": max(values)} for region_id, values in sorted(grouped.items())],
        "avg_as_sum_count": [
            {"region_id": region_id, "sum": sum(values), "count": len(values)}
            for region_id, values in sorted(grouped.items())
        ],
    }


def run_baseline(*, repeats: int = 500) -> dict[str, Any]:
    if repeats < 1:
        raise ValueError("repeats must be >= 1")
    try:
        cudf = importlib.import_module("cudf")
        cupy = importlib.import_module("cupy")
    except ImportError as exc:
        return {
            "goal": GOAL,
            "status": "blocked",
            "app": "raydb_style_columnar_aggregate",
            "blocked_reason": f"cuDF/CuPy package is unavailable: {exc}",
            "cudf_available": False,
            "performance_claim_authorized": False,
            "claim_boundary": CLAIM_BOUNDARY,
        }

    dataframe = _make_cudf_dataframe(cudf)
    expected = expected_rows()

    # Warm up CUDA context and cuDF kernels before recording diagnostic samples.
    for _ in range(5):
        _run_cudf_contract(dataframe)
        cupy.cuda.get_current_stream().synchronize()

    device_sync_samples_ms: list[float] = []
    host_rows_samples_ms: list[float] = []
    end_to_end_samples_ms: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        grouped = _run_cudf_grouped(dataframe)
        cupy.cuda.get_current_stream().synchronize()
        device_sync_ms = (time.perf_counter_ns() - start) / 1_000_000.0
        device_sync_samples_ms.append(device_sync_ms)

        start = time.perf_counter_ns()
        _rows_from_grouped(grouped)
        cupy.cuda.get_current_stream().synchronize()
        host_rows_ms = (time.perf_counter_ns() - start) / 1_000_000.0
        host_rows_samples_ms.append(host_rows_ms)
        end_to_end_samples_ms.append(device_sync_ms + host_rows_ms)

    correctness_rows = _run_cudf_contract(dataframe)
    device_stats = _stats(device_sync_samples_ms)
    host_rows_stats = _stats(host_rows_samples_ms)
    end_to_end_stats = _stats(end_to_end_samples_ms)
    return {
        "goal": GOAL,
        "status": "ok",
        "app": "raydb_style_columnar_aggregate",
        "repeats": repeats,
        "query_contract": "cudf_filter_groupby_count_sum_min_max_sum_count",
        "input_boundary": "fixture loaded once into a cuDF GPU DataFrame before timed loops",
        "output_boundary": "device_sync excludes host row materialization; host_rows measures conversion of compact grouped output",
        "cudf_version": cudf.__version__,
        "cupy_version": cupy.__version__,
        "cudf_available": True,
        "expected_cpu_reference_rows": expected,
        "cudf_rows": correctness_rows,
        "matches_cpu_reference_by_mode": {
            mode: correctness_rows.get(mode) == expected[mode] for mode in expected
        },
        "all_match_cpu_reference": correctness_rows == expected,
        "cudf_device_sync_timing_ms": device_stats,
        "cudf_host_rows_timing_ms": host_rows_stats,
        "cudf_end_to_end_timing_ms": end_to_end_stats,
        "performance_claim_authorized": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _make_cudf_dataframe(cudf: Any) -> Any:
    fixture = make_fixture()
    columns = fixture["columns"]
    return cudf.DataFrame(
        {
            "row_id": list(fixture["row_ids"]),
            "region_id": list(columns["region_id"]),
            "ship_year": list(columns["ship_year"]),
            "discount": list(columns["discount"]),
            "quantity": list(columns["quantity"]),
            "revenue": list(columns["revenue"]),
        }
    )


def _run_cudf_contract(dataframe: Any) -> dict[str, list[dict[str, int]]]:
    grouped = _run_cudf_grouped(dataframe)
    return _rows_from_grouped(grouped)


def _run_cudf_grouped(dataframe: Any) -> Any:
    filtered = dataframe[
        (dataframe["ship_year"] >= 1994)
        & (dataframe["ship_year"] <= 1995)
        & (dataframe["discount"] >= 4)
        & (dataframe["discount"] <= 6)
        & (dataframe["quantity"] < 25)
    ]
    return (
        filtered.groupby("region_id")
        .agg({"revenue": ["count", "sum", "min", "max"]})
        .sort_index()
    )


def _rows_from_grouped(grouped: Any) -> dict[str, list[dict[str, int]]]:
    pandas_frame = grouped.to_pandas()
    rows: list[tuple[int, int, int, int, int]] = []
    for region_id, row in pandas_frame.iterrows():
        rows.append(
            (
                int(region_id),
                int(row[("revenue", "count")]),
                int(row[("revenue", "sum")]),
                int(row[("revenue", "min")]),
                int(row[("revenue", "max")]),
            )
        )
    return {
        "count": [{"region_id": region_id, "count": count} for region_id, count, _sum, _min, _max in rows],
        "sum": [{"region_id": region_id, "sum": sum_value} for region_id, _count, sum_value, _min, _max in rows],
        "min": [{"region_id": region_id, "min": min_value} for region_id, _count, _sum, min_value, _max in rows],
        "max": [{"region_id": region_id, "max": max_value} for region_id, _count, _sum, _min, max_value in rows],
        "avg_as_sum_count": [
            {"region_id": region_id, "sum": sum_value, "count": count}
            for region_id, count, sum_value, _min, _max in rows
        ],
    }


def _stats(samples: list[float]) -> dict[str, Any]:
    return {
        "median": statistics.median(samples),
        "min": min(samples),
        "max": max(samples),
        "mean": statistics.fmean(samples),
        "samples": samples,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Goal2526 cuDF GPU dataframe baseline.")
    parser.add_argument("--repeats", type=int, default=500)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    payload = run_baseline(repeats=args.repeats)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] in {"ok", "blocked"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
