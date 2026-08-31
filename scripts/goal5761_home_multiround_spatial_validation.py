#!/usr/bin/env python3
"""Home GPU functional closure for Goal5761/M3 (no performance timing)."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
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
from rtdsl.v4_callback_abi import AnyHitProofAuthority, compile_callback_abi
from rtdsl.v4_callback_ir import AnyHitDeliveryContract
from rtdsl.v4_multiround_spatial import (
    DistanceWindowBoundaryPolicy,
    MultiRoundSpatialSchema,
    RadiusGraphComponentsRequest,
    RankedDistanceWindowRequest,
    verify_multiround_spatial_schema,
)
from rtdsl.v4_multiround_spatial_optix_compiler import (
    compile_verified_multiround_spatial_executable,
)
from rtdsl.v4_multiround_spatial_optix_runtime import (
    execute_radius_graph_components,
    execute_ranked_distance_window,
    prepare_multiround_spatial_callback,
)
from rtdsl.v4_typed_physical_schema import (
    ReferenceTargetProfile,
    verify_typed_physical_schema,
)
from scripts.goal5761_m3_spatial_fixtures import (
    compile_callback,
    physical_schema,
)


ROOT = Path(__file__).resolve().parents[1]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def _proof(callback) -> AnyHitProofAuthority:
    return AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256=_digest({
            "kind": "goal5761_spatial_candidate_order_independence_v1",
            "callback": callback.ir_sha256,
            "source": _sha(ROOT / "scripts/goal5761_m3_spatial_fixtures.py"),
            "raw_device_order_semantic": False,
            "canonical_order": "lexicographic_u32_pair",
        }),
        proof_kind="external_machine_checked_order_independence_v1",
    )


def _authority(target, *, capacity=4096, maximum_rounds=8):
    callback = compile_callback()
    physical = verify_typed_physical_schema(
        callback, physical_schema(callback), target=target)
    relation_schema = BoundedRelationEmissionSchema(
        callback.ir_sha256, callback.effect_digest,
        physical.schema.schema_sha256, capacity,
        minimum_overlap_f32=0.0,
        duplicate_policy=RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP)
    relation = verify_bounded_relation_schema(physical, relation_schema)
    proof = _proof(callback)
    abi = compile_callback_abi(
        callback, any_hit_proof_authority=proof,
        physical_schema_authority=physical)
    relation_contract = compile_bounded_relation_contract(
        relation, abi_sha256=abi.abi_sha256)
    schema = MultiRoundSpatialSchema(
        relation_schema_sha256=relation.schema.schema_sha256,
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        physical_schema_sha256=physical.schema.schema_sha256,
        maximum_rounds=maximum_rounds,
        maximum_event_capacity=capacity)
    authority = verify_multiround_spatial_schema(
        relation, relation_contract, abi, schema,
        any_hit_proof_authority=proof)
    return authority, proof


def _executable(authority, proof, args):
    return compile_verified_multiround_spatial_executable(
        authority,
        any_hit_proof_authority=proof,
        compute_capability=(6, 1),
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        expected_python_version=platform.python_version(),
        expected_numba_version=numba.__version__,
        expected_numpy_version=np.__version__,
    )


def _rtnn(target, args):
    app = _module(
        "goal5761_rtnn_contract",
        ROOT / "Paper-reproduction-apps/rtnn-paper/rtdl3_action_migration.py")
    fixture = ROOT / "Paper-reproduction-apps/rtnn-paper/data/fixtures/goal5531_exact_knn"
    search = app._load_xyz(fixture / "search.xyz")
    queries = app._load_xyz(fixture / "queries.xyz")
    expected = app._expected_for_points(
        search, queries, k=4, min_distance=0.0, max_distance=3.0)
    authority, proof = _authority(target)
    executable, log = _executable(authority, proof, args)
    with prepare_multiround_spatial_callback(
        authority, executable,
        any_hit_proof_authority=proof,
        search_points=search,
        initial_radius=0.375,
        native_library_path=args.native,
    ) as owner:
        result = execute_ranked_distance_window(
            owner, queries,
            RankedDistanceWindowRequest(
                k=4, minimum_distance=0.0, maximum_distance=3.0,
                initial_radius=0.375, maximum_rounds=4,
                boundary_policy=DistanceWindowBoundaryPolicy.OPEN))
    matched = result.value == expected
    if not matched:
        raise RuntimeError(f"RTNN exact output mismatch: {result.value!r} != {expected!r}")
    return {
        "lane": "rtnn.point_selection.spatial_bounded.v1",
        "consumer": "frozen_paper_rtnn",
        "input": {
            "search_points_f32": np.asarray(search, dtype=np.float32).tolist(),
            "query_points_f32": np.asarray(queries, dtype=np.float32).tolist(),
            "k": 4,
            "minimum_distance": 0.0,
            "maximum_distance": 3.0,
            "initial_radius": 0.375,
            "maximum_rounds": 4,
            "boundary_policy": DistanceWindowBoundaryPolicy.OPEN.value,
        },
        "expected": expected,
        "actual": result.value,
        "exact_output_matched": matched,
        "candidate_rows": result.candidate_rows,
        "round_candidate_counts": result.round_candidate_counts,
        "role_counters_by_round": result.role_counters_by_round,
        "status_by_round": result.status_by_round,
        "telemetry": result.telemetry.__dict__,
        "traversal_receipt": result.traversal_receipt,
        "callback_ir_sha256": authority.relation.physical.callback.ir_sha256,
        "physical_schema_sha256": authority.relation.physical.schema.schema_sha256,
        "multiround_schema_sha256": authority.schema.schema_sha256,
        "authority_nonce": authority.authority_nonce,
        "executable_sha256": executable.executable_sha256,
        "composed_ptx_sha256": result.composed_ptx_sha256,
        "nvrtc_log_sha256": hashlib.sha256(log.encode()).hexdigest(),
        "output_sha256": result.output_sha256,
    }


def _rt_dbscan(target, args):
    app = _module(
        "goal5761_rt_dbscan_contract",
        ROOT / "Paper-reproduction-apps/rt-dbscan-paper/rtdl3_action_migration.py")
    path = ROOT / "Paper-reproduction-apps/rt-dbscan-paper/data/fixtures/border_noise3d_component_signature.csv"
    points = np.loadtxt(path, delimiter=",", comments="#", dtype=np.float32)
    expected = app._expected_from_points(points, epsilon=0.35, min_points=5)
    authority, proof = _authority(target)
    executable, log = _executable(authority, proof, args)
    with prepare_multiround_spatial_callback(
        authority, executable,
        any_hit_proof_authority=proof,
        search_points=points,
        initial_radius=0.35,
        native_library_path=args.native,
    ) as owner:
        result = execute_radius_graph_components(
            owner, RadiusGraphComponentsRequest(epsilon=0.35, min_points=5))
    actual = result.value
    matched = (
        actual["canonical_component_labels"]
        == expected["canonical_component_labels"]
        and actual["core_flags"] == expected["core_flags"])
    if not matched:
        raise RuntimeError(f"RT-DBSCAN exact output mismatch: {actual!r} != {expected!r}")
    return {
        "lane": "rt_dbscan.fixed_radius.prepared_spatial_components.v1",
        "consumer": "frozen_paper_rt_dbscan",
        "input": {
            "points_f32": np.asarray(points, dtype=np.float32).tolist(),
            "epsilon": 0.35,
            "min_points": 5,
        },
        "expected": {
            "canonical_component_labels": expected["canonical_component_labels"],
            "core_flags": expected["core_flags"],
        },
        "actual": {
            "edge_count": actual["edge_count"],
            "edge_rows": actual["edge_rows"],
            "neighbor_counts": actual["neighbor_counts"],
            "core_flags": actual["core_flags"],
            "canonical_component_labels": actual["canonical_component_labels"],
        },
        "exact_output_matched": matched,
        "candidate_rows": result.candidate_rows,
        "round_candidate_counts": result.round_candidate_counts,
        "role_counters_by_round": result.role_counters_by_round,
        "status_by_round": result.status_by_round,
        "telemetry": result.telemetry.__dict__,
        "traversal_receipt": result.traversal_receipt,
        "callback_ir_sha256": authority.relation.physical.callback.ir_sha256,
        "physical_schema_sha256": authority.relation.physical.schema.schema_sha256,
        "multiround_schema_sha256": authority.schema.schema_sha256,
        "authority_nonce": authority.authority_nonce,
        "executable_sha256": executable.executable_sha256,
        "composed_ptx_sha256": result.composed_ptx_sha256,
        "nvrtc_log_sha256": hashlib.sha256(log.encode()).hexdigest(),
        "output_sha256": result.output_sha256,
    }


def main():
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
    lanes = (_rtnn(target, args), _rt_dbscan(target, args))
    if len({row["callback_ir_sha256"] for row in lanes}) != 1 \
            or len({row["physical_schema_sha256"] for row in lanes}) != 1 \
            or len({row["multiround_schema_sha256"] for row in lanes}) != 1:
        raise RuntimeError("paper lanes did not share one generic M3 capability")
    if not all(row["exact_output_matched"] for row in lanes):
        raise RuntimeError("one or more paper lanes failed exact output")
    if not all(row["traversal_receipt"]["physical_executor_classification"]
               == "optix_traversal_observed" for row in lanes):
        raise RuntimeError("one or more paper lanes lacked behavioral OptiX traversal")
    result = {
        "schema": "rtdl.goal5761.home_multiround_spatial_result.v1",
        "goal": 5761,
        "scope": "functional_only_no_registered_performance_timing",
        "machine": _machine(),
        "native_library_sha256": native_sha,
        "lane_count": 2,
        "exact_output_count": 2,
        "behavioral_true_optix_count": 2,
        "shared_callback_and_multiround_schema": True,
        "persistent_gas_multiround_observed": (
            lanes[0]["telemetry"]["gas_build_count"] == 1
            and lanes[0]["telemetry"]["gas_refit_count"] >= 1
            and lanes[0]["telemetry"]["launch_count"] >= 2),
        "registered_performance_timing_count": 0,
        "lanes": lanes,
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output / "librtdl_optix.so").write_bytes(args.native.read_bytes())
    print(json.dumps({
        "result": str(args.output / "RESULT.json"),
        "exact": result["exact_output_count"],
        "behavioral": result["behavioral_true_optix_count"],
        "persistent": result["persistent_gas_multiround_observed"],
        "native": native_sha,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
