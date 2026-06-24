from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import statistics
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.current.apps.simulation import rtdl_barnes_hut_force_app as app


PAPER_REFERENCE = {
    "title": "RT-BarnesHut: Accelerating Barnes-Hut Using Ray-Tracing Hardware",
    "venue": "PPoPP 2025",
    "doi": "10.1145/3710848.3710885",
    "authors": (
        "Vani Nagarajan",
        "Rohan Gangaraju",
        "Kirshanthan Sundararajah",
        "Artem Pelenitsyn",
        "Milind Kulkarni",
    ),
}

BENCHMARK_NAME = "barnes_hut_ppopp2025_style"
BENCHMARK_SCOPE = (
    "RT-BarnesHut-style reconstruction benchmark over generic RTDL spatial "
    "candidate, node-coverage, and partner force-reference contracts."
)
BH_V2_8_GROUPED_VECTOR_TYPED_STREAM_VERSION = "rtdl.barnes_hut.v2_8.grouped_vector_sum_typed_stream.v1"
BH_V2_8_GROUPED_VECTOR_EXECUTION_PATH = "generic_grouped_vector_sum_typed_stream_partner_columns"
CLAIM_BOUNDARY = (
    "Research benchmark / reconstruction instrument only. This is not a full "
    "RT-BarnesHut paper reproduction, not an authors-code comparison, not a "
    "whole N-body solver speedup claim, and not public performance wording."
)

MODES = (
    "scope",
    "cpu_reference",
    "node_coverage_cpu_oracle",
    "rtdl_cpu_rows",
    "embree_rows",
    "opening_rows_cpu",
    "bucketized_tree_cpu",
    "opening_frontier_bucketized_cpu",
    "aggregate_frontier_collect_bucketized_cpu",
    "aggregate_frontier_expanded_membership_cpu",
    "aggregate_frontier_expanded_membership_embree",
    "aggregate_frontier_expanded_membership_optix",
    "aggregate_frontier_weighted_vector_cpu_host",
    "aggregate_frontier_weighted_vector_embree_host",
    "aggregate_frontier_weighted_vector_cpu_host_numba",
    "aggregate_frontier_weighted_vector_embree_host_numba",
    "force_contributions_bucketized_cpu",
    "bucketized_force_cpu",
    "streamed_force_sum_bucketized_cpu",
    "materialization_pressure_bucketized_cpu",
    "fused_frontier_force_sum_bucketized_cpu",
    "fused_frontier_force_sum_bucketized_cpu_numba",
    "fused_frontier_force_sum_bucketized_numba_cuda",
    "prepared_execution_fused_vector_sum_numba_cuda",
    "native_fused_vector_sum_cuda_device",
    "prepared_aggregate_frontier_weighted_vector_optix",
    "grouped_vector_sum_typed_stream_plan",
    "v2_8_grouped_vector_sum_plan",
    "embree_node_coverage_prepared",
    "optix_node_coverage_prepared",
    "partner_exact_force",
)


def _paper_metadata() -> dict[str, Any]:
    return {
        **PAPER_REFERENCE,
        "paper_reproduction": False,
        "authors_code_comparison": False,
    }


def _promotion_metadata(*, mode: str, contract: str, rt_core_accelerated: bool) -> dict[str, Any]:
    return {
        "benchmark": BENCHMARK_NAME,
        "mode": mode,
        "benchmark_scope": BENCHMARK_SCOPE,
        "contract": contract,
        "paper_reference": _paper_metadata(),
        "research_benchmark": True,
        "reconstruction_instrument": True,
        "paper_reproduction": False,
        "authors_code_comparison": False,
        "public_speedup_claim_authorized": False,
        "native_engine_app_specific": False,
        "rt_core_accelerated": rt_core_accelerated,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _annotate(payload: dict[str, Any], *, mode: str, contract: str, rt_core_accelerated: bool) -> dict[str, Any]:
    metadata = _promotion_metadata(
        mode=mode,
        contract=contract,
        rt_core_accelerated=rt_core_accelerated,
    )
    return {
        **payload,
        "benchmark_metadata": metadata,
        "claim_boundary": metadata["claim_boundary"],
        "app_boundary": payload.get("boundary"),
    }


def scope_payload() -> dict[str, Any]:
    return {
        "benchmark_metadata": _promotion_metadata(
            mode="scope",
            contract="benchmark_scope_and_gap_matrix",
            rt_core_accelerated=False,
        ),
        "current_supported_contracts": (
            "one_level_body_to_quadtree_node_candidate_rows",
            "prepared_fixed_radius_node_coverage_threshold_decision_embree",
            "prepared_fixed_radius_node_coverage_threshold_decision_optix",
            "generic_aggregate_opening_rows_2d_v1",
            "generic_bucketized_aggregate_tree_2d_v1",
            "generic_aggregate_tree_opening_frontier_2d_v1",
            "generic_aggregate_frontier_collect_2d_v1",
            "generic_aggregate_frontier_collect_2d_host_weighted_vector_sum_baseline",
            "generic_aggregate_frontier_collect_2d_host_numba_cpu_weighted_vector_sum_baseline",
            "generic_expanded_aabb_point_membership_rows_2d_v1",
            "generic_weighted_inverse_square_contribution_rows_2d_v1",
            "generic_grouped_vector_sum_rows_2d_v1",
            "generic_weighted_inverse_square_vector_sum_2d_v1",
            "generic_vector_sum_materialization_pressure_2d_v1",
            "generic_aggregate_frontier_weighted_vector_sum_2d_v1",
            "generic_aggregate_frontier_weighted_vector_sum_2d_numba_cpu_v1",
            "generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1",
            "generic_aggregate_frontier_device_columns_2d_v1",
            "generic_aggregate_frontier_device_columns_prepared_weighted_vector_sum_2d_v1",
            "generic_aggregate_frontier_device_columns_prepared_weighted_vector_sum_2d_numba_v1",
            "generic_weighted_point_pairwise_inverse_square_force_partner_reference",
        ),
        "current_non_goals": (
            "full RT-BarnesHut paper reproduction",
            "authors-code timing or parity",
            "hierarchical opening-rule acceleration in native Embree/OptiX",
            "paper-code timing without an NVIDIA/OWL/OptiX-capable environment",
            "native force-vector contribution rows",
            "native grouped vector-sum reductions",
            "native aggregate-frontier collection lowering",
            "native fused frontier-to-vector-sum lowering",
            "automatic partner selection across prepared aggregate-frontier routes",
            "timestep integration or full N-body solver",
            "public speedup wording",
        ),
        "runtime_pressure": (
            "hierarchical spatial aggregate descriptors",
            "opening-predicate continuation over tree nodes",
            "bucketized leaf policy and Morton/DFS ordering",
            "vector-valued reductions",
            "partner-resident force accumulation",
            "prepared tree lifetime versus dynamic body state",
        ),
    }


def describe_barnes_hut_v2_8_grouped_vector_sum_typed_stream(
    *,
    partner: str = "cupy",
    presegmented: bool = True,
) -> dict[str, Any]:
    row_offsets = (0, 2, 3) if presegmented else None
    request = rt.execute_grouped_vector_sum_typed_stream_partner_columns(
        group_ids=(0, 0, 1),
        values_x=(1.0, 2.5, -4.0),
        values_y=(-1.0, 0.5, 3.0),
        group_count=2,
        partner=partner,
        stream_id="barnes_hut_v2_8_grouped_vector_sum_descriptor",
        producer_primitive="aggregate_frontier_weighted_vector_columns_2d",
        row_offsets=row_offsets,
        dry_run=True,
    )
    return {
        "benchmark_app": BENCHMARK_NAME,
        "contract_version": BH_V2_8_GROUPED_VECTOR_TYPED_STREAM_VERSION,
        "execution_path": BH_V2_8_GROUPED_VECTOR_EXECUTION_PATH,
        "operation": "grouped_vector_sum_f64x2",
        "partner": partner,
        "presegmented_offsets": presegmented,
        "uses_v2_8_typed_result_stream": True,
        "uses_v2_8_grouped_vector_sum_front_door": True,
        "requires_caller_supplied_partner_columns": True,
        "source_materialization": request["source_materialization"],
        "typed_stream": request["typed_stream"],
        "continuation_plan": request["continuation_plan"],
        "partner_policy": {
            "explicit_user_partner_choice_required": True,
            "automatic_partner_selection_allowed": False,
            "supported_partners": ("cupy", "numba", "torch", "triton"),
            "numba_status": "preview_supported_no_cpp_reference_for_grouped_vector_sum_f64x2",
            "numba_reference_partner_supported": True,
        },
        "claim_boundary": {
            "research_benchmark": True,
            "full_rt_barneshut_paper_reproduction": False,
            "authors_code_comparison": False,
            "native_force_law_embedded": False,
            "native_grouped_vector_sum_promoted": False,
            "device_resident_result_stream_proven": False,
            "true_zero_copy_claim_authorized": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "automatic_partner_selection_allowed": False,
        },
    }


def describe_barnes_hut_grouped_vector_sum_typed_stream(
    *,
    partner: str = "cupy",
    presegmented: bool = True,
) -> dict[str, Any]:
    """Current alias for the legacy v2.8 grouped-vector typed-stream descriptor."""

    descriptor = describe_barnes_hut_v2_8_grouped_vector_sum_typed_stream(
        partner=partner,
        presegmented=presegmented,
    )
    return {
        **descriptor,
        "legacy_helper_alias": "describe_barnes_hut_v2_8_grouped_vector_sum_typed_stream",
        "current_helper": "describe_barnes_hut_grouped_vector_sum_typed_stream",
        "current_mode_alias": "grouped_vector_sum_typed_stream_plan",
    }


def run_barnes_hut_v2_8_grouped_vector_sum_typed_stream_preview(
    inputs: dict[str, Any],
    *,
    partner: str = "cupy",
    dry_run: bool = False,
    triton_offset_groups_per_program: int = 1,
    validate_row_offsets: bool = True,
) -> dict[str, Any]:
    request = rt.execute_grouped_vector_sum_typed_stream_partner_columns(
        group_ids=inputs["group_ids"],
        values_x=inputs["values_x"],
        values_y=inputs["values_y"],
        group_count=int(inputs["group_count"]),
        partner=partner,
        stream_id=str(inputs.get("stream_id", "barnes_hut_v2_8_grouped_vector_sum_preview")),
        producer_primitive=str(inputs.get("producer_primitive", "aggregate_frontier_weighted_vector_columns_2d")),
        row_offsets=inputs.get("row_offsets"),
        triton_offset_groups_per_program=triton_offset_groups_per_program,
        validate_row_offsets=bool(validate_row_offsets),
        dry_run=dry_run,
    )
    return {
        "benchmark_app": BENCHMARK_NAME,
        "contract_version": BH_V2_8_GROUPED_VECTOR_TYPED_STREAM_VERSION,
        "execution_path": BH_V2_8_GROUPED_VECTOR_EXECUTION_PATH,
        **request,
        "claim_boundary": {
            "research_benchmark": True,
            "full_rt_barneshut_paper_reproduction": False,
            "authors_code_comparison": False,
            "native_force_law_embedded": False,
            "native_grouped_vector_sum_promoted": False,
            "device_resident_result_stream_proven": False,
            "true_zero_copy_claim_authorized": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "automatic_partner_selection_allowed": False,
        },
    }


def run_barnes_hut_grouped_vector_sum_typed_stream_preview(
    inputs: dict[str, Any],
    *,
    partner: str = "cupy",
    dry_run: bool = False,
    triton_offset_groups_per_program: int = 1,
    validate_row_offsets: bool = True,
) -> dict[str, Any]:
    """Current alias for the legacy v2.8 grouped-vector typed-stream runner."""

    payload = run_barnes_hut_v2_8_grouped_vector_sum_typed_stream_preview(
        inputs,
        partner=partner,
        dry_run=dry_run,
        triton_offset_groups_per_program=triton_offset_groups_per_program,
        validate_row_offsets=bool(validate_row_offsets),
    )
    return {
        **payload,
        "legacy_helper_alias": "run_barnes_hut_v2_8_grouped_vector_sum_typed_stream_preview",
        "current_helper": "run_barnes_hut_grouped_vector_sum_typed_stream_preview",
    }


def _make_bodies(body_count: int | None) -> tuple[app.Body, ...]:
    return app.make_bodies() if body_count is None else app.make_generated_bodies(body_count)


def _opening_rows_payload(*, body_count: int | None, theta: float) -> dict[str, Any]:
    bodies = _make_bodies(body_count)
    nodes = app.build_one_level_quadtree(bodies)
    candidate_rows = app._run_node_candidates("cpu_python_reference", bodies, nodes)
    opening = rt.evaluate_aggregate_opening_rows_2d(
        bodies,
        nodes,
        theta=theta,
        candidate_rows=candidate_rows,
    )
    return {
        "app": "barnes_hut_force_app",
        "backend": "cpu_python_reference",
        "body_count": len(bodies),
        "node_count": len(nodes),
        "theta": theta,
        "candidate_row_count": len(candidate_rows),
        "opening_rows": {
            "accepted_aggregate_rows": list(opening["accepted_aggregate_rows"]),
            "fallback_exact_rows": list(opening["fallback_exact_rows"]),
            "per_source_summary": opening["per_source_summary"],
            "summary": opening["summary"],
            "metadata": opening["metadata"],
        },
        "boundary": (
            "Generic aggregate opening rows only; force-vector accumulation, "
            "native hierarchical traversal, paper reproduction, and public "
            "speedup wording remain out of scope."
        ),
    }


def _truncate_rows(rows: tuple[object, ...], *, limit: int = 64) -> tuple[list[object], bool]:
    if len(rows) <= limit:
        return list(rows), False
    return list(rows[:limit]), True


def _bucketized_tree_payload(
    *,
    body_count: int | None,
    bucket_size: int,
    max_depth: int,
) -> dict[str, Any]:
    bodies = _make_bodies(body_count)
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    node_sample, truncated = _truncate_rows(tuple(asdict(node) for node in tree["nodes"]))
    return {
        "app": "barnes_hut_force_app",
        "backend": "cpu_python_reference",
        "body_count": len(bodies),
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree": {
            "summary": tree["summary"],
            "metadata": tree["metadata"],
            "ordered_source_ids_sample": list(tree["ordered_source_ids"][:64]),
            "node_sample": node_sample,
            "node_sample_truncated": truncated,
        },
        "boundary": (
            "Generic bucketized aggregate-tree rows only. This adopts the "
            "portable Morton ordering, bucketized leaves, DFS order, and "
            "resume-index metadata from the paper artifact, but it is not "
            "OptiX triangle encoding or authors-code timing."
        ),
    }


def _opening_frontier_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
) -> dict[str, Any]:
    bodies = _make_bodies(body_count)
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    opening = rt.evaluate_aggregate_tree_opening_frontier_2d(
        bodies,
        tree["nodes"],
        theta=theta,
    )
    accepted_sample, accepted_truncated = _truncate_rows(opening["accepted_aggregate_rows"])
    fallback_sample, fallback_truncated = _truncate_rows(opening["fallback_exact_rows"])
    return {
        "app": "barnes_hut_force_app",
        "backend": "cpu_python_reference",
        "body_count": len(bodies),
        "theta": theta,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "opening_frontier": {
            "accepted_aggregate_rows": accepted_sample,
            "fallback_exact_rows": fallback_sample,
            "accepted_aggregate_rows_truncated": accepted_truncated,
            "fallback_exact_rows_truncated": fallback_truncated,
            "per_source_summary": opening["per_source_summary"],
            "summary": opening["summary"],
            "metadata": opening["metadata"],
        },
        "boundary": (
            "Generic hierarchical opening frontier over bucketized aggregate "
            "tree rows only; force-vector accumulation and native RT traversal "
            "remain separate benchmark pressure points."
        ),
    }


def _aggregate_frontier_collect_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
) -> dict[str, Any]:
    bodies = _make_bodies(body_count)
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    collected = rt.collect_aggregate_frontier_2d(
        bodies,
        tree["nodes"],
        theta=theta,
    )
    row_sample, row_truncated = _truncate_rows(collected["frontier_rows"])
    i64_sample, i64_truncated = _truncate_rows(collected["frontier_i64_rows"])
    return {
        "app": "barnes_hut_force_app",
        "backend": "cpu_python_reference",
        "body_count": len(bodies),
        "theta": theta,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "frontier_collection": {
            "frontier_rows": row_sample,
            "frontier_rows_truncated": row_truncated,
            "frontier_i64_rows": i64_sample,
            "frontier_i64_rows_truncated": i64_truncated,
            "source_ids": collected["source_ids"],
            "row_offsets": collected["row_offsets"],
            "row_schema": collected["row_schema"],
            "per_source_summary": collected["per_source_summary"],
            "summary": collected["summary"],
            "metadata": collected["metadata"],
        },
        "boundary": (
            "Generic aggregate-frontier collection only. This emits IDs, kind "
            "codes, and source offsets for partner/native consumers; Barnes-Hut "
            "force math remains app or partner code and is not embedded here."
        ),
    }


def _near_zone_boxes_for_opening_rule(
    tree_nodes: tuple[rt.AggregateTreeNodeRow, ...],
    *,
    theta: float,
) -> tuple[rt.Aabb2D, ...]:
    """Return conservative app-owned near zones for the opening predicate.

    If a source is outside this square, then its Euclidean distance from the
    node center is greater than ``2 * half_size / theta`` and the aggregate
    opening test is definitely true. Sources inside the square still require
    the app-owned exact opening check. The engine only sees boxes and points.
    """

    if theta <= 0.0:
        raise ValueError("theta must be positive")
    boxes: list[rt.Aabb2D] = []
    for node in tree_nodes:
        radius = (2.0 * float(node.half_size)) / float(theta)
        boxes.append(
            rt.Aabb2D(
                float(node.cx) - radius,
                float(node.cy) - radius,
                float(node.cx) + radius,
                float(node.cy) + radius,
            )
        )
    return tuple(boxes)


