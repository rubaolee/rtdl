from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def _distance_sq(left: dict[str, float | int], right: dict[str, float | int]) -> float:
    dx = float(left["x"]) - float(right["x"])
    dy = float(left["y"]) - float(right["y"])
    return dx * dx + dy * dy


def main() -> int:
    query_points = (
        {"id": 1, "x": 0.0, "y": 0.0},
        {"id": 2, "x": 2.0, "y": 0.0},
    )
    search_points = (
        {"id": 10, "x": 0.1, "y": 0.1},
        {"id": 11, "x": 0.4, "y": 0.0},
        {"id": 12, "x": 2.2, "y": 0.0},
        {"id": 13, "x": 8.0, "y": 8.0},
    )
    radius = 0.5
    radius_sq = radius * radius

    candidate_checks = []
    neighbor_rows = []
    for query in query_points:
        for candidate in search_points:
            distance_sq = _distance_sq(query, candidate)
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

    plan = rtdl_v4.plan_operator_request_v4("fixed_radius", partner="torch")
    payload = {
        "status": "ok",
        "concept": "fixed-radius is a relation-building problem: test candidates, emit neighbor rows, then continue with counts or labels",
        "manual_data_flow": (
            "query_points -> candidate checks -> neighbor relation rows -> count-threshold continuation"
        ),
        "radius": radius,
        "candidate_checks": candidate_checks,
        "neighbor_rows": tuple(neighbor_rows),
        "threshold_rows": threshold_rows,
        "v4_surface": {
            "operator": "fixed_radius",
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
