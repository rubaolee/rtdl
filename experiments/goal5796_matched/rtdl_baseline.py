#!/usr/bin/env python3
"""RTDL public matched functional arm for Goal5796; no private imports."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess

from rtdsl.v4 import (
    AnyHitProtocolProof,
    BoundedRelationBatch,
    BoundedRelationProtocol,
    BoundedRelationStaticInput,
    TriangleReductionBatch,
    TriangleReductionMode,
    TriangleReductionProtocol,
    TriangleReductionStaticInput,
    V4Target,
    V4Toolchain,
    compile_protocol_program,
    standard_protocol_physical_plan,
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def proof_for(protocol, proof_path: Path) -> tuple[object, AnyHitProtocolProof]:
    plan = standard_protocol_physical_plan(protocol)
    return plan, AnyHitProtocolProof(
        callback_ir_sha256=plan.callback_ir_sha256,
        effect_digest=plan.effect_digest,
        proof_sha256=sha(proof_path),
        proof_kind="external_machine_checked_order_independence_v1",
    )


def run_relation_fixture(fixture, *, target, toolchain, proof_path: Path):
    protocol = BoundedRelationProtocol(
        capacity=int(fixture["capacity"]),
        minimum_overlap_f32=float(fixture["minimum_overlap"]),
    )
    plan, proof = proof_for(protocol, proof_path)
    verified = compile_protocol_program(
        protocol, physical_plan=plan, any_hit_proof=proof)
    materialized = verified.materialize(target=target, toolchain=toolchain)
    prepared = materialized.prepare(BoundedRelationStaticInput(
        tuple(tuple(row) for row in fixture["indexed"])))
    try:
        result = prepared.execute(BoundedRelationBatch(
            tuple(tuple(row) for row in fixture["sources"]),
            expected_rows=tuple(tuple(row) for row in fixture["expected_rows"]),
        ))
        lifecycle = prepared.lifecycle_receipt
    finally:
        prepared.close()
        prepared.close()
    output = [list(row) for row in result.output]
    if output != fixture["expected_rows"]:
        raise RuntimeError(f"RTDL relation mismatch for {fixture['id']}")
    return output, {
        "raw_event_count": int(result.details["raw_event_count"]),
        "duplicate_count": int(result.details["duplicate_count"]),
        "canonical_row_count": len(output),
        "program_identity_sha256": verified.identity.identity_sha256,
        "executable_identity_sha256": result.executable_identity.identity_sha256,
        "output_sha256": result.output_sha256,
        "physical_executor_classification": result.traversal_receipt[
            "physical_executor_classification"],
        "traversal_receipt": result.traversal_receipt,
        "lifecycle": lifecycle,
    }


def run_triangle(task, *, target, toolchain, proof_path: Path):
    protocol = TriangleReductionProtocol(TriangleReductionMode.WEIGHTED_HIT_COUNT)
    plan, proof = proof_for(protocol, proof_path)
    verified = compile_protocol_program(
        protocol, physical_plan=plan, any_hit_proof=proof)
    materialized = verified.materialize(target=target, toolchain=toolchain)
    vertices = tuple(tuple(row) for row in task["vertices"])
    triangles = tuple(
        (index, index + 1, index + 2) for index in range(0, len(vertices), 3))
    prepared = materialized.prepare(TriangleReductionStaticInput(
        vertices=vertices,
        triangles=triangles,
        primitive_metadata={},
        event_capacity=sum(int(v) for v in task["expected_per_ray"]),
    ))
    queries = tuple(
        (tuple(origin), tuple(direction), float(task["tmax"]))
        for origin, direction in task["rays"]
    )
    try:
        result = prepared.execute(TriangleReductionBatch(
            queries=queries,
            query_metadata={"query.weight": tuple(task["weights"])},
        ))
        lifecycle = prepared.lifecycle_receipt
    finally:
        prepared.close()
        prepared.close()
    per_ray = [int(v) for v in result.details["per_ray_u64"]]
    weighted = int(result.output)
    if per_ray != task["expected_per_ray"] or weighted != task["expected_weighted_sum"]:
        raise RuntimeError("RTDL triangle result mismatch")
    return per_ray, weighted, {
        "program_identity_sha256": verified.identity.identity_sha256,
        "executable_identity_sha256": result.executable_identity.identity_sha256,
        "output_sha256": result.output_sha256,
        "physical_executor_classification": result.traversal_receipt[
            "physical_executor_classification"],
        "traversal_receipt": result.traversal_receipt,
        "lifecycle": lifecycle,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    spec_bytes = args.spec.read_bytes()
    spec = json.loads(spec_bytes)
    target = V4Target.from_native(
        args.native, optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability)
    toolchain = V4Toolchain.current(
        compute_capability=tuple(map(int, args.compute_capability.split("."))),
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
    )
    relation_task = spec["tasks"]["CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"]
    relation_outputs = {}
    relation_receipts = {}
    for fixture in relation_task["fixtures"]:
        output, receipt = run_relation_fixture(
            fixture, target=target, toolchain=toolchain, proof_path=args.proof)
        relation_outputs[fixture["id"]] = output
        relation_receipts[fixture["id"]] = receipt
    overflow_fixture = dict(next(
        row for row in relation_task["fixtures"]
        if row["id"] == relation_task["overflow_witness"]["base_fixture_id"]))
    overflow_fixture["capacity"] = int(relation_task["overflow_witness"]["capacity"])
    try:
        run_relation_fixture(
            overflow_fixture, target=target, toolchain=toolchain,
            proof_path=args.proof)
    except Exception as error:
        if "capacity_overflow@rows" not in str(error):
            raise
        overflow_probe = {
            "status": "FAIL_CLOSED", "application_result_exposed": False,
            "exception_type": type(error).__name__, "exception": str(error),
            "capacity": overflow_fixture["capacity"],
            "expected_unique_row_count": relation_task["overflow_witness"]
                ["expected_unique_row_count"],
        }
    else:
        raise RuntimeError("RTDL relation overflow witness was accepted")
    triangle_task = spec["tasks"]["BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1"]
    per_ray, weighted, triangle_receipt = run_triangle(
        triangle_task, target=target, toolchain=toolchain, proof_path=args.proof)
    result = {
        "schema": "rtdl.goal5796.rtdl_public_matched_functional.v1",
        "status": "PASS", "arm": "D_RTDL_PUBLIC_CALLBACK_PROTOCOL",
        "spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
        "native_sha256": sha(args.native),
        "proof_carrier_sha256": sha(args.proof),
        "proof_semantic_revalidation_claimed": False,
        "outputs": {
            "bounded_relation": relation_outputs,
            "triangle": {"per_ray": per_ray, "weighted_sum": weighted},
        },
        "capacity_overflow_witness": overflow_probe,
        "receipts": {
            "bounded_relation": relation_receipts,
            "triangle": triangle_receipt,
        },
        "machine": {
            "hostname": platform.node(),
            "nvidia_smi": subprocess.run(
                ["nvidia-smi", "--query-gpu=name,driver_version,uuid,compute_cap",
                 "--format=csv,noheader"], check=True, text=True,
                capture_output=True).stdout.strip(),
        },
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
        "public_import_only": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(
        result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
