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


def make_case() -> dict[str, object]:
    return {
        "bodies": (
            {"id": 1, "x": 0.0, "y": 0.0, "mass": 1.0},
            {"id": 2, "x": 0.2, "y": 0.1, "mass": 1.0},
            {"id": 3, "x": 3.0, "y": 0.0, "mass": 2.0},
        ),
        "aggregate_cells": (
            {"id": 100, "x": 0.1, "y": 0.05, "mass": 2.0, "half_width": 0.3},
            {"id": 101, "x": 3.0, "y": 0.0, "mass": 2.0, "half_width": 0.2},
        ),
        "theta": 0.5,
    }


def _contribution(body: dict[str, float | int], source: dict[str, float | int]) -> dict[str, float | int]:
    dx = float(source["x"]) - float(body["x"])
    dy = float(source["y"]) - float(body["y"])
    dist_sq = dx * dx + dy * dy + 0.01
    inv_dist3 = 1.0 / (dist_sq ** 1.5)
    return {
        "body_id": int(body["id"]),
        "source_id": int(source["id"]),
        "fx": round(float(source["mass"]) * dx * inv_dist3, 6),
        "fy": round(float(source["mass"]) * dy * inv_dist3, 6),
    }


def _frontier_rows(case: dict[str, object]) -> tuple[dict[str, float | int | str], ...]:
    bodies = case["bodies"]
    aggregate_cells = case["aggregate_cells"]
    theta = float(case["theta"])
    frontier_rows = []
    for body in bodies:
        for cell in aggregate_cells:
            dx = float(cell["x"]) - float(body["x"])
            dy = float(cell["y"]) - float(body["y"])
            distance = (dx * dx + dy * dy + 1.0e-9) ** 0.5
            width = 2.0 * float(cell["half_width"])
            accepts_aggregate = width / distance < theta
            if accepts_aggregate:
                frontier_rows.append(
                    {
                        "body_id": int(body["id"]),
                        "frontier_id": int(cell["id"]),
                        "kind": "aggregate_cell",
                        "opening_ratio": round(width / distance, 4),
                    }
                )
            else:
                for other in bodies:
                    if int(other["id"]) == int(body["id"]):
                        continue
                    frontier_rows.append(
                        {
                            "body_id": int(body["id"]),
                            "frontier_id": int(other["id"]),
                            "kind": "exact_body",
                            "opening_ratio": round(width / distance, 4),
                        }
                    )
                break
    return tuple(frontier_rows)


def _force_rows(case: dict[str, object], frontier_rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    bodies = case["bodies"]
    aggregate_cells = case["aggregate_cells"]
    sources_by_id = {
        **{int(body["id"]): body for body in bodies},
        **{
            int(cell["id"]): {"id": cell["id"], "x": cell["x"], "y": cell["y"], "mass": cell["mass"]}
            for cell in aggregate_cells
        },
    }
    contribution_rows = tuple(
        _contribution(
            next(body for body in bodies if int(body["id"]) == int(row["body_id"])),
            sources_by_id[int(row["frontier_id"])],
        )
        for row in frontier_rows
    )
    force_by_body = []
    for body in bodies:
        rows = [row for row in contribution_rows if row["body_id"] == int(body["id"])]
        force_by_body.append(
            {
                "body_id": int(body["id"]),
                "fx": round(sum(float(row["fx"]) for row in rows), 6),
                "fy": round(sum(float(row["fy"]) for row in rows), 6),
                "frontier_count": len(rows),
            }
        )
    return {"contribution_rows": contribution_rows, "force_by_body": tuple(force_by_body)}


def run_relation_mode() -> dict[str, object]:
    case = make_case()
    frontier_rows = _frontier_rows(case)
    force = _force_rows(case, frontier_rows)
    return {
        "tutorial_classification": "core_tutorial_program_relation_first",
        "kernel_programming_method": (
            "Model the program as emitted frontier rows, then apply a grouped "
            "weighted-vector continuation. The current public kernel syntax does "
            "not expose aggregate-frontier as an @rt.kernel predicate, so this "
            "lesson teaches the RTDL relation contract explicitly before V4."
        ),
        "mode": "relation_first",
        "status": "ok",
        "teaches": (
            "Aggregate frontier is a generic row relation: each source body keeps "
            "either an aggregate-cell row or exact-body rows, then a weighted "
            "continuation reduces vector contributions per body"
        ),
        "honesty_note": (
            "The current public tutorial API does not expose aggregate frontier "
            "as an @rt.kernel predicate. This lesson teaches the relation shape "
            "first, then shows the V4 prepared operator surface."
        ),
        "theta": case["theta"],
        "bodies": case["bodies"],
        "aggregate_cells": case["aggregate_cells"],
        "frontier_rows": frontier_rows,
        **force,
    }


def run_visible_flow() -> dict[str, object]:
    relation = run_relation_mode()
    return {
        "mode": "visible_python_flow",
        "status": "ok",
        "concept": "manual aggregate-frontier opening rule plus grouped vector continuation",
        "manual_data_flow": "bodies + aggregate cells -> frontier rows -> contribution rows -> grouped vector force",
        "theta": relation["theta"],
        "frontier_rows": relation["frontier_rows"],
        "contribution_rows": relation["contribution_rows"],
        "force_by_body": relation["force_by_body"],
    }


def run_v4_mode() -> dict[str, object]:
    frontier_plan = rtdl_v4.plan_operator_request_v4("aggregate_frontier", partner="rtdl_native")
    grouped_plan = rtdl_v4.plan_operator_request_v4("grouped_sum", partner="cupy")
    return {
        "mode": "v4",
        "status": "ok",
        "teaches": "V4 operator/runtime mapping for aggregate-frontier rows and grouped weighted continuation",
        "v4_surfaces": {
            "frontier": {
                "request": "aggregate_frontier",
                "partner": "rtdl_native",
                "status": frontier_plan.status,
                "surface": frontier_plan.api_surface,
                "generic_primitive": frontier_plan.generic_primitive,
            },
            "continuation": {
                "request": "grouped_sum",
                "partner": "cupy",
                "status": grouped_plan.status,
                "surface": grouped_plan.api_surface,
                "generic_primitive": grouped_plan.generic_primitive,
            },
        },
        "relationship_to_relation": (
            "The relation-first mode names the rows. The V4 frontier surface is "
            "the prepared route for row generation, and the grouped_sum surface "
            "is the explicit partner continuation that consumes those rows."
        ),
    }


def run_both_modes() -> dict[str, object]:
    relation = run_relation_mode()
    v4 = run_v4_mode()
    return {
        "status": "ok",
        "concept": "aggregate frontier is relation-first and V4-prepared-surface second",
        "relation_mode": relation,
        "visible_flow": run_visible_flow(),
        "v4_mode": v4,
        "same_semantics": {
            "relation": "aggregate_or_exact_frontier_rows_to_weighted_force_rows",
            "relation_output_field": "frontier_rows",
            "continuation_output_field": "force_by_body",
            "v4_frontier_target": v4["v4_surfaces"]["frontier"]["surface"],
            "v4_continuation_target": v4["v4_surfaces"]["continuation"]["surface"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RTDL aggregate-frontier tutorial")
    parser.add_argument("--mode", choices=("relation", "v4", "both", "visible"), default="both")
    args = parser.parse_args()
    if args.mode == "relation":
        payload = run_relation_mode()
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
