#!/usr/bin/env python3
"""Untimed Home correctness/behavior gate for the 32,768-body RT-BarnesHut case."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

from rtdsl.aggregate_hierarchy_native import (
    prepare_aggregate_frontier_reduce_explicit_native_3d,
)
from rtdsl.optix_runtime import _load_optix_library
from rtdsl.physical_execution_provenance import OptixTraversalAuditSession


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
    path = source_root / "Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py"
    spec = importlib.util.spec_from_file_location("goal5776_rtbh_v4", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load RT-BarnesHut V4 front door")
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


def _project(app, rows, scale: float):
    return app._canonical_force_rows(tuple({
        "source_id": int(row["source_id"]),
        "scalar_force": float(row["reducer_value_0"]) * scale,
    } for row in rows))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--prepared-arrays", required=True, type=Path)
    parser.add_argument("--expected-forces", required=True, type=Path)
    parser.add_argument("--expected-prepared-sha256", required=True)
    parser.add_argument("--expected-forces-sha256", required=True)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    native = args.native.resolve()
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    app = _load_app(source_root)
    data = app.load_real_scale_v4_input(
        args.prepared_arrays, args.expected_forces,
        expected_prepared_sha256=args.expected_prepared_sha256,
        expected_forces_sha256=args.expected_forces_sha256,
    )
    expected = tuple(data["expected_rows"])

    # V4 goes first, preventing reuse of a V2-created owner.
    started = time.perf_counter()
    with app.prepare_v4(prepared_input=data) as owner:
        v4_prepare = time.perf_counter() - started
        v4 = owner.execute(softening=0.0)
    if not v4["matched"] or not _receipt_ok(v4["traversal_receipt"]):
        raise RuntimeError("V4 RT-BarnesHut real-scale gate failed: " + json.dumps({
            "matched": v4["matched"],
            "maximum_abs_delta": v4["maximum_abs_delta"],
            "receipt_ok": _receipt_ok(v4["traversal_receipt"]),
            "snapshot": v4["traversal_receipt"].get("native_snapshot"),
        }, sort_keys=True))

    maximum = data["spec"].prepared_hierarchy.hierarchy.point_count
    started = time.perf_counter()
    v2_owner = prepare_aggregate_frontier_reduce_explicit_native_3d(
        data["spec"], backend="optix_traversal", max_output_rows=maximum)
    v2_prepare = time.perf_counter() - started
    library = _load_optix_library()
    try:
        with OptixTraversalAuditSession.open(
            library=library, library_path=native) as audit:
            started = time.perf_counter()
            physical = v2_owner.execute(softening=0.0)
            v2_execute = time.perf_counter() - started
            v2_output = _project(
                app, physical["rows"], float(data["force_scale"]))
            v2_receipt = audit.finish(
                semantic_digest=data["input_sha256"],
                output_digest=_digest(v2_output),
                route_identity=(
                    "goal5776:rt_barneshut:v2_direct:true_optix:32768"),
            )
    finally:
        v2_owner.close()
    v2_comparison = app._compare_force_rows(v2_output, expected)
    if not v2_comparison["matched"] or not _receipt_ok(v2_receipt):
        raise RuntimeError("V2 RT-BarnesHut real-scale gate failed")

    result = {
        "schema": "rtdl.goal5776.rt_barneshut_real_scale_home_smoke.v1",
        "status": "passed",
        "scope": "untimed_functional_capacity_and_behavioral_optix_only",
        "registered_performance_observation_created": False,
        "body_count": len(expected),
        "hierarchy_node_count": int(data["spec"].prepared_hierarchy.hierarchy.node_count),
        "input_sha256": data["input_sha256"],
        "prepared_arrays_sha256": data["prepared_arrays_sha256"],
        "expected_forces_sha256": data["expected_forces_sha256"],
        "native_library_sha256": _sha(native),
        "v4": {
            "matched": True,
            "maximum_abs_delta": v4["maximum_abs_delta"],
            "maximum_rel_delta": v4["maximum_rel_delta"],
            "mismatch_count": v4["mismatch_count"],
            "prepare_seconds_observed_not_formal": v4_prepare,
            "execute_seconds_observed_not_formal": v4[
                "registered_prepared_execution_seconds"],
            "output_sha256": _digest(v4["output"]),
            "traversal_receipt": v4["traversal_receipt"],
            "lifecycle_receipt": v4["lifecycle_receipt"],
        },
        "v2_direct": {
            "matched": True,
            "maximum_abs_delta": v2_comparison["maximum_abs_delta"],
            "maximum_rel_delta": v2_comparison["maximum_rel_delta"],
            "mismatch_count": v2_comparison["mismatch_count"],
            "prepare_seconds_observed_not_formal": v2_prepare,
            "execute_seconds_observed_not_formal": v2_execute,
            "output_sha256": _digest(v2_output),
            "traversal_receipt": v2_receipt,
        },
        "claim_boundary": {
            "formal_performance_claimed": False,
            "modern_rtx_claimed": False,
            "author_runtime_ratio_claimed": False,
            "paper_input_and_output_contract_preserved": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
    print(json.dumps({
        "status": "passed", "bodies": len(expected),
        "v2_execute": v2_execute,
        "v4_execute": v4["registered_prepared_execution_seconds"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
