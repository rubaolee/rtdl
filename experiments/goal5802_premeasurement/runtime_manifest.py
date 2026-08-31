"""Exact runtime paths for a separately prepared Goal5802 target.

The local premeasurement freeze does not create this manifest.  A target
prepare transaction must populate it before the external preexecution CFR.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import stat
import sys
from typing import Any, Mapping
import zipfile

from .direct_source_audit import audit_direct_source
from .workload import relation_k_plus_one_workload


SCHEMA = "rtdl.goal5802.target_runtime_manifest.v2"
PYOPTIX_SOURCE_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
PYOPTIX_SOURCE_TREE = "0bf0ec24efb4a43f129aee25dd265aa8149374e3"
SYMLINK_FILE_ROLES = {"clean_python", "cxx_compiler", "nvcc", "nvidia_smi"}
RELATION_TASK = "CUSTOM_AABB_CLOSED_RELATION_COUNT_V2_MATCHED"
TRIANGLE_TASK = "BUILTIN_TRIANGLE_WEIGHTED_SCALAR_V2_MATCHED"
FINAL_PROJECTION_CLAIM = (
    "OBSERVED_NVCC_DEPENDENCY_SET_UNDER_MATCHED_ARCH_AND_EXACT_HOST_CXX__"
    "EMPIRICALLY_SUFFICIENT_FOR_FRESH_PROCESS_EXACT_NVRTC_REPLAY__"
    "NOT_A_GENERAL_NVRTC_SUPERSET")
HOST_RUNTIME_SCHEMA = "rtdl.goal5802.host_runtime_provenance.v3"
HOST_RUNTIME_DISTRIBUTIONS = (
    "numpy", "cupy-cuda12x", "cuda-python", "numba", "llvmlite")
HOST_RUNTIME_MODULES = (
    "numpy", "cupy", "cuda.bindings.driver", "cuda.bindings.nvrtc", "optix",
    "numba", "llvmlite")
BUILD_COMPILER_RUNTIME_NAMES = ("numba", "llvmlite")


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _valid_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 \
        and all(character in "0123456789abcdef" for character in value)


def _manifest_tool_record(record: Mapping[str, Any]) -> dict[str, object]:
    kind = record.get("path_kind")
    if kind == "REGULAR_FILE":
        keys = {"path", "path_kind", "bytes", "sha256"}
    elif kind == "EXACT_SYMLINK_TO_REGULAR_FILE":
        keys = {
            "path", "path_kind", "symlink_target", "resolved_path",
            "bytes", "sha256",
        }
    else:
        raise RuntimeError("Goal5802 target-observation tool path kind differs")
    if set(record) != keys:
        raise RuntimeError("Goal5802 target-observation tool record differs")
    return {key: record[key] for key in keys}


def validate_target_observation_receipt(
        value: Mapping[str, Any], files: Mapping[str, Any], *,
        require_current_loader_environment: bool = True) -> dict[str, str]:
    """Reconstruct a v2 target observation from preserved command bytes."""

    required = {
        "schema", "status", "tools", "command_receipts",
        "gpu_name", "compute_capability", "driver_version",
        "cuda_driver_version", "cuda_toolkit_version", "optix_version",
        "loader_environment", "clock_read_count",
        "registered_performance_timing_count", "gpu_kernel_launch_count",
        "formal_worker_count", "observation_sha256",
    }
    unsigned = dict(value)
    observed_seal = unsigned.pop("observation_sha256", None)
    if set(value) != required \
            or value.get("schema") != "rtdl.goal5802.target_observation.v2" \
            or value.get("status") \
            != "PASS__UNTIMED_EXACT_TARGET_OBSERVATION" \
            or observed_seal != digest(unsigned) \
            or any(type(value.get(key)) is not int or value[key] != 0 for key in (
                "clock_read_count", "registered_performance_timing_count",
                "gpu_kernel_launch_count", "formal_worker_count")):
        raise RuntimeError("Goal5802 target observation envelope differs")
    tools = value.get("tools")
    if not isinstance(tools, Mapping) or set(tools) != {"nvidia_smi", "nvcc"} \
            or any(not isinstance(tools.get(role), Mapping)
                   or dict(tools[role]) != _manifest_tool_record(files[role])
                   for role in ("nvidia_smi", "nvcc")):
        raise RuntimeError("Goal5802 target observation tool identity differs")
    commands = value.get("command_receipts")
    if not isinstance(commands, Mapping) \
            or set(commands) != {"nvidia_smi", "nvcc"}:
        raise RuntimeError("Goal5802 target observation commands absent")
    expected_commands = {
        "nvidia_smi": [
            str(tools["nvidia_smi"]["path"]),
            "--query-gpu=name,compute_cap,driver_version",
            "--format=csv,noheader,nounits",
        ],
        "nvcc": [str(tools["nvcc"]["path"]), "--version"],
    }
    for role, expected_command in expected_commands.items():
        row = commands.get(role)
        if not isinstance(row, Mapping) or set(row) != {
                "command", "exit_code", "stdout_utf8", "stdout_sha256",
                "stderr_utf8", "stderr_sha256"} \
                or row.get("command") != expected_command \
                or row.get("exit_code") != 0 \
                or not isinstance(row.get("stdout_utf8"), str) \
                or not isinstance(row.get("stderr_utf8"), str) \
                or row.get("stdout_sha256") != hashlib.sha256(
                    row["stdout_utf8"].encode("utf-8")).hexdigest() \
                or row.get("stderr_sha256") != hashlib.sha256(
                    row["stderr_utf8"].encode("utf-8")).hexdigest():
            raise RuntimeError(
                f"Goal5802 target observation command differs: {role}")
    gpu_rows = str(commands["nvidia_smi"]["stdout_utf8"]).strip().splitlines()
    fields = ([item.strip() for item in gpu_rows[0].split(",")]
              if len(gpu_rows) == 1 else [])
    nvcc_lines = str(commands["nvcc"]["stdout_utf8"]).strip().splitlines()
    projection = {
        "gpu_name": fields[0] if len(fields) == 3 else "",
        "compute_capability": fields[1] if len(fields) == 3 else "",
        "driver_version": fields[2] if len(fields) == 3 else "",
        "cuda_driver_version": value.get("cuda_driver_version"),
        "cuda_toolkit_version": nvcc_lines[-1] if nvcc_lines else "",
        "optix_version": value.get("optix_version"),
    }
    if any(not isinstance(item, str) or not item for item in projection.values()) \
            or any(value.get(key) != projection[key]
                   for key in projection):
        raise RuntimeError("Goal5802 target observation raw projection differs")
    loader = value.get("loader_environment")
    current_loader = {
        "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH"),
        "LD_PRELOAD": os.environ.get("LD_PRELOAD"),
    }
    if not isinstance(loader, Mapping) or set(loader) != set(current_loader) \
            or loader.get("LD_PRELOAD") is not None \
            or any(item is not None and not isinstance(item, str)
                   for item in loader.values()) \
            or loader.get("LD_LIBRARY_PATH") is not None and (
                not loader["LD_LIBRARY_PATH"]
                or any(not item or not Path(item).is_absolute()
                       for item in loader["LD_LIBRARY_PATH"].split(os.pathsep))) \
            or require_current_loader_environment \
            and dict(loader) != current_loader:
        raise RuntimeError("Goal5802 target loader environment differs")
    return projection


def validate_direct_nvrtc_identity_document(
        value: Mapping[str, Any], files: Mapping[str, Any]) -> None:
    """Validate the Direct v2 compile KAT and both actually loaded DSOs."""

    required = {
        "schema", "status", "discovery", "loaded_library_path",
        "loaded_library_bytes", "loaded_library_sha256",
        "loaded_builtins_path", "loaded_builtins_bytes",
        "loaded_builtins_sha256", "nvrtc_version", "nvrtc_compile_kat",
        "clock_read_count", "registered_performance_timing_count",
        "gpu_kernel_launch_count", "formal_worker_count",
    }
    if set(value) != required \
            or value.get("schema") \
            != "rtdl.goal5802.direct_loaded_nvrtc_identity.v2" \
            or value.get("status") != "PASS__UNTIMED_NO_GPU" \
            or value.get("discovery") != (
                "MINIMAL_NVRTC_COMPILE_THEN_DLADDR_NVRTCVERSION_AND_"
                "PROC_SELF_MAPS_UNIQUE_BUILTINS_REALPATH_OPEN_NOFOLLOW_FSTAT") \
            or any(type(value.get(key)) is not int or value[key] != 0 for key in (
                "clock_read_count", "registered_performance_timing_count",
                "gpu_kernel_launch_count", "formal_worker_count")):
        raise RuntimeError("Goal5802 Direct loaded-NVRTC v2 envelope differs")
    expected_library = files["nvrtc_library"]
    expected_builtins = files["nvrtc_builtins"]
    if value.get("loaded_library_path") != expected_library["path"] \
            or value.get("loaded_library_bytes") != expected_library["bytes"] \
            or value.get("loaded_library_sha256") \
            != expected_library["sha256"] \
            or value.get("loaded_builtins_path") != expected_builtins["path"] \
            or value.get("loaded_builtins_bytes") != expected_builtins["bytes"] \
            or value.get("loaded_builtins_sha256") \
            != expected_builtins["sha256"]:
        raise RuntimeError("Goal5802 Direct loaded NVRTC/builtins identity differs")
    version = value.get("nvrtc_version")
    if not isinstance(version, Mapping) or set(version) != {"major", "minor"} \
            or type(version.get("major")) is not int or version["major"] <= 0 \
            or type(version.get("minor")) is not int or version["minor"] < 0:
        raise RuntimeError("Goal5802 Direct NVRTC version differs")
    kat = value.get("nvrtc_compile_kat")
    expected_source = (
        'extern "C" __global__ void goal5802_nvrtc_identity_probe() {}\n')
    if not isinstance(kat, Mapping) or set(kat) != {
            "source_utf8", "source_sha256", "compile_options",
            "product_bytes", "product_sha256", "compile_success",
            "program_destroyed"} \
            or kat.get("source_utf8") != expected_source \
            or kat.get("source_sha256") != hashlib.sha256(
                kat["source_utf8"].encode("utf-8")).hexdigest() \
            or kat.get("compile_options") != ["--std=c++11"] \
            or type(kat.get("product_bytes")) is not int \
            or kat["product_bytes"] <= 0 \
            or not _valid_sha256(kat.get("product_sha256")) \
            or kat.get("compile_success") is not True \
            or kat.get("program_destroyed") is not True:
        raise RuntimeError("Goal5802 Direct NVRTC compile KAT differs")


def direct_nvrtc_identity_stdout_bytes(value: Mapping[str, Any]) -> bytes:
    """Reconstruct the Direct C++ one-line JSON field order exactly."""

    ordered = {
        "schema": value.get("schema"),
        "status": value.get("status"),
        "discovery": value.get("discovery"),
        "loaded_library_path": value.get("loaded_library_path"),
        "loaded_library_bytes": value.get("loaded_library_bytes"),
        "loaded_library_sha256": value.get("loaded_library_sha256"),
        "loaded_builtins_path": value.get("loaded_builtins_path"),
        "loaded_builtins_bytes": value.get("loaded_builtins_bytes"),
        "loaded_builtins_sha256": value.get("loaded_builtins_sha256"),
        "nvrtc_version": {
            "major": value.get("nvrtc_version", {}).get("major")
                if isinstance(value.get("nvrtc_version"), Mapping) else None,
            "minor": value.get("nvrtc_version", {}).get("minor")
                if isinstance(value.get("nvrtc_version"), Mapping) else None,
        },
        "nvrtc_compile_kat": {
            key: value.get("nvrtc_compile_kat", {}).get(key)
                if isinstance(value.get("nvrtc_compile_kat"), Mapping) else None
            for key in (
                "source_utf8", "source_sha256", "compile_options",
                "product_bytes", "product_sha256", "compile_success",
                "program_destroyed")
        },
        "clock_read_count": value.get("clock_read_count"),
        "registered_performance_timing_count": value.get(
            "registered_performance_timing_count"),
        "gpu_kernel_launch_count": value.get("gpu_kernel_launch_count"),
        "formal_worker_count": value.get("formal_worker_count"),
    }
    return json.dumps(
        ordered, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"


def _validate_k_plus_one_common(
        value: object, *, arm: str, extra_fields: set[str]) -> Mapping[str, Any]:
    workload = relation_k_plus_one_workload()
    required = {
        "schema", "arm", "task", "workload_sha256",
        "packed_input_sha256", "indexed_count", "source_count",
        "raw_count_below_raw_capacity", "compact_control",
        "executed_parameter_projection",
        "status_output_commit_blocking_boundary_count",
        "application_output_exposed", "application_output_d2h_call_count",
        "application_output_d2h_bytes",
        "registered_performance_timing_count", "formal_worker_count",
        *extra_fields,
    }
    expected_failure = dict(workload["expected_failure"])
    expected_control = {
        key: expected_failure[key] for key in (
            "raw_event_count", "unique_event_count", "overflowed", "status",
            "semantic_capacity", "raw_capacity", "control_d2h_bytes")}
    if not isinstance(value, Mapping) or set(value) != required \
            or value.get("schema") \
            != "rtdl.goal5802.relation_k_plus_one_device_failure.v1" \
            or value.get("arm") != arm \
            or value.get("task") != RELATION_TASK \
            or value.get("workload_sha256") != workload["workload_sha256"] \
            or value.get("packed_input_sha256") \
            != workload["packed_input_sha256"] \
            or value.get("indexed_count") != 1 \
            or value.get("source_count") != 4098 \
            or value.get("raw_count_below_raw_capacity") is not True \
            or value.get("compact_control") != expected_control \
            or value.get("executed_parameter_projection") != {
                "orientation_count": 2,
                "minimum_overlap_f32_bits": 0x3f800000,
                "semantic_capacity": 4096,
                "raw_capacity": 8192,
            } \
            or value.get("status_output_commit_blocking_boundary_count") != 1 \
            or value.get("application_output_exposed") is not False \
            or value.get("application_output_d2h_call_count") != 0 \
            or value.get("application_output_d2h_bytes") != 0 \
            or type(value.get(
                "registered_performance_timing_count")) is not int \
            or value["registered_performance_timing_count"] != 0 \
            or value.get("formal_worker_count") != 0:
        raise RuntimeError(f"{arm} K+1 device-failure evidence differs")
    return value


def validate_pyoptix_operation_kat(
        value: Mapping[str, Any], files: Mapping[str, Any], *,
        expected_source_sha256: str | None = None) -> None:
    """Validate the untimed PyOptiX operation KAT without importing an arm.

    The comparative worker intentionally carries no live monkeypatch observer.
    This target receipt is therefore the independent, pre-worker proof that the
    exact retained PyOptiX implementation performs the registered launch,
    transfer, synchronization, and first-input/reuse shapes.  Exact schema
    checks prevent a coherently resealed but weakened receipt from being
    accepted by the formal controller.
    """

    required_top = {
        "schema", "status", "rows", "task_count",
        "guard_inside_comparative_timer", "source_boundary",
        "clock_read_count", "registered_performance_timing_count",
        "formal_worker_count", "untimed_optix_launch_count",
        "untimed_auxiliary_cuda_kernel_launch_count",
        "untimed_gpu_launch_count", "relation_k_plus_one_hostile",
        "receipt_sha256",
    }
    unsigned = dict(value)
    observed = unsigned.pop("receipt_sha256", None)
    if set(value) != required_top \
            or value.get("schema") \
            != "rtdl.goal5802.pyoptix_operation_guard_untimed_kat.v1" \
            or value.get("status") \
            != "PASS__UNTIMED_PREWORKER_OPERATION_GUARD" \
            or value.get("task_count") != 2 \
            or value.get("guard_inside_comparative_timer") is not False \
            or value.get("clock_read_count") != 0 \
            or value.get("registered_performance_timing_count") != 0 \
            or value.get("formal_worker_count") != 0 \
            or value.get("untimed_optix_launch_count") != 8 \
            or value.get("untimed_auxiliary_cuda_kernel_launch_count") != 3 \
            or value.get("untimed_gpu_launch_count") != 11 \
            or observed != digest(unsigned):
        raise RuntimeError("PyOptiX operation KAT envelope differs")

    boundary = value.get("source_boundary")
    expected_launcher = {
        "zero_on_stream": 1, "enqueue": 1, "enqueue_d2h": 2,
        "synchronize": 2,
    }
    expected_live_guard = {
        class_name: {
            "timed_observer_count": 0,
            "untimed_kat_observer_count": 1,
            "timed_fast_core_call_count": 1,
            "timed_observed_core_call_count": 0,
            "untimed_observed_core_call_count": 1,
            "observed_wrapper_common_fast_core_call_count": 1,
            "timed_event_reset_count": 0,
        }
        for class_name in ("DeferredRelationPrepared", "ScalarTrianglePrepared")
    }
    expected_execute_shapes = {
        "DeferredRelationPrepared": {
            "launcher_calls": {
                "zero_on_stream": 1, "fill_ff_on_stream": 1,
                "enqueue_compaction": 1, "enqueue_d2d": 1,
                "enqueue_d2h": 2, "synchronize": 2, "enqueue": 1,
            },
            "hidden_gpu_or_helper_calls": [],
        },
        "ScalarTrianglePrepared": {
            "launcher_calls": expected_launcher,
            "hidden_gpu_or_helper_calls": [],
        },
    }
    if not isinstance(boundary, Mapping) or set(boundary) != {
            "schema", "source_sha256", "method_ast_sha256",
            "launcher_call_shape", "direct_gpu_call_count",
            "per_ray_host_materialization_count", "live_guard_shape",
            "relation_canonicalization", "execute_boundary_shape",
            "formal_fast_result_shape",
            "dynamic_helper_shape", "dynamic_materialization_shape",
            "optix_validation_mode", "optix_log_callback_mode",
            "module_optimization_level", "module_debug_level",
            "formal_forensic_operation_count",
            "formal_measurement_label_count",
            "relation_raw_capacity_policy",
            "formal_launcher_call_shape"} \
            or boundary.get("schema") \
            != "rtdl.goal5802.pyoptix_scalar_execute_boundary.v1" \
            or not _valid_sha256(boundary.get("source_sha256")) \
            or not _valid_sha256(boundary.get("method_ast_sha256")) \
            or (expected_source_sha256 is not None
                and boundary.get("source_sha256") != expected_source_sha256) \
            or boundary.get("launcher_call_shape") != expected_launcher \
            or boundary.get("direct_gpu_call_count") != 0 \
            or boundary.get("per_ray_host_materialization_count") != 0 \
            or boundary.get("optix_validation_mode") != "OFF" \
            or boundary.get("optix_log_callback_mode") != "OFF" \
            or boundary.get("module_optimization_level") != "DEFAULT" \
            or boundary.get("module_debug_level") != "NONE" \
            or boundary.get("formal_forensic_operation_count") != 0 \
            or boundary.get("formal_measurement_label_count") != 0 \
            or boundary.get("relation_raw_capacity_policy") != (
                "2_TIMES_SEMANTIC_CAPACITY__RAW_STORAGE_SAFETY_ONLY__"
                "DEVICE_UNIQUE_GATE_REQUIRED") \
            or boundary.get("live_guard_shape") != expected_live_guard \
            or boundary.get("relation_canonicalization") != {
                "numpy_lexsort_call_count": 1,
                "numpy_adjacent_any_call_count": 0,
                "python_rowwise_builtin_calls": [],
            } \
            or boundary.get("execute_boundary_shape") != expected_execute_shapes:
        raise RuntimeError("PyOptiX operation KAT source boundary differs")
    if boundary.get("formal_fast_result_shape") != {
            "DeferredRelationPrepared": {
                "constructor": "_RelationFastResult",
                "formal_return_dict_count": 0,
                "timed_execute_dict_count": 0,
                "timed_execute_trace_call_count": 0,
            },
            "ScalarTrianglePrepared": {
                "constructor": "_TriangleFastResult",
                "formal_return_dict_count": 0,
                "timed_execute_dict_count": 0,
                "timed_execute_trace_call_count": 0,
            }}:
        raise RuntimeError("PyOptiX formal result boundary differs")
    if boundary.get("dynamic_helper_shape") != {
            "device_alloc_call_count": 1,
            "async_copy_call_count": 1,
            "copy_uses_owned_raw_stream": True,
            "upload_count_trace_increment_count": 1,
            "upload_bytes_trace_increment_count": 1,
            "gas_build_call_count": 1,
            "gas_upload_helper_call_count": 1,
            "gas_trace_increment_count": 1,
            } or boundary.get("dynamic_materialization_shape") != {
            "DeferredRelationPrepared": {
                "calls": {
                    "_enqueue_pinned_dynamic_h2d": 1,
                    "_build_dynamic_custom_gas_async": 1,
                    "self.b.np.copyto": 1,
                },
                "forbidden_direct_calls": [],
            },
            "ScalarTrianglePrepared": {
                "calls": {
                    "_enqueue_pinned_dynamic_h2d": 2,
                    "_build_dynamic_custom_gas_async": 0,
                    "self.b.np.copyto": 2,
                },
                "forbidden_direct_calls": [],
            }}:
        raise RuntimeError("PyOptiX dynamic materialization boundary differs")
    if boundary.get("formal_launcher_call_shape") != {
            "zero_on_stream": {
                "self.b.cp.cuda.runtime.memsetAsync": 1},
            "fill_ff_on_stream": {
                "self.b.cp.cuda.runtime.memsetAsync": 1},
            "enqueue": {
                "self.device_params.copy_from_async": 1,
                "self.b.optix.launch": 1,
            },
            "enqueue_d2h": {
                "device_array.data.copy_to_host_async": 1},
            "enqueue_compaction": {"kernel": 1},
            "enqueue_d2d": {
                "self.b.cp.cuda.runtime.memcpyAsync": 1},
            "synchronize": {"self._raw_stream.synchronize": 1},
            }:
        raise RuntimeError("PyOptiX formal launcher boundary differs")

    count_keys = {
        "prepare_device_allocation_call_count",
        "prepare_h2d_call_count",
        "prepare_pinned_host_allocation_call_count",
        "prepare_stream_creation_count",
        "execute_device_allocation_call_count",
        "execute_pinned_host_allocation_call_count",
        "execute_async_h2d_call_count",
        "execute_async_d2h_call_count",
        "execute_blocking_d2h_call_count",
        "execute_device_zero_fill_call_count",
        "execute_explicit_stream_sync_call_count",
        "execute_launch_call_count",
        "execute_stream_creation_call_count",
        "execute_stream_destroy_call_count",
    }

    def exact_counts(**nonzero: int) -> dict[str, int]:
        result = {key: 0 for key in count_keys}
        result.update(nonzero)
        return result

    expected_guard = {
        "scope": "PYTHON_VISIBLE_TASK_OWNER_EXECUTE__NOT_CUPTI_OR_DRIVER_WIDE",
        "unapproved_device_allocation_call_count": 0,
        "unapproved_pinned_host_allocation_call_count": 0,
        "unapproved_blocking_asnumpy_call_count": 0,
        "unauthorized_direct_stream_sync_count": 0,
        "complete_driver_operation_observation_claimed": False,
    }
    row_specs = {
        "CUSTOM_AABB_CLOSED_RELATION_COUNT_V2_MATCHED": {
            "dynamic_upload_calls": 2,
            "dynamic_upload_bytes": 212992,
            "dynamic_accel_builds": 1,
            "execute_counts": exact_counts(
                execute_async_h2d_call_count=2,
                execute_async_d2h_call_count=2,
                execute_device_zero_fill_call_count=4,
                execute_explicit_stream_sync_call_count=2,
                execute_launch_call_count=3),
            "prepare_counts": exact_counts(
                prepare_device_allocation_call_count=11,
                prepare_h2d_call_count=2,
                prepare_pinned_host_allocation_call_count=6,
                prepare_stream_creation_count=1),
            "order": [
                "control_reset", "max_key_reset", "unique_count_reset",
                "keys_fill_ff", "params0_h2d", "launch0",
                "params1_h2d", "launch1", "semantic_compaction",
                "unique_count_d2d", "control_d2h", "status_ready_sync",
                "unique_rows_d2h", "output_ready_sync",
            ],
        },
        "BUILTIN_TRIANGLE_WEIGHTED_SCALAR_V2_MATCHED": {
            "dynamic_upload_calls": 2,
            "dynamic_upload_bytes": 524288,
            "dynamic_accel_builds": 0,
            "execute_counts": exact_counts(
                execute_async_h2d_call_count=1,
                execute_async_d2h_call_count=2,
                execute_device_zero_fill_call_count=3,
                execute_explicit_stream_sync_call_count=2,
                execute_launch_call_count=1),
            "prepare_counts": exact_counts(
                prepare_device_allocation_call_count=7,
                prepare_h2d_call_count=1,
                prepare_pinned_host_allocation_call_count=5,
                prepare_stream_creation_count=1),
            "order": [
                "per_ray_reset", "scalar_reset", "status_reset",
                "params_h2d", "launch", "status_d2h", "status_ready_sync",
                "scalar_d2h", "scalar_ready_sync",
            ],
        },
    }
    rows = value.get("rows")
    if not isinstance(rows, list) or len(rows) != 2 \
            or [row.get("task") if isinstance(row, Mapping) else None
                for row in rows] != list(row_specs):
        raise RuntimeError("PyOptiX operation KAT task rows differ")
    identity_common = {
        "distribution_version": "9.1.0",
        "initializer_path": files["pyoptix_initializer"]["path"],
        "initializer_sha256": files["pyoptix_initializer"]["sha256"],
        "extension_path": files["pyoptix_extension"]["path"],
        "extension_sha256": files["pyoptix_extension"]["sha256"],
        "optix_api_version": "9.0.0",
        "matched_ptx_path": files["matched_ptx"]["path"],
        "matched_ptx_sha256": files["matched_ptx"]["sha256"],
        "retained_matched_ptx_sha256": files["matched_ptx"]["sha256"],
    }
    projection_keys = {
        "independent_execute_guard", "dynamic_input_receipt",
        "execute_operation_counts", "operation_order",
        "prepare_operation_counts", "live_execute_guard_inside_timer",
    }
    dynamic_keys = {
        "prepared_input_reused", "dynamic_device_upload_call_count",
        "dynamic_device_upload_bytes", "dynamic_accel_build_count",
        "dynamic_explicit_sync_count", "dynamic_blocking_upload_call_count",
        "dynamic_input_generation",
    }
    for row in rows:
        identity_expected = dict(identity_common)
        if row.get("task") == "CUSTOM_AABB_CLOSED_RELATION_COUNT_V2_MATCHED":
            identity_expected.update({
                "compaction_cubin_path": files["compaction_cubin"]["path"],
                "compaction_cubin_sha256": files["compaction_cubin"]["sha256"],
                "retained_compaction_cubin_sha256": files[
                    "compaction_cubin"]["sha256"],
            })
        if not isinstance(row, Mapping) or set(row) != {
                "task", "first_execute", "reused_execute", "runtime_identity"} \
                or row.get("runtime_identity") != identity_expected:
            raise RuntimeError("PyOptiX operation KAT row identity differs")
        spec = row_specs[str(row["task"])]
        for name, reused in (("first_execute", False), ("reused_execute", True)):
            projection = row.get(name)
            if not isinstance(projection, Mapping) \
                    or set(projection) != projection_keys \
                    or projection.get("independent_execute_guard") \
                    != expected_guard \
                    or projection.get("execute_operation_counts") \
                    != spec["execute_counts"] \
                    or projection.get("operation_order") != spec["order"] \
                    or projection.get("prepare_operation_counts") \
                    != spec["prepare_counts"] \
                    or projection.get("live_execute_guard_inside_timer") is not True:
                raise RuntimeError("PyOptiX operation KAT projection differs")
            dynamic = projection.get("dynamic_input_receipt")
            expected_dynamic = {
                "prepared_input_reused": reused,
                "dynamic_device_upload_call_count": (
                    0 if reused else spec["dynamic_upload_calls"]),
                "dynamic_device_upload_bytes": (
                    0 if reused else spec["dynamic_upload_bytes"]),
                "dynamic_accel_build_count": (
                    0 if reused else spec["dynamic_accel_builds"]),
                "dynamic_explicit_sync_count": 0,
                "dynamic_blocking_upload_call_count": 0,
                "dynamic_input_generation": 1,
            }
            if not isinstance(dynamic, Mapping) or set(dynamic) != dynamic_keys \
                    or dict(dynamic) != expected_dynamic:
                raise RuntimeError("PyOptiX operation KAT dynamic receipt differs")

    hostile = _validate_k_plus_one_common(
        value.get("relation_k_plus_one_hostile"), arm=(
            "B_NVIDIA_PYOPTIX_9_1_SOURCE_OPTIX_9_0_COMPAT_SCALAR_ONLY"),
        extra_fields={
            "operation_order", "execute_operation_counts",
            "independent_execute_guard", "dynamic_input_receipt"})
    expected_failure_counts = exact_counts(
        execute_async_h2d_call_count=2,
        execute_async_d2h_call_count=1,
        execute_device_zero_fill_call_count=4,
        execute_explicit_stream_sync_call_count=1,
        execute_launch_call_count=3)
    expected_failure_order = [
        "control_reset", "max_key_reset", "unique_count_reset",
        "keys_fill_ff", "params0_h2d", "launch0", "params1_h2d",
        "launch1", "semantic_compaction", "unique_count_d2d",
        "control_d2h", "status_ready_sync",
    ]
    expected_failure_dynamic = {
        "prepared_input_reused": False,
        "dynamic_device_upload_call_count": 2,
        "dynamic_device_upload_bytes": 213096,
        "dynamic_accel_build_count": 1,
        "dynamic_explicit_sync_count": 0,
        "dynamic_blocking_upload_call_count": 0,
        "dynamic_input_generation": 1,
    }
    if hostile.get("operation_order") != expected_failure_order \
            or hostile.get("execute_operation_counts") \
            != expected_failure_counts \
            or hostile.get("independent_execute_guard") != expected_guard \
            or hostile.get("dynamic_input_receipt") \
            != expected_failure_dynamic:
        raise RuntimeError("PyOptiX K+1 observed operation evidence differs")


def _direct_dynamic_receipt(*, relation: bool, reused: bool) \
        -> dict[str, object]:
    return {
        "prepared_input_reused": reused,
        "dynamic_device_upload_call_count": 0 if reused else 2,
        "dynamic_device_upload_bytes": (
            0 if reused else (212992 if relation else 524288)),
        "dynamic_accel_build_count": 0 if reused else (1 if relation else 0),
        "dynamic_explicit_sync_count": 0,
        "dynamic_blocking_upload_call_count": 0,
        "dynamic_input_generation": 1,
    }


def _direct_operation_ledger(*, relation: bool) -> dict[str, object]:
    dynamic = _direct_dynamic_receipt(relation=relation, reused=True)
    common = {
        "semantic_compaction_launch_count": 1 if relation else 0,
        "semantic_compaction_key_capacity": 8192 if relation else 0,
        "semantic_compaction_scratch_bytes": 98312 if relation else 0,
        "callback_status_kernel_launch_count": 0,
        "checked_product_kernel_launch_count": 0,
        "compact_control_finalizer_kernel_launch_count": 0,
        "total_auxiliary_cuda_kernel_launch_count": 1 if relation else 0,
        "execution_parameter_h2d_bytes": 240 if relation else 120,
        "execution_parameter_h2d_copy_call_count": 2 if relation else 1,
        "stream_ordered_memset_call_count": 4 if relation else 3,
        "status_d2h_copy_call_count": 1,
        "output_d2h_copy_call_count": 1,
        "operation_evidence_source": (
            "UNTIMED_OBSERVER_SAME_TEMPLATE_CORE_AND_EXACT_SOURCE_AUDIT"),
        "live_operation_trace_inside_timer": False,
        "optix_launch_count": 2 if relation else 1,
        "async_h2d_call_count": 2 if relation else 1,
        "async_h2d_bytes": 240 if relation else 120,
        "async_d2h_call_count": 2,
        "compact_status_control_d2h_bytes": 16 if relation else 4,
        "application_output_d2h_bytes": 32768 if relation else 8,
        "total_success_d2h_bytes": 32784 if relation else 12,
        "status_output_commit_blocking_boundary_count": 2,
        "per_ray_d2h_bytes": 0,
        "optix_module_disk_cache_enabled": False,
        "optix_validation_mode": "OFF",
        "optix_log_callback_mode": "OFF",
        "module_optimization_level": "DEFAULT",
        "module_debug_level": "NONE",
        "dynamic_input_receipt": dynamic,
    }
    if relation:
        common["user_visible_output_bytes"] = 32768
    else:
        common.update({
            "device_intermediate_per_ray_bytes": 131072,
            "device_reset_bytes": 131084,
            "h2d_launch_parameter_bytes": 120,
        })
    return common


def validate_direct_operation_kat(
        value: Mapping[str, Any], files: Mapping[str, Any]) -> None:
    """Validate the actual Direct first/reuse GPU KAT before worker zero."""

    required_top = {
        "schema", "status", "rows", "task_count",
        "guard_inside_comparative_timer", "source_audit",
        "clock_read_count", "registered_performance_timing_count",
        "formal_worker_count", "untimed_optix_launch_count",
        "untimed_auxiliary_cuda_kernel_launch_count",
        "untimed_gpu_launch_count", "relation_k_plus_one_hostile",
        "receipt_sha256",
    }
    unsigned = dict(value)
    observed_seal = unsigned.pop("receipt_sha256", None)
    if set(value) != required_top \
            or value.get("schema") \
            != "rtdl.goal5802.direct_operation_guard_untimed_kat.v1" \
            or value.get("status") \
            != "PASS__UNTIMED_PREWORKER_ACTUAL_DIRECT_OPERATION_GUARD" \
            or value.get("task_count") != 2 \
            or value.get("guard_inside_comparative_timer") is not False \
            or value.get("clock_read_count") != 0 \
            or value.get("registered_performance_timing_count") != 0 \
            or value.get("formal_worker_count") != 0 \
            or value.get("untimed_optix_launch_count") != 8 \
            or value.get("untimed_auxiliary_cuda_kernel_launch_count") != 3 \
            or value.get("untimed_gpu_launch_count") != 11 \
            or observed_seal != digest(unsigned):
        raise RuntimeError("Direct operation KAT envelope differs")
    source_audit = audit_direct_source(
        Path(str(files["direct_scalar_source"]["path"])))
    if value.get("source_audit") != source_audit \
            or source_audit.get("source_sha256") \
            != files["direct_scalar_source"]["sha256"]:
        raise RuntimeError("Direct operation KAT exact-source audit differs")
    rows = value.get("rows")
    if not isinstance(rows, list) or len(rows) != 2 \
            or [row.get("task") if isinstance(row, Mapping) else None
                for row in rows] != [RELATION_TASK, TRIANGLE_TASK]:
        raise RuntimeError("Direct operation KAT task rows differ")
    recounted_optix_launches = 0
    recounted_auxiliary_launches = 0
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {
                "task", "command", "exit_code", "stdout_utf8",
                "stdout_sha256", "stderr_utf8", "stderr_sha256",
                "worker_receipt"}:
            raise RuntimeError("Direct operation KAT row schema differs")
        relation = row["task"] == RELATION_TASK
        expected_command = [
            files["direct_scalar_worker"]["path"],
            "--local-untimed-functional", "--task", row["task"],
            "--ptx", files["matched_ptx"]["path"],
        ]
        if relation:
            expected_command.extend([
                "--compaction-cubin", files["compaction_cubin"]["path"]])
        if row.get("command") != expected_command \
                or row.get("exit_code") != 0 \
                or not isinstance(row.get("stdout_utf8"), str) \
                or row.get("stdout_sha256") != hashlib.sha256(
                    row["stdout_utf8"].encode("utf-8")).hexdigest() \
                or not isinstance(row.get("stderr_utf8"), str) \
                or row.get("stderr_utf8") != "" \
                or row.get("stderr_sha256") != hashlib.sha256(b"").hexdigest() \
                or not _valid_sha256(row.get("stdout_sha256")):
            raise RuntimeError("Direct operation KAT process receipt differs")
        worker = row.get("worker_receipt")
        try:
            reconstructed_worker = json.loads(str(row["stdout_utf8"]))
        except json.JSONDecodeError as error:
            raise RuntimeError("Direct operation KAT stdout is not JSON") from error
        if reconstructed_worker != worker:
            raise RuntimeError("Direct operation KAT stdout/document differs")
        expected_worker_fields = {
            "schema", "status", "arm", "worker_id", "freeze_file_sha256",
            "execution_authority_sha256", "runtime_manifest_sha256", "task",
            "regime", "registered_performance_timing_count",
            "phase_durations_ns", "execute_or_regime_durations_ns",
            "execution_lifecycle_receipts", "correctness", "operation_ledger",
            "untimed_observed_operation_traces",
            "receipt_serialization_inside_timer", "retained_executed_ptx_sha256",
            "close_inside_primary_timer",
        }
        if relation:
            expected_worker_fields.update({
                "retained_compaction_cubin_sha256",
                "relation_k_plus_one_hostile"})
        if not isinstance(worker, Mapping) or set(worker) != expected_worker_fields \
                or worker.get("schema") \
                != "rtdl.goal5802.direct_scalar.worker.v1" \
                or worker.get("status") != "PASS" \
                or worker.get("arm") != "A_DIRECT_CUDA_OPTIX" \
                or worker.get("task") != row["task"] \
                or worker.get("regime") != "LOCAL_UNTIMED" \
                or any(worker.get(key) != "" for key in (
                    "worker_id", "freeze_file_sha256",
                    "execution_authority_sha256", "runtime_manifest_sha256")) \
                or worker.get("registered_performance_timing_count") != 0 \
                or worker.get("execute_or_regime_durations_ns") != [] \
                or worker.get("phase_durations_ns") != {
                    "process_startup_and_admission": None,
                    "input_materialization": None, "load_or_deploy": None,
                    "prepare": None, "steady_warmups": None,
                    "complete_execute": None,
                    "measurement_evidence_materialization": None,
                    "close": None, "post_execution_identity_validation": None,
                } \
                or worker.get("receipt_serialization_inside_timer") is not False \
                or worker.get("close_inside_primary_timer") is not False \
                or worker.get("retained_executed_ptx_sha256") \
                != files["matched_ptx"]["sha256"] \
                or (relation and worker.get(
                    "retained_compaction_cubin_sha256")
                    != files["compaction_cubin"]["sha256"]):
            raise RuntimeError("Direct operation KAT worker envelope differs")
        lifecycle = worker.get("execution_lifecycle_receipts")
        expected_lifecycle = [
            _direct_dynamic_receipt(relation=relation, reused=False),
            _direct_dynamic_receipt(relation=relation, reused=True),
        ]
        if lifecycle != expected_lifecycle:
            raise RuntimeError("Direct operation KAT first/reuse lifecycle differs")
        expected_trace = {
            "optix_launch_count": 2 if relation else 1,
            "compaction_launch_count": 1 if relation else 0,
            "async_h2d_call_count": 2 if relation else 1,
            "async_h2d_bytes": 240 if relation else 120,
            "async_d2h_call_count": 2,
            "async_d2h_bytes": 32784 if relation else 12,
            "async_d2d_call_count": 1 if relation else 0,
            "async_d2d_bytes": 4 if relation else 0,
            "host_blocking_boundary_count": 2,
        }
        observed_traces = worker.get("untimed_observed_operation_traces")
        if observed_traces != [expected_trace, expected_trace]:
            raise RuntimeError("Direct operation KAT observed traces differ")
        recounted_optix_launches += sum(
            int(trace["optix_launch_count"]) for trace in observed_traces)
        recounted_auxiliary_launches += sum(
            int(trace["compaction_launch_count"]) for trace in observed_traces)
        if worker.get("operation_ledger") != _direct_operation_ledger(
                relation=relation):
            raise RuntimeError("Direct operation KAT operation ledger differs")
        correctness = worker.get("correctness")
        if relation:
            expected_correctness = {
                "oracle_exact": True, "canonical_row_count": 4096,
                "canonical_rows": [[index, index] for index in range(4096)],
                "raw_event_count": 8192, "semantic_unique_count": 4096,
                "device_status": 0, "device_overflow": 0,
            }
        else:
            expected_correctness = {
                "oracle_exact": True, "device_status": 0,
                "reduced_u64": 65530,
            }
        if correctness != expected_correctness:
            raise RuntimeError("Direct operation KAT correctness differs")
    hostile = _validate_k_plus_one_common(
        value.get("relation_k_plus_one_hostile"), arm="A_DIRECT_CUDA_OPTIX",
        extra_fields={"observed_operation_trace", "dynamic_input_receipt"})
    expected_hostile_trace = {
        "optix_launch_count": 2,
        "compaction_launch_count": 1,
        "async_h2d_call_count": 2,
        "async_h2d_bytes": 240,
        "async_d2h_call_count": 1,
        "async_d2h_bytes": 16,
        "async_d2d_call_count": 1,
        "async_d2d_bytes": 4,
        "host_blocking_boundary_count": 1,
    }
    expected_hostile_dynamic = {
        "prepared_input_reused": False,
        "dynamic_device_upload_call_count": 2,
        "dynamic_device_upload_bytes": 213096,
        "dynamic_accel_build_count": 1,
        "dynamic_explicit_sync_count": 0,
        "dynamic_blocking_upload_call_count": 0,
        "dynamic_input_generation": 1,
    }
    if hostile.get("observed_operation_trace") != expected_hostile_trace \
            or hostile.get("dynamic_input_receipt") \
            != expected_hostile_dynamic:
        raise RuntimeError("Direct K+1 observed operation evidence differs")
    relation_worker = rows[0]["worker_receipt"]
    worker_hostile = relation_worker.get("relation_k_plus_one_hostile")
    expected_worker_hostile = {
        key: item for key, item in hostile.items() if key not in {
            "arm", "workload_sha256",
            "registered_performance_timing_count", "formal_worker_count"}}
    if worker_hostile != expected_worker_hostile:
        raise RuntimeError("Direct K+1 worker/wrapper evidence differs")
    recounted_optix_launches += 2
    recounted_auxiliary_launches += 1
    if recounted_optix_launches != value["untimed_optix_launch_count"] \
            or recounted_auxiliary_launches \
            != value["untimed_auxiliary_cuda_kernel_launch_count"] \
            or recounted_optix_launches + recounted_auxiliary_launches \
            != value["untimed_gpu_launch_count"]:
        raise RuntimeError("Direct operation KAT launch recount differs")


def _rtdl_dynamic_receipt(*, task: str, reused: bool) -> dict[str, object]:
    relation = task == RELATION_TASK
    if task not in {RELATION_TASK, TRIANGLE_TASK}:
        raise RuntimeError(f"unsupported RTDL operation-KAT task: {task}")
    return {
        "prepared_input_reused": reused,
        "dynamic_device_upload_call_count": (
            0 if reused else (2 if relation else 8)),
        "dynamic_device_upload_bytes": (
            0 if reused else (212992 if relation else 589824)),
        "dynamic_accel_build_count": 0 if reused else (1 if relation else 0),
        "dynamic_explicit_sync_count": 0,
        "dynamic_blocking_upload_call_count": 0,
        "dynamic_input_generation": 1,
    }


def _rtdl_native_operation_receipt(
        *, task: str, reused: bool) -> dict[str, object]:
    relation = task == RELATION_TASK
    dynamic = _rtdl_dynamic_receipt(task=task, reused=reused)
    task_specific = ({
        "semantic_compaction_launch_count": 1,
        "semantic_compaction_key_capacity": 8192,
        "semantic_compaction_scratch_bytes": 98312,
        "callback_status_kernel_launch_count": 5,
        "checked_product_kernel_launch_count": 0,
        "compact_control_finalizer_kernel_launch_count": 1,
        "total_auxiliary_cuda_kernel_launch_count": 7,
        "execution_parameter_h2d_bytes": 224,
        "execution_parameter_h2d_copy_call_count": 2,
        "stream_ordered_memset_call_count": 9,
    } if relation else {
        "semantic_compaction_launch_count": 0,
        "semantic_compaction_key_capacity": 0,
        "semantic_compaction_scratch_bytes": 0,
        "callback_status_kernel_launch_count": 3,
        "checked_product_kernel_launch_count": 2,
        "compact_control_finalizer_kernel_launch_count": 1,
        "total_auxiliary_cuda_kernel_launch_count": 6,
        "execution_parameter_h2d_bytes": 200,
        "execution_parameter_h2d_copy_call_count": 1,
        "stream_ordered_memset_call_count": 4,
    })
    return {
        "schema": "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2",
        "optix_launch_count": 2 if relation else 1,
        "host_blocking_boundary_count": 2,
        "control_d2h_bytes": 16 if relation else 4,
        "output_d2h_bytes": 32768 if relation else 8,
        "status_before_output": True,
        "output_d2h_after_status_failure": 0,
        "role_counters_materialized": False,
        **dynamic,
        **task_specific,
        "status_d2h_copy_call_count": 1,
        "output_d2h_copy_call_count": 1,
    }


def _rtdl_k_plus_one_native_operation_receipt() -> dict[str, object]:
    result = _rtdl_native_operation_receipt(
        task=RELATION_TASK, reused=False)
    result.update({
        "host_blocking_boundary_count": 1,
        "output_d2h_bytes": 0,
        "dynamic_device_upload_bytes": 213096,
        "output_d2h_copy_call_count": 0,
    })
    return result


def validate_rtdl_operation_kat(
        value: Mapping[str, Any], files: Mapping[str, Any],
        deployment_ids: Mapping[str, Any], *,
        expected_executable_identities: Mapping[str, Any] | None = None) -> None:
    """Validate exact final RTDL first/reuse execution evidence.

    This is the RTDL counterpart to the two baseline preworker KATs.  It binds
    the public clean-installed artifact, authority, trust chain, native image,
    deployment id, executable identity, and the *actual* 27-field native
    receipt for both the first dynamic input and its reuse.  It is untimed and
    therefore cannot become a favorable performance sample.
    """

    required_top = {
        "schema", "status", "rows", "task_count",
        "guard_inside_comparative_timer", "clock_read_count",
        "registered_performance_timing_count", "formal_worker_count",
        "untimed_optix_launch_count",
        "untimed_auxiliary_cuda_kernel_launch_count",
        "untimed_gpu_launch_count", "relation_k_plus_one_hostile",
        "receipt_sha256",
    }
    unsigned = dict(value)
    observed_seal = unsigned.pop("receipt_sha256", None)
    if set(value) != required_top \
            or value.get("schema") \
            != "rtdl.goal5802.rtdl_operation_guard_untimed_kat.v1" \
            or value.get("status") \
            != "PASS__UNTIMED_PREWORKER_ACTUAL_RTDL_OPERATION_GUARD" \
            or value.get("task_count") != 2 \
            or value.get("guard_inside_comparative_timer") is not False \
            or value.get("clock_read_count") != 0 \
            or value.get("registered_performance_timing_count") != 0 \
            or value.get("formal_worker_count") != 0 \
            or value.get("untimed_optix_launch_count") != 8 \
            or value.get("untimed_auxiliary_cuda_kernel_launch_count") != 33 \
            or value.get("untimed_gpu_launch_count") != 41 \
            or observed_seal != digest(unsigned):
        raise RuntimeError("RTDL operation KAT envelope differs")
    if not isinstance(deployment_ids, Mapping) \
            or set(deployment_ids) != {"relation", "triangle"}:
        raise RuntimeError("RTDL operation KAT deployment ids differ")
    if expected_executable_identities is not None \
            and (set(expected_executable_identities) \
                 != {"relation", "triangle"}
                 or not all(_valid_sha256(item)
                            for item in expected_executable_identities.values())):
        raise RuntimeError("RTDL operation KAT expected identities differ")

    rows = value.get("rows")
    if not isinstance(rows, list) or len(rows) != 2 \
            or [row.get("task") if isinstance(row, Mapping) else None
                for row in rows] != [RELATION_TASK, TRIANGLE_TASK]:
        raise RuntimeError("RTDL operation KAT task rows differ")
    relation_output_sha = digest([[index, index] for index in range(4096)])
    expected_output_sha = {
        RELATION_TASK: relation_output_sha,
        TRIANGLE_TASK: digest(65530),
    }
    expected_summary = {
        RELATION_TASK: {
            "canonical_row_count": 4096,
            "raw_event_count": 8192,
            "semantic_unique_count": 4096,
        },
        TRIANGLE_TASK: {"reduced_u64": 65530},
    }
    recounted_optix = 0
    recounted_auxiliary = 0
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {
                "task", "deployment_identity", "runtime_identity",
                "first_execute", "reused_execute"}:
            raise RuntimeError("RTDL operation KAT row schema differs")
        task = str(row["task"])
        relation = task == RELATION_TASK
        task_key = "relation" if relation else "triangle"
        prefix = task_key
        expected_deployment_identity = {
            "artifact_sha256": files[f"{prefix}_artifact"]["sha256"],
            "authority_sha256": files[f"{prefix}_authority"]["sha256"],
            "trust_root_sha256": files["trust_root"]["sha256"],
            "trust_head_sha256": files["trust_head"]["sha256"],
            "trust_package_sha256": files["trust_package"]["sha256"],
            "native_sha256": files["native_library"]["sha256"],
            "deployment_id": deployment_ids[task_key],
        }
        if row.get("deployment_identity") != expected_deployment_identity:
            raise RuntimeError("RTDL operation KAT deployment identity differs")
        runtime_identity = row.get("runtime_identity")
        if not isinstance(runtime_identity, Mapping) or set(runtime_identity) != {
                "rtdsl_init_path", "rtdsl_init_sha256",
                "rtdlexe_module_path", "rtdlexe_module_sha256",
                "executed_executable_identity_sha256"} \
                or runtime_identity.get("rtdsl_init_path") \
                != files["rtdsl_init"]["path"] \
                or runtime_identity.get("rtdsl_init_sha256") \
                != files["rtdsl_init"]["sha256"] \
                or runtime_identity.get("rtdlexe_module_path") \
                != files["rtdlexe_module"]["path"] \
                or runtime_identity.get("rtdlexe_module_sha256") \
                != files["rtdlexe_module"]["sha256"] \
                or not _valid_sha256(runtime_identity.get(
                    "executed_executable_identity_sha256")):
            raise RuntimeError("RTDL operation KAT runtime identity differs")
        executable_identity = runtime_identity[
            "executed_executable_identity_sha256"]
        if expected_executable_identities is not None \
                and executable_identity \
                != expected_executable_identities[task_key]:
            raise RuntimeError("RTDL operation KAT executable identity differs")
        for name, reused in (("first_execute", False),
                             ("reused_execute", True)):
            projection = row.get(name)
            if not isinstance(projection, Mapping) or set(projection) != {
                    "dynamic_input_receipt", "native_operation_receipt",
                    "output_canonical_sha256", "product_output_sha256",
                    "executable_identity_sha256", "oracle_exact",
                    "device_status_ok", "output_summary", "role_counters"}:
                raise RuntimeError("RTDL operation KAT projection schema differs")
            expected_operation = _rtdl_native_operation_receipt(
                task=task, reused=reused)
            # diagnostics=False is the measured route.  A product-side output
            # hash here would silently add forbidden work to execute; the
            # KAT's post-execute canonical hash is the validation identity.
            if projection.get("dynamic_input_receipt") \
                    != _rtdl_dynamic_receipt(task=task, reused=reused) \
                    or projection.get("native_operation_receipt") \
                    != expected_operation \
                    or projection.get("output_canonical_sha256") \
                    != expected_output_sha[task] \
                    or projection.get("product_output_sha256") is not None \
                    or projection.get("executable_identity_sha256") \
                    != executable_identity \
                    or projection.get("oracle_exact") is not True \
                    or projection.get("device_status_ok") is not True \
                    or projection.get("output_summary") \
                    != expected_summary[task] \
                    or projection.get("role_counters") != []:
                raise RuntimeError("RTDL operation KAT execution evidence differs")
            recounted_optix += int(expected_operation["optix_launch_count"])
            recounted_auxiliary += int(
                expected_operation["total_auxiliary_cuda_kernel_launch_count"])
    hostile = _validate_k_plus_one_common(
        value.get("relation_k_plus_one_hostile"),
        arm="D_RTDL_CLEAN_INSTALLED_RTLEXE",
        extra_fields={
            "product_compact_control", "failure_code",
            "native_operation_receipt", "deployment_identity"})
    expected_product_control = {
        "schema": "rtdl.v4.rtdlexe.relation_compact_control.v1",
        "raw_event_count": 4097,
        "unique_event_count": 4097,
        "overflowed": 1,
        "status": 0xffff5102,
        "semantic_capacity": 4096,
        "control_d2h_bytes": 16,
    }
    if hostile.get("product_compact_control") != expected_product_control \
            or hostile.get("failure_code") != "RX035_DEVICE_STATUS_INVALID" \
            or hostile.get("native_operation_receipt") \
            != _rtdl_k_plus_one_native_operation_receipt() \
            or hostile.get("deployment_identity") \
            != rows[0]["deployment_identity"]:
        raise RuntimeError("RTDL K+1 native failure evidence differs")
    recounted_optix += 2
    recounted_auxiliary += 7
    if recounted_optix != value["untimed_optix_launch_count"] \
            or recounted_auxiliary \
            != value["untimed_auxiliary_cuda_kernel_launch_count"] \
            or recounted_optix + recounted_auxiliary \
            != value["untimed_gpu_launch_count"]:
        raise RuntimeError("RTDL operation KAT launch recount differs")


def sha256_file(path: Path) -> str:
    with path.open("rb") as handle:
        value = hashlib.sha256()
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def tree_identity(root: Path) -> dict[str, object]:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise RuntimeError(f"runtime tree is not a directory: {root}")
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"runtime tree contains symlink: {path}")
        if path.is_file():
            rows.append({
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            })
        elif not path.is_dir():
            raise RuntimeError(f"runtime tree contains special file: {path}")
    encoded = json.dumps(
        rows, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode("utf-8")
    return {
        "file_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "tree_sha256": hashlib.sha256(encoded).hexdigest(),
    }


def rtdsl_package_identity(root: Path) -> dict[str, object]:
    """Identity the complete installed ``rtdsl`` tree in wheel-row framing."""

    root = root.resolve(strict=True)
    if not root.is_dir() or root.name != "rtdsl":
        raise RuntimeError(f"installed rtdsl package root differs: {root}")
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"installed rtdsl package contains symlink: {path}")
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            if relative.startswith("__pycache__/") or "/__pycache__/" in relative \
                    or relative.endswith((".pyc", ".pyo")):
                raise RuntimeError(
                    f"installed rtdsl package contains bytecode cache: {path}")
            rows.append({
                "path": f"rtdsl/{relative}",
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            })
        elif not path.is_dir():
            raise RuntimeError(
                f"installed rtdsl package contains special file: {path}")
    if not rows:
        raise RuntimeError("installed rtdsl package is empty")
    return {
        "file_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "tree_sha256": digest(rows),
        "files": rows,
    }


def rtdsl_wheel_package_identity(wheel: Path) -> dict[str, object]:
    """Reconstruct the exact ``rtdsl/*`` byte tree directly from the wheel."""

    wheel = wheel.resolve(strict=True)
    if not wheel.is_file() or wheel.is_symlink():
        raise RuntimeError("RTDL wheel is not a canonical regular file")
    dist = "rtdl_source_tree-4.0.0rc1.dist-info"
    allowed_dist = {
        f"{dist}/METADATA", f"{dist}/WHEEL", f"{dist}/top_level.txt",
        f"{dist}/RECORD",
    }
    rows: list[dict[str, object]] = []
    with zipfile.ZipFile(wheel) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or any(info.is_dir() for info in infos):
            raise RuntimeError("RTDL wheel has duplicate or directory members")
        for info in infos:
            name = info.filename
            posix = PurePosixPath(name)
            mode = info.external_attr >> 16
            if posix.is_absolute() or name != posix.as_posix() \
                    or not posix.parts or any(part in {"", ".", ".."}
                                              for part in posix.parts) \
                    or stat.S_ISLNK(mode):
                raise RuntimeError(f"RTDL wheel member is unsafe: {name}")
            if name in allowed_dist:
                continue
            if not name.startswith("rtdsl/"):
                raise RuntimeError(f"RTDL wheel member escapes package: {name}")
            relative = name.removeprefix("rtdsl/")
            if not relative or relative.startswith("__pycache__/") \
                    or "/__pycache__/" in relative \
                    or relative.endswith((".pyc", ".pyo")):
                raise RuntimeError(f"RTDL wheel package member is invalid: {name}")
            payload = archive.read(info)
            rows.append({
                "path": name, "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            })
    rows.sort(key=lambda row: str(row["path"]))
    if not rows:
        raise RuntimeError("RTDL wheel package is empty")
    return {
        "file_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "tree_sha256": digest(rows),
        "files": rows,
    }


def _current_cpu_model() -> str:
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        for line in cpuinfo.read_text(
                encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                return line.split(":", 1)[1].strip()
    return platform.processor() or "UNKNOWN"


def _current_host_projection() -> dict[str, object]:
    governors = sorted({
        path.read_text(encoding="utf-8").strip()
        for path in Path("/sys/devices/system/cpu").glob(
            "cpu[0-9]*/cpufreq/scaling_governor") if path.is_file()})
    affinity = (sorted(os.sched_getaffinity(0))
                if hasattr(os, "sched_getaffinity") else None)
    return {
        "system": platform.system(), "release": platform.release(),
        "machine": platform.machine(), "libc": list(platform.libc_ver()),
        "cpu_model": _current_cpu_model(), "affinity": affinity,
        "cpu_governors": governors or ["UNAVAILABLE"],
    }


