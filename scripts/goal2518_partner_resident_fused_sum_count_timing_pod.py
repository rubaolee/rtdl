#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable


def _run_text(command: list[str]) -> str:
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return (result.stdout + result.stderr).strip()


def _stats(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {
        "min": ordered[0],
        "median": statistics.median(ordered),
        "mean": statistics.fmean(ordered),
        "max": ordered[-1],
    }


def _canonical(rows: tuple[dict[str, object], ...]) -> list[tuple[int, int, int]]:
    return sorted((int(row["region_id"]), int(row["sum"]), int(row["count"])) for row in rows)


def _time_cuda_call(torch, fn: Callable[[], tuple[dict[str, object], ...]], *, warmup: int, iterations: int):
    for _ in range(warmup):
        fn()
    torch.cuda.synchronize()
    timings: list[float] = []
    last_rows: tuple[dict[str, object], ...] = ()
    for _ in range(iterations):
        torch.cuda.synchronize()
        start = time.perf_counter()
        last_rows = fn()
        torch.cuda.synchronize()
        timings.append(time.perf_counter() - start)
    return last_rows, timings


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo / "src"))
    sys.path.insert(0, str(repo))

    import rtdsl as rt

    output_path = repo / "docs/reports/goal2518_partner_resident_fused_sum_count_timing_pod_2026-05-23.json"
    payload: dict[str, object] = {
        "goal": "Goal2518 partner-resident fused sum_count timing",
        "python": sys.version,
        "platform": platform.platform(),
        "git_head": _run_text(["git", "-C", str(repo), "rev-parse", "HEAD"]),
        "rtdl_optix_lib": os.environ.get("RTDL_OPTIX_LIB", ""),
        "ld_library_path": os.environ.get("LD_LIBRARY_PATH", ""),
        "claim_boundary": (
            "Internal timing evidence for one synthetic partner-resident grouped aggregate path. "
            "No public speedup, SQL, DBMS, whole-app, true zero-copy, or authors-code claim is authorized."
        ),
    }
    try:
        import torch
    except Exception as exc:
        payload.update({"status": "blocked", "blocked_reason": f"torch import failed: {exc}"})
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return 2
    if not torch.cuda.is_available():
        payload.update({"status": "blocked", "blocked_reason": "CUDA is not available"})
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return 2

    row_count = int(os.environ.get("RTDL_GOAL2518_ROW_COUNT", "200000"))
    group_capacity = int(os.environ.get("RTDL_GOAL2518_GROUP_CAPACITY", "1024"))
    warmup = int(os.environ.get("RTDL_GOAL2518_WARMUP", "5"))
    iterations = int(os.environ.get("RTDL_GOAL2518_ITERATIONS", "30"))
    if row_count <= 0 or group_capacity <= 0 or warmup < 0 or iterations <= 0:
        raise ValueError("row_count/group_capacity/iterations must be positive and warmup must be nonnegative")

    idx = torch.arange(row_count, dtype=torch.int64, device="cuda")
    record_set = {
        "row_ids": idx + 1,
        "columns": {
            "region_id": idx % group_capacity,
            "ship_year": 1993 + (idx % 5),
            "discount": idx % 10,
            "quantity": idx % 50,
            "revenue": (idx % 1000) + 1,
        },
    }
    descriptor = rt.prepare_partner_resident_columnar_record_set(record_set, backend="optix")
    sum_query = {
        "predicates": (
            ("ship_year", "between", 1994, 1995),
            ("discount", "between", 4, 6),
            ("quantity", "lt", 25),
        ),
        "group_keys": ("region_id",),
        "value_field": "revenue",
    }
    count_query = {
        "predicates": sum_query["predicates"],
        "group_keys": ("region_id",),
    }

    def two_launch() -> tuple[dict[str, object], ...]:
        sum_rows = rt.run_optix_partner_resident_columnar_grouped_sum_i64(
            descriptor,
            sum_query,
            allow_experimental_native=True,
            group_capacity=group_capacity,
        )
        count_rows = rt.run_optix_partner_resident_columnar_grouped_count_i64(
            descriptor,
            count_query,
            allow_experimental_native=True,
            group_capacity=group_capacity,
        )
        return rt.merge_columnar_grouped_sum_count_rows(sum_rows, count_rows, group_keys=("region_id",))

    def fused() -> tuple[dict[str, object], ...]:
        return rt.run_optix_partner_resident_columnar_grouped_sum_count_i64(
            descriptor,
            sum_query,
            allow_experimental_native=True,
            group_capacity=group_capacity,
        )

    two_rows, two_timings = _time_cuda_call(torch, two_launch, warmup=warmup, iterations=iterations)
    fused_rows, fused_timings = _time_cuda_call(torch, fused, warmup=warmup, iterations=iterations)
    two_stats = _stats(two_timings)
    fused_stats = _stats(fused_timings)
    rows_match = _canonical(two_rows) == _canonical(fused_rows)
    speedup_ratio = two_stats["mean"] / fused_stats["mean"] if fused_stats["mean"] else None
    payload.update(
        {
            "status": "ok",
            "cuda_available": True,
            "torch_version": getattr(torch, "__version__", "unknown"),
            "optix_version": list(rt.optix_version()),
            "row_count": row_count,
            "group_capacity": group_capacity,
            "warmup_iterations": warmup,
            "timed_iterations": iterations,
            "result_group_count": len(fused_rows),
            "rows_match_two_launch_reference": rows_match,
            "two_launch_native_launch_count": 2,
            "fused_native_launch_count": 1,
            "two_launch_timings_sec": two_stats,
            "fused_timings_sec": fused_stats,
            "internal_fused_speedup_ratio_mean": speedup_ratio,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "native_avg_abi_added": False,
            "fused_symbol": rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_COUNT_I64_WITH_CAPACITY_SYMBOL,
        }
    )
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return 0 if rows_match and payload["fused_native_launch_count"] == 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
