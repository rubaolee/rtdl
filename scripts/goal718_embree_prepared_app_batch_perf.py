#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_dbscan_clustering_app as dbscan
from examples import rtdl_outlier_detection_app as outlier


def _bench(label: str, fn: Callable[[], object], *, repeats: int, warmups: int) -> dict[str, object]:
    for _ in range(warmups):
        fn()
    samples: list[float] = []
    row_count = 0
    for _ in range(repeats):
        start = time.perf_counter()
        rows = fn()
        samples.append(time.perf_counter() - start)
        row_count = len(rows) if hasattr(rows, "__len__") else 0
    return {
        "label": label,
        "repeat_count": repeats,
        "samples_sec": samples,
        "median_sec": statistics.median(samples),
        "min_sec": min(samples),
        "max_sec": max(samples),
        "row_count": row_count,
    }


def _time_once(fn: Callable[[], object]) -> float:
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start


def _speedup(before: dict[str, object], after: dict[str, object]) -> float | None:
    after_sec = float(after["median_sec"])
    if after_sec <= 0.0:
        return None
    return float(before["median_sec"]) / after_sec


def _outlier_batch(case: dict[str, tuple[rt.Point, ...]], *, repeats: int, warmups: int) -> dict[str, object]:
    points = case["points"]
    one_shot = _bench(
        "one_shot_summary_plus_density",
        lambda: outlier._run_embree_density_summary(case),
        repeats=repeats,
        warmups=warmups,
    )
    prepare_sec = _time_once(lambda: rt.prepare_embree_fixed_radius_count_threshold_2d(points).close())
    prepared = rt.prepare_embree_fixed_radius_count_threshold_2d(points)
    try:
        prepared_run = _bench(
            "prepared_summary_plus_density",
            lambda: outlier._density_rows_from_count_rows(
                points,
                prepared.run(
                    points,
                    radius=outlier.RADIUS,
                    threshold=outlier.MIN_NEIGHBORS_INCLUDING_SELF,
                ),
            ),
            repeats=repeats,
            warmups=warmups,
        )
    finally:
        prepared.close()
    return {
        "one_shot": one_shot,
        "prepare_sec": prepare_sec,
        "prepared_run_only": prepared_run,
        "prepared_speedup_vs_one_shot": _speedup(one_shot, prepared_run),
    }


def _dbscan_batch(case: dict[str, tuple[rt.Point, ...]], *, repeats: int, warmups: int) -> dict[str, object]:
    points = case["points"]
    one_shot = _bench(
        "one_shot_summary_plus_core_flags",
        lambda: dbscan._run_embree_core_flag_summary(case),
        repeats=repeats,
        warmups=warmups,
    )
    prepare_sec = _time_once(lambda: rt.prepare_embree_fixed_radius_count_threshold_2d(points).close())
    prepared = rt.prepare_embree_fixed_radius_count_threshold_2d(points)
    try:
        prepared_run = _bench(
            "prepared_summary_plus_core_flags",
            lambda: dbscan._core_flag_rows_from_count_rows(
                points,
                prepared.run(
                    points,
                    radius=dbscan.EPSILON,
                    threshold=dbscan.MIN_POINTS,
                ),
            ),
            repeats=repeats,
            warmups=warmups,
        )
    finally:
        prepared.close()
    return {
        "one_shot": one_shot,
        "prepare_sec": prepare_sec,
        "prepared_run_only": prepared_run,
        "prepared_speedup_vs_one_shot": _speedup(one_shot, prepared_run),
    }


def run_suite(*, copies: tuple[int, ...], repeats: int, warmups: int) -> dict[str, object]:
    rt.configure_embree(threads=os.environ.get("RTDL_EMBREE_THREADS", "auto"))
    cases: list[dict[str, object]] = []
    for copy_count in copies:
        outlier_case = outlier.make_outlier_case(copies=copy_count)
        dbscan_case = dbscan.make_dbscan_case(copies=copy_count)
        cases.append(
            {
                "copies": copy_count,
                "outlier_point_count": len(outlier_case["points"]),
                "dbscan_point_count": len(dbscan_case["points"]),
                "outlier": _outlier_batch(outlier_case, repeats=repeats, warmups=warmups),
                "dbscan": _dbscan_batch(dbscan_case, repeats=repeats, warmups=warmups),
            }
        )
    return {
        "goal": 718,
        "valid": True,
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "embree_version": rt.embree_version(),
        "embree_threads": rt.embree_thread_config().__dict__,
        "copies": list(copies),
        "repeats": repeats,
        "warmups": warmups,
        "cases": cases,
        "boundary": "Measures repeated app summary phases with Python density/core conversion, but excludes full CLI JSON output and oracle work. Prepared mode reports run-only timing after one reusable Embree BVH prepare.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal718 Embree prepared app-batch benchmark.")
    parser.add_argument("--copies", default="512,2048,8192")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)
    copy_values = tuple(int(item) for item in args.copies.split(",") if item)
    payload = run_suite(copies=copy_values, repeats=args.repeats, warmups=args.warmups)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
