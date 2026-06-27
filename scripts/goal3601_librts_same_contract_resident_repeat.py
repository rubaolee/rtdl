from __future__ import annotations

import argparse
import importlib
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


SCHEMA = "rtdl.goal3601.librts_same_contract_resident_repeat.v1"
APP_MODULE = (
    "examples.benchmark_apps.librts_spatial_index."
    "rtdl_librts_spatial_index_benchmark_app"
)


def _check_output(args: list[str], *, cwd: Path | None = None) -> str:
    try:
        return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _metadata(source_root: Path) -> dict[str, object]:
    return {
        "source_commit": _check_output(["git", "rev-parse", "HEAD"], cwd=source_root),
        "git_status_short": _check_output(["git", "status", "--short"], cwd=source_root),
        "gpu": _check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"]
        ),
    }


def _parse_ops(value: str, default_ops: tuple[str, ...]) -> tuple[str, ...]:
    if value == "all":
        return default_ops
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _time_operation(
    prepared: Any,
    query_handle: Any,
    *,
    operation: str,
    repeat: int,
    warmup: int,
) -> dict[str, object]:
    counts: list[int] = []
    for _ in range(warmup):
        counts.append(int(prepared.count_prepared_queries(query_handle, operation=operation)))

    timings: list[float] = []
    for _ in range(repeat):
        started = time.perf_counter()
        count = int(prepared.count_prepared_queries(query_handle, operation=operation))
        timings.append(time.perf_counter() - started)
        counts.append(count)

    measured_counts = counts[-repeat:]
    if len(set(measured_counts)) != 1:
        raise RuntimeError(f"LibRTS same-contract repeat changed count for {operation}")
    return {
        "operation": operation,
        "count": int(measured_counts[0]),
        "repeat": int(repeat),
        "warmup": int(warmup),
        "median_sec": float(statistics.median(timings)),
        "min_sec": float(min(timings)),
        "max_sec": float(max(timings)),
        "total_sec": float(sum(timings)),
    }


def run(args: argparse.Namespace) -> dict[str, object]:
    source_root = Path(args.source_root).resolve()
    sys.path.insert(0, str(source_root))
    sys.path.insert(0, str(source_root / "src"))

    if args.optix_library:
        os.environ["RTDL_OPTIX_LIBRARY"] = str(Path(args.optix_library).resolve())
        os.environ["RTDL_OPTIX_LIB"] = str(Path(args.optix_library).resolve())

    app = importlib.import_module(APP_MODULE)
    import rtdsl as rt  # noqa: PLC0415

    operations = _parse_ops(args.operations, tuple(app.OPERATIONS))
    fixture = app.make_uniform_fixture(
        box_count=int(args.box_count),
        query_count=int(args.query_count),
        seed=int(args.seed),
    )

    cpu_started = time.perf_counter()
    expected_counts = app.run_counts(fixture, "all")["counts"]
    cpu_reference_sec = time.perf_counter() - cpu_started

    prepare_started = time.perf_counter()
    prepared = rt.prepare_optix_aabb_index_2d(fixture.boxes)
    scene_prepare_sec = time.perf_counter() - prepare_started

    point_queries = None
    box_queries = None
    point_query_prepare_sec = 0.0
    box_query_prepare_sec = 0.0
    try:
        if "point_contains" in operations:
            started = time.perf_counter()
            point_queries = rt.prepare_optix_aabb_point_queries_2d(fixture.point_queries)
            point_query_prepare_sec = time.perf_counter() - started
        if any(op in {"range_contains", "range_intersects"} for op in operations):
            started = time.perf_counter()
            box_queries = rt.prepare_optix_aabb_box_queries_2d(fixture.box_queries)
            box_query_prepare_sec = time.perf_counter() - started

        rows = []
        for operation in operations:
            query_handle = point_queries if operation == "point_contains" else box_queries
            if query_handle is None:
                raise RuntimeError(f"missing query handle for {operation}")
            row = _time_operation(
                prepared,
                query_handle,
                operation=operation,
                repeat=int(args.repeat),
                warmup=int(args.warmup),
            )
            row["expected_count"] = int(expected_counts[operation])
            row["matches_cpu_reference"] = int(row["count"]) == int(expected_counts[operation])
            rows.append(row)
    finally:
        if point_queries is not None:
            point_queries.close()
        if box_queries is not None:
            box_queries.close()
        prepared.close()

    query_summed_median_sec = float(sum(float(row["median_sec"]) for row in rows))
    query_total_sec = float(sum(float(row["total_sec"]) for row in rows))
    all_match = bool(rows) and all(bool(row["matches_cpu_reference"]) for row in rows)

    return {
        "goal": "Goal3601",
        "schema": SCHEMA,
        "lane": args.lane,
        "app": "librts_spatial_index",
        "contract": "generic_prepared_aabb_index_query_2d",
        "primitive": "AABB_INDEX_QUERY_2D",
        "source_root": str(source_root),
        **_metadata(source_root),
        "fixture": fixture.metadata(),
        "operations": operations,
        "repeat_protocol": {
            "repeat": int(args.repeat),
            "warmup": int(args.warmup),
            "measured_run_count_per_operation": int(args.repeat),
            "query_summed_median_sec": query_summed_median_sec,
            "query_total_sec": query_total_sec,
        },
        "run_phases": {
            "cpu_reference_sec": float(cpu_reference_sec),
            "scene_prepare_sec": float(scene_prepare_sec),
            "point_query_prepare_sec": float(point_query_prepare_sec),
            "box_query_prepare_sec": float(box_query_prepare_sec),
            "query_summed_median_sec": query_summed_median_sec,
            "query_total_sec": query_total_sec,
        },
        "expected_counts": {key: int(value) for key, value in expected_counts.items()},
        "rows": rows,
        "all_match_cpu_reference": all_match,
        "rt_core_accelerated": True,
        "native_engine_customization": False,
        "claim_boundary": {
            "internal_evidence_only": True,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3601 LibRTS same-contract resident repeat harness.")
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--lane", required=True)
    parser.add_argument("--optix-library", type=Path)
    parser.add_argument("--box-count", type=int, default=1024)
    parser.add_argument("--query-count", type=int, default=512)
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--repeat", type=int, default=15000)
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--operations", default="all")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")

    payload = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_match_cpu_reference"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