def _frontier_rows_via_expanded_membership(
    bodies: tuple[app.Body, ...],
    tree_nodes: tuple[rt.AggregateTreeNodeRow, ...],
    *,
    theta: float,
    membership_backend: str,
) -> dict[str, object]:
    """Lower Barnes-Hut frontier discovery onto generic point/AABB rows.

    The generic primitive returns only source/node near-zone rows. This helper
    is app/reference code: it interprets those rows as a conservative opening
    filter and then applies the Barnes-Hut opening decision outside the engine.
    """

    theta = float(theta)
    if theta <= 0.0:
        raise ValueError("theta must be positive")
    source_ids = tuple(int(body.id) for body in bodies)
    node_ids = tuple(int(node.id) for node in tree_nodes)
    near_boxes = _near_zone_boxes_for_opening_rule(tree_nodes, theta=theta)

    membership_start = time.perf_counter()
    membership = rt.expanded_aabb_point_membership_rows_2d(
        near_boxes,
        bodies,
        indexed_ids=node_ids,
        source_ids=source_ids,
        row_capacity=len(source_ids) * len(node_ids),
        backend=membership_backend,
    )
    membership_sec = time.perf_counter() - membership_start

    near_node_ids_by_source: dict[int, set[int]] = {source_id: set() for source_id in source_ids}
    for source_id, node_id, _metadata_flags in membership["candidate_id_rows"]:
        near_node_ids_by_source.setdefault(int(source_id), set()).add(int(node_id))

    node_by_id = {int(node.id): node for node in tree_nodes}
    child_ids = {int(child_id) for node in tree_nodes for child_id in node.child_ids}
    root_ids = tuple(int(node.id) for node in tree_nodes if int(node.id) not in child_ids)
    member_sets = {int(node.id): set(int(member_id) for member_id in node.member_ids) for node in tree_nodes}

    frontier_rows: list[dict[str, object]] = []
    accepted_rows: list[dict[str, object]] = []
    fallback_rows: list[dict[str, object]] = []
    row_offsets = [0]
    per_source: dict[int, dict[str, int]] = {}
    total_visited = 0
    total_aggregate = 0
    total_exact = 0
    total_exact_opening_tests = 0
    total_safe_far_accepts = 0

    for source in bodies:
        source_id = int(source.id)
        source_rows: list[dict[str, object]] = []
        near_node_ids = near_node_ids_by_source.get(source_id, set())
        fallback_seen: set[int] = set()
        visited_count = 0
        aggregate_count = 0
        exact_count = 0
        exact_opening_tests = 0
        safe_far_accepts = 0

        def emit_aggregate(node: rt.AggregateTreeNodeRow) -> None:
            nonlocal aggregate_count
            row = {
                "source_id": source_id,
                "frontier_kind": "aggregate",
                "frontier_kind_code": 1,
                "item_id": int(node.id),
                "aggregate_id": int(node.id),
                "target_id": None,
                "owner_aggregate_id": int(node.id),
                "dfs_index": int(node.dfs_index),
                "resume_index": node.resume_index,
                "metadata_flags": rt.AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE,
            }
            source_rows.append(row)
            accepted_rows.append(
                {
                    "source_id": source_id,
                    "aggregate_id": int(node.id),
                    "aggregate_mass": float(node.mass),
                    "aggregate_cx": float(node.cx),
                    "aggregate_cy": float(node.cy),
                    "dfs_index": int(node.dfs_index),
                    "resume_index": node.resume_index,
                }
            )
            aggregate_count += 1

        def emit_exact(node: rt.AggregateTreeNodeRow, target_id: int) -> None:
            nonlocal exact_count
            row = {
                "source_id": source_id,
                "frontier_kind": "exact",
                "frontier_kind_code": 2,
                "item_id": int(target_id),
                "aggregate_id": int(node.id),
                "target_id": int(target_id),
                "owner_aggregate_id": int(node.id),
                "dfs_index": int(node.dfs_index),
                "resume_index": node.resume_index,
                "metadata_flags": rt.AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE,
            }
            source_rows.append(row)
            fallback_rows.append(
                {
                    "source_id": source_id,
                    "target_id": int(target_id),
                    "aggregate_id": int(node.id),
                    "dfs_index": int(node.dfs_index),
                    "resume_index": node.resume_index,
                }
            )
            exact_count += 1

        def visit(node: rt.AggregateTreeNodeRow) -> None:
            nonlocal visited_count, exact_opening_tests, safe_far_accepts
            visited_count += 1
            contains_source = source_id in member_sets[int(node.id)]
            if not contains_source:
                if int(node.id) not in near_node_ids:
                    emit_aggregate(node)
                    safe_far_accepts += 1
                    return
                exact_opening_tests += 1
                dx = float(node.cx) - float(source.x)
                dy = float(node.cy) - float(source.y)
                distance = (dx * dx + dy * dy) ** 0.5
                opening_ratio = float("inf") if distance == 0.0 else (2.0 * float(node.half_size)) / distance
                if opening_ratio < theta:
                    emit_aggregate(node)
                    return
            if node.child_ids:
                for child_id in node.child_ids:
                    visit(node_by_id[int(child_id)])
                return
            for target_id in node.member_ids:
                target_id = int(target_id)
                if target_id == source_id or target_id in fallback_seen:
                    continue
                fallback_seen.add(target_id)
                emit_exact(node, target_id)

        for root_id in root_ids:
            visit(node_by_id[root_id])

        frontier_rows.extend(source_rows)
        row_offsets.append(len(frontier_rows))
        per_source[source_id] = {
            "frontier_offset": row_offsets[-2],
            "frontier_count": len(source_rows),
            "visited_node_count": visited_count,
            "accepted_aggregate_count": aggregate_count,
            "fallback_exact_count": exact_count,
            "near_zone_candidate_count": len(near_node_ids),
            "exact_opening_test_count": exact_opening_tests,
            "safe_far_accept_count": safe_far_accepts,
        }
        total_visited += visited_count
        total_aggregate += aggregate_count
        total_exact += exact_count
        total_exact_opening_tests += exact_opening_tests
        total_safe_far_accepts += safe_far_accepts

    frontier_i64_rows = tuple(
        (
            int(row["source_id"]),
            int(row["frontier_kind_code"]),
            int(row["item_id"]),
            int(row["owner_aggregate_id"]),
            int(row["dfs_index"]),
            -1 if row["resume_index"] is None else int(row["resume_index"]),
            int(row["metadata_flags"]),
        )
        for row in frontier_rows
    )
    return {
        "frontier_rows": tuple(frontier_rows),
        "frontier_i64_rows": frontier_i64_rows,
        "accepted_aggregate_rows": tuple(accepted_rows),
        "fallback_exact_rows": tuple(fallback_rows),
        "source_ids": source_ids,
        "row_offsets": tuple(row_offsets),
        "row_schema": rt.AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA,
        "per_source_summary": per_source,
        "summary": {
            "source_count": len(source_ids),
            "tree_node_count": len(tree_nodes),
            "root_count": len(root_ids),
            "leaf_node_count": sum(1 for node in tree_nodes if node.is_leaf),
            "frontier_row_count": len(frontier_rows),
            "accepted_aggregate_row_count": total_aggregate,
            "fallback_exact_row_count": total_exact,
            "visited_node_total": total_visited,
            "near_zone_candidate_row_count": int(membership["valid_count"]),
            "exact_opening_test_count": total_exact_opening_tests,
            "safe_far_accept_count": total_safe_far_accepts,
        },
        "membership_primitive": {
            "primitive": membership["primitive"],
            "contract": membership["contract"],
            "backend": membership["backend"],
            "row_schema": membership["row_schema"],
            "valid_count": int(membership["valid_count"]),
            "rt_core_accelerated": bool(membership["rt_core_accelerated"]),
            "native_engine_customization": bool(membership["native_engine_customization"]),
            "native_generic_symbol": membership["native_generic_symbol"],
            "run_phases": membership["run_phases"],
            "wrapper_elapsed_sec": membership_sec,
        },
        "metadata": {
            "contract": (
                f"{rt.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT}+"
                f"{rt.EXPANDED_AABB_POINT_MEMBERSHIP_2D_CONTRACT}"
            ),
            "theta": theta,
            "membership_backend": membership_backend,
            "near_zone_policy": "conservative_square_distance_rejection",
            "near_zone_radius": "2 * node.half_size / theta",
            "opening_math_location": "app_python_reference",
            "force_math_location": "app_or_partner_code",
            "native_engine_app_specific": False,
            "app_math_embedded_in_engine": False,
            "force_law_embedded_in_engine": False,
            "rt_assisted_frontier_collection": membership_backend == "optix",
            "public_speedup_claim_authorized": False,
        },
    }


def _aggregate_frontier_expanded_membership_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
    membership_backend: str,
    skip_validation: bool,
) -> dict[str, Any]:
    total_start = time.perf_counter()
    body_start = time.perf_counter()
    bodies = _make_bodies(body_count)
    body_generation_sec = time.perf_counter() - body_start
    tree_start = time.perf_counter()
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    tree_nodes = tuple(tree["nodes"])
    tree_build_sec = time.perf_counter() - tree_start
    lowering_start = time.perf_counter()
    lowered = _frontier_rows_via_expanded_membership(
        bodies,
        tree_nodes,
        theta=theta,
        membership_backend=membership_backend,
    )
    frontier_lowering_sec = time.perf_counter() - lowering_start
    force_start = time.perf_counter()
    force_rows, contributions, vector_sums = _force_rows_from_frontier(
        bodies,
        tree_nodes,
        lowered["accepted_aggregate_rows"],
        lowered["fallback_exact_rows"],
    )
    force_interpretation_sec = time.perf_counter() - force_start
    baseline_match: bool | None = None
    baseline_validation_sec = 0.0
    if not skip_validation:
        validation_start = time.perf_counter()
        baseline = rt.collect_aggregate_frontier_2d(
            bodies,
            tree_nodes,
            theta=theta,
        )
        baseline_match = baseline["frontier_i64_rows"] == lowered["frontier_i64_rows"]
        baseline_validation_sec = time.perf_counter() - validation_start
        if not baseline_match:
            raise AssertionError(
                "expanded-membership aggregate frontier lowering diverged from "
                "collect_aggregate_frontier_2d"
            )
    total_sec = time.perf_counter() - total_start
    row_sample, row_truncated = _truncate_rows(lowered["frontier_rows"])
    force_sample, force_truncated = _truncate_rows(force_rows)
    return {
        "app": "barnes_hut_force_app",
        "backend": membership_backend,
        "body_count": len(bodies),
        "theta": theta,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "run_phases": {
            "body_generation_sec": body_generation_sec,
            "tree_build_sec": tree_build_sec,
            "frontier_lowering_sec": frontier_lowering_sec,
            "membership_primitive_wrapper_sec": lowered["membership_primitive"]["wrapper_elapsed_sec"],
            "force_interpretation_sec": force_interpretation_sec,
            "baseline_validation_sec": baseline_validation_sec,
            "total_sec": total_sec,
        },
        "frontier_collection": {
            "frontier_rows": row_sample,
            "frontier_rows_truncated": row_truncated,
            "source_ids": lowered["source_ids"],
            "row_offsets": lowered["row_offsets"],
            "row_schema": lowered["row_schema"],
            "summary": lowered["summary"],
            "per_source_summary": lowered["per_source_summary"],
            "metadata": lowered["metadata"],
        },
        "membership_primitive": lowered["membership_primitive"],
        "force_summary": {
            "force_row_count": len(force_rows),
            "checksum_force_x": sum(float(row["force_x"]) for row in force_rows),
            "checksum_force_y": sum(float(row["force_y"]) for row in force_rows),
            "force_rows": force_sample,
            "force_rows_truncated": force_truncated,
            "contribution_summary": contributions["summary"],
            "vector_sum_summary": vector_sums["summary"],
        },
        "baseline_validation": {
            "skipped": skip_validation,
            "matches_collect_aggregate_frontier_2d": baseline_match,
        },
        "boundary": (
            "RT-assisted Barnes-Hut aggregate-frontier lowering: generic "
            "EXPANDED_AABB_POINT_MEMBERSHIP_2D discovers app-owned near-zone "
            "candidate rows, then Python app code applies theta/opening and "
            "force interpretation. The native engine only sees points, boxes, "
            "IDs, capacity, and rows."
        ),
    }


def _force_rows_from_frontier(
    bodies: tuple[app.Body, ...],
    tree_nodes: tuple[rt.AggregateTreeNodeRow, ...],
    accepted_rows: tuple[dict[str, object], ...],
    fallback_rows: tuple[dict[str, object], ...],
) -> tuple[tuple[dict[str, object], ...], dict[str, object], dict[str, object]]:
    contributions = rt.evaluate_weighted_inverse_square_contribution_rows_2d(
        bodies,
        bodies,
        accepted_aggregate_rows=accepted_rows,
        fallback_exact_rows=fallback_rows,
        aggregate_nodes=tree_nodes,
        softening=app.SOFTENING,
    )
    vector_sums = rt.sum_vector_contribution_rows_2d(
        contributions["contribution_rows"],
        source_ids=tuple(body.id for body in bodies),
    )
    vector_sum_by_source = {int(row["source_id"]): row for row in vector_sums["vector_sum_rows"]}
    accepted_by_source: dict[int, list[int]] = {body.id: [] for body in bodies}
    fallback_by_source: dict[int, list[int]] = {body.id: [] for body in bodies}
    for row in contributions["contribution_rows"]:
        source_id = int(row["source_id"])
        if row["contribution_kind"] == "aggregate":
            accepted_by_source[source_id].append(int(row["aggregate_id"]))
        else:
            fallback_by_source[source_id].append(int(row["target_id"]))
    return tuple(
        {
            "body_id": body.id,
            "force_x": float(vector_sum_by_source[body.id]["vector_x"]),
            "force_y": float(vector_sum_by_source[body.id]["vector_y"]),
            "accepted_node_ids": sorted(accepted_by_source[body.id]),
            "exact_body_ids": sorted(fallback_by_source[body.id]),
        }
        for body in bodies
    ), contributions, vector_sums


def _host_weighted_vector_sum_from_frontier_rows(
    bodies: tuple[app.Body, ...],
    tree_nodes: tuple[rt.AggregateTreeNodeRow, ...],
    frontier_rows: tuple[dict[str, object], ...],
    *,
    softening: float,
) -> tuple[tuple[dict[str, object], ...], dict[str, object]]:
    source_by_id = {int(body.id): body for body in bodies}
    target_by_id = dict(source_by_id)
    node_by_id = {int(node.id): node for node in tree_nodes}
    vector_x_by_id = {int(body.id): 0.0 for body in bodies}
    vector_y_by_id = {int(body.id): 0.0 for body in bodies}
    aggregate_count_by_id = {int(body.id): 0 for body in bodies}
    exact_count_by_id = {int(body.id): 0 for body in bodies}
    softening_sq = float(softening) * float(softening)
    aggregate_count = 0
    exact_count = 0

    for row in frontier_rows:
        source_id = int(row["source_id"])
        source = source_by_id[source_id]
        kind_code = int(row["frontier_kind_code"])
        if kind_code == 1:
            node = node_by_id[int(row["item_id"])]
            target_x = float(node.cx)
            target_y = float(node.cy)
            target_mass = float(node.mass)
            aggregate_count += 1
            aggregate_count_by_id[source_id] += 1
        elif kind_code == 2:
            target = target_by_id[int(row["item_id"])]
            target_x = float(target.x)
            target_y = float(target.y)
            target_mass = float(target.mass)
            exact_count += 1
            exact_count_by_id[source_id] += 1
        else:
            raise ValueError(f"unsupported aggregate-frontier kind code: {kind_code}")

        dx = target_x - float(source.x)
        dy = target_y - float(source.y)
        dist_sq = dx * dx + dy * dy + softening_sq
        if dist_sq == 0.0:
            continue
        inv_dist = 1.0 / (dist_sq ** 0.5)
        scale = float(source.mass) * target_mass * inv_dist * inv_dist * inv_dist
        vector_x_by_id[source_id] += dx * scale
        vector_y_by_id[source_id] += dy * scale

    force_rows = tuple(
        {
            "body_id": int(body.id),
            "force_x": float(vector_x_by_id[int(body.id)]),
            "force_y": float(vector_y_by_id[int(body.id)]),
            "contribution_count": int(aggregate_count_by_id[int(body.id)] + exact_count_by_id[int(body.id)]),
            "aggregate_contribution_count": int(aggregate_count_by_id[int(body.id)]),
            "exact_contribution_count": int(exact_count_by_id[int(body.id)]),
        }
        for body in bodies
    )
    return force_rows, {
        "frontier_row_count": len(frontier_rows),
        "aggregate_contribution_row_count": aggregate_count,
        "exact_contribution_row_count": exact_count,
        "source_count": len(bodies),
        "softening": float(softening),
        "contribution_rows_materialized_on_host": False,
        "streamed_host_accumulation": True,
    }


_HOST_NUMBA_CPU_FRONTIER_VECTOR_SUM_KERNEL = None


def _host_numba_cpu_frontier_vector_sum_kernel() -> object:
    global _HOST_NUMBA_CPU_FRONTIER_VECTOR_SUM_KERNEL
    if _HOST_NUMBA_CPU_FRONTIER_VECTOR_SUM_KERNEL is not None:
        return _HOST_NUMBA_CPU_FRONTIER_VECTOR_SUM_KERNEL

    try:
        from numba import njit, prange
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Numba CPU host baseline requires Numba") from exc

    @njit(parallel=True)
    def kernel(
        frontier_i64_rows,
        row_offsets,
        source_ids,
        source_x_by_id,
        source_y_by_id,
        source_mass_by_id,
        target_x_by_id,
        target_y_by_id,
        target_mass_by_id,
        node_cx_by_id,
        node_cy_by_id,
        node_mass_by_id,
        softening_sq,
        vector_x,
        vector_y,
        aggregate_counts,
        exact_counts,
    ):
        for source_index in prange(source_ids.shape[0]):
            source_id = source_ids[source_index]
            source_x = source_x_by_id[source_id]
            source_y = source_y_by_id[source_id]
            source_mass = source_mass_by_id[source_id]
            sum_x = 0.0
            sum_y = 0.0
            aggregate_count = 0
            exact_count = 0
            start = row_offsets[source_index]
            end = row_offsets[source_index + 1]
            for row_index in range(start, end):
                kind_code = frontier_i64_rows[row_index, 1]
                item_id = frontier_i64_rows[row_index, 2]
                if kind_code == 1:
                    target_x = node_cx_by_id[item_id]
                    target_y = node_cy_by_id[item_id]
                    target_mass = node_mass_by_id[item_id]
                    aggregate_count += 1
                elif kind_code == 2:
                    target_x = target_x_by_id[item_id]
                    target_y = target_y_by_id[item_id]
                    target_mass = target_mass_by_id[item_id]
                    exact_count += 1
                else:
                    continue

                dx = target_x - source_x
                dy = target_y - source_y
                dist_sq = dx * dx + dy * dy + softening_sq
                if dist_sq != 0.0:
                    inv_dist = 1.0 / (dist_sq ** 0.5)
                    scale = source_mass * target_mass * inv_dist * inv_dist * inv_dist
                    sum_x += dx * scale
                    sum_y += dy * scale
            vector_x[source_index] = sum_x
            vector_y[source_index] = sum_y
            aggregate_counts[source_index] = aggregate_count
            exact_counts[source_index] = exact_count

    _HOST_NUMBA_CPU_FRONTIER_VECTOR_SUM_KERNEL = kernel
    return kernel


