from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

import numpy as np
import rtdsl as rt

from run_exact_point_contains_count_gate import load_geometry_mbr_columns


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-npz", type=Path, required=True)
    parser.add_argument("--cache-json", type=Path, required=True)
    parser.add_argument("--query", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cache_metadata = json.loads(args.cache_json.read_text(encoding="utf-8"))
    with np.load(args.cache_npz, allow_pickle=False) as arrays:
        indexed = rt.Aabb2DColumns(
            ids=arrays["ids"],
            min_x=arrays["min_x"],
            min_y=arrays["min_y"],
            max_x=arrays["max_x"],
            max_y=arrays["max_y"],
        )
    queries = load_geometry_mbr_columns(args.query)
    prepare_start = time.perf_counter()
    prepared = rt.prepare_aabb_index_2d_columns(indexed, backend="optix")
    prepare_sec = time.perf_counter() - prepare_start
    try:
        query_start = time.perf_counter()
        result = prepared.count(box_queries=queries, operation="range_contains")
        query_sec = time.perf_counter() - query_start
    finally:
        prepared.close()

    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5519_cached_range_contains_probe.v1",
        "input_identity": {
            "geometry_sha256": cache_metadata["source_sha256"],
            "query_sha256": _sha256(args.query),
            "cache_row_count_matches": len(indexed) == int(cache_metadata["row_count"]),
            "app_owned_cache_contract": cache_metadata["schema"],
        },
        "indexed_count": len(indexed),
        "query_count": len(queries),
        "result_count": int(result["counts"]["range_contains"]),
        "optix_library": os.environ.get("RTDL_OPTIX_LIB", ""),
        "optix_library_sha256": _sha256(Path(os.environ["RTDL_OPTIX_LIB"])),
        "prepare_sec": prepare_sec,
        "query_sec": query_sec,
        "claim_boundary": {
            "diagnostic_only": True,
            "app_specific_core_behavior_authorized": False,
            "performance_ratio_authorized": False,
            "embree_in_scope": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
