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


def hidden_row_count(prepared, query_segments) -> int:
    old = os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE")
    os.environ["RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"] = "planar_map_lsi"
    try:
        rows = prepared.run_raw(query_segments)
        try:
            return int(rows.row_count)
        finally:
            rows.close()
    finally:
        if old is None:
            os.environ.pop("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE", None)
        else:
            os.environ["RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"] = old


def first_mismatch_chunk(lsi, row_prepared, query_segments, chunk_size: int):
    for start in range(0, len(query_segments), chunk_size):
        end = min(len(query_segments), start + chunk_size)
        chunk = query_segments[start:end]
        count = int(lsi.count(chunk))
        rows = hidden_row_count(row_prepared, chunk)
        if count != rows:
            return {
                "start": start,
                "end": end,
                "count": count,
                "rows": rows,
                "delta": count - rows,
            }
    return None


def refine_range(lsi, row_prepared, query_segments, start: int, end: int):
    current = {
        "start": start,
        "end": end,
        "count": int(lsi.count(query_segments[start:end])),
        "rows": hidden_row_count(row_prepared, query_segments[start:end]),
    }
    steps = [dict(current)]
    while current["end"] - current["start"] > 1:
        mid = (current["start"] + current["end"]) // 2
        left = {
            "start": current["start"],
            "end": mid,
            "count": int(lsi.count(query_segments[current["start"]:mid])),
            "rows": hidden_row_count(row_prepared, query_segments[current["start"]:mid]),
        }
        right = {
            "start": mid,
            "end": current["end"],
            "count": int(lsi.count(query_segments[mid:current["end"]])),
            "rows": hidden_row_count(row_prepared, query_segments[mid:current["end"]]),
        }
        left["delta"] = left["count"] - left["rows"]
        right["delta"] = right["count"] - right["rows"]
        steps.append({"left": left, "right": right})
        if left["delta"] != 0:
            current = left
        elif right["delta"] != 0:
            current = right
        else:
            # The mismatch is non-additive over this split. Keep the current
            # interval as the smallest contiguous proof found by bisection.
            break
    current["delta"] = current["count"] - current["rows"]
    return current, steps


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--chunk-size", type=int, default=10000)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    t0 = time.perf_counter()
    base = load_cdb(args.base)
    query = load_cdb(args.query)
    base_segments = chains_to_planar_map_segments(base)
    query_segments = chains_to_planar_map_segments(query)
    t1 = time.perf_counter()

    with prepare_planar_map_lsi_2d_optix(base_segments) as lsi, prepare_segment_pair_intersection_optix(
        base_segments
    ) as rows_prepared:
        full_count = int(lsi.count(query_segments))
        full_rows = hidden_row_count(rows_prepared, query_segments)
        t2 = time.perf_counter()
        chunk = first_mismatch_chunk(lsi, rows_prepared, query_segments, args.chunk_size)
        t3 = time.perf_counter()
        refined = None
        refine_steps = []
        if chunk is not None:
            refined, refine_steps = refine_range(
                lsi,
                rows_prepared,
                query_segments,
                int(chunk["start"]),
                int(chunk["end"]),
            )
        t4 = time.perf_counter()

    witness_segments = []
    if refined is not None:
        for idx in range(refined["start"], refined["end"]):
            seg = query_segments[idx]
            witness_segments.append({"query_index": idx, **seg})

    summary = {
        "schema": "rtdl.goal4859.chunk_mismatch_locator.v1",
        "base": str(Path(args.base)),
        "query": str(Path(args.query)),
        "base_segments": len(base_segments),
        "query_segments": len(query_segments),
        "full_count": full_count,
        "full_hidden_rows": full_rows,
        "full_delta": full_count - full_rows,
        "chunk_size": args.chunk_size,
        "first_mismatch_chunk": chunk,
        "refined_mismatch": refined,
        "witness_query_segments": witness_segments[:20],
        "refine_steps": refine_steps[:40],
        "timings_seconds": {
            "load_and_segment": t1 - t0,
            "full_count_and_rows": t2 - t1,
            "chunk_scan": t3 - t2,
            "refine": t4 - t3,
            "total": t4 - t0,
        },
    }
    Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
