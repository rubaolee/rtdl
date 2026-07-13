#!/usr/bin/env python3
"""RTDL raw-row diagnostic for RayJoin Section 5.3 PIP.

This script compares against the AuthorPatch PIP diagnostic metric:
`closest_eids != DONTKNOW`.  It intentionally does not use face-positive counts
as the author-side PIP benchmark reports closest edge ids, not polygon face
classification output.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from goal4855_rayjoin_section53_pip_public_front_door import _iter_query_point_chunks
from goal4855_rayjoin_section53_pip_public_front_door import _pack_base_segments_stream
from goal4855_rayjoin_section53_pip_public_front_door import _scan_cdb
from goal4855_rayjoin_section53_pip_public_front_door import _shared_bounds
from rtdsl import prepare_planar_map_point_location_2d_optix


FNV_OFFSET = 1469598103934665603
FNV_PRIME = 1099511628211
DONTKNOW_U32 = 0xFFFFFFFF


def _hash_step(hash_value: int, value: int, index: int) -> int:
    hash_value ^= (
        int(value)
        + 0x9E3779B97F4A7C15
        + (int(index) << 6)
        + (int(index) >> 2)
    ) & 0xFFFFFFFFFFFFFFFF
    return (hash_value * FNV_PRIME) & 0xFFFFFFFFFFFFFFFF


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--poly1", required=True)
    parser.add_argument("--poly2", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--chunk-size", type=int, default=500_000)
    args = parser.parse_args()

    poly1 = Path(args.poly1)
    poly2 = Path(args.poly2)
    t0 = time.perf_counter()
    poly1_stats = _scan_cdb(poly1)
    poly2_stats = _scan_cdb(poly2)
    scan_sec = time.perf_counter() - t0
    bounds = _shared_bounds(poly1_stats, poly2_stats)

    t_pack = time.perf_counter()
    base = _pack_base_segments_stream(poly1, poly1_stats.segment_count)
    pack_sec = time.perf_counter() - t_pack

    total = 0
    segment_found = 0
    face_positive = 0
    segment_hash_raw = FNV_OFFSET
    segment_hash_minus1 = FNV_OFFSET
    face_hash = FNV_OFFSET
    chunk_rows = []

    t_query = time.perf_counter()
    with prepare_planar_map_point_location_2d_optix(
        base,
        query_map_id=1,
        scale_bounds=bounds,
    ) as locator:
        for chunk_index, (first_point_id, points, pack_points_sec) in enumerate(
            _iter_query_point_chunks(poly2, chunk_size=args.chunk_size),
            start=1,
        ):
            chunk_segment_found = 0
            chunk_face_positive = 0
            chunk_start = time.perf_counter()
            rows = locator.run_raw(points)
            try:
                for row_index in range(rows.row_count):
                    row = rows.rows_ptr[row_index]
                    global_index = total
                    segment_id = int(row.segment_id)
                    face_id = int(row.face_id)
                    if segment_id != DONTKNOW_U32:
                        segment_found += 1
                        chunk_segment_found += 1
                    if face_id not in (DONTKNOW_U32, 0):
                        face_positive += 1
                        chunk_face_positive += 1
                    segment_hash_raw = _hash_step(segment_hash_raw, segment_id, global_index)
                    normalized_segment_id = (
                        DONTKNOW_U32
                        if segment_id == DONTKNOW_U32
                        else (segment_id - 1) & 0xFFFFFFFFFFFFFFFF
                    )
                    segment_hash_minus1 = _hash_step(
                        segment_hash_minus1,
                        normalized_segment_id,
                        global_index,
                    )
                    face_hash = _hash_step(face_hash, face_id, global_index)
                    total += 1
            finally:
                rows.close()
            chunk_rows.append(
                {
                    "chunk_index": chunk_index,
                    "first_point_id": int(first_point_id),
                    "point_count": int(points.count),
                    "segment_found": int(chunk_segment_found),
                    "face_positive": int(chunk_face_positive),
                    "pack_points_sec": float(pack_points_sec),
                    "run_raw_wall_sec": float(time.perf_counter() - chunk_start),
                }
            )
            print(
                f"[goal4856-raw] {args.label} chunk={chunk_index} "
                f"points={points.count} segment_found={chunk_segment_found} "
                f"face_positive={chunk_face_positive}",
                flush=True,
            )
    query_sec = time.perf_counter() - t_query

    summary = {
        "schema": "rtdl.goal4856.section53_pip_raw_diagnostic.v1",
        "label": args.label,
        "poly1": str(poly1),
        "poly2": str(poly2),
        "metric_contract": "closest edge found: segment_id != DONTKNOW",
        "total_points": int(total),
        "segment_found_count": int(segment_found),
        "face_positive_count": int(face_positive),
        "segment_hash_raw_fnv64": int(segment_hash_raw),
        "segment_hash_minus1_fnv64": int(segment_hash_minus1),
        "face_hash_fnv64": int(face_hash),
        "dontknow_u32": int(DONTKNOW_U32),
        "input_stats": {
            "poly1": poly1_stats.__dict__,
            "poly2": poly2_stats.__dict__,
        },
        "timings_sec": {
            "scan": float(scan_sec),
            "pack_base": float(pack_sec),
            "raw_query_and_download": float(query_sec),
        },
        "chunks": chunk_rows,
    }
    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
