from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def _table_relation() -> dict[str, object]:
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
    hit_rows: list[dict[str, int]] = []
    for ray in ray_rows:
        for primitive in primitive_rows:
            hit = not (float(ray["x1"]) < float(primitive["min_x"]) or float(primitive["max_x"]) < float(ray["x0"]))
            if hit:
                hit_rows.append(
                    {
                        "ray_id": int(ray["ray_id"]),
                        "customer_id": int(ray["customer_id"]),
                        "primitive_id": int(primitive["primitive_id"]),
                        "amount": int(ray["payload_amount"]),
                    }
                )

    dedup_rows = tuple({int(row["ray_id"]): row for row in hit_rows}.values())
    grouped_aggregates = tuple(
        {
            "customer_id": customer_id,
            "count": sum(1 for row in dedup_rows if int(row["customer_id"]) == customer_id),
            "sum_amount": sum(int(row["amount"]) for row in dedup_rows if int(row["customer_id"]) == customer_id),
        }
        for customer_id in sorted({int(row["customer_id"]) for row in dedup_rows})
    )
    return {
        "orders": orders,
        "regions": regions,
        "ray_rows": ray_rows,
        "primitive_rows": primitive_rows,
        "hit_rows": tuple(hit_rows),
        "dedup_rows": dedup_rows,
        "grouped_aggregates": grouped_aggregates,
    }


def run_relation_mode() -> dict[str, object]:
    return {
        "tutorial_classification": "core_tutorial_program_relation_first",
        "kernel_programming_method": (
            "Lower table rows into rays carrying payload columns, emit hit rows, "
            "deduplicate, then group. V4 surfaces execute recognized hit and "
            "grouped-continuation shapes after this lowering is understood."
        ),
        "status": "ok",
        "mode": "relation",
        "concept": "RayDB-style lowering keeps table payloads attached to RTDL hit rows, then applies database-style grouping",
        "manual_data_flow": "table rows -> rays + primitive intervals -> hit rows with payloads -> dedup -> grouped aggregate",
        **_table_relation(),
    }


def run_visible_mode() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "visible_python_flow",
        "concept": "an order row becomes a ray row carrying payload_amount; a hit row carries the payload into grouping",
        "order_row": {"order_id": 1, "customer_id": 7, "x0": 0.0, "x1": 1.0, "amount": 30},
        "ray_row": {"ray_id": 1, "customer_id": 7, "x0": 0.0, "x1": 1.0, "payload_amount": 30},
        "hit_row": {"ray_id": 1, "customer_id": 7, "primitive_id": 100, "amount": 30},
        "aggregate_row": {"customer_id": 7, "count": 2, "sum_amount": 80},
    }


def run_v4_mode() -> dict[str, object]:
    any_hit_plan = rtdl_v4.plan_operator_request_v4("any_hit", partner="torch")
    weighted_plan = rtdl_v4.plan_operator_request_v4("any_hit_weighted_sum", partner="torch")
    grouped_plan = rtdl_v4.plan_operator_request_v4("grouped_sum", partner="cupy")
    return {
        "status": "ok",
        "mode": "v4",
        "relationship_to_relation": "The relation mode names table-to-ray payload rows, hit rows, dedup rows, and grouped aggregate rows. V4 maps the recognized hit and grouped continuation shapes to explicit partner surfaces.",
        "v4_surfaces": {
            "hit": {
                "request": "any_hit",
                "partner": "torch",
                "status": any_hit_plan.status,
                "surface": any_hit_plan.api_surface,
            },
            "weighted": {
                "request": "any_hit_weighted_sum",
                "partner": "torch",
                "status": weighted_plan.status,
                "surface": weighted_plan.api_surface,
            },
            "grouped": {
                "request": "grouped_sum",
                "partner": "cupy",
                "status": grouped_plan.status,
                "surface": grouped_plan.api_surface,
            },
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RayDB-style table-to-ray lowering tutorial.")
    parser.add_argument("--mode", choices=("relation", "v4", "both", "visible"), default="both")
    args = parser.parse_args(argv)

    payload: dict[str, object] = {
        "status": "ok",
        "concept": "table rows can be lowered into RTDL ray rows with payloads and grouped continuations",
    }
    if args.mode in {"relation", "both"}:
        payload["relation_mode"] = run_relation_mode()
    if args.mode in {"v4", "both"}:
        payload["v4_mode"] = run_v4_mode()
    if args.mode == "visible":
        payload["visible_flow"] = run_visible_mode()

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
