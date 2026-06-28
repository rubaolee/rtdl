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


def _overlaps(left: dict[str, float | int], right: dict[str, float | int]) -> bool:
    return not (
        float(left["max_x"]) < float(right["min_x"])
        or float(right["max_x"]) < float(left["min_x"])
        or float(left["max_y"]) < float(right["min_y"])
        or float(right["max_y"]) < float(left["min_y"])
    )


def _input_shapes() -> tuple[tuple[dict[str, float | int], ...], tuple[dict[str, float | int], ...]]:
    moving_shapes = (
        {"shape_id": 1, "min_x": 0.0, "min_y": 0.0, "max_x": 1.0, "max_y": 1.0},
        {"shape_id": 2, "min_x": 2.0, "min_y": 0.0, "max_x": 3.0, "max_y": 1.0},
    )
    static_shapes = (
        {"shape_id": 10, "min_x": 0.8, "min_y": 0.2, "max_x": 1.2, "max_y": 0.7},
        {"shape_id": 11, "min_x": 4.0, "min_y": 0.0, "max_x": 5.0, "max_y": 1.0},
    )
    return moving_shapes, static_shapes


def _contact_relation(capacity: int = 2) -> dict[str, object]:
    moving_shapes, static_shapes = _input_shapes()
    broadphase_rows = tuple(
        {"pair_id": index + 1, "moving_id": moving["shape_id"], "static_id": static["shape_id"]}
        for index, (moving, static) in enumerate(
            pair for pair in ((m, s) for m in moving_shapes for s in static_shapes) if _overlaps(pair[0], pair[1])
        )
    )
    witness_candidates = tuple(
        {
            "pair_id": row["pair_id"],
            "witness_id": row["pair_id"] * 100 + slot,
            "normal_x": -1.0,
            "normal_y": 0.0,
            "depth": round(0.04 + slot * 0.02, 3),
        }
        for row in broadphase_rows
        for slot in (1, 2, 3)
    )
    bounded_witness_rows: list[dict[str, float | int]] = []
    validation_rows: list[dict[str, bool | int]] = []
    for pair in broadphase_rows:
        rows = [row for row in witness_candidates if int(row["pair_id"]) == int(pair["pair_id"])]
        rows.sort(key=lambda row: (-float(row["depth"]), int(row["witness_id"])))
        bounded_witness_rows.extend({**row, "slot": slot} for slot, row in enumerate(rows[:capacity]))
        validation_rows.append(
            {
                "pair_id": int(pair["pair_id"]),
                "candidate_count": len(rows),
                "kept_count": min(len(rows), capacity),
                "capacity": capacity,
                "overflowed": len(rows) > capacity,
            }
        )
    return {
        "moving_shapes": moving_shapes,
        "static_shapes": static_shapes,
        "broadphase_rows": broadphase_rows,
        "witness_candidates": witness_candidates,
        "bounded_witness_rows": tuple(bounded_witness_rows),
        "validation_rows": tuple(validation_rows),
    }


def run_relation_mode() -> dict[str, object]:
    return {
        "tutorial_classification": "core_tutorial_program_relation_first",
        "kernel_programming_method": (
            "Write the problem as broadphase candidate rows followed by bounded "
            "witness rows. A future direct kernel would emit those rows; the V4 "
            "surface only executes recognized pieces after the relation is clear."
        ),
        "status": "ok",
        "mode": "relation",
        "concept": "contact manifold lowering is broadphase rows followed by bounded witness continuation",
        "manual_data_flow": "shape bounds -> broadphase candidate pairs -> witness candidates -> bounded witness rows -> overflow validation",
        **_contact_relation(),
    }


def run_visible_mode() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "visible_python_flow",
        "concept": "one overlapping pair produces several witness candidates; the continuation keeps the deepest two",
        "pair_id": 1,
        "candidate_depths": (0.06, 0.08, 0.10),
        "kept_depths": (0.10, 0.08),
        "overflowed": True,
    }


def run_v4_mode() -> dict[str, object]:
    aabb_plan = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
    closest_plan = rtdl_v4.plan_operator_request_v4("closest_hit_argmin", partner="torch")
    return {
        "status": "ok",
        "mode": "v4",
        "relationship_to_relation": "The relation mode names broadphase pair rows and bounded witness rows. V4 maps those shapes to AABB query and closest-hit grouped argmin surfaces.",
        "v4_surfaces": {
            "broadphase": {
                "request": "aabb_index_query",
                "partner": "rtdl_native",
                "status": aabb_plan.status,
                "surface": aabb_plan.api_surface,
            },
            "witness": {
                "request": "closest_hit_argmin",
                "partner": "torch",
                "status": closest_plan.status,
                "surface": closest_plan.api_surface,
            },
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Contact manifold lowering from relation rows.")
    parser.add_argument("--mode", choices=("relation", "v4", "both", "visible"), default="both")
    args = parser.parse_args(argv)

    payload: dict[str, object] = {
        "status": "ok",
        "concept": "contact manifold is assembled from broadphase and bounded witness rows",
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