def _host_numba_cpu_weighted_vector_sum_from_frontier_i64_rows(
    bodies: tuple[app.Body, ...],
    tree_nodes: tuple[rt.AggregateTreeNodeRow, ...],
    collection: dict[str, object],
    *,
    softening: float,
    query_repeat: int,
    warmup: int,
) -> tuple[tuple[dict[str, object], ...], dict[str, object]]:
    try:
        import numpy as np
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Numba CPU host baseline requires NumPy") from exc

    start_prepare = time.perf_counter()
    frontier_i64_rows = np.asarray(collection["frontier_i64_rows"], dtype=np.int64)
    if frontier_i64_rows.size == 0:
        frontier_i64_rows = np.empty((0, len(collection["row_schema"])), dtype=np.int64)
    row_offsets = np.asarray(collection["row_offsets"], dtype=np.int64)
    source_ids = np.asarray(collection["source_ids"], dtype=np.int64)
    if row_offsets.shape[0] != source_ids.shape[0] + 1:
        raise ValueError("row_offsets must have source_count + 1 entries")
    if frontier_i64_rows.ndim != 2 or frontier_i64_rows.shape[1] != len(collection["row_schema"]):
        raise ValueError("frontier_i64_rows has an unexpected shape")

    body_ids = [int(body.id) for body in bodies]
    node_ids = [int(node.id) for node in tree_nodes]
    if not body_ids or not node_ids:
        raise ValueError("Numba CPU host baseline requires non-empty body and node rows")
    if min(body_ids) < 0 or min(node_ids) < 0:
        raise ValueError("Numba CPU host baseline requires non-negative ids")

    max_body_id = max(body_ids)
    max_node_id = max(node_ids)
    source_x_by_id = np.zeros((max_body_id + 1,), dtype=np.float64)
    source_y_by_id = np.zeros((max_body_id + 1,), dtype=np.float64)
    source_mass_by_id = np.zeros((max_body_id + 1,), dtype=np.float64)
    target_x_by_id = np.zeros((max_body_id + 1,), dtype=np.float64)
    target_y_by_id = np.zeros((max_body_id + 1,), dtype=np.float64)
    target_mass_by_id = np.zeros((max_body_id + 1,), dtype=np.float64)
    for body in bodies:
        body_id = int(body.id)
        source_x_by_id[body_id] = float(body.x)
        source_y_by_id[body_id] = float(body.y)
        source_mass_by_id[body_id] = float(body.mass)
        target_x_by_id[body_id] = float(body.x)
        target_y_by_id[body_id] = float(body.y)
        target_mass_by_id[body_id] = float(body.mass)

    node_cx_by_id = np.zeros((max_node_id + 1,), dtype=np.float64)
    node_cy_by_id = np.zeros((max_node_id + 1,), dtype=np.float64)
    node_mass_by_id = np.zeros((max_node_id + 1,), dtype=np.float64)
    for node in tree_nodes:
        node_id = int(node.id)
        node_cx_by_id[node_id] = float(node.cx)
        node_cy_by_id[node_id] = float(node.cy)
        node_mass_by_id[node_id] = float(node.mass)

    vector_x = np.empty((source_ids.shape[0],), dtype=np.float64)
    vector_y = np.empty((source_ids.shape[0],), dtype=np.float64)
    aggregate_counts = np.empty((source_ids.shape[0],), dtype=np.int64)
    exact_counts = np.empty((source_ids.shape[0],), dtype=np.int64)
    kernel = _host_numba_cpu_frontier_vector_sum_kernel()
    prepare_seconds = time.perf_counter() - start_prepare

    softening_sq = float(softening) * float(softening)
    warmup_count = max(0, int(warmup))
    repeat_count = max(1, int(query_repeat))
    for _ in range(warmup_count):
        kernel(
            frontier_i64_rows,
            row_offsets,
            source_ids,
            source_x_by_id,
            source_y_by_id,
            source_mass_by_id,
            target_x_by_id,
            target_y_by_id,
            target_mass_by_id,
            node_cx_by_id,
            node_cy_by_id,
            node_mass_by_id,
            softening_sq,
            vector_x,
            vector_y,
            aggregate_counts,
            exact_counts,
        )

    repeat_seconds: list[float] = []
    for _ in range(repeat_count):
        start_run = time.perf_counter()
        kernel(
            frontier_i64_rows,
            row_offsets,
            source_ids,
            source_x_by_id,
            source_y_by_id,
            source_mass_by_id,
            target_x_by_id,
            target_y_by_id,
            target_mass_by_id,
            node_cx_by_id,
            node_cy_by_id,
            node_mass_by_id,
            softening_sq,
            vector_x,
            vector_y,
            aggregate_counts,
            exact_counts,
        )
        repeat_seconds.append(time.perf_counter() - start_run)

    run_median_seconds = statistics.median(repeat_seconds)
    force_rows = tuple(
        {
            "body_id": int(source_ids[index]),
            "force_x": float(vector_x[index]),
            "force_y": float(vector_y[index]),
            "contribution_count": int(aggregate_counts[index] + exact_counts[index]),
            "aggregate_contribution_count": int(aggregate_counts[index]),
            "exact_contribution_count": int(exact_counts[index]),
        }
        for index in range(source_ids.shape[0])
    )
    return force_rows, {
        "frontier_row_count": int(frontier_i64_rows.shape[0]),
        "aggregate_contribution_row_count": int(aggregate_counts.sum()),
        "exact_contribution_row_count": int(exact_counts.sum()),
        "source_count": int(source_ids.shape[0]),
        "softening": float(softening),
        "prepare_seconds": prepare_seconds,
        "repeat_seconds": tuple(float(value) for value in repeat_seconds),
        "run_median_seconds": float(run_median_seconds),
        "warmup": warmup_count,
        "repeat": repeat_count,
        "contribution_rows_materialized_on_host": False,
        "frontier_i64_rows_materialized_on_host": True,
        "streamed_host_accumulation": True,
        "numba_cpu_njit_used": True,
        "parallel_by_source_offsets": True,
        "raw_c_or_cuda_kernel_required": False,
    }


def _aggregate_frontier_weighted_vector_host_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
    backend: str,
    skip_validation: bool,
    force_output_mode: str,
    frontier_row_capacity: int | None,
    frontier_capacity_multiplier: int,
) -> dict[str, Any]:
    if backend not in {"cpu", "embree"}:
        raise ValueError("host aggregate-frontier baseline backend must be cpu or embree")
    if frontier_row_capacity is not None and frontier_row_capacity <= 0:
        raise ValueError("frontier_row_capacity must be positive when provided")
    if frontier_capacity_multiplier <= 0:
        raise ValueError("frontier_capacity_multiplier must be positive")

    total_start = time.perf_counter()
    body_start = time.perf_counter()
    bodies = _make_bodies(body_count)
    body_generation_sec = time.perf_counter() - body_start

    tree_start = time.perf_counter()
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    tree_nodes = tuple(tree["nodes"])
    tree_build_sec = time.perf_counter() - tree_start

    row_capacity = (
        int(frontier_row_capacity)
        if frontier_row_capacity is not None
        else max(1024, len(bodies) * int(frontier_capacity_multiplier))
    )
    collect_start = time.perf_counter()
    if backend == "embree":
        collected = rt.collect_aggregate_frontier_2d_embree(
            bodies,
            tree_nodes,
            theta=theta,
            max_total_rows=row_capacity,
        )
    else:
        collected = rt.collect_aggregate_frontier_2d(
            bodies,
            tree_nodes,
            theta=theta,
            max_total_rows=row_capacity,
        )
    frontier_collect_sec = time.perf_counter() - collect_start

    vector_start = time.perf_counter()
    force_rows, vector_summary = _host_weighted_vector_sum_from_frontier_rows(
        bodies,
        tree_nodes,
        tuple(collected["frontier_rows"]),
        softening=app.SOFTENING,
    )
    vector_sum_sec = time.perf_counter() - vector_start
    total_sec = time.perf_counter() - total_start
    force_sample, force_truncated = _truncate_rows(force_rows)

    validation: dict[str, object]
    if skip_validation or len(bodies) > 2048:
        validation = {
            "skipped": True,
            "reason": "user_skip_validation" if skip_validation else "body_count_above_2048",
        }
    else:
        reference = rt.sum_aggregate_frontier_weighted_vectors_2d(
            bodies,
            bodies,
            tree_nodes,
            theta=theta,
            softening=app.SOFTENING,
        )
        expected_by_id = {
            int(row["source_id"]): (float(row["vector_x"]), float(row["vector_y"]))
            for row in reference["vector_sum_rows"]
        }
        max_abs_diff_x = max(
            abs(float(row["force_x"]) - expected_by_id[int(row["body_id"])][0])
            for row in force_rows
        )
        max_abs_diff_y = max(
            abs(float(row["force_y"]) - expected_by_id[int(row["body_id"])][1])
            for row in force_rows
        )
        validation = {
            "skipped": False,
            "compared_against": "sum_aggregate_frontier_weighted_vectors_2d_cpu_reference",
            "tolerance": 1.0e-7,
            "max_abs_diff_x": max_abs_diff_x,
            "max_abs_diff_y": max_abs_diff_y,
            "passed": max_abs_diff_x <= 1.0e-7 and max_abs_diff_y <= 1.0e-7,
            "reference_frontier_row_count": int(reference["summary"]["contribution_row_count"]),
        }
        if not bool(validation["passed"]):
            raise AssertionError("host aggregate-frontier weighted-vector baseline failed validation")

    return {
        "app": "barnes_hut_force_app",
        "backend": f"{backend}+host_python_vector_sum",
        "mode": f"aggregate_frontier_weighted_vector_{backend}_host",
        "body_count": len(bodies),
        "theta": theta,
        "softening": app.SOFTENING,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "row_capacity": row_capacity,
        "run_phases": {
            "body_generation_sec": body_generation_sec,
            "tree_build_sec": tree_build_sec,
            "frontier_collect_sec": frontier_collect_sec,
            "vector_sum_sec": vector_sum_sec,
            "total_sec": total_sec,
        },
        "frontier_collection": {
            "contract": collected["metadata"]["contract"],
            "backend": backend,
            "native_symbol": collected["metadata"].get("native_symbol"),
            "frontier_row_count": int(collected["summary"]["frontier_row_count"]),
            "accepted_aggregate_row_count": int(collected["summary"]["accepted_aggregate_row_count"]),
            "fallback_exact_row_count": int(collected["summary"]["fallback_exact_row_count"]),
            "frontier_rows_materialized_on_host": True,
        },
        "vector_sum_summary": {
            **vector_summary,
            "contract": "generic_aggregate_frontier_collect_2d_host_weighted_vector_sum_baseline",
            "force_rows": force_sample if force_output_mode == "full" else [],
            "force_rows_truncated": force_truncated if force_output_mode == "full" else True,
            "force_output_mode": force_output_mode,
            "checksum_force_x": sum(float(row["force_x"]) for row in force_rows),
            "checksum_force_y": sum(float(row["force_y"]) for row in force_rows),
        },
        "validation": validation,
        "claim_flags": {
            "same_logical_frontier_contract": True,
            "same_device_resident_contract": False,
            "frontier_rows_materialized_on_host": True,
            "contribution_rows_materialized_on_host": False,
            "native_engine_app_specific": False,
            "automatic_partner_selection_allowed": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
        "boundary": (
            f"Host baseline for {backend} aggregate-frontier collection plus "
            "streamed Python weighted-vector accumulation. It shares the logical "
            "frontier/vector output contract with the prepared OptiX app mode, "
            "but it intentionally materializes frontier rows on host and is not "
            "the same device-resident handoff contract."
        ),
    }


def _aggregate_frontier_weighted_vector_host_numba_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
    backend: str,
    skip_validation: bool,
    force_output_mode: str,
    frontier_row_capacity: int | None,
    frontier_capacity_multiplier: int,
    query_repeat: int,
    warmup: int,
) -> dict[str, Any]:
    if backend not in {"cpu", "embree"}:
        raise ValueError("host+Numba aggregate-frontier baseline backend must be cpu or embree")
    if frontier_row_capacity is not None and frontier_row_capacity <= 0:
        raise ValueError("frontier_row_capacity must be positive when provided")
    if frontier_capacity_multiplier <= 0:
        raise ValueError("frontier_capacity_multiplier must be positive")

    total_start = time.perf_counter()
    body_start = time.perf_counter()
    bodies = _make_bodies(body_count)
    body_generation_sec = time.perf_counter() - body_start

    tree_start = time.perf_counter()
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    tree_nodes = tuple(tree["nodes"])
    tree_build_sec = time.perf_counter() - tree_start

    row_capacity = (
        int(frontier_row_capacity)
        if frontier_row_capacity is not None
        else max(1024, len(bodies) * int(frontier_capacity_multiplier))
    )
    collect_start = time.perf_counter()
    if backend == "embree":
        collected = rt.collect_aggregate_frontier_2d_embree(
            bodies,
            tree_nodes,
            theta=theta,
            max_total_rows=row_capacity,
        )
    else:
        collected = rt.collect_aggregate_frontier_2d(
            bodies,
            tree_nodes,
            theta=theta,
            max_total_rows=row_capacity,
        )
    frontier_collect_sec = time.perf_counter() - collect_start

    vector_start = time.perf_counter()
    force_rows, vector_summary = _host_numba_cpu_weighted_vector_sum_from_frontier_i64_rows(
        bodies,
        tree_nodes,
        collected,
        softening=app.SOFTENING,
        query_repeat=query_repeat,
        warmup=warmup,
    )
    vector_total_sec = time.perf_counter() - vector_start
    total_sec = time.perf_counter() - total_start
    force_sample, force_truncated = _truncate_rows(force_rows)

    validation: dict[str, object]
    if skip_validation or len(bodies) > 2048:
        validation = {
            "skipped": True,
            "reason": "user_skip_validation" if skip_validation else "body_count_above_2048",
        }
    else:
        reference = rt.sum_aggregate_frontier_weighted_vectors_2d(
            bodies,
            bodies,
            tree_nodes,
            theta=theta,
            softening=app.SOFTENING,
        )
        expected_by_id = {
            int(row["source_id"]): (float(row["vector_x"]), float(row["vector_y"]))
            for row in reference["vector_sum_rows"]
        }
        max_abs_diff_x = max(
            abs(float(row["force_x"]) - expected_by_id[int(row["body_id"])][0])
            for row in force_rows
        )
        max_abs_diff_y = max(
            abs(float(row["force_y"]) - expected_by_id[int(row["body_id"])][1])
            for row in force_rows
        )
        validation = {
            "skipped": False,
            "compared_against": "sum_aggregate_frontier_weighted_vectors_2d_cpu_reference",
            "tolerance": 1.0e-7,
            "max_abs_diff_x": max_abs_diff_x,
            "max_abs_diff_y": max_abs_diff_y,
            "passed": max_abs_diff_x <= 1.0e-7 and max_abs_diff_y <= 1.0e-7,
            "reference_frontier_row_count": int(reference["summary"]["contribution_row_count"]),
        }
        if not bool(validation["passed"]):
            raise AssertionError("host+Numba aggregate-frontier weighted-vector baseline failed validation")

    vector_run_median_sec = float(vector_summary["run_median_seconds"])
    return {
        "app": "barnes_hut_force_app",
        "backend": f"{backend}+host_numba_cpu_vector_sum",
        "mode": f"aggregate_frontier_weighted_vector_{backend}_host_numba",
        "body_count": len(bodies),
        "theta": theta,
        "softening": app.SOFTENING,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "row_capacity": row_capacity,
        "run_phases": {
            "body_generation_sec": body_generation_sec,
            "tree_build_sec": tree_build_sec,
            "frontier_collect_sec": frontier_collect_sec,
            "vector_prepare_sec": float(vector_summary["prepare_seconds"]),
            "vector_run_median_sec": vector_run_median_sec,
            "vector_total_wall_sec": vector_total_sec,
            "total_sec": total_sec,
        },
        "medians": {
            "frontier_collect_seconds": frontier_collect_sec,
            "numba_cpu_vector_seconds": vector_run_median_sec,
            "frontier_collect_plus_numba_cpu_vector_seconds": frontier_collect_sec + vector_run_median_sec,
        },
        "frontier_collection": {
            "contract": collected["metadata"]["contract"],
            "backend": backend,
            "native_symbol": collected["metadata"].get("native_symbol"),
            "frontier_row_count": int(collected["summary"]["frontier_row_count"]),
            "accepted_aggregate_row_count": int(collected["summary"]["accepted_aggregate_row_count"]),
            "fallback_exact_row_count": int(collected["summary"]["fallback_exact_row_count"]),
            "frontier_rows_materialized_on_host": True,
            "frontier_i64_rows_materialized_on_host": True,
        },
        "vector_sum_summary": {
            **vector_summary,
            "contract": "generic_aggregate_frontier_collect_2d_host_numba_cpu_weighted_vector_sum_baseline",
            "force_rows": force_sample if force_output_mode == "full" else [],
            "force_rows_truncated": force_truncated if force_output_mode == "full" else True,
            "force_output_mode": force_output_mode,
            "checksum_force_x": sum(float(row["force_x"]) for row in force_rows),
            "checksum_force_y": sum(float(row["force_y"]) for row in force_rows),
        },
        "validation": validation,
        "claim_flags": {
            "same_logical_frontier_contract": True,
            "same_device_resident_contract": False,
            "frontier_rows_materialized_on_host": True,
            "frontier_i64_rows_materialized_on_host": True,
            "contribution_rows_materialized_on_host": False,
            "python_vector_sum_used": False,
            "numba_cpu_njit_used": True,
            "raw_c_or_cuda_kernel_required": False,
            "native_engine_app_specific": False,
            "automatic_partner_selection_allowed": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
        "boundary": (
            f"Host-materialized baseline for {backend} aggregate-frontier collection plus "
            "Numba CPU weighted-vector accumulation over row_offsets. It improves the "
            "CPU-side continuation without C++ or CUDA source, but it still materializes "
            "frontier rows on host and is not the same device-resident handoff contract "
            "as the prepared OptiX app route."
        ),
    }


def _force_contributions_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
) -> dict[str, Any]:
    bodies = _make_bodies(body_count)
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    opening = rt.evaluate_aggregate_tree_opening_frontier_2d(
        bodies,
        tree["nodes"],
        theta=theta,
    )
    contributions = rt.evaluate_weighted_inverse_square_contribution_rows_2d(
        bodies,
        bodies,
        accepted_aggregate_rows=opening["accepted_aggregate_rows"],
        fallback_exact_rows=opening["fallback_exact_rows"],
        aggregate_nodes=tree["nodes"],
        softening=app.SOFTENING,
    )
    contribution_sample, contribution_truncated = _truncate_rows(contributions["contribution_rows"])
    return {
        "app": "barnes_hut_force_app",
        "backend": "cpu_python_reference",
        "body_count": len(bodies),
        "theta": theta,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "opening_summary": opening["summary"],
        "force_contributions": {
            "contribution_rows": contribution_sample,
            "contribution_rows_truncated": contribution_truncated,
            "per_source_summary": contributions["per_source_summary"],
            "summary": contributions["summary"],
            "metadata": contributions["metadata"],
        },
        "boundary": (
            "Generic weighted inverse-square vector contributions only. This "
            "still materializes rows in Python and is not native force "
            "accumulation or paper-code timing."
        ),
    }


