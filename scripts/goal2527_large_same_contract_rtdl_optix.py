from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable


GOAL = "goal2527_large_same_contract_rtdl_optix"
APP = "raydb_style_columnar_aggregate"
CLAIM_BOUNDARY = (
    "Large same-contract RTDL OptiX partner-resident diagnostic timing only. "
    "Torch CUDA tensor construction and RTDL descriptor preparation are outside timed loops. "
    "Timed loops include native RTDL launches, CUDA synchronization, and compact grouped host-row "
    "materialization. This artifact does not authorize public speedup, whole-DBMS, authors-code, "
    "RayDB reproduction, or true-zero-copy claims."
)


def parse_row_counts(value: str) -> list[int]:
    row_counts = [int(item.strip()) for item in value.split(",") if item.strip()]
    if not row_counts or any(item <= 0 for item in row_counts):
        raise ValueError("row counts must be a comma-separated list of positive integers")
    return row_counts


def stats_ms(samples: list[float]) -> dict[str, Any]:
    ordered = sorted(samples)
    return {
        "median": statistics.median(ordered),
        "mean": statistics.fmean(ordered),
        "min": ordered[0],
        "max": ordered[-1],
        "samples": samples,
    }


def run_text(command: list[str]) -> str:
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return (result.stdout + result.stderr).strip()


def canonical_full_rows(rows: list[dict[str, Any]]) -> list[dict[str, int]]:
    return [
        {
            "region_id": int(row["region_id"]),
            "count": int(row["count"]),
            "sum": int(row["sum"]),
            "min": int(row["min"]),
            "max": int(row["max"]),
        }
        for row in sorted(rows, key=lambda item: int(item["region_id"]))
    ]


def build_record_set(torch: Any, row_count: int, group_capacity: int) -> dict[str, Any]:
    idx = torch.arange(row_count, dtype=torch.int64, device="cuda")
    return {
        "row_ids": idx + 1,
        "columns": {
            "region_id": idx % group_capacity,
            "ship_year": 1993 + (idx % 5),
            "discount": idx % 10,
            "quantity": idx % 50,
            "revenue": (idx % 1000) + 1,
        },
    }


def grouped_query(*, include_value_field: bool) -> dict[str, Any]:
    query: dict[str, Any] = {
        "predicates": (
            ("ship_year", "between", 1994, 1995),
            ("discount", "between", 4, 6),
            ("quantity", "lt", 25),
        ),
        "group_keys": ("region_id",),
    }
    if include_value_field:
        query["value_field"] = "revenue"
    return query


def assemble_full_rows(
    *,
    sum_count_rows: tuple[dict[str, Any], ...],
    min_rows: tuple[dict[str, Any], ...],
    max_rows: tuple[dict[str, Any], ...],
) -> list[dict[str, int]]:
    by_group: dict[int, dict[str, int]] = {}
    for row in sum_count_rows:
        region_id = int(row["region_id"])
        by_group[region_id] = {
            "region_id": region_id,
            "sum": int(row["sum"]),
            "count": int(row["count"]),
        }
    for row in min_rows:
        by_group.setdefault(int(row["region_id"]), {"region_id": int(row["region_id"])})["min"] = int(row["min"])
    for row in max_rows:
        by_group.setdefault(int(row["region_id"]), {"region_id": int(row["region_id"])})["max"] = int(row["max"])
    return canonical_full_rows(list(by_group.values()))


def time_cuda(torch: Any, fn: Callable[[], Any], *, warmup: int, repeats: int) -> tuple[Any, dict[str, Any]]:
    last_result: Any = None
    for _ in range(warmup):
        last_result = fn()
    torch.cuda.synchronize()
    samples: list[float] = []
    for _ in range(repeats):
        torch.cuda.synchronize()
        start = time.perf_counter_ns()
        last_result = fn()
        torch.cuda.synchronize()
        samples.append((time.perf_counter_ns() - start) / 1_000_000.0)
    return last_result, stats_ms(samples)


