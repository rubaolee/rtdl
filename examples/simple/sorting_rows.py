from __future__ import annotations

import json
from collections import defaultdict

import rtdsl.v4 as rtdl_v4


def main() -> int:
    hit_rows = [
        {"query": 0, "candidate": 8, "distance": 0.42, "weight": 2.0},
        {"query": 0, "candidate": 3, "distance": 0.18, "weight": 1.5},
        {"query": 1, "candidate": 2, "distance": 0.31, "weight": 0.5},
        {"query": 1, "candidate": 7, "distance": 0.11, "weight": 3.0},
        {"query": 2, "candidate": 5, "distance": 0.27, "weight": 4.0},
    ]

    sorted_rows = sorted(
        hit_rows,
        key=lambda row: (row["query"], row["distance"], row["candidate"]),
    )

    nearest_by_query: dict[int, dict[str, float | int]] = {}
    weight_sum_by_query: defaultdict[int, float] = defaultdict(float)
    for row in sorted_rows:
        nearest_by_query.setdefault(row["query"], row)
        weight_sum_by_query[row["query"]] += row["weight"]

    nearest_plan = rtdl_v4.plan_operator_request_v4(
        "point_group_nearest",
        partner="torch",
    )
    grouped_sum_plan = rtdl_v4.plan_operator_request_v4(
        "grouped_sum",
        partner="cupy",
    )

    payload = {
        "status": "ok",
        "idea": "sort relation rows, then continue with top-k or grouped summaries",
        "sorted_rows": sorted_rows,
        "nearest_by_query": {
            str(query): row for query, row in sorted(nearest_by_query.items())
        },
        "weight_sum_by_query": {
            str(query): weight
            for query, weight in sorted(weight_sum_by_query.items())
        },
        "planner": {
            "nearest": {
                "status": nearest_plan.status,
                "surface": nearest_plan.api_surface,
            },
            "grouped_sum": {
                "status": grouped_sum_plan.status,
                "surface": grouped_sum_plan.api_surface,
            },
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
