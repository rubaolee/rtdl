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


def _speedup(before: dict[str, object], after: dict[str, object]) -> float | None:
    after_sec = float(after["median_sec"])
    if after_sec <= 0:
        return None
    return float(before["median_sec"]) / after_sec


def run_suite(*, copies: tuple[int, ...], repeats: int, warmups: int) -> dict[str, object]:
    rt.configure_embree(threads=os.environ.get("RTDL_EMBREE_THREADS", "auto"))
    cases: list[dict[str, object]] = []
    for copy_count in copies:
        outlier_case = outlier.make_outlier_case(copies=copy_count)
        outlier_rows = _bench(
            "outlier_rows",
            lambda case=outlier_case: outlier._run_rows("embree", case),
            repeats=repeats,
            warmups=warmups,
        )
        outlier_summary = _bench(
            "outlier_count_threshold_summary",
            lambda case=outlier_case: rt.fixed_radius_count_threshold_2d_embree(
                case["points"],
                case["points"],
                radius=outlier.RADIUS,
                threshold=outlier.MIN_NEIGHBORS_INCLUDING_SELF,
            ),
            repeats=repeats,
            warmups=warmups,
        )

        dbscan_case = dbscan.make_dbscan_case(copies=copy_count)
        dbscan_rows = _bench(
            "dbscan_rows",
            lambda case=dbscan_case: dbscan._run_rows("embree", case),
            repeats=repeats,
            warmups=warmups,
        )
        dbscan_summary = _bench(
            "dbscan_core_flag_summary",
            lambda case=dbscan_case: rt.fixed_radius_count_threshold_2d_embree(
                case["points"],
                case["points"],
                radius=dbscan.EPSILON,
                threshold=dbscan.MIN_POINTS,
            ),
            repeats=repeats,
            warmups=warmups,
        )
        cases.append(
            {
                "copies": copy_count,
                "outlier_point_count": len(outlier_case["points"]),
                "dbscan_point_count": len(dbscan_case["points"]),
                "outlier_rows": outlier_rows,
                "outlier_summary": outlier_summary,
                "outlier_summary_speedup_vs_rows": _speedup(outlier_rows, outlier_summary),
                "dbscan_rows": dbscan_rows,
                "dbscan_summary": dbscan_summary,
                "dbscan_summary_speedup_vs_rows": _speedup(dbscan_rows, dbscan_summary),
            }
        )
    return {
        "goal": 715,
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
        "boundary": "Measures native Embree fixed-radius row emission versus native Embree count-threshold summary only; app oracle validation and JSON serialization are intentionally excluded.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal715 Embree fixed-radius summary microbenchmark.")
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
