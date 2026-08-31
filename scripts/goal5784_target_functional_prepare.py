#!/usr/bin/env python3
"""Untimed target functional/cache preparation for four Goal5784 units."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from goal5776_real_scale_formal_worker import _validate_receipt_row_binding
from goal5784_targeted_formal_contract import UNITS, V2, V4
from goal5784_targeted_runtime_inputs import build_targeted_inputs
from goal5784_targeted_worker import run_endpoint_with_mechanism_binding
from rtdsl.v4_callback_numba_codegen import (
    formal_numba_leaf_cache_lifecycle_metadata,
    materialize_formal_numba_leaf_cache_manifest,
)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _delta(before: dict[str, object], after: dict[str, object]) -> dict[str, int]:
    return {key: int(after[key]) - int(before[key])
            for key in ("hit_count", "miss_count", "disabled_count")}


def _seal(root: Path) -> None:
    for path in sorted((root, *root.rglob("*")),
                       key=lambda item: len(item.parts), reverse=True):
        if path.is_symlink():
            raise RuntimeError(f"Goal5784 cannot seal symlink: {path}")
        path.chmod(path.stat().st_mode & ~0o222)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--compute-capability", choices=("61", "89"), required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--cache-manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--execution-source-sha256", required=True)
    args = parser.parse_args()
    source = args.source_root.resolve()
    native = args.native.resolve()
    cache = args.cache_root.resolve()
    manifest = args.cache_manifest.resolve()
    output = args.output_root.resolve()
    execution_source_sha256 = args.execution_source_sha256.lower()
    if len(execution_source_sha256) != 64 or any(
            char not in "0123456789abcdef"
            for char in execution_source_sha256):
        raise ValueError("Goal5784 invalid execution-source digest")
    for path in (cache, manifest, output):
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)
    cache.mkdir(parents=True)
    output.mkdir(parents=True)
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    os.environ["RTDL_V4_FORMAL_LEAF_CACHE"] = str(cache)
    os.environ.pop("RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST", None)
    os.environ.pop("RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256", None)
    runtime = {
        "source_root": str(source),
        "native_library_path": str(native),
        "compute_capability": [int(args.compute_capability[0]),
                               int(args.compute_capability[1])],
        "optix_sdk_version": "9.0.0",
        "optix_include": str(args.optix_include.resolve()),
        "cuda_include": str(args.cuda_include.resolve()),
        "execution_source_sha256": execution_source_sha256,
        "inputs": build_targeted_inputs(args.data_root),
    }
    records = []
    cache_total = {key: 0 for key in ("hit_count", "miss_count", "disabled_count")}
    triangle_mechanism_bound = 0
    for unit in UNITS:
        for lifecycle in unit.supported_lifecycles:
            for method in (V2, V4):
                before = formal_numba_leaf_cache_lifecycle_metadata()
                endpoint = run_endpoint_with_mechanism_binding(
                    unit_id=unit.unit_id, method=method,
                    lifecycle=lifecycle, runtime=runtime)
                after = formal_numba_leaf_cache_lifecycle_metadata()
                delta = _delta(before, after)
                if method == V4:
                    for key, value in delta.items():
                        cache_total[key] += value
                    if delta["disabled_count"] != 0:
                        raise RuntimeError("Goal5784 disabled formal leaf cache")
                receipt = dict(endpoint["traversal_receipt"])
                _validate_receipt_row_binding(receipt, endpoint["rows"])
                snapshot = dict(receipt["native_snapshot"])
                if (
                    endpoint.get("matched") is not True
                    or receipt.get("physical_executor_classification")
                        != "optix_traversal_observed"
                    or int(snapshot.get("successful_launch_count", 0)) <= 0
                    or int(snapshot.get("successful_launch_count", 0))
                        != int(snapshot.get("complete_context_launch_count", -1))
                    or any(int(snapshot.get(key, 0)) != 0 for key in (
                        "failed_launch_count", "incomplete_context_launch_count",
                        "unbound_launch_count", "pending_context_at_finish",
                        "session_error"))
                ):
                    raise RuntimeError(
                        f"Goal5784 functional failure: {unit.unit_id}/{lifecycle}/{method}")
                record = {
                    "unit_id": unit.unit_id, "app": unit.app,
                    "lifecycle": lifecycle, "method": method,
                    "matched": True, "rows": endpoint["rows"],
                    "traversal_receipt": receipt,
                    "mechanism_binding": endpoint["goal5784_mechanism_binding"],
                    "formal_leaf_cache_delta": (
                        delta if method == V4
                        else {"mode": "not_applicable_to_v2_direct"}),
                    "formal_worker": False,
                    "registered_formal_timing_created": False,
                }
                path = output / f"{len(records):03d}.json"
                path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n",
                                encoding="utf-8", newline="\n")
                records.append(record)
                if method == V4 and unit.app == "triangle_counting":
                    if endpoint["goal5784_mechanism_binding"].get(
                            "mechanism_id") \
                            != "compiler_fused_checked_u64_device_reduction":
                        raise RuntimeError("Goal5784 functional mechanism unbound")
                    triangle_mechanism_bound += 1
    if len(records) != 16 or cache_total["miss_count"] <= 0 \
            or triangle_mechanism_bound != 6:
        raise RuntimeError("Goal5784 functional/cache cardinality mismatch")
    materialize_formal_numba_leaf_cache_manifest(cache, manifest)
    _seal(cache)
    summary = {
        "schema": "rtdl.goal5784.target_functional_prepare.v1",
        "execution_unit_count": 4,
        "functional_trial_count": 16,
        "all_correct_and_behaviorally_true_optix": True,
        "leaf_cache_population": cache_total,
        "triangle_v4_mechanism_bound_trial_count": triangle_mechanism_bound,
        "triangle_v4_mechanism_binding_complete": True,
        "leaf_cache_manifest_sha256": _sha(manifest),
        "formal_worker_count": 0,
        "registered_formal_timing_count": 0,
    }
    (output / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
