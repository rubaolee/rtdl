#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import rtdsl as rt
from examples.reference.rtdl_fixed_radius_neighbors_reference import fixed_radius_neighbors_reference
from examples.reference.rtdl_knn_rows_reference import knn_rows_reference


def _points_2d(count: int, *, id_base: int, stride: float) -> tuple[rt.Point, ...]:
    width = max(1, int(count ** 0.5))
    return tuple(
        rt.Point(
            id=id_base + index,
            x=(index % width) * stride,
            y=(index // width) * stride,
        )
        for index in range(count)
    )


def _case(query_count: int, search_count: int) -> dict[str, tuple[rt.Point, ...]]:
    return {
        "query_points": _points_2d(query_count, id_base=1_000_000, stride=0.37),
        "search_points": _points_2d(search_count, id_base=2_000_000, stride=0.31),
    }


def _measure(kernel, case, threads: str, iterations: int) -> dict[str, object]:
    rt.configure_embree(threads=threads)
    rows = rt.run_embree(kernel, **case)
    row_count = len(rows)
    samples = []
    for _ in range(iterations):
        start = time.perf_counter()
        rows = rt.run_embree(kernel, **case)
        samples.append(time.perf_counter() - start)
        if len(rows) != row_count:
            raise RuntimeError("row count changed across repeated runs")
    return {
        "threads": threads,
        "row_count": row_count,
        "samples_sec": samples,
        "median_sec": statistics.median(samples),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=int, default=4000)
    parser.add_argument("--search", type=int, default=12000)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--threads", default="1,2,4,auto")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    case = _case(args.queries, args.search)
    thread_values = [item.strip() for item in args.threads.split(",") if item.strip()]
    workloads = {
        "fixed_radius_neighbors": fixed_radius_neighbors_reference,
        "knn_rows": knn_rows_reference,
    }
    results = {
        "goal": 710,
        "queries": args.queries,
        "search": args.search,
        "iterations": args.iterations,
        "embree_config_before": rt.embree_thread_config().__dict__,
        "workloads": {},
    }
    for name, kernel in workloads.items():
        workload_results = [_measure(kernel, case, threads, args.iterations) for threads in thread_values]
        baseline = next(item for item in workload_results if item["threads"] == "1")["median_sec"]
        for item in workload_results:
            item["speedup_vs_1_thread"] = baseline / item["median_sec"] if item["median_sec"] else None
        results["workloads"][name] = workload_results
    rt.configure_embree(threads=None)

    text = json.dumps(results, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

