from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.librts_spatial_index import (  # noqa: E402
    rtdl_librts_spatial_index_benchmark_app as librts_app,
)
import rtdsl as rt  # noqa: E402


GOAL2798_HARNESS_VERSION = "rtdl.goal2798.librts_v2_5_warm_median_harness.v1"
CLAIM_BOUNDARY = {
    "canonical_harness": True,
    "tier_c_no_regression_harness": True,
    "public_speedup_claim_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "triton_speedup_claim_authorized": False,
    "true_zero_copy_claim_authorized": False,
    "paper_reproduction_claim_authorized": False,
    "native_engine_customization": False,
}


def _check_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _run_metadata() -> dict[str, Any]:
    return {
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
    }


def run_goal2798_librts_warm_median_harness(
    *,
    box_count: int,
    query_count: int,
    seed: int,
    warmup: int = 3,
    repeat: int = 9,
    operations: tuple[str, ...] = librts_app.OPERATIONS,
) -> dict[str, Any]:
    started = time.perf_counter()
    fixture = librts_app.make_uniform_fixture(
        box_count=int(box_count),
        query_count=int(query_count),
        seed=int(seed),
    )
    cpu_started = time.perf_counter()
    cpu_counts = librts_app.run_counts(fixture, "all")["counts"]
    cpu_sec = time.perf_counter() - cpu_started

    prepare_started = time.perf_counter()
    prepared = rt.prepare_optix_aabb_index_2d(fixture.boxes)
    scene_prepare_sec = time.perf_counter() - prepare_started
    point_queries = None
    box_queries = None
    point_query_prepare_sec = 0.0
    box_query_prepare_sec = 0.0
    rows: list[dict[str, Any]] = []
    try:
        if "point_contains" in operations:
            started = time.perf_counter()
            point_queries = rt.prepare_optix_aabb_point_queries_2d(fixture.point_queries)
            point_query_prepare_sec = time.perf_counter() - started
        if any(operation in {"range_contains", "range_intersects"} for operation in operations):
            started = time.perf_counter()
            box_queries = rt.prepare_optix_aabb_box_queries_2d(fixture.box_queries)
            box_query_prepare_sec = time.perf_counter() - started

        for operation in operations:
            query_handle = point_queries if operation == "point_contains" else box_queries
            if query_handle is None:
                raise ValueError(f"missing prepared query handle for {operation}")
            observed_count, timings = _time_prepared_query(
                prepared,
                query_handle,
                operation=operation,
                warmup=int(warmup),
                repeat=int(repeat),
            )
            expected_count = int(cpu_counts[operation])
            rows.append(
                {
                    "operation": operation,
                    "status": "pass" if int(observed_count) == expected_count else "mismatch",
                    "expected_count": expected_count,
                    "observed_count": int(observed_count),
                    "matches_cpu_reference": int(observed_count) == expected_count,
                    "warmup": int(warmup),
                    "repeat": int(repeat),
                    "query_median_ms": statistics.median(timings) * 1000.0,
                    "query_min_ms": min(timings) * 1000.0,
                    "query_max_ms": max(timings) * 1000.0,
                    "query_times_ms": tuple(value * 1000.0 for value in timings),
                    "rt_core_accelerated": True,
                    "generic_primitive": "AABB_INDEX_QUERY_2D",
                    "primitive_contract": "generic_prepared_aabb_index_query_2d",
                }
            )
    finally:
        for handle in (point_queries, box_queries):
            if handle is not None:
                handle.close()
        prepared.close()

    status = "pass" if rows and all(row["status"] == "pass" for row in rows) else "fail"
    return {
        "goal": "Goal2798",
        "harness_version": GOAL2798_HARNESS_VERSION,
        "status": status,
        "app": "librts_spatial_index",
        "fixture": fixture.metadata(),
        "box_count": int(box_count),
        "query_count": int(query_count),
        "seed": int(seed),
        "operations": tuple(operations),
        "backend": "optix",
        "generic_primitive": "AABB_INDEX_QUERY_2D",
        "scene_prepare_sec": scene_prepare_sec,
        "point_query_prepare_sec": point_query_prepare_sec,
        "box_query_prepare_sec": box_query_prepare_sec,
        "cpu_reference_sec": cpu_sec,
        "cpu_counts": cpu_counts,
        "rows": tuple(rows),
        "row_count": len(rows),
        "elapsed_sec": time.perf_counter() - started,
        **_run_metadata(),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _time_prepared_query(
    prepared: Any,
    query_handle: Any,
    *,
    operation: str,
    warmup: int,
    repeat: int,
) -> tuple[int, tuple[float, ...]]:
    if repeat < 1:
        raise ValueError("repeat must be positive")
    last_count = 0
    for _ in range(max(0, warmup)):
        last_count = int(prepared.count_prepared_queries(query_handle, operation=operation))
    timings: list[float] = []
    for _ in range(repeat):
        started = time.perf_counter()
        last_count = int(prepared.count_prepared_queries(query_handle, operation=operation))
        timings.append(time.perf_counter() - started)
    return last_count, tuple(timings)


def _parse_csv_strings(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal2798 LibRTS v2.5 warm median OptiX harness.")
    parser.add_argument("--box-count", type=int, default=4096)
    parser.add_argument("--query-count", type=int, default=2048)
    parser.add_argument("--seed", type=int, default=2798)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--repeat", type=int, default=9)
    parser.add_argument("--operations", default=",".join(librts_app.OPERATIONS))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    payload = run_goal2798_librts_warm_median_harness(
        box_count=args.box_count,
        query_count=args.query_count,
        seed=args.seed,
        warmup=args.warmup,
        repeat=args.repeat,
        operations=_parse_csv_strings(args.operations),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
