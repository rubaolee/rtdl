from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


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


def main() -> int:
    neighbor_rows = (
        {"point_id": 1, "neighbor_id": 2},
        {"point_id": 2, "neighbor_id": 1},
        {"point_id": 2, "neighbor_id": 3},
        {"point_id": 3, "neighbor_id": 2},
        {"point_id": 4, "neighbor_id": 5},
        {"point_id": 5, "neighbor_id": 4},
    )
    min_neighbors_for_core = 2
    point_ids = sorted({row["point_id"] for row in neighbor_rows} | {row["neighbor_id"] for row in neighbor_rows})
    neighbor_counts = {
        point_id: sum(1 for row in neighbor_rows if row["point_id"] == point_id)
        for point_id in point_ids
    }
    core_points = tuple(
        {"point_id": point_id, "neighbor_count": neighbor_counts[point_id], "is_core": neighbor_counts[point_id] >= min_neighbors_for_core}
        for point_id in point_ids
    )
    core_set = {row["point_id"] for row in core_points if row["is_core"]}
    parent = {point_id: point_id for point_id in point_ids}
    union_edges = []
    for row in neighbor_rows:
        left = int(row["point_id"])
        right = int(row["neighbor_id"])
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

    plan = rtdl_v4.plan_operator_request_v4("component_union", partner="numba")
    payload = {
        "status": "ok",
        "concept": "RTDBSCAN continues a radius-neighbor relation by marking core points and unioning density-reachable edges",
        "manual_data_flow": "neighbor rows -> core flags -> union edges -> component labels -> component-size signature",
        "neighbor_rows": neighbor_rows,
        "core_points": core_points,
        "union_edges": tuple(union_edges),
        "component_labels": labels,
        "component_signature": signature,
        "v4_surface": {
            "request": "component_union",
            "partner": "numba",
            "status": plan.status,
            "surface": plan.api_surface,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