def _bucketized_force_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
) -> dict[str, Any]:
    bodies = _make_bodies(body_count)
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    tree_nodes = tuple(tree["nodes"])
    opening = rt.evaluate_aggregate_tree_opening_frontier_2d(
        bodies,
        tree_nodes,
        theta=theta,
    )
    force_rows, contributions, vector_sums = _force_rows_from_frontier(
        bodies,
        tree_nodes,
        opening["accepted_aggregate_rows"],
        opening["fallback_exact_rows"],
    )
    exact_forces = app.brute_force_forces(bodies) if len(bodies) <= 2048 else None
    error_rows = app._force_error_rows(force_rows, exact_forces) if exact_forces is not None else ()
    force_sample, force_truncated = _truncate_rows(force_rows)
    payload: dict[str, Any] = {
        "app": "barnes_hut_force_app",
        "backend": "cpu_python_reference",
        "body_count": len(bodies),
        "theta": theta,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "opening_summary": opening["summary"],
        "contribution_summary": contributions["summary"],
        "vector_sum_summary": vector_sums["summary"],
        "contribution_contract": contributions["metadata"]["contract"],
        "vector_sum_contract": vector_sums["metadata"]["contract"],
        "force_row_count": len(force_rows),
        "checksum_force_x": sum(float(row["force_x"]) for row in force_rows),
        "checksum_force_y": sum(float(row["force_y"]) for row in force_rows),
        "force_rows": force_sample,
        "force_rows_truncated": force_truncated,
        "validation_skipped": exact_forces is None,
        "boundary": (
            "Python-level Barnes-Hut force interpretation over generic RTDL "
            "tree/frontier/contribution/vector-sum rows. User/app Python owns "
            "dataset policy and theta choice; RTDL owns only app-agnostic "
            "aggregate and vector contracts here."
        ),
    }
    if exact_forces is not None:
        payload["max_relative_error"] = max((row["relative_error"] for row in error_rows), default=0.0)
        payload["mean_relative_error"] = (
            sum(row["relative_error"] for row in error_rows) / len(error_rows)
            if error_rows
            else 0.0
        )
    return payload


def _streamed_force_sum_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
) -> dict[str, Any]:
    bodies = _make_bodies(body_count)
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    opening = rt.evaluate_aggregate_tree_opening_frontier_2d(
        bodies,
        tree["nodes"],
        theta=theta,
    )
    vector_sums = rt.sum_weighted_inverse_square_contributions_2d(
        bodies,
        bodies,
        accepted_aggregate_rows=opening["accepted_aggregate_rows"],
        fallback_exact_rows=opening["fallback_exact_rows"],
        aggregate_nodes=tree["nodes"],
        softening=app.SOFTENING,
    )
    force_rows = tuple(
        {
            "body_id": int(row["source_id"]),
            "force_x": float(row["vector_x"]),
            "force_y": float(row["vector_y"]),
            "contribution_count": int(row["contribution_count"]),
            "aggregate_contribution_count": int(row["aggregate_contribution_count"]),
            "exact_contribution_count": int(row["exact_contribution_count"]),
        }
        for row in vector_sums["vector_sum_rows"]
    )
    exact_forces = app.brute_force_forces(bodies) if len(bodies) <= 2048 else None
    error_rows = app._force_error_rows(force_rows, exact_forces) if exact_forces is not None else ()
    force_sample, force_truncated = _truncate_rows(force_rows)
    payload: dict[str, Any] = {
        "app": "barnes_hut_force_app",
        "backend": "cpu_python_reference",
        "body_count": len(bodies),
        "theta": theta,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "opening_summary": opening["summary"],
        "vector_sum_summary": vector_sums["summary"],
        "vector_sum_contract": vector_sums["metadata"]["contract"],
        "force_row_count": len(force_rows),
        "checksum_force_x": sum(float(row["force_x"]) for row in force_rows),
        "checksum_force_y": sum(float(row["force_y"]) for row in force_rows),
        "force_rows": force_sample,
        "force_rows_truncated": force_truncated,
        "validation_skipped": exact_forces is None,
        "boundary": (
            "Generic streamed weighted inverse-square vector sum over "
            "bucketized tree/frontier rows. This avoids contribution-row "
            "materialization locally, but the opening frontier is still a "
            "Python reference and this is not native or paper-code timing."
        ),
    }
    if exact_forces is not None:
        payload["max_relative_error"] = max((row["relative_error"] for row in error_rows), default=0.0)
        payload["mean_relative_error"] = (
            sum(row["relative_error"] for row in error_rows) / len(error_rows)
            if error_rows
            else 0.0
        )
    return payload


def _materialization_pressure_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
) -> dict[str, Any]:
    bodies = _make_bodies(body_count)
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    opening = rt.evaluate_aggregate_tree_opening_frontier_2d(
        bodies,
        tree["nodes"],
        theta=theta,
    )
    pressure = rt.estimate_vector_sum_materialization_pressure_2d(
        accepted_aggregate_row_count=opening["summary"]["accepted_aggregate_row_count"],
        fallback_exact_row_count=opening["summary"]["fallback_exact_row_count"],
        source_count=opening["summary"]["source_count"],
    )
    return {
        "app": "barnes_hut_force_app",
        "backend": "cpu_python_reference",
        "body_count": len(bodies),
        "theta": theta,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "opening_summary": opening["summary"],
        "materialization_pressure": pressure,
        "boundary": (
            "Generic materialization-pressure estimate only. It is a local "
            "planning guard for choosing materialized reference, streamed "
            "reference, or native/partner fused execution."
        ),
    }


_HOST_NUMBA_CPU_FUSED_FRONTIER_VECTOR_SUM_KERNEL = None


def _host_numba_cpu_fused_frontier_vector_sum_kernel() -> object:
    global _HOST_NUMBA_CPU_FUSED_FRONTIER_VECTOR_SUM_KERNEL
    if _HOST_NUMBA_CPU_FUSED_FRONTIER_VECTOR_SUM_KERNEL is not None:
        return _HOST_NUMBA_CPU_FUSED_FRONTIER_VECTOR_SUM_KERNEL

    try:
        from numba import njit, prange
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("fused Numba CPU frontier baseline requires Numba") from exc

    @njit(parallel=True)
    def kernel(
        source_ids,
        source_x_by_id,
        source_y_by_id,
        source_mass_by_id,
        target_x_by_id,
        target_y_by_id,
        target_mass_by_id,
        source_leaf_dfs_by_id,
        root_ordinals,
        node_cx,
        node_cy,
        node_half_size,
        node_mass,
        node_dfs_index,
        node_subtree_end,
        child_offsets,
        child_ordinals,
        member_offsets,
        member_ids,
        theta,
        softening_sq,
        stack_workspace,
        vector_x,
        vector_y,
        aggregate_counts,
        exact_counts,
        visited_counts,
    ):
        for source_index in prange(source_ids.shape[0]):
            source_id = source_ids[source_index]
            source_x = source_x_by_id[source_id]
            source_y = source_y_by_id[source_id]
            source_mass = source_mass_by_id[source_id]
            source_leaf_dfs = source_leaf_dfs_by_id[source_id]
            stack_size = 0
            for root_index in range(root_ordinals.shape[0] - 1, -1, -1):
                stack_workspace[source_index, stack_size] = root_ordinals[root_index]
                stack_size += 1

            sum_x = 0.0
            sum_y = 0.0
            aggregate_count = 0
            exact_count = 0
            visited_count = 0

            while stack_size > 0:
                stack_size -= 1
                node_ordinal = stack_workspace[source_index, stack_size]
                visited_count += 1
                dx_node = node_cx[node_ordinal] - source_x
                dy_node = node_cy[node_ordinal] - source_y
                distance = (dx_node * dx_node + dy_node * dy_node) ** 0.5
                if distance == 0.0:
                    opening_ratio = 1.0e308
                else:
                    opening_ratio = (2.0 * node_half_size[node_ordinal]) / distance
                contains_source = (
                    source_leaf_dfs >= 0
                    and node_dfs_index[node_ordinal] <= source_leaf_dfs
                    and source_leaf_dfs < node_subtree_end[node_ordinal]
                )

                if (not contains_source) and opening_ratio < theta:
                    dist_sq = dx_node * dx_node + dy_node * dy_node + softening_sq
                    if dist_sq != 0.0:
                        inv_dist = 1.0 / (dist_sq ** 0.5)
                        scale = source_mass * node_mass[node_ordinal] * inv_dist * inv_dist * inv_dist
                        sum_x += dx_node * scale
                        sum_y += dy_node * scale
                    aggregate_count += 1
                    continue

                child_start = child_offsets[node_ordinal]
                child_end = child_offsets[node_ordinal + 1]
                if child_end > child_start:
                    for child_index in range(child_end - 1, child_start - 1, -1):
                        stack_workspace[source_index, stack_size] = child_ordinals[child_index]
                        stack_size += 1
                    continue

                member_start = member_offsets[node_ordinal]
                member_end = member_offsets[node_ordinal + 1]
                for member_index in range(member_start, member_end):
                    target_id = member_ids[member_index]
                    if target_id == source_id:
                        continue
                    dx = target_x_by_id[target_id] - source_x
                    dy = target_y_by_id[target_id] - source_y
                    dist_sq = dx * dx + dy * dy + softening_sq
                    if dist_sq != 0.0:
                        inv_dist = 1.0 / (dist_sq ** 0.5)
                        scale = source_mass * target_mass_by_id[target_id] * inv_dist * inv_dist * inv_dist
                        sum_x += dx * scale
                        sum_y += dy * scale
                    exact_count += 1

            vector_x[source_index] = sum_x
            vector_y[source_index] = sum_y
            aggregate_counts[source_index] = aggregate_count
            exact_counts[source_index] = exact_count
            visited_counts[source_index] = visited_count

    _HOST_NUMBA_CPU_FUSED_FRONTIER_VECTOR_SUM_KERNEL = kernel
    return kernel


