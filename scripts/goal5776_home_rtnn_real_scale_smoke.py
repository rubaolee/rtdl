#!/usr/bin/env python3
"""Untimed Home correctness/behavioral gate for RTNN 12M x 4096, K=4."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import time

import numba
import numpy as np

from rtdsl.direct_optix_physical import prepare_direct_optix_bounded_selection_3d
from rtdsl.optix_runtime import _load_optix_library
from rtdsl.physical_execution_provenance import OptixTraversalAuditSession
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _load_app(source_root: Path):
    path = source_root / "Paper-reproduction-apps/rtnn-paper/v4_whole_app.py"
    spec = importlib.util.spec_from_file_location("goal5776_rtnn_v4", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load RTNN V4 front door")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _receipt_ok(receipt: dict[str, object]) -> bool:
    row = dict(receipt["native_snapshot"])
    successful = int(row["successful_launch_count"])
    return (
        receipt["physical_executor_classification"] == "optix_traversal_observed"
        and successful > 0
        and int(row["complete_context_launch_count"]) == successful
        and all(int(row[name]) == 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error"))
        and bool(row["first_traversable"]) and bool(row["last_traversable"])
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--input-root", required=True, type=Path)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    native = args.native.resolve()
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    app = _load_app(source_root)
    data = app.load_real_scale_v4_input(args.input_root)
    target = ReferenceTargetProfile(
        provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
        native_sha256=_sha(native), supports_custom_aabb=True,
        supports_builtin_triangle=True)
    runtime = {
        "target": target, "compute_capability": (6, 1),
        "optix_include": args.optix_include.resolve(),
        "cuda_include": args.cuda_include.resolve(),
        "expected_python_version": platform.python_version(),
        "expected_numba_version": numba.__version__,
        "expected_numpy_version": np.__version__,
        "native_library_path": native,
    }

    # Run V4 first so its result cannot inherit a V2-created physical owner.
    started = time.perf_counter()
    with app.prepare_v4(**runtime, prepared_input=data) as owner:
        v4_prepare = time.perf_counter() - started
        v4 = owner.execute(
            data["queries"], k=data["k"],
            minimum_distance=data["minimum_distance"],
            maximum_distance=data["maximum_distance"],
            initial_radius=data["initial_radius"],
            maximum_rounds=data["maximum_rounds"])
    v4_receipt_ok = _receipt_ok(v4["traversal_receipt"])
    if not v4["matched"] or not v4_receipt_ok:
        mismatches = [
            {"index": index, "actual": actual, "expected": expected}
            for index, (actual, expected) in enumerate(
                zip(v4["output"], data["expected"], strict=False))
            if actual != expected
        ][:3]
        raise RuntimeError("V4 RTNN real-scale gate failed: " + json.dumps({
            "matched": v4["matched"], "receipt_ok": v4_receipt_ok,
            "actual_rows": len(v4["output"]),
            "expected_rows": len(data["expected"]),
            "first_mismatches": mismatches,
            "snapshot": v4["traversal_receipt"].get("native_snapshot"),
        }, sort_keys=True))

    migration = app._load_app()
    packed_search = migration._pack_point_rows(data["search"])
    packed_queries = migration._pack_point_rows(data["queries"])
    started = time.perf_counter()
    v2_owner = prepare_direct_optix_bounded_selection_3d(
        packed_search, max_distance_bound=data["maximum_distance"])
    v2_prepare = time.perf_counter() - started
    library = _load_optix_library()
    try:
        with OptixTraversalAuditSession.open(
            library=library, library_path=native) as audit:
            started = time.perf_counter()
            physical = v2_owner.run(
                packed_queries,
                minimum_distance=data["minimum_distance"],
                maximum_distance=data["maximum_distance"], k=data["k"],
                minimum_boundary="open", maximum_boundary="open")
            v2_execute = time.perf_counter() - started
            actual = migration._canonical_rows(
                migration._relation_rows_from_rows(physical["rows"]))
            output_sha = _digest(actual)
            receipt = audit.finish(
                semantic_digest=data["input_sha256"], output_digest=output_sha,
                route_identity="goal5776:rtnn:v2_direct:true_optix:kitti12m")
    finally:
        v2_owner.close()
    if not app._paper_rows_match(actual, data["expected"]) \
            or not _receipt_ok(receipt):
        raise RuntimeError("V2 RTNN real-scale gate failed")

    result = {
        "schema": "rtdl.goal5776.rtnn_real_scale_home_smoke.v1",
        "status": "passed",
        "scope": "untimed_functional_capacity_and_behavioral_optix_only",
        "registered_performance_observation_created": False,
        "search_count": len(data["search"]),
        "query_count": len(data["queries"]),
        "output_row_count": len(data["expected"]),
        "input_manifest_sha256": data["input_sha256"],
        "native_library_sha256": _sha(native),
        "v4": {
            "matched": True,
            "prepare_seconds_observed_not_formal": v4_prepare,
            "execute_seconds_observed_not_formal": v4[
                "registered_prepared_execution_seconds"],
            "output_sha256": _digest(v4["output"]),
            "traversal_receipt": v4["traversal_receipt"],
            "lifecycle_receipt": v4["lifecycle_receipt"],
        },
        "v2_direct": {
            "matched": True,
            "prepare_seconds_observed_not_formal": v2_prepare,
            "execute_seconds_observed_not_formal": v2_execute,
            "output_sha256": output_sha,
            "traversal_receipt": receipt,
        },
        "claim_boundary": {
            "formal_performance_claimed": False,
            "modern_rtx_claimed": False,
            "exact_paper_input_claimed": False,
            "same_source_level_b_only": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
    print(json.dumps({
        "status": "passed", "rows": len(data["expected"]),
        "v2_execute": v2_execute,
        "v4_execute": v4["registered_prepared_execution_seconds"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
