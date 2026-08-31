#!/usr/bin/env python3
"""Compose Goal5835 mapping evidence with the sealed Goal5834-B3 GPU result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .fixtures import load_registered_cases
from .independent_edge_capsule_oracle import edge_capsule_bits


B3_RAW_SHA256 = \
    "b50043e81713aacf6a70986a6e334789cbfeef17342ae97a8ae401ab1507f513"
B3_EVALUATION_SHA256 = \
    "786ebd4970dadf842c57aa6c08539694d0cdbe8a6b2f6672932029b5f19be02a"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path):
    return json.loads(path.read_text(
        encoding="utf-8", errors="strict"),
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-standard JSON constant {value}")))


def build_receipt(args):
    raw_path = args.raw_receipt.resolve(strict=True)
    evaluation_path = args.b3_evaluation.resolve(strict=True)
    if _sha(raw_path) != B3_RAW_SHA256 \
            or _sha(evaluation_path) != B3_EVALUATION_SHA256:
        raise RuntimeError("Goal5835 requires exact controlling B3 evidence")
    raw = _load(raw_path)
    evaluation = _load(evaluation_path)
    if raw.get("status") != "RAW_GPU_BITS_SEALED__UNEVALUATED" \
            or raw.get("lineage") != "B3" \
            or raw.get("expected_output_available_to_worker") is not False \
            or evaluation.get("status") != \
                "GOAL5834_B3_COMPLETE_REGISTERED_FIXTURE_EVALUATION" \
            or evaluation.get(
                "goal5835_registered_fixture_mapping_authorized") is not True:
        raise RuntimeError("Goal5834-B3 did not authorize this mapping")
    cases = load_registered_cases(
        args.fixture_authority, args.worker_inputs)
    raw_rows = {row["execution_id"]: row for row in raw["rows"]}
    evaluation_rows = {
        row["execution_id"]: row for row in evaluation["evaluation_rows"]}
    if set(raw_rows) != {row.execution_id for row in cases} \
            or set(evaluation_rows) != set(raw_rows):
        raise RuntimeError("Goal5835/B3 execution identities differ")

    mapped_rows = []
    for case in cases:
        static, batch = case.problem.public_inputs()
        if static.commitment_sha256 != \
                case.public_static_input_commitment_sha256 \
                or batch.commitment_sha256 != \
                    case.public_query_commitment_sha256:
            raise RuntimeError(f"public mapping drift at {case.execution_id}")
        frozen_static = {
            "control_points": [list(row) for row in static.control_points],
            "widths": list(static.widths),
            "segment_indices": list(static.segment_indices),
            "application_ids": list(static.application_ids),
        }
        frozen_queries = [[list(start), list(end)]
                          for start, end in batch.queries]
        if frozen_static != case.frozen_static_input \
                or frozen_queries != [[list(start), list(end)]
                                      for start, end in case.frozen_queries]:
            raise RuntimeError(f"mapped bytes differ at {case.execution_id}")
        capsules = tuple((
            row.start, row.end, row.radius, row.application_id,
        ) for row in case.problem.swept_segments)
        edges = tuple((row.start, row.end)
                      for row in case.problem.obstacle_edges)
        oracle_bits, oracle_collision = edge_capsule_bits(capsules, edges)
        observed = raw_rows[case.execution_id]
        prior = evaluation_rows[case.execution_id]
        observed_bits = tuple(observed["per_query_hit"])
        if observed_bits != oracle_bits \
                or observed["collision_host_or"] != oracle_collision \
                or prior["match"] is not True:
            raise RuntimeError(f"Goal5835 mapping mismatch at {case.execution_id}")
        mapped_rows.append({
            "family_id": case.family_id,
            "execution_id": case.execution_id,
            "identity_projection": case.problem.identity_projection(),
            "static_input_commitment_sha256": static.commitment_sha256,
            "query_commitment_sha256": batch.commitment_sha256,
            "per_edge_hit": list(observed_bits),
            "collision": observed["collision_host_or"],
            "raw_gpu_bit_vector_commitment_sha256":
                observed["raw_gpu_bit_vector_commitment_sha256"],
            "true_optix": observed["traversal_receipt"].get(
                "physical_executor_classification") ==
                "optix_traversal_observed",
            "independent_active_set_oracle_match": True,
        })

    root = Path(__file__).resolve().parent
    sources = []
    for name in (
        "bounded_piecewise_linear_core.py", "fixtures.py",
        "independent_edge_capsule_oracle.py", "README.md",
    ):
        path = root / name
        sources.append({
            "path": str(path), "bytes": path.stat().st_size,
            "sha256": _sha(path),
        })
    return {
        "schema": "rtdl.goal5835.sui_derived_edge_crossing_mapping.v1",
        "status": "GOAL5835_COMPLETE_BOUNDED_SUI_DERIVED_EDGE_CROSSING_MAPPING",
        "paper_app_status": "NOT_A_PAPER_APP",
        "source_relation": "SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES",
        "implemented_predicate":
            "OR_over_registered_obstacle_edges_of_OR_over_swept_sphere_capsules",
        "full_rt_ccd_implemented": False,
        "fixture_family_count": 10,
        "mapped_execution_count": 11,
        "matching_execution_count": len(mapped_rows),
        "generalization_exam_count": 0,
        "new_goal5835_gpu_launch_count": 0,
        "inherited_b3_true_optix_launch_count":
            raw["total_successful_application_launch_count"],
        "registered_performance_timing_count": 0,
        "fixture_authority_sha256": _sha(
            args.fixture_authority.resolve(strict=True)),
        "worker_inputs_sha256": _sha(args.worker_inputs.resolve(strict=True)),
        "b3_raw_gpu_receipt_sha256": _sha(raw_path),
        "b3_independent_evaluation_sha256": _sha(evaluation_path),
        "application_sources": sources,
        "rows": mapped_rows,
        "method_boundaries": [
            "edge_crossing_only__face_interior_without_edge_contact_is_miss",
            "start_inside_and_initial_overlap_not_implemented",
            "near_tangent_and_near_parallel_inputs_excluded",
            "exact_time_of_impact_and_collided_identity_not_exposed",
            "author_code_same_input_comparison_deferred_to_goal5836",
            "modern_rtx_functional_gate_deferred_to_goal5836"
        ],
        "goal5836_authorized": False,
        "performance_claimed": False,
        "paper_app_claimed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-authority", required=True, type=Path)
    parser.add_argument("--worker-inputs", required=True, type=Path)
    parser.add_argument("--raw-receipt", required=True, type=Path)
    parser.add_argument("--b3-evaluation", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = build_receipt(args)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": result["status"],
        "matching_execution_count": result["matching_execution_count"],
        "mapped_execution_count": result["mapped_execution_count"],
        "paper_app_status": result["paper_app_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