def run_row_count(
    *,
    rt: Any,
    torch: Any,
    row_count: int,
    group_capacity: int,
    warmup: int,
    repeats: int,
    expected_rows: list[dict[str, int]] | None,
) -> dict[str, Any]:
    setup_start = time.perf_counter_ns()
    record_set = build_record_set(torch, row_count, group_capacity)
    descriptor = rt.prepare_partner_resident_columnar_record_set(record_set, backend="optix")
    torch.cuda.synchronize()
    setup_ms = (time.perf_counter_ns() - setup_start) / 1_000_000.0
    value_query = grouped_query(include_value_field=True)

    def sum_count_only() -> tuple[dict[str, Any], ...]:
        return tuple(
            rt.run_optix_partner_resident_columnar_grouped_i64_reduction(
                descriptor,
                value_query,
                reduction="sum_count",
                allow_experimental_native=True,
                group_capacity=group_capacity,
                semantic_aggregate="avg_as_sum_count",
            )["rows"]
        )

    def full_contract_three_launch() -> list[dict[str, int]]:
        sum_count_rows = sum_count_only()
        min_rows = tuple(
            rt.run_optix_partner_resident_columnar_grouped_i64_reduction(
                descriptor,
                value_query,
                reduction="min",
                allow_experimental_native=True,
                group_capacity=group_capacity,
            )["rows"]
        )
        max_rows = tuple(
            rt.run_optix_partner_resident_columnar_grouped_i64_reduction(
                descriptor,
                value_query,
                reduction="max",
                allow_experimental_native=True,
                group_capacity=group_capacity,
            )["rows"]
        )
        return assemble_full_rows(sum_count_rows=sum_count_rows, min_rows=min_rows, max_rows=max_rows)

    def full_contract_fused() -> list[dict[str, int]]:
        return canonical_full_rows(
            list(
                rt.run_optix_partner_resident_columnar_grouped_i64_reduction(
                    descriptor,
                    value_query,
                    reduction="stats",
                    allow_experimental_native=True,
                    group_capacity=group_capacity,
                    semantic_aggregate="count_sum_min_max",
                )["rows"]
            )
        )

    sum_count_rows, sum_count_timing = time_cuda(torch, sum_count_only, warmup=warmup, repeats=repeats)
    three_launch_rows, three_launch_timing = time_cuda(
        torch, full_contract_three_launch, warmup=warmup, repeats=repeats
    )
    fused_rows, fused_timing = time_cuda(torch, full_contract_fused, warmup=warmup, repeats=repeats)
    three_launch_rows = canonical_full_rows(three_launch_rows)
    fused_rows = canonical_full_rows(fused_rows)
    return {
        "status": "ok",
        "row_count": row_count,
        "group_capacity": group_capacity,
        "setup_ms": setup_ms,
        "descriptor": descriptor.to_metadata(),
        "result_group_count": len(fused_rows),
        "sum_count_rows": [
            {"region_id": int(row["region_id"]), "sum": int(row["sum"]), "count": int(row["count"])}
            for row in sorted(sum_count_rows, key=lambda item: int(item["region_id"]))
        ],
        "full_rows": fused_rows,
        "three_launch_full_rows": three_launch_rows,
        "matches_expected": expected_rows is not None and fused_rows == expected_rows,
        "three_launch_matches_expected": expected_rows is not None and three_launch_rows == expected_rows,
        "fused_matches_three_launch": fused_rows == three_launch_rows,
        "sum_count_only_timing_ms": sum_count_timing,
        "full_contract_fused_timing_ms": fused_timing,
        "full_contract_three_launch_timing_ms": three_launch_timing,
        "native_launch_count_full_contract": 1,
        "native_launch_count_three_launch_full_contract": 3,
        "native_launch_count_sum_count_only": 1,
        "timing_boundary": (
            "RTDL OptiX partner-resident fused count/sum/min/max native launch over preconstructed "
            "CUDA tensors plus compact grouped host-row materialization; setup excluded"
        ),
        "three_launch_timing_boundary": (
            "Legacy comparison path: fused sum_count, min, and max as three native launches; setup excluded"
        ),
    }


def load_expected_rows(path: Path | None) -> dict[str, list[dict[str, int]]]:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected = payload.get("expected_rows_by_row_count", {})
    return {
        str(row_count): canonical_full_rows(item["full_rows"])
        for row_count, item in expected.items()
        if isinstance(item, dict) and "full_rows" in item
    }


