from __future__ import annotations

import json
import os
from pathlib import Path

from rtdsl.optix_runtime import prepare_planar_map_lsi_2d_optix
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix


def seg(seg_id: int, x0: float, y0: float, x1: float, y1: float) -> dict[str, float | int]:
    return {"id": seg_id, "x0": x0, "y0": y0, "x1": x1, "y1": y1}


CASES = [
    {
        "name": "proper_crossing",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 0.5, -1.0, 0.5, 1.0)],
    },
    {
        "name": "shared_left_endpoint",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 0.0, 0.0, 0.0, 1.0)],
    },
    {
        "name": "shared_right_endpoint",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 1.0, 0.0, 1.0, 1.0)],
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
    {
        "name": "near_endpoint_inside",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 0.999999999, -1.0, 0.999999999, 1.0)],
    },
    {
        "name": "query_hits_base_start_from_below",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 0.0, -1.0, 0.0, 1.0)],
    },
    {
        "name": "query_hits_base_end_from_below",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [seg(1, 1.0, -1.0, 1.0, 1.0)],
    },
    {
        "name": "two_base_one_query_endpoint_choice",
        "base": [
            seg(1, 0.0, 0.0, 1.0, 0.0),
            seg(2, 1.0, 0.0, 2.0, 1.0),
        ],
        "query": [seg(1, 1.0, -1.0, 1.0, 1.0)],
    },
    {
        "name": "two_query_one_base_endpoint_choice",
        "base": [seg(1, 0.0, 0.0, 1.0, 0.0)],
        "query": [
            seg(1, 1.0, -1.0, 1.0, 1.0),
            seg(2, 1.0, 0.0, 2.0, 1.0),
        ],
    },
]


def public_lsi_count(base, query) -> tuple[int, dict]:
    with prepare_planar_map_lsi_2d_optix(base) as prepared:
        meta = prepared.count_with_metadata(query)
    return int(meta["count"]), meta


def row_count(base, query, *, predicate: str | None) -> tuple[int, list[dict]]:
    old = os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE")
    if predicate is None:
        os.environ.pop("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE", None)
    else:
        os.environ["RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"] = predicate
    try:
        with prepare_segment_pair_intersection_optix(base) as prepared:
            rows = prepared.run_raw(query)
            try:
                row_dicts = rows.to_dict_rows()
                return int(rows.row_count), row_dicts
            finally:
                rows.close()
    finally:
        if old is None:
            os.environ.pop("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE", None)
        else:
            os.environ["RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"] = old


def main() -> int:
    out_rows = []
    for case in CASES:
        lsi, meta = public_lsi_count(case["base"], case["query"])
        raw_count, raw_rows = row_count(case["base"], case["query"], predicate=None)
        hidden_count, hidden_rows = row_count(case["base"], case["query"], predicate="planar_map_lsi")
        out_rows.append(
            {
                "name": case["name"],
                "public_lsi_count": lsi,
                "raw_row_count": raw_count,
                "hidden_predicate_row_count": hidden_count,
                "raw_rows": raw_rows,
                "hidden_predicate_rows": hidden_rows,
                "count_rows_match": lsi == hidden_count,
                "native_count_mode": meta.get("raw_segment_pair_result", {}).get("native_symbol"),
            }
        )
    summary = {
        "schema": "rtdl.goal4859.synthetic_count_vs_row_contract_probe.v1",
        "rows": out_rows,
        "mismatch_count": sum(1 for row in out_rows if not row["count_rows_match"]),
        "claim_boundary": "small synthetic contract probe only",
    }
    output = Path("/workspace/goal4859_synthetic_count_vs_row_contract_probe_summary.json")
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
