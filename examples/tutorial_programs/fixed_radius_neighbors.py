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
def fixed_radius_neighbors_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=0.5, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


def _distance_sq(left: Point, right: Point) -> float:
    dx = float(left.x) - float(right.x)
    dy = float(left.y) - float(right.y)
    return dx * dx + dy * dy


def make_case() -> dict[str, tuple[Point, ...]]:
    return {
        "query_points": (
            Point(id=1, x=0.0, y=0.0),
            Point(id=2, x=2.0, y=0.0),
        ),
        "search_points": (
            Point(id=10, x=0.1, y=0.1),
            Point(id=11, x=0.4, y=0.0),
            Point(id=12, x=2.2, y=0.0),
            Point(id=13, x=8.0, y=8.0),
        ),
    }


def run_kernel_mode() -> dict[str, object]:
    case = make_case()
    compiled = rt.compile_kernel(fixed_radius_neighbors_kernel)
    rows = tuple(rt.run_cpu_python_reference(fixed_radius_neighbors_kernel, **case))
    rows = tuple(
        {
            "query_id": int(row["query_id"]),
            "neighbor_id": int(row["neighbor_id"]),
            "distance": round(float(row["distance"]), 4),
        }
        for row in rows
    )
    counts_by_query = {
        point.id: sum(1 for row in rows if int(row["query_id"]) == point.id)
        for point in case["query_points"]
    }
    return {
        "mode": "kernel",
        "status": "ok",
        "teaches": "RTDL kernel: input -> traverse -> refine(fixed_radius_neighbors) -> emit neighbor rows",
        "kernel_summary": compiled.format(),
        "query_points": tuple(point.__dict__ for point in case["query_points"]),
        "search_points": tuple(point.__dict__ for point in case["search_points"]),
        "neighbor_rows": rows,
        "threshold_rows": tuple(
            {
                "query_id": query_id,
                "neighbor_count": count,
                "threshold_reached": count >= 2,
            }
            for query_id, count in sorted(counts_by_query.items())
        ),
    }


def run_v4_mode() -> dict[str, object]:
    plan = rtdl_v4.plan_operator_request_v4("fixed_radius", partner="torch")
    return {
        "mode": "v4",
        "status": "ok",
        "teaches": "V4 operator/runtime mapping for the same fixed-radius relation",
        "operator": "fixed_radius",
        "partner": "torch",
        "plan_status": plan.status,
        "surface": plan.api_surface,
        "generic_primitive": plan.generic_primitive,
        "relationship_to_kernel": (
            "This is the execution/planning target for a recognized fixed-radius "
            "kernel pattern. It is not the beginner programming model."
        ),
    }


def run_both_modes() -> dict[str, object]:
    kernel = run_kernel_mode()
    v4 = run_v4_mode()
    return {
        "status": "ok",
        "concept": (
            "fixed-radius is first an RTDL kernel relation; V4 then maps that "
            "relation to a concrete operator surface"
        ),
        "kernel_mode": kernel,
        "v4_mode": v4,
        "same_semantics": {
            "relation": "fixed_radius_neighbor_rows",
            "kernel_output_field": "neighbor_rows",
            "v4_execution_target": v4["surface"],
        },
    }


def run_legacy_visible_flow() -> dict[str, object]:
    case = make_case()
    query_points = (
        {"id": point.id, "x": point.x, "y": point.y}
        for point in case["query_points"]
    )
    search_points = (
        {"id": point.id, "x": point.x, "y": point.y}
        for point in case["search_points"]
    )
    query_points = tuple(query_points)
    search_points = tuple(search_points)
    radius = 0.5
    radius_sq = radius * radius

    candidate_checks = []
    neighbor_rows = []
    for query in query_points:
        for candidate in search_points:
            distance_sq = _distance_sq(
                Point(id=int(query["id"]), x=float(query["x"]), y=float(query["y"])),
                Point(id=int(candidate["id"]), x=float(candidate["x"]), y=float(candidate["y"])),
            )
            inside_radius = distance_sq <= radius_sq
            candidate_checks.append(
                {
                    "query_id": int(query["id"]),
                    "candidate_id": int(candidate["id"]),
                    "distance_sq": round(distance_sq, 4),
                    "inside_radius": inside_radius,
                }
            )
            if inside_radius:
                neighbor_rows.append(
                    {
                        "query_id": int(query["id"]),
                        "neighbor_id": int(candidate["id"]),
                        "distance_sq": round(distance_sq, 4),
                    }
                )

    neighbor_rows.sort(key=lambda row: (row["query_id"], row["distance_sq"], row["neighbor_id"]))
    counts_by_query = {
        int(query["id"]): sum(1 for row in neighbor_rows if row["query_id"] == int(query["id"]))
        for query in query_points
    }
    threshold_rows = tuple(
        {
            "query_id": query_id,
            "neighbor_count": count,
            "threshold_reached": count >= 2,
        }
        for query_id, count in sorted(counts_by_query.items())
    )

    return {
        "status": "ok",
        "mode": "visible_python_flow",
        "concept": "manual mirror of the fixed-radius relation rows emitted by kernel mode",
        "manual_data_flow": (
            "query_points -> candidate checks -> neighbor relation rows -> count-threshold continuation"
        ),
        "radius": radius,
        "candidate_checks": candidate_checks,
        "neighbor_rows": tuple(neighbor_rows),
        "threshold_rows": threshold_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RTDL fixed-radius neighbor tutorial")
    parser.add_argument("--mode", choices=("kernel", "v4", "both", "visible"), default="both")
    args = parser.parse_args()
    if args.mode == "kernel":
        payload = run_kernel_mode()
    elif args.mode == "v4":
        payload = run_v4_mode()
    elif args.mode == "visible":
        payload = run_legacy_visible_flow()
    else:
        payload = run_both_modes()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
