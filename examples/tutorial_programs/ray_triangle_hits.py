from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4
from rtdsl.reference import Ray2D, Triangle, ray_triangle_any_hit_cpu


def main() -> int:
    rays = (
        Ray2D(1, -1.0, 0.25, 1.0, 0.0, 4.0),
        Ray2D(2, -1.0, 2.0, 1.0, 0.0, 4.0),
    )
    triangles = (
        Triangle(10, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0),
        Triangle(20, 2.0, 0.0, 3.0, 0.0, 2.0, 1.0),
    )
    hit_rows = ray_triangle_any_hit_cpu(rays, triangles)
    plan = rtdl_v4.plan_operator_request_v4("any_hit", partner="torch")
    payload = {
        "status": "ok",
        "concept": "ray/triangle any-hit creates one hit flag per ray; the app decides what a hit means",
        "hit_rows": hit_rows,
        "planner": {
            "operator": "any_hit",
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
