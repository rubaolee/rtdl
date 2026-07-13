#!/usr/bin/env python3
"""Compare raw segment-pair count with public planar-map LSI count on tiny cases."""

from __future__ import annotations

import json
from pathlib import Path

from rtdsl.optix_runtime import (
    prepare_planar_map_lsi_2d_optix,
    prepare_segment_pair_intersection_optix,
    prepare_segment_pair_left_set_optix,
)


def seg(seg_id: int, x0: float, y0: float, x1: float, y1: float) -> dict[str, float | int]:
    return {"id": seg_id, "x0": x0, "y0": y0, "x1": x1, "y1": y1}


CASES = [
    {
        "name": "proper_crossing",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 0.5, -1.0, 0.5, 1.0)],
    },
    {
        "name": "identical_same_direction",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 0.0, 0.0, 1.0, 0.0)],
    },
    {
        "name": "identical_reverse_direction",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 1.0, 0.0, 0.0, 0.0)],
    },
    {
        "name": "shared_left_endpoint",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 0.0, 0.0, 0.0, 1.0)],
    },
    {
        "name": "shared_left_endpoint_diagonal_up",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 0.0, 0.0, 1.0, 1.0)],
    },
    {
        "name": "shared_left_endpoint_diagonal_down",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 0.0, 0.0, 1.0, -1.0)],
    },
    {
        "name": "vertical_base_shared_bottom_endpoint_right",
        "base": [seg(1, 0.0, 0.0, 0.0, 1.0)],
        "query": [seg(1, 0.0, 0.0, 1.0, 0.0)],
    },
    {
        "name": "vertical_base_shared_bottom_endpoint_left",
        "base": [seg(1, 0.0, 0.0, 0.0, 1.0)],
        "query": [seg(1, 0.0, 0.0, -1.0, 0.0)],
    },
    {
        "name": "reversed_base_shared_endpoint",
        "base": [seg(1, 1.0, 0.0, 0.0, 0.0)],
        "query": [seg(1, 0.0, 0.0, 0.0, 1.0)],
    },
    {
        "name": "shared_right_endpoint",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 1.0, 0.0, 1.0, 1.0)],
    },
    {
        "name": "shared_right_endpoint_diagonal",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 1.0, 0.0, 0.0, 1.0)],
    },
    {
        "name": "collinear_partial_overlap",
        "base": [seg(1, 0.0, 0.0, 2.0, 0.0)],
        "query": [seg(1, 1.0, 0.0, 3.0, 0.0)],
    },
    {
        "name": "collinear_touching_endpoint",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 1.0, 0.0, 2.0, 0.0)],
    },
]


def raw_count(base, query) -> int:
    with prepare_segment_pair_intersection_optix(base) as prepared:
        with prepare_segment_pair_left_set_optix(query) as left:
            result = prepared.count_prepared_left_exact_intersections(left)
    return int(result["count"] if isinstance(result, dict) else result)


def lsi_count(base, query) -> int:
    with prepare_planar_map_lsi_2d_optix(base) as prepared:
        return int(prepared.count(query))


def main() -> int:
    rows = []
    for case in CASES:
        raw = raw_count(case["base"], case["query"])
        lsi = lsi_count(case["base"], case["query"])
        rows.append(
            {
                "name": case["name"],
                "raw_segment_pair_count": raw,
                "planar_map_lsi_count": lsi,
                "differs": raw != lsi,
            }
        )
    summary = {
        "schema": "rtdl.goal4851.synthetic_planar_map_lsi_probe.v1",
        "rows": rows,
        "differing_case_count": sum(1 for row in rows if row["differs"]),
        "claim_boundary": "synthetic semantic-delta probe only; no paper performance claim",
    }
    out = Path("/workspace/goal4851_synthetic_planar_map_lsi_probe_summary.json")
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
