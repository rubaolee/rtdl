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

from examples import rtdl_hausdorff_distance_app


def _median_time(fn: Callable[[], object], repeats: int) -> tuple[float, object]:
    timings: list[float] = []
    value = None
    for _ in range(repeats):
        start = time.perf_counter()
        value = fn()
        timings.append(time.perf_counter() - start)
    return statistics.median(timings), value


def _case(copies: int, repeats: int) -> dict[str, object]:
    case = rtdl_hausdorff_distance_app.make_authored_point_sets(copies=copies)
    points_a = case["points_a"]
    points_b = case["points_b"]

    def row_mode():
        rows_ab = rtdl_hausdorff_distance_app._run_nearest("embree", points_a, points_b)
        rows_ba = rtdl_hausdorff_distance_app._run_nearest("embree", points_b, points_a)
        directed_ab = rtdl_hausdorff_distance_app._directed_from_rows(rows_ab, "a_to_b")
        directed_ba = rtdl_hausdorff_distance_app._directed_from_rows(rows_ba, "b_to_a")
        undirected = max(
            (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
            key=lambda item: (float(item[1]["distance"]), item[0]),
        )
        return {
            "directed_a_to_b": directed_ab,
            "directed_b_to_a": directed_ba,
            "hausdorff_distance": float(undirected[1]["distance"]),
            "witness_direction": undirected[0],
        }

    def summary_mode():
        import rtdsl as rt

        directed_ab = rt.directed_hausdorff_2d_embree(points_a, points_b)
        directed_ba = rt.directed_hausdorff_2d_embree(points_b, points_a)
        undirected = max(
            (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
            key=lambda item: (float(item[1]["distance"]), item[0]),
        )
        return {
            "directed_a_to_b": directed_ab,
            "directed_b_to_a": directed_ba,
            "hausdorff_distance": float(undirected[1]["distance"]),
            "witness_direction": undirected[0],
        }

    rows_sec, rows_result = _median_time(row_mode, repeats)
    summary_sec, summary_result = _median_time(summary_mode, repeats)
    if rows_result["hausdorff_distance"] != summary_result["hausdorff_distance"]:
        raise AssertionError("summary mode did not match row mode Hausdorff distance")
    if rows_result["witness_direction"] != summary_result["witness_direction"]:
        raise AssertionError("summary mode did not match row mode witness direction")
    return {
        "app": "hausdorff_distance",
        "copies": copies,
        "point_count_a": len(points_a),
        "point_count_b": len(points_b),
        "row_mode_sec": rows_sec,
        "directed_summary_sec": summary_sec,
        "summary_speedup_vs_rows": rows_sec / summary_sec if summary_sec else None,
        "hausdorff_distance": summary_result["hausdorff_distance"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal722 Embree Hausdorff summary perf harness.")
    parser.add_argument("--copies", type=int, nargs="+", default=[256, 1024, 4096])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    results = []
    for copies in args.copies:
        result = _case(copies, args.repeats)
        results.append(result)
        print(json.dumps(result, sort_keys=True))
    payload = {
        "goal": 722,
        "description": "Embree native directed-Hausdorff summary compared with KNN rows plus Python reduction.",
        "repeats": args.repeats,
        "results": results,
    }
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
