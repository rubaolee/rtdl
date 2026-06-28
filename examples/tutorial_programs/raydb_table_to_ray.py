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
    orders = (
        {"order_id": 1, "customer_id": 7, "x0": 0.0, "x1": 1.0, "amount": 30},
        {"order_id": 2, "customer_id": 7, "x0": 0.5, "x1": 1.5, "amount": 50},
        {"order_id": 3, "customer_id": 9, "x0": 2.0, "x1": 3.0, "amount": 80},
    )
    regions = (
        {"region_id": 100, "min_x": 0.25, "max_x": 1.25},
        {"region_id": 101, "min_x": 2.5, "max_x": 3.5},
    )
    ray_rows = tuple(
        {
            "ray_id": order["order_id"],
            "customer_id": order["customer_id"],
            "x0": order["x0"],
            "x1": order["x1"],
            "payload_amount": order["amount"],
        }
        for order in orders
    )
    primitive_rows = tuple(
        {"primitive_id": region["region_id"], "min_x": region["min_x"], "max_x": region["max_x"]}
        for region in regions
    )
    hit_rows = []
    for ray in ray_rows:
        for primitive in primitive_rows:
            hit = not (float(ray["x1"]) < float(primitive["min_x"]) or float(primitive["max_x"]) < float(ray["x0"]))
            if hit:
                hit_rows.append(
                    {
                        "ray_id": ray["ray_id"],
                        "customer_id": ray["customer_id"],
                        "primitive_id": primitive["primitive_id"],
                        "amount": ray["payload_amount"],
                    }
                )

    dedup_rows = tuple({key: row for key, row in ((row["ray_id"], row) for row in hit_rows)}.values())
    grouped_aggregates = tuple(
        {
            "customer_id": customer_id,
            "count": sum(1 for row in dedup_rows if row["customer_id"] == customer_id),
            "sum_amount": sum(int(row["amount"]) for row in dedup_rows if row["customer_id"] == customer_id),
        }
        for customer_id in sorted({row["customer_id"] for row in dedup_rows})
    )
    any_hit_plan = rtdl_v4.plan_operator_request_v4("any_hit", partner="torch")
    weighted_plan = rtdl_v4.plan_operator_request_v4("weighted_sum", partner="torch")
    grouped_plan = rtdl_v4.plan_operator_request_v4("grouped_sum", partner="cupy")
    payload = {
        "status": "ok",
        "concept": "RayDB-style programs lower table predicates into ray and primitive columns, keep payloads with hit rows, deduplicate, then aggregate",
        "manual_data_flow": "table rows -> rays + primitive intervals -> hit rows with payloads -> dedup -> grouped aggregate",
        "ray_rows": ray_rows,
        "primitive_rows": primitive_rows,
        "hit_rows": tuple(hit_rows),
        "dedup_rows": dedup_rows,
        "grouped_aggregates": grouped_aggregates,
        "v4_surfaces": {
            "hit": {"request": "any_hit", "status": any_hit_plan.status, "surface": any_hit_plan.api_surface},
            "weighted": {"request": "weighted_sum", "status": weighted_plan.status, "surface": weighted_plan.api_surface},
            "grouped": {"request": "grouped_sum", "status": grouped_plan.status, "surface": grouped_plan.api_surface},
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
