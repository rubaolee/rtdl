from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import rtdsl as rt

from run_exact_range_intersects_count_gate import load_geometry_mbr_columns


SCHEMA = "rtdl.paper_reproduction.librts.goal5507_rtdl_range_intersects_probe.v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_probe(*, geometry: Path, query: Path, count_only: bool = False) -> dict[str, object]:
    geometry_columns = load_geometry_mbr_columns(geometry)
    query_columns = load_geometry_mbr_columns(query)
    prepare_start = time.perf_counter()
    prepared = rt.prepare_aabb_index_2d_columns(geometry_columns, backend="optix")
    prepare_sec = time.perf_counter() - prepare_start
    try:
        query_start = time.perf_counter()
        result = prepared.count(box_queries=query_columns, operation="range_intersects")
        query_wall_sec = time.perf_counter() - query_start
        if count_only:
            rows = ()
            row_wall_sec = None
        else:
            row_start = time.perf_counter()
            rows = prepared.intersection_rows(
                query_columns,
                tuple(range(len(query_columns))),
                row_capacity=max(1, len(geometry_columns) * len(query_columns)),
            )
            row_wall_sec = time.perf_counter() - row_start
    finally:
        prepared.close()
    unique_rows = sorted(set(rows))
    return {
        "schema": SCHEMA,
        "status": "rtdl_probe_completed",
        "input_identity": {
            "geometry_path": str(geometry),
            "query_path": str(query),
            "geometry_sha256": _sha256(geometry),
            "query_sha256": _sha256(query),
            "same_input_files": True,
        },
        "rtdl": {
            "public_api": "Aabb2DColumns + prepare_aabb_index_2d_columns + prepared.count",
            "operation": "range_intersects",
            "backend": result["backend"],
            "result_count": int(result["counts"]["range_intersects"]),
            "prepare_sec": prepare_sec,
            "query_wall_sec": query_wall_sec,
            "primitive_query_sec": result["run_phases"]["query_aabb_index_2d_sec"],
            "rt_core_accelerated": bool(result["rt_core_accelerated"]),
            "native_engine_customization": bool(result["native_engine_customization"]),
            "intersection_rows_count": len(rows),
            "intersection_unique_rows_count": len(unique_rows),
            "intersection_duplicate_row_count": len(rows) - len(unique_rows),
            "intersection_rows": [list(row) for row in unique_rows],
            "intersection_rows_sec": row_wall_sec,
            "count_only": count_only,
        },
        "claim_boundary": {
            "generic_native_patch_probe_only": True,
            "full_input_adjudication": False,
            "author_specific_rtdl_core_behavior_authorized": False,
            "performance_ratio_authorized": False,
            "paper_reproduction_claimed": False,
            "embree_in_scope": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--query", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--count-only", action="store_true")
    args = parser.parse_args()
    payload = run_probe(
        geometry=args.geometry.resolve(),
        query=args.query.resolve(),
        count_only=args.count_only,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
