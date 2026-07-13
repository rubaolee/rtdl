from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from run_exact_point_contains_count_gate import load_geometry_mbr_columns


SCHEMA = "rtdl.paper_reproduction.librts.goal5519_range_contains_semantic_audit.v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _box_values(columns: object, dtype: np.dtype) -> np.ndarray:
    return np.column_stack(
        (
            np.asarray(columns.min_x, dtype=dtype),
            np.asarray(columns.min_y, dtype=dtype),
            np.asarray(columns.max_x, dtype=dtype),
            np.asarray(columns.max_y, dtype=dtype),
        )
    )


def _strict_valid(values: np.ndarray) -> np.ndarray:
    return (values[:, 0] < values[:, 2]) & (values[:, 1] < values[:, 3])


def _containment_counts(indexed: np.ndarray, queries: np.ndarray) -> np.ndarray:
    counts = np.zeros(indexed.shape[0], dtype=np.uint64)
    for start in range(0, indexed.shape[0], 256):
        boxes = indexed[start : start + 256]
        hits = (
            (boxes[:, None, 0] <= queries[None, :, 0])
            & (boxes[:, None, 1] <= queries[None, :, 1])
            & (boxes[:, None, 2] >= queries[None, :, 2])
            & (boxes[:, None, 3] >= queries[None, :, 3])
        )
        counts[start : start + boxes.shape[0]] = hits.sum(axis=1, dtype=np.uint64)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-npz", type=Path, required=True)
    parser.add_argument("--cache-json", type=Path, required=True)
    parser.add_argument("--query", type=Path, required=True)
    parser.add_argument("--expected-geometry-sha256", required=True)
    parser.add_argument("--expected-query-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cache_metadata = json.loads(args.cache_json.read_text(encoding="utf-8"))
    if cache_metadata.get("source_sha256") != args.expected_geometry_sha256:
        raise ValueError("cached geometry SHA-256 does not match the exact archive input")
    query_sha256 = _sha256(args.query)
    if query_sha256 != args.expected_query_sha256:
        raise ValueError("query SHA-256 does not match the exact archive input")

    with np.load(args.cache_npz, allow_pickle=False) as arrays:
        indexed64 = np.column_stack(
            (
                np.asarray(arrays["min_x"], dtype=np.float64),
                np.asarray(arrays["min_y"], dtype=np.float64),
                np.asarray(arrays["max_x"], dtype=np.float64),
                np.asarray(arrays["max_y"], dtype=np.float64),
            )
        )
    if indexed64.shape[0] != int(cache_metadata["row_count"]):
        raise ValueError("cached row count does not match metadata")

    query_columns = load_geometry_mbr_columns(args.query)
    queries64 = _box_values(query_columns, np.float64)
    indexed32 = indexed64.astype(np.float32)
    queries32 = queries64.astype(np.float32)

    valid64 = _strict_valid(indexed64)
    valid32 = _strict_valid(indexed32)
    query_valid64 = _strict_valid(queries64)
    query_valid32 = _strict_valid(queries32)
    collapsed_indices = np.flatnonzero(valid64 & ~valid32)
    originally_degenerate_indices = np.flatnonzero(~valid64)
    invalid32_indices = np.flatnonzero(~valid32)

    invalid32_counts = _containment_counts(indexed32[invalid32_indices], queries32)
    collapsed_counts32 = _containment_counts(indexed32[collapsed_indices], queries32)
    collapsed_counts64 = _containment_counts(indexed64[collapsed_indices], queries64)

    nonzero_positions = np.flatnonzero(invalid32_counts)
    nonzero_rows = [
        {
            "indexed_row": int(invalid32_indices[position]),
            "float32_box": [float(value) for value in indexed32[invalid32_indices[position]]],
            "float64_box": [float(value) for value in indexed64[invalid32_indices[position]]],
            "float32_containment_count": int(invalid32_counts[position]),
        }
        for position in nonzero_positions[:1000]
    ]

    result = {
        "schema": SCHEMA,
        "status": "range_contains_numeric_validity_contribution_audited",
        "input_identity": {
            "geometry_sha256": cache_metadata["source_sha256"],
            "query_sha256": query_sha256,
            "same_exact_archive_inputs_as_goal5519": True,
        },
        "row_counts": {
            "indexed": int(indexed64.shape[0]),
            "queries": int(queries64.shape[0]),
        },
        "indexed_validity": {
            "float64_strictly_invalid_count": int((~valid64).sum()),
            "float32_strictly_invalid_count": int((~valid32).sum()),
            "float64_valid_but_float32_collapsed_count": int(collapsed_indices.size),
            "originally_degenerate_count": int(originally_degenerate_indices.size),
            "float32_invalid_containment_contribution": int(invalid32_counts.sum()),
            "float32_collapsed_containment_contribution": int(collapsed_counts32.sum()),
            "float64_collapsed_containment_contribution": int(collapsed_counts64.sum()),
            "float32_invalid_rows_with_nonzero_contribution": int(nonzero_positions.size),
            "nonzero_contribution_rows": nonzero_rows,
        },
        "query_validity": {
            "float64_strictly_invalid_count": int((~query_valid64).sum()),
            "float32_strictly_invalid_count": int((~query_valid32).sum()),
            "float64_valid_but_float32_collapsed_count": int((query_valid64 & ~query_valid32).sum()),
        },
        "diagnostic_hypotheses": {
            "goal5519_author_minus_rtdl": 79,
            "strict_indexed_validity_filter_explains_delta": int(invalid32_counts.sum()) == 79,
            "float32_collapse_only_explains_delta": int(collapsed_counts32.sum()) == 79,
        },
        "claim_boundary": {
            "diagnostic_only": True,
            "core_behavior_changed": False,
            "author_semantics_proven": False,
            "paper_reproduction_claimed": False,
            "performance_ratio_authorized": False,
            "embree_in_scope": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
