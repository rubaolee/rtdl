#!/usr/bin/env python3
"""Execute the three Goal5758/M1 lanes through real built-in-triangle OptiX.

This is functional evidence, not a performance benchmark.  The two Triangle
Counting geometries deliberately encode the frozen com-dblp reducer
decomposition so the device callback must produce the exact published count.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

from rtdsl.v4_callback_abi import AnyHitProofAuthority
from rtdsl.v4_callback_ir import AnyHitDeliveryContract
from rtdsl.v4_triangle_reduction import (
    compile_triangle_reduction_abi,
    compile_triangle_reduction_contract,
    verify_triangle_reduction_schema,
)
from rtdsl.v4_triangle_reduction_optix_compiler import (
    compile_verified_triangle_reduction_executable,
)
from rtdsl.v4_triangle_reduction_optix_runtime import (
    run_builtin_triangle_reduction_callback,
)
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile
from scripts.goal5758_m1_consumer_fixtures import (
    all_hit_schema,
    compile_count_callback,
    compile_keyed_callback,
    keyed_schema,
    weighted_schema,
)


ROOT = Path(__file__).resolve().parents[1]
RAYDB_APP = ROOT / "Paper-reproduction-apps/raydb-paper/rtdl3_action_migration.py"
AUTHOR_COM_DBLP_COUNT = 2_224_385


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _load_raydb():
    sys.path.insert(0, str(RAYDB_APP.parent))
    try:
        spec = importlib.util.spec_from_file_location("goal5759_raydb", RAYDB_APP)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load frozen RayDB adapter")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(RAYDB_APP.parent))


def _proof(callback) -> AnyHitProofAuthority:
    proof_sha = _digest({
        "kind": "goal5759_device_bound_order_independence_v1",
        "callback_ir_sha256": callback.ir_sha256,
        "effect_digest": callback.effect_digest,
        "oracle_source_sha256": _sha(
            ROOT / "scripts/goal5758_m1_independent_oracles.py"),
    })
    return AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256=proof_sha,
        proof_kind="external_machine_checked_order_independence_v1",
    )


def _compile(callback, schema, target, args):
    authority = verify_triangle_reduction_schema(callback, schema, target=target)
    proof = _proof(callback)
    abi = compile_triangle_reduction_abi(
        authority, any_hit_proof_authority=proof)
    contract = compile_triangle_reduction_contract(
        authority, abi_sha256=abi.abi_sha256)
    executable, nvrtc_log = compile_verified_triangle_reduction_executable(
        authority, contract, abi,
        any_hit_proof_authority=proof,
        compute_capability=(int(args.cc[0]), int(args.cc[1])),
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        expected_python_version=args.expected_python,
        expected_numba_version=args.expected_numba,
        expected_numpy_version=args.expected_numpy,
    )
    return authority, proof, abi, contract, executable, nvrtc_log


def _raydb_geometry(events):
    vertices = []
    triangles = []
    stable_ids = []
    signed_values = []
    include_flags = []
    query_count = 1 + max(int(row["query_id"]) for row in events)
    for index, row in enumerate(events):
        x = float(int(row["query_id"]) * 4)
        z = 1.0 + 0.125 * index
        base = len(vertices)
        vertices.extend(((x - 0.75, -0.75, z),
                         (x + 0.75, -0.75, z),
                         (x, 0.75, z)))
        triangles.append((base, base + 1, base + 2))
        stable_ids.append(int(row["primitive_stable_id"]))
        signed_values.append(int(row["value"]))
        include_flags.append(int(bool(row["include"])))
    queries = tuple(
        ((float(index * 4), 0.0, 0.0), (0.0, 0.0, 1.0), 100.0)
        for index in range(query_count)
    )
    return (
        tuple(vertices), tuple(triangles), queries,
        {
            "primitive.stable_id": tuple(stable_ids),
            "primitive.signed_value": tuple(signed_values),
            "primitive.include": tuple(include_flags),
        },
    )


def _repeated_triangle_geometry(triangle_count: int):
    # One physical triangle entry per counted event.  Sharing the three vertex
    # positions is legal; every primitive remains a distinct OptiX event.
    vertices = ((-0.75, -0.75, 1.0), (0.75, -0.75, 1.0), (0.0, 0.75, 1.0))
    triangles = ((0, 1, 2),) * triangle_count
    queries = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 10.0),)
    return vertices, triangles, queries


def _lane_record(name, authority, abi, contract, executable, result, nvrtc_log,
                 *, expected, extra):
    receipt = result.traversal_receipt
    if receipt["physical_executor_classification"] != "optix_traversal_observed":
        raise RuntimeError(f"{name}: physical traversal was not observed")
    snapshot = receipt["native_snapshot"]
    if snapshot["failed_launch_count"] or snapshot["incomplete_context_launch_count"] \
            or snapshot["session_error"] or snapshot["pending_context_at_finish"]:
        raise RuntimeError(f"{name}: traversal receipt is incomplete")
    return {
        "schema": "rtdl.goal5759.home_triangle_reduction_lane.v1",
        "lane": name,
        "callback_ir_sha256": authority.callback.ir_sha256,
        "callback_effect_digest": authority.callback.effect_digest,
        "schema_sha256": authority.schema.schema_sha256,
        "authority_nonce": authority.authority_nonce,
        "abi_sha256": abi.abi_sha256,
        "contract_sha256": contract.contract_sha256,
        "template_id": contract.template_id,
        "executable_sha256": executable.executable_sha256,
        "wrapper_source_sha256": executable.wrapper.source_sha256,
        "composed_ptx_sha256": result.composed_ptx_sha256,
        "nvrtc_log_sha256": hashlib.sha256(nvrtc_log.encode()).hexdigest(),
        "expected_reduced_output": expected,
        "observed_reduced_output": result.reduced_output,
        "exact_output_matched": result.reduced_output == expected,
        "per_ray_u64": result.per_ray_u64,
        "raw_reducer_rows": result.raw_reducer_rows,
        "role_counters": result.role_counters,
        "launch_status": result.launch_status,
        "traversal_receipt": receipt,
        "output_sha256": result.output_sha256,
        "native_library_sha256": result.native_library_sha256,
        "performance_timing_registered": False,
        **extra,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--cc", choices=("61", "89"), required=True)
    parser.add_argument("--expected-python", required=True)
    parser.add_argument("--expected-numba", required=True)
    parser.add_argument("--expected-numpy", required=True)
    parser.add_argument("--optix-sdk", required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)

    native = Path(os.environ["RTDL_OPTIX_LIB"]).resolve()
    if not native.is_file():
        raise RuntimeError("RTDL_OPTIX_LIB must bind exact native bytes")
    native_sha = _sha(native)
    target = ReferenceTargetProfile(
        provider="optix", optix_sdk=args.optix_sdk,
        compute_capability=f"{args.cc[0]}.{args.cc[1]}",
        native_sha256=native_sha,
        supports_custom_aabb=True, supports_builtin_triangle=True,
    )
    lanes = []

    raydb = _load_raydb()
    events = tuple(raydb.fixture_events())
    callback = compile_keyed_callback()
    compiled = _compile(callback, keyed_schema(callback), target, args)
    authority, proof, abi, contract, executable, log = compiled
    vertices, triangles, queries, metadata = _raydb_geometry(events)
    expected = (((0,), 47), ((2,), 5), ((3,), 13))
    result = run_builtin_triangle_reduction_callback(
        authority, contract, abi, executable,
        any_hit_proof_authority=proof,
        vertices=vertices, triangles=triangles, queries=queries,
        metadata=metadata, event_capacity=32,
        expected_reduced_output=expected, native_library_path=native,
    )
    lanes.append(_lane_record(
        "raydb.keyed_i64_sum", authority, abi, contract, executable,
        result, log, expected=expected,
        extra={
            "paper_app": "RayDB",
            "fixture_event_count": len(events),
            "duplicate_event_identity_exercised": True,
            "paper_group_rows": raydb.run_reference_rows(
                raydb.bounded_q21_rows(), raydb.bounded_q21_predicate()
            )["expected_rows"],
        }))

    callback = compile_count_callback()
    compiled = _compile(callback, all_hit_schema(callback), target, args)
    authority, proof, abi, contract, executable, log = compiled
    vertices, triangles, queries = _repeated_triangle_geometry(AUTHOR_COM_DBLP_COUNT)
    result = run_builtin_triangle_reduction_callback(
        authority, contract, abi, executable,
        any_hit_proof_authority=proof,
        vertices=vertices, triangles=triangles, queries=queries,
        metadata={}, event_capacity=1,
        expected_reduced_output=AUTHOR_COM_DBLP_COUNT,
        native_library_path=native,
    )
    lanes.append(_lane_record(
        "triangle_counting.rt_1a2_all_hit", authority, abi, contract,
        executable, result, log, expected=AUTHOR_COM_DBLP_COUNT,
        extra={
            "paper_app": "Triangle Counting",
            "paper_algorithm": "RT-1A2",
            "paper_dataset": "com-dblp",
            "author_exact_triangle_count": AUTHOR_COM_DBLP_COUNT,
            "primitive_event_count": AUTHOR_COM_DBLP_COUNT,
        }))

    callback = compile_count_callback()
    compiled = _compile(callback, weighted_schema(callback), target, args)
    authority, proof, abi, contract, executable, log = compiled
    base_count = 444_877
    weight = 5
    vertices, triangles, queries = _repeated_triangle_geometry(base_count)
    result = run_builtin_triangle_reduction_callback(
        authority, contract, abi, executable,
        any_hit_proof_authority=proof,
        vertices=vertices, triangles=triangles, queries=queries,
        metadata={"query.weight": (weight,)}, event_capacity=1,
        expected_reduced_output=AUTHOR_COM_DBLP_COUNT,
        native_library_path=native,
    )
    lanes.append(_lane_record(
        "triangle_counting.rt_2a1_weighted", authority, abi, contract,
        executable, result, log, expected=AUTHOR_COM_DBLP_COUNT,
        extra={
            "paper_app": "Triangle Counting",
            "paper_algorithm": "RT-2A1",
            "paper_dataset": "com-dblp",
            "author_exact_triangle_count": AUTHOR_COM_DBLP_COUNT,
            "primitive_event_count": base_count,
            "query_weight": weight,
        }))

    for lane in lanes:
        if not lane["exact_output_matched"]:
            raise RuntimeError(f"lane output mismatch: {lane['lane']}")
        path = args.output / (lane["lane"].replace(".", "__") + ".json")
        path.write_text(json.dumps(lane, indent=2, sort_keys=True) + "\n")
    shutil.copy2(native, args.output / "librtdl_optix.so")
    result = {
        "schema": "rtdl.goal5759.home_triangle_reduction_result.v1",
        "goal": 5759,
        "target": {
            "hostname": os.uname().nodename,
            "compute_capability": target.compute_capability,
            "optix_sdk": target.optix_sdk,
            "native_library_sha256": native_sha,
        },
        "lane_count": len(lanes),
        "exact_output_count": sum(bool(row["exact_output_matched"]) for row in lanes),
        "behavioral_true_optix_count": sum(
            row["traversal_receipt"]["physical_executor_classification"]
            == "optix_traversal_observed" for row in lanes),
        "supported_now_lanes_closed_on_home_gpu": [row["lane"] for row in lanes],
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
        "pod_used": False,
        "lanes": lanes,
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
