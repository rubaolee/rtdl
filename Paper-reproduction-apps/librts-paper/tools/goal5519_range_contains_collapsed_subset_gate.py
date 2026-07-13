from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import rtdsl as rt

from run_exact_point_contains_count_gate import load_geometry_mbr_columns
from run_exact_range_contains_count_gate import run_author_range_contains


SCHEMA = "rtdl.paper_reproduction.librts.goal5519_collapsed_subset_gate.v1"


def _write_box_wkt(path: Path, boxes: np.ndarray) -> None:
    with path.open("w", encoding="utf-8") as output:
        for min_x, min_y, max_x, max_y in boxes:
            output.write(
                "POLYGON (("
                f"{min_x:.17g} {min_y:.17g}, "
                f"{max_x:.17g} {min_y:.17g}, "
                f"{max_x:.17g} {max_y:.17g}, "
                f"{min_x:.17g} {max_y:.17g}, "
                f"{min_x:.17g} {min_y:.17g}))\n"
            )


def _oracle_count(indexed: np.ndarray, queries: np.ndarray) -> int:
    return int(
        sum(
            np.count_nonzero(
                (box[0] <= queries[:, 0])
                & (box[1] <= queries[:, 1])
                & (box[2] >= queries[:, 2])
                & (box[3] >= queries[:, 3])
            )
            for box in indexed
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-npz", type=Path, required=True)
    parser.add_argument("--query", type=Path, required=True)
    parser.add_argument("--subset-wkt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--serialize-dir", type=Path, required=True)
    parser.add_argument("--rows", type=int, nargs="+", required=True)
    parser.add_argument(
        "--author-binary",
        type=Path,
        default=Path("/workspace/librts-ae/SpatialQueryBenchmark/build/query"),
    )
    parser.add_argument("--ae-root", type=Path, default=Path("/workspace/librts-ae"))
    args = parser.parse_args()

    with np.load(args.cache_npz, allow_pickle=False) as arrays:
        all_boxes = np.column_stack(
            (
                np.asarray(arrays["min_x"], dtype=np.float64),
                np.asarray(arrays["min_y"], dtype=np.float64),
                np.asarray(arrays["max_x"], dtype=np.float64),
                np.asarray(arrays["max_y"], dtype=np.float64),
            )
        )
    row_indices = np.asarray(args.rows, dtype=np.int64)
    boxes64 = all_boxes[row_indices]
    boxes32 = boxes64.astype(np.float32)
    if np.any((boxes64[:, 0] >= boxes64[:, 2]) | (boxes64[:, 1] >= boxes64[:, 3])):
        raise ValueError("diagnostic rows must be strictly valid before float32 packing")
    if not np.all((boxes32[:, 0] >= boxes32[:, 2]) | (boxes32[:, 1] >= boxes32[:, 3])):
        raise ValueError("diagnostic rows must collapse after float32 packing")

    args.subset_wkt.parent.mkdir(parents=True, exist_ok=True)
    _write_box_wkt(args.subset_wkt, boxes64)
    queries = load_geometry_mbr_columns(args.query)
    query_values32 = np.column_stack(
        (queries.min_x, queries.min_y, queries.max_x, queries.max_y)
    ).astype(np.float32)
    oracle_count = _oracle_count(boxes32, query_values32)

    args.serialize_dir.mkdir(parents=True, exist_ok=True)
    author, author_stdout, author_command = run_author_range_contains(
        author_binary=args.author_binary,
        ae_root=args.ae_root,
        geometry_path=args.subset_wkt,
        query_path=args.query,
        serialize_dir=args.serialize_dir,
    )

    columns = rt.Aabb2DColumns(
        ids=np.arange(boxes64.shape[0], dtype=np.uint32),
        min_x=boxes64[:, 0],
        min_y=boxes64[:, 1],
        max_x=boxes64[:, 2],
        max_y=boxes64[:, 3],
    )
    prepared = rt.prepare_aabb_index_2d_columns(columns, backend="optix")
    try:
        rtdl = prepared.count(box_queries=queries, operation="range_contains")
    finally:
        prepared.close()
    rtdl_count = int(rtdl["counts"]["range_contains"])
    author_count = int(author["result_count"])

    result = {
        "schema": SCHEMA,
        "status": "collapsed_indexed_box_operation_semantics_discriminated",
        "rows": [int(value) for value in row_indices],
        "float64_boxes": boxes64.tolist(),
        "float32_boxes": boxes32.tolist(),
        "query_count": len(queries),
        "float32_inclusive_containment_oracle_count": oracle_count,
        "author": {
            **author,
            "command": author_command,
            "stdout": author_stdout,
        },
        "rtdl": {
            "result_count": rtdl_count,
            "operation": "range_contains",
            "backend": rtdl["backend"],
            "optix_library": os.environ.get("RTDL_OPTIX_LIB", ""),
        },
        "diagnosis": {
            "author_matches_float32_inclusive_oracle": author_count == oracle_count,
            "rtdl_strict_validity_filter_drops_all_subset_hits": rtdl_count == 0,
            "subset_explains_full_goal5519_delta": author_count - rtdl_count == 79,
        },
        "claim_boundary": {
            "generic_operation_semantics_diagnostic": True,
            "core_behavior_changed": False,
            "full_input_result_repaired": False,
            "paper_reproduction_claimed": False,
            "performance_ratio_authorized": False,
            "embree_in_scope": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if all(result["diagnosis"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
