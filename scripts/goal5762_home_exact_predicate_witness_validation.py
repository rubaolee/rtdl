#!/usr/bin/env python3
"""Home GPU functional closure for Goal5762/M4 (zero performance timing)."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess

import numba
import numpy as np

from rtdsl.v4_bounded_relation import (
    BoundedRelationEmissionSchema,
    RelationDuplicatePolicy,
    compile_bounded_relation_contract,
    verify_bounded_relation_schema,
)
from rtdsl.v4_bounded_relation_optix_compiler import (
    compile_verified_bounded_relation_executable,
)
from rtdsl.v4_bounded_relation_optix_runtime import run_bounded_relation_callback
from rtdsl.v4_callback_abi import AnyHitProofAuthority, compile_callback_abi
from rtdsl.v4_callback_ir import AnyHitDeliveryContract
from rtdsl.v4_exact_predicate_witness import (
    CandidateProducerKind,
    ExactPartnerAlgebra,
    ExactPredicateWitnessSchema,
    directed_point_location_sos,
    exact_segment_aabb_projection,
    exact_vertical_ray_aabb_projection,
    global_max_nearest_witness_f32,
    grouped_exact_segment_pair_counts,
    verify_exact_predicate_witness_schema,
)
from rtdsl.v4_multiround_spatial import (
    DistanceWindowBoundaryPolicy,
    MultiRoundSpatialSchema,
    RankedDistanceWindowRequest,
    verify_multiround_spatial_schema,
)
from rtdsl.v4_multiround_spatial_optix_compiler import (
    compile_verified_multiround_spatial_executable,
)
from rtdsl.v4_multiround_spatial_optix_runtime import (
    execute_ranked_distance_window,
    prepare_multiround_spatial_callback,
)
from rtdsl.v4_typed_physical_schema import (
    ReferenceTargetProfile,
    verify_typed_physical_schema,
)
from scripts.goal5760_m2_consumer_fixtures import (
    compile_callback as compile_box_callback,
    exact_relation,
    physical_schema as box_physical_schema,
)
from scripts.goal5761_m3_spatial_fixtures import (
    compile_callback as compile_spatial_callback,
    physical_schema as spatial_physical_schema,
)
from scripts.goal5762_m4_exact_fixtures import (
    point_location_fixture,
    segment_pair_fixture,
    xhd_fixture,
)


ROOT = Path(__file__).resolve().parents[1]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _machine():
    line = subprocess.run([
        "nvidia-smi", "--query-gpu=name,driver_version,uuid,compute_cap",
        "--format=csv,noheader"], check=True, text=True,
        capture_output=True).stdout.strip()
    fields = tuple(item.strip() for item in line.split(","))
    if len(fields) != 4 or fields[3] != "6.1":
        raise RuntimeError(f"unexpected Home GPU identity: {line!r}")
    return {"gpu": fields[0], "driver": fields[1], "uuid": fields[2],
            "compute_capability": fields[3], "hostname": platform.node()}


def _proof(callback, label: str, fixture_path: str) -> AnyHitProofAuthority:
    return AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256=_digest({
            "kind": f"goal5762_{label}_candidate_order_independence_v1",
            "callback": callback.ir_sha256,
            "fixture_source": _sha(ROOT / fixture_path),
            "raw_device_order_semantic": False,
            "canonical_order": "lexicographic_u32_pair",
        }),
        proof_kind="external_machine_checked_order_independence_v1",
    )


def _relation_authority(target, *, capacity=4096):
    callback = compile_box_callback()
    physical = verify_typed_physical_schema(
        callback, box_physical_schema(callback), target=target)
    relation_schema = BoundedRelationEmissionSchema(
        callback.ir_sha256, callback.effect_digest,
        physical.schema.schema_sha256, capacity,
        minimum_overlap_f32=0.0,
        duplicate_policy=RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP)
    relation = verify_bounded_relation_schema(physical, relation_schema)
    proof = _proof(
        callback, "exact_predicate",
        "scripts/goal5762_m4_exact_fixtures.py")
    abi = compile_callback_abi(
        callback, any_hit_proof_authority=proof,
        physical_schema_authority=physical)
    contract = compile_bounded_relation_contract(
        relation, abi_sha256=abi.abi_sha256)
    schema = ExactPredicateWitnessSchema(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        physical_schema_sha256=physical.schema.schema_sha256,
        source_authority_nonce=relation.authority_nonce,
        producer_kind=CandidateProducerKind.CLOSED_AABB_RELATION,
        partner_algebras=(
            ExactPartnerAlgebra.DIRECTED_POINT_LOCATION_SOS_I46,
            ExactPartnerAlgebra.SEGMENT_PAIR_GROUPED_COUNT_SOS_I46,
        ),
        maximum_candidate_capacity=capacity)
    exact = verify_exact_predicate_witness_schema(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        physical_schema_sha256=physical.schema.schema_sha256,
        source_authority_nonce=relation.authority_nonce,
        schema=schema)
    return relation, contract, abi, proof, exact


def _spatial_authority(target, *, capacity=4096):
    callback = compile_spatial_callback()
    physical = verify_typed_physical_schema(
        callback, spatial_physical_schema(callback), target=target)
    relation_schema = BoundedRelationEmissionSchema(
        callback.ir_sha256, callback.effect_digest,
        physical.schema.schema_sha256, capacity,
        minimum_overlap_f32=0.0,
        duplicate_policy=RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP)
    relation = verify_bounded_relation_schema(physical, relation_schema)
    proof = _proof(
        callback, "global_witness",
        "scripts/goal5762_m4_exact_fixtures.py")
    abi = compile_callback_abi(
        callback, any_hit_proof_authority=proof,
        physical_schema_authority=physical)
    relation_contract = compile_bounded_relation_contract(
        relation, abi_sha256=abi.abi_sha256)
    multiround_schema = MultiRoundSpatialSchema(
        relation_schema_sha256=relation.schema.schema_sha256,
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        physical_schema_sha256=physical.schema.schema_sha256,
        maximum_rounds=1, maximum_event_capacity=capacity)
    multiround = verify_multiround_spatial_schema(
        relation, relation_contract, abi, multiround_schema,
        any_hit_proof_authority=proof)
    schema = ExactPredicateWitnessSchema(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        physical_schema_sha256=physical.schema.schema_sha256,
        source_authority_nonce=multiround.authority_nonce,
        producer_kind=CandidateProducerKind.SPHERE_NEAREST,
        partner_algebras=(
            ExactPartnerAlgebra.GLOBAL_MAX_NEAREST_WITNESS_F32,),
        maximum_candidate_capacity=capacity)
    exact = verify_exact_predicate_witness_schema(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        physical_schema_sha256=physical.schema.schema_sha256,
        source_authority_nonce=multiround.authority_nonce,
        schema=schema)
    return multiround, proof, exact


def _xhd(target, args):
    sources, targets = xhd_fixture()
    authority, proof, exact_authority = _spatial_authority(target)
    executable, log = compile_verified_multiround_spatial_executable(
        authority, any_hit_proof_authority=proof,
        compute_capability=(6, 1), optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        expected_python_version=platform.python_version(),
        expected_numba_version=numba.__version__,
        expected_numpy_version=np.__version__)
    maximum_distance = 32.0
    with prepare_multiround_spatial_callback(
        authority, executable, any_hit_proof_authority=proof,
        search_points=targets, initial_radius=maximum_distance,
        native_library_path=args.native,
    ) as owner:
        nearest = execute_ranked_distance_window(
            owner, sources,
            RankedDistanceWindowRequest(
                k=1, minimum_distance=0.0,
                maximum_distance=maximum_distance,
                initial_radius=maximum_distance, maximum_rounds=1,
                boundary_policy=DistanceWindowBoundaryPolicy.CLOSED))
    actual = global_max_nearest_witness_f32(
        nearest.value,
        expected_query_ids=tuple(range(len(sources))))
    all_pairs = []
    for query_id, query in enumerate(sources):
        candidates = []
        for item_id, item in enumerate(targets):
            delta = np.subtract(query, item, dtype=np.float32)
            squared = np.multiply(delta, delta, dtype=np.float32)
            d2 = np.add(np.add(squared[0], squared[1], dtype=np.float32),
                        squared[2], dtype=np.float32)
            candidates.append((float(d2), item_id))
        d2, item_id = min(candidates, key=lambda row: (row[0], row[1]))
        all_pairs.append((query_id, item_id, 1, d2))
    expected = global_max_nearest_witness_f32(
        all_pairs, expected_query_ids=tuple(range(len(sources))))
    if actual != expected:
        raise RuntimeError(f"X-HD witness mismatch: {actual!r} != {expected!r}")
    return {
        "lane": "x_hd.nearest_state.cell_mbr_exact_witness.v1",
        "physical_fragment": "v4_sphere_nearest_candidate_relation",
        "paper_algorithm_name_preserved_but_physical_fragment_not_claimed_cell_mbr": True,
        "input": {
            "source_points_f32": sources.tolist(),
            "target_points_f32": targets.tolist(),
        },
        "candidate_rows": nearest.candidate_rows,
        "nearest_rows": nearest.value,
        "actual": actual,
        "expected": expected,
        "exact_output_matched": True,
        "exact_authority": exact_authority.schema.to_dict(),
        "exact_authority_nonce": exact_authority.authority_nonce,
        "producer_authority_nonce": authority.authority_nonce,
        "callback_ir_sha256": authority.relation.physical.callback.ir_sha256,
        "physical_schema_sha256": authority.relation.physical.schema.schema_sha256,
        "executable_sha256": executable.executable_sha256,
        "composed_ptx_sha256": nearest.composed_ptx_sha256,
        "nvrtc_log_sha256": hashlib.sha256(log.encode()).hexdigest(),
        "telemetry": nearest.telemetry.__dict__,
        "role_counters_by_round": nearest.role_counters_by_round,
        "status_by_round": nearest.status_by_round,
        "traversal_receipt": nearest.traversal_receipt,
        "output_sha256": _digest(actual),
    }


def _rayjoin(target, args):
    relation, contract, abi, proof, exact_authority = _relation_authority(target)
    point_executable, point_log = compile_verified_bounded_relation_executable(
        relation, contract, abi, any_hit_proof_authority=proof,
        compute_capability=(6, 1), optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        expected_python_version=platform.python_version(),
        expected_numba_version=numba.__version__,
        expected_numpy_version=np.__version__)
    # Executable authorities are deliberately single-use.  The two frozen
    # RayJoin lanes therefore receive separate compiler products even though
    # they share the same verified producer schema.
    pair_executable, pair_log = compile_verified_bounded_relation_executable(
        relation, contract, abi, any_hit_proof_authority=proof,
        compute_capability=(6, 1), optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        expected_python_version=platform.python_version(),
        expected_numba_version=numba.__version__,
        expected_numpy_version=np.__version__)

    points, point_segments = point_location_fixture()
    point_indexed = exact_segment_aabb_projection(point_segments)
    point_sources = exact_vertical_ray_aabb_projection(points, point_segments)
    point_candidates_expected = exact_relation(
        point_sources, point_indexed, minimum_overlap=0.0)
    point_candidates = run_bounded_relation_callback(
        relation, contract, abi, point_executable,
        any_hit_proof_authority=proof,
        indexed_boxes=point_indexed, source_boxes=point_sources,
        expected_rows=point_candidates_expected,
        native_library_path=args.native)
    point_actual = directed_point_location_sos(
        points, point_segments, point_candidates.rows,
        query_map_id=0, capacity=contract.capacity)
    point_expected_rows = (
        (200, 10, 100),
        (201, 10, 100),
        (202, 0, 0xFFFFFFFF),
        (203, 10, 100),
        (204, 30, 102),
    )
    if point_actual["rows"] != point_expected_rows:
        raise RuntimeError(
            f"RayJoin point-location mismatch: {point_actual['rows']!r} != "
            f"{point_expected_rows!r}")

    left, right = segment_pair_fixture()
    right_boxes = exact_segment_aabb_projection(right)
    left_boxes = exact_segment_aabb_projection(left)
    pair_candidates_expected = exact_relation(
        left_boxes, right_boxes, minimum_overlap=0.0)
    pair_candidates = run_bounded_relation_callback(
        relation, contract, abi, pair_executable,
        any_hit_proof_authority=proof,
        indexed_boxes=right_boxes, source_boxes=left_boxes,
        expected_rows=pair_candidates_expected,
        native_library_path=args.native)
    pair_actual = grouped_exact_segment_pair_counts(
        left, right, pair_candidates.rows, capacity=contract.capacity)
    # The paper's asymmetric SoS assigns the (302,402) endpoint touch to this
    # left/right orientation; it is not an ordinary inclusive predicate.
    expected_pairs = ((300, 400), (302, 402))
    expected_groups = ((7, 70, 1), (8, 71, 1))
    if pair_actual["exact_pairs"] != expected_pairs \
            or pair_actual["grouped_counts"] != expected_groups:
        raise RuntimeError(f"RayJoin exact pair mismatch: {pair_actual!r}")

    common = {
        "exact_authority": exact_authority.schema.to_dict(),
        "exact_authority_nonce": exact_authority.authority_nonce,
        "producer_authority_nonce": relation.authority_nonce,
        "callback_ir_sha256": relation.physical.callback.ir_sha256,
        "physical_schema_sha256": relation.physical.schema.schema_sha256,
    }
    point_lane = {
        **common,
        "lane": "rayjoin.planar_map.directed_segment_point_location_2d.v1",
        "input": {
            "points": [row.__dict__ for row in points],
            "segments": [row.__dict__ for row in point_segments],
            "source_boxes": [list(row) for row in point_sources],
            "indexed_boxes": [list(row) for row in point_indexed],
            "query_map_id": 0,
            "candidate_capacity": contract.capacity,
        },
        "candidate_rows": point_candidates.rows,
        "actual": point_actual,
        "expected_rows": point_expected_rows,
        "exact_output_matched": True,
        "role_counters": point_candidates.role_counters,
        "launch_status": point_candidates.launch_status,
        "traversal_receipt": point_candidates.traversal_receipt,
        "composed_ptx_sha256": point_candidates.composed_ptx_sha256,
        "executable_sha256": point_executable.executable_sha256,
        "nvrtc_log_sha256": hashlib.sha256(point_log.encode()).hexdigest(),
        "output_sha256": _digest(point_actual["rows"]),
    }
    pair_lane = {
        **common,
        "lane": "rayjoin.planar_map.segment_pair_grouped_range_exact_count_2d.v1",
        "input": {
            "left_segments": [row.__dict__ for row in left],
            "right_segments": [row.__dict__ for row in right],
            "source_boxes": [list(row) for row in left_boxes],
            "indexed_boxes": [list(row) for row in right_boxes],
            "candidate_capacity": contract.capacity,
        },
        "candidate_rows": pair_candidates.rows,
        "actual": pair_actual,
        "expected_exact_pairs": expected_pairs,
        "expected_grouped_counts": expected_groups,
        "exact_output_matched": True,
        "role_counters": pair_candidates.role_counters,
        "launch_status": pair_candidates.launch_status,
        "traversal_receipt": pair_candidates.traversal_receipt,
        "composed_ptx_sha256": pair_candidates.composed_ptx_sha256,
        "executable_sha256": pair_executable.executable_sha256,
        "nvrtc_log_sha256": hashlib.sha256(pair_log.encode()).hexdigest(),
        "output_sha256": _digest({
            "pairs": pair_actual["exact_pairs"],
            "groups": pair_actual["grouped_counts"],
        }),
    }
    return point_lane, pair_lane


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    native_sha = _sha(args.native)
    target = ReferenceTargetProfile(
        provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
        native_sha256=native_sha,
        supports_custom_aabb=True, supports_builtin_triangle=True)
    lanes = (_xhd(target, args), *_rayjoin(target, args))
    if any(not row["exact_output_matched"] for row in lanes):
        raise RuntimeError("M4 lane mismatch")
    if any(row["traversal_receipt"]["physical_executor_classification"]
           != "optix_traversal_observed" for row in lanes):
        raise RuntimeError("M4 lane lacks behavioral OptiX traversal")
    result = {
        "schema": "rtdl.goal5762.home_exact_predicate_witness_result.v1",
        "goal": 5762,
        "scope": "functional_only_no_registered_performance_timing",
        "machine": _machine(),
        "native_library_sha256": native_sha,
        "lane_count": 3,
        "exact_output_count": 3,
        "behavioral_true_optix_count": 3,
        "registered_performance_timing_count": 0,
        "native_or_app_source_changed": False,
        "candidate_rows_trusted_as_final_output": False,
        "exact_predicate_or_witness_recomputed_after_traversal": True,
        "lanes": lanes,
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output / "librtdl_optix.so").write_bytes(args.native.read_bytes())
    print(json.dumps({
        "result": str(args.output / "RESULT.json"),
        "exact": 3, "behavioral": 3, "native": native_sha,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
