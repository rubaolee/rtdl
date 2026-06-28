from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4
from rtdsl.reference import Point, knn_rows_cpu


def main() -> int:
    query_points = (
        Point(1, 0.0, 0.0),
        Point(2, 4.0, 0.0),
    )
    search_points = (
        Point(100, 0.2, 0.0),
        Point(101, 2.0, 0.0),
        Point(102, 4.1, 0.1),
        Point(103, 7.0, 0.0),
    )
    nearest_rows = knn_rows_cpu(query_points, search_points, k=1)
    plan = rtdl_v4.plan_operator_request_v4("point_group_nearest", partner="torch")
    payload = {
        "status": "ok",
        "concept": "nearest neighbor is a nearest-witness relation; the app consumes the witness rows",
        "k": 1,
        "nearest_rows": nearest_rows,
        "planner": {
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
