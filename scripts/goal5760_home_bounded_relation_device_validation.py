#!/usr/bin/env python3
"""Functional-only Home GPU closure for Goal5760/M2."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess

import numba
import numpy

from rtdsl.v4_bounded_relation import (
    BoundedRelationError,
    BoundedRelationEmissionSchema,
    compile_bounded_relation_contract,
    verify_bounded_relation_schema,
)
from rtdsl.v4_bounded_relation_optix_compiler import (
    compile_verified_bounded_relation_executable,
)
from rtdsl.v4_bounded_relation_optix_runtime import (
    run_bounded_relation_callback,
)
from rtdsl.v4_callback_abi import AnyHitProofAuthority, compile_callback_abi
from rtdsl.v4_callback_ir import AnyHitDeliveryContract
from rtdsl.v4_typed_physical_schema import (
    ReferenceTargetProfile,
    verify_typed_physical_schema,
)
from scripts.goal5760_m2_consumer_fixtures import (
    compile_callback,
    exact_relation,
    physical_schema,
    polygon_set_jaccard_candidate_boxes,
)


ROOT = Path(__file__).resolve().parents[1]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _proof(callback) -> AnyHitProofAuthority:
    return AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256=_digest({
            "kind": "goal5760_relation_order_independence_v1",
            "callback": callback.ir_sha256,
            "oracle_source": _sha(
                ROOT / "scripts/goal5760_m2_consumer_fixtures.py"),
            "raw_order_semantic": False,
            "canonical_order": "lexicographic_u32_pair",
        }),
        proof_kind="external_machine_checked_order_independence_v1",
    )


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


def _lane(name, *, indexed, sources, threshold, capacity, target, args,
          expect_overflow=False):
    callback = compile_callback()
    physical = verify_typed_physical_schema(
        callback, physical_schema(callback), target=target)
    schema = BoundedRelationEmissionSchema(
        callback.ir_sha256, callback.effect_digest,
        physical.schema.schema_sha256, capacity,
        minimum_overlap_f32=threshold)
    authority = verify_bounded_relation_schema(physical, schema)
    proof = _proof(callback)
    abi = compile_callback_abi(
        callback, any_hit_proof_authority=proof,
        physical_schema_authority=physical)
    contract = compile_bounded_relation_contract(
        authority, abi_sha256=abi.abi_sha256)
    executable, log = compile_verified_bounded_relation_executable(
        authority, contract, abi,
        any_hit_proof_authority=proof,
        compute_capability=(6, 1),
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        expected_python_version=platform.python_version(),
        expected_numba_version=numba.__version__,
        expected_numpy_version=numpy.__version__,
    )
    expected = exact_relation(sources, indexed, minimum_overlap=threshold)
    try:
        result = run_bounded_relation_callback(
            authority, contract, abi, executable,
            any_hit_proof_authority=proof,
            indexed_boxes=indexed, source_boxes=sources,
            expected_rows=expected,
            native_library_path=args.native)
    except BoundedRelationError as exc:
        if not expect_overflow or exc.code != "capacity_overflow":
            raise
        return {
            "schema": "rtdl.goal5760.home_bounded_relation_attack.v1",
            "attack": name,
            "expected_disposition": "fail_closed_reject_complete_result",
            "observed_code": exc.code,
            "observed_path": exc.path,
            "observed_message": exc.message,
            "passed": True,
            "capacity": capacity,
            "expected_relation_cardinality": len(expected),
            "callback_ir_sha256": callback.ir_sha256,
            "contract_sha256": contract.contract_sha256,
            "executable_sha256": executable.executable_sha256,
        }
    if expect_overflow:
        raise RuntimeError("capacity overflow attack unexpectedly returned a result")
    receipt = result.traversal_receipt
    snapshot = receipt["native_snapshot"]
    if snapshot["successful_launch_count"] != 2 \
            or snapshot["complete_context_launch_count"] != 2 \
            or snapshot["failed_launch_count"] \
            or snapshot["incomplete_context_launch_count"] \
            or snapshot["pending_context_at_finish"] \
            or snapshot["session_error"] \
            or receipt["physical_executor_classification"] \
            != "optix_traversal_observed":
        raise RuntimeError(f"{name}: traversal receipt is incomplete")
    if len(result.role_counters) != 7 or not all(
            result.role_counters[index] > 0 for index in (0, 1, 2, 3, 4, 6)):
        raise RuntimeError(
            f"{name}: fixture did not exercise every non-miss role: "
            f"{result.role_counters!r}")
    return {
        "schema": "rtdl.goal5760.home_bounded_relation_lane.v1",
        "lane": name,
        "consumer_class": (
            "paper_librts" if name.startswith("librts.")
            else "existing_non_librts_polygon_set_jaccard_application"),
        "callback_ir_sha256": callback.ir_sha256,
        "physical_schema_sha256": physical.schema.schema_sha256,
        "relation_schema_sha256": schema.schema_sha256,
        "authority_nonce": authority.authority_nonce,
        "abi_sha256": abi.abi_sha256,
        "contract_sha256": contract.contract_sha256,
        "executable_sha256": executable.executable_sha256,
        "wrapper_source_sha256": executable.wrapper.source_sha256,
        "composed_ptx_sha256": result.composed_ptx_sha256,
        "nvrtc_log_sha256": hashlib.sha256(log.encode()).hexdigest(),
        "minimum_overlap_f32": threshold,
        "capacity": capacity,
        "indexed_boxes": indexed,
        "source_boxes": sources,
        "expected_rows": expected,
        "observed_rows": result.rows,
        "raw_rows": result.raw_rows,
        "raw_event_count": result.raw_event_count,
        "duplicate_count": result.duplicate_count,
        "exact_output_matched": result.rows == expected,
        "role_counters": result.role_counters,
        "launch_status": result.launch_status,
        "traversal_receipt": receipt,
        "output_sha256": result.output_sha256,
    }


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
    machine = _machine()
    target = ReferenceTargetProfile(
        provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
        native_sha256=native_sha,
        supports_custom_aabb=True, supports_builtin_triangle=True)
    indexed = (
        (0.0, 0.0, 2.0, 2.0, 10),
        (4.0, 4.0, 6.0, 6.0, 20),
        (2.0, 0.0, 3.0, 1.0, 30),
        (12.0, 12.0, 13.0, 13.0, 40),
    )
    sources = (
        (1.0, 1.0, 2.5, 2.5, 100),
        (5.0, 5.0, 7.0, 7.0, 200),
        (20.0, 20.0, 21.0, 21.0, 300),
    )
    polygon_indexed, polygon_sources = polygon_set_jaccard_candidate_boxes()
    lanes = (
        _lane("librts.aabb_index.prepared_query_2d.v1",
              indexed=indexed, sources=sources, threshold=0.0,
              capacity=64, target=target, args=args),
        _lane("librts.aabb_overlap.filter_bounded_emit_2d.v1",
              indexed=indexed, sources=sources, threshold=0.75,
              capacity=64, target=target, args=args),
        _lane("polygon_set_jaccard.aabb_candidate_stage.v1",
              indexed=polygon_indexed, sources=polygon_sources, threshold=0.0,
              capacity=64, target=target, args=args),
    )
    aggregate_role_counters = tuple(
        sum(int(lane["role_counters"][index]) for lane in lanes)
        for index in range(7))
    if not all(value > 0 for value in aggregate_role_counters):
        raise RuntimeError(
            "the three-lane cohort did not exercise all seven roles: "
            f"{aggregate_role_counters!r}")
    overflow_attack = _lane(
        "capacity_overflow_partial_rows_are_not_authority",
        indexed=indexed, sources=sources, threshold=0.0,
        capacity=1, target=target, args=args, expect_overflow=True)
    result = {
        "schema": "rtdl.goal5760.home_bounded_relation_result.v1",
        "goal": 5760,
        "scope": "functional_only_no_registered_performance_timing",
        "machine": machine,
        "native_library_sha256": native_sha,
        "lane_count": len(lanes),
        "exact_output_count": sum(row["exact_output_matched"] for row in lanes),
        "behavioral_true_optix_count": sum(
            row["traversal_receipt"]["physical_executor_classification"]
            == "optix_traversal_observed" for row in lanes),
        "one_shared_callback_ir": len({row["callback_ir_sha256"] for row in lanes}) == 1,
        "one_shared_physical_schema": len(
            {row["physical_schema_sha256"] for row in lanes}) == 1,
        "aggregate_role_counters": aggregate_role_counters,
        "all_seven_roles_exercised_across_cohort": True,
        "registered_performance_timing_count": 0,
        "overflow_attack": overflow_attack,
        "lanes": lanes,
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output / "librtdl_optix.so").write_bytes(args.native.read_bytes())
    print(json.dumps({
        "result": str(args.output / "RESULT.json"),
        "exact": result["exact_output_count"],
        "behavioral": result["behavioral_true_optix_count"],
        "native": native_sha,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
