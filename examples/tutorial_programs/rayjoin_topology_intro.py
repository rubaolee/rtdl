from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def main() -> int:
    left_edges = (
        {"edge_id": 1, "shape_id": "A", "side": "left", "x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 1.0},
        {"edge_id": 2, "shape_id": "A", "side": "right", "x0": 1.0, "y0": 0.0, "x1": 1.0, "y1": 1.0},
    )
    right_edges = (
        {"edge_id": 10, "shape_id": "B", "side": "left", "x0": 0.0, "y0": 1.0, "x1": 1.0, "y1": 0.0},
        {"edge_id": 11, "shape_id": "B", "side": "right", "x0": 2.0, "y0": 0.0, "x1": 2.0, "y1": 1.0},
    )
    boundary_policy = "include_boundary_once_by_left_owner"
    candidate_pairs = tuple(
        {"left_edge": left["edge_id"], "right_edge": right["edge_id"], "owner": left["shape_id"]}
        for left in left_edges
        for right in right_edges
        if max(min(left["x0"], left["x1"]), min(right["x0"], right["x1"])) <= min(max(left["x0"], left["x1"]), max(right["x0"], right["x1"]))
        and max(min(left["y0"], left["y1"]), min(right["y0"], right["y1"])) <= min(max(left["y0"], left["y1"]), max(right["y0"], right["y1"]))
    )
    topology_rows = tuple(
        {
            **row,
            "boundary_policy": boundary_policy,
            "emit": row["owner"] == "A",
        }
        for row in candidate_pairs
    )
    emitted_rows = tuple(row for row in topology_rows if row["emit"])
    aabb_plan = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
    hit_plan = rtdl_v4.plan_operator_request_v4("any_hit", partner="torch")
    payload = {
        "status": "ok",
        "concept": "RayJoin is not only pair discovery: it also applies topology and boundary policy before rows become join output",
        "manual_data_flow": "shape edges -> AABB candidate pairs -> intersection tests -> topology rows -> boundary-policy filtered output",
        "boundary_policy": boundary_policy,
        "candidate_pairs": candidate_pairs,
        "topology_rows": topology_rows,
        "emitted_rows": emitted_rows,
        "v4_surfaces": {
            "broadphase": {"request": "aabb_index_query", "status": aabb_plan.status, "surface": aabb_plan.api_surface},
            "refine": {"request": "any_hit", "status": hit_plan.status, "surface": hit_plan.api_surface},
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
