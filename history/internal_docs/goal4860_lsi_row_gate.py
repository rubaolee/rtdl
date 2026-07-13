from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from rtdsl.datasets import chains_to_planar_map_segments
from rtdsl.datasets import load_cdb
from rtdsl.optix_runtime import prepare_planar_map_lsi_2d_optix


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    t0 = time.perf_counter()
    base = load_cdb(args.base)
    t1 = time.perf_counter()
    query = load_cdb(args.query)
    t2 = time.perf_counter()
    base_segments = chains_to_planar_map_segments(base)
    t3 = time.perf_counter()
    query_segments = chains_to_planar_map_segments(query)
    t4 = time.perf_counter()

    with prepare_planar_map_lsi_2d_optix(base_segments) as lsi:
        count_meta = lsi.count_with_metadata(query_segments)
        t5 = time.perf_counter()
        rows = lsi.run_raw(query_segments)
        try:
            row_count = int(rows.row_count)
            first_rows = rows.to_dict_rows()[:5]
        finally:
            rows.close()
        t6 = time.perf_counter()

    summary = {
        "schema": "rtdl.goal4860.planar_map_lsi_row_gate.v1",
        "base": str(Path(args.base)),
        "query": str(Path(args.query)),
        "expected": int(args.expected),
        "base_chains": len(base.chains),
        "query_chains": len(query.chains),
        "base_segments": len(base_segments),
        "query_segments": len(query_segments),
        "planar_map_lsi_count": int(count_meta["count"]),
        "planar_map_lsi_row_count": row_count,
        "count_equals_expected": int(count_meta["count"]) == int(args.expected),
        "rows_equal_count": row_count == int(count_meta["count"]),
        "rows_equal_expected": row_count == int(args.expected),
        "first_rows": first_rows,
        "count_metadata": count_meta,
        "timings_seconds": {
            "load_base": t1 - t0,
            "load_query": t2 - t1,
            "segments_base": t3 - t2,
            "segments_query": t4 - t3,
            "count": t5 - t4,
            "rows": t6 - t5,
            "total": t6 - t0,
        },
        "claim_boundary": {
            "section52_lsi_row_contract_gate": True,
            "section53_pip_claim": False,
            "section57_overlay_claim": False,
            "performance_claim": False,
        },
    }
    Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
