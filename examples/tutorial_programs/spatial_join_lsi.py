from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.aabb_index import aabb_intersection_pair_rows_2d
import rtdsl.v4 as rtdl_v4
from rtdsl.reference import Segment, lsi_cpu


def _bounds(segment: Segment) -> tuple[float, float, float, float]:
    return (
        min(segment.x0, segment.x1),
        min(segment.y0, segment.y1),
        max(segment.x0, segment.x1),
        max(segment.y0, segment.y1),
    )


def main() -> int:
    left = (
        Segment(100, 0.0, 0.0, 4.0, 4.0),
        Segment(101, 0.0, 3.0, 4.0, 3.0),
        Segment(102, 0.0, 5.0, 4.0, 5.0),
    )
    right = (
        Segment(200, 0.0, 4.0, 4.0, 0.0),
        Segment(201, 2.0, 0.0, 2.0, 4.0),
        Segment(202, 5.0, 5.0, 6.0, 6.0),
    )

    broadphase = aabb_intersection_pair_rows_2d(
        tuple(_bounds(segment) for segment in right),
        tuple(_bounds(segment) for segment in left),
        indexed_ids=tuple(segment.id for segment in right),
        query_ids=tuple(segment.id for segment in left),
        backend="cpu",
    )
    exact_hits = lsi_cpu(left, right)
    exact_pairs = tuple(
        sorted((int(row["left_id"]), int(row["right_id"])) for row in exact_hits)
    )
    plan = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")

    payload = {
        "status": "ok",
        "concept": "spatial join starts with broadphase candidate rows, then refines them with line-segment intersection",
        "broadphase_candidate_pairs": broadphase["candidate_id_rows"],
        "exact_intersection_pairs": exact_pairs,
        "candidate_count": broadphase["valid_count"],
        "exact_hit_count": len(exact_pairs),
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
