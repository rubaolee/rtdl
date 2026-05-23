from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
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
    "force_contributions_bucketized_cpu",
    "bucketized_force_cpu",
    "streamed_force_sum_bucketized_cpu",
    "materialization_pressure_bucketized_cpu",
    "fused_frontier_force_sum_bucketized_cpu",
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
            "prepared_fixed_radius_node_coverage_threshold_decision",
            "generic_aggregate_opening_rows_2d_v1",
            "generic_bucketized_aggregate_tree_2d_v1",
            "generic_aggregate_tree_opening_frontier_2d_v1",
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