def validate_host_runtime_provenance(
        host_runtime: Mapping[str, Any], files: Mapping[str, Any], *,
        require_current_host: bool = True) -> None:
    unsigned = dict(host_runtime)
    observed_seal = unsigned.pop("receipt_sha256", None)
    expected_fields = {
        "schema", "status", "python", "distributions",
        "loaded_module_files", "host", "thread_and_visibility_environment",
        "registered_performance_timing_count", "formal_worker_count",
        "receipt_sha256",
    }
    distributions = host_runtime.get("distributions")
    distribution_names = ({row.get("name") for row in distributions}
                          if isinstance(distributions, list)
                          and all(isinstance(row, Mapping)
                                  for row in distributions) else set())
    distributions_exact = isinstance(distributions, list) and all(
        isinstance(row, Mapping)
        and set(row) == {"name", "version", "file_count", "payload_bytes",
                        "tree_sha256", "files"}
        and isinstance(row["name"], str)
        and isinstance(row["version"], str) and bool(row["version"])
        and type(row["file_count"]) is int and row["file_count"] > 0
        and type(row["payload_bytes"]) is int and row["payload_bytes"] > 0
        and _valid_sha256(row["tree_sha256"])
        and isinstance(row["files"], list)
        and all(isinstance(item, Mapping) and set(item) == {
                    "relative_path", "path", "bytes", "sha256"}
                and isinstance(item["relative_path"], str)
                and isinstance(item["path"], str)
                and type(item["bytes"]) is int and item["bytes"] >= 0
                and _valid_sha256(item["sha256"])
                and Path(str(item["path"])).is_absolute()
                and Path(str(item["path"])).is_file()
                and not Path(str(item["path"])).is_symlink()
                and Path(str(item["path"])).stat().st_size == item["bytes"]
                and sha256_file(Path(str(item["path"]))) == item["sha256"]
                for item in row["files"])
        and row["file_count"] == len(row["files"])
        and row["payload_bytes"] == sum(
            int(item["bytes"]) for item in row["files"])
        and row["tree_sha256"] == digest(row["files"])
        for row in distributions)
    modules = host_runtime.get("loaded_module_files")
    modules_exact = isinstance(modules, Mapping) and all(
        isinstance(record, Mapping)
        and set(record) == {"path", "bytes", "sha256"}
        and isinstance(record["path"], str)
        and type(record["bytes"]) is int and record["bytes"] > 0
        and _valid_sha256(record["sha256"])
        and Path(str(record["path"])).is_absolute()
        and Path(str(record["path"])).is_file()
        and not Path(str(record["path"])).is_symlink()
        and Path(str(record["path"])).stat().st_size == record["bytes"]
        and sha256_file(Path(str(record["path"]))) == record["sha256"]
        for record in modules.values())
    python_record = host_runtime.get("python")
    python_executable = (python_record.get("executable")
                         if isinstance(python_record, Mapping) else None)
    clean_python = files["clean_python"]
    python_exact = isinstance(python_record, Mapping) \
        and set(python_record) == {"version", "implementation", "executable"} \
        and isinstance(python_executable, Mapping) \
        and python_executable == {
            "path": clean_python.get("resolved_path", clean_python.get("path")),
            "bytes": clean_python["bytes"], "sha256": clean_python["sha256"]}
    expected_environment = {
        key: os.environ.get(key) for key in (
            "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
            "PYTHONHASHSEED", "CUDA_VISIBLE_DEVICES",
            "PATH", "LD_LIBRARY_PATH", "LD_PRELOAD")}
    search_path = expected_environment["PATH"]
    if set(host_runtime) != expected_fields \
            or host_runtime.get("schema") \
            != HOST_RUNTIME_SCHEMA \
            or host_runtime.get("status") \
            != "PASS__UNTIMED_EXACT_HOST_RUNTIME_CAPTURE" \
            or observed_seal != digest(unsigned) \
            or not distributions_exact \
            or [row.get("name") for row in distributions] \
            != list(HOST_RUNTIME_DISTRIBUTIONS) \
            or not modules_exact \
            or set(modules or {}) != set(HOST_RUNTIME_MODULES) \
            or not python_exact \
            or not isinstance(host_runtime.get("host"), Mapping) \
            or set(host_runtime["host"]) != {
                "system", "release", "machine", "libc", "cpu_model",
                "affinity", "cpu_governors"} \
            or require_current_host \
            and host_runtime.get("host") != _current_host_projection() \
            or host_runtime.get("thread_and_visibility_environment") \
            != expected_environment \
            or not search_path \
            or any(not item or not Path(item).is_absolute()
                   for item in search_path.split(os.pathsep)) \
            or expected_environment["LD_PRELOAD"] is not None \
            or expected_environment["LD_LIBRARY_PATH"] is not None and (
                not expected_environment["LD_LIBRARY_PATH"]
                or any(not item or not Path(item).is_absolute()
                       for item in expected_environment[
                           "LD_LIBRARY_PATH"].split(os.pathsep))) \
            or type(host_runtime.get(
                "registered_performance_timing_count")) is not int \
            or host_runtime["registered_performance_timing_count"] != 0 \
            or type(host_runtime.get("formal_worker_count")) is not int \
            or host_runtime["formal_worker_count"] != 0:
        raise RuntimeError("Goal5802 host/runtime provenance differs")


