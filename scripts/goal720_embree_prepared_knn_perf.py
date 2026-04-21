from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_ann_candidate_app
from examples import rtdl_facility_knn_assignment
from examples import rtdl_hausdorff_distance_app


def _median_time(fn: Callable[[], object], repeats: int) -> tuple[float, object]:
    timings: list[float] = []
    value = None
    for _ in range(repeats):
        start = time.perf_counter()
        value = fn()
        timings.append(time.perf_counter() - start)
    return statistics.median(timings), value


def _hausdorff_case(copies: int, repeats: int) -> dict[str, object]:
    case = rtdl_hausdorff_distance_app.make_authored_point_sets(copies=copies)
    points_a = case["points_a"]
    points_b = case["points_b"]

    def one_shot():
        return (
            tuple(rtdl_hausdorff_distance_app._run_nearest("embree", points_a, points_b)),
            tuple(rtdl_hausdorff_distance_app._run_nearest("embree", points_b, points_a)),
        )

    one_shot_sec, expected = _median_time(one_shot, repeats)
    prepare_start = time.perf_counter()
    prepared_b = rt.prepare_embree_knn_rows_2d(points_b)
    prepared_a = rt.prepare_embree_knn_rows_2d(points_a)
    prepare_sec = time.perf_counter() - prepare_start
    try:
        prepared_sec, actual = _median_time(
            lambda: (
                prepared_b.run(points_a, k=1),
                prepared_a.run(points_b, k=1),
            ),
            repeats,
        )
    finally:
        prepared_b.close()
        prepared_a.close()
    if actual != expected:
        raise AssertionError("prepared Hausdorff kNN rows did not match one-shot Embree rows")
    return {
        "app": "hausdorff_distance",
        "copies": copies,
        "query_count": len(points_a) + len(points_b),
        "search_count_per_pass": len(points_a),
        "k": 1,
        "one_shot_sec": one_shot_sec,
        "prepare_sec": prepare_sec,
        "prepared_run_sec": prepared_sec,
        "prepared_run_speedup_vs_one_shot": one_shot_sec / prepared_sec if prepared_sec else None,
    }


def _ann_case(copies: int, repeats: int) -> dict[str, object]:
    case = rtdl_ann_candidate_app.make_ann_case(copies=copies)
    query_points = case["query_points"]
    candidate_points = case["candidate_points"]

    def one_shot():
        return tuple(rtdl_ann_candidate_app._run_rows("embree", case))

    one_shot_sec, expected = _median_time(one_shot, repeats)
    prepare_sec, prepared = _median_time(lambda: rt.prepare_embree_knn_rows_2d(candidate_points), 1)
    try:
        prepared_sec, actual = _median_time(lambda: prepared.run(query_points, k=rtdl_ann_candidate_app.K), repeats)
    finally:
        prepared.close()
    if actual != expected:
        raise AssertionError("prepared ANN candidate kNN rows did not match one-shot Embree rows")
    return {
        "app": "ann_candidate_search",
        "copies": copies,
        "query_count": len(query_points),
        "search_count": len(candidate_points),
        "k": rtdl_ann_candidate_app.K,
        "one_shot_sec": one_shot_sec,
        "prepare_sec": prepare_sec,
        "prepared_run_sec": prepared_sec,
        "prepared_run_speedup_vs_one_shot": one_shot_sec / prepared_sec if prepared_sec else None,
    }


def _facility_case(copies: int, repeats: int) -> dict[str, object]:
    case = rtdl_facility_knn_assignment.make_facility_knn_case(copies=copies)
    customers = case["customers"]
    depots = case["depots"]

    def one_shot():
        return tuple(rtdl_facility_knn_assignment._run_rows("embree", case))

    one_shot_sec, expected = _median_time(one_shot, repeats)
    prepare_sec, prepared = _median_time(lambda: rt.prepare_embree_knn_rows_2d(depots), 1)
    try:
        prepared_sec, actual = _median_time(
            lambda: prepared.run(customers, k=rtdl_facility_knn_assignment.K),
            repeats,
        )
    finally:
        prepared.close()
    if actual != expected:
        raise AssertionError("prepared facility kNN rows did not match one-shot Embree rows")
    return {
        "app": "facility_knn_assignment",
        "copies": copies,
        "query_count": len(customers),
        "search_count": len(depots),
        "k": rtdl_facility_knn_assignment.K,
        "one_shot_sec": one_shot_sec,
        "prepare_sec": prepare_sec,
        "prepared_run_sec": prepared_sec,
        "prepared_run_speedup_vs_one_shot": one_shot_sec / prepared_sec if prepared_sec else None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal720 prepared Embree kNN perf harness.")
    parser.add_argument("--copies", type=int, nargs="+", default=[256, 1024, 4096])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    results: list[dict[str, object]] = []
    for copies in args.copies:
        for case_fn in (_hausdorff_case, _ann_case, _facility_case):
            result = case_fn(copies, args.repeats)
            results.append(result)
            print(json.dumps(result, sort_keys=True))
    payload = {
        "goal": 720,
        "description": "Prepared Embree 2-D kNN rows compared with one-shot Embree kNN app paths.",
        "repeats": args.repeats,
        "results": results,
    }
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
