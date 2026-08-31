#!/usr/bin/env python3
"""Untimed Home correctness/behavior gate for the 59,986,052-row RayDB packet."""

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
        raise RuntimeError(f"cannot load module: {path}")
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--partition-rows", type=int, default=5_000_000)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.source_root.resolve()
    native = args.native.resolve()
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    app = _load(root / "Paper-reproduction-apps/raydb-paper/v4_whole_app.py",
                "goal5776_raydb_v4")
    runner = _load(root / "Paper-reproduction-apps/raydb-paper/run_ssb_packet_rtdl.py",
                   "goal5776_raydb_v2")
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
    # V4 first: it cannot inherit any V2 physical state.
    v4_started = time.perf_counter()
    v4 = app.run_v4_real_scale_packet(
        **runtime, packet_path=args.packet.resolve(),
        partition_rows=args.partition_rows)
    v4_wall = time.perf_counter() - v4_started
    if not v4["matched"] or not _receipt_ok(v4["traversal_receipt"]):
        raise RuntimeError("V4 RayDB real-scale gate failed")

    library = _load_optix_library()
    with OptixTraversalAuditSession.open(
            library=library, library_path=native) as audit:
        v2_started = time.perf_counter()
        v2 = runner.run_packet(
            args.packet.resolve(), partition_rows=args.partition_rows)
        v2_wall = time.perf_counter() - v2_started
        v2_output = tuple(
            (tuple(row["group"]), int(row["value"])) for row in v2["rtdl_rows"])
        v2_receipt = audit.finish(
            semantic_digest=v2["packet_json_sha256"],
            output_digest=_digest(v2_output),
            route_identity="goal5776:raydb:v2_direct:partitioned_optix")
    if not v2["rtdl_matches_oracle"] or not _receipt_ok(v2_receipt):
        raise RuntimeError("V2 RayDB real-scale gate failed")
    if v4["output"]["grouped_rows"] != v2["rtdl_rows"]:
        raise RuntimeError("V2/V4 RayDB output mismatch")

    result = {
        "schema": "rtdl.goal5776.raydb_real_scale_home_smoke.v1",
        "status": "passed",
        "scope": "untimed_functional_capacity_and_behavioral_optix_only",
        "registered_performance_observation_created": False,
        "row_count": v4["row_count"],
        "partition_rows": args.partition_rows,
        "input_packet_sha256": _sha(args.packet.resolve()),
        "native_library_sha256": _sha(native),
        "output": v4["output"],
        "v4": {
            "matched": True,
            "wall_seconds_observed_not_formal": v4_wall,
            "compiler_seconds_observed_not_formal": v4["reported_compiler_seconds"],
            "complete_packet_seconds_observed_not_formal":
                v4["reported_complete_packet_seconds"],
            "physical_lowering": v4["physical_lowering"],
            "partition_count": v4["partition_count"],
            "traversal_receipt": v4["traversal_receipt"],
        },
        "v2_direct": {
            "matched": True,
            "wall_seconds_observed_not_formal": v2_wall,
            "complete_packet_seconds_observed_not_formal":
                v2["registered_primary_timing"]["elapsed_seconds"],
            "partition_count": v2["partition_count"],
            "traversal_receipt": v2_receipt,
        },
        "claim_boundary": {
            "formal_performance_claimed": False,
            "modern_rtx_claimed": False,
            "author_runtime_ratio_claimed": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
    print(json.dumps({
        "status": "passed", "rows": v4["row_count"],
        "v4_wall": v4_wall, "v2_wall": v2_wall,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
