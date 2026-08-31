#!/usr/bin/env python3
"""Freeze the 12M-point RTNN real-scale input and an independent CPU oracle.

The oracle uses SciPy cKDTree only as an over-inclusive candidate finder.  It
then re-evaluates every candidate with the paper lane's exact float32 distance
arithmetic, open boundaries, distance/id ordering, and K=4.  Neither V2, V4,
RTDL, nor an OptiX result is imported.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree


K = 4
MIN_DISTANCE = np.float32(0.0)
MAX_DISTANCE = np.float32(2.0)
QUERY_RADIUS = 2.0001  # over-inclusive; exact f32 filter below is authoritative


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _distance_f32(query: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    delta = np.asarray(query, dtype=np.float32) - np.asarray(
        candidates, dtype=np.float32
    )
    dx2 = np.float32(delta[:, 0] * delta[:, 0])
    dy2 = np.float32(delta[:, 1] * delta[:, 1])
    dz2 = np.float32(delta[:, 2] * delta[:, 2])
    distance_sq = np.float32(np.float32(dx2 + dy2) + dz2)
    return np.sqrt(distance_sq, dtype=np.float32)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search", required=True, type=Path)
    parser.add_argument("--search-sha256", required=True)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--queries-sha256", required=True)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--source-manifest-sha256", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    for path, expected in (
        (args.search, args.search_sha256),
        (args.queries, args.queries_sha256),
        (args.source_manifest, args.source_manifest_sha256),
    ):
        if _sha(path) != expected:
            raise RuntimeError(f"RTNN source SHA-256 mismatch: {path}")
    source_manifest = json.loads(args.source_manifest.read_text(encoding="utf-8"))
    if source_manifest.get("search_count") != 12_000_000:
        raise ValueError("RTNN source manifest search count changed")
    if source_manifest.get("query_count") != 4096:
        raise ValueError("RTNN source manifest query count changed")

    search = np.ascontiguousarray(
        np.loadtxt(args.search, delimiter=",", dtype=np.float32), dtype=np.float32
    )
    queries = np.ascontiguousarray(
        np.loadtxt(args.queries, delimiter=",", dtype=np.float32), dtype=np.float32
    )
    if search.shape != (12_000_000, 3) or queries.shape != (4096, 3):
        raise ValueError("RTNN XYZ matrix shape mismatch")
    if not np.all(np.isfinite(search)) or not np.all(np.isfinite(queries)):
        raise ValueError("RTNN XYZ matrix contains nonfinite coordinates")

    tree = cKDTree(search, copy_data=False, balanced_tree=True, compact_nodes=True)
    query_ids: list[int] = []
    candidate_ids: list[int] = []
    ranks: list[int] = []
    distance_squares: list[np.float32] = []
    candidate_counts = []
    # Query and consume one neighborhood at a time.  The 12M-point packet is
    # assembled from overlapping KITTI frames; materializing all 4096 radius
    # neighborhoods together can occupy the whole machine even though each
    # individual exact ranking is modest.  This bounded-memory form is
    # semantically identical and keeps the Home validation host responsive.
    for query_id in range(len(queries)):
        ids = tree.query_ball_point(
            queries[query_id], QUERY_RADIUS, workers=1, return_sorted=True
        )
        ids_array = np.asarray(ids, dtype=np.int64)
        distance = _distance_f32(queries[query_id], search[ids_array])
        eligible = (distance > MIN_DISTANCE) & (distance < MAX_DISTANCE)
        ids_array = ids_array[eligible]
        distance = distance[eligible]
        order = np.lexsort((ids_array, distance))
        ids_array = ids_array[order]
        distance = distance[order]
        candidate_counts.append(int(len(ids_array)))
        # Radius-bounded KNN returns up to K rows.  The frozen KITTI-derived
        # packet contains two legitimate short rows; inventing sentinels or
        # widening the open radius would change the paper contract.
        take_count = min(K, len(ids_array))
        for rank, (candidate_id, value) in enumerate(
            zip(ids_array[:take_count], distance[:take_count]), start=1
        ):
            query_ids.append(query_id)
            candidate_ids.append(int(candidate_id))
            ranks.append(rank)
            distance_squares.append(np.float32(np.float32(value) * np.float32(value)))
        if (query_id + 1) % 256 == 0:
            print(
                json.dumps(
                    {
                        "oracle_queries_complete": query_id + 1,
                        "maximum_candidates_so_far": max(candidate_counts),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )

    expected = {
        "expected_query_u32.npy": np.asarray(query_ids, dtype=np.uint32),
        "expected_candidate_u32.npy": np.asarray(candidate_ids, dtype=np.uint32),
        "expected_rank_u32.npy": np.asarray(ranks, dtype=np.uint32),
        "expected_distance_sq_f32.npy": np.asarray(
            distance_squares, dtype=np.float32
        ),
    }
    expected_row_count = sum(min(K, count) for count in candidate_counts)
    if any(len(value) != expected_row_count for value in expected.values()):
        raise RuntimeError("RTNN oracle row count mismatch")

    args.output_dir.mkdir(parents=True, exist_ok=False)
    arrays = {
        "search_f32.npy": search,
        "queries_f32.npy": queries,
        **expected,
    }
    members = {}
    for name, value in arrays.items():
        path = args.output_dir / name
        np.save(path, value, allow_pickle=False)
        members[name] = {
            "sha256": _sha(path),
            "size_bytes": path.stat().st_size,
            "shape": list(value.shape),
            "dtype": str(value.dtype),
        }
    manifest = {
        "schema": "rtdl.goal5776.rtnn_real_scale_input.v1",
        "source": {
            "search_sha256": args.search_sha256,
            "queries_sha256": args.queries_sha256,
            "manifest_sha256": args.source_manifest_sha256,
            "identity_level": source_manifest["identity_level"],
            "paper_workload_label": source_manifest["paper_workload_label"],
        },
        "contract": {
            "search_count": len(search),
            "query_count": len(queries),
            "k": K,
            "minimum_distance": float(MIN_DISTANCE),
            "maximum_distance": float(MAX_DISTANCE),
            "minimum_boundary": "open",
            "maximum_boundary": "open",
            "distance_arithmetic": "f32_sub_mul_add_sqrt_then_f32_square",
            "ordering": ["distance", "candidate_id"],
        },
        "oracle": {
            "candidate_finder": "scipy.spatial.cKDTree.query_ball_point",
            "candidate_finder_radius_overinclusive": QUERY_RADIUS,
            "candidate_finder_is_output_authority": False,
            "exact_f32_recheck_is_output_authority": True,
            "expected_row_count": expected_row_count,
            "short_query_ids": [
                index for index, count in enumerate(candidate_counts)
                if count < K
            ],
            "minimum_eligible_candidate_count": min(candidate_counts),
            "maximum_eligible_candidate_count": max(candidate_counts),
        },
        "members": members,
        "claim_boundary": {
            "level_b_same_source": True,
            "exact_paper_input": False,
            "formal_performance_result_created": False,
            "oracle_imports_v2_v4_rtdl_or_optix": False,
        },
    }
    manifest_path = args.output_dir / "MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "manifest_sha256": _sha(manifest_path),
        "minimum_candidates": min(candidate_counts),
        "maximum_candidates": max(candidate_counts),
        "row_count": len(query_ids),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
