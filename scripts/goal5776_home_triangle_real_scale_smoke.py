#!/usr/bin/env python3
"""Untimed real-SNAP correctness/capacity/true-OptiX V2/V4 gate."""

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

from rtdsl.physical_execution_provenance import OptixTraversalAuditSession
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _receipt_ok(receipt: dict[str, object]) -> bool:
    snapshot = dict(receipt["native_snapshot"])
    successful = int(snapshot["successful_launch_count"])
    return (
        receipt["physical_executor_classification"] == "optix_traversal_observed"
        and successful > 0
        and int(snapshot["complete_context_launch_count"]) == successful
        and all(int(snapshot[name]) == 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error"))
        and bool(snapshot["first_traversable"])
        and bool(snapshot["last_traversable"])
    )


def _runtime(native: Path, optix_include: Path, cuda_include: Path):
    return {
        "target": ReferenceTargetProfile(
            provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
            native_sha256=_sha(native), supports_custom_aabb=True,
            supports_builtin_triangle=True),
        "compute_capability": (6, 1),
        "optix_include": optix_include,
        "cuda_include": cuda_include,
        "expected_python_version": platform.python_version(),
        "expected_numba_version": numba.__version__,
        "expected_numpy_version": np.__version__,
        "native_library_path": native,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--edge-file", required=True, type=Path)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--expected-triangle-count", required=True, type=int)
    parser.add_argument("--max-relation-rows", type=int, default=1_000_000)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    source = args.source_root.resolve()
    edge_file = args.edge_file.resolve()
    native = args.native.resolve()
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    v2_app = _load(
        source / "Paper-reproduction-apps/triangle-counting-paper/v2_14_whole_app.py",
        "goal5776_triangle_v2")
    v4_app = _load(
        source / "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
        "goal5776_triangle_v4")
    from rtdsl import optix_runtime
    library = optix_runtime._load_optix_library()
    runtime = _runtime(
        native, args.optix_include.resolve(), args.cuda_include.resolve())
    rows = []
    for algorithm in ("RT-1A2", "RT-2A1"):
        with OptixTraversalAuditSession.open(
            library=library, library_path=native) as audit:
            v2_started = time.perf_counter()
            v2 = v2_app.run_v2_14(
                paper_algorithm=algorithm, backend="optix",
                edge_file=str(edge_file), edge_format="binary",
                expected_triangle_count=args.expected_triangle_count,
                segmented=True, max_relation_rows=args.max_relation_rows)
            v2_seconds = time.perf_counter() - v2_started
            v2_receipt = audit.finish(
                semantic_digest=_sha(edge_file),
                output_digest=hashlib.sha256(str(
                    v2["output"]["triangle_count"]).encode()).hexdigest(),
                route_identity=(
                    f"goal5776:triangle:{algorithm}:v2_direct:segmented_true_optix"),
            )
        prepared = v4_app.prepare_v4_segmented(
            algorithm, **runtime, edge_file=str(edge_file),
            expected_triangle_count=args.expected_triangle_count,
            max_relation_rows=args.max_relation_rows)
        v4 = prepared.execute()
        if not v2["matched"] or not v4["matched"] or \
                int(v2["output"]["triangle_count"]) != args.expected_triangle_count or \
                int(v4["output"]["triangle_count"]) != args.expected_triangle_count:
            raise RuntimeError(f"{algorithm} disagrees with author triangle count")
        if not _receipt_ok(v2_receipt) or \
                not v4["traversal_receipts"] or \
                not all(_receipt_ok(item) for item in v4["traversal_receipts"]):
            raise RuntimeError(f"{algorithm} behavioral true-OptiX gate failed")
        rows.append({
            "paper_algorithm": algorithm,
            "expected_triangle_count": args.expected_triangle_count,
            "v2_direct": {
                "matched": True,
                "complete_seconds_observed_not_formal": v2_seconds,
                "segment_count": int(v2["source_result"]["segment_count"]),
                "traversal_receipt": v2_receipt,
            },
            "v4": {
                "matched": True,
                "prepare_seconds_observed_not_formal": prepared.total_prepare_seconds,
                "execute_seconds_observed_not_formal": v4[
                    "registered_prepared_execution_seconds"],
                "segment_count": int(v4["segment_count"]),
                "traversal_receipts": v4["traversal_receipts"],
                "device_columns_preserved": True,
                "per_ray_host_materialized": False,
            },
        })
    result = {
        "schema": "rtdl.goal5776.triangle_real_scale_home_smoke.v1",
        "status": "passed",
        "scope": "untimed_functional_capacity_and_behavioral_optix_only",
        "registered_performance_observation_created": False,
        "dataset": args.dataset,
        "edge_file_sha256": _sha(edge_file),
        "edge_file_bytes": edge_file.stat().st_size,
        "expected_triangle_count": args.expected_triangle_count,
        "max_relation_rows": args.max_relation_rows,
        "native_library_sha256": _sha(native),
        "rows": rows,
        "correct_lane_count": 4,
        "behavioral_true_optix_lane_count": 4,
        "claim_boundary": {
            "application_selected_both_algorithms_separately": True,
            "default_selected_between_algorithms": False,
            "formal_performance_claimed": False,
            "modern_rtx_claimed": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "passed", "dataset": args.dataset,
        "segments": {row["paper_algorithm"]: row["v4"]["segment_count"]
                     for row in rows},
    }, sort_keys=True))


if __name__ == "__main__":
    main()
