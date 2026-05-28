from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.v2_0.apps.simulation import rtdl_barnes_hut_force_app as app


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
    "force_contributions_bucketized_cpu",
    "bucketized_force_cpu",
    "streamed_force_sum_bucketized_cpu",
    "materialization_pressure_bucketized_cpu",
    "fused_frontier_force_sum_bucketized_cpu",
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
            "generic_expanded_aabb_point_membership_rows_2d_v1",
            "generic_weighted_inverse_square_contribution_rows_2d_v1",
            "generic_grouped_vector_sum_rows_2d_v1",
            "generic_weighted_inverse_square_vector_sum_2d_v1",
            "generic_vector_sum_materialization_pressure_2d_v1",
            "generic_aggregate_frontier_weighted_vector_sum_2d_v1",
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


def run_benchmark(
    mode: str = "scope",
    *,
    body_count: int | None = None,
    theta: float = app.THETA,
    node_radius: float = app.NODE_DISCOVERY_RADIUS,
    bucket_size: int = 32,
    max_depth: int = 32,
    partner: str = "cupy",
    skip_validation: bool = False,
    require_rt_core: bool = False,
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
    if mode == "embree_node_coverage_prepared":
        return _annotate(
            app.run_app(
                "embree",
                theta=theta,
                body_count=body_count,
                output_mode="candidate_summary",
                optix_summary_mode="node_coverage_prepared",
                node_radius=node_radius,
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
                require_rt_core=require_rt_core,
            ),
            mode=mode,
            contract="prepared_fixed_radius_node_coverage_threshold_decision_optix",
            rt_core_accelerated=True,
        )
    if mode == "partner_exact_force":
        return _annotate(
            app.run_app(
                "partner_exact_force",
                theta=theta,
                body_count=body_count,
                output_mode="full",
                partner=partner,
                skip_validation=skip_validation,
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
    parser.add_argument("--bucket-size", type=int, default=32)
    parser.add_argument("--max-depth", type=int, default=32)
    parser.add_argument("--partner", choices=("torch", "cupy"), default="cupy")
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--require-rt-core", action="store_true")
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args(argv)

    payload = run_benchmark(
        args.mode,
        body_count=args.body_count,
        theta=args.theta,
        node_radius=args.node_radius,
        bucket_size=args.bucket_size,
        max_depth=args.max_depth,
        partner=args.partner,
        skip_validation=args.skip_validation,
        require_rt_core=args.require_rt_core,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
