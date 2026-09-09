#!/usr/bin/env python3
"""Generate one distinct LibRTS long-query grid and exact oracle manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from experiments.v4_librts_long_workload.query_grid import (
    generate_query_grid,
    sha256_file,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--indexed-npz", type=Path, required=True)
    parser.add_argument("--source-query", type=Path, required=True)
    parser.add_argument(
        "--operation", choices=("point_contains", "range_contains"), required=True
    )
    parser.add_argument("--x-count", type=int, required=True)
    parser.add_argument("--y-count", type=int, required=True)
    parser.add_argument("--stream-chunk-rows", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with np.load(args.indexed_npz.resolve(strict=True), allow_pickle=False) as arrays:
        indexed = {
            name: np.ascontiguousarray(arrays[name], dtype=np.float32)
            for name in ("min_x", "min_y", "max_x", "max_y")
        }
    result = generate_query_grid(
        indexed=indexed,
        source_query_path=args.source_query,
        operation=args.operation,
        x_count=args.x_count,
        y_count=args.y_count,
        output=args.output,
        indexed_identity={
            "indexed_npz": str(args.indexed_npz.resolve(strict=True)),
            "indexed_npz_sha256": sha256_file(args.indexed_npz),
        },
        stream_chunk_rows=args.stream_chunk_rows,
    )
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
