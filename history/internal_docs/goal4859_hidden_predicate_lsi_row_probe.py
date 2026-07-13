from __future__ import annotations

import argparse
import json
import os
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
    query = load_cdb(args.query)
    base_segments = chains_to_planar_map_segments(base)
    query_segments = chains_to_planar_map_segments(query)
    t1 = time.perf_counter()

    with prepare_planar_map_lsi_2d_optix(base_segments) as lsi:
        public_count = lsi.count(query_segments)
    t2 = time.perf_counter()

    old = os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE")
    os.environ["RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"] = "planar_map_lsi"
    try:
        with prepare_segment_pair_intersection_optix(base_segments) as prepared:
            rows = prepared.run_raw(query_segments)
            try:
                row_count = int(rows.row_count)
                first_rows = rows.to_dict_rows()[:5]
            finally:
                rows.close()
    finally:
        if old is None:
            os.environ.pop("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE", None)
        else:
            os.environ["RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"] = old
    t3 = time.perf_counter()

    summary = {
        "schema": "rtdl.goal4859.hidden_predicate_lsi_row_probe.v1",
        "base": str(Path(args.base)),
        "query": str(Path(args.query)),
        "expected": args.expected,
        "public_planar_map_lsi_count": int(public_count),
        "hidden_predicate_row_count": int(row_count),
        "rows_equal_public_count": int(row_count) == int(public_count),
        "rows_equal_expected": None if args.expected is None else int(row_count) == args.expected,
        "first_rows": first_rows,
        "timings_seconds": {
            "load_and_segment": t1 - t0,
            "public_lsi_count": t2 - t1,
            "hidden_predicate_rows": t3 - t2,
            "total": t3 - t0,
        },
        "route": "public_segment_pair_run_raw_with_hidden_native_predicate_env",
        "private_bundled_helper_imported": False,
        "runtime_or_native_edits": False,
        "public_api_gap": "No formal prepare_planar_map_lsi_2d_optix.run_raw rows front door yet.",
    }
    Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