def numba_llvmlite_runtime_authority(
        host_runtime: Mapping[str, Any], files: Mapping[str, Any]) \
        -> dict[str, object]:
    """Project the exact sealed compiler-runtime authority used by BUILD_COLD."""

    if host_runtime.get("schema") != HOST_RUNTIME_SCHEMA:
        raise RuntimeError("Goal5802 compiler runtime host schema differs")
    distributions = host_runtime.get("distributions")
    modules = host_runtime.get("loaded_module_files")
    if not isinstance(distributions, list) or not isinstance(modules, Mapping):
        raise RuntimeError("Goal5802 compiler runtime authority source absent")
    by_distribution = {
        row.get("name"): row for row in distributions
        if isinstance(row, Mapping) and isinstance(row.get("name"), str)}
    if len(by_distribution) != len(distributions):
        raise RuntimeError("Goal5802 compiler distribution rows ambiguous")
    distribution_rows = []
    module_rows = []
    for name in BUILD_COMPILER_RUNTIME_NAMES:
        row = by_distribution.get(name)
        module = modules.get(name)
        distribution_files = row.get("files") \
            if isinstance(row, Mapping) else None
        matching_distribution_files = [
            item for item in distribution_files
            if isinstance(item, Mapping)
            and item.get("path") == module.get("path")
        ] if isinstance(distribution_files, list) \
            and isinstance(module, Mapping) else []
        if not isinstance(row, Mapping) or set(row) != {
                "name", "version", "file_count", "payload_bytes",
                "tree_sha256", "files"} \
                or not isinstance(row.get("version"), str) \
                or not row["version"] \
                or type(row.get("file_count")) is not int \
                or row["file_count"] <= 0 \
                or type(row.get("payload_bytes")) is not int \
                or row["payload_bytes"] <= 0 \
                or not _valid_sha256(row.get("tree_sha256")) \
                or not isinstance(module, Mapping) or set(module) != {
                    "path", "bytes", "sha256"} \
                or not isinstance(module.get("path"), str) \
                or not Path(module["path"]).is_absolute() \
                or type(module.get("bytes")) is not int or module["bytes"] <= 0 \
                or not _valid_sha256(module.get("sha256")) \
                or len(matching_distribution_files) != 1 \
                or matching_distribution_files[0].get("bytes") \
                != module["bytes"] \
                or matching_distribution_files[0].get("sha256") \
                != module["sha256"]:
            raise RuntimeError("Goal5802 compiler runtime authority row differs")
        distribution_rows.append({
            "name": name,
            "version": row["version"],
            "file_count": row["file_count"],
            "payload_bytes": row["payload_bytes"],
            "tree_sha256": row["tree_sha256"],
        })
        module_rows.append({"name": name, **dict(module)})
    file_record = files.get("host_runtime_provenance")
    if not isinstance(file_record, Mapping) \
            or not _valid_sha256(file_record.get("sha256")) \
            or not _valid_sha256(host_runtime.get("receipt_sha256")):
        raise RuntimeError("Goal5802 compiler runtime provenance binding absent")
    unsigned: dict[str, object] = {
        "schema": "rtdl.goal5802.numba_llvmlite_runtime_authority.v1",
        "status": "EXACT_SEALED_BUILD_COMPILER_RUNTIME",
        "host_runtime_provenance_file_sha256": file_record["sha256"],
        "host_runtime_provenance_receipt_sha256": host_runtime["receipt_sha256"],
        "distributions": distribution_rows,
        "loaded_module_files": module_rows,
    }
    return {**unsigned, "authority_sha256": digest(unsigned)}


