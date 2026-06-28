from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def _distance_sq(left: dict[str, float | int | str], right: dict[str, float | int | str]) -> float:
    dx = float(left["x"]) - float(right["x"])
    dy = float(left["y"]) - float(right["y"])
    return dx * dx + dy * dy


def main() -> int:
    query_points = (
        {"id": 1, "x": 0.0, "y": 0.0, "search_group": "near_origin"},
        {"id": 2, "x": 4.0, "y": 0.0, "search_group": "near_four"},
    )
    search_points = (
        {"id": 100, "x": 0.2, "y": 0.0, "group": "near_origin"},
        {"id": 101, "x": 2.0, "y": 0.0, "group": "near_origin"},
        {"id": 102, "x": 4.1, "y": 0.1, "group": "near_four"},
        {"id": 103, "x": 7.0, "y": 0.0, "group": "near_four"},
    )
    search_groups = (
        {"group": "near_origin", "bounds": {"min_x": -0.5, "max_x": 2.5, "min_y": -0.5, "max_y": 0.5}},
        {"group": "near_four", "bounds": {"min_x": 3.5, "max_x": 7.5, "min_y": -0.5, "max_y": 0.5}},
    )

    candidate_rows = []
    for query in query_points:
        for candidate in search_points:
            if candidate["group"] != query["search_group"]:
                continue
            distance_sq = _distance_sq(query, candidate)
            candidate_rows.append(
                {
                    "query_id": int(query["id"]),
                    "candidate_id": int(candidate["id"]),
                    "search_group": str(candidate["group"]),
                    "distance_sq": round(distance_sq, 4),
                }
            )

    nearest_rows = []
    for query in query_points:
        rows_for_query = [
            row for row in candidate_rows if row["query_id"] == int(query["id"])
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

    plan = rtdl_v4.plan_operator_request_v4("point_group_nearest", partner="torch")
    payload = {
        "status": "ok",
        "concept": "NN in RTDL is nearest-witness relation building: prepare search groups, emit candidate distances, keep the argmin witness",
        "manual_data_flow": (
            "query_points + search_groups -> candidate witness rows -> per-query argmin continuation"
        ),
        "search_groups": search_groups,
        "candidate_rows": tuple(candidate_rows),
        "nearest_rows": tuple(nearest_rows),
        "v4_surface": {
            "operator": "point_group_nearest",
            "partner": "torch",
            "status": plan.status,
            "surface": plan.api_surface,
            "generic_primitive": plan.generic_primitive,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
