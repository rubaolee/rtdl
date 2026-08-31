#!/usr/bin/env python3
"""Two-consumer Home proof for the V4 prepared triangle-reduction owner."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys

import numba
import numpy as np

from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


ROOT = Path(__file__).resolve().parents[1]


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load(name, relative):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    return module


def _record(consumer, call_index, result):
    receipt = result["traversal_receipt"]
    snapshot = receipt["native_snapshot"]
    successful = int(snapshot["successful_launch_count"])
    lifecycle = result["lifecycle_receipt"]
    if (
        result["matched"] is not True
        or receipt["physical_executor_classification"]
        != "optix_traversal_observed"
        or successful <= 0
        or int(snapshot["complete_context_launch_count"]) != successful
        or any(int(snapshot[name]) != 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error"))
    ):
        raise RuntimeError(json.dumps({
            "consumer": consumer,
            "matched": result["matched"],
            "physical": receipt["physical_executor_classification"],
            "successful": successful,
            "complete": snapshot["complete_context_launch_count"],
            "failed": snapshot["failed_launch_count"],
            "incomplete": snapshot["incomplete_context_launch_count"],
            "pending": snapshot["pending_context_at_finish"],
            "session_error": snapshot["session_error"],
            "output": result["output"],
            "expected": result["expected"],
        }, sort_keys=True))
    return {
        "consumer": consumer,
        "call_index": call_index,
        "matched": True,
        "output": result["output"],
        "expected": result["expected"],
        "output_sha256": receipt["output_digest"],
        "traversal_receipt_sha256": receipt["receipt_sha256"],
        "provider_library_sha256": receipt["provider_library_sha256"],
        "physical_executor_classification": receipt[
            "physical_executor_classification"],
        "successful_launch_count": successful,
        "complete_context_launch_count": int(
            snapshot["complete_context_launch_count"]),
        "failed_launch_count": int(snapshot["failed_launch_count"]),
        "incomplete_context_launch_count": int(
            snapshot["incomplete_context_launch_count"]),
        "pending_context_at_finish": int(snapshot["pending_context_at_finish"]),
        "session_error": int(snapshot["session_error"]),
        "first_traversable": int(snapshot["first_traversable"]),
        "last_traversable": int(snapshot["last_traversable"]),
        "session_identity": lifecycle["session_identity"],
        "execution_count": lifecycle["execution_count"],
        "registered_prepared_execution_seconds": result[
            "registered_prepared_execution_seconds"],
        "reported_total_prepare_seconds": result[
            "reported_total_prepare_seconds"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    target = ReferenceTargetProfile(
        provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
        native_sha256=_sha(args.native), supports_custom_aabb=True,
        supports_builtin_triangle=True)
    kwargs = {
        "target": target, "compute_capability": (6, 1),
        "optix_include": args.optix_include, "cuda_include": args.cuda_include,
        "expected_python_version": platform.python_version(),
        "expected_numba_version": numba.__version__,
        "expected_numpy_version": np.__version__,
        "native_library_path": args.native,
    }
    triangle = _load(
        "goal5773_home_triangle",
        "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py")
    raydb = _load(
        "goal5773_home_raydb",
        "Paper-reproduction-apps/raydb-paper/v4_whole_app.py")
    records = []
    for algorithm in triangle.FORMAL_PAPER_ALGORITHMS:
        with triangle.prepare_v4(algorithm, **kwargs) as prepared:
            data = prepared.prepared_input
            records.append(_record(
                f"triangle_counting_{algorithm}", 0, prepared.execute()))
            reversed_queries = tuple(reversed(data.queries))
            query_metadata = {
                key: tuple(reversed(value))
                for key, value in data.metadata.items()
                if key.startswith("query.")}
            records.append(_record(
                f"triangle_counting_{algorithm}", 1,
                prepared.execute(
                    queries=reversed_queries,
                    query_metadata=query_metadata)))
    with raydb.prepare_v4(**kwargs) as prepared:
        records.append(_record("raydb_q21", 0, prepared.execute()))
        # Launch index is the verified reducer key for this RayDB schema, so
        # query ordering is application semantics rather than a free physical
        # permutation.  Exercise a distinct live query value without changing
        # that key binding: the longer finite tmax preserves this frozen scene's
        # exact result while proving execute-time query storage is not cached.
        longer_queries = tuple(
            (origin, direction, float(tmax) + 1.0)
            for origin, direction, tmax in prepared.prepared_input.queries)
        records.append(_record(
            "raydb_q21", 1,
            prepared.execute(queries=longer_queries)))
    for consumer in sorted({row["consumer"] for row in records}):
        rows = [row for row in records if row["consumer"] == consumer]
        if (
            len(rows) != 2
            or [row["execution_count"] for row in rows] != [1, 2]
            or len({row["session_identity"] for row in rows}) != 1
        ):
            raise RuntimeError(f"{consumer} did not prove reuse")
    result = {
        "schema": "rtdl.goal5773.home_triangle_reduction_lifecycle.v1",
        "native_library_sha256": _sha(args.native),
        "consumer_lane_count": 3,
        "prepared_owner_count": 3,
        "distinct_dynamic_call_count": 6,
        "exact_output_count": 6,
        "behavioral_true_optix_count": 6,
        "records": records,
        "formal_performance_row_created": False,
        "cold_result_replaced": False,
        "speed_or_no_slower_claimed": False,
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