def validate_runtime_manifest_document(value: Mapping[str, Any]) -> None:
    """Validate the sealed document without touching target payload paths.

    The controller performs the expensive exact file/tree validation once and
    conditions the same union of deployment files before every comparative
    worker.  A worker uses this document-only check so it cannot asymmetrically
    pre-read one arm's deployment payload before its primary timer.
    """

    required_top = {
        "schema", "status", "files", "directories", "deployment_ids",
        "pyoptix", "target_observation", "target_policy",
        "architecture_contract", "build_provenance",
        "formal_preflight_contract",
        "registered_performance_timing_count",
        "formal_worker_zero", "manifest_sha256",
    }
    if set(value) != required_top:
        raise RuntimeError("Goal5802 runtime manifest top-level keys differ")
    if value.get("schema") != SCHEMA \
            or value.get("status") \
            != "PREPARED_UNTIMED__FORMAL_EXECUTION_LOCKED" \
            or type(value.get(
                "registered_performance_timing_count")) is not int \
            or value["registered_performance_timing_count"] != 0 \
            or value.get("formal_worker_zero") is not False:
        raise RuntimeError("Goal5802 runtime manifest envelope invalid")
    unsigned = dict(value)
    observed_manifest_digest = unsigned.pop("manifest_sha256")
    if observed_manifest_digest != digest(unsigned):
        raise RuntimeError("Goal5802 runtime manifest self-digest mismatch")


