#!/usr/bin/env python3
"""Build and behaviorally execute the formal seven-role V4 callback route."""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import shutil
from pathlib import Path

from goal5749_nvrtc_wrapper_preflight import _compile
from rtdsl.v4_callback_artifact_cache import (
    V4CallbackProviderKey,
    load_callback_artifact,
    materialize_callback_artifact,
)
from rtdsl.v4_callback_abi import (
    compile_callback_abi,
    derive_compiler_recognized_any_hit_proof,
)
from rtdsl.v4_callback_frontend import compile_callback_source
from rtdsl.v4_callback_interpreter import RuntimeRecord, execute_callback_role
from rtdsl.v4_callback_ir import CallbackRole, EffectKind
from rtdsl.v4_callback_numba_codegen import (
    compile_formal_numba_leaf_isolated,
    generate_formal_numba_leaf,
)
from rtdsl.v4_callback_optix_wrapper_codegen import generate_trusted_optix_wrapper_v1
from rtdsl.v4_callback_ptx_composer import compose_callback_ptx
from rtdsl.v4_formal_optix_runtime import run_formal_callback_ptx
from tests.goal5750_v4_callback_ir_test import SOURCE, manifest
from tests.goal5751_v4_optix_wrapper_codegen_test import FORMAL_SOURCE


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cpu_reference(program, spheres, queries):
    query_view = tuple({"origin": tuple(origin), "tmax": tmax} for origin, tmax in queries)
    outputs = []
    role_counts = {role.value: 0 for role in CallbackRole}
    for query_index, _query in enumerate(queries):
        made = execute_callback_role(program, CallbackRole.MAKE_RAY, {
            "launch_id": query_index, "queries": query_view,
        })
        role_counts[CallbackRole.MAKE_RAY.value] += 1
        ray = {
            "origin": made.effect.field("origin"),
            "direction": made.effect.field("direction"),
            "tmin": made.effect.field("tmin"),
            "tmax": made.effect.field("tmax"),
        }
        payload = made.effect.field("payload")
        assert isinstance(payload, RuntimeRecord)
        hits: list[tuple[float, int]] = []
        for center, radius, item_id in spheres:
            primitive = {"center": tuple(center), "radius": radius, "item_id": item_id}
            bounded = execute_callback_role(
                program, CallbackRole.BOUNDS, {"primitive": primitive})
            role_counts[CallbackRole.BOUNDS.value] += 1
            if (bounded.effect.field("lower") != tuple(float(center[i]) - float(radius) for i in range(3))
                    or bounded.effect.field("upper") != tuple(float(center[i]) + float(radius) for i in range(3))):
                raise RuntimeError("CPU callback bounds disagree with admitted physical template")
            intersection = execute_callback_role(
                program, CallbackRole.INTERSECTION,
                {"ray": ray, "primitive": primitive},
            )
            role_counts[CallbackRole.INTERSECTION.value] += 1
            if intersection.effect.kind is EffectKind.HIT:
                hit = (float(intersection.effect.field("t")),
                       int(intersection.effect.field("hit_kind")))
                hits.append(hit)
                updated = execute_callback_role(
                    program, CallbackRole.ANY_HIT,
                    {"hit": {"t": hit[0], "hit_kind": hit[1]}, "payload": payload},
                )
                role_counts[CallbackRole.ANY_HIT.value] += 1
                payload = updated.effect.field("payload")
                assert isinstance(payload, RuntimeRecord)
        if hits:
            best_t = float(payload.field("best_t"))
            best_id = int(payload.field("best_id"))
            closest = execute_callback_role(
                program, CallbackRole.CLOSEST_HIT,
                {"hit": {"t": best_t, "hit_kind": best_id}, "payload": payload},
            )
            role_counts[CallbackRole.CLOSEST_HIT.value] += 1
            payload = closest.effect.field("payload")
        else:
            missed = execute_callback_role(
                program, CallbackRole.MISS, {"ray": ray, "payload": payload})
            role_counts[CallbackRole.MISS.value] += 1
            payload = missed.effect.field("payload")
        assert isinstance(payload, RuntimeRecord)
        final = execute_callback_role(
            program, CallbackRole.FINALIZE, {"payload": payload})
        role_counts[CallbackRole.FINALIZE.value] += 1
        value = final.effect.field("value")
        assert isinstance(value, RuntimeRecord)
        outputs.append((int(value.field("item_id")), float(value.field("distance"))))
    return tuple(outputs), role_counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--cc", choices=("61", "89"), required=True)
    parser.add_argument("--expected-python", required=True)
    parser.add_argument("--expected-numba", required=True)
    parser.add_argument("--expected-numpy", required=True)
    parser.add_argument("--expected-llvmlite", required=True)
    parser.add_argument("--cuda-toolkit", required=True)
    parser.add_argument("--optix-sdk", required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)

    verified = compile_callback_source(FORMAL_SOURCE, manifest())
    proof = derive_compiler_recognized_any_hit_proof(verified)
    proof_payload = proof.to_dict()
    proof_digest = proof.proof_sha256
    abi = compile_callback_abi(verified, any_hit_proof_authority=proof)
    leaves = []
    generated_leaves = []
    symbols = {}
    for role in CallbackRole:
        generated = generate_formal_numba_leaf(
            verified, abi, role, any_hit_proof_authority=proof)
        generated_leaves.append(generated)
        artifact = compile_formal_numba_leaf_isolated(
            generated,
            compute_capability=(int(args.cc[0]), int(args.cc[1])),
            accepted_ptx_isa=("8.0", "9.0"),
            allowed_external_symbols=frozenset(),
            expected_python_version=args.expected_python,
            expected_numba_version=args.expected_numba,
            expected_numpy_version=args.expected_numpy,
        )
        leaves.append(artifact)
        symbols[role.value] = artifact.abi_name
    wrapper = generate_trusted_optix_wrapper_v1(
        verified, abi, any_hit_proof_authority=proof)
    options = [
        f"-I{args.optix_include.resolve()}", f"-I{args.cuda_include.resolve()}",
        "-I/usr/include", "-I/usr/include/x86_64-linux-gnu", "--std=c++14",
        f"--gpu-architecture=compute_{args.cc}",
        "--relocatable-device-code=true", "-D__x86_64__=1", "-D__LP64__=1",
    ]
    wrapper_ptx, nvrtc_log = _compile(wrapper.source, options)
    composed = compose_callback_ptx(
        wrapper_ptx, leaves, exact_symbols_by_role=symbols)

    native_source = Path(os.environ["RTDL_OPTIX_LIB"]).resolve()
    if not native_source.is_file():
        raise RuntimeError("RTDL_OPTIX_LIB does not bind the executed native bytes")
    native_sha256 = _sha256(native_source)
    canonical_abi = json.dumps(
        abi.to_dict(), sort_keys=True, separators=(",", ":"), allow_nan=False)
    payload_layout_sha256 = hashlib.sha256(
        ("payload-layout-v1\0" + canonical_abi).encode()).hexdigest()
    attribute_layout_sha256 = hashlib.sha256(
        ("attribute-layout-v1\0" + canonical_abi).encode()).hexdigest()
    sbt_layout_sha256 = hashlib.sha256(json.dumps({
        "schema": "rtdl.v4.formal_sbt_layout.v1",
        "raygen_records": 1, "miss_records": 1, "hitgroup_records": 1,
        "hitgroup_programs": ["intersection", "any_hit", "closest_hit"],
        "trace_depth": 1, "payload_values": 10, "attribute_values": 2,
    }, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    provider_key = V4CallbackProviderKey(
        callback_ir_sha256=verified.ir_sha256,
        callback_abi_sha256=abi.abi_sha256,
        generated_source_sha256_by_role=tuple(
            (item.role.value, item.generated_source_sha256) for item in generated_leaves),
        leaf_ptx_sha256_by_role=tuple(
            (item.role, item.ptx_sha256) for item in leaves),
        wrapper_source_sha256=wrapper.source_sha256,
        wrapper_template="trusted_optix_wrapper_v1",
        physical_template=wrapper.physical_template,
        payload_layout_sha256=payload_layout_sha256,
        attribute_layout_sha256=attribute_layout_sha256,
        sbt_layout_sha256=sbt_layout_sha256,
        native_provider_sha256=native_sha256,
        target_compute_capability=(int(args.cc[0]), int(args.cc[1])),
        python_version=args.expected_python,
        numba_version=args.expected_numba,
        numpy_version=args.expected_numpy,
        llvmlite_version=args.expected_llvmlite,
        cuda_toolkit_version=args.cuda_toolkit,
        optix_sdk_version=args.optix_sdk,
        ptx_isa=composed.ptx_version,
        wrapper_numeric_policy="strict",
        leaf_numeric_policy="strict",
        composer_schema="rtdl.v4.composed_callback_ptx.v1",
        compile_options=tuple(options),
        link_options=("max_trace_depth=1", "payload_values=10", "attribute_values=2"),
    )
    construction_receipt = {
        "schema": "rtdl.goal5751.provider_construction_receipt.v1",
        "callback_ir_sha256": verified.ir_sha256,
        "callback_abi_sha256": abi.abi_sha256,
        "proof_sha256": proof_digest,
        "wrapper_ptx_sha256": hashlib.sha256(wrapper_ptx.encode()).hexdigest(),
        "composed_ptx_sha256": composed.ptx_sha256,
        "leaf_bindings": [list(item) for item in composed.leaf_bindings],
        "stripped_wrapper_externs": list(composed.stripped_wrapper_externs),
        "stripped_numba_environments": list(composed.stripped_numba_environments),
    }
    first_cache_result = materialize_callback_artifact(
        args.output / "PROVIDER_CACHE", provider_key,
        composed_ptx=composed.ptx, construction_receipt=construction_receipt)
    cached = load_callback_artifact(args.output / "PROVIDER_CACHE", provider_key)
    if first_cache_result.cache_hit or not cached.cache_hit:
        raise RuntimeError("provider cache create/load disposition is inconsistent")
    if cached.composed_ptx_sha256 != composed.ptx_sha256 or cached.composed_ptx != composed.ptx:
        raise RuntimeError("provider cache did not return the exact composed PTX")

    spheres = (
        ((5.0, 0.0, 0.0), 1.0, 9),
        ((5.0, 0.0, 0.0), 1.0, 3),
        ((8.0, 0.0, 0.0), 1.0, 5),
    )
    queries = (
        ((0.0, 0.0, 0.0), 100.0),
        ((0.0, 4.0, 0.0), 100.0),
    )
    expected, cpu_role_counts = _cpu_reference(verified, spheres, queries)
    semantic_digest = hashlib.sha256(json.dumps({
        "callback_ir_sha256": verified.ir_sha256,
        "callback_abi_sha256": abi.abi_sha256,
        "composed_ptx_sha256": cached.composed_ptx_sha256,
        "proof_sha256": proof_digest,
    }, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result = run_formal_callback_ptx(
        cached.composed_ptx, spheres=spheres, queries=queries,
        semantic_digest=semantic_digest, expected_output=expected)

    # Attack the physical-template boundary with a semantically well-formed
    # but wrong bounds callback.  Three primitive programs for query zero can
    # all attempt to claim the same per-launch error record; atomic first-error
    # ownership must produce one intact fail-closed record, never acceptance.
    invalid_source = FORMAL_SOURCE.replace(
        "lower=primitive.center - extent,",
        "lower=primitive.center,",
    )
    if invalid_source == FORMAL_SOURCE:
        raise RuntimeError("bounds attack did not alter the frozen source row")
    invalid_verified = compile_callback_source(invalid_source, manifest())
    invalid_proof = derive_compiler_recognized_any_hit_proof(invalid_verified)
    invalid_proof_digest = invalid_proof.proof_sha256
    invalid_abi = compile_callback_abi(
        invalid_verified, any_hit_proof_authority=invalid_proof)
    invalid_leaves = []
    invalid_symbols = {}
    for role in CallbackRole:
        generated = generate_formal_numba_leaf(
            invalid_verified, invalid_abi, role,
            any_hit_proof_authority=invalid_proof)
        artifact = compile_formal_numba_leaf_isolated(
            generated,
            compute_capability=(int(args.cc[0]), int(args.cc[1])),
            accepted_ptx_isa=("8.0", "9.0"),
            allowed_external_symbols=frozenset(),
            expected_python_version=args.expected_python,
            expected_numba_version=args.expected_numba,
            expected_numpy_version=args.expected_numpy,
        )
        invalid_leaves.append(artifact)
        invalid_symbols[role.value] = artifact.abi_name
    invalid_wrapper = generate_trusted_optix_wrapper_v1(
        invalid_verified, invalid_abi,
        any_hit_proof_authority=invalid_proof)
    invalid_wrapper_ptx, _ = _compile(invalid_wrapper.source, options)
    invalid_composed = compose_callback_ptx(
        invalid_wrapper_ptx, invalid_leaves,
        exact_symbols_by_role=invalid_symbols)
    invalid_semantic_digest = hashlib.sha256(json.dumps({
        "callback_ir_sha256": invalid_verified.ir_sha256,
        "callback_abi_sha256": invalid_abi.abi_sha256,
        "composed_ptx_sha256": invalid_composed.ptx_sha256,
        "proof_sha256": invalid_proof_digest,
    }, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    failure = run_formal_callback_ptx(
        invalid_composed.ptx, spheres=spheres, queries=queries,
        semantic_digest=invalid_semantic_digest,
        expected_device_error_code=0xFFFF000A,
    )

    (args.output / "TRUSTED_WRAPPER.cu").write_text(wrapper.source)
    (args.output / "TRUSTED_WRAPPER.ptx").write_text(wrapper_ptx)
    (args.output / "COMPOSED_FORMAL_CALLBACK.ptx").write_text(composed.ptx)
    (args.output / "NVRTC.log").write_text(nvrtc_log)
    (args.output / "ANY_HIT_PROOF.json").write_text(
        json.dumps(proof_payload, indent=2, sort_keys=True) + "\n")
    shutil.copy2(native_source, args.output / "librtdl_optix.so")
    payload = {
        "schema": "rtdl.goal5751.formal_device_validation.v1",
        "callback_ir_sha256": verified.ir_sha256,
        "callback_abi_sha256": abi.abi_sha256,
        "any_hit_proof_sha256": proof_digest,
        "wrapper_source_sha256": wrapper.source_sha256,
        "wrapper_ptx_sha256": hashlib.sha256(wrapper_ptx.encode()).hexdigest(),
        "composed_ptx_sha256": composed.ptx_sha256,
        "generated_provider": {
            "provider_identity": cached.provider_identity,
            "provider_key_sha256": provider_key.key_sha256,
            "artifact_manifest_sha256": cached.artifact_manifest_sha256,
            "construction_receipt_sha256": cached.construction_receipt_sha256,
            "first_materialization_cache_hit": first_cache_result.cache_hit,
            "executed_load_cache_hit": cached.cache_hit,
            "exact_cached_ptx_executed": True,
        },
        "leaf_bindings": [list(item) for item in composed.leaf_bindings],
        "cpu_output": [list(item) for item in expected],
        "device_output": [list(zip(result.output_ids, result.output_distance))[i]
                          for i in range(len(result.output_ids))],
        "cpu_role_counts": cpu_role_counts,
        "device_role_counters": list(result.role_counters),
        "device_status": list(result.launch_status),
        "bounds_attack": dataclasses.asdict(failure),
        "traversal_receipt": result.traversal_receipt,
        "output_sha256": result.output_sha256,
        "native_library_sha256": native_sha256,
        "claims": {
            "all_seven_numba_leaves_executed": True,
            "cpu_device_differential_exact": True,
            "behavioral_optix_traversal": True,
            "performance_claimed": False,
            "application_claimed": False,
        },
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n")
    manifest_rows = []
    for path in sorted(item for item in args.output.rglob("*") if item.is_file()):
        manifest_rows.append({
            "path": path.relative_to(args.output).as_posix(),
            "size": path.stat().st_size, "sha256": _sha256(path),
        })
    (args.output / "MANIFEST.json").write_text(
        json.dumps(manifest_rows, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
