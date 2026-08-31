#!/usr/bin/env python3
"""Home-only final adapter trial for Goal5776 RayDB and RayJoin.

This is not a formal performance cohort.  It executes each remaining real-scale
front door once to prove correctness, endpoint shape and behavioral traversal
before the source is frozen for a modern-RTX transaction.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from goal5776_real_scale_formal_contract import COLD, PREPARED, V2, V4
from goal5776_real_scale_frontdoors import run_real_scale_endpoint
from goal5776_symmetric_endpoint import validate_behavioral_true_optix
from rtdsl.v4_callback_numba_codegen import (
    formal_numba_leaf_cache_lifecycle_metadata,
)


def _cache_delta(before, after) -> dict[str, int]:
    return {
        key: int(after[key]) - int(before[key])
        for key in ("hit_count", "miss_count", "disabled_count")
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--leaf-cache-root", required=True, type=Path)
    parser.add_argument("--leaf-cache-manifest", required=True, type=Path)
    parser.add_argument("--raydb-packet", required=True, type=Path)
    parser.add_argument("--rayjoin-left", required=True, type=Path)
    parser.add_argument("--rayjoin-right", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    native = args.native.resolve()
    manifest = args.leaf_cache_manifest.resolve()
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    os.environ["RTDL_V4_FORMAL_LEAF_CACHE"] = str(args.leaf_cache_root.resolve())
    os.environ["RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST"] = str(manifest)
    import hashlib
    manifest_sha = hashlib.sha256(manifest.read_bytes()).hexdigest()
    os.environ["RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256"] = manifest_sha
    runtime = {
        "source_root": str(args.source_root.resolve()),
        "native_library_path": str(native),
        "compute_capability": [6, 1],
        "optix_sdk_version": "9.0.0",
        "optix_include": str(args.optix_include.resolve()),
        "cuda_include": str(args.cuda_include.resolve()),
        "inputs": {
            "raydb__ssb_sf10_q11": {
                "packet_path": str(args.raydb_packet.resolve()),
                "partition_rows": 5_000_000,
            },
            "rayjoin__top4_six_batch": {
                "left": str(args.rayjoin_left.resolve()),
                "right": str(args.rayjoin_right.resolve()),
                "lsi_capacity": 1_000_000,
                "expected_output_sha256": (
                    "977c93718af22eb6cb887948304f2a9c56cf33aa57e05f5872bf6b2bf271ec3d"
                ),
            },
        },
    }
    trials = (
        ("raydb__ssb_sf10_q11", V2, COLD),
        ("raydb__ssb_sf10_q11", V4, COLD),
        ("rayjoin__top4_six_batch", V2, COLD),
        ("rayjoin__top4_six_batch", V4, COLD),
        ("rayjoin__top4_six_batch", V2, PREPARED),
        ("rayjoin__top4_six_batch", V4, PREPARED),
    )
    results = []
    for unit_id, method, lifecycle in trials:
        cache_before = formal_numba_leaf_cache_lifecycle_metadata()
        endpoint = run_real_scale_endpoint(
            unit_id=unit_id, method=method, lifecycle=lifecycle,
            runtime=runtime,
        )
        cache_after = formal_numba_leaf_cache_lifecycle_metadata()
        cache_delta = _cache_delta(cache_before, cache_after)
        validate_behavioral_true_optix(endpoint["traversal_receipt"])
        if method == V4 and (
            cache_delta["hit_count"] <= 0
            or cache_delta["miss_count"] != 0
            or cache_delta["disabled_count"] != 0
        ):
            raise RuntimeError(
                f"sealed V4 final trial did not use only cache hits: {cache_delta}")
        results.append({
            "unit_id": unit_id,
            "method": method,
            "lifecycle": lifecycle,
            "matched": endpoint["matched"],
            "row_count": len(endpoint["rows"]),
            "rows": endpoint["rows"],
            "loading_seconds_reported_separately": endpoint[
                "loading_seconds_reported_separately"
            ],
            "preparation_seconds_reported_separately": endpoint[
                "preparation_seconds_reported_separately"
            ],
            "prepared_session_complete_wall_seconds_reported_separately": endpoint.get(
                "prepared_session_complete_wall_seconds_reported_separately"
            ),
            "phase_accounting": endpoint["phase_accounting"],
            "traversal_receipt": endpoint["traversal_receipt"],
            "formal_leaf_cache_delta": (
                cache_delta if method == V4
                else {"mode": "not_applicable_to_v2_direct"}
            ),
        })
    payload = {
        "schema": "rtdl.goal5776.home_final_frontdoor_trial.v1",
        "scope": "Home correctness_endpoint_shape_behavioral_optix_only",
        "formal_performance_result_created": False,
        "modern_rtx_claimed": False,
        "trial_count": len(results),
        "all_matched": all(bool(row["matched"]) for row in results),
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({
        "status": "passed", "trial_count": len(results),
        "all_matched": payload["all_matched"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