def validate_runtime_manifest(value: Mapping[str, Any]) -> None:
    validate_runtime_manifest_document(value)
    files = value.get("files")
    directories = value.get("directories")
    if not isinstance(files, Mapping) or not isinstance(directories, Mapping):
        raise RuntimeError("Goal5802 runtime path identities absent")
    required_files = {
        "clean_python", "direct_scalar_worker", "direct_scalar_source",
        "direct_build_recipe", "direct_worker_build_receipt",
        "direct_operation_kat", "rtdl_operation_kat",
        "device_source", "compaction_source", "matched_ptx",
        "compaction_cubin", "matched_ptx_prepare_receipt",
        "callback_proof", "nvrtc_library", "nvrtc_builtins",
        "cxx_compiler", "nvcc", "nvidia_smi",
        "target_observation_receipt",
        "rtdl_wheel", "pyoptix_wheel", "pyoptix_wheel_build_receipt",
        "pyoptix_clean_install_receipt", "goal5800_v7_source",
        "pyoptix_operation_kat", "host_runtime_provenance",
        "header_projection_receipt", "combined_runtime_receipt",
        "pyoptix_initializer", "pyoptix_extension", "rtdsl_init",
        "rtdlexe_module", "native_library", "trust_root", "trust_head",
        "trust_package", "relation_artifact", "relation_authority",
        "triangle_artifact", "triangle_authority",
    }
    if set(files) != required_files:
        raise RuntimeError("Goal5802 runtime file role set differs")
    for role, raw in files.items():
        if not isinstance(raw, Mapping):
            raise RuntimeError(f"Goal5802 runtime file row invalid: {role}")
        path = Path(str(raw["path"]))
        kind = raw.get("path_kind")
        if kind == "REGULAR_FILE":
            fields_ok = set(raw) == {"path", "path_kind", "bytes", "sha256"}
            resolved = path
            path_ok = path.is_absolute() and path.is_file() and not path.is_symlink()
        elif kind == "EXACT_SYMLINK_TO_REGULAR_FILE":
            fields_ok = set(raw) == {
                "path", "path_kind", "symlink_target", "resolved_path",
                "bytes", "sha256"}
            resolved = path.resolve(strict=True) if path.is_symlink() else path
            path_ok = role in SYMLINK_FILE_ROLES \
                and path.is_absolute() and path.is_symlink() \
                and str(path.readlink()) == raw.get("symlink_target") \
                and str(resolved) == raw.get("resolved_path") \
                and resolved.is_file()
        else:
            fields_ok = path_ok = False
            resolved = path
        if not fields_ok or not path_ok \
                or resolved.stat().st_size != raw["bytes"] \
                or sha256_file(resolved) != raw["sha256"]:
            raise RuntimeError(f"Goal5802 runtime file differs: {role}")
    if set(directories) != {
            "optix_include", "cuda_include", "optix_sdk",
            "header_projection", "rtdsl_package"}:
        raise RuntimeError("Goal5802 runtime directory role set differs")
    for role, raw in directories.items():
        expected_fields = ({
            "path", "file_count", "payload_bytes", "tree_sha256", "files"}
            if role == "rtdsl_package" else {
                "path", "file_count", "payload_bytes", "tree_sha256"})
        if not isinstance(raw, Mapping) or set(raw) != expected_fields:
            raise RuntimeError(f"Goal5802 runtime tree row invalid: {role}")
        tree_path = Path(str(raw["path"]))
        if not tree_path.is_absolute():
            raise RuntimeError(f"Goal5802 runtime tree path is not absolute: {role}")
        observed = (rtdsl_package_identity(tree_path)
                    if role == "rtdsl_package" else tree_identity(tree_path))
        if {key: raw[key] for key in observed} != observed:
            raise RuntimeError(f"Goal5802 runtime tree differs: {role}")
    package_root = Path(str(directories["rtdsl_package"]["path"]))
    wheel_package = rtdsl_wheel_package_identity(
        Path(str(files["rtdl_wheel"]["path"])))
    if wheel_package != {
            key: directories["rtdsl_package"][key] for key in wheel_package}:
        raise RuntimeError("Goal5802 installed RTDL package differs from wheel")
    if Path(str(files["rtdsl_init"]["path"])) != package_root / "__init__.py" \
            or Path(str(files["rtdlexe_module"]["path"])) \
            != package_root / "v4_rtdlexe.py":
        raise RuntimeError("Goal5802 runtime package entry paths differ")
    from scripts.goal5802_build_header_projection_untimed import (
        validate_projection_only,
    )
    header_projection_path = Path(str(
        files["header_projection_receipt"]["path"]))
    header_projection = json.loads(
        header_projection_path.read_text(encoding="utf-8"))
    if not isinstance(header_projection, Mapping):
        raise RuntimeError("Goal5802 header projection receipt is not an object")
    projection_root = Path(str(directories["header_projection"]["path"]))
    validate_projection_only(header_projection, projection_root)
    if header_projection.get("projection_file_count") \
            != directories["header_projection"]["file_count"] \
            or header_projection.get("projection_payload_bytes") \
            != directories["header_projection"]["payload_bytes"] \
            or header_projection.get("projection_tree_sha256") \
            != directories["header_projection"]["tree_sha256"] \
            or any(not Path(str(directories[role]["path"])).is_relative_to(
                projection_root) for role in ("optix_include", "cuda_include")):
        raise RuntimeError("Goal5802 header projection binding differs")
    from scripts.goal5802_prepare_matched_ptx_untimed import (
        validate_matched_ptx_prepare_receipt,
    )
    matched_receipt_path = Path(str(
        files["matched_ptx_prepare_receipt"]["path"]))
    matched_receipt = json.loads(
        matched_receipt_path.read_text(encoding="utf-8"))
    if not isinstance(matched_receipt, Mapping):
        raise RuntimeError("Goal5802 matched-PTX receipt is not an object")
    validate_matched_ptx_prepare_receipt(
        matched_receipt, projection_receipt=header_projection,
        projection_root=projection_root)
    direct_build_path = Path(str(files["direct_worker_build_receipt"]["path"]))
    direct_build = json.loads(direct_build_path.read_text(encoding="utf-8"))
    if not isinstance(direct_build, Mapping):
        raise RuntimeError("Goal5802 Direct build receipt is not an object")
    direct_unsigned = dict(direct_build)
    direct_seal = direct_unsigned.pop("receipt_sha256", None)
    if direct_build.get("schema") \
            != "rtdl.goal5802.direct_worker_untimed_build_receipt.v2" \
            or direct_seal != digest(direct_unsigned) \
            or direct_build.get("output_bytes") \
            != files["direct_scalar_worker"]["bytes"] \
            or direct_build.get("output_sha256") \
            != files["direct_scalar_worker"]["sha256"] \
            or direct_build.get("direct_source_sha256") \
            != files["direct_scalar_source"]["sha256"] \
            or type(direct_build.get(
                "registered_performance_timing_count")) is not int \
            or direct_build["registered_performance_timing_count"] != 0 \
            or type(direct_build.get("gpu_kernel_launch_count")) is not int \
            or direct_build["gpu_kernel_launch_count"] != 0:
        raise RuntimeError("Goal5802 Direct build receipt binding differs")
    direct_nvrtc = direct_build.get("loaded_nvrtc_identity_document")
    if not isinstance(direct_nvrtc, Mapping):
        raise RuntimeError("Goal5802 Direct NVRTC identity is absent")
    validate_direct_nvrtc_identity_document(direct_nvrtc, files)
    if direct_build.get("loaded_nvrtc_identity_stdout_sha256") \
            != hashlib.sha256(
                direct_nvrtc_identity_stdout_bytes(direct_nvrtc)).hexdigest():
        raise RuntimeError("Goal5802 Direct NVRTC identity stdout differs")
    deployment_ids = value.get("deployment_ids")
    if not isinstance(deployment_ids, Mapping) \
            or set(deployment_ids) != {"relation", "triangle"} \
            or not all(isinstance(item, str) and item
                       for item in deployment_ids.values()):
        raise RuntimeError("Goal5802 deployment ids invalid")
    pyoptix = value.get("pyoptix")
    if not isinstance(pyoptix, Mapping) or set(pyoptix) != {
            "distribution_version", "optix_api_version", "source_commit",
            "source_tree", "goal5800_v7_source_sha256"} \
            or pyoptix["distribution_version"] != "9.1.0" \
            or pyoptix["optix_api_version"] != "9.0.0" \
            or pyoptix["source_commit"] != PYOPTIX_SOURCE_COMMIT \
            or pyoptix["source_tree"] != PYOPTIX_SOURCE_TREE:
        raise RuntimeError("Goal5802 PyOptiX compatibility identity invalid")
    goal5800_sha = pyoptix["goal5800_v7_source_sha256"]
    if not isinstance(goal5800_sha, str) or len(goal5800_sha) != 64 \
            or any(ch not in "0123456789abcdef" for ch in goal5800_sha):
        raise RuntimeError("Goal5802 PyOptiX owner source identity invalid")
    target_policy = value.get("target_policy")
    if target_policy != {
            "gpu_model_or_driver_preselection_allowed": False,
            "eligibility": "FIRST_OWNER_PROVIDED_TARGET_PASSING_UNTIMED_GATE",
            "result_conditioned_replacement_allowed": False,
            "driver_or_gpu_failure_disposition": (
                "PRESERVE_FAILED_ROW__NO_REPLACEMENT") }:
        raise RuntimeError("Goal5802 target-selection policy differs")
    observation_path = Path(str(files["target_observation_receipt"]["path"]))
    observation = json.loads(observation_path.read_text(encoding="utf-8"))
    if not isinstance(observation, Mapping):
        raise RuntimeError("Goal5802 target observation receipt is not an object")
    observation_projection = validate_target_observation_receipt(
        observation, files, require_current_loader_environment=True)
    target = value.get("target_observation")
    if not isinstance(target, Mapping) or set(target) != {
            "gpu_name", "compute_capability", "driver_version",
            "cuda_driver_version", "cuda_toolkit_version", "optix_version",
            "observation_receipt_sha256"} \
            or not all(isinstance(item, str) and item for item in target.values()):
        raise RuntimeError("Goal5802 target observation invalid")
    receipt_sha = target["observation_receipt_sha256"]
    if len(receipt_sha) != 64 \
            or any(ch not in "0123456789abcdef" for ch in receipt_sha):
        raise RuntimeError("Goal5802 target observation receipt digest invalid")
    if files["target_observation_receipt"]["sha256"] != receipt_sha:
        raise RuntimeError("Goal5802 target observation receipt is not file-bound")
    if any(target.get(key) != observation_projection[key]
           for key in observation_projection):
        raise RuntimeError("Goal5802 target observation projection differs")
    cc_text = target["compute_capability"]
    cc_parts = cc_text.split(".")
    if len(cc_parts) != 2 or not all(part.isdigit() for part in cc_parts):
        raise RuntimeError("Goal5802 compute capability is not major.minor")
    cc_numbers = [int(part) for part in cc_parts]
    sm_target = "sm_" + "".join(cc_parts)
    compute_target = "compute_" + "".join(cc_parts)
    artifact_rows: dict[str, object] = {}
    for prefix in ("relation", "triangle"):
        artifact = json.loads(Path(str(files[f"{prefix}_artifact"]["path"]))
                              .read_text(encoding="utf-8"))
        product = artifact.get("product_projection") \
            if isinstance(artifact, dict) else None
        toolchain = product.get("target_toolchain") \
            if isinstance(product, dict) else None
        metadata = product.get("ptx_metadata") \
            if isinstance(product, dict) else None
        provider = product.get("provider_key") \
            if isinstance(product, dict) else None
        if not all(isinstance(item, dict)
                   for item in (toolchain, metadata, provider)) \
                or toolchain.get("compute_capability") != cc_numbers \
                or metadata.get("target") != sm_target \
                or provider.get("target_compute_capability") != cc_numbers \
                or provider.get("ptx_target") != sm_target:
            raise RuntimeError(
                f"Goal5802 RTDL artifact architecture differs: {prefix}")
        artifact_rows[prefix] = {
            "artifact_sha256": files[f"{prefix}_artifact"]["sha256"],
            "target_toolchain_compute_capability": cc_numbers,
            "ptx_metadata_target": sm_target,
            "provider_target_compute_capability": cc_numbers,
            "provider_ptx_target": sm_target,
        }
    architecture = value.get("architecture_contract")
    if architecture != {
            "compute_capability": cc_text,
            "nvrtc_compute_architecture": compute_target,
            "ptx_target": sm_target,
            "ptx_target_directive_count": 1,
            "rtdl_artifacts": artifact_rows,
            "libnvrtc_sha256": files["nvrtc_library"]["sha256"],
            "libnvrtc_builtins_sha256": files[
                "nvrtc_builtins"]["sha256"],
            "libnvrtc_version": architecture.get("libnvrtc_version")
                if isinstance(architecture, Mapping) else None,
            "fresh_process_projection_claim": FINAL_PROJECTION_CLAIM,
            } \
            or not isinstance(architecture.get("libnvrtc_version"), list) \
            or len(architecture["libnvrtc_version"]) != 2 \
            or not all(type(item) is int and item >= 0
                       for item in architecture["libnvrtc_version"]):
        raise RuntimeError("Goal5802 architecture contract differs")
    if direct_nvrtc.get("nvrtc_version") != {
            "major": architecture["libnvrtc_version"][0],
            "minor": architecture["libnvrtc_version"][1],
    }:
        raise RuntimeError("Goal5802 Direct/Python NVRTC versions differ")
    provenance = value.get("build_provenance")
    combined_receipt_path = Path(str(
        files["combined_runtime_receipt"]["path"]))
    combined_root = combined_receipt_path.parent
    combined_site = combined_root / "venv/lib/python3.12/site-packages"
    extension_path = Path(str(files["pyoptix_extension"]["path"]))
    combined_path_projection = {
        "root_path": str(combined_root),
        "clean_python_relative": "venv/bin/python",
        "site_packages_relative": "venv/lib/python3.12/site-packages",
        "rtdsl_package_relative": "venv/lib/python3.12/site-packages/rtdsl",
        "pyoptix_initializer_relative": (
            "venv/lib/python3.12/site-packages/optix/__init__.py"),
        "pyoptix_extension_relative": extension_path.relative_to(
            combined_root).as_posix(),
        "all_runtime_paths_inside_receipted_combined_root": True,
    }
    if Path(str(files["clean_python"]["path"])) \
            != combined_root / "venv/bin/python" \
            or Path(str(directories["rtdsl_package"]["path"])) \
            != combined_site / "rtdsl" \
            or Path(str(files["pyoptix_initializer"]["path"])) \
            != combined_site / "optix/__init__.py" \
            or extension_path.parent != combined_site / "optix" \
            or not extension_path.name.startswith("_optix.cpython-312-") \
            or extension_path.suffix != ".so":
        raise RuntimeError(
            "Goal5802 executed Python paths escape receipted combined runtime")
    expected_provenance = {
        "direct_worker_receipt_sha256": files[
            "direct_worker_build_receipt"]["sha256"],
        "direct_operation_kat_sha256": files[
            "direct_operation_kat"]["sha256"],
        "rtdl_operation_kat_sha256": files[
            "rtdl_operation_kat"]["sha256"],
        "matched_ptx_receipt_sha256": files[
            "matched_ptx_prepare_receipt"]["sha256"],
        "pyoptix_wheel_build_receipt_sha256": files[
            "pyoptix_wheel_build_receipt"]["sha256"],
        "pyoptix_clean_install_receipt_sha256": files[
            "pyoptix_clean_install_receipt"]["sha256"],
        "pyoptix_operation_kat_sha256": files[
            "pyoptix_operation_kat"]["sha256"],
        "host_runtime_provenance_sha256": files[
            "host_runtime_provenance"]["sha256"],
        "header_projection_receipt_sha256": files[
            "header_projection_receipt"]["sha256"],
        "combined_runtime_receipt_sha256": files[
            "combined_runtime_receipt"]["sha256"],
        "combined_runtime_full_venv_member_tree_sha256": (
            json.loads(Path(str(files["combined_runtime_receipt"]["path"]))
                       .read_text(encoding="utf-8"))[
                           "venv_member_tree_sha256"]),
        "combined_runtime_path_projection": combined_path_projection,
        "header_projection_tree_sha256": directories[
            "header_projection"]["tree_sha256"],
        "fresh_process_projection_replay_verified": True,
        "all_source_to_runtime_links_verified_untimed": True,
    }
    if provenance != expected_provenance:
        raise RuntimeError("Goal5802 runtime build provenance binding differs")
    formal_preflight_contract = value.get("formal_preflight_contract")
    if formal_preflight_contract != {
            "required_before_worker_zero": True,
            "python_startup_flags_exact": ["-I", "-S", "-B", "-P", "-c"],
            "controlled_site_packages_injection_required": True,
            "controlled_host_code_snapshot_import_required": True,
            "pth_execution_in_build_kat_preflight_or_formal": False,
            "live_target_all_fields_equal": True,
            "exact_loader_environment_replayed": True,
            "direct_nvrtc_v2_compile_identity_required": True,
            "fresh_python_matched_ptx_identity_required": True,
            "clean_python_rtdsl_package_import_identity_required": True,
            "cross_arm_libnvrtc_builtins_version_equal_required": True,
            "any_mismatch": "TERMINATE_BEFORE_WORKER_ZERO",
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
    } or not isinstance(formal_preflight_contract, Mapping) \
            or any(type(formal_preflight_contract.get(key)) is not int
                   or formal_preflight_contract[key] != 0 for key in (
                       "registered_performance_timing_count",
                       "gpu_kernel_launch_count")):
        raise RuntimeError("Goal5802 formal runtime preflight contract differs")
    host_runtime_path = Path(str(files["host_runtime_provenance"]["path"]))
    host_runtime = json.loads(host_runtime_path.read_text(encoding="utf-8"))
    if not isinstance(host_runtime, dict):
        raise RuntimeError("Goal5802 host/runtime receipt is not an object")
    validate_host_runtime_provenance(host_runtime, files)
    numba_llvmlite_runtime_authority(host_runtime, files)
    unsigned_host_runtime = dict(host_runtime)
    observed_host_runtime_sha = unsigned_host_runtime.pop("receipt_sha256", None)
    expected_host_runtime_fields = {
        "schema", "status", "python", "distributions",
        "loaded_module_files", "host", "thread_and_visibility_environment",
        "registered_performance_timing_count", "formal_worker_count",
        "receipt_sha256",
    }
    distribution_rows = host_runtime.get("distributions")
    distribution_names = ({row.get("name") for row in distribution_rows}
                          if isinstance(distribution_rows, list)
                          and all(isinstance(row, Mapping)
                                  for row in distribution_rows) else set())
    distributions_exact = isinstance(distribution_rows, list) and all(
        isinstance(row, Mapping)
        and set(row) == {"name", "version", "file_count", "payload_bytes",
                        "tree_sha256", "files"}
        and isinstance(row["name"], str)
        and isinstance(row["version"], str) and bool(row["version"])
        and type(row["file_count"]) is int and row["file_count"] > 0
        and type(row["payload_bytes"]) is int and row["payload_bytes"] > 0
        and _valid_sha256(row["tree_sha256"])
        and isinstance(row["files"], list)
        and all(isinstance(item, Mapping) and set(item) == {
                    "relative_path", "path", "bytes", "sha256"}
                and isinstance(item["relative_path"], str)
                and isinstance(item["path"], str)
                and type(item["bytes"]) is int and item["bytes"] >= 0
                and _valid_sha256(item["sha256"])
                and Path(str(item["path"])).is_absolute()
                and Path(str(item["path"])).is_file()
                and not Path(str(item["path"])).is_symlink()
                and Path(str(item["path"])).stat().st_size == item["bytes"]
                and sha256_file(Path(str(item["path"]))) == item["sha256"]
                for item in row["files"])
        and row["file_count"] == len(row["files"])
        and row["payload_bytes"] == sum(
            int(item["bytes"]) for item in row["files"])
        and row["tree_sha256"] == digest(row["files"])
        for row in distribution_rows)
    loaded_modules = host_runtime.get("loaded_module_files")
    loaded_modules_exact = isinstance(loaded_modules, Mapping) and all(
        isinstance(record, Mapping)
        and set(record) == {"path", "bytes", "sha256"}
        and isinstance(record["path"], str)
        and type(record["bytes"]) is int and record["bytes"] > 0
        and _valid_sha256(record["sha256"])
        and Path(str(record["path"])).is_absolute()
        and Path(str(record["path"])).is_file()
        and not Path(str(record["path"])).is_symlink()
        and Path(str(record["path"])).stat().st_size == record["bytes"]
        and sha256_file(Path(str(record["path"]))) == record["sha256"]
        for record in loaded_modules.values())
    python_record = host_runtime.get("python")
    python_executable = (python_record.get("executable")
                         if isinstance(python_record, Mapping) else None)
    clean_python = files["clean_python"]
    clean_python_path = clean_python.get(
        "resolved_path", clean_python.get("path"))
    python_exact = isinstance(python_record, Mapping) \
        and set(python_record) == {"version", "implementation", "executable"} \
        and isinstance(python_executable, Mapping) \
        and set(python_executable) == {"path", "bytes", "sha256"} \
        and python_executable.get("path") == clean_python_path \
        and python_executable.get("bytes") == clean_python["bytes"] \
        and python_executable.get("sha256") == clean_python["sha256"]
    expected_thread_environment = {
        key: os.environ.get(key) for key in (
            "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
            "PYTHONHASHSEED", "CUDA_VISIBLE_DEVICES",
            "PATH", "LD_LIBRARY_PATH", "LD_PRELOAD")}
    if set(host_runtime) != expected_host_runtime_fields \
            or host_runtime.get("schema") \
            != HOST_RUNTIME_SCHEMA \
            or host_runtime.get("status") \
            != "PASS__UNTIMED_EXACT_HOST_RUNTIME_CAPTURE" \
            or observed_host_runtime_sha != digest(unsigned_host_runtime) \
            or not distributions_exact \
            or [row.get("name") for row in distribution_rows] \
            != list(HOST_RUNTIME_DISTRIBUTIONS) \
            or not loaded_modules_exact \
            or set(loaded_modules or {}) != set(HOST_RUNTIME_MODULES) \
            or not python_exact \
            or host_runtime.get("host") != _current_host_projection() \
            or host_runtime.get("thread_and_visibility_environment") \
            != expected_thread_environment \
            or not expected_thread_environment["PATH"] \
            or any(not item or not Path(item).is_absolute()
                   for item in expected_thread_environment["PATH"].split(
                       os.pathsep)) \
            or expected_thread_environment["LD_PRELOAD"] is not None \
            or expected_thread_environment["LD_LIBRARY_PATH"] is not None and (
                not expected_thread_environment["LD_LIBRARY_PATH"]
                or any(not item or not Path(item).is_absolute()
                       for item in expected_thread_environment[
                           "LD_LIBRARY_PATH"].split(os.pathsep))) \
            or type(host_runtime.get(
                "registered_performance_timing_count")) is not int \
            or host_runtime["registered_performance_timing_count"] != 0 \
            or type(host_runtime.get("formal_worker_count")) is not int \
            or host_runtime["formal_worker_count"] != 0:
        raise RuntimeError("Goal5802 host/runtime provenance differs")
    operation_kat_path = Path(str(files["pyoptix_operation_kat"]["path"]))
    operation_kat = json.loads(operation_kat_path.read_text(encoding="utf-8"))
    if not isinstance(operation_kat, Mapping):
        raise RuntimeError("PyOptiX operation KAT is not an object")
    validate_pyoptix_operation_kat(operation_kat, files)
    direct_operation_kat_path = Path(str(files["direct_operation_kat"]["path"]))
    direct_operation_kat = json.loads(
        direct_operation_kat_path.read_text(encoding="utf-8"))
    if not isinstance(direct_operation_kat, Mapping):
        raise RuntimeError("Direct operation KAT is not an object")
    validate_direct_operation_kat(direct_operation_kat, files)
    rtdl_operation_kat_path = Path(str(files["rtdl_operation_kat"]["path"]))
    rtdl_operation_kat = json.loads(
        rtdl_operation_kat_path.read_text(encoding="utf-8"))
    if not isinstance(rtdl_operation_kat, Mapping):
        raise RuntimeError("RTDL operation KAT is not an object")
    validate_rtdl_operation_kat(
        rtdl_operation_kat, files, deployment_ids)
