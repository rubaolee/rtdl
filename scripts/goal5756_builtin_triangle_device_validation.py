#!/usr/bin/env python3
"""Compile and behaviorally execute the Goal5756 built-in-triangle route."""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import os
from pathlib import Path
import shutil

from rtdsl.v4_callback_abi import compile_callback_abi
from rtdsl.v4_callback_interpreter import RuntimeRecord, execute_callback_role
from rtdsl.v4_callback_ir import CallbackRole
from rtdsl.v4_triangle_optix_compiler import (
    compile_verified_triangle_executable,
    consume_verified_triangle_executable,
)
from rtdsl.v4_triangle_optix_runtime import run_builtin_triangle_callback
from rtdsl.v4_triangle_optix_wrapper_codegen import (
    generate_trusted_optix_triangle_wrapper_v1,
)
from rtdsl.v4_typed_physical_schema import (
    ReferenceTargetProfile,
    default_reference_templates,
    lower_canonical_reference_plan,
    verify_typed_physical_schema,
)
from tests.goal5755_v4_typed_physical_schema_test import (
    BACK_HIT_KIND,
    FRONT_HIT_KIND,
    orientation_authority,
    triangle_schema,
    verified_callback,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cpu_reference(callback, vertices, triangles, front, back, queries):
    query_view = tuple({
        "origin": tuple(map(float, origin)),
        "direction": tuple(map(float, direction)),
        "tmax": float(tmax),
    } for origin, direction, tmax in queries)
    outputs = []
    hit_rows = []
    role_counts = {role.value: 0 for role in CallbackRole}
    for query_index, (origin, direction, tmax) in enumerate(queries):
        made = execute_callback_role(callback, CallbackRole.MAKE_RAY, {
            "launch_id": query_index,
            "queries": query_view,
        })
        role_counts[CallbackRole.MAKE_RAY.value] += 1
        payload = made.effect.field("payload")
        assert isinstance(payload, RuntimeRecord)
        best = None
        for primitive_index, triangle in enumerate(triangles):
            p0, p1, p2 = (vertices[index] for index in triangle)
            edge1 = tuple(p1[axis] - p0[axis] for axis in range(3))
            edge2 = tuple(p2[axis] - p0[axis] for axis in range(3))
            cross = (
                direction[1] * edge2[2] - direction[2] * edge2[1],
                direction[2] * edge2[0] - direction[0] * edge2[2],
                direction[0] * edge2[1] - direction[1] * edge2[0],
            )
            determinant = sum(edge1[axis] * cross[axis] for axis in range(3))
            if abs(determinant) < 1.0e-8:
                continue
            inverse = 1.0 / determinant
            offset = tuple(origin[axis] - p0[axis] for axis in range(3))
            u = sum(offset[axis] * cross[axis] for axis in range(3)) * inverse
            if u < 0.0 or u > 1.0:
                continue
            qvec = (
                offset[1] * edge1[2] - offset[2] * edge1[1],
                offset[2] * edge1[0] - offset[0] * edge1[2],
                offset[0] * edge1[1] - offset[1] * edge1[0],
            )
            v = sum(direction[axis] * qvec[axis] for axis in range(3)) * inverse
            if v < 0.0 or u + v > 1.0:
                continue
            t = sum(edge2[axis] * qvec[axis] for axis in range(3)) * inverse
            if t < 0.0 or t > tmax:
                continue
            normal = (
                edge1[1] * edge2[2] - edge1[2] * edge2[1],
                edge1[2] * edge2[0] - edge1[0] * edge2[2],
                edge1[0] * edge2[1] - edge1[1] * edge2[0],
            )
            hit_kind = (
                FRONT_HIT_KIND
                if sum(normal[axis] * direction[axis] for axis in range(3)) < 0.0
                else BACK_HIT_KIND
            )
            candidate = (t, primitive_index, hit_kind, (u, v))
            if best is None or candidate[:2] < best[:2]:
                best = candidate
        if best is None:
            ray = {
                "origin": tuple(map(float, origin)),
                "direction": tuple(map(float, direction)),
                "tmin": 0.0,
                "tmax": float(tmax),
            }
            missed = execute_callback_role(callback, CallbackRole.MISS, {
                "ray": ray,
                "payload": payload,
            })
            role_counts[CallbackRole.MISS.value] += 1
            payload = missed.effect.field("payload")
            hit_rows.append(None)
        else:
            t, primitive_index, hit_kind, barycentrics = best
            closest = execute_callback_role(callback, CallbackRole.CLOSEST_HIT, {
                "hit": {
                    "t": t,
                    "primitive_index": primitive_index,
                    "hit_kind": hit_kind,
                    "barycentrics": barycentrics,
                },
                "payload": payload,
                "first_side": tuple(front),
                "second_side": tuple(back),
            })
            role_counts[CallbackRole.CLOSEST_HIT.value] += 1
            payload = closest.effect.field("payload")
            hit_rows.append({
                "t": t,
                "primitive_index": primitive_index,
                "hit_kind": hit_kind,
                "barycentrics": list(barycentrics),
            })
        assert isinstance(payload, RuntimeRecord)
        final = execute_callback_role(callback, CallbackRole.FINALIZE, {
            "payload": payload,
        })
        role_counts[CallbackRole.FINALIZE.value] += 1
        value = final.effect.field("value")
        assert isinstance(value, RuntimeRecord)
        outputs.append((
            int(value.field("cell_id")),
            int(value.field("neighbor_id")),
            int(value.field("face_id")),
        ))
    return tuple(outputs), tuple(hit_rows), role_counts


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

    native_path = Path(os.environ["RTDL_OPTIX_LIB"]).resolve()
    if not native_path.is_file():
        raise RuntimeError("RTDL_OPTIX_LIB must bind the executed native bytes")
    native_sha = _sha(native_path)
    callback = verified_callback()
    orientation = orientation_authority(callback)
    target = ReferenceTargetProfile(
        provider="optix",
        optix_sdk=args.optix_sdk,
        compute_capability=f"{args.cc[0]}.{args.cc[1]}",
        native_sha256=native_sha,
        supports_custom_aabb=True,
        supports_builtin_triangle=True,
    )
    authority = verify_typed_physical_schema(
        callback,
        triangle_schema(callback),
        target=target,
        orientation_authorities={orientation.authority_sha256: orientation},
    )
    plan = lower_canonical_reference_plan(authority, default_reference_templates())
    abi = compile_callback_abi(
        callback, physical_schema_authority=authority)
    executable, nvrtc_log = compile_verified_triangle_executable(
        authority,
        plan,
        abi,
        compute_capability=(int(args.cc[0]), int(args.cc[1])),
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        expected_python_version=args.expected_python,
        expected_numba_version=args.expected_numba,
        expected_numpy_version=args.expected_numpy,
    )
    generated_leaves = executable.generated_leaves
    compiled_leaves = executable.compiled_leaves
    wrapper = executable.wrapper
    wrapper_ptx = executable.wrapper_ptx
    composed = executable.composed
    try:
        consume_verified_triangle_executable(
            dataclasses.replace(executable), authority, plan, abi)
    except RuntimeError as error:
        if "forged, serialized, or consumed" not in str(error):
            raise
    else:
        raise RuntimeError("a copied executable authority was accepted")

    vertices = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    triangles = ((0, 1, 2),)
    front_values = (11,)
    back_values = (13,)
    queries = (
        ((0.2, 0.2, 1.0), (0.0, 0.0, -1.0), 10.0),
        ((0.2, 0.2, -1.0), (0.0, 0.0, 1.0), 10.0),
        ((2.0, 2.0, 1.0), (0.0, 0.0, -1.0), 10.0),
    )
    expected, cpu_hits, cpu_role_counts = _cpu_reference(
        callback, vertices, triangles, front_values, back_values, queries)
    result = run_builtin_triangle_callback(
        authority,
        plan,
        abi,
        executable,
        vertices=vertices,
        triangles=triangles,
        front_values=front_values,
        back_values=back_values,
        queries=queries,
        expected_output=expected,
        native_library_path=native_path,
    )
    try:
        consume_verified_triangle_executable(executable, authority, plan, abi)
    except RuntimeError as error:
        if "forged, serialized, or consumed" not in str(error):
            raise
    else:
        raise RuntimeError("a consumed executable authority was replayed")
    observed_hit_kinds = tuple(row["hit_kind"] for row in result.hit_observations)
    if observed_hit_kinds != (FRONT_HIT_KIND, BACK_HIT_KIND, None):
        raise RuntimeError("front/back/miss fixture did not exercise all required cases")
    if tuple(row["primitive_index"] for row in result.hit_observations) != (0, 0, None):
        raise RuntimeError("device primitive-index observations are not exact")
    if result.role_counters[4:7] != (2, 1, 3):
        raise RuntimeError("device role counters disagree with two-hit/one-miss fixture")

    (args.output / "CALLBACK_ABI.json").write_text(
        json.dumps(abi.to_dict(), indent=2, sort_keys=True) + "\n")
    (args.output / "TYPED_PHYSICAL_SCHEMA.json").write_text(
        json.dumps(authority.schema.to_dict(), indent=2, sort_keys=True) + "\n")
    (args.output / "TRIANGLE_ORIENTATION_AUTHORITY.json").write_text(
        json.dumps(orientation.semantic_dict() | {
            "authority_sha256": orientation.authority_sha256,
        }, indent=2, sort_keys=True) + "\n")
    (args.output / "CANONICAL_REFERENCE_PLAN.json").write_text(
        json.dumps({
            **dataclasses.asdict(plan),
            "template_id": plan.template_id.value,
            "ordered_buffer_semantics": [
                item.value for item in plan.ordered_buffer_semantics],
            "plan_sha256": plan.plan_sha256,
        }, indent=2, sort_keys=True) + "\n")
    (args.output / "TRUSTED_TRIANGLE_WRAPPER.cu").write_text(wrapper.source)
    (args.output / "TRUSTED_TRIANGLE_WRAPPER.ptx").write_text(wrapper_ptx)
    (args.output / "COMPOSED_TRIANGLE_CALLBACK.ptx").write_text(composed.ptx)
    (args.output / "NVRTC.log").write_text(nvrtc_log)
    for generated, artifact in zip(generated_leaves, compiled_leaves):
        (args.output / f"LEAF_{generated.role.value}.py").write_text(
            generated.generated_source)
        (args.output / f"LEAF_{generated.role.value}.ptx").write_text(
            artifact.ptx)
    shutil.copy2(native_path, args.output / "librtdl_optix.so")
    payload = {
        "schema": "rtdl.goal5756.builtin_triangle_device_validation.v1",
        "callback_ir_sha256": callback.ir_sha256,
        "callback_effect_digest": callback.effect_digest,
        "typed_physical_schema_sha256": authority.schema.schema_sha256,
        "triangle_orientation_authority_sha256": orientation.authority_sha256,
        "canonical_plan_sha256": plan.plan_sha256,
        "callback_abi_sha256": abi.abi_sha256,
        "wrapper_source_sha256": wrapper.source_sha256,
        "wrapper_ptx_sha256": hashlib.sha256(wrapper_ptx.encode()).hexdigest(),
        "composed_ptx_sha256": composed.ptx_sha256,
        "verified_executable_sha256": executable.executable_sha256,
        "leaf_ptx_sha256_by_role": {
            item.role: item.ptx_sha256 for item in compiled_leaves
        },
        "native_library_sha256": native_sha,
        "target": dataclasses.asdict(target),
        "fixture": {
            "vertices": vertices,
            "triangles": triangles,
            "front_values": front_values,
            "back_values": back_values,
            "queries": queries,
        },
        "cpu_hit_rows": cpu_hits,
        "device_hit_observations": result.hit_observations,
        "cpu_output": expected,
        "device_output": result.output,
        "cpu_role_counts": cpu_role_counts,
        "device_role_counters": result.role_counters,
        "device_launch_status": result.launch_status,
        "traversal_receipt": result.traversal_receipt,
        "output_sha256": result.output_sha256,
        "buffer_binding_sha256": result.buffer_binding_sha256,
        "claims": {
            "all_four_numba_leaves_executed": True,
            "primitive_index_observed": True,
            "front_hit_kind_observed": True,
            "back_hit_kind_observed": True,
            "miss_observed": True,
            "cpu_device_differential_exact": True,
            "behavioral_optix_traversal": True,
            "builtin_triangle_gas": True,
            "user_intersection_program_present": False,
            "raw_or_serialized_ptx_runtime_entry_allowed": False,
            "copied_executable_authority_accepted": False,
            "consumed_executable_authority_replay_accepted": False,
            "performance_claimed": False,
            "held_out_generalization_claimed": False,
        },
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n")
    manifest = []
    for path in sorted(item for item in args.output.rglob("*") if item.is_file()):
        manifest.append({
            "path": path.relative_to(args.output).as_posix(),
            "size": path.stat().st_size,
            "sha256": _sha(path),
        })
    (args.output / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
