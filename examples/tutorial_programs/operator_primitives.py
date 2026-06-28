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
    relation_row_examples = (
        {
            "relation": "fixed_radius_neighbor",
            "row": {"query_id": 1, "neighbor_id": 10, "distance_sq": 0.02},
            "meaning": "query 1 has neighbor 10 inside the requested radius",
        },
        {
            "relation": "nearest_witness",
            "row": {"query_id": 2, "neighbor_id": 102, "distance_sq": 0.02, "rank": 1},
            "meaning": "candidate 102 is the closest witness for query 2",
        },
        {
            "relation": "ray_triangle_hit",
            "row": {"ray_id": 7, "triangle_id": 42, "hit": True},
            "meaning": "ray 7 intersects triangle 42",
        },
        {
            "relation": "aabb_overlap",
            "row": {"left_box_id": 3, "right_box_id": 8, "overlaps": True},
            "meaning": "box 3 overlaps box 8",
        },
    )

    operator_catalog_rows = []
    continuation_classes = []
    for row in rtdl_v4.measured_operator_catalog_v4():
        operator_catalog_rows.append(
            {
                "operator_surface": row["api_surface"],
                "generic_primitive": row["generic_primitive"],
                "continuation_class": row["continuation_class"],
                "partners": row["measured_partners"],
            }
        )
        continuation_classes.append(row["continuation_class"])
    payload = {
        "status": "ok",
        "tutorial_classification": "core_concept_map_not_execution_program",
        "not_a_kernel_execution_example": True,
        "kernel_first_requirement": "Use this as a vocabulary map after hello_world.py and sorting_rows.py; executable relation tutorials follow it.",
        "concept": "V4 operator surfaces produce relation rows; continuations turn those rows into app output",
        "manual_data_flow": "input objects -> candidate rows -> refined relation rows -> continuation rows -> app output",
        "relation_row_examples": relation_row_examples,
        "operator_catalog_rows": operator_catalog_rows,
        "continuation_classes": sorted(set(continuation_classes)),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
