from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4
from rtdsl.reference import Point, fixed_radius_neighbors_cpu


def main() -> int:
    query_points = (
        Point(1, 0.0, 0.0),
        Point(2, 2.0, 0.0),
    )
    search_points = (
        Point(10, 0.1, 0.1),
        Point(11, 0.4, 0.0),
        Point(12, 2.2, 0.0),
        Point(13, 8.0, 8.0),
    )
    rows = fixed_radius_neighbors_cpu(
        query_points,
        search_points,
        radius=0.5,
        k_max=4,
    )
    plan = rtdl_v4.plan_operator_request_v4("fixed_radius", partner="torch")
    payload = {
        "status": "ok",
        "concept": "fixed-radius creates neighbor relation rows before the app decides what they mean",
        "radius": 0.5,
        "neighbor_rows": rows,
        "planner": {
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
