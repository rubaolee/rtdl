#!/usr/bin/env python3
"""Untimed Home capacity/correctness gate for RayJoin top4 county x zipcode."""

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


def _v2_output(protocol: dict[str, object]) -> tuple[dict[str, object], ...]:
    rows = tuple(protocol["measured_rows"])
    result = []
    for index, row in enumerate(rows):
        result.append({
            "batch_index": index,
            "lsi_row_count": int(row["lsi_row_count"]),
            "descriptor_pair_count": int(row["descriptor_pair_count"]),
            "total_groups": int(row.get("descriptor_total_groups", 0)),
            "total_point_rows": int(row.get("descriptor_total_point_rows", 0)),
            "pair_rows_sha256": row.get("descriptor_pair_rows_sha256"),
        })
    return tuple(result)


def _common_output(rows) -> tuple[tuple[object, ...], ...]:
    return tuple((
        int(row["batch_index"]), int(row["lsi_row_count"]),
        int(row["descriptor_pair_count"]), int(row.get("total_groups", 0)),
        int(row.get("total_point_rows", 0)), row.get("pair_rows_sha256"),
    ) for row in rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--left", required=True, type=Path)
    parser.add_argument("--right", required=True, type=Path)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--capacity", type=int, default=1_000_000)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.source_root.resolve()
    native = args.native.resolve()
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    app = _load(root / "Paper-reproduction-apps/rayjoin-paper/v4_whole_app.py",
                "goal5776_rayjoin_v4")
    legacy = _load(root / "Paper-reproduction-apps/rayjoin-paper/rtdl3_whole_app.py",
                   "goal5776_rayjoin_existing_partners")
    target = ReferenceTargetProfile(
        provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
        native_sha256=_sha(native), supports_custom_aabb=True,
        supports_builtin_triangle=True)

    started = time.perf_counter()
    v4 = app.run_v4_real_scale_six_batch(
        args.left, args.right, lsi_capacity=args.capacity, target=target,
        compute_capability=(6, 1), optix_include=args.optix_include.resolve(),
        cuda_include=args.cuda_include.resolve(),
        expected_python_version=platform.python_version(),
        expected_numba_version=numba.__version__,
        expected_numpy_version=np.__version__, native_library_path=native)
    v4_wall = time.perf_counter() - started
    if not v4["matched"] or not _receipt_ok(v4["traversal_receipt"]):
        raise RuntimeError("V4 RayJoin real-scale gate failed")

    v2_args = legacy.prepared_six_batch_args(
        args.left, args.right, lsi_capacity=args.capacity,
        pair_name="v2_real_scale_six_batch")
    library = _load_optix_library()
    audit = OptixTraversalAuditSession.open(
        library=library, library_path=native)
    try:
        started = time.perf_counter()
        v2_protocol = legacy.run_v2_prepared_six_batch(v2_args)
        v2_wall = time.perf_counter() - started
        v2_output = _v2_output(v2_protocol)
        v2_receipt = audit.finish(
            semantic_digest=_digest({
                "left": _sha(args.left), "right": _sha(args.right),
                "capacity": args.capacity, "batches": 6}),
            output_digest=_digest(v2_output),
            route_identity="goal5776:rayjoin:v2_direct:prepared_six_batch")
    except Exception:
        audit.abort()
        raise
    if not _receipt_ok(v2_receipt):
        raise RuntimeError("V2 RayJoin traversal receipt failed")
    common_v4 = _common_output(v4["output"])
    common_v2 = _common_output(v2_output)
    if common_v4 != common_v2:
        raise RuntimeError("V2/V4 RayJoin six-batch outputs differ")

    result = {
        "schema": "rtdl.goal5776.rayjoin_real_scale_home_smoke.v1",
        "status": "passed",
        "scope": "untimed_functional_capacity_and_behavioral_optix_only",
        "registered_performance_observation_created": False,
        "county_edge_count": 1_705_027, "zipcode_edge_count": 9_982_960,
        "left_sha256": _sha(args.left), "right_sha256": _sha(args.right),
        "capacity": args.capacity, "batch_count": 6,
        "native_library_sha256": _sha(native),
        "canonical_output": common_v4,
        "v4": {
            "wall_seconds_observed_not_formal": v4_wall,
            "physical_lowering": v4["physical_lowering"],
            "callback_ptx_sha256": v4["callback_ptx_sha256"],
            "traversal_receipt": v4["traversal_receipt"],
            "python_candidate_or_event_rows_materialized": False,
        },
        "v2_direct": {
            "wall_seconds_observed_not_formal": v2_wall,
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
        "status": "passed", "batches": 6,
        "v4_wall": v4_wall, "v2_wall": v2_wall}, sort_keys=True))


if __name__ == "__main__":
    main()
