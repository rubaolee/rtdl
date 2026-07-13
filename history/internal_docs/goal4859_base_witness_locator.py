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


def hidden_row_count(base_segments, query_segments) -> tuple[int, list[dict]]:
    old = os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE")
    os.environ["RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"] = "planar_map_lsi"
    try:
        with prepare_segment_pair_intersection_optix(base_segments) as prepared:
            rows = prepared.run_raw(query_segments)
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


def count_rows(base_segments, query_segments) -> tuple[int, int, list[dict]]:
    with prepare_planar_map_lsi_2d_optix(base_segments) as lsi:
        count = int(lsi.count(query_segments))
    rows, row_dicts = hidden_row_count(base_segments, query_segments)
    return count, rows, row_dicts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--query-start", type=int, required=True)
    parser.add_argument("--query-end", type=int, required=True)
    parser.add_argument("--base-chunk-size", type=int, default=200000)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    t0 = time.perf_counter()
    base = load_cdb(args.base)
    query = load_cdb(args.query)
    base_segments = chains_to_planar_map_segments(base)
    query_segments_all = chains_to_planar_map_segments(query)
    query_segments = query_segments_all[args.query_start : args.query_end]
    t1 = time.perf_counter()

    full_count, full_rows, full_row_dicts = count_rows(base_segments, query_segments)
    t2 = time.perf_counter()

    mismatch_chunks = []
    for start in range(0, len(base_segments), args.base_chunk_size):
        end = min(len(base_segments), start + args.base_chunk_size)
        chunk = base_segments[start:end]
        count, rows, row_dicts = count_rows(chunk, query_segments)
        if count != rows:
            mismatch_chunks.append(
                {
                    "start": start,
                    "end": end,
                    "count": count,
                    "rows": rows,
                    "delta": count - rows,
                    "row_sample": row_dicts[:10],
                }
            )
    t3 = time.perf_counter()

    refined = []
    for chunk in mismatch_chunks:
        start = int(chunk["start"])
        end = int(chunk["end"])
        while end - start > 1:
            mid = (start + end) // 2
            left_count, left_rows, _ = count_rows(base_segments[start:mid], query_segments)
            right_count, right_rows, _ = count_rows(base_segments[mid:end], query_segments)
            if left_count != left_rows:
                end = mid
            elif right_count != right_rows:
                start = mid
            else:
                break
        count, rows, row_dicts = count_rows(base_segments[start:end], query_segments)
        refined.append(
            {
                "start": start,
                "end": end,
                "count": count,
                "rows": rows,
                "delta": count - rows,
                "base_segments": [
                    {"base_index": idx, **base_segments[idx]}
                    for idx in range(start, end)
                ],
                "row_sample": row_dicts[:10],
            }
        )
    t4 = time.perf_counter()

    summary = {
        "schema": "rtdl.goal4859.base_witness_locator.v1",
        "base": str(Path(args.base)),
        "query": str(Path(args.query)),
        "query_range": [args.query_start, args.query_end],
        "query_segments": [
            {"query_index": idx, **query_segments_all[idx]}
            for idx in range(args.query_start, args.query_end)
        ],
        "full_count": full_count,
        "full_hidden_rows": full_rows,
        "full_delta": full_count - full_rows,
        "full_row_sample": full_row_dicts[:10],
        "base_chunk_size": args.base_chunk_size,
        "mismatch_chunks": mismatch_chunks,
        "refined_base_witnesses": refined,
        "timings_seconds": {
            "load_and_segment": t1 - t0,
            "full_count_rows": t2 - t1,
            "base_chunk_scan": t3 - t2,
            "refine": t4 - t3,
            "total": t4 - t0,
        },
    }
    Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
