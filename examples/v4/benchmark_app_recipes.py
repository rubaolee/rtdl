from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rt


def _plan(kind: str, *, partner: str, **kwargs: object) -> dict[str, object]:
    plan = rt.plan_operator_request_v4(kind, partner=partner, **kwargs)
    return {
        "request": kind,
        "partner": partner,
        "status": plan.status,
        "surface": plan.api_surface,
        "tier": plan.tier,
    }


def benchmark_app_recipes() -> list[dict[str, object]]:
    return [
        {
            "app": "RTDBSCAN",
            "idea": "fixed-radius neighbor evidence plus component-union continuation",
            "operators": [
                _plan("fixed_radius", partner="torch"),
                _plan("component_union", partner="numba"),
            ],
        },
        {
            "app": "RTNN",
            "idea": "nearest-witness relation plus ranked summary when that route is available",
            "operators": [
                _plan("point_group_nearest", partner="torch"),
                _plan("ranked_summary", partner="rtdl_native"),
            ],
        },
        {
            "app": "Triangle counting",
            "idea": "ray/triangle hit relation plus grouped primitive reduction",
            "operators": [
                _plan("any_hit", partner="torch"),
                _plan("grouped_i64", partner="torch"),
            ],
        },
        {
            "app": "Robot collision",
            "idea": "ray/triangle or segment/primitives any-hit flags for collision decisions",
            "operators": [_plan("any_hit", partner="torch")],
        },
        {
            "app": "RayDB-style",
            "idea": "hit rows as a relation, then weighted or grouped summaries",
            "operators": [
                _plan("any_hit", partner="torch"),
                _plan("weighted_sum", partner="torch"),
                _plan("grouped_sum", partner="cupy"),
            ],
        },
        {
            "app": "LibRTS spatial index",
            "idea": "AABB-style indexed predicates for point, box, and overlap queries",
            "operators": [_plan("aabb_index_query", partner="rtdl_native")],
        },
        {
            "app": "Contact manifold",
            "idea": "broadphase AABB candidates plus closest-hit refinement",
            "operators": [
                _plan("aabb_index_query", partner="rtdl_native"),
                _plan("closest_hit_argmin", partner="torch"),
            ],
        },
        {
            "app": "Spatial RayJoin",
            "idea": "shape-pair candidate discovery plus join/refinement relation",
            "operators": [
                _plan("aabb_index_query", partner="rtdl_native"),
                _plan("any_hit", partner="torch"),
            ],
        },
        {
            "app": "Barnes-Hut",
            "idea": "aggregate frontier followed by weighted vector continuation",
            "operators": [
                _plan("aggregate_frontier", partner="rtdl_native"),
                _plan("grouped_sum", partner="cupy"),
            ],
        },
        {
            "app": "Hausdorff XHD",
            "idea": "threshold decision route or exact nearest-witness route",
            "operators": [
                _plan("fixed_radius", partner="torch"),
                _plan("point_group_nearest", partner="torch"),
            ],
        },
    ]


def main() -> int:
    payload = {
        "status": "ok",
        "app_count": 10,
        "recipes": benchmark_app_recipes(),
        "release_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
