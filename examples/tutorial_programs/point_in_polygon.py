from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4
from rtdsl.reference import Point, Polygon, pip_cpu


def main() -> int:
    points = (
        Point(1, 0.25, 0.25),
        Point(2, 0.75, 0.75),
        Point(3, 2.50, 2.50),
    )
    polygons = (
        Polygon(10, ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))),
        Polygon(20, ((2.0, 2.0), (3.0, 2.0), (3.0, 3.0), (2.0, 3.0))),
    )

    hits = pip_cpu(points, polygons, result_mode="positive_hits")
    plan = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")

    payload = {
        "status": "ok",
        "concept": "point-in-polygon uses broadphase candidate discovery plus exact containment logic",
        "input": {
            "point_count": len(points),
            "polygon_count": len(polygons),
        },
        "positive_hits": tuple(
            {
                "point_id": int(row["point_id"]),
                "polygon_id": int(row["polygon_id"]),
            }
            for row in hits
        ),
        "planner": {
            "operator": "aabb_index_query",
            "partner": "rtdl_native",
            "status": plan.status,
            "surface": plan.api_surface,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
