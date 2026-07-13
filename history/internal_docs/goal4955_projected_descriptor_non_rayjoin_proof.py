#!/usr/bin/env python3
"""Goal4955 non-RayJoin projected descriptor proof.

This proof does not import the RayJoin paper-reproduction app.  It demonstrates
the generic part of Goal4955: grouped descriptor-pair aggregation can operate on
projected columns without materializing point geometry payload columns.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def descriptor_pair_count_projected(carrier: dict[str, np.ndarray]) -> dict[str, object]:
    label_a = np.asarray(carrier["label_a"], dtype=np.int64)
    label_b = np.asarray(carrier["label_b"], dtype=np.int64)
    lengths = np.asarray(carrier["group_length"], dtype=np.int64)
    if label_a.size == 0:
        return {"pair_count": 0, "total_groups": 0, "total_point_rows": 0, "pairs": []}
    pairs = np.column_stack((label_a, label_b))
    unique_pairs, inverse = np.unique(pairs, axis=0, return_inverse=True)
    group_counts = np.bincount(inverse)
    point_counts = np.bincount(inverse, weights=lengths).astype(np.int64, copy=False)
    order = np.lexsort((unique_pairs[:, 1], unique_pairs[:, 0]))
    rows = [
        {
            "label_a": int(unique_pairs[index, 0]),
            "label_b": int(unique_pairs[index, 1]),
            "group_count": int(group_counts[index]),
            "point_row_count": int(point_counts[index]),
        }
        for index in order
    ]
    return {
        "pair_count": int(unique_pairs.shape[0]),
        "total_groups": int(label_a.size),
        "total_point_rows": int(lengths.sum()),
        "pairs": rows,
    }


def main() -> int:
    carrier = {
        "group_offset": np.asarray([0, 3, 5, 9, 11], dtype=np.int64),
        "group_length": np.asarray([3, 2, 4, 2, 5], dtype=np.int64),
        "label_a": np.asarray([10, 10, 20, 20, 20], dtype=np.int64),
        "label_b": np.asarray([100, 100, 200, 300, 300], dtype=np.int64),
    }
    result = descriptor_pair_count_projected(carrier)
    expected = {
        "pair_count": 3,
        "total_groups": 5,
        "total_point_rows": 16,
        "pairs": [
            {"label_a": 10, "label_b": 100, "group_count": 2, "point_row_count": 5},
            {"label_a": 20, "label_b": 200, "group_count": 1, "point_row_count": 4},
            {"label_a": 20, "label_b": 300, "group_count": 2, "point_row_count": 7},
        ],
    }
    payload = {
        "schema": "rtdl.internal.goal4955.projected_descriptor_non_rayjoin_proof.v1",
        "rayjoin_imported": False,
        "cdb_required": False,
        "authorofficial_required": False,
        "geometry_payload_materialized": False,
        "projected_out_columns": ("x", "y", "alt_label", "source_side_id", "source_element_id"),
        "carrier_columns": sorted(carrier.keys()),
        "result": result,
        "expected": expected,
        "pass": result == expected,
    }
    output = Path(__file__).with_suffix(".json")
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
