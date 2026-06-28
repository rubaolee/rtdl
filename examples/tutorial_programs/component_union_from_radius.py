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
def radius_edges_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=0.55, k_max=8))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


def make_case() -> dict[str, tuple[Point, ...]]:
    points = (
        Point(id=1, x=0.0, y=0.0),
        Point(id=2, x=0.2, y=0.0),
        Point(id=3, x=0.4, y=0.0),
        Point(id=4, x=4.0, y=0.0),
        Point(id=5, x=4.2, y=0.0),
    )
    return {"query_points": points, "search_points": points}


def _find(parent: dict[int, int], value: int) -> int:
    while parent[value] != value:
        parent[value] = parent[parent[value]]
        value = parent[value]
    return value


def _union(parent: dict[int, int], left: int, right: int) -> None:
    root_left = _find(parent, left)
    root_right = _find(parent, right)
    if root_left != root_right:
        parent[max(root_left, root_right)] = min(root_left, root_right)


def _component_union_from_neighbor_rows(
    neighbor_rows: tuple[dict[str, float | int], ...],
    *,
    min_neighbors_for_core: int,
) -> dict[str, object]:
    point_ids = sorted({int(row["query_id"]) for row in neighbor_rows} | {int(row["neighbor_id"]) for row in neighbor_rows})
    neighbor_counts = {
        point_id: sum(1 for row in neighbor_rows if int(row["query_id"]) == point_id)
        for point_id in point_ids
    }
    core_points = tuple(
        {
            "point_id": point_id,
            "neighbor_count": neighbor_counts[point_id],
            "is_core": neighbor_counts[point_id] >= min_neighbors_for_core,
        }
        for point_id in point_ids
    )
    core_set = {int(row["point_id"]) for row in core_points if row["is_core"]}
    parent = {point_id: point_id for point_id in point_ids}
    union_edges = []
    for row in neighbor_rows:
        left = int(row["query_id"])
        right = int(row["neighbor_id"])
        if left == right:
            continue
        if left in core_set or right in core_set:
            _union(parent, left, right)
            union_edges.append({"left": left, "right": right, "reason": "density_reachable"})

    labels = tuple(
        {"point_id": point_id, "component": _find(parent, point_id)}
        for point_id in point_ids
    )
    signature = tuple(
        {"component": component, "size": sum(1 for row in labels if row["component"] == component)}
        for component in sorted({row["component"] for row in labels})
    )
    return {
        "core_points": core_points,
        "union_edges": tuple(union_edges),
        "component_labels": labels,
        "component_signature": signature,
    }


def run_kernel_mode() -> dict[str, object]:
    case = make_case()
    compiled = rt.compile_kernel(radius_edges_kernel)
    rows = tuple(rt.run_cpu_python_reference(radius_edges_kernel, **case))
    neighbor_rows = tuple(
        {
            "query_id": int(row["query_id"]),
            "neighbor_id": int(row["neighbor_id"]),
            "distance": round(float(row["distance"]), 4),
        }
        for row in rows
        if int(row["query_id"]) != int(row["neighbor_id"])
    )
    continuation = _component_union_from_neighbor_rows(neighbor_rows, min_neighbors_for_core=2)
    return {
        "mode": "kernel_plus_continuation",
        "status": "ok",
        "teaches": (
            "RTDL kernel emits fixed-radius neighbor rows; component union is an "
            "app-owned continuation over those rows"
        ),
        "kernel_summary": compiled.format(),
        "neighbor_rows": neighbor_rows,
        **continuation,
    }


def run_visible_flow() -> dict[str, object]:
    neighbor_rows = (
        {"query_id": 1, "neighbor_id": 2, "distance": 0.2},
        {"query_id": 1, "neighbor_id": 3, "distance": 0.4},
        {"query_id": 2, "neighbor_id": 1, "distance": 0.2},
        {"query_id": 2, "neighbor_id": 3, "distance": 0.2},
        {"query_id": 3, "neighbor_id": 1, "distance": 0.4},
        {"query_id": 3, "neighbor_id": 2, "distance": 0.2},
        {"query_id": 4, "neighbor_id": 5, "distance": 0.2},
        {"query_id": 5, "neighbor_id": 4, "distance": 0.2},
    )
    continuation = _component_union_from_neighbor_rows(neighbor_rows, min_neighbors_for_core=2)
    return {
        "mode": "visible_python_flow",
        "status": "ok",
        "concept": "manual mirror of radius-neighbor rows continued into density components",
        "manual_data_flow": "neighbor rows -> core flags -> union edges -> component labels",
        "neighbor_rows": neighbor_rows,
        **continuation,
    }


def run_v4_mode() -> dict[str, object]:
    plan = rtdl_v4.plan_operator_request_v4("component_union", partner="numba")
    return {
        "mode": "v4",
        "status": "ok",
        "teaches": "V4 operator/runtime mapping for component-union continuation over radius rows",
        "operator": "component_union",
        "partner": "numba",
        "plan_status": plan.status,
        "surface": plan.api_surface,
        "generic_primitive": plan.generic_primitive,
        "relationship_to_kernel": (
            "The kernel produces neighbor rows. Component union consumes the row "
            "graph and writes compact labels. V4 provides the measured Numba "
            "continuation surface for this recognized pattern."
        ),
    }


def run_both_modes() -> dict[str, object]:
    kernel = run_kernel_mode()
    v4 = run_v4_mode()
    return {
        "status": "ok",
        "concept": "component union is a continuation over RTDL radius-neighbor rows",
        "kernel_mode": kernel,
        "visible_flow": run_visible_flow(),
        "v4_mode": v4,
        "same_semantics": {
            "relation": "radius_neighbor_rows_to_component_labels",
            "kernel_output_field": "neighbor_rows",
            "continuation_output_field": "component_labels",
            "v4_execution_target": v4["surface"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RTDL component-union tutorial")
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
