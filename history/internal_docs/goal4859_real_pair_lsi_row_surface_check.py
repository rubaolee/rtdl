from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from rtdsl.datasets import chains_to_planar_map_segments
from rtdsl.datasets import load_cdb
from rtdsl.optix_runtime import prepare_planar_map_lsi_2d_optix
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--expected", type=int)
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
        lsi_meta = lsi.count_with_metadata(query_segments)
    t5 = time.perf_counter()

    with prepare_segment_pair_intersection_optix(base_segments) as raw_prepared:
        rows = raw_prepared.run_raw(query_segments)
        try:
            raw_row_count = int(rows.row_count)
            first_rows = rows.to_dict_rows()[:5]
        finally:
            rows.close()
    t6 = time.perf_counter()

    summary = {
        "schema": "rtdl.goal4859.real_pair_lsi_row_surface_check.v1",
        "base": str(Path(args.base)),
        "query": str(Path(args.query)),
        "expected_count": args.expected,
        "base_chains": len(base.chains),
        "query_chains": len(query.chains),
        "base_segments": len(base_segments),
        "query_segments": len(query_segments),
        "planar_map_lsi_count": int(lsi_meta["count"]),
        "raw_segment_pair_row_count": raw_row_count,
        "raw_equals_planar_map_lsi": raw_row_count == int(lsi_meta["count"]),
        "expected_equals_planar_map_lsi": None if args.expected is None else args.expected == int(lsi_meta["count"]),
        "first_raw_rows": first_rows,
        "timings_seconds": {
            "load_base": t1 - t0,
            "load_query": t2 - t1,
            "segments_base": t3 - t2,
            "segments_query": t4 - t3,
            "planar_map_lsi_count": t5 - t4,
            "raw_rows": t6 - t5,
            "total": t6 - t0,
        },
        "interpretation": {
            "generic_public_lsi_count_available": True,
            "generic_public_lsi_rows_available": raw_row_count == int(lsi_meta["count"]),
            "if_false": "Public raw segment-pair rows are not the same contract as planar-map LSI rows.",
        },
    }
    Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
