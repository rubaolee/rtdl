from __future__ import annotations

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


def main() -> int:
    moving_shapes = (
        {"shape_id": 1, "min_x": 0.0, "min_y": 0.0, "max_x": 1.0, "max_y": 1.0},
        {"shape_id": 2, "min_x": 2.0, "min_y": 0.0, "max_x": 3.0, "max_y": 1.0},
    )
    static_shapes = (
        {"shape_id": 10, "min_x": 0.8, "min_y": 0.2, "max_x": 1.2, "max_y": 0.7},
        {"shape_id": 11, "min_x": 4.0, "min_y": 0.0, "max_x": 5.0, "max_y": 1.0},
    )
    broadphase_rows = tuple(
        {"pair_id": index + 1, "moving_id": moving["shape_id"], "static_id": static["shape_id"]}
        for index, (moving, static) in enumerate(
            (pair for pair in ((m, s) for m in moving_shapes for s in static_shapes) if _overlaps(pair[0], pair[1]))
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
    capacity = 2
    bounded_witness_rows = []
    validation_rows = []
    for pair in broadphase_rows:
        rows = [row for row in witness_candidates if row["pair_id"] == pair["pair_id"]]
        rows.sort(key=lambda row: (-float(row["depth"]), int(row["witness_id"])))
        bounded_witness_rows.extend({**row, "slot": slot} for slot, row in enumerate(rows[:capacity]))
        validation_rows.append(
            {
                "pair_id": pair["pair_id"],
                "candidate_count": len(rows),
                "kept_count": min(len(rows), capacity),
                "capacity": capacity,
                "overflowed": len(rows) > capacity,
            }
        )

    aabb_plan = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
    closest_plan = rtdl_v4.plan_operator_request_v4("closest_hit_argmin", partner="torch")
    payload = {
        "status": "ok",
        "concept": "Contact manifold starts with broadphase shape pairs, refines them into contact witnesses, and keeps a bounded witness set per pair",
        "manual_data_flow": "shape bounds -> broadphase candidate pairs -> witness candidates -> bounded witness rows -> overflow validation",
        "moving_shapes": moving_shapes,
        "static_shapes": static_shapes,
        "broadphase_rows": broadphase_rows,
        "witness_candidates": witness_candidates,
        "bounded_witness_rows": tuple(bounded_witness_rows),
        "validation_rows": tuple(validation_rows),
        "v4_surfaces": {
            "broadphase": {"request": "aabb_index_query", "status": aabb_plan.status, "surface": aabb_plan.api_surface},
            "refine": {"request": "closest_hit_argmin", "status": closest_plan.status, "surface": closest_plan.api_surface},
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