def run_all(
    *,
    row_counts: list[int],
    group_capacity: int,
    warmup: int,
    repeats: int,
    expected_path: Path | None,
) -> dict[str, Any]:
    repo = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo / "src"))
    sys.path.insert(0, str(repo))
    import torch
    import rtdsl as rt

    payload: dict[str, Any] = {
        "goal": GOAL,
        "app": APP,
        "status": "ok",
        "python": sys.version,
        "platform": platform.platform(),
        "git_head": run_text(["git", "-C", str(repo), "rev-parse", "HEAD"]),
        "rtdl_optix_lib": os.environ.get("RTDL_OPTIX_LIB", ""),
        "ld_library_path": os.environ.get("LD_LIBRARY_PATH", ""),
        "torch_version": getattr(torch, "__version__", "unknown"),
        "cuda_available": bool(torch.cuda.is_available()),
        "row_counts": row_counts,
        "group_capacity": group_capacity,
        "warmup": warmup,
        "repeats": repeats,
        "query_contract": "RTDL partner-resident grouped i64 reductions for sum_count, min, and max",
        "claim_boundary": CLAIM_BOUNDARY,
        "systems": {"rtdl_optix_partner_resident": {}},
        "performance_matrix": [],
        "performance_claim_authorized": False,
    }
    if not torch.cuda.is_available():
        payload.update({"status": "blocked", "blocked_reason": "CUDA unavailable"})
        return payload
    payload["optix_version"] = list(rt.optix_version())
    expected_by_row_count = load_expected_rows(expected_path)
    for row_count in row_counts:
        expected_rows = expected_by_row_count.get(str(row_count))
        result = run_row_count(
            rt=rt,
            torch=torch,
            row_count=row_count,
            group_capacity=group_capacity,
            warmup=warmup,
            repeats=repeats,
            expected_rows=expected_rows,
        )
        payload["systems"]["rtdl_optix_partner_resident"][str(row_count)] = result
        payload["performance_matrix"].append(
            {
                "row_count": row_count,
                "system": "rtdl_optix_partner_resident_sum_count_only",
                "median_ms": result["sum_count_only_timing_ms"]["median"],
                "mean_ms": result["sum_count_only_timing_ms"]["mean"],
                "min_ms": result["sum_count_only_timing_ms"]["min"],
                "max_ms": result["sum_count_only_timing_ms"]["max"],
                "matches_expected": result["matches_expected"],
                "result_group_count": result["result_group_count"],
                "native_launch_count": result["native_launch_count_sum_count_only"],
                "timing_boundary": "one fused RTDL sum_count launch only; not the full count/sum/min/max contract",
            }
        )
        payload["performance_matrix"].append(
            {
                "row_count": row_count,
                "system": "rtdl_optix_partner_resident_full_contract",
                "median_ms": result["full_contract_fused_timing_ms"]["median"],
                "mean_ms": result["full_contract_fused_timing_ms"]["mean"],
                "min_ms": result["full_contract_fused_timing_ms"]["min"],
                "max_ms": result["full_contract_fused_timing_ms"]["max"],
                "matches_expected": result["matches_expected"],
                "result_group_count": result["result_group_count"],
                "native_launch_count": result["native_launch_count_full_contract"],
                "timing_boundary": result["timing_boundary"],
            }
        )
        payload["performance_matrix"].append(
            {
                "row_count": row_count,
                "system": "rtdl_optix_partner_resident_full_contract_three_launch",
                "median_ms": result["full_contract_three_launch_timing_ms"]["median"],
                "mean_ms": result["full_contract_three_launch_timing_ms"]["mean"],
                "min_ms": result["full_contract_three_launch_timing_ms"]["min"],
                "max_ms": result["full_contract_three_launch_timing_ms"]["max"],
                "matches_expected": result["three_launch_matches_expected"],
                "result_group_count": result["result_group_count"],
                "native_launch_count": result["native_launch_count_three_launch_full_contract"],
                "timing_boundary": result["three_launch_timing_boundary"],
            }
        )
    payload["all_available_results_match_expected"] = all(
        result.get("matches_expected", False)
        for result in payload["systems"]["rtdl_optix_partner_resident"].values()
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Goal2527 RTDL OptiX large same-contract timing.")
    parser.add_argument("--row-counts", default="100000,1000000,5000000")
    parser.add_argument("--group-capacity", type=int, default=1024)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--expected-json", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    payload = run_all(
        row_counts=parse_row_counts(args.row_counts),
        group_capacity=args.group_capacity,
        warmup=args.warmup,
        repeats=args.repeats,
        expected_path=args.expected_json,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] == "ok" and payload["all_available_results_match_expected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
