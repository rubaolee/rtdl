#!/usr/bin/env python3
"""Home functional validation for V4 M6 hierarchy-frontier composition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import rtdsl as rt
from rtdsl.v4_hierarchy_frontier import (
    HierarchyFrontierSchema,
    HierarchyReducer,
    compile_hierarchy_frontier,
    execute_hierarchy_frontier,
    hierarchy_content_sha256,
)

from goal5764_m6_hierarchy_fixtures import (
    hierarchy_coverage_fixture,
    rt_barneshut_author_fixture,
)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _schema(spec, producer_name: str, reducer: HierarchyReducer):
    hierarchy = spec.prepared_hierarchy.hierarchy
    return HierarchyFrontierSchema(
        producer_contract_sha256=hashlib.sha256(producer_name.encode()).hexdigest(),
        hierarchy_sha256=hierarchy_content_sha256(spec),
        reducer=reducer,
        maximum_output_rows=hierarchy.point_count,
        maximum_visits_per_source=hierarchy.node_count * 2 + 1,
    )


def _hierarchy_columns(spec) -> dict[str, object]:
    hierarchy = spec.prepared_hierarchy.hierarchy
    return {
        name: getattr(hierarchy, name)
        for name in (
            "point_x", "point_y", "point_z", "point_weight",
            "node_cx", "node_cy", "node_cz", "node_half_size", "node_weight",
            "member_offsets", "member_indices", "child_offsets", "child_indices",
            "node_next_index", "node_rope_index", "source_leaf_node_index",
            "node_subtree_end_index",
        )
    }


def _run_author() -> dict[str, object]:
    spec, expected_rows, metadata = rt_barneshut_author_fixture(256)
    schema = _schema(
        spec,
        "author_prepared_aggregate_hierarchy_force_v1",
        HierarchyReducer.INVERSE_SQUARE_SCALAR_SUM,
    )
    compiled = compile_hierarchy_frontier(spec, schema)
    result = execute_hierarchy_frontier(compiled, spec)
    actual_force = tuple({
        "source_id": int(row["source_id"]),
        "scalar_force": float(row["reducer_value_0"]) * metadata["force_scale"],
    } for row in result.rows)
    maximum_delta = max(
        abs(float(left["scalar_force"]) - float(right["scalar_force"]))
        for left, right in zip(actual_force, expected_rows)
    )
    if maximum_delta > 1.0e-9:
        raise RuntimeError(f"author force mismatch: {maximum_delta}")
    return {
        "lane": "rt_barneshut.aggregate_hierarchy.frontier_reduce.v1",
        "input": {
            "hierarchy_columns": _hierarchy_columns(spec),
            "opening": spec.opening.to_metadata(),
            "reducer": spec.reducer,
            "softening": 0.0,
        },
        "paper_reference": metadata,
        "expected_rows": expected_rows,
        "actual_force_rows": actual_force,
        "native_rows": result.rows,
        "maximum_abs_delta": maximum_delta,
        "exact_output_matched": True,
        "compiled": compiled.to_dict(),
        "output_sha256": result.output_sha256,
        "traversal_receipt": result.traversal_receipt,
        "endpoint_metadata": result.endpoint_metadata,
    }


def _run_coverage() -> dict[str, object]:
    spec, metadata = hierarchy_coverage_fixture()
    schema = _schema(
        spec,
        metadata["consumer_contract"],
        HierarchyReducer.AGGREGATE_COUNT,
    )
    compiled = compile_hierarchy_frontier(spec, schema)
    result = execute_hierarchy_frontier(compiled, spec)
    actual = tuple(float(row["reducer_value_0"]) for row in result.rows)
    if actual != metadata["expected_reducer_values"]:
        raise RuntimeError(f"coverage count mismatch: {actual!r}")
    return {
        "lane": "hierarchical_spatial_coverage.aggregate_count.v1",
        "input": {
            "hierarchy_columns": _hierarchy_columns(spec),
            "opening": spec.opening.to_metadata(),
            "reducer": spec.reducer,
            "softening": 0.0,
        },
        "consumer": metadata,
        "expected_reducer_values": metadata["expected_reducer_values"],
        "native_rows": result.rows,
        "exact_output_matched": True,
        "compiled": compiled.to_dict(),
        "output_sha256": result.output_sha256,
        "traversal_receipt": result.traversal_receipt,
        "endpoint_metadata": result.endpoint_metadata,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    lanes = (_run_author(), _run_coverage())
    native_ids = {
        lane["traversal_receipt"]["provider_library_sha256"] for lane in lanes
    }
    result = {
        "schema": "rtdl.goal5764.home_hierarchy_frontier_result.v1",
        "goal": 5764,
        "scope": "functional_only_no_registered_performance_timing",
        "lane_count": 2,
        "exact_output_count": 2,
        "behavioral_true_optix_count": 2,
        "native_identity_count": len(native_ids),
        "program_bundle_count": 1,
        "registered_performance_timing_count": 0,
        "trace_depth": 1,
        "callable_depth": 0,
        "lanes": lanes,
        "claim_boundary": {
            "rt_barneshut_representative_lane_closed": True,
            "second_real_nonpaper_consumer_closed": True,
            "full_paper_app_migrated": False,
            "modern_rtx_or_rt_silicon_measured": False,
            "performance_claimed": False,
        },
    }
    path = args.output / "RESULT.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "lanes": 2,
        "exact": 2,
        "behavioral_optix": 2,
        "result": str(path),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
