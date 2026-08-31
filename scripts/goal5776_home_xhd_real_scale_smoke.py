#!/usr/bin/env python3
"""Untimed Home correctness/behavior gate for full Dragon -> HappyBuddha X-HD."""

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


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load X-HD module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
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


def _global_witness(value: dict[str, object]) -> dict[str, object]:
    return {
        "source_id": int(value["source_id"]),
        "item_id": int(value["item_id"]),
        "value": float(value["value"]),
    }


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
    app = _load(
        source_root / "Paper-reproduction-apps/x-hd-paper/v4_whole_app.py",
        "goal5776_xhd_v4")
    v2_module = _load(
        source_root / "Paper-reproduction-apps/x-hd-paper/v2_true_optix_direct.py",
        "goal5776_xhd_v2")
    data = app.load_real_scale_v4_input(args.input_root)
    expected_global = _global_witness(data["expected"])
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

    # Run V4 first so it cannot inherit a V2-created physical owner.
    started = time.perf_counter()
    with app.prepare_v4(**runtime, prepared_input=data) as owner:
        v4_prepare = time.perf_counter() - started
        v4 = owner.execute(data["sources"])
    if not v4["matched"] or not _receipt_ok(v4["traversal_receipt"]):
        raise RuntimeError("V4 X-HD real-scale gate failed")
    v4_global = _global_witness(v4["output"])

    library = _load_optix_library()
    with OptixTraversalAuditSession.open(
        library=library, library_path=native) as audit:
        started = time.perf_counter()
        v2 = v2_module.run_loaded_true_optix_direct(
            data["sources"], data["targets"])
        v2_total = time.perf_counter() - started
        v2_global = {
            "source_id": int(v2["witness"]["source_id"]),
            "item_id": int(v2["witness"]["target_id"]),
            "value": float(v2["witness"]["distance"]),
        }
        v2_receipt = audit.finish(
            semantic_digest=data["input_sha256"],
            output_digest=_digest(v2_global),
            route_identity="goal5776:xhd:v2_direct:true_optix:dragon_happy",
        )
    v2_match = (
        v2_global["source_id"] == expected_global["source_id"]
        and v2_global["item_id"] == expected_global["item_id"]
        and abs(v2_global["value"] - expected_global["value"]) <= 1.0e-7
    )
    if not v2_match or not _receipt_ok(v2_receipt):
        raise RuntimeError("V2 X-HD real-scale gate failed: " + json.dumps({
            "actual": v2_global, "expected": expected_global,
            "receipt_ok": _receipt_ok(v2_receipt),
        }, sort_keys=True))

    result = {
        "schema": "rtdl.goal5776.xhd_real_scale_home_smoke.v1",
        "status": "passed",
        "scope": "untimed_functional_capacity_and_behavioral_optix_only",
        "registered_performance_observation_created": False,
        "source_count": len(data["sources"]),
        "target_count": len(data["targets"]),
        "input_manifest_sha256": data["input_sha256"],
        "native_library_sha256": _sha(native),
        "expected_global_witness": expected_global,
        "v4": {
            "matched": True,
            "prepare_seconds_observed_not_formal": v4_prepare,
            "execute_seconds_observed_not_formal": v4[
                "registered_prepared_execution_seconds"],
            "global_witness": v4_global,
            "full_output_sha256": _digest(v4["output"]),
            "traversal_receipt": v4["traversal_receipt"],
            "lifecycle_receipt": v4["lifecycle_receipt"],
        },
        "v2_direct": {
            "matched": True,
            "complete_seconds_observed_not_formal": v2_total,
            "global_witness": v2_global,
            "output_sha256": _digest(v2_global),
            "traversal_receipt": v2_receipt,
        },
        "claim_boundary": {
            "formal_performance_claimed": False,
            "modern_rtx_claimed": False,
            "author_runtime_ratio_claimed": False,
            "route_independent_full_per_query_oracle_checked_by_v4": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
    print(json.dumps({
        "status": "passed", "sources": len(data["sources"]),
        "targets": len(data["targets"]),
        "v2_complete": v2_total,
        "v4_execute": v4["registered_prepared_execution_seconds"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
