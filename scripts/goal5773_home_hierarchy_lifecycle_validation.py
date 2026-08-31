#!/usr/bin/env python3
"""Home functional proof for reusable V4 hierarchy owners.

Runs one paper consumer and one app-neutral non-paper consumer twice each with
distinct dynamic softening.  This is functional evidence, not performance.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

import rtdsl as rt
from rtdsl.v4_hierarchy_frontier import (
    HierarchyFrontierSchema,
    HierarchyReducer,
    compile_hierarchy_frontier,
    hierarchy_content_sha256,
    prepare_hierarchy_frontier,
)


ROOT = Path(__file__).resolve().parents[1]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str, relative: str):
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


def _validate(record, *, expected, tolerance=1.0e-9):
    traversal = record.traversal_receipt
    snapshot = traversal["native_snapshot"]
    successful = int(snapshot["successful_launch_count"])
    if (
        traversal["physical_executor_classification"]
        != "optix_traversal_observed"
        or successful <= 0
        or int(snapshot["complete_context_launch_count"]) != successful
        or any(int(snapshot[name]) != 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error"))
        or not snapshot["first_traversable"]
        or not snapshot["last_traversable"]
    ):
        raise RuntimeError("hierarchy call lacked complete bound traversal")
    actual = tuple(float(row["reducer_value_0"]) for row in record.rows)
    delta = max(abs(left - right) for left, right in zip(
        actual, expected, strict=True))
    if delta > tolerance:
        raise RuntimeError(f"hierarchy result mismatch: {delta}")
    return {
        "matched": True,
        "output": actual,
        "expected": expected,
        "maximum_abs_delta": delta,
        "output_sha256": record.output_sha256,
        "traversal_receipt_sha256": traversal["receipt_sha256"],
        "provider_library_sha256": traversal["provider_library_sha256"],
        "physical_executor_classification": traversal[
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
    }


def _reference_values(spec, softening):
    count = spec.prepared_hierarchy.hierarchy.point_count
    endpoint = rt.aggregate_frontier_reduce_reference_3d(
        rt.aggregate_frontier_reduce_execution_contract_3d(
            spec, backend="reference", max_output_rows=count),
        softening=softening,
    )
    return tuple(float(row["reducer_value_0"]) for row in endpoint["rows"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)

    app = _load(
        "goal5773_home_rtbh",
        "Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py")
    fixtures = _load(
        "goal5773_home_hierarchy_fixtures",
        "scripts/goal5764_m6_hierarchy_fixtures.py")
    records = []

    with app.prepare_v4(body_count=256) as prepared:
        session = prepared.owner.lifecycle_receipt["session_identity"]
        for index, softening in enumerate((0.0, 0.125)):
            record = prepared.execute(softening=softening)
            if record["matched"] is not True:
                raise RuntimeError("RT-BarnesHut prepared result mismatch")
            receipt = record["traversal_receipt"]
            snapshot = receipt["native_snapshot"]
            records.append({
                "consumer": "rt_barneshut_paper",
                "call_index": index,
                "softening": softening,
                "session_identity": session,
                "execution_count": record["lifecycle_receipt"]["execution_count"],
                "matched": True,
                "output": record["output"],
                "expected": record["expected"],
                "maximum_abs_delta": record["maximum_abs_delta"],
                "output_sha256": receipt["output_digest"],
                "traversal_receipt_sha256": receipt["receipt_sha256"],
                "provider_library_sha256": receipt["provider_library_sha256"],
                "physical_executor_classification": receipt[
                    "physical_executor_classification"],
                "successful_launch_count": snapshot["successful_launch_count"],
                "complete_context_launch_count": snapshot[
                    "complete_context_launch_count"],
                "failed_launch_count": snapshot["failed_launch_count"],
                "incomplete_context_launch_count": snapshot[
                    "incomplete_context_launch_count"],
                "pending_context_at_finish": snapshot["pending_context_at_finish"],
                "session_error": snapshot["session_error"],
                "first_traversable": snapshot["first_traversable"],
                "last_traversable": snapshot["last_traversable"],
                "registered_prepared_execution_seconds": record[
                    "registered_prepared_execution_seconds"],
                "reported_total_prepare_seconds": record[
                    "reported_total_prepare_seconds"],
            })

    base, metadata = fixtures.hierarchy_coverage_fixture()
    nonpaper_spec = rt.aggregate_frontier_reduce_spec_3d(
        base.prepared_hierarchy,
        opening=base.opening,
        reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM,
    )
    count = nonpaper_spec.prepared_hierarchy.hierarchy.point_count
    schema = HierarchyFrontierSchema(
        producer_contract_sha256=hashlib.sha256(
            b"hierarchical_spatial_field_intensity_v1").hexdigest(),
        hierarchy_sha256=hierarchy_content_sha256(nonpaper_spec),
        reducer=HierarchyReducer.INVERSE_SQUARE_SCALAR_SUM,
        maximum_output_rows=count,
        maximum_visits_per_source=(
            nonpaper_spec.prepared_hierarchy.hierarchy.node_count * 2 + 1),
    )
    compiled = compile_hierarchy_frontier(nonpaper_spec, schema)
    with prepare_hierarchy_frontier(compiled, nonpaper_spec) as prepared:
        session = prepared.lifecycle_receipt["session_identity"]
        prepare_seconds = prepared.prepare_seconds
        for index, softening in enumerate((0.0, 0.25)):
            started = time.perf_counter()
            executed = prepared.execute(softening=softening)
            execute_seconds = time.perf_counter() - started
            validated = _validate(
                executed,
                expected=_reference_values(nonpaper_spec, softening),
            )
            records.append({
                "consumer": "nonpaper_hierarchical_field_intensity",
                "consumer_contract": metadata["consumer_contract"],
                "call_index": index,
                "softening": softening,
                "session_identity": session,
                "execution_count": prepared.lifecycle_receipt["execution_count"],
                "reported_total_prepare_seconds": prepare_seconds,
                "registered_prepared_execution_seconds": execute_seconds,
                **validated,
            })

    for consumer in (
        "rt_barneshut_paper", "nonpaper_hierarchical_field_intensity"):
        rows = [row for row in records if row["consumer"] == consumer]
        if (
            len(rows) != 2
            or [row["execution_count"] for row in rows] != [1, 2]
            or len({row["session_identity"] for row in rows}) != 1
            or len({row["softening"] for row in rows}) != 2
            or any(row["matched"] is not True for row in rows)
            or any(row["physical_executor_classification"]
                   != "optix_traversal_observed" for row in rows)
        ):
            raise RuntimeError(f"{consumer} did not prove prepared reuse")

    result = {
        "schema": "rtdl.goal5773.home_hierarchy_lifecycle.v1",
        "native_library_sha256": _sha(args.native),
        "consumer_count": 2,
        "prepared_owner_count": 2,
        "distinct_dynamic_call_count": 4,
        "exact_output_count": 4,
        "behavioral_true_optix_count": 4,
        "records": records,
        "formal_performance_row_created": False,
        "speed_or_no_slower_claimed": False,
        "cold_result_replaced": False,
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
