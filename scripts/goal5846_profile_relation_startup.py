#!/usr/bin/env python3
"""Nonformal phase profile for V4 bounded-relation startup engineering."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import statistics
import time

from experiments.goal5842_causal_admission.contracts import RELATION_TASK
from experiments.goal5842_causal_admission.tasks import build_task


def _measure(action):
    started = time.perf_counter_ns()
    value = action()
    return value, time.perf_counter_ns() - started


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _initialize_cuda_primary_context():
    cuda = ctypes.CDLL("libcuda.so.1")
    cuda.cuInit.argtypes = [ctypes.c_uint]
    cuda.cuInit.restype = ctypes.c_int
    cuda.cuDeviceGet.argtypes = [
        ctypes.POINTER(ctypes.c_int), ctypes.c_int
    ]
    cuda.cuDeviceGet.restype = ctypes.c_int
    cuda.cuDevicePrimaryCtxRetain.argtypes = [
        ctypes.POINTER(ctypes.c_void_p), ctypes.c_int
    ]
    cuda.cuDevicePrimaryCtxRetain.restype = ctypes.c_int
    cuda.cuCtxSetCurrent.argtypes = [ctypes.c_void_p]
    cuda.cuCtxSetCurrent.restype = ctypes.c_int
    device = ctypes.c_int()
    context = ctypes.c_void_p()
    for name, result in (
        ("cuInit", cuda.cuInit(0)),
        ("cuDeviceGet", cuda.cuDeviceGet(ctypes.byref(device), 0)),
        (
            "cuDevicePrimaryCtxRetain",
            cuda.cuDevicePrimaryCtxRetain(
                ctypes.byref(context), device.value
            ),
        ),
        ("cuCtxSetCurrent", cuda.cuCtxSetCurrent(context)),
    ):
        if int(result) != 0:
            raise RuntimeError(f"{name} failed with CUDA result {result}")
    return cuda, context


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--leaf-cache-root", type=Path, required=True)
    parser.add_argument("--leaf-cache-manifest", type=Path)
    parser.add_argument("--leaf-cache-manifest-sha256")
    parser.add_argument("--executable-cache-root", type=Path)
    parser.add_argument("--executable-cache-manifest", type=Path)
    parser.add_argument("--executable-cache-manifest-sha256")
    parser.add_argument("--steady-repetitions", type=int, default=32)
    parser.add_argument("--steady-warmups", type=int, default=16)
    parser.add_argument("--disable-executable-cache", action="store_true")
    parser.add_argument("--disable-native-initialization-overlap", action="store_true")
    parser.add_argument("--preinitialize-cuda-primary", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if min(args.steady_repetitions, args.steady_warmups) <= 0:
        raise ValueError("steady timing counts must be positive")
    if args.output is not None and args.output.exists():
        raise FileExistsError(args.output)

    from rtdsl import v4_bounded_relation_prepared_runtime as relation_runtime
    from rtdsl.physical_execution_provenance import (
        validate_bound_compact_traversal_receipt,
    )
    from rtdsl.v4 import (
        FormalNumbaLeafCachePolicy,
        V4ExecutableCachePolicy,
        V4Target,
        V4Toolchain,
    )

    leaf_manifest = (
        None if args.leaf_cache_manifest is None
        else args.leaf_cache_manifest.resolve(strict=True)
    )
    executable_manifest = (
        None if args.executable_cache_manifest is None
        else args.executable_cache_manifest.resolve(strict=True)
    )
    leaf_policy = FormalNumbaLeafCachePolicy(
        root=args.leaf_cache_root,
        manifest=leaf_manifest,
        manifest_sha256=args.leaf_cache_manifest_sha256,
    )
    if args.disable_executable_cache:
        executable_policy = None
    else:
        if args.executable_cache_root is None:
            raise ValueError(
                "--executable-cache-root is required unless the cache is disabled"
            )
        executable_policy = V4ExecutableCachePolicy(
            root=args.executable_cache_root,
            manifest=executable_manifest,
            manifest_sha256=args.executable_cache_manifest_sha256,
        )
    task = build_task(RELATION_TASK)
    cuda_primary_keepalive = None
    cuda_primary_initialization_ns = 0
    if args.preinitialize_cuda_primary:
        cuda_primary_keepalive, cuda_primary_initialization_ns = _measure(
            _initialize_cuda_primary_context
        )
    native = args.native.resolve(strict=True)
    capability = tuple(int(part) for part in args.compute_capability.split("."))
    target = V4Target.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include.resolve(strict=True),
        cuda_include=args.cuda_include.resolve(strict=True),
        formal_leaf_cache=leaf_policy,
        executable_cache=executable_policy,
    )
    if args.disable_native_initialization_overlap:
        native_initialization_ns = 0
    else:
        toolchain, native_initialization_ns = _measure(
            lambda: toolchain.begin_native_initialization(target)
        )
    route, route_ns = _measure(task.route_factory)
    program, admission_ns = _measure(route.compile)
    materialized, materialize_ns = _measure(
        lambda: program.materialize(target=target, toolchain=toolchain)
    )
    prepared, prepare_ns = _measure(lambda: materialized.prepare(task.static_input))

    def validate(result):
        if (
            type(result.output) is not relation_runtime.ValidatedBoundedRelationRows
            or result.output != task.expected_output
        ):
            raise RuntimeError("public bounded-relation output differs from oracle")
        validate_bound_compact_traversal_receipt(
            result.traversal_receipt,
            provider_library_sha256=materialized.identity.provider_artifact_sha256,
            route_identity="v4_callback_ir:custom_aabb_bounded_relation_v1",
            output_digest=result.output_sha256,
            expected_program_bundle="v4_custom_aabb_bounded_relation_composed",
            expected_raygen_invocation_count=(
                len(task.batch.source_boxes) + len(task.static_input.indexed_boxes)
            ),
            expected_successful_launch_count=2,
        )

    try:
        first, first_ns = _measure(lambda: prepared.execute(task.batch))
        validate(first)
        for _ in range(args.steady_warmups):
            validate(prepared.execute(task.batch))
        samples = []
        for _ in range(args.steady_repetitions):
            result, elapsed = _measure(lambda: prepared.execute(task.batch))
            validate(result)
            samples.append(elapsed)
        receipt = first.traversal_receipt
    finally:
        prepared.close()

    phases = {
        "native_initialization_start": native_initialization_ns,
        "route_declaration": route_ns,
        "generic_admission": admission_ns,
        "materialize": materialize_ns,
        "prepare": prepare_ns,
        "first_public_execution": first_ns,
    }
    result = {
        "schema": "rtdl.goal5846.relation_startup_profile.v1",
        "status": "PASS__NONFORMAL_ENGINEERING_DIAGNOSTIC",
        "native_sha256": _sha256_file(native),
        "query_count": len(task.batch.source_boxes),
        "row_count": len(task.expected_output),
        "setup_plus_first_ns": sum(phases.values()),
        "phases_ns": phases,
        "steady": {
            "warmups": args.steady_warmups,
            "samples_ns": samples,
            "median_ns": int(statistics.median(samples)),
            "minimum_ns": min(samples),
            "maximum_ns": max(samples),
        },
        "executable_cache": {
            "enabled": executable_policy is not None,
            "root": (
                None if executable_policy is None
                else str(executable_policy.root)
            ),
            "sealed": (
                False if executable_policy is None
                else executable_policy.manifest is not None
            ),
            "manifest_sha256": (
                None if executable_policy is None
                else executable_policy.manifest_sha256
            ),
        },
        "native_initialization_overlap": (
            not args.disable_native_initialization_overlap
        ),
        "cuda_primary_preinitialized": args.preinitialize_cuda_primary,
        "excluded_cuda_primary_initialization_ns": (
            cuda_primary_initialization_ns
        ),
        "leaf_cache": {
            "root": str(leaf_policy.root),
            "sealed": leaf_policy.manifest is not None,
            "manifest_sha256": leaf_policy.manifest_sha256,
        },
        "optix_provenance": {
            "classification": receipt["physical_executor_classification"],
            "validated_successful_launch_count": 2,
            "program_bundle": receipt["expected_program_bundle"],
        },
        "claim_boundary": {
            "formal_performance_claim_authorized": False,
            "external_review_complete": False,
        },
    }
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
