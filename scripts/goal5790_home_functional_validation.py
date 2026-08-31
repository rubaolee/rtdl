#!/usr/bin/env python3
"""Goal5790 Home functional runner for one weighted Triangle ON/OFF lane.

The runner has two explicit modes. ``inspect-target`` compiles the exact V4
program and reports target-local identities without launching an application.
``functional`` runs one fresh-process lane and writes exact output, traversal,
plan and event-derived operation evidence.  It records no elapsed value and
cannot register a performance result.  Device work returns an unsealed object;
receipt hashing/serialization happens only in the subsequent evidence phase.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys

import numba
import numpy as np

from scripts.goal5790_home_ptx_producer_probe import observe_ptx_producers

from rtdsl.v4_checked_u64_device_reduction import (
    checked_u64_downstream_operation_identity,
    checked_u64_downstream_operation_sha256,
)
from rtdsl.v4_fusion_ablation import (
    FusionVariant,
    build_checked_u64_product_sum_ablation_plan,
    load_verified_shared_contract_freeze,
    verify_fusion_ablation_plan,
    verify_target_materialization_authority,
)
from rtdsl.v4_operation_evidence import (
    receipt_from_mapping,
    verify_operation_evidence_receipt,
)
from rtdsl.v4_triangle_reduction_device_runtime import (
    VerifiedTriangleDeviceColumnCountExecutor,
)
from rtdsl.v4_triangle_standard_library import (
    compile_count_callback,
    compile_standard_triangle_program,
    weighted_hit_count_schema,
)
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


PROGRAM_BUNDLE = "v4_builtin_triangle_checked_reduction_composed"
OUTPUT_CONTRACT = {
    "paper_algorithm": "RT-2A1",
    "reducer": "checked_u64_product_sum",
    "result": "exact_u64_triangle_count",
    "overflow": "fail_closed_before_provisional_sum_is_trusted",
}
TIMER_CONTRACTS = {
    "cold": {
        "included": [
            "graph_input_load_and_degree_oriented_csr",
            "restricted_callback_verify_compile_and_program_prepare",
            "bounded_device_geometry_production",
            "optix_execute_and_declared_downstream_reducer",
            "scalar_host_materialization_and_owner_close",
        ],
        "excluded": ["oracle_comparison", "receipt_serialization"],
    },
    "prepared": {
        "included": [
            "first_prepared_execute_only",
            "bounded_device_geometry_production",
            "optix_execute_and_declared_downstream_reducer",
            "scalar_host_materialization",
        ],
        "separately_reported": [
            "graph_load", "compile_and_prepare", "owner_close"],
        "excluded": ["oracle_comparison", "receipt_serialization"],
    },
    "bounded_smoke": {
        "functional_only": True,
        "registered_timing": False,
        "included": [],
        "excluded": [
            "all_elapsed_values", "oracle_comparison", "receipt_serialization",
        ],
    },
}
HOME_MACHINE_AUTHORITY = {
    "schema": "rtdl.goal5790.frozen_home_machine_authority.v3",
    "execution_environment_class": "HOME_PASCAL_FUNCTIONAL_ONLY",
    "gpu_name": "NVIDIA GeForce GTX 1070",
    "gpu_uuid": "GPU-8e04454e-c177-6e5b-3f43-e676980ecdfa",
    "driver_version": "580.126.09",
    "compute_capability": "6.1",
    "cuda_nvcc_version": "Build cuda_12.2.r12.2/compiler.33191640_0",
    "cuda_host_compiler_path": "/usr/bin/g++-12",
    "cuda_host_compiler_version": (
        "g++-12 (Ubuntu 12.4.0-2ubuntu1~24.04.1) 12.4.0"
    ),
    "cuda_nvrtc_resolved_path": (
        "/home/lestat/vendor/cuda-12.2.2/targets/x86_64-linux/lib/"
        "libnvrtc.so.12.2.140"
    ),
    "cuda_nvrtc_sha256": (
        "000ca6278ba8b32a7dac383eb7440929c5a09095b43dd5f2df3911f63520db70"
    ),
    "cuda_nvrtc_builtins_resolved_path": (
        "/home/lestat/vendor/cuda-12.2.2/targets/x86_64-linux/lib/"
        "libnvrtc-builtins.so.12.2.140"
    ),
    "cuda_nvrtc_builtins_sha256": (
        "968ebb00640e461f587ad96d01735ac85bf4b2ab4d1cb35b3b489c3cf2cc7f18"
    ),
    "cuda_nvrtc_runtime_version": [12, 2],
    "cuda_nvvm_resolved_path": (
        "/home/lestat/vendor/cuda-12.2.2/nvvm/lib64/libnvvm.so.4.0.0"
    ),
    "cuda_nvvm_sha256": (
        "b69eaddcce6a063361f2d172ed535c3d6f7ae494a40c6ffdb7de024f89dbf80a"
    ),
    "cuda_libdevice_resolved_path": (
        "/home/lestat/vendor/cuda-12.2.2/nvvm/libdevice/libdevice.10.bc"
    ),
    "cuda_libdevice_sha256": (
        "5c9f80bf689d5d0e67dabf914a2a865a3d8b8c5ff86b86c46f63c3bb067ca523"
    ),
    "cuda_toolkit_resolved_path": "/home/lestat/vendor/cuda-12.2.2",
    "modern_rtx_execution_authorized": False,
    "pod_used": False,
}


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _admit_home_machine(args) -> dict[str, object]:
    """Admit only the frozen lx1 Home GTX1070; never infer Home from a flag."""
    value = json.loads(
        args.home_machine_authority.read_text(encoding="utf-8"))
    expected = dict(HOME_MACHINE_AUTHORITY)
    expected["receipt_sha256"] = _digest(HOME_MACHINE_AUTHORITY)
    if value != expected or args.compute_capability != "61":
        raise RuntimeError("Goal5790 frozen Home-machine authority drift")
    completed = subprocess.run([
        "nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap",
        "--format=csv,noheader",
    ], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        check=False)
    rows = list(csv.reader(completed.stdout.splitlines()))
    if completed.returncode or len(rows) != 1 or len(rows[0]) != 4:
        raise RuntimeError("Goal5790 could not derive one exact Home GPU identity")
    observed = tuple(field.strip() for field in rows[0])
    exact = (
        expected["gpu_name"], expected["gpu_uuid"],
        expected["driver_version"], expected["compute_capability"],
    )
    if observed != exact:
        raise RuntimeError(
            f"Goal5790 rejects non-Home GPU identity: {observed!r}")
    for path_field, sha_field in (
        ("cuda_nvrtc_resolved_path", "cuda_nvrtc_sha256"),
        ("cuda_nvrtc_builtins_resolved_path", "cuda_nvrtc_builtins_sha256"),
        ("cuda_nvvm_resolved_path", "cuda_nvvm_sha256"),
        ("cuda_libdevice_resolved_path", "cuda_libdevice_sha256"),
    ):
        path = Path(str(expected[path_field]))
        if not path.is_file() or str(path.resolve()) != str(expected[path_field]) \
                or _sha(path) != expected[sha_field]:
            raise RuntimeError(f"Goal5790 exact PTX producer drift: {path_field}")
    if os.environ.get("LD_PRELOAD") != expected["cuda_nvrtc_resolved_path"]:
        raise RuntimeError("Goal5790 exact NVRTC LD_PRELOAD authority drift")
    toolkit = expected["cuda_toolkit_resolved_path"]
    if os.environ.get("CUDA_HOME") != toolkit \
            or os.environ.get("CUDA_PATH") != toolkit:
        raise RuntimeError("Goal5790 CUDA_HOME/CUDA_PATH producer selector drift")
    if any(os.environ.get(name) for name in (
        "RTDL_V4_FORMAL_LEAF_CACHE",
        "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST",
        "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256",
    )):
        raise RuntimeError("Goal5790 rejects ambient formal-leaf cache authority")
    observed_toolchain = observe_ptx_producers()
    exact_nvrtc = sorted((
        expected["cuda_nvrtc_resolved_path"],
        expected["cuda_nvrtc_builtins_resolved_path"],
    ))
    if (
        observed_toolchain.get("cuda_home") != toolkit
        or observed_toolchain.get("cuda_path") != toolkit
        or observed_toolchain.get("numba_selected_nvvm_by") != "CUDA_HOME"
        or observed_toolchain.get("numba_selected_nvvm_path")
            != expected["cuda_nvvm_resolved_path"]
        or observed_toolchain.get("numba_selected_nvvm_sha256")
            != expected["cuda_nvvm_sha256"]
        or observed_toolchain.get("numba_selected_libdevice_by") != "CUDA_HOME"
        or observed_toolchain.get("numba_selected_libdevice_path")
            != expected["cuda_libdevice_resolved_path"]
        or observed_toolchain.get("numba_selected_libdevice_sha256")
            != expected["cuda_libdevice_sha256"]
        or observed_toolchain.get("loaded_nvvm_paths")
            != [expected["cuda_nvvm_resolved_path"]]
        or observed_toolchain.get("cupy_nvrtc_runtime_version")
            != expected["cuda_nvrtc_runtime_version"]
        or observed_toolchain.get("loaded_nvrtc_family_paths") != exact_nvrtc
        or observed_toolchain.get("nvrtc_probe_output") != 5790
    ):
        raise RuntimeError("Goal5790 observed PTX producer identity drift")
    args.ptx_producer_observation = observed_toolchain
    return expected


def _ptx_directives(ptx: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in ptx.splitlines():
        match = re.match(
            r"^\s*\.(version|target|address_size)\s+(.+?)\s*$", line)
        if match:
            key = match.group(1)
            if key in found:
                raise RuntimeError("Goal5790 compiled PTX duplicate directive")
            found[key] = match.group(2)
    if set(found) != {"version", "target", "address_size"}:
        raise RuntimeError("Goal5790 compiled PTX directive set drift")
    return found


def _ptx_program_identity(program) -> dict[str, object]:
    executable = program.executable
    wrapper_directives = _ptx_directives(executable.wrapper_ptx)
    leaves = [{
        "role": str(leaf.role),
        "abi_name": leaf.abi_name,
        "ptx_sha256": leaf.ptx_sha256,
        "directives": _ptx_directives(leaf.ptx),
    } for leaf in executable.compiled_leaves]
    composed = {
        "ptx_sha256": executable.composed.ptx_sha256,
        "directives": {
            "version": executable.composed.ptx_version,
            "target": executable.composed.ptx_target,
            "address_size": executable.composed.address_size,
        },
    }
    if wrapper_directives != composed["directives"] \
            or any(leaf["directives"] != composed["directives"] for leaf in leaves):
        raise RuntimeError("Goal5790 wrapper/leaf/composed PTX directives differ")
    if hashlib.sha256(executable.wrapper_ptx.encode()).hexdigest() \
            != executable.wrapper_ptx_sha256 \
            or executable.wrapper_ptx_sha256 \
                != executable.composed.wrapper_ptx_sha256:
        raise RuntimeError("Goal5790 wrapper PTX digest drift")
    result = {
        "schema": "rtdl.goal5790.ptx_program_identity.v1",
        "wrapper": {
            "ptx_sha256": executable.wrapper_ptx_sha256,
            "directives": wrapper_directives,
        },
        "ordered_leaves": leaves,
        "composed": composed,
        "composer_leaf_bindings": [
            list(binding) for binding in executable.composed.leaf_bindings],
        "wrapper_leaf_composed_directive_equality_verified": True,
    }
    return result


def _raw_edges(path: Path) -> list[list[int]]:
    payload = path.read_bytes()
    if not payload or len(payload) % 8:
        raise ValueError("Goal5790 edge view must contain little-endian i32 pairs")
    rows = [list(row) for row in struct.iter_unpack("<ii", payload)]
    if any(left < 0 or right < 0 for left, right in rows):
        raise ValueError("Goal5790 edge view contains a negative vertex ID")
    return rows


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _receipt_ok(receipt: dict[str, object]) -> bool:
    snapshot = dict(receipt["native_snapshot"])
    successful = int(snapshot["successful_launch_count"])
    return (
        receipt["physical_executor_classification"]
            == "optix_traversal_observed"
        and successful > 0
        and int(snapshot["complete_context_launch_count"]) == successful
        and all(int(snapshot.get(name, -1)) == 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error",
        ))
        and bool(snapshot["first_traversable"])
        and bool(snapshot["last_traversable"])
    )


def _runtime(args) -> dict[str, object]:
    native = args.native.resolve()
    return {
        "target": ReferenceTargetProfile(
            provider="optix", optix_sdk=args.optix_sdk,
            compute_capability=(
                f"{args.compute_capability[0]}.{args.compute_capability[1]}"),
            native_sha256=_sha(native), supports_custom_aabb=True,
            supports_builtin_triangle=True),
        "compute_capability": tuple(int(char) for char in args.compute_capability),
        "optix_include": args.optix_include.resolve(),
        "cuda_include": args.cuda_include.resolve(),
        "expected_python_version": platform.python_version(),
        "expected_numba_version": numba.__version__,
        "expected_numpy_version": np.__version__,
        "native_library_path": native,
    }


def _compile_executor(args, app):
    runtime = _runtime(args)
    callback = compile_count_callback()
    schema = weighted_hit_count_schema(callback)
    proof = app._proof(callback)
    program = compile_standard_triangle_program(
        callback, schema, runtime["target"], proof,
        compute_capability=runtime["compute_capability"],
        optix_include=runtime["optix_include"],
        cuda_include=runtime["cuda_include"],
        expected_python_version=runtime["expected_python_version"],
        expected_numba_version=runtime["expected_numba_version"],
        expected_numpy_version=runtime["expected_numpy_version"],
    )
    executor = VerifiedTriangleDeviceColumnCountExecutor(
        authority=program.authority, contract=program.contract,
        abi=program.abi, any_hit_proof_authority=program.proof,
        executable=program.executable,
        native_library_path=runtime["native_library_path"],
    )
    return runtime, executor, program


def _inspect_target(args, app) -> dict[str, object]:
    import cupy as cp

    _, executor, program = _compile_executor(args, app)
    try:
        on_recipe = checked_u64_downstream_operation_identity(
            "fusion_on", target_identity_sha256=executor.target_identity_sha256,
            cupy_version=cp.__version__)
        off_recipe = checked_u64_downstream_operation_identity(
            "fusion_off", target_identity_sha256=executor.target_identity_sha256,
            cupy_version=cp.__version__)
        result = {
            "schema": "rtdl.goal5790.target_program_inspection.v1",
            "provider_identity": "optix",
            "program_bundle_identity": PROGRAM_BUNDLE,
            "callback_ir_sha256": executor.callback_ir_sha256,
            "callback_authority_nonce": executor.callback_authority_nonce,
            "contract_sha256": executor.contract_sha256,
            "abi_sha256": executor.abi_sha256,
            "composed_program_sha256": executor.composed_program_sha256,
            "native_library_sha256": executor.native_library_sha256,
            "target_identity_sha256": executor.target_identity_sha256,
            "fusion_on_downstream_operation_recipe": on_recipe,
            "fusion_off_downstream_operation_recipe": off_recipe,
            "fusion_on_downstream_operation_recipe_sha256": (
                checked_u64_downstream_operation_sha256(
                    "fusion_on",
                    target_identity_sha256=executor.target_identity_sha256,
                    cupy_version=cp.__version__)),
            "fusion_off_downstream_operation_recipe_sha256": (
                checked_u64_downstream_operation_sha256(
                    "fusion_off",
                    target_identity_sha256=executor.target_identity_sha256,
                    cupy_version=cp.__version__)),
            "cupy_version": cp.__version__,
            "application_worker_executed": False,
            "optix_launch_executed": False,
            "registered_performance_timing_created": False,
            "home_machine_authority": args.home_machine_authority_value,
            "home_machine_authority_sha256": args.home_machine_authority_value[
                "receipt_sha256"],
            "ptx_producer_toolchain": {
                field: args.home_machine_authority_value[field]
                for field in (
                    "cuda_nvrtc_resolved_path", "cuda_nvrtc_sha256",
                    "cuda_nvrtc_builtins_resolved_path",
                    "cuda_nvrtc_builtins_sha256",
                    "cuda_nvrtc_runtime_version",
                    "cuda_nvvm_resolved_path", "cuda_nvvm_sha256",
                    "cuda_libdevice_resolved_path", "cuda_libdevice_sha256",
                    "cuda_toolkit_resolved_path",
                )
            },
            "ptx_producer_observation": args.ptx_producer_observation,
            "ptx_program_identity": _ptx_program_identity(program),
        }
        result["ptx_program_identity_sha256"] = _digest(
            result["ptx_program_identity"])
    finally:
        executor.close()
    return result


def _functional(args, app) -> dict[str, object]:
    import cupy as cp

    variant = FusionVariant(args.variant)
    lifecycle = args.lifecycle
    edge_file = args.edge_file.resolve()
    target_value = json.loads(
        args.target_materialization.read_text(encoding="utf-8"))
    target_authority = verify_target_materialization_authority(target_value)
    freeze = load_verified_shared_contract_freeze(
        args.shared_freeze.read_bytes())
    edge_sha = _sha(edge_file)
    raw_edges = _raw_edges(edge_file)
    bounded_view = {
        "schema": "rtdl.goal5790.bounded_triangle_input.v1",
        "input_kind": args.input_kind,
        "dataset": args.dataset,
        "edge_record_encoding": "little_endian_i32_pair",
        "source_mode": args.source_mode,
        "original_full_edge_filename": args.original_edge_filename,
        "original_full_edge_sha256": args.original_edge_sha256,
        "original_full_edge_size_bytes": args.original_edge_size_bytes,
        "prefix_rule": args.prefix_rule,
        "requested_prefix_edge_record_count": args.prefix_edge_count,
        "actual_edge_record_count": len(raw_edges),
        "bounded_view_edge_sha256": edge_sha,
        "bounded_view_edge_size_bytes": edge_file.stat().st_size,
        "raw_edges": raw_edges,
    }
    input_contract = {
        "dataset": args.dataset,
        "input_kind": args.input_kind,
        "edge_file_sha256": edge_sha,
        "edge_file_bytes": edge_file.stat().st_size,
        "original_full_edge_filename": args.original_edge_filename,
        "original_full_edge_sha256": args.original_edge_sha256,
        "original_full_edge_size_bytes": args.original_edge_size_bytes,
        "bounded_prefix_rule": args.prefix_rule,
        "bounded_prefix_edge_record_count": args.prefix_edge_count,
        "paper_algorithm": "RT-2A1",
        "max_relation_rows": args.max_relation_rows,
        "expected_triangle_count": args.expected_triangle_count,
    }
    input_sha = _digest(input_contract)
    oracle_contract = {
        "authority": args.oracle_authority,
        "dataset": args.dataset,
        "original_full_edge_filename": args.original_edge_filename,
        "original_full_edge_sha256": args.original_edge_sha256,
        "edge_file_sha256": edge_sha,
        "raw_edges_sha256": _digest(raw_edges),
        "expected_triangle_count": args.expected_triangle_count,
    }
    oracle_sha = _digest(oracle_contract)
    timer_contract = TIMER_CONTRACTS[lifecycle]
    timer_sha = _digest(timer_contract)
    lifecycle_sha = _digest({
        "lifecycle": lifecycle,
        "fresh_parent_pid": True,
        "first_prepared_execute_only": lifecycle == "prepared",
        "complete_endpoint": lifecycle == "cold",
        "bounded_functional_smoke_only": lifecycle == "bounded_smoke",
    })

    benchmark = app._benchmark()
    graph = benchmark.build_segmented_rt_graph_csr_binary(
        edge_file, expected_triangle_count=args.expected_triangle_count)
    _, executor, program = _compile_executor(args, app)
    if (
        executor.native_library_sha256 != target_authority.native_library_sha256
        or executor.callback_ir_sha256 != target_authority.callback_ir_sha256
        or executor.composed_program_sha256 != target_authority.composed_program_sha256
        or executor.target_identity_sha256 != target_authority.target_identity_sha256
    ):
        executor.close()
        raise RuntimeError("functional executor differs from target materialization")

    scalar_sum = 0
    segments: list[dict[str, object]] = []
    try:
        for segment in benchmark.iter_segmented_rt_graph_device_geometry(
            graph, paper_algorithm="RT-2A1",
            max_relation_rows=args.max_relation_rows,
            max_directed_edge_rows=args.max_relation_rows,
        ):
            segment_id = int(segment["segment_id"])
            query_count = int(segment["rays"]["ids"].size)
            segment_input_sha = _digest({
                "global_input_sha256": input_sha,
                "segment_id": segment_id,
                "partition": segment["partition"],
                "relation_count": int(segment["relation_count"]),
                "primitive_count": int(segment["triangles"]["ids"].size),
                "query_count": query_count,
            })
            plan = build_checked_u64_product_sum_ablation_plan(
                freeze, variant=variant,
                target_materialization=target_authority,
                input_sha256=segment_input_sha,
                output_contract_sha256=_digest(OUTPUT_CONTRACT),
                oracle_sha256=oracle_sha,
                timer_contract_sha256=timer_sha,
                lifecycle_contract_sha256=lifecycle_sha,
                value_count=query_count,
            )
            plan = verify_fusion_ablation_plan(plan)
            nonce = (
                f"goal5790-home-{os.getpid()}-{args.input_kind}-{lifecycle}-"
                f"{variant.value}-{segment_id:06d}"
            )
            unsealed = executor.execute_segment_unsealed(
                segment["triangles"], segment["rays"],
                ray_weights=segment["ray_weights"],
                fusion_ablation_plan=plan,
                operation_execution_nonce=nonce,
            )
            if unsealed.state != "device_complete_unsealed":
                unsealed.abort()
                raise RuntimeError(
                    "Goal5790 device phase did not stop at the unsealed boundary")
            traversal_semantic_binding = {
                "authority": unsealed.authority_nonce,
                "contract": unsealed.contract_sha256,
                "abi": unsealed.abi_sha256,
                "composed_ptx": unsealed.composed_program_sha256,
                "native": unsealed.native_library_sha256,
                "device_column_count": True,
            }
            if (
                traversal_semantic_binding["authority"]
                    != target_authority.callback_authority_nonce
                or traversal_semantic_binding["contract"]
                    != target_authority.contract_sha256
                or traversal_semantic_binding["abi"]
                    != target_authority.abi_sha256
                or traversal_semantic_binding["composed_ptx"]
                    != target_authority.composed_program_sha256
                or traversal_semantic_binding["native"]
                    != target_authority.native_library_sha256
            ):
                unsealed.abort()
                raise RuntimeError(
                    "Goal5790 unsealed traversal identity differs from target")
            # This is deliberately a second phase.  A future registered timer
            # ends before this call; Home records no elapsed value at all.
            executed = unsealed.seal()
            if unsealed.state != "sealed":
                raise RuntimeError("Goal5790 evidence phase did not seal")
            if executed["fusion_ablation_plan_sha256"] != plan.plan_sha256:
                raise RuntimeError("runtime returned a different fusion plan")
            traversal = dict(executed["traversal_receipt"])
            if not _receipt_ok(traversal):
                raise RuntimeError("Goal5790 segment lacked bound OptiX traversal")
            operation = receipt_from_mapping(
                dict(executed["operation_evidence_receipt"]))
            verify_operation_evidence_receipt(
                operation, plan.operation_contract(),
                expected_execution_nonce=nonce)
            value = int(executed["reduced_output"])
            if value < 0 or scalar_sum > ((1 << 64) - 1) - value:
                raise OverflowError("Goal5790 segmented U64 scalar sum overflow")
            scalar_sum += value
            segments.append({
                "segment_id": segment_id,
                "partition": segment["partition"],
                "relation_count": int(segment["relation_count"]),
                "primitive_count": int(executed["triangle_count"]),
                "query_count": int(executed["query_count"]),
                "scalar_sum": value,
                "output_sha256": executed["output_sha256"],
                "fusion_ablation_plan": plan.to_dict(),
                "operation_evidence_receipt": operation.to_dict(),
                "checked_u64_weighted_reduction": executed[
                    "checked_u64_weighted_reduction"],
                "traversal_receipt": traversal,
                "traversal_semantic_binding": traversal_semantic_binding,
                "device_phase_terminal_state": "device_complete_unsealed",
                "evidence_phase_terminal_state": "sealed",
                "evidence_sealed_after_device_phase": True,
            })
            del executed, segment
            cp.get_default_memory_pool().free_all_blocks()
    finally:
        executor.close()
    matched = scalar_sum == args.expected_triangle_count
    if not segments or not matched:
        raise RuntimeError("Goal5790 output disagrees with independent oracle")
    output_sha = _digest(scalar_sum)
    if any(segment["operation_evidence_receipt"]["output_sha256"]
           != segment["output_sha256"] for segment in segments):
        raise RuntimeError("operation evidence does not bind segment output")
    result = {
        "schema": "rtdl.goal5790.home_functional_lane.v1",
        "status": "PASS__FUNCTIONAL_OPERATION_EVIDENCE_ONLY",
        "parent_pid": os.getpid(),
        "input_kind": args.input_kind,
        "dataset": args.dataset,
        "paper_algorithm": "RT-2A1",
        "variant": variant.value,
        "lifecycle": lifecycle,
        "input_view": bounded_view,
        "input_contract": input_contract,
        "input_sha256": input_sha,
        "oracle_contract": oracle_contract,
        "oracle_sha256": oracle_sha,
        "output": scalar_sum,
        "expected": args.expected_triangle_count,
        "output_sha256": output_sha,
        "matched": matched,
        "native_library_sha256": target_authority.native_library_sha256,
        "execution_source_archive_sha256": (
            target_authority.execution_source_archive_sha256),
        "execution_source_tree_sha256": (
            target_authority.execution_source_tree_sha256),
        "target_materialization_authority": target_authority.to_dict(),
        "timer_contract": timer_contract,
        "timer_contract_sha256": timer_sha,
        "lifecycle_contract_sha256": lifecycle_sha,
        "elapsed_values_recorded": False,
        "segments": segments,
        "segment_count": len(segments),
        "particle_included": False,
        "registered_performance_timing_created": False,
        "performance_claimed": False,
        "compiler_fusion_claimed": False,
        "home_timing_is_diagnostic_only": True,
        "formal_worker": False,
        "execution_environment_class": args.home_machine_authority_value[
            "execution_environment_class"],
        "home_machine_authority": args.home_machine_authority_value,
        "home_machine_authority_sha256": args.home_machine_authority_value[
            "receipt_sha256"],
        "pod_used": args.home_machine_authority_value["pod_used"],
        "downstream_operation_recipe_scope": (
            "source_dependency_target_recipe__not_opaque_compiled_binary"),
        "opaque_compiled_binary_attestation_claimed": False,
        "two_phase_execution_evidence_seal_enforced": True,
        "evidence_hashing_or_serialization_inside_registered_timer": False,
        "ptx_producer_observation": args.ptx_producer_observation,
        "ptx_program_identity": _ptx_program_identity(program),
    }
    result["ptx_program_identity_sha256"] = _digest(
        result["ptx_program_identity"])
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("inspect-target", "functional"),
                        required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--compute-capability", choices=("61",), required=True)
    parser.add_argument("--home-machine-authority", type=Path, required=True)
    parser.add_argument("--optix-sdk", default="9.0.0")
    parser.add_argument("--shared-freeze", type=Path)
    parser.add_argument("--target-materialization", type=Path)
    parser.add_argument("--input-kind", choices=("small", "bounded_real"))
    parser.add_argument("--dataset")
    parser.add_argument("--edge-file", type=Path)
    parser.add_argument("--expected-triangle-count", type=int)
    parser.add_argument("--max-relation-rows", type=int, default=1_000_000)
    parser.add_argument("--oracle-authority")
    parser.add_argument("--source-mode", choices=(
        "inline_fixture", "frozen_full_file_prefix"))
    parser.add_argument("--original-edge-sha256")
    parser.add_argument("--original-edge-filename")
    parser.add_argument("--original-edge-size-bytes", type=int)
    parser.add_argument("--prefix-rule")
    parser.add_argument("--prefix-edge-count", type=int)
    parser.add_argument("--variant", choices=("fusion_on", "fusion_off"))
    parser.add_argument("--lifecycle", choices=(
        "cold", "prepared", "bounded_smoke"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    source = args.source_root.resolve()
    native = args.native.resolve()
    args.home_machine_authority_value = _admit_home_machine(args)
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    app = _load(
        source / "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
        f"goal5790_triangle_v4_{os.getpid()}",
    )
    if args.mode == "inspect-target":
        result = _inspect_target(args, app)
    else:
        required = (
            args.shared_freeze, args.target_materialization, args.input_kind,
            args.dataset, args.edge_file, args.expected_triangle_count,
            args.oracle_authority, args.source_mode, args.original_edge_sha256,
            args.original_edge_filename,
            args.original_edge_size_bytes, args.prefix_rule,
            args.prefix_edge_count, args.variant, args.lifecycle,
        )
        if any(value is None for value in required):
            raise ValueError("functional mode omitted a required argument")
        if args.max_relation_rows <= 0 or args.expected_triangle_count < 0 \
                or args.original_edge_size_bytes <= 0 \
                or args.prefix_edge_count <= 0:
            raise ValueError("functional bounds/oracle are invalid")
        result = _functional(args, app)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": result.get("status", result.get("schema")),
        "mode": args.mode,
        "output": str(args.output),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
