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


def _prepared_case(points, *, radius: float, threshold: int, repeats: int, warmups: int) -> dict[str, object]:
    prepare_sec = _time_once(lambda: rt.prepare_embree_fixed_radius_count_threshold_2d(points).close())
    prepared = rt.prepare_embree_fixed_radius_count_threshold_2d(points)
    try:
        one_shot = _bench(
            "one_shot_summary",
            lambda: rt.fixed_radius_count_threshold_2d_embree(
                points,
                points,
                radius=radius,
                threshold=threshold,
            ),
            repeats=repeats,
            warmups=warmups,
        )
        prepared_run = _bench(
            "prepared_summary_run_only",
            lambda: prepared.run(points, radius=radius, threshold=threshold),
            repeats=repeats,
            warmups=warmups,
        )
    finally:
        prepared.close()
    return {
        "prepare_sec": prepare_sec,
        "one_shot": one_shot,
        "prepared_run_only": prepared_run,
        "prepared_run_speedup_vs_one_shot": _speedup(one_shot, prepared_run),
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
                "outlier": _prepared_case(
                    outlier_case["points"],
                    radius=outlier.RADIUS,
                    threshold=outlier.MIN_NEIGHBORS_INCLUDING_SELF,
                    repeats=repeats,
                    warmups=warmups,
                ),
                "dbscan": _prepared_case(
                    dbscan_case["points"],
                    radius=dbscan.EPSILON,
                    threshold=dbscan.MIN_POINTS,
                    repeats=repeats,
                    warmups=warmups,
                ),
            }
        )
    return {
        "goal": 717,
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
        "boundary": "Measures prepared Embree fixed-radius count-threshold run-only time against one-shot summary calls over the same search/query set; prepare time is reported separately and whole-app JSON/oracle work is excluded.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal717 prepared Embree fixed-radius summary benchmark.")
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
