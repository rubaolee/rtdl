#!/usr/bin/env python3
"""Non-timed PyOptiX controls for Goal5797's five protocol mechanisms.

This file imports only the frozen Goal5796 PyOptiX arm and standard Python
modules.  It never imports RTDL.  All device variants are exact, deterministic
single edits of the frozen matched CUDA source and are preserved beside the
result before compilation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

import cupy as cp
from cuda.bindings import runtime as cuda_runtime
import numpy as np


HERE = Path(__file__).resolve().parent
MATCHED = HERE.parent / "goal5796_matched"
sys.path.insert(0, str(MATCHED))
import pyoptix_baseline as base  # noqa: E402


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def variant_sources(base_source: bytes) -> dict[str, bytes]:
    text = base_source.decode("utf-8")
    variants = {"valid_a": text}

    effects_old = (
        "    set_payload_u64(before + 1ull);\n"
        "    optixIgnoreIntersection();\n"
        "}\n\n"
        "extern \"C\" __global__ void __miss__goal5796_triangle() {}"
    )
    effects_new = (
        "    set_payload_u64(before + 1ull);\n"
        "    optixTerminateRay();\n"
        "}\n\n"
        "extern \"C\" __global__ void __miss__goal5796_triangle() {}"
    )
    if text.count(effects_old) != 1:
        raise RuntimeError("effects source anchor is not unique")
    variants["role_effect_closure"] = text.replace(
        effects_old, effects_new, 1)

    abi_old = "optixReportIntersection(0.0f, 0u, item.item_id);"
    abi_new = "optixReportIntersection(0.0f, 0u, primitive_index);"
    if text.count(abi_old) != 1:
        raise RuntimeError("ABI source anchor is not unique")
    variants["payload_attribute_abi_ownership"] = text.replace(
        abi_old, abi_new, 1)

    physical_anchor = (
        "extern \"C\" __global__ void __raygen__goal5796_relation() {"
    )
    physical_helper = r'''static __forceinline__ __device__ Box goal5797_swap_xy(Box value) {
    const float lower_x = value.lower_x;
    const float upper_x = value.upper_x;
    value.lower_x = value.lower_y;
    value.lower_y = lower_x;
    value.upper_x = value.upper_y;
    value.upper_y = upper_x;
    return value;
}

extern "C" __global__ void __raygen__goal5796_relation() {'''
    if text.count(physical_anchor) != 1:
        raise RuntimeError("physical helper anchor is not unique")
    physical = text.replace(physical_anchor, physical_helper, 1)
    query_anchor = "const Box query = params.queries[query_index];"
    if physical.count(query_anchor) != 2:
        raise RuntimeError("physical query anchors are not exactly two")
    physical = physical.replace(
        query_anchor,
        "const Box query = goal5797_swap_xy(params.queries[query_index]);",
    )
    variants["physical_geometry_binding"] = physical

    identity_old = "set_payload_u64(before + 1ull);"
    identity_new = "set_payload_u64(before + 2ull);"
    if text.count(identity_old) != 1:
        raise RuntimeError("identity source anchor is not unique")
    variants["checked_program_executable_identity"] = text.replace(
        identity_old, identity_new, 1)
    return {key: value.encode("utf-8") for key, value in variants.items()}


def compile_ptx_bytes(
    source: bytes, *, source_name: str, optix_include: Path, cuda_include: Path,
) -> bytes:
    nvrtc = base.nvrtc
    program = base.check_nvrtc(nvrtc.nvrtcCreateProgram(
        source, source_name.encode(), 0, [], []))
    options = [
        b"--std=c++17", b"--device-as-default-execution-space",
        b"--relocatable-device-code=true",
        f"-I{optix_include}".encode(), f"-I{cuda_include}".encode(),
    ]
    base.check_nvrtc(
        nvrtc.nvrtcCompileProgram(program, len(options), options), program)
    size = base.check_nvrtc(nvrtc.nvrtcGetPTXSize(program))
    ptx = b" " * size
    base.check_nvrtc(nvrtc.nvrtcGetPTX(program, ptx))
    return ptx


def run_relation_forward(context, pipeline, sbt, fixture):
    indexed = base.boxes_array(fixture["indexed"])
    sources = base.boxes_array(fixture["sources"])
    d_indexed = base.to_device(indexed)
    d_sources = base.to_device(sources)
    raw_capacity = max(1, 2 * len(indexed) * len(sources))
    d_rows = cp.zeros(raw_capacity * 2, dtype=np.uint32)
    d_count = cp.zeros(1, dtype=np.uint32)
    d_overflow = cp.zeros(1, dtype=np.uint32)
    d_status = cp.zeros(1, dtype=np.uint32)
    handle, gas_keepalive = base.build_custom_gas(context, indexed)
    params = np.zeros(1, dtype=base.PARAM_DTYPE)
    params[0] = (
        handle, d_indexed.ptr, d_sources.ptr, d_rows.data.ptr,
        d_count.data.ptr, d_overflow.data.ptr,
        len(indexed), len(sources), raw_capacity, 0,
        np.float32(fixture["minimum_overlap"]), np.float32(0.0),
        np.float32(1.0), 0, 0, 0, 0, 0, d_status.data.ptr,
    )
    device_params = base.launch(pipeline, sbt, params, len(sources))
    keepalive = [
        d_indexed, d_sources, d_rows, d_count, d_overflow, d_status,
        *gas_keepalive, device_params,
    ]
    del keepalive
    raw_count = int(cp.asnumpy(d_count)[0])
    overflow = int(cp.asnumpy(d_overflow)[0])
    status = int(cp.asnumpy(d_status)[0])
    if overflow or status or raw_count > raw_capacity:
        raise RuntimeError(
            f"relation device failure: {raw_count}/{overflow}/{status}")
    raw = cp.asnumpy(d_rows[:raw_count * 2]).reshape((-1, 2))
    rows = sorted({(int(row[0]), int(row[1])) for row in raw})
    return [list(row) for row in rows], {
        "raw_event_count": raw_count,
        "device_overflow": overflow,
        "device_status": status,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--base-device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--expected-optix-api-version", default="9.0.0")
    parser.add_argument("--compatibility-authority", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.evidence_dir.exists():
        raise FileExistsError("Goal5797 controls are create-only")
    version = tuple(int(item) for item in base.optix.version())
    expected_version = tuple(
        int(item) for item in args.expected_optix_api_version.split("."))
    if version != expected_version:
        raise RuntimeError(f"OptiX API mismatch: {version} != {expected_version}")
    if not args.compatibility_authority.is_file():
        raise RuntimeError("compatibility authority missing")

    spec_bytes = args.spec.read_bytes()
    spec = json.loads(spec_bytes)
    generated = variant_sources(args.base_device_source.read_bytes())
    args.evidence_dir.mkdir(parents=True)
    source_dir = args.evidence_dir / "device_sources"
    source_dir.mkdir()
    ptx_dir = args.evidence_dir / "ptx"
    ptx_dir.mkdir()

    context, logger = base.make_context()
    compiled = {}
    keepalive = []
    for name, source in generated.items():
        source_path = source_dir / f"{name}.cu"
        source_path.write_bytes(source)
        ptx = compile_ptx_bytes(
            source, source_name=source_path.name,
            optix_include=args.optix_include, cuda_include=args.cuda_include)
        ptx_path = ptx_dir / f"{name}.ptx"
        ptx_path.write_bytes(ptx)
        relation_pipeline, relation_groups, _ = base.build_pipeline(
            context, ptx, task="relation")
        triangle_pipeline, triangle_groups, _ = base.build_pipeline(
            context, ptx, task="triangle")
        relation_sbt, relation_sbt_keepalive = base.make_sbt(relation_groups)
        triangle_sbt, triangle_sbt_keepalive = base.make_sbt(triangle_groups)
        keepalive.append((
            relation_pipeline, relation_groups, relation_sbt,
            relation_sbt_keepalive, triangle_pipeline, triangle_groups,
            triangle_sbt, triangle_sbt_keepalive,
        ))
        compiled[name] = {
            "source_sha256": sha_bytes(source), "ptx_sha256": sha_bytes(ptx),
            "relation_pipeline": relation_pipeline,
            "relation_sbt": relation_sbt,
            "triangle_pipeline": triangle_pipeline,
            "triangle_sbt": triangle_sbt,
        }

    relation_task = spec["tasks"]["CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"]
    diagnostic = next(
        row for row in relation_task["fixtures"]
        if row["id"] == "diagnostic_cross")
    triangle_task = spec["tasks"]["BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1"]

    valid_relation, valid_relation_diag = run_relation_forward(
        context, compiled["valid_a"]["relation_pipeline"],
        compiled["valid_a"]["relation_sbt"], diagnostic)
    valid_per_ray, valid_weighted = base.run_triangle(
        context, compiled["valid_a"]["triangle_pipeline"],
        compiled["valid_a"]["triangle_sbt"], triangle_task)

    effects_per_ray, effects_weighted = base.run_triangle(
        context, compiled["role_effect_closure"]["triangle_pipeline"],
        compiled["role_effect_closure"]["triangle_sbt"], triangle_task)
    abi_rows, abi_diag = run_relation_forward(
        context, compiled["payload_attribute_abi_ownership"]["relation_pipeline"],
        compiled["payload_attribute_abi_ownership"]["relation_sbt"], diagnostic)
    physical_rows, physical_diag = run_relation_forward(
        context, compiled["physical_geometry_binding"]["relation_pipeline"],
        compiled["physical_geometry_binding"]["relation_sbt"], diagnostic)
    identity_per_ray, identity_weighted = base.run_triangle(
        context,
        compiled["checked_program_executable_identity"]["triangle_pipeline"],
        compiled["checked_program_executable_identity"]["triangle_sbt"],
        triangle_task)

    broad_fixture = dict(next(
        row for row in relation_task["fixtures"]
        if row["id"] == relation_task["overflow_witness"]["base_fixture_id"]))
    broad_fixture["capacity"] = 8
    complete_rows, complete_diag = base.run_relation_fixture(
        context, compiled["valid_a"]["relation_pipeline"],
        compiled["valid_a"]["relation_sbt"], broad_fixture)
    if len(complete_rows) != 8:
        raise RuntimeError("status control requires exactly eight complete rows")
    partial_rows = complete_rows[:7]

    expected = {
        "valid_relation": [[100, 10], [101, 20]],
        "valid_per_ray": [3, 2, 0, 1], "valid_weighted": 16,
        "effects_per_ray": [1, 1, 0, 1], "effects_weighted": 11,
        "abi_rows": [[100, 0], [101, 1]],
        "physical_rows": [[100, 20], [101, 10]],
        "identity_per_ray": [6, 4, 0, 2], "identity_weighted": 32,
        "complete_count": 8, "partial_count": 7,
    }
    observed = {
        "valid_relation": valid_relation,
        "valid_per_ray": valid_per_ray, "valid_weighted": valid_weighted,
        "effects_per_ray": effects_per_ray,
        "effects_weighted": effects_weighted,
        "abi_rows": abi_rows, "physical_rows": physical_rows,
        "identity_per_ray": identity_per_ray,
        "identity_weighted": identity_weighted,
        "complete_count": len(complete_rows), "partial_count": len(partial_rows),
    }
    if observed != expected:
        raise RuntimeError(f"Goal5797 preregistered output mismatch: {observed!r}")
    # CuPy 14 intentionally does not expose getLastError on its public runtime
    # facade.  Use the already-pinned cuda-bindings runtime API directly.
    cuda_error = cuda_runtime.cudaGetLastError()[0]
    cuda_last_error = int(cuda_error.value)
    validation_errors = [
        item for item in logger.messages if int(item["level"]) <= 2]
    if cuda_last_error != 0 or validation_errors:
        raise RuntimeError(
            f"baseline runtime diagnostic fired: cuda={cuda_last_error}, "
            f"optix={validation_errors!r}")

    identities = {
        name: {
            "device_source_sha256": row["source_sha256"],
            "loaded_ptx_sha256": row["ptx_sha256"],
        }
        for name, row in compiled.items()
    }
    result = {
        "schema": "rtdl.goal5797.pyoptix_protocol_ablation_controls.v1",
        "status": "PASS",
        "arm": "B_CURRENT_PYOPTIX_SOURCE_OPTIX90_COMPATIBILITY",
        "pyoptix_repository_commit": base.PYOPTIX_COMMIT,
        "pyoptix_distribution_version": importlib.metadata.version("pyoptix"),
        "optix_api_version": ".".join(map(str, version)),
        "compatibility_authority_sha256": sha_bytes(
            args.compatibility_authority.read_bytes()),
        "semantic_spec_sha256": sha_bytes(spec_bytes),
        "host_control_source_sha256": sha_bytes(Path(__file__).read_bytes()),
        "identities": identities,
        "nearby_valid": {
            "relation": valid_relation,
            "relation_diagnostics": valid_relation_diag,
            "triangle": {"per_ray": valid_per_ray, "weighted_sum": valid_weighted},
        },
        "behavioral_controls": {
            "role_effect_closure": {
                "exception": None, "output": {
                    "per_ray": effects_per_ray, "weighted_sum": effects_weighted},
                "silent_wrong": True,
            },
            "payload_attribute_abi_ownership": {
                "exception": None, "output": abi_rows,
                "diagnostics": abi_diag, "silent_wrong": True,
            },
            "physical_geometry_binding": {
                "exception": None, "output": physical_rows,
                "diagnostics": physical_diag, "silent_wrong": True,
            },
            "device_status_continuation": {
                "exception": None,
                "status": "OVERFLOW", "application_result_consumed": True,
                "declared_capacity": 7,
                "expected_complete_row_count": len(complete_rows),
                "returned_row_count": len(partial_rows),
                "returned_rows": partial_rows,
                "complete_diagnostics": complete_diag,
                "protocol_invariant_violated": True,
            },
            "checked_program_executable_identity": {
                "exception": None, "output": {
                    "per_ray": identity_per_ray,
                    "weighted_sum": identity_weighted},
                "task_a_expected_weighted_sum": 16,
                "silent_wrong": True,
            },
        },
        "baseline_runtime": {
            "process_exit_code": 0,
            "cuda_last_error": "SUCCESS",
            "cuda_last_error_code": cuda_last_error,
            "optix_validation": "PASS",
            "optix_validation_error_message_count": len(validation_errors),
        },
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
        "usability_claimed": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(
        result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