def _fused_frontier_force_sum_numba_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
    skip_validation: bool,
    query_repeat: int,
    warmup: int,
    force_output_mode: str,
) -> dict[str, Any]:
    try:
        import numpy as np
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("fused Numba CPU frontier baseline requires NumPy") from exc

    total_start = time.perf_counter()
    body_start = time.perf_counter()
    bodies = _make_bodies(body_count)
    body_generation_sec = time.perf_counter() - body_start

    tree_start = time.perf_counter()
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    tree_nodes = tuple(tree["nodes"])
    tree_build_sec = time.perf_counter() - tree_start

    prepare_start = time.perf_counter()
    body_ids = [int(body.id) for body in bodies]
    node_ids = [int(node.id) for node in tree_nodes]
    if not body_ids or not node_ids:
        raise ValueError("fused Numba CPU frontier baseline requires non-empty bodies and tree nodes")
    if min(body_ids) < 0 or min(node_ids) < 0:
        raise ValueError("fused Numba CPU frontier baseline requires non-negative ids")
    max_body_id = max(body_ids)
    max_node_id = max(node_ids)

    source_ids = np.asarray(body_ids, dtype=np.int64)
    source_x_by_id = np.zeros((max_body_id + 1,), dtype=np.float64)
    source_y_by_id = np.zeros((max_body_id + 1,), dtype=np.float64)
    source_mass_by_id = np.zeros((max_body_id + 1,), dtype=np.float64)
    target_x_by_id = np.zeros((max_body_id + 1,), dtype=np.float64)
    target_y_by_id = np.zeros((max_body_id + 1,), dtype=np.float64)
    target_mass_by_id = np.zeros((max_body_id + 1,), dtype=np.float64)
    for body in bodies:
        body_id = int(body.id)
        source_x_by_id[body_id] = float(body.x)
        source_y_by_id[body_id] = float(body.y)
        source_mass_by_id[body_id] = float(body.mass)
        target_x_by_id[body_id] = float(body.x)
        target_y_by_id[body_id] = float(body.y)
        target_mass_by_id[body_id] = float(body.mass)

    node_ordinal_by_id = np.full((max_node_id + 1,), -1, dtype=np.int64)
    for ordinal, node in enumerate(tree_nodes):
        node_ordinal_by_id[int(node.id)] = ordinal

    node_count = len(tree_nodes)
    node_cx = np.empty((node_count,), dtype=np.float64)
    node_cy = np.empty((node_count,), dtype=np.float64)
    node_half_size = np.empty((node_count,), dtype=np.float64)
    node_mass = np.empty((node_count,), dtype=np.float64)
    node_dfs_index = np.empty((node_count,), dtype=np.int64)
    node_subtree_end = np.empty((node_count,), dtype=np.int64)
    source_leaf_dfs_by_id = np.full((max_body_id + 1,), -1, dtype=np.int64)
    child_lengths = []
    member_lengths = []
    child_id_set: set[int] = set()
    for ordinal, node in enumerate(tree_nodes):
        node_cx[ordinal] = float(node.cx)
        node_cy[ordinal] = float(node.cy)
        node_half_size[ordinal] = float(node.half_size)
        node_mass[ordinal] = float(node.mass)
        node_dfs_index[ordinal] = int(node.dfs_index)
        node_subtree_end[ordinal] = int(node.resume_index) if node.resume_index is not None else node_count
        child_lengths.append(len(node.child_ids))
        member_lengths.append(len(node.member_ids))
        for child_id in node.child_ids:
            child_id_set.add(int(child_id))
        if bool(node.is_leaf):
            for member_id in node.member_ids:
                if 0 <= int(member_id) <= max_body_id and source_leaf_dfs_by_id[int(member_id)] < 0:
                    source_leaf_dfs_by_id[int(member_id)] = int(node.dfs_index)

    root_ordinals = np.asarray(
        [ordinal for ordinal, node in enumerate(tree_nodes) if int(node.id) not in child_id_set],
        dtype=np.int64,
    )
    child_offsets = np.zeros((node_count + 1,), dtype=np.int64)
    member_offsets = np.zeros((node_count + 1,), dtype=np.int64)
    for index in range(node_count):
        child_offsets[index + 1] = child_offsets[index] + child_lengths[index]
        member_offsets[index + 1] = member_offsets[index] + member_lengths[index]
    child_ordinals = np.empty((int(child_offsets[-1]),), dtype=np.int64)
    member_ids = np.empty((int(member_offsets[-1]),), dtype=np.int64)
    child_cursor = 0
    member_cursor = 0
    for node in tree_nodes:
        for child_id in node.child_ids:
            child_ordinal = int(node_ordinal_by_id[int(child_id)])
            if child_ordinal < 0:
                raise ValueError(f"child node id {child_id} is not present")
            child_ordinals[child_cursor] = child_ordinal
            child_cursor += 1
        for member_id in node.member_ids:
            member_ids[member_cursor] = int(member_id)
            member_cursor += 1

    stack_workspace = np.empty((len(bodies), max(1, node_count)), dtype=np.int64)
    vector_x = np.empty((len(bodies),), dtype=np.float64)
    vector_y = np.empty((len(bodies),), dtype=np.float64)
    aggregate_counts = np.empty((len(bodies),), dtype=np.int64)
    exact_counts = np.empty((len(bodies),), dtype=np.int64)
    visited_counts = np.empty((len(bodies),), dtype=np.int64)
    kernel = _host_numba_cpu_fused_frontier_vector_sum_kernel()
    vector_prepare_sec = time.perf_counter() - prepare_start

    softening_sq = app.SOFTENING * app.SOFTENING
    warmup_count = max(0, int(warmup))
    repeat_count = max(1, int(query_repeat))
    for _ in range(warmup_count):
        kernel(
            source_ids,
            source_x_by_id,
            source_y_by_id,
            source_mass_by_id,
            target_x_by_id,
            target_y_by_id,
            target_mass_by_id,
            source_leaf_dfs_by_id,
            root_ordinals,
            node_cx,
            node_cy,
            node_half_size,
            node_mass,
            node_dfs_index,
            node_subtree_end,
            child_offsets,
            child_ordinals,
            member_offsets,
            member_ids,
            float(theta),
            softening_sq,
            stack_workspace,
            vector_x,
            vector_y,
            aggregate_counts,
            exact_counts,
            visited_counts,
        )

    repeat_seconds: list[float] = []
    for _ in range(repeat_count):
        run_start = time.perf_counter()
        kernel(
            source_ids,
            source_x_by_id,
            source_y_by_id,
            source_mass_by_id,
            target_x_by_id,
            target_y_by_id,
            target_mass_by_id,
            source_leaf_dfs_by_id,
            root_ordinals,
            node_cx,
            node_cy,
            node_half_size,
            node_mass,
            node_dfs_index,
            node_subtree_end,
            child_offsets,
            child_ordinals,
            member_offsets,
            member_ids,
            float(theta),
            softening_sq,
            stack_workspace,
            vector_x,
            vector_y,
            aggregate_counts,
            exact_counts,
            visited_counts,
        )
        repeat_seconds.append(time.perf_counter() - run_start)

    vector_run_median_sec = float(statistics.median(repeat_seconds))
    force_rows = tuple(
        {
            "body_id": int(source_ids[index]),
            "force_x": float(vector_x[index]),
            "force_y": float(vector_y[index]),
            "contribution_count": int(aggregate_counts[index] + exact_counts[index]),
            "aggregate_contribution_count": int(aggregate_counts[index]),
            "exact_contribution_count": int(exact_counts[index]),
            "visited_node_count": int(visited_counts[index]),
        }
        for index in range(len(bodies))
    )
    total_sec = time.perf_counter() - total_start
    force_sample, force_truncated = _truncate_rows(force_rows)

    validation: dict[str, object]
    if skip_validation or len(bodies) > 2048:
        validation = {
            "skipped": True,
            "reason": "user_skip_validation" if skip_validation else "body_count_above_2048",
        }
    else:
        reference = rt.sum_aggregate_frontier_weighted_vectors_2d(
            bodies,
            bodies,
            tree_nodes,
            theta=theta,
            softening=app.SOFTENING,
        )
        expected_by_id = {
            int(row["source_id"]): (float(row["vector_x"]), float(row["vector_y"]))
            for row in reference["vector_sum_rows"]
        }
        max_abs_diff_x = max(
            abs(float(row["force_x"]) - expected_by_id[int(row["body_id"])][0])
            for row in force_rows
        )
        max_abs_diff_y = max(
            abs(float(row["force_y"]) - expected_by_id[int(row["body_id"])][1])
            for row in force_rows
        )
        validation = {
            "skipped": False,
            "compared_against": "sum_aggregate_frontier_weighted_vectors_2d_cpu_reference",
            "tolerance": 1.0e-7,
            "max_abs_diff_x": max_abs_diff_x,
            "max_abs_diff_y": max_abs_diff_y,
            "passed": max_abs_diff_x <= 1.0e-7 and max_abs_diff_y <= 1.0e-7,
            "reference_frontier_row_count": int(reference["summary"]["contribution_row_count"]),
        }
        if not bool(validation["passed"]):
            raise AssertionError("fused Numba CPU frontier baseline failed validation")

    aggregate_count = int(aggregate_counts.sum())
    exact_count = int(exact_counts.sum())
    return {
        "app": "barnes_hut_force_app",
        "backend": "cpu_numba_fused_frontier_vector_sum",
        "mode": "fused_frontier_force_sum_bucketized_cpu_numba",
        "body_count": len(bodies),
        "theta": theta,
        "softening": app.SOFTENING,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "run_phases": {
            "body_generation_sec": body_generation_sec,
            "tree_build_sec": tree_build_sec,
            "vector_prepare_sec": vector_prepare_sec,
            "vector_run_median_sec": vector_run_median_sec,
            "total_sec": total_sec,
        },
        "medians": {
            "fused_numba_cpu_vector_seconds": vector_run_median_sec,
        },
        "vector_sum_summary": {
            "contract": "generic_aggregate_frontier_weighted_vector_sum_2d_numba_cpu_v1",
            "source_count": len(bodies),
            "target_count": len(bodies),
            "tree_node_count": len(tree_nodes),
            "visited_node_total": int(visited_counts.sum()),
            "contribution_row_count": aggregate_count + exact_count,
            "aggregate_contribution_row_count": aggregate_count,
            "exact_contribution_row_count": exact_count,
            "materialized_frontier_rows": False,
            "materialized_contribution_rows": False,
            "frontier_rows_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "numba_cpu_njit_used": True,
            "parallel_by_source": True,
            "raw_c_or_cuda_kernel_required": False,
            "prepare_seconds": vector_prepare_sec,
            "repeat_seconds": tuple(float(value) for value in repeat_seconds),
            "run_median_seconds": vector_run_median_sec,
            "warmup": warmup_count,
            "repeat": repeat_count,
            "checksum_force_x": sum(float(row["force_x"]) for row in force_rows),
            "checksum_force_y": sum(float(row["force_y"]) for row in force_rows),
            "force_rows": force_sample if force_output_mode == "full" else [],
            "force_rows_truncated": force_truncated if force_output_mode == "full" else True,
            "force_output_mode": force_output_mode,
        },
        "validation": validation,
        "claim_flags": {
            "same_logical_frontier_contract": True,
            "same_device_resident_contract": False,
            "frontier_rows_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "python_vector_sum_used": False,
            "numba_cpu_njit_used": True,
            "raw_c_or_cuda_kernel_required": False,
            "native_engine_app_specific": False,
            "automatic_partner_selection_allowed": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
        "boundary": (
            "Fused CPU/Numba aggregate-frontier weighted-vector baseline. This "
            "avoids frontier and contribution row materialization and requires "
            "no C++ or CUDA source, but it is still app partner code rather than "
            "an Embree/OptiX backend comparison or public speedup claim."
        ),
    }


def _fused_frontier_force_sum_numba_cuda_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
    skip_validation: bool,
    query_repeat: int,
    warmup: int,
    force_output_mode: str,
) -> dict[str, Any]:
    if query_repeat < 1:
        raise ValueError("query_repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if force_output_mode not in {"full", "force_summary"}:
        raise ValueError("force_output_mode must be 'full' or 'force_summary'")

    total_start = time.perf_counter()
    body_start = time.perf_counter()
    bodies = _make_bodies(body_count)
    body_generation_sec = time.perf_counter() - body_start

    tree_start = time.perf_counter()
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    tree_nodes = tuple(tree["nodes"])
    tree_build_sec = time.perf_counter() - tree_start

    prepare_start = time.perf_counter()
    prepared = rt.prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda(
        bodies,
        bodies,
        tree_nodes,
    )
    vector_prepare_sec = time.perf_counter() - prepare_start

    warmup_count = max(0, int(warmup))
    repeat_count = max(1, int(query_repeat))
    for _ in range(warmup_count):
        prepared.sum(theta=theta, softening=app.SOFTENING, use_cuda_events=True)

    repeat_seconds: list[float] = []
    kernel_event_seconds: list[float] = []
    metadata_partner_seconds: list[float] = []
    last_actual: dict[str, object] | None = None
    for _ in range(repeat_count):
        run_start = time.perf_counter()
        actual = prepared.sum(theta=theta, softening=app.SOFTENING, use_cuda_events=True)
        repeat_seconds.append(time.perf_counter() - run_start)
        metadata = actual["metadata"]
        if isinstance(metadata, dict):
            metadata_partner_seconds.append(float(metadata["partner_seconds"]))
            kernel_event_ms = metadata.get("kernel_event_ms")
            if kernel_event_ms is not None:
                kernel_event_seconds.append(float(kernel_event_ms) / 1000.0)
        last_actual = actual
    if last_actual is None:
        raise AssertionError("repeat_count normalization failed")

    copy_start = time.perf_counter()
    columns = last_actual["columns"]
    if not isinstance(columns, dict):
        raise TypeError("fused Numba CUDA columns must be a mapping")
    source_ids = _device_column_to_list(columns["source_ids"], value_type=int)
    vector_x = _device_column_to_list(columns["vector_x"], value_type=float)
    vector_y = _device_column_to_list(columns["vector_y"], value_type=float)
    visited_counts = _device_column_to_list(columns["visited_counts"], value_type=int)
    aggregate_counts = _device_column_to_list(columns["aggregate_counts"], value_type=int)
    exact_counts = _device_column_to_list(columns["exact_counts"], value_type=int)
    vector_copy_to_host_sec = time.perf_counter() - copy_start

    force_rows = tuple(
        {
            "body_id": int(source_ids[index]),
            "force_x": float(vector_x[index]),
            "force_y": float(vector_y[index]),
            "contribution_count": int(aggregate_counts[index] + exact_counts[index]),
            "aggregate_contribution_count": int(aggregate_counts[index]),
            "exact_contribution_count": int(exact_counts[index]),
            "visited_node_count": int(visited_counts[index]),
        }
        for index in range(len(source_ids))
    )
    force_sample, force_truncated = _truncate_rows(force_rows)

    metadata = last_actual["metadata"]
    if not isinstance(metadata, dict):
        raise TypeError("fused Numba CUDA metadata must be a mapping")
    aggregate_count = int(sum(aggregate_counts))
    exact_count = int(sum(exact_counts))
    contribution_count = aggregate_count + exact_count
    if contribution_count != int(metadata["contribution_row_count"]):
        raise AssertionError("per-source count columns do not match fused CUDA metadata")

    validation: dict[str, object]
    if skip_validation or len(bodies) > 2048:
        validation = {
            "skipped": True,
            "reason": "user_skip_validation" if skip_validation else "body_count_above_2048",
        }
    else:
        reference = rt.sum_aggregate_frontier_weighted_vectors_2d(
            bodies,
            bodies,
            tree_nodes,
            theta=theta,
            softening=app.SOFTENING,
        )
        expected_by_id = {
            int(row["source_id"]): (float(row["vector_x"]), float(row["vector_y"]))
            for row in reference["vector_sum_rows"]
        }
        max_abs_diff_x = max(
            abs(float(row["force_x"]) - expected_by_id[int(row["body_id"])][0])
            for row in force_rows
        )
        max_abs_diff_y = max(
            abs(float(row["force_y"]) - expected_by_id[int(row["body_id"])][1])
            for row in force_rows
        )
        validation = {
            "skipped": False,
            "compared_against": "sum_aggregate_frontier_weighted_vectors_2d_cpu_reference",
            "tolerance": 1.0e-7,
            "max_abs_diff_x": max_abs_diff_x,
            "max_abs_diff_y": max_abs_diff_y,
            "passed": max_abs_diff_x <= 1.0e-7 and max_abs_diff_y <= 1.0e-7,
            "reference_frontier_row_count": int(reference["summary"]["contribution_row_count"]),
        }
        if int(validation["reference_frontier_row_count"]) != contribution_count:
            validation["passed"] = False
            validation["count_mismatch"] = {
                "actual": contribution_count,
                "expected": int(validation["reference_frontier_row_count"]),
            }
        if not bool(validation["passed"]):
            raise AssertionError("fused Numba CUDA app mode failed validation")

    partner_wall_median_sec = float(statistics.median(metadata_partner_seconds or repeat_seconds))
    call_wall_median_sec = float(statistics.median(repeat_seconds))
    kernel_event_median_sec = (
        float(statistics.median(kernel_event_seconds))
        if kernel_event_seconds
        else None
    )
    vector_run_median_sec = (
        float(kernel_event_median_sec)
        if kernel_event_median_sec is not None
        else partner_wall_median_sec
    )
    checksum_force_x = float(sum(vector_x))
    checksum_force_y = float(sum(vector_y))
    total_sec = time.perf_counter() - total_start

    return {
        "app": "barnes_hut_force_app",
        "backend": "numba_cuda_fused_aggregate_tree_vector_sum",
        "mode": "fused_frontier_force_sum_bucketized_numba_cuda",
        "body_count": len(bodies),
        "theta": theta,
        "softening": app.SOFTENING,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "run_phases": {
            "body_generation_sec": body_generation_sec,
            "tree_build_sec": tree_build_sec,
            "vector_prepare_sec": vector_prepare_sec,
            "prepared_api_prepare_seconds": float(metadata["prepare_seconds"]),
            "vector_run_median_sec": vector_run_median_sec,
            "kernel_event_median_sec": kernel_event_median_sec,
            "partner_wall_median_sec": partner_wall_median_sec,
            "call_wall_median_sec": call_wall_median_sec,
            "vector_copy_to_host_sec": vector_copy_to_host_sec,
            "total_sec": total_sec,
        },
        "medians": {
            "fused_numba_cuda_kernel_event_seconds": kernel_event_median_sec,
            "fused_numba_cuda_partner_wall_seconds": partner_wall_median_sec,
            "fused_numba_cuda_call_wall_seconds": call_wall_median_sec,
        },
        "vector_sum_summary": {
            "contract": rt.AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CUDA_CONTRACT,
            "logical_reference_contract": rt.AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
            "source_count": len(bodies),
            "target_count": len(bodies),
            "tree_node_count": len(tree_nodes),
            "visited_node_total": int(sum(visited_counts)),
            "contribution_row_count": contribution_count,
            "aggregate_contribution_row_count": aggregate_count,
            "exact_contribution_row_count": exact_count,
            "frontier_rows_emitted": False,
            "materialized_frontier_rows": False,
            "materialized_contribution_rows": False,
            "frontier_rows_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "numba_cuda_jit_used": True,
            "numba_cuda_python_source_used": True,
            "parallel_by_source": True,
            "raw_c_or_cuda_kernel_required": False,
            "prepared_lookup_columns_resident": True,
            "aggregate_tree_columns_resident": True,
            "source_columns_reused": True,
            "target_columns_reused": True,
            "output_columns_reused": True,
            "prepare_seconds": vector_prepare_sec,
            "prepared_api_prepare_seconds": float(metadata["prepare_seconds"]),
            "repeat_seconds": tuple(float(value) for value in repeat_seconds),
            "partner_wall_seconds": tuple(float(value) for value in metadata_partner_seconds),
            "kernel_event_seconds": tuple(float(value) for value in kernel_event_seconds),
            "run_median_seconds": vector_run_median_sec,
            "kernel_event_median_seconds": kernel_event_median_sec,
            "partner_wall_median_seconds": partner_wall_median_sec,
            "call_wall_median_seconds": call_wall_median_sec,
            "warmup": warmup_count,
            "repeat": repeat_count,
            "checksum_force_x": checksum_force_x,
            "checksum_force_y": checksum_force_y,
            "force_rows": force_sample if force_output_mode == "full" else [],
            "force_rows_truncated": force_truncated if force_output_mode == "full" else True,
            "force_output_mode": force_output_mode,
        },
        "validation": validation,
        "claim_flags": {
            "same_logical_frontier_contract": True,
            "fused_aggregate_tree_contract": True,
            "same_device_resident_contract": True,
            "frontier_rows_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "python_vector_sum_used": False,
            "numba_cuda_jit_used": True,
            "numba_cuda_python_source_used": True,
            "raw_c_or_cuda_kernel_required": False,
            "native_engine_app_specific": False,
            "automatic_partner_selection_allowed": False,
            "rt_cores_used": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
        "boundary": (
            "Barnes-Hut app front-door route for the reusable no-C++ Numba CUDA "
            "aggregate-tree fused weighted-vector partner API. It avoids frontier "
            "and contribution-row materialization and keeps the native engine "
            "app-agnostic, but it is not an RT-core primitive, not automatic "
            "partner selection, and not public speedup wording."
        ),
    }


def _prepared_execution_fused_vector_sum_numba_cuda_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
    skip_validation: bool,
    query_repeat: int,
    warmup: int,
    force_output_mode: str,
) -> dict[str, Any]:
    if query_repeat < 1:
        raise ValueError("query_repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if force_output_mode not in {"full", "force_summary"}:
        raise ValueError("force_output_mode must be 'full' or 'force_summary'")

    total_start = time.perf_counter()
    body_start = time.perf_counter()
    bodies = _make_bodies(body_count)
    body_generation_sec = time.perf_counter() - body_start

    tree_start = time.perf_counter()
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    tree_nodes = tuple(tree["nodes"])
    tree_build_sec = time.perf_counter() - tree_start

    source_fingerprint = rt.make_prepared_input_fingerprint(bodies)
    target_fingerprint = rt.make_prepared_input_fingerprint(bodies)
    aggregate_tree_fingerprint = rt.make_prepared_input_fingerprint(tree_nodes)
    cache = rt.ExplicitPreparedSessionCache(max_entries=1)

    def prepare_session() -> Any:
        return rt.prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda(
            bodies,
            bodies,
            tree_nodes,
        )

    def run_vector_sum(prepared: Any) -> dict[str, object]:
        return prepared.sum(theta=theta, softening=app.SOFTENING, use_cuda_events=True)

    runner_result = rt.run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session(
        source_fingerprint=source_fingerprint,
        target_fingerprint=target_fingerprint,
        aggregate_tree_fingerprint=aggregate_tree_fingerprint,
        source_count=len(bodies),
        target_count=len(bodies),
        tree_node_count=len(tree_nodes),
        theta=theta,
        softening=app.SOFTENING,
        partner="numba_cuda",
        cache=cache,
        prepare_session=prepare_session,
        run_vector_sum=run_vector_sum,
        backend="partner",
        output_contract=rt.AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CUDA_CONTRACT,
        device="cuda",
        warmup_count=max(0, int(warmup)),
        measured_repeat_count=max(1, int(query_repeat)),
        retain_repeat_outputs=True,
        scorecard_binding={
            "id": "set_a_barnes_hut_app_geomean_0_844x",
            "set": "A",
            "app": "barnes_hut",
            "metric": "set_a_app_geomean_v3_vs_v2_14",
            "current_value": 0.844,
            "target": "move_toward_or_above_parity",
            "source": "docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md",
            "route_kind": "trunk_fix_candidate",
            "role": "aggregate_tree_fused_vector_sum_front_door_probe",
        },
        win_source="partner_continuation",
    )
    runner_metadata = runner_result.to_metadata()
    actual_outputs = (
        tuple(runner_result.output)
        if isinstance(runner_result.output, tuple)
        else (runner_result.output,)
    )
    if not actual_outputs:
        raise AssertionError("prepared execution runner returned no vector-sum output")
    last_actual = actual_outputs[-1]
    if not isinstance(last_actual, dict):
        raise TypeError("prepared execution fused Numba CUDA output must be a mapping")

    metadata_partner_seconds: list[float] = []
    kernel_event_seconds: list[float] = []
    for actual in actual_outputs:
        if not isinstance(actual, dict):
            continue
        actual_metadata = actual.get("metadata")
        if isinstance(actual_metadata, dict):
            metadata_partner_seconds.append(float(actual_metadata["partner_seconds"]))
            kernel_event_ms = actual_metadata.get("kernel_event_ms")
            if kernel_event_ms is not None:
                kernel_event_seconds.append(float(kernel_event_ms) / 1000.0)
    repeat_seconds = tuple(float(value) for value in runner_metadata["measured_repeat_seconds"])

    copy_start = time.perf_counter()
    columns = last_actual["columns"]
    if not isinstance(columns, dict):
        raise TypeError("prepared execution fused Numba CUDA columns must be a mapping")
    source_ids = _device_column_to_list(columns["source_ids"], value_type=int)
    vector_x = _device_column_to_list(columns["vector_x"], value_type=float)
    vector_y = _device_column_to_list(columns["vector_y"], value_type=float)
    visited_counts = _device_column_to_list(columns["visited_counts"], value_type=int)
    aggregate_counts = _device_column_to_list(columns["aggregate_counts"], value_type=int)
    exact_counts = _device_column_to_list(columns["exact_counts"], value_type=int)
    vector_copy_to_host_sec = time.perf_counter() - copy_start

    force_rows = tuple(
        {
            "body_id": int(source_ids[index]),
            "force_x": float(vector_x[index]),
            "force_y": float(vector_y[index]),
            "contribution_count": int(aggregate_counts[index] + exact_counts[index]),
            "aggregate_contribution_count": int(aggregate_counts[index]),
            "exact_contribution_count": int(exact_counts[index]),
            "visited_node_count": int(visited_counts[index]),
        }
        for index in range(len(source_ids))
    )
    force_sample, force_truncated = _truncate_rows(force_rows)

    metadata = last_actual["metadata"]
    if not isinstance(metadata, dict):
        raise TypeError("prepared execution fused Numba CUDA metadata must be a mapping")
    aggregate_count = int(sum(aggregate_counts))
    exact_count = int(sum(exact_counts))
    contribution_count = aggregate_count + exact_count
    if contribution_count != int(metadata["contribution_row_count"]):
        raise AssertionError("per-source count columns do not match fused CUDA metadata")

    validation: dict[str, object]
    if skip_validation or len(bodies) > 2048:
        validation = {
            "skipped": True,
            "reason": "user_skip_validation" if skip_validation else "body_count_above_2048",
        }
    else:
        reference = rt.sum_aggregate_frontier_weighted_vectors_2d(
            bodies,
            bodies,
            tree_nodes,
            theta=theta,
            softening=app.SOFTENING,
        )
        expected_by_id = {
            int(row["source_id"]): (float(row["vector_x"]), float(row["vector_y"]))
            for row in reference["vector_sum_rows"]
        }
        max_abs_diff_x = max(
            abs(float(row["force_x"]) - expected_by_id[int(row["body_id"])][0])
            for row in force_rows
        )
        max_abs_diff_y = max(
            abs(float(row["force_y"]) - expected_by_id[int(row["body_id"])][1])
            for row in force_rows
        )
        validation = {
            "skipped": False,
            "compared_against": "sum_aggregate_frontier_weighted_vectors_2d_cpu_reference",
            "tolerance": 1.0e-7,
            "max_abs_diff_x": max_abs_diff_x,
            "max_abs_diff_y": max_abs_diff_y,
            "passed": max_abs_diff_x <= 1.0e-7 and max_abs_diff_y <= 1.0e-7,
            "reference_frontier_row_count": int(reference["summary"]["contribution_row_count"]),
        }
        if int(validation["reference_frontier_row_count"]) != contribution_count:
            validation["passed"] = False
            validation["count_mismatch"] = {
                "actual": contribution_count,
                "expected": int(validation["reference_frontier_row_count"]),
            }
        if not bool(validation["passed"]):
            raise AssertionError("prepared execution fused Numba CUDA app mode failed validation")

    partner_wall_median_sec = float(statistics.median(metadata_partner_seconds or repeat_seconds))
    call_wall_median_sec = float(statistics.median(repeat_seconds))
    kernel_event_median_sec = (
        float(statistics.median(kernel_event_seconds))
        if kernel_event_seconds
        else None
    )
    vector_run_median_sec = (
        float(kernel_event_median_sec)
        if kernel_event_median_sec is not None
        else partner_wall_median_sec
    )
    checksum_force_x = float(sum(vector_x))
    checksum_force_y = float(sum(vector_y))
    total_sec = time.perf_counter() - total_start

    return {
        "app": "barnes_hut_force_app",
        "backend": "prepared_execution_runner_numba_cuda_fused_aggregate_tree_vector_sum",
        "mode": "prepared_execution_fused_vector_sum_numba_cuda",
        "body_count": len(bodies),
        "theta": theta,
        "softening": app.SOFTENING,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "prepared_execution_session_runner": runner_metadata,
        "phoenix_v3_m72": {
            "target": "barnes_hut_aggregate_tree_set_a_blocker",
            "scorecard_blocker_bound": bool(runner_metadata["scorecard_blocker_bound"]),
            "scorecard_blocker_app": runner_metadata.get("scorecard_blocker_app"),
            "scorecard_blocker_current_value": runner_metadata.get("scorecard_blocker_current_value"),
            "scorecard_blocker_target": runner_metadata.get("scorecard_blocker_target"),
            "scorecard_blocker_route_kind": runner_metadata.get("scorecard_blocker_route_kind"),
            "win_source": runner_metadata.get("win_source"),
            "m43_reuse_scope": runner_metadata.get("m43_reuse_scope"),
            "release_path_candidate": bool(runner_metadata.get("release_path_candidate")),
            "pod_authorized": False,
            "release_authorized": False,
            "all_app_authorized": False,
        },
        "run_phases": {
            "body_generation_sec": body_generation_sec,
            "tree_build_sec": tree_build_sec,
            "runner_prepare_or_cache_sec": float(
                runner_metadata["prepared_execution_report"]["summary_sec"]["setup"]
            ),
            "prepared_api_prepare_seconds": float(metadata["prepare_seconds"]),
            "vector_run_median_sec": vector_run_median_sec,
            "kernel_event_median_sec": kernel_event_median_sec,
            "partner_wall_median_sec": partner_wall_median_sec,
            "call_wall_median_sec": call_wall_median_sec,
            "runner_measured_median_sec": float(runner_metadata["measured_median_sec"]),
            "vector_copy_to_host_sec": vector_copy_to_host_sec,
            "total_sec": total_sec,
        },
        "medians": {
            "fused_numba_cuda_kernel_event_seconds": kernel_event_median_sec,
            "fused_numba_cuda_partner_wall_seconds": partner_wall_median_sec,
            "fused_numba_cuda_call_wall_seconds": call_wall_median_sec,
            "prepared_execution_runner_measured_seconds": float(runner_metadata["measured_median_sec"]),
        },
        "vector_sum_summary": {
            "contract": rt.AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CUDA_CONTRACT,
            "logical_reference_contract": rt.AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
            "source_count": len(bodies),
            "target_count": len(bodies),
            "tree_node_count": len(tree_nodes),
            "visited_node_total": int(sum(visited_counts)),
            "contribution_row_count": contribution_count,
            "aggregate_contribution_row_count": aggregate_count,
            "exact_contribution_row_count": exact_count,
            "frontier_rows_emitted": False,
            "materialized_frontier_rows": False,
            "materialized_contribution_rows": False,
            "frontier_rows_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "numba_cuda_jit_used": True,
            "numba_cuda_python_source_used": True,
            "parallel_by_source": True,
            "raw_c_or_cuda_kernel_required": False,
            "prepared_lookup_columns_resident": True,
            "aggregate_tree_columns_resident": True,
            "source_columns_reused": True,
            "target_columns_reused": True,
            "output_columns_reused": True,
            "internal_device_residency_between_rtdl_phases": bool(
                runner_metadata["internal_device_residency_between_rtdl_phases"]
            ),
            "hot_path_host_materialization": bool(runner_metadata["hot_path_host_materialization"]),
            "runtime_trunk_executes_end_to_end": bool(runner_metadata["runtime_trunk_executes_end_to_end"]),
            "win_source": runner_metadata.get("win_source"),
            "scorecard_blocker_bound": bool(runner_metadata["scorecard_blocker_bound"]),
            "scorecard_blocker_app": runner_metadata.get("scorecard_blocker_app"),
            "scorecard_blocker_current_value": runner_metadata.get("scorecard_blocker_current_value"),
            "scorecard_blocker_target": runner_metadata.get("scorecard_blocker_target"),
            "m43_reuse_scope": runner_metadata.get("m43_reuse_scope"),
            "prepare_seconds": float(metadata["prepare_seconds"]),
            "repeat_seconds": repeat_seconds,
            "partner_wall_seconds": tuple(float(value) for value in metadata_partner_seconds),
            "kernel_event_seconds": tuple(float(value) for value in kernel_event_seconds),
            "run_median_seconds": vector_run_median_sec,
            "kernel_event_median_seconds": kernel_event_median_sec,
            "partner_wall_median_seconds": partner_wall_median_sec,
            "call_wall_median_seconds": call_wall_median_sec,
            "warmup": max(0, int(warmup)),
            "repeat": max(1, int(query_repeat)),
            "checksum_force_x": checksum_force_x,
            "checksum_force_y": checksum_force_y,
            "force_rows": force_sample if force_output_mode == "full" else [],
            "force_rows_truncated": force_truncated if force_output_mode == "full" else True,
            "force_output_mode": force_output_mode,
        },
        "validation": validation,
        "claim_flags": {
            "same_logical_frontier_contract": True,
            "fused_aggregate_tree_contract": True,
            "productized_execution_path": "prepared_execution_session_runner",
            "runtime_trunk_executes_end_to_end": bool(runner_metadata["runtime_trunk_executes_end_to_end"]),
            "scorecard_blocker_bound": bool(runner_metadata["scorecard_blocker_bound"]),
            "scorecard_blocker_app": runner_metadata.get("scorecard_blocker_app"),
            "scorecard_blocker_current_value": runner_metadata.get("scorecard_blocker_current_value"),
            "scorecard_blocker_target": runner_metadata.get("scorecard_blocker_target"),
            "scorecard_blocker_route_kind": runner_metadata.get("scorecard_blocker_route_kind"),
            "win_source": runner_metadata.get("win_source"),
            "m43_reuse_scope": runner_metadata.get("m43_reuse_scope"),
            "same_device_resident_contract": True,
            "frontier_rows_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "hot_path_host_materialization": False,
            "python_vector_sum_used": False,
            "numba_cuda_jit_used": True,
            "numba_cuda_python_source_used": True,
            "raw_c_or_cuda_kernel_required": False,
            "native_engine_app_specific": False,
            "automatic_partner_selection_allowed": False,
            "automatic_partner_selection_authorized": False,
            "rt_cores_used": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "v4_embedding_or_external_zero_copy_authorized": False,
            "full_all_app_rerun_authorized_by_this_packet": False,
        },
        "boundary": (
            "Phoenix V3 prepared-execution runner route for the reusable no-C++ "
            "Numba CUDA aggregate-tree fused weighted-vector partner API. It "
            "avoids frontier and contribution-row materialization and keeps the "
            "native engine app-agnostic, but it is not an RT-core primitive, not "
            "automatic partner selection, not V4 external buffer interop, and "
            "not public speedup wording."
        ),
    }


def _native_fused_vector_sum_cuda_device_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
    skip_validation: bool,
    query_repeat: int,
    warmup: int,
    force_output_mode: str,
) -> dict[str, Any]:
    if query_repeat < 1:
        raise ValueError("query_repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if force_output_mode not in {"full", "force_summary"}:
        raise ValueError("force_output_mode must be 'full' or 'force_summary'")

    total_start = time.perf_counter()
    body_start = time.perf_counter()
    bodies = _make_bodies(body_count)
    body_generation_sec = time.perf_counter() - body_start

    tree_start = time.perf_counter()
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    tree_nodes = tuple(tree["nodes"])
    tree_build_sec = time.perf_counter() - tree_start

    import cupy as cp  # type: ignore

    source_ids_device = cp.asarray([int(point.id) for point in bodies], dtype=cp.int64)
    source_x_device = cp.asarray([float(point.x) for point in bodies], dtype=cp.float64)
    source_y_device = cp.asarray([float(point.y) for point in bodies], dtype=cp.float64)
    source_weight_device = cp.asarray([float(point.mass) for point in bodies], dtype=cp.float64)
    source_column_owners = (
        source_ids_device,
        source_x_device,
        source_y_device,
        source_weight_device,
    )

    source_fingerprint = rt.make_prepared_input_fingerprint(bodies)
    target_fingerprint = rt.make_prepared_input_fingerprint(bodies)
    aggregate_tree_fingerprint = rt.make_prepared_input_fingerprint(tree_nodes)
    cache = rt.ExplicitPreparedSessionCache(max_entries=1)

    def prepare_session() -> Any:
        return rt.prepare_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_optix(
            bodies,
            tree_nodes,
        )

    def run_vector_sum(prepared: Any) -> dict[str, object]:
        native_output = prepared.run_device_columns(
            source_ids_device_ptr=int(source_ids_device.data.ptr),
            source_x_device_ptr=int(source_x_device.data.ptr),
            source_y_device_ptr=int(source_y_device.data.ptr),
            source_weight_device_ptr=int(source_weight_device.data.ptr),
            source_count=len(bodies),
            theta=theta,
            softening=app.SOFTENING,
            source_column_owners=source_column_owners,
        )
        native_metadata = native_output.to_metadata()
        native_metadata.update(
            {
                "partner": "native_cuda",
                "source_count": len(bodies),
                "target_count": len(bodies),
                "tree_node_count": len(tree_nodes),
                "prepared_lookup_columns_resident": True,
                "aggregate_tree_columns_resident": True,
                "source_columns_reused": True,
                "target_columns_reused": True,
                "output_columns_reused": False,
                "device_resident": bool(native_output.device_resident),
                "frontier_rows_emitted": False,
                "materialized_frontier_rows": False,
                "materialized_contribution_rows": False,
                "frontier_rows_materialized_on_host": False,
                "contribution_rows_materialized_on_host": False,
                "hot_path_host_materialization": False,
                "rt_cores_used": False,
                "optix_trace_used": False,
                "cuda_only_fused_device_accumulation": True,
                "native_engine_app_specific": False,
                "automatic_partner_selection_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            }
        )
        native_columns = native_output.as_cupy_columns()
        columns = {
            "source_ids": native_columns["source_id"],
            "vector_x": native_columns["vector_x"],
            "vector_y": native_columns["vector_y"],
            "visited_counts": native_columns["visited_count"],
            "aggregate_counts": native_columns["aggregate_count"],
            "exact_counts": native_columns["exact_count"],
        }
        return {
            "columns": columns,
            "metadata": native_metadata,
        }

    runner_result = rt.run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session(
        source_fingerprint=source_fingerprint,
        target_fingerprint=target_fingerprint,
        aggregate_tree_fingerprint=aggregate_tree_fingerprint,
        source_count=len(bodies),
        target_count=len(bodies),
        tree_node_count=len(tree_nodes),
        theta=theta,
        softening=app.SOFTENING,
        partner="native_cuda",
        cache=cache,
        prepare_session=prepare_session,
        run_vector_sum=run_vector_sum,
        backend="optix",
        output_contract=rt.AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE_CONTRACT,
        device="cuda",
        warmup_count=max(0, int(warmup)),
        measured_repeat_count=max(1, int(query_repeat)),
        retain_repeat_outputs=True,
        scorecard_binding={
            "id": "set_a_barnes_hut_app_geomean_0_844x",
            "set": "A",
            "app": "barnes_hut",
            "metric": "set_a_app_geomean_v3_vs_v2_14",
            "current_value": 0.844,
            "target": "move_toward_or_above_parity",
            "source": "docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md",
            "route_kind": "trunk_fix_candidate",
            "role": "aggregate_tree_native_fused_vector_sum_front_door_probe",
        },
        win_source="kernel",
    )
    runner_metadata = runner_result.to_metadata()
    actual_outputs = (
        tuple(runner_result.output)
        if isinstance(runner_result.output, tuple)
        else (runner_result.output,)
    )
    if not actual_outputs:
        raise AssertionError("native prepared execution runner returned no vector-sum output")
    last_actual = actual_outputs[-1]
    if not isinstance(last_actual, dict):
        raise TypeError("native prepared execution output must be a mapping")
    metadata = last_actual["metadata"]
    if not isinstance(metadata, dict):
        raise TypeError("native prepared execution metadata must be a mapping")

    copy_start = time.perf_counter()
    columns = last_actual["columns"]
    if not isinstance(columns, dict):
        raise TypeError("native prepared execution columns must be a mapping")
    source_ids = _device_column_to_list(columns["source_ids"], value_type=int)
    vector_x = _device_column_to_list(columns["vector_x"], value_type=float)
    vector_y = _device_column_to_list(columns["vector_y"], value_type=float)
    visited_counts = _device_column_to_list(columns["visited_counts"], value_type=int)
    aggregate_counts = _device_column_to_list(columns["aggregate_counts"], value_type=int)
    exact_counts = _device_column_to_list(columns["exact_counts"], value_type=int)
    vector_copy_to_host_sec = time.perf_counter() - copy_start

    force_rows = tuple(
        {
            "body_id": int(source_ids[index]),
            "force_x": float(vector_x[index]),
            "force_y": float(vector_y[index]),
            "contribution_count": int(aggregate_counts[index] + exact_counts[index]),
            "aggregate_contribution_count": int(aggregate_counts[index]),
            "exact_contribution_count": int(exact_counts[index]),
            "visited_node_count": int(visited_counts[index]),
        }
        for index in range(len(source_ids))
    )
    force_sample, force_truncated = _truncate_rows(force_rows)

    aggregate_count = int(sum(aggregate_counts))
    exact_count = int(sum(exact_counts))
    contribution_count = aggregate_count + exact_count
    validation: dict[str, object]
    if skip_validation or len(bodies) > 2048:
        validation = {
            "skipped": True,
            "reason": "user_skip_validation" if skip_validation else "body_count_above_2048",
        }
    else:
        reference = rt.sum_aggregate_frontier_weighted_vectors_2d(
            bodies,
            bodies,
            tree_nodes,
            theta=theta,
            softening=app.SOFTENING,
        )
        expected_by_id = {
            int(row["source_id"]): (float(row["vector_x"]), float(row["vector_y"]))
            for row in reference["vector_sum_rows"]
        }
        max_abs_diff_x = max(
            abs(float(row["force_x"]) - expected_by_id[int(row["body_id"])][0])
            for row in force_rows
        )
        max_abs_diff_y = max(
            abs(float(row["force_y"]) - expected_by_id[int(row["body_id"])][1])
            for row in force_rows
        )
        validation = {
            "skipped": False,
            "compared_against": "sum_aggregate_frontier_weighted_vectors_2d_cpu_reference",
            "tolerance": 1.0e-7,
            "max_abs_diff_x": max_abs_diff_x,
            "max_abs_diff_y": max_abs_diff_y,
            "passed": max_abs_diff_x <= 1.0e-7 and max_abs_diff_y <= 1.0e-7,
            "reference_frontier_row_count": int(reference["summary"]["contribution_row_count"]),
        }
        if int(validation["reference_frontier_row_count"]) != contribution_count:
            validation["passed"] = False
            validation["count_mismatch"] = {
                "actual": contribution_count,
                "expected": int(validation["reference_frontier_row_count"]),
            }
        if not bool(validation["passed"]):
            raise AssertionError("native fused CUDA device app mode failed validation")

    repeat_seconds = tuple(float(value) for value in runner_metadata["measured_repeat_seconds"])
    native_traversal_seconds = [
        float(actual["metadata"]["traversal_seconds"])
        for actual in actual_outputs
        if isinstance(actual, dict) and isinstance(actual.get("metadata"), dict)
    ]
    native_traversal_median_sec = (
        float(statistics.median(native_traversal_seconds))
        if native_traversal_seconds
        else float(runner_metadata["measured_median_sec"])
    )
    total_sec = time.perf_counter() - total_start

    return {
        "app": "barnes_hut_force_app",
        "backend": "optix_native_cuda_device_fused_aggregate_tree_vector_sum",
        "mode": "native_fused_vector_sum_cuda_device",
        "body_count": len(bodies),
        "theta": theta,
        "softening": app.SOFTENING,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "prepared_execution_session_runner": runner_metadata,
        "phoenix_v3_m72": {
            "target": "barnes_hut_aggregate_tree_set_a_blocker",
            "scorecard_blocker_bound": bool(runner_metadata["scorecard_blocker_bound"]),
            "scorecard_blocker_app": runner_metadata.get("scorecard_blocker_app"),
            "scorecard_blocker_current_value": runner_metadata.get("scorecard_blocker_current_value"),
            "scorecard_blocker_target": runner_metadata.get("scorecard_blocker_target"),
            "scorecard_blocker_route_kind": runner_metadata.get("scorecard_blocker_route_kind"),
            "win_source": runner_metadata.get("win_source"),
            "release_path_candidate": bool(runner_metadata.get("release_path_candidate")),
            "pod_authorized": False,
            "release_authorized": False,
            "all_app_authorized": False,
        },
        "run_phases": {
            "body_generation_sec": body_generation_sec,
            "tree_build_sec": tree_build_sec,
            "runner_prepare_or_cache_sec": float(
                runner_metadata["prepared_execution_report"]["summary_sec"]["setup"]
            ),
            "native_traversal_median_sec": native_traversal_median_sec,
            "runner_measured_median_sec": float(runner_metadata["measured_median_sec"]),
            "vector_copy_to_host_sec": vector_copy_to_host_sec,
            "total_sec": total_sec,
        },
        "medians": {
            "native_cuda_kernel_seconds": native_traversal_median_sec,
            "prepared_execution_runner_measured_seconds": float(runner_metadata["measured_median_sec"]),
        },
        "vector_sum_summary": {
            "contract": rt.AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE_CONTRACT,
            "logical_reference_contract": rt.AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
            "source_count": len(bodies),
            "target_count": len(bodies),
            "tree_node_count": len(tree_nodes),
            "visited_node_total": int(sum(visited_counts)),
            "contribution_row_count": contribution_count,
            "aggregate_contribution_row_count": aggregate_count,
            "exact_contribution_row_count": exact_count,
            "frontier_rows_emitted": False,
            "materialized_frontier_rows": False,
            "materialized_contribution_rows": False,
            "frontier_rows_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "cuda_only_fused_device_accumulation": True,
            "prepared_lookup_columns_resident": True,
            "aggregate_tree_columns_resident": True,
            "source_columns_reused": True,
            "target_columns_reused": True,
            "output_columns_reused": False,
            "device_resident": bool(metadata.get("device_resident")),
            "internal_device_residency_between_rtdl_phases": bool(
                runner_metadata["internal_device_residency_between_rtdl_phases"]
            ),
            "hot_path_host_materialization": bool(runner_metadata["hot_path_host_materialization"]),
            "runtime_trunk_executes_end_to_end": bool(runner_metadata["runtime_trunk_executes_end_to_end"]),
            "win_source": runner_metadata.get("win_source"),
            "scorecard_blocker_bound": bool(runner_metadata["scorecard_blocker_bound"]),
            "scorecard_blocker_app": runner_metadata.get("scorecard_blocker_app"),
            "scorecard_blocker_current_value": runner_metadata.get("scorecard_blocker_current_value"),
            "scorecard_blocker_target": runner_metadata.get("scorecard_blocker_target"),
            "m43_reuse_scope": runner_metadata.get("m43_reuse_scope"),
            "native_traversal_seconds": tuple(native_traversal_seconds),
            "repeat_seconds": repeat_seconds,
            "run_median_seconds": native_traversal_median_sec,
            "call_wall_median_seconds": float(runner_metadata["measured_median_sec"]),
            "warmup": max(0, int(warmup)),
            "repeat": max(1, int(query_repeat)),
            "checksum_force_x": float(sum(vector_x)),
            "checksum_force_y": float(sum(vector_y)),
            "force_rows": force_sample if force_output_mode == "full" else [],
            "force_rows_truncated": force_truncated if force_output_mode == "full" else True,
            "force_output_mode": force_output_mode,
        },
        "validation": validation,
        "claim_flags": {
            "same_logical_frontier_contract": True,
            "fused_aggregate_tree_contract": True,
            "productized_execution_path": "prepared_execution_session_runner",
            "runtime_trunk_executes_end_to_end": bool(runner_metadata["runtime_trunk_executes_end_to_end"]),
            "scorecard_blocker_bound": bool(runner_metadata["scorecard_blocker_bound"]),
            "scorecard_blocker_app": runner_metadata.get("scorecard_blocker_app"),
            "scorecard_blocker_current_value": runner_metadata.get("scorecard_blocker_current_value"),
            "scorecard_blocker_target": runner_metadata.get("scorecard_blocker_target"),
            "scorecard_blocker_route_kind": runner_metadata.get("scorecard_blocker_route_kind"),
            "win_source": runner_metadata.get("win_source"),
            "same_device_resident_contract": True,
            "frontier_rows_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "hot_path_host_materialization": False,
            "python_vector_sum_used": False,
            "numba_cuda_jit_used": False,
            "numba_cuda_python_source_used": False,
            "raw_c_or_cuda_kernel_used": True,
            "native_engine_app_specific": False,
            "automatic_partner_selection_allowed": False,
            "automatic_partner_selection_authorized": False,
            "rt_cores_used": False,
            "optix_trace_used": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "v4_embedding_or_external_zero_copy_authorized": False,
            "full_all_app_rerun_authorized_by_this_packet": False,
        },
        "boundary": (
            "Phoenix V3 prepared-execution runner route for the reusable native "
            "CUDA device-resident aggregate-tree fused weighted-vector primitive. "
            "It avoids frontier and contribution-row materialization and keeps "
            "the native engine app-agnostic. It is not an RT-core speedup claim "
            "because this implementation does not launch an OptiX optixTrace "
            "pipeline, not automatic partner selection, not V4 external buffer "
            "interop, and not public speedup wording."
        ),
    }


def _fused_frontier_force_sum_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
) -> dict[str, Any]:
    bodies = _make_bodies(body_count)
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    vector_sums = rt.sum_aggregate_frontier_weighted_vectors_2d(
        bodies,
        bodies,
        tree["nodes"],
        theta=theta,
        softening=app.SOFTENING,
    )
    force_rows = tuple(
        {
            "body_id": int(row["source_id"]),
            "force_x": float(row["vector_x"]),
            "force_y": float(row["vector_y"]),
            "contribution_count": int(row["contribution_count"]),
            "aggregate_contribution_count": int(row["aggregate_contribution_count"]),
            "exact_contribution_count": int(row["exact_contribution_count"]),
            "visited_node_count": int(row["visited_node_count"]),
        }
        for row in vector_sums["vector_sum_rows"]
    )
    exact_forces = app.brute_force_forces(bodies) if len(bodies) <= 2048 else None
    error_rows = app._force_error_rows(force_rows, exact_forces) if exact_forces is not None else ()
    force_sample, force_truncated = _truncate_rows(force_rows)
    payload: dict[str, Any] = {
        "app": "barnes_hut_force_app",
        "backend": "cpu_python_reference",
        "body_count": len(bodies),
        "theta": theta,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "vector_sum_summary": vector_sums["summary"],
        "vector_sum_contract": vector_sums["metadata"]["contract"],
        "force_row_count": len(force_rows),
        "checksum_force_x": sum(float(row["force_x"]) for row in force_rows),
        "checksum_force_y": sum(float(row["force_y"]) for row in force_rows),
        "force_rows": force_sample,
        "force_rows_truncated": force_truncated,
        "validation_skipped": exact_forces is None,
        "boundary": (
            "Generic fused aggregate-frontier weighted vector sum. This avoids "
            "opening-frontier and contribution-row materialization in Python, "
            "but it is still a reference contract, not native/OptiX paper-code "
            "timing."
        ),
    }
    if exact_forces is not None:
        payload["max_relative_error"] = max((row["relative_error"] for row in error_rows), default=0.0)
        payload["mean_relative_error"] = (
            sum(row["relative_error"] for row in error_rows) / len(error_rows)
            if error_rows
            else 0.0
        )
    return payload


def _device_column_to_list(column: object, *, value_type: type) -> list[object]:
    if hasattr(column, "copy_to_host"):
        values = column.copy_to_host()
    elif hasattr(column, "get"):
        values = column.get()
    else:
        values = column
    if hasattr(values, "tolist"):
        values = values.tolist()
    return [value_type(value) for value in values]


def _median_fields(rows: list[dict[str, float]], field_names: tuple[str, ...]) -> dict[str, float]:
    return {
        field: float(statistics.median(float(row[field]) for row in rows))
        for field in field_names
    }


def _prepared_aggregate_frontier_weighted_vector_optix_payload(
    *,
    body_count: int | None,
    theta: float,
    bucket_size: int,
    max_depth: int,
    partner: str,
    skip_validation: bool,
    query_repeat: int,
    warmup: int,
    force_output_mode: str,
    frontier_row_capacity: int | None,
    frontier_capacity_multiplier: int,
) -> dict[str, Any]:
    if partner not in {"cupy", "numba"}:
        raise ValueError("prepared aggregate-frontier route supports --partner cupy or numba")
    if query_repeat < 1:
        raise ValueError("query_repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if frontier_row_capacity is not None and frontier_row_capacity <= 0:
        raise ValueError("frontier_row_capacity must be positive when provided")
    if frontier_capacity_multiplier <= 0:
        raise ValueError("frontier_capacity_multiplier must be positive")
    if force_output_mode not in {"full", "force_summary"}:
        raise ValueError("force_output_mode must be 'full' or 'force_summary'")

    setup_start = time.perf_counter()
    bodies = _make_bodies(body_count)
    body_generation_sec = time.perf_counter() - setup_start

    tree_start = time.perf_counter()
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    tree_nodes = tuple(tree["nodes"])
    tree_build_sec = time.perf_counter() - tree_start

    frontier_prepare_start = time.perf_counter()
    prepared_frontier = rt.prepare_aggregate_frontier_device_columns_2d_optix(
        tree_nodes,
        theta=theta,
    )
    frontier_prepare_wall_sec = time.perf_counter() - frontier_prepare_start

    vector_prepare_start = time.perf_counter()
    if partner == "numba":
        prepared_vector = rt.prepare_aggregate_frontier_device_columns_weighted_vectors_2d_numba(
            bodies,
            bodies,
            tree_nodes,
        )
        partner_contract = rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CONTRACT
    else:
        prepared_vector = rt.prepare_aggregate_frontier_device_columns_weighted_vectors_2d_cupy(
            bodies,
            bodies,
            tree_nodes,
        )
        partner_contract = rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_CONTRACT
    vector_prepare_wall_sec = time.perf_counter() - vector_prepare_start

    initial_capacity = (
        int(frontier_row_capacity)
        if frontier_row_capacity is not None
        else max(1024, len(bodies) * int(frontier_capacity_multiplier))
    )
    capacity_attempts: list[dict[str, object]] = []
    repeats: list[dict[str, float]] = []
    last_result: dict[str, object] | None = None

    with prepared_frontier:
        capacity = initial_capacity
        for attempt_index in range(4):
            frontier = prepared_frontier.run_device_columns(
                row_capacity=capacity,
                **prepared_vector.frontier_source_device_args(),
            )
            attempt = {
                "attempt_index": attempt_index,
                "capacity": int(capacity),
                "overflow": bool(frontier.overflow),
                "row_count": int(frontier.row_count),
                "attempted_count": int(frontier.attempted_count),
                "traversal_seconds": float(frontier.traversal_seconds),
            }
            capacity_attempts.append(attempt)
            if not frontier.overflow:
                capacity = int(frontier.attempted_count) + 1024
                break
            capacity = int(frontier.attempted_count) + 1024
        else:
            raise RuntimeError("aggregate-frontier device-column capacity probe overflowed four times")

        for _ in range(warmup):
            prepared_vector.run_with_prepared_frontier(
                prepared_frontier,
                row_capacity=capacity,
                softening=app.SOFTENING,
            )

        for repeat_index in range(query_repeat):
            wall_start = time.perf_counter()
            actual = prepared_vector.run_with_prepared_frontier(
                prepared_frontier,
                row_capacity=capacity,
                softening=app.SOFTENING,
            )
            wall_seconds = time.perf_counter() - wall_start
            frontier = actual["frontier"]
            vector_sum = actual["vector_sum"]
            vector_metadata = vector_sum["metadata"]
            metadata = actual["metadata"]
            if bool(frontier.overflow):
                raise RuntimeError("prepared aggregate-frontier hot run overflowed after capacity probe")
            repeats.append(
                {
                    "repeat_index": float(repeat_index),
                    "frontier_traversal_seconds": float(metadata["frontier_traversal_seconds"]),
                    "partner_seconds": float(metadata["partner_seconds"]),
                    "hot_seconds_native_plus_partner": float(metadata["hot_seconds"]),
                    "wall_seconds": float(wall_seconds),
                    "frontier_row_count": float(vector_metadata["frontier_row_count"]),
                    "aggregate_contribution_row_count": float(
                        vector_metadata["aggregate_contribution_row_count"]
                    ),
                    "exact_contribution_row_count": float(vector_metadata["exact_contribution_row_count"]),
                }
            )
            last_result = actual

    if last_result is None:
        raise RuntimeError("no prepared aggregate-frontier hot repeat executed")

    vector_sum = last_result["vector_sum"]
    vector_metadata = vector_sum["metadata"]
    columns = vector_sum["columns"]
    source_ids = _device_column_to_list(columns["source_ids"], value_type=int)
    vector_x = _device_column_to_list(columns["vector_x"], value_type=float)
    vector_y = _device_column_to_list(columns["vector_y"], value_type=float)
    force_rows = tuple(
        {
            "body_id": int(source_id),
            "force_x": float(force_x),
            "force_y": float(force_y),
        }
        for source_id, force_x, force_y in zip(source_ids, vector_x, vector_y)
    )
    force_sample, force_truncated = _truncate_rows(force_rows)

    validation: dict[str, object]
    validation_skipped = bool(skip_validation or len(bodies) > 2048)
    if validation_skipped:
        validation = {
            "skipped": True,
            "reason": "user_skip_validation" if skip_validation else "body_count_above_2048",
        }
    else:
        reference = rt.sum_aggregate_frontier_weighted_vectors_2d(
            bodies,
            bodies,
            tree_nodes,
            theta=theta,
            softening=app.SOFTENING,
        )
        expected_by_id = {
            int(row["source_id"]): (float(row["vector_x"]), float(row["vector_y"]))
            for row in reference["vector_sum_rows"]
        }
        max_abs_diff_x = max(
            abs(float(row["force_x"]) - expected_by_id[int(row["body_id"])][0])
            for row in force_rows
        )
        max_abs_diff_y = max(
            abs(float(row["force_y"]) - expected_by_id[int(row["body_id"])][1])
            for row in force_rows
        )
        validation = {
            "skipped": False,
            "compared_against": "sum_aggregate_frontier_weighted_vectors_2d_cpu_reference",
            "tolerance": 1.0e-7,
            "max_abs_diff_x": max_abs_diff_x,
            "max_abs_diff_y": max_abs_diff_y,
            "passed": max_abs_diff_x <= 1.0e-7 and max_abs_diff_y <= 1.0e-7,
            "reference_frontier_row_count": int(reference["summary"]["contribution_row_count"]),
        }
        if not bool(validation["passed"]):
            raise AssertionError("prepared aggregate-frontier vector output failed CPU validation")

    medians = _median_fields(
        repeats,
        (
            "frontier_traversal_seconds",
            "partner_seconds",
            "hot_seconds_native_plus_partner",
            "wall_seconds",
        ),
    )
    return {
        "app": "barnes_hut_force_app",
        "backend": "optix+partner",
        "mode": "prepared_aggregate_frontier_weighted_vector_optix",
        "partner": partner,
        "body_count": len(bodies),
        "theta": theta,
        "softening": app.SOFTENING,
        "bucket_size": bucket_size,
        "max_depth": max_depth,
        "tree_summary": tree["summary"],
        "run_phases": {
            "body_generation_sec": body_generation_sec,
            "tree_build_sec": tree_build_sec,
            "frontier_prepare_wall_sec": frontier_prepare_wall_sec,
            "vector_prepare_wall_sec": vector_prepare_wall_sec,
            "partner_prepare_seconds": float(getattr(prepared_vector, "prepare_seconds", 0.0)),
        },
        "capacity": {
            "initial_capacity": initial_capacity,
            "final_row_capacity": int(capacity),
            "frontier_capacity_multiplier": int(frontier_capacity_multiplier),
            "capacity_attempts": capacity_attempts,
        },
        "hot_repeats": repeats,
        "medians": medians,
        "vector_sum_summary": {
            "contract": str(vector_metadata["contract"]),
            "frontier_contract": rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_CONTRACT,
            "partner_contract": partner_contract,
            "source_count": int(vector_metadata["source_count"]),
            "frontier_row_count": int(vector_metadata["frontier_row_count"]),
            "aggregate_contribution_row_count": int(vector_metadata["aggregate_contribution_row_count"]),
            "exact_contribution_row_count": int(vector_metadata["exact_contribution_row_count"]),
            "checksum_force_x": sum(float(row["force_x"]) for row in force_rows),
            "checksum_force_y": sum(float(row["force_y"]) for row in force_rows),
            "force_rows": force_sample if force_output_mode == "full" else [],
            "force_rows_truncated": force_truncated if force_output_mode == "full" else True,
            "force_output_mode": force_output_mode,
        },
        "validation": validation,
        "claim_flags": {
            "same_frontier_contract": True,
            "explicit_partner_choice": True,
            "automatic_partner_selection_allowed": False,
            "native_engine_app_specific": False,
            "frontier_columns_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "prepared_lookup_columns_resident": True,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
        "boundary": (
            "Prepared RTDL/OptiX aggregate-frontier device columns plus explicit "
            f"{partner} Barnes-Hut weighted-vector partner continuation. The "
            "native engine remains app-agnostic; force-law math and partner "
            "choice remain app code. This is not an automatic partner dispatch, "
            "not an OptiX-vs-Embree comparison, and not public speedup wording."
        ),
    }


def run_benchmark(
    mode: str = "scope",
    *,
    body_count: int | None = None,
    theta: float = app.THETA,
    node_radius: float = app.NODE_DISCOVERY_RADIUS,
    node_topology: str = "one_level",
    bucket_size: int = 32,
    max_depth: int = 32,
    partner: str = "cupy",
    skip_validation: bool = False,
    require_rt_core: bool = False,
    query_repeat: int = 1,
    warmup: int = 0,
    force_output_mode: str = "full",
    frontier_row_capacity: int | None = None,
    frontier_capacity_multiplier: int = 700,
) -> dict[str, Any]:
    if mode not in MODES:
        raise ValueError(f"unsupported Barnes-Hut benchmark mode: {mode}")
    if mode == "scope":
        return scope_payload()
    if mode == "cpu_reference":
        return _annotate(
            app.run_app(
                "cpu_python_reference",
                theta=theta,
                body_count=body_count,
                output_mode="full",
            ),
            mode=mode,
            contract="one_level_candidate_rows_plus_python_opening_rule_force_reference",
            rt_core_accelerated=False,
        )
    if mode == "node_coverage_cpu_oracle":
        bodies = _make_bodies(body_count)
        nodes = app.build_one_level_quadtree(bodies)
        return _annotate(
            {
                "app": "barnes_hut_force_app",
                "backend": "cpu_python_reference",
                "body_count": len(bodies),
                "node_count": len(nodes),
                "node_radius": node_radius,
                "node_coverage": app.node_coverage_oracle(bodies, nodes, radius=node_radius),
                "boundary": "CPU node-coverage oracle only; no RT traversal or force-vector acceleration claim.",
            },
            mode=mode,
            contract="fixed_radius_node_coverage_cpu_oracle",
            rt_core_accelerated=False,
        )
    if mode == "rtdl_cpu_rows":
        return _annotate(
            app.run_app(
                "cpu",
                theta=theta,
                body_count=body_count,
                output_mode="candidate_summary",
            ),
            mode=mode,
            contract="generic_fixed_radius_candidate_rows_cpu_backend",
            rt_core_accelerated=False,
        )
    if mode == "embree_rows":
        return _annotate(
            app.run_app(
                "embree",
                theta=theta,
                body_count=body_count,
                output_mode="candidate_summary",
            ),
            mode=mode,
            contract="generic_fixed_radius_candidate_rows_embree_backend",
            rt_core_accelerated=False,
        )
    if mode == "opening_rows_cpu":
        return _annotate(
            _opening_rows_payload(body_count=body_count, theta=theta),
            mode=mode,
            contract=rt.AGGREGATE_OPENING_ROWS_2D_CONTRACT,
            rt_core_accelerated=False,
        )
    if mode == "bucketized_tree_cpu":
        return _annotate(
            _bucketized_tree_payload(
                body_count=body_count,
                bucket_size=bucket_size,
                max_depth=max_depth,
            ),
            mode=mode,
            contract=rt.AGGREGATE_BUCKETIZED_TREE_2D_CONTRACT,
            rt_core_accelerated=False,
        )
    if mode == "opening_frontier_bucketized_cpu":
        return _annotate(
            _opening_frontier_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
            ),
            mode=mode,
            contract=rt.AGGREGATE_TREE_OPENING_FRONTIER_2D_CONTRACT,
            rt_core_accelerated=False,
        )
    if mode == "aggregate_frontier_collect_bucketized_cpu":
        return _annotate(
            _aggregate_frontier_collect_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
            ),
            mode=mode,
            contract=rt.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT,
            rt_core_accelerated=False,
        )
    if mode == "aggregate_frontier_expanded_membership_cpu":
        if require_rt_core:
            raise ValueError("--require-rt-core requires aggregate_frontier_expanded_membership_optix")
        return _annotate(
            _aggregate_frontier_expanded_membership_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
                membership_backend="cpu",
                skip_validation=skip_validation,
            ),
            mode=mode,
            contract=(
                f"{rt.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT}+"
                f"{rt.EXPANDED_AABB_POINT_MEMBERSHIP_2D_CONTRACT}+"
                "python_opening_and_force_interpretation"
            ),
            rt_core_accelerated=False,
        )
    if mode == "aggregate_frontier_expanded_membership_embree":
        if require_rt_core:
            raise ValueError("--require-rt-core requires aggregate_frontier_expanded_membership_optix")
        return _annotate(
            _aggregate_frontier_expanded_membership_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
                membership_backend="embree",
                skip_validation=skip_validation,
            ),
            mode=mode,
            contract=(
                f"{rt.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT}+"
                f"{rt.EXPANDED_AABB_POINT_MEMBERSHIP_2D_CONTRACT}+"
                "python_opening_and_force_interpretation"
            ),
            rt_core_accelerated=False,
        )
    if mode == "aggregate_frontier_expanded_membership_optix":
        lowered_payload = _aggregate_frontier_expanded_membership_payload(
            body_count=body_count,
            theta=theta,
            bucket_size=bucket_size,
            max_depth=max_depth,
            membership_backend="optix",
            skip_validation=skip_validation,
        )
        if require_rt_core and not lowered_payload["membership_primitive"]["rt_core_accelerated"]:
            raise RuntimeError(
                "aggregate_frontier_expanded_membership_optix did not report "
                "RT-core acceleration for the generic membership primitive"
            )
        return _annotate(
            lowered_payload,
            mode=mode,
            contract=(
                f"{rt.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT}+"
                f"{rt.EXPANDED_AABB_POINT_MEMBERSHIP_2D_CONTRACT}+"
                "python_opening_and_force_interpretation"
            ),
            rt_core_accelerated=True,
        )
    if mode in {"aggregate_frontier_weighted_vector_cpu_host", "aggregate_frontier_weighted_vector_embree_host"}:
        if require_rt_core:
            raise ValueError("--require-rt-core requires prepared_aggregate_frontier_weighted_vector_optix")
        backend = "embree" if mode == "aggregate_frontier_weighted_vector_embree_host" else "cpu"
        return _annotate(
            _aggregate_frontier_weighted_vector_host_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
                backend=backend,
                skip_validation=skip_validation,
                force_output_mode=force_output_mode,
                frontier_row_capacity=frontier_row_capacity,
                frontier_capacity_multiplier=frontier_capacity_multiplier,
            ),
            mode=mode,
            contract=(
                f"{rt.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT}+"
                "generic_aggregate_frontier_collect_2d_host_weighted_vector_sum_baseline"
            ),
            rt_core_accelerated=False,
        )
    if mode in {
        "aggregate_frontier_weighted_vector_cpu_host_numba",
        "aggregate_frontier_weighted_vector_embree_host_numba",
    }:
        if require_rt_core:
            raise ValueError("--require-rt-core requires prepared_aggregate_frontier_weighted_vector_optix")
        backend = "embree" if mode == "aggregate_frontier_weighted_vector_embree_host_numba" else "cpu"
        return _annotate(
            _aggregate_frontier_weighted_vector_host_numba_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
                backend=backend,
                skip_validation=skip_validation,
                force_output_mode=force_output_mode,
                frontier_row_capacity=frontier_row_capacity,
                frontier_capacity_multiplier=frontier_capacity_multiplier,
                query_repeat=query_repeat,
                warmup=warmup,
            ),
            mode=mode,
            contract=(
                f"{rt.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT}+"
                "generic_aggregate_frontier_collect_2d_host_numba_cpu_weighted_vector_sum_baseline"
            ),
            rt_core_accelerated=False,
        )
    if mode == "force_contributions_bucketized_cpu":
        return _annotate(
            _force_contributions_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
            ),
            mode=mode,
            contract=rt.WEIGHTED_INVERSE_SQUARE_CONTRIBUTION_ROWS_2D_CONTRACT,
            rt_core_accelerated=False,
        )
    if mode == "bucketized_force_cpu":
        return _annotate(
            _bucketized_force_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
            ),
            mode=mode,
            contract=(
                f"{rt.AGGREGATE_BUCKETIZED_TREE_2D_CONTRACT}+"
                f"{rt.AGGREGATE_TREE_OPENING_FRONTIER_2D_CONTRACT}+"
                f"{rt.WEIGHTED_INVERSE_SQUARE_CONTRIBUTION_ROWS_2D_CONTRACT}+"
                f"{rt.GROUPED_VECTOR_SUM_ROWS_2D_CONTRACT}+python_force_interpretation"
            ),
            rt_core_accelerated=False,
        )
    if mode == "streamed_force_sum_bucketized_cpu":
        return _annotate(
            _streamed_force_sum_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
            ),
            mode=mode,
            contract=(
                f"{rt.AGGREGATE_BUCKETIZED_TREE_2D_CONTRACT}+"
                f"{rt.AGGREGATE_TREE_OPENING_FRONTIER_2D_CONTRACT}+"
                f"{rt.WEIGHTED_INVERSE_SQUARE_VECTOR_SUM_2D_CONTRACT}+python_force_interpretation"
            ),
            rt_core_accelerated=False,
        )
    if mode == "materialization_pressure_bucketized_cpu":
        return _annotate(
            _materialization_pressure_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
            ),
            mode=mode,
            contract=rt.VECTOR_SUM_MATERIALIZATION_PRESSURE_2D_CONTRACT,
            rt_core_accelerated=False,
        )
    if mode == "fused_frontier_force_sum_bucketized_cpu":
        return _annotate(
            _fused_frontier_force_sum_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
            ),
            mode=mode,
            contract=(
                f"{rt.AGGREGATE_BUCKETIZED_TREE_2D_CONTRACT}+"
                f"{rt.AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT}+"
                "python_force_interpretation"
            ),
            rt_core_accelerated=False,
        )
    if mode == "fused_frontier_force_sum_bucketized_cpu_numba":
        if require_rt_core:
            raise ValueError("--require-rt-core requires prepared_aggregate_frontier_weighted_vector_optix")
        return _annotate(
            _fused_frontier_force_sum_numba_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
                skip_validation=skip_validation,
                query_repeat=query_repeat,
                warmup=warmup,
                force_output_mode=force_output_mode,
            ),
            mode=mode,
            contract=(
                f"{rt.AGGREGATE_BUCKETIZED_TREE_2D_CONTRACT}+"
                "generic_aggregate_frontier_weighted_vector_sum_2d_numba_cpu_v1+"
                "explicit_numba_cpu_partner_force_interpretation"
            ),
            rt_core_accelerated=False,
        )
    if mode == "fused_frontier_force_sum_bucketized_numba_cuda":
        if require_rt_core:
            raise ValueError("--require-rt-core requires prepared_aggregate_frontier_weighted_vector_optix")
        return _annotate(
            _fused_frontier_force_sum_numba_cuda_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
                skip_validation=skip_validation,
                query_repeat=query_repeat,
                warmup=warmup,
                force_output_mode=force_output_mode,
            ),
            mode=mode,
            contract=(
                f"{rt.AGGREGATE_BUCKETIZED_TREE_2D_CONTRACT}+"
                f"{rt.AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CUDA_CONTRACT}+"
                "explicit_numba_cuda_partner_force_interpretation"
            ),
            rt_core_accelerated=False,
        )
    if mode == "prepared_execution_fused_vector_sum_numba_cuda":
        if require_rt_core:
            raise ValueError("--require-rt-core requires prepared_aggregate_frontier_weighted_vector_optix")
        return _annotate(
            _prepared_execution_fused_vector_sum_numba_cuda_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
                skip_validation=skip_validation,
                query_repeat=query_repeat,
                warmup=warmup,
                force_output_mode=force_output_mode,
            ),
            mode=mode,
            contract=(
                f"{rt.AGGREGATE_BUCKETIZED_TREE_2D_CONTRACT}+"
                f"{rt.AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CUDA_CONTRACT}+"
                "prepared_execution_session_runner+"
                "explicit_numba_cuda_partner_force_interpretation"
            ),
            rt_core_accelerated=False,
        )
    if mode == "native_fused_vector_sum_cuda_device":
        if require_rt_core:
            raise ValueError("--require-rt-core is not valid for native_fused_vector_sum_cuda_device")
        return _annotate(
            _native_fused_vector_sum_cuda_device_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
                skip_validation=skip_validation,
                query_repeat=query_repeat,
                warmup=warmup,
                force_output_mode=force_output_mode,
            ),
            mode=mode,
            contract=(
                f"{rt.AGGREGATE_BUCKETIZED_TREE_2D_CONTRACT}+"
                f"{rt.AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE_CONTRACT}+"
                "prepared_execution_session_runner+"
                "native_cuda_device_resident_force_interpretation"
            ),
            rt_core_accelerated=False,
        )
    if mode == "prepared_aggregate_frontier_weighted_vector_optix":
        return _annotate(
            _prepared_aggregate_frontier_weighted_vector_optix_payload(
                body_count=body_count,
                theta=theta,
                bucket_size=bucket_size,
                max_depth=max_depth,
                partner=partner,
                skip_validation=skip_validation,
                query_repeat=query_repeat,
                warmup=warmup,
                force_output_mode=force_output_mode,
                frontier_row_capacity=frontier_row_capacity,
                frontier_capacity_multiplier=frontier_capacity_multiplier,
            ),
            mode=mode,
            contract=(
                f"{rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_CONTRACT}+"
                f"{rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_CONTRACT}/"
                f"{rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CONTRACT}+"
                "explicit_partner_force_interpretation"
            ),
            rt_core_accelerated=True,
        )
    if mode in {"grouped_vector_sum_typed_stream_plan", "v2_8_grouped_vector_sum_plan"}:
        descriptor = (
            describe_barnes_hut_grouped_vector_sum_typed_stream(partner=partner)
            if mode == "grouped_vector_sum_typed_stream_plan"
            else describe_barnes_hut_v2_8_grouped_vector_sum_typed_stream(partner=partner)
        )
        return _annotate(
            descriptor,
            mode=mode,
            contract="generic_grouped_vector_sum_f64x2_typed_stream",
            rt_core_accelerated=False,
        )
    if mode == "embree_node_coverage_prepared":
        return _annotate(
            app.run_app(
                "embree",
                theta=theta,
                body_count=body_count,
                output_mode="candidate_summary",
                optix_summary_mode="node_coverage_prepared",
                node_radius=node_radius,
                node_topology=node_topology,
                node_depth=max_depth,
                skip_validation=skip_validation,
                query_repeat=query_repeat,
                warmup=warmup,
            ),
            mode=mode,
            contract="prepared_fixed_radius_node_coverage_threshold_decision_embree",
            rt_core_accelerated=False,
        )
    if mode == "optix_node_coverage_prepared":
        return _annotate(
            app.run_app(
                "optix",
                theta=theta,
                body_count=body_count,
                output_mode="candidate_summary",
                optix_summary_mode="node_coverage_prepared",
                node_radius=node_radius,
                node_topology=node_topology,
                node_depth=max_depth,
                skip_validation=skip_validation,
                require_rt_core=require_rt_core,
                query_repeat=query_repeat,
                warmup=warmup,
            ),
            mode=mode,
            contract="prepared_fixed_radius_node_coverage_threshold_decision_optix",
            rt_core_accelerated=True,
        )
    if mode == "partner_exact_force":
        if force_output_mode not in {"full", "force_summary"}:
            raise ValueError("force_output_mode must be 'full' or 'force_summary'")
        return _annotate(
            app.run_app(
                "partner_exact_force",
                theta=theta,
                body_count=body_count,
                output_mode=force_output_mode,
                partner=partner,
                skip_validation=skip_validation,
                query_repeat=query_repeat,
                warmup=warmup,
            ),
            mode=mode,
            contract="generic_weighted_point_pairwise_inverse_square_force_partner_reference",
            rt_core_accelerated=False,
        )
    raise AssertionError(f"unhandled mode: {mode}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="RT-BarnesHut-style RTDL research benchmark wrapper."
    )
    parser.add_argument("--mode", choices=MODES, default="scope")
    parser.add_argument("--body-count", type=int, default=None)
    parser.add_argument("--theta", type=float, default=app.THETA)
    parser.add_argument("--node-radius", type=float, default=app.NODE_DISCOVERY_RADIUS)
    parser.add_argument("--node-topology", choices=app.NODE_TOPOLOGIES, default="one_level")
    parser.add_argument("--bucket-size", type=int, default=32)
    parser.add_argument("--max-depth", type=int, default=32)
    parser.add_argument("--partner", choices=("torch", "cupy", "numba"), default="cupy")
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--require-rt-core", action="store_true")
    parser.add_argument("--repeat", type=int, default=1, help="Repeat hot prepared-query phase.")
    parser.add_argument("--warmup", type=int, default=0, help="Prepared-query warmup iterations to drop.")
    parser.add_argument(
        "--frontier-row-capacity",
        type=int,
        default=None,
        help="Explicit row capacity for prepared aggregate-frontier device-column mode.",
    )
    parser.add_argument(
        "--frontier-capacity-multiplier",
        type=int,
        default=700,
        help="Initial rows-per-body capacity multiplier for prepared aggregate-frontier probing.",
    )
    parser.add_argument(
        "--force-output-mode",
        choices=("full", "force_summary"),
        default="full",
        help="Output mode for partner_exact_force; force_summary suppresses per-body force rows.",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args(argv)

    payload = run_benchmark(
        args.mode,
        body_count=args.body_count,
        theta=args.theta,
        node_radius=args.node_radius,
        node_topology=args.node_topology,
        bucket_size=args.bucket_size,
        max_depth=args.max_depth,
        partner=args.partner,
        skip_validation=args.skip_validation,
        require_rt_core=args.require_rt_core,
        query_repeat=args.repeat,
        warmup=args.warmup,
        force_output_mode=args.force_output_mode,
        frontier_row_capacity=args.frontier_row_capacity,
        frontier_capacity_multiplier=args.frontier_capacity_multiplier,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
