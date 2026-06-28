from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl as rt
import rtdsl.v4 as rtdl_v4
from rtdsl.reference import Point


@rt.kernel(backend="rtdl", precision="float_approx")
def nearest_witness_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=1))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


def _distance_sq(left: Point, right: Point) -> float:
    dx = float(left.x) - float(right.x)
    dy = float(left.y) - float(right.y)
    return dx * dx + dy * dy


def make_case() -> dict[str, tuple[Point, ...]]:
    return {
        "query_points": (
            Point(id=1, x=0.0, y=0.0),
            Point(id=2, x=4.0, y=0.0),
        ),
        "search_points": (
            Point(id=100, x=0.2, y=0.0),
            Point(id=101, x=2.0, y=0.0),
            Point(id=102, x=4.1, y=0.1),
            Point(id=103, x=7.0, y=0.0),
        ),
    }


def run_kernel_mode() -> dict[str, object]:
    case = make_case()
    compiled = rt.compile_kernel(nearest_witness_kernel)
    rows = tuple(rt.run_cpu_python_reference(nearest_witness_kernel, **case))
    nearest_rows = tuple(
        {
            "query_id": int(row["query_id"]),
            "neighbor_id": int(row["neighbor_id"]),
            "distance": round(float(row["distance"]), 4),
            "rank": int(row["neighbor_rank"]),
        }
        for row in rows
    )
    return {
        "mode": "kernel",
        "status": "ok",
        "teaches": "RTDL kernel: input -> traverse -> refine(knn_rows(k=1)) -> emit nearest witness rows",
        "kernel_summary": compiled.format(),
        "query_points": tuple(point.__dict__ for point in case["query_points"]),
        "search_points": tuple(point.__dict__ for point in case["search_points"]),
        "nearest_rows": nearest_rows,
    }


def run_v4_mode() -> dict[str, object]:
    plan = rtdl_v4.plan_operator_request_v4("point_group_nearest", partner="torch")
    return {
        "mode": "v4",
        "status": "ok",
        "teaches": "V4 operator/runtime mapping for a nearest-witness relation",
        "operator": "point_group_nearest",
        "partner": "torch",
        "plan_status": plan.status,
        "surface": plan.api_surface,
        "generic_primitive": plan.generic_primitive,
        "relationship_to_kernel": (
            "The kernel teaches nearest-witness rows. The V4 surface is the "
            "device-array execution target when the same relation is recognized."
        ),
    }


def run_visible_flow() -> dict[str, object]:
    case = make_case()
    candidate_rows = []
    for query in case["query_points"]:
        for candidate in case["search_points"]:
            distance_sq = _distance_sq(query, candidate)
            candidate_rows.append(
                {
                    "query_id": int(query.id),
                    "candidate_id": int(candidate.id),
                    "distance_sq": round(distance_sq, 4),
                }
            )

    nearest_rows = []
    for query in case["query_points"]:
        rows_for_query = [
            row for row in candidate_rows if row["query_id"] == int(query.id)
        ]
        best = min(rows_for_query, key=lambda row: (row["distance_sq"], row["candidate_id"]))
        nearest_rows.append(
            {
                "query_id": best["query_id"],
                "neighbor_id": best["candidate_id"],
                "distance_sq": best["distance_sq"],
                "rank": 1,
            }
        )

    return {
        "status": "ok",
        "mode": "visible_python_flow",
        "concept": "manual mirror of candidate distance rows plus per-query argmin continuation",
        "manual_data_flow": (
            "query_points + search_points -> candidate witness rows -> per-query argmin continuation"
        ),
        "candidate_rows": tuple(candidate_rows),
        "nearest_rows": tuple(nearest_rows),
    }


def run_both_modes() -> dict[str, object]:
    kernel = run_kernel_mode()
    v4 = run_v4_mode()
    return {
        "status": "ok",
        "concept": (
            "nearest witness is first a candidate-row plus argmin relation; V4 "
            "then maps that relation to a concrete operator surface"
        ),
        "kernel_mode": kernel,
        "visible_flow": run_visible_flow(),
        "v4_mode": v4,
        "same_semantics": {
            "relation": "nearest_witness_rows",
            "kernel_output_field": "nearest_rows",
            "v4_execution_target": v4["surface"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RTDL nearest-witness tutorial")
    parser.add_argument("--mode", choices=("kernel", "v4", "both", "visible"), default="both")
    args = parser.parse_args()
    if args.mode == "kernel":
        payload = run_kernel_mode()
    elif args.mode == "v4":
        payload = run_v4_mode()
    elif args.mode == "visible":
        payload = run_visible_flow()
    else:
        payload = run_both_modes()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
