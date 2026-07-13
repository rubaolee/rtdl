from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from rtdsl.datasets import chains_to_planar_map_segments
from rtdsl.datasets import load_cdb
from rtdsl.optix_runtime import prepare_planar_map_lsi_2d_optix


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    base_segments = chains_to_planar_map_segments(load_cdb(args.base))
    query_segments = chains_to_planar_map_segments(load_cdb(args.query))
    with tempfile.NamedTemporaryFile("w+", delete=False) as dump:
        dump_path = dump.name

    old_dump = os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_DUMP_PATH")
    old_capacity = os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_DUMP_CAPACITY")
    os.environ["RTDL_OPTIX_SEGMENT_PAIR_DUMP_PATH"] = dump_path
    os.environ["RTDL_OPTIX_SEGMENT_PAIR_DUMP_CAPACITY"] = "100000000"
    try:
        with prepare_planar_map_lsi_2d_optix(base_segments) as lsi:
            count = lsi.count(query_segments)
            rows = lsi.run_raw(query_segments)
            try:
                row_pairs = {
                    (int(row["left_id"]), int(row["right_id"]))
                    for row in rows.to_dict_rows()
                }
            finally:
                rows.close()
    finally:
        if old_dump is None:
            os.environ.pop("RTDL_OPTIX_SEGMENT_PAIR_DUMP_PATH", None)
        else:
            os.environ["RTDL_OPTIX_SEGMENT_PAIR_DUMP_PATH"] = old_dump
        if old_capacity is None:
            os.environ.pop("RTDL_OPTIX_SEGMENT_PAIR_DUMP_CAPACITY", None)
        else:
            os.environ["RTDL_OPTIX_SEGMENT_PAIR_DUMP_CAPACITY"] = old_capacity

    dumped_pairs = set()
    with open(dump_path, "r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            left, right = stripped.split()
            dumped_pairs.add((int(left), int(right)))
    Path(dump_path).unlink(missing_ok=True)

    missing = sorted(dumped_pairs - row_pairs)
    extra = sorted(row_pairs - dumped_pairs)
    summary = {
        "schema": "rtdl.goal4860.planar_map_lsi_row_pair_diff_probe.v1",
        "base": args.base,
        "query": args.query,
        "count": int(count),
        "dumped_pair_count": len(dumped_pairs),
        "row_pair_count": len(row_pairs),
        "missing_from_rows_count": len(missing),
        "extra_in_rows_count": len(extra),
        "missing_from_rows_first": missing[:20],
        "extra_in_rows_first": extra[:20],
    }
    Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
