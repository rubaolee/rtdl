#!/usr/bin/env python3
"""Standalone raw-byte recount for Goal5802.

This imports neither the primary evaluator nor a measured arm.  In formal use
it rehashes the authority/runtime and each receipt/stdout/stderr before it
independently checks identity, correctness, operation ledgers, statistics, and
the exact registered amortization equation.
"""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import random
import re
import shlex
import stat
import struct
from typing import Any, Mapping, Sequence
import zipfile


ARMS = (
    "A_DIRECT_CUDA_OPTIX",
    "B_NVIDIA_PYOPTIX_9_1_SOURCE_OPTIX_9_0_COMPAT_SCALAR_ONLY",
    "D_RTDL_CLEAN_INSTALLED_RTLEXE",
)
TASKS = (
    "CUSTOM_AABB_CLOSED_RELATION_COUNT_V2_MATCHED",
    "BUILTIN_TRIANGLE_WEIGHTED_SCALAR_V2_MATCHED",
)
REGIMES = ("DEPLOYMENT_COLD", "PREPARE", "STEADY_E2E")
DIRECT, PYOPTIX, RTDL = ARMS
RATIO_SPECS = (
    ("RTDL_OVER_PYOPTIX", RTDL, PYOPTIX),
    ("DIRECT_OVER_PYOPTIX", DIRECT, PYOPTIX),
    ("RTDL_OVER_DIRECT", RTDL, DIRECT),
)
THRESHOLDS = {"DEPLOYMENT_COLD": 1.10, "PREPARE": 1.10,
              "STEADY_E2E": 1.05}
FINAL_PROJECTION_CLAIM = (
    "OBSERVED_NVCC_DEPENDENCY_SET_UNDER_MATCHED_ARCH_AND_EXACT_HOST_CXX__"
    "EMPIRICALLY_SUFFICIENT_FOR_FRESH_PROCESS_EXACT_NVRTC_REPLAY__"
    "NOT_A_GENERAL_NVRTC_SUPERSET")
PREDICTION_AUTHORITY_PATH = (
    "history/internal_docs/"
    "goal5802_premeasurement_three_survival_question_prediction_freeze_"
    "20260824.json")
PREDICTION_AUTHORITY_COMMIT = "c064fab001469a69e29219e24d2059c75316d0c2"
PREDICTION_AUTHORITY_GIT_BLOB = "a3818a4bce842d7ab30986c2cd0b5c8f11a1a654"
PREDICTION_AUTHORITY_BYTES = 10538
PREDICTION_AUTHORITY_SHA256 = (
    "45812c3a5a371615752096e95f5156ded5ac7d19ed53466ed03239d6622855b6")
SUCCESSOR_FORECAST_SCHEMA = (
    "rtdl.goal5802.final_successor_subjective_forecast.v2")
SUCCESSOR_FORECAST_STATUS = (
    "FINAL_PRODUCT_TASK_AND_INSTRUMENT_BOUND__SUBJECTIVE_NO_INFERENTIAL_"
    "WEIGHT__FORMAL_EXECUTION_LOCKED")
SUCCESSOR_FORECAST_SEAL_DOMAIN = (
    b"RTDL-GOAL5802-FINAL-SUCCESSOR-FORECAST-V2")
SUCCESSOR_FORECAST_IDENTITY_KEYS = {
    "complete_product_binding_sha256",
    "workload_authority_sha256",
    "operation_contract_sha256",
    "comparative_schedule_sha256",
    "build_cold_absolute_schedule_sha256",
    "complete_instrument_source_manifest_sha256",
    "goal5799_repaired_contract_sha256",
}
SUCCESSOR_FORECAST_GATES = {
    regime: f"CI_UPPER_LE_{threshold:.2f}"
    for regime, threshold in THRESHOLDS.items()
}
SUCCESSOR_FORECAST_PREDECESSOR_PROBABILITIES = {
    (TASKS[0], "DEPLOYMENT_COLD"): 0.55,
    (TASKS[0], "PREPARE"): 0.75,
    (TASKS[0], "STEADY_E2E"): 0.60,
    (TASKS[1], "DEPLOYMENT_COLD"): 0.60,
    (TASKS[1], "PREPARE"): 0.80,
    (TASKS[1], "STEADY_E2E"): 0.70,
}
SUCCESSOR_FORECAST_PREDECESSOR_AUTHORITY = {
    "schema": "rtdl.goal5802.three_survival_question_prediction_freeze.v1",
    "path": PREDICTION_AUTHORITY_PATH,
    "authority_commit": PREDICTION_AUTHORITY_COMMIT,
    "git_blob_sha1": PREDICTION_AUTHORITY_GIT_BLOB,
    "canonical_utf8_lf_bytes": PREDICTION_AUTHORITY_BYTES,
    "canonical_utf8_lf_sha256": PREDICTION_AUTHORITY_SHA256,
    "role": "CALIBRATION_PREDECESSOR_ONLY__NOT_CURRENT_FORECAST",
}
SUCCESSOR_FORECAST_CHANGE_ROWS = (
    {
        "change_id": "FINAL_PRODUCT_IDENTITY_BOUND",
        "description": (
            "The successor binds the complete final clean-installed product "
            "rather than the predecessor product commit."),
        "expected_ratio_pressure": "AMBIGUOUS",
    },
    {
        "change_id": "V2_MATCHED_TASK_IDENTITIES_BOUND",
        "description": (
            "Both final V2 matched workloads replace the predecessor V1 task "
            "identities."),
        "expected_ratio_pressure": "AMBIGUOUS",
    },
    {
        "change_id": (
            "RELATION_SEMANTIC_COMPACTION_CAPACITY_AND_SCRATCH_INCLUDED"),
        "description": (
            "The relation forecast includes device semantic compaction, its "
            "exact key capacity, and exact scratch allocation projected from "
            "the final operation contract."),
        "expected_ratio_pressure": "UPWARD_RTDL_OVER_PYOPTIX",
    },
    {
        "change_id": (
            "RTDL_HELPER_KERNEL_MEMSET_AND_PARAMETER_H2D_COSTS_INCLUDED"),
        "description": (
            "The forecast includes each arm's helper launches, memsets, and "
            "execution-parameter H2D bytes."),
        "expected_ratio_pressure": "UPWARD_RTDL_OVER_PYOPTIX",
    },
    {
        "change_id": "RTDL_TRIANGLE_DYNAMIC_UPLOAD_COST_INCLUDED",
        "description": (
            "The RTDL and baseline triangle first-execute upload counts and "
            "bytes are projected separately from the final operation contract."),
        "expected_ratio_pressure": "UPWARD_RTDL_OVER_PYOPTIX",
    },
    {
        "change_id": "NATIVE_27_FIELD_OPERATION_RECEIPT_INCLUDED",
        "description": (
            "The exact native 27-field operation receipt is represented and "
            "its serialization remains outside the primary timer."),
        "expected_ratio_pressure": "NO_PRIMARY_TIMER_EFFECT",
    },
    {
        "change_id": "RTDLEXE_DEPLOYMENT_VALIDATION_INCLUDED",
        "description": (
            "The .rtdlexe authority and artifact validation cost is included "
            "in deployment-cold load/deploy."),
        "expected_ratio_pressure": "UPWARD_RTDL_OVER_PYOPTIX",
    },
    {
        "change_id": "COMPLETE_SYMMETRIC_INSTRUMENT_BOUND",
        "description": (
            "The successor binds the complete symmetric final instrument "
            "rather than an earlier partial harness."),
        "expected_ratio_pressure": "AMBIGUOUS",
    },
)
SUCCESSOR_FORECAST_CHANGE_IDS = tuple(
    row["change_id"] for row in SUCCESSOR_FORECAST_CHANGE_ROWS)
SUCCESSOR_FORECAST_OPERATION_PROJECTION = {
    "rtdl_native_operation_receipt_schema": (
        "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2"),
    "rtdl_native_operation_receipt_field_count": 27,
    "rtdlexe_deployment_validation_inside_deployment_cold_primary_timer": True,
    "rtdlexe_deployment_validation_inside_prepare_or_steady_primary_timer": False,
}
RTDSL_PACKAGE_PREFLIGHT_MODULES = (
    "rtdsl", "rtdsl.v4", "rtdsl.v4_callback_lifecycle",
    "rtdsl.v4_bounded_relation_optix_compiler",
    "rtdsl.v4_triangle_standard_library",
    "rtdsl.v4_triangle_reduction_optix_compiler",
    "rtdsl.v4_rtdlexe",
)
AUXILIARY_OPERATION_KEYS = {
    "semantic_compaction_launch_count",
    "semantic_compaction_key_capacity",
    "semantic_compaction_scratch_bytes",
    "callback_status_kernel_launch_count",
    "checked_product_kernel_launch_count",
    "compact_control_finalizer_kernel_launch_count",
    "total_auxiliary_cuda_kernel_launch_count",
    "execution_parameter_h2d_bytes",
    "execution_parameter_h2d_copy_call_count",
    "stream_ordered_memset_call_count",
    "status_d2h_copy_call_count",
    "output_d2h_copy_call_count",
}


def _independent_git_object_sha1(kind: str, payload: bytes) -> str:
    return hashlib.sha1(
        f"{kind} {len(payload)}\0".encode("ascii") + payload).hexdigest()


def _independent_parse_git_tree(
        payload: bytes) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    cursor = 0
    while cursor < len(payload):
        space = payload.find(b" ", cursor)
        nul = payload.find(b"\0", space + 1)
        if space <= cursor or nul <= space or nul + 21 > len(payload):
            raise RuntimeError("independent historical Git tree is malformed")
        try:
            mode = payload[cursor:space].decode("ascii")
            name = payload[space + 1:nul].decode("utf-8")
        except UnicodeError as error:
            raise RuntimeError(
                "independent historical Git tree name is invalid") from error
        rows.append((mode, name, payload[nul + 1:nul + 21].hex()))
        cursor = nul + 21
    if cursor != len(payload) or not rows:
        raise RuntimeError("independent historical Git tree is malformed")
    return rows


def _validate_prediction_git_path_proof(proof: object) -> None:
    """Offline-rehash the predecessor forecast's commit/tree/blob chain."""

    required = {
        "proof_schema", "commit_object_base64", "root_tree_sha1",
        "path_components", "tree_path_proof",
        "offline_commit_tree_blob_chain_rehash_required",
    }
    expected_components = list(Path(PREDICTION_AUTHORITY_PATH).parts)
    if not isinstance(proof, Mapping) or set(proof) != required \
            or proof.get("proof_schema") \
            != "rtdl.goal5802.git_commit_path_proof.v1" \
            or proof.get("path_components") != expected_components \
            or proof.get(
                "offline_commit_tree_blob_chain_rehash_required") is not True:
        raise RuntimeError("independent historical Git proof envelope differs")
    try:
        commit_payload = base64.b64decode(
            str(proof["commit_object_base64"]), validate=True)
    except (ValueError, TypeError) as error:
        raise RuntimeError(
            "independent historical Git commit encoding differs") from error
    if _independent_git_object_sha1("commit", commit_payload) \
            != PREDICTION_AUTHORITY_COMMIT:
        raise RuntimeError("independent historical Git commit rehash differs")
    first_line = commit_payload.split(b"\n", 1)[0]
    if not first_line.startswith(b"tree ") or len(first_line) != 45:
        raise RuntimeError("independent historical Git root tree absent")
    try:
        current_tree = first_line[5:].decode("ascii")
    except UnicodeError as error:
        raise RuntimeError(
            "independent historical Git root tree differs") from error
    if proof.get("root_tree_sha1") != current_tree:
        raise RuntimeError("independent historical Git root tree differs")
    rows = proof.get("tree_path_proof")
    if not isinstance(rows, list) or len(rows) != len(expected_components):
        raise RuntimeError("independent historical Git path proof differs")
    for index, (component, row) in enumerate(zip(expected_components, rows)):
        is_final = index == len(expected_components) - 1
        expected_kind = "blob" if is_final else "tree"
        required_row = {
            "component", "tree_sha1", "tree_object_base64", "selected_mode",
            "selected_kind", "selected_object_sha1",
        }
        if not isinstance(row, Mapping) or set(row) != required_row \
                or row.get("component") != component \
                or row.get("tree_sha1") != current_tree \
                or row.get("selected_kind") != expected_kind:
            raise RuntimeError("independent historical Git path proof differs")
        try:
            tree_payload = base64.b64decode(
                str(row["tree_object_base64"]), validate=True)
        except (ValueError, TypeError) as error:
            raise RuntimeError(
                "independent historical Git tree encoding differs") from error
        if _independent_git_object_sha1("tree", tree_payload) != current_tree:
            raise RuntimeError("independent historical Git tree rehash differs")
        matches = [entry for entry in _independent_parse_git_tree(tree_payload)
                   if entry[1] == component]
        if len(matches) != 1:
            raise RuntimeError("independent historical Git selection differs")
        mode, _, selected_object = matches[0]
        if row.get("selected_mode") != mode \
                or row.get("selected_object_sha1") != selected_object \
                or (is_final and mode != "100644") \
                or (not is_final and mode not in {"40000", "040000"}):
            raise RuntimeError("independent historical Git selection differs")
        current_tree = selected_object
    if current_tree != PREDICTION_AUTHORITY_GIT_BLOB:
        raise RuntimeError("independent historical Git blob selection differs")


def _expected_auxiliary_operation(arm: str, task: str) -> dict[str, int]:
    relation = task == TASKS[0]
    if arm == RTDL:
        return ({
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
            "status_d2h_copy_call_count": 1,
            "output_d2h_copy_call_count": 1,
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
            "status_d2h_copy_call_count": 1,
            "output_d2h_copy_call_count": 1,
        })
    return ({
        "semantic_compaction_launch_count": 1,
        "semantic_compaction_key_capacity": 8192,
        "semantic_compaction_scratch_bytes": 98312,
        "callback_status_kernel_launch_count": 0,
        "checked_product_kernel_launch_count": 0,
        "compact_control_finalizer_kernel_launch_count": 0,
        "total_auxiliary_cuda_kernel_launch_count": 1,
        "execution_parameter_h2d_bytes": 240,
        "execution_parameter_h2d_copy_call_count": 2,
        "stream_ordered_memset_call_count": 4,
        "status_d2h_copy_call_count": 1,
        "output_d2h_copy_call_count": 1,
    } if relation else {
        "semantic_compaction_launch_count": 0,
        "semantic_compaction_key_capacity": 0,
        "semantic_compaction_scratch_bytes": 0,
        "callback_status_kernel_launch_count": 0,
        "checked_product_kernel_launch_count": 0,
        "compact_control_finalizer_kernel_launch_count": 0,
        "total_auxiliary_cuda_kernel_launch_count": 0,
        "execution_parameter_h2d_bytes": 120,
        "execution_parameter_h2d_copy_call_count": 1,
        "stream_ordered_memset_call_count": 3,
        "status_d2h_copy_call_count": 1,
        "output_d2h_copy_call_count": 1,
    })
LEGACY_LITERALS = (
    "experiments/goal5798_premeasurement/rtdl_worker.py",
    "experiments/goal5798_premeasurement/pyoptix_worker.py",
    "experiments/goal5798_premeasurement/direct_measurement.cpp",
)
SYMLINK_FILE_ROLES = {"clean_python", "cxx_compiler", "nvcc", "nvidia_smi"}
RUNTIME_FILE_ROLES = {
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
    "pyoptix_initializer",
    "pyoptix_extension", "rtdsl_init", "rtdlexe_module", "native_library",
    "trust_root", "trust_head", "trust_package", "relation_artifact",
    "relation_authority", "triangle_artifact", "triangle_authority",
}
RUNTIME_TOP_LEVEL_KEYS = {
    "schema", "status", "files", "directories", "deployment_ids",
    "pyoptix", "target_observation", "target_policy",
    "architecture_contract", "build_provenance",
    "formal_preflight_contract",
    "registered_performance_timing_count", "formal_worker_zero",
    "manifest_sha256",
}
PYOPTIX_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
PYOPTIX_TREE = "0bf0ec24efb4a43f129aee25dd265aa8149374e3"
OPTIX_HEADERS_COMMIT = "fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd"
OPTIX_HEADERS_TREE = "c30f1b41cb64f6cba6290d7ad82686cc84922267"
PYOPTIX_HISTORICAL_BUILD_RECEIPT_BYTES = 15901
PYOPTIX_HISTORICAL_BUILD_RECEIPT_SHA256 = (
    "ef7ec47448a4ef012094ee9f127a8844c030aaba8936cc09b78ba5e6efa7d2de")
PYOPTIX_HISTORICAL_SOURCE_FILE_COUNT = 72
PYOPTIX_HISTORICAL_SOURCE_SHA256 = (
    "fbe686453fbd22b00f680857c3d3ee4407699e25b5a06123c58f69f0f7a60c89")
PYOPTIX_HISTORICAL_HEADERS_ROOT = (
    "/home/lestat/work/goal5798_candidate_v8_prepare_run/upstream/optix-dev")
PYOPTIX_WHEEL_BYTES = 620161
PYOPTIX_WHEEL_SHA256 = (
    "a659ed6df6125daa9cd37481c957e592c234f1cf423edb6b55d91a0f00683c4b")
PYOPTIX_EXTENSION_MEMBER = "optix/_optix.cpython-312-x86_64-linux-gnu.so"
PYOPTIX_EXTENSION_BYTES = 2630616
PYOPTIX_EXTENSION_SHA256 = (
    "2e546d0daa497511c878dfd97c93266689ba4a3de1f563d4732137ac23ba0a36")
PYOPTIX_REQUIRED_DISTRIBUTIONS = {
    "pyoptix": "9.1.0",
    "numpy": "2.4.4",
    "cupy-cuda12x": "14.0.1",
    "cuda-python": "12.9.7",
    "cuda-bindings": "12.9.7",
    "cuda-pathfinder": "1.6.1",
    "numba": "0.65.1",
    "llvmlite": "0.47.0",
}
OFFLINE_PYOPTIX_VALIDATION_BOUNDARY = {
    "installed_measured_runtime_distribution_import_count": 0,
    "pyoptix_import_count": 0,
    "cupy_import_count": 0,
    "device_query_count": 0,
    "gpu_kernel_launch_count": 0,
    "registered_measurement_clock_read_count": 0,
    "formal_worker_count": 0,
    "registered_performance_timing_count": 0,
    "execution_authority_consumed": False,
    "self_hash_is_execution_authority": False,
    "caller_must_bind_exact_plan_before_run": True,
}
OFFLINE_PYOPTIX_PIP_POLICY = {
    "python_interpreter_executes_pip_module_without_script_or_shebang": True,
    "pip_loaded_via_runpy_with_site_disabled": True,
    "safe_path_enabled_for_every_build_command": True,
    "isolated": True,
    "no_index": True,
    "no_deps": True,
    "no_cache_dir": True,
    "no_compile": True,
    "exact_venv_site_packages_target": True,
    "prefix_mode_allowed": False,
    "implicit_download_allowed": False,
    "pip_script_or_shebang_invocation_allowed": False,
}


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_exact_canonical_json(path: Path, label: str) -> dict[str, Any]:
    """Read one canonical JSON object without trusting a product validator."""

    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"independent {label} is absent or symbolic")
    payload = path.read_bytes()

    def reject_duplicate_keys(
            pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise RuntimeError(
                    f"independent {label} has duplicate JSON key: {key}")
            value[key] = item
        return value

    try:
        value = json.loads(
            payload.decode("utf-8"), object_pairs_hook=reject_duplicate_keys,
            parse_constant=lambda item: (_ for _ in ()).throw(
                RuntimeError(
                    f"independent {label} has non-finite value: {item}")),
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(
            f"independent {label} is not UTF-8 JSON") from error
    if not isinstance(value, dict) or payload != _canonical(value) + b"\n":
        raise RuntimeError(
            f"independent {label} is not canonical object JSON plus LF")
    return value


def _independent_combined_venv_members(
        combined_root: Path) -> list[dict[str, object]]:
    """Recount every directory and file in the combined virtualenv."""

    venv = combined_root / "venv"
    if venv.is_symlink() or not venv.is_dir():
        raise RuntimeError("independent combined virtualenv is absent or symbolic")
    rows: list[dict[str, object]] = []
    for path in sorted(venv.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(
                f"independent combined virtualenv has symlink: {path}")
        metadata = path.stat()
        row: dict[str, object] = {
            "path": path.relative_to(combined_root).as_posix(),
            "mode": stat.S_IMODE(metadata.st_mode),
        }
        if stat.S_ISDIR(metadata.st_mode):
            row["kind"] = "DIRECTORY"
        elif stat.S_ISREG(metadata.st_mode):
            row.update({
                "kind": "REGULAR_FILE", "bytes": metadata.st_size,
                "sha256": _sha(path),
            })
        else:
            raise RuntimeError(
                f"independent combined virtualenv has special member: {path}")
        rows.append(row)
    if not rows:
        raise RuntimeError("independent combined virtualenv is empty")
    return rows


def _independent_regular_file_rows(
        root: Path, relative_root: str) -> list[dict[str, object]]:
    target = root / relative_root
    if target.is_symlink() or not target.is_dir():
        raise RuntimeError(
            f"independent combined-runtime tree differs: {relative_root}")
    rows: list[dict[str, object]] = []
    for path in sorted(target.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(
                f"independent combined-runtime symbolic member: {path}")
        if path.is_file():
            rows.append({
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha(path),
            })
    rows.sort(key=lambda row: str(row["path"]))
    return rows


def _validate_combined_runtime_root_independently(
        combined_root: Path) -> dict[str, Any]:
    """Reconstruct one generic runtime without assuming its consumer role."""

    root = combined_root.resolve(strict=True)
    if combined_root.is_symlink() or not root.is_dir() \
            or (root / "terminal_failure_receipt.json").exists():
        raise RuntimeError("independent generic combined-runtime root differs")
    receipt_path = root / "combined_runtime_receipt.json"
    receipt = _load_exact_canonical_json(
        receipt_path, "generic combined-runtime receipt")
    required_receipt_keys = {
        "schema", "status", "plan_sha256", "plan_file_sha256",
        "input_file_count", "input_tree_sha256", "input_files",
        "virtualenv_app_data_file_count",
        "virtualenv_app_data_tree_sha256", "virtualenv_app_data_files",
        "command_count", "commands_sha256",
        "installed_package_snapshot_sha256", "venv_member_count",
        "venv_member_tree_sha256", "venv_members",
        "expected_explicit_distributions",
        "unexpected_installed_distribution_count", "evidence_files",
        "pip_invocation_policy", "authority_boundary",
        "base_python_site_boundary", "execution_scope", "create_only",
        "receipt_sha256",
    }
    body = dict(receipt)
    seal = body.pop("receipt_sha256", None)
    if set(receipt) != required_receipt_keys \
            or receipt.get("schema") \
            != "rtdl.goal5802.combined_runtime_build_receipt.v1" \
            or receipt.get("status") \
            != "PASS__OFFLINE_CREATE_ONLY_COMBINED_RUNTIME_BUILT" \
            or seal != _digest(body) \
            or receipt.get("create_only") is not True \
            or type(receipt.get("unexpected_installed_distribution_count")) \
            is not int \
            or receipt["unexpected_installed_distribution_count"] != 0:
        raise RuntimeError("independent generic combined-runtime receipt differs")
    _exact_scalar_mapping(receipt.get("execution_scope"), {
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
        "clock_read_count": 0,
        "measured_arm_import_count": 0,
        "execution_authority_consumed": False,
    }, "generic combined-runtime execution scope")

    plan_path = root / "plan.json"
    plan = _load_exact_canonical_json(plan_path, "generic combined-runtime plan")
    plan_body = dict(plan)
    plan_seal = plan_body.pop("plan_sha256", None)
    commands = plan.get("commands")
    policy = plan.get("pip_invocation_policy")
    install = (commands[1].get("argv")
               if isinstance(commands, list) and len(commands) == 4
               and isinstance(commands[1], Mapping) else None)
    required_flags = (
        "--no-index", "--no-deps", "--no-cache-dir", "--no-compile",
        "--disable-pip-version-check", "--target",
    )
    forbidden_tokens = (
        "--index-url", "--extra-index-url", "--trusted-host", "--proxy",
        "http://", "https://", "ftp://", "git+http", "git+ssh",
    )
    if plan_seal != _digest(plan_body) \
            or plan.get("schema") \
            != "rtdl.goal5802.combined_runtime_plan.v1" \
            or plan.get("status") \
            != "FROZEN_LOCAL_INTEGRITY_PLAN__EXTERNAL_INPUT_AUTHORITY_REQUIRED" \
            or plan.get("output_directory") != str(root) \
            or receipt.get("plan_sha256") != plan_seal \
            or receipt.get("plan_file_sha256") != _sha(plan_path) \
            or not isinstance(commands, list) or len(commands) != 4 \
            or any(not isinstance(row, Mapping)
                   or set(row) != {"label", "argv"}
                   or not isinstance(row["argv"], list)
                   or row["argv"][1:5] != ["-I", "-S", "-B", "-P"]
                   for row in commands) \
            or not isinstance(install, list) \
            or install[1:6] != ["-I", "-S", "-B", "-P", "-c"] \
            or any(install.count(flag) != 1 for flag in required_flags) \
            or "--prefix" in install \
            or any(token in "\n".join(install).lower()
                   for token in forbidden_tokens) \
            or receipt.get("command_count") != 4 \
            or receipt.get("commands_sha256") != _digest(commands) \
            or not isinstance(policy, Mapping) \
            or policy.get(
                "pip_bytecode_compilation_during_install_forbidden") is not True \
            or policy.get(
                "site_initialization_disabled_for_every_build_command") is not True \
            or policy.get("pth_execution_during_build_forbidden") is not True \
            or receipt.get("pip_invocation_policy") != policy \
            or receipt.get("authority_boundary") \
            != plan.get("authority_boundary"):
        raise RuntimeError(
            "independent generic combined-runtime plan/policy differs")

    def validate_rows(value: object, label: str) -> list[dict[str, object]]:
        if not isinstance(value, list):
            raise RuntimeError(f"independent {label} is not a list")
        observed: list[dict[str, object]] = []
        seen: set[str] = set()
        for row in value:
            if not isinstance(row, Mapping) \
                    or set(row) != {"path", "bytes", "sha256"} \
                    or type(row.get("bytes")) is not int or row["bytes"] < 0 \
                    or not _valid_sha256(row.get("sha256")):
                raise RuntimeError(f"independent {label} row differs")
            relative = PurePosixPath(str(row["path"]))
            if relative.is_absolute() or ".." in relative.parts \
                    or relative.as_posix() != row["path"] \
                    or row["path"] in seen:
                raise RuntimeError(f"independent {label} path differs")
            seen.add(str(row["path"]))
            path = root / Path(*relative.parts)
            if path.is_symlink() or not path.is_file() \
                    or path.stat().st_size != row["bytes"] \
                    or _sha(path) != row["sha256"]:
                raise RuntimeError(f"independent {label} identity differs")
            observed.append(dict(row))
        return observed

    input_rows = validate_rows(receipt.get("input_files"), "generic input")
    expected_inputs: list[dict[str, object]] = []
    bootstrap = plan.get("virtualenv_bootstrap")
    wheels = plan.get("wheels")
    runner = plan.get("runner_source")
    if not isinstance(bootstrap, Mapping) \
            or not isinstance(bootstrap.get("files"), list) \
            or not isinstance(wheels, list) \
            or not isinstance(runner, Mapping):
        raise RuntimeError("independent generic input plan differs")
    for row in bootstrap["files"]:
        if not isinstance(row, Mapping):
            raise RuntimeError("independent generic bootstrap row differs")
        expected_inputs.append({
            "path": (PurePosixPath(str(bootstrap["saved_root"]))
                     / str(row["path"])).as_posix(),
            "bytes": row["bytes"], "sha256": row["sha256"],
        })
    for row in wheels:
        if not isinstance(row, Mapping):
            raise RuntimeError("independent generic wheel row differs")
        expected_inputs.append({
            "path": str(row["saved_path"]), "bytes": row["bytes"],
            "sha256": row["sha256"],
        })
    expected_inputs.append({
        "path": str(runner["saved_path"]), "bytes": runner["bytes"],
        "sha256": runner["sha256"],
    })
    expected_inputs.sort(key=lambda row: str(row["path"]))
    actual_inputs = _independent_regular_file_rows(root, "inputs")
    if input_rows != expected_inputs or input_rows != actual_inputs \
            or type(receipt.get("input_file_count")) is not int \
            or receipt["input_file_count"] != len(input_rows) \
            or receipt.get("input_tree_sha256") != _digest(input_rows):
        raise RuntimeError(
            "independent generic input tree differs: "
            f"receipt_vs_plan={input_rows == expected_inputs},"
            f"receipt_vs_actual={input_rows == actual_inputs},"
            f"receipt={len(input_rows)},plan={len(expected_inputs)},"
            f"actual={len(actual_inputs)}")

    app_data_rows = validate_rows(
        receipt.get("virtualenv_app_data_files"),
        "generic virtualenv app-data")
    # The producer seals Path-component traversal order.  A complete string
    # sort orders a sibling ``name.lock`` before descendants of ``name/``;
    # Path ordering does the reverse.  Preserve the sealed receipt order for
    # its digest, but compare complete filesystem coverage by canonical path.
    canonical_app_data_rows = sorted(
        app_data_rows, key=lambda row: str(row["path"]))
    if canonical_app_data_rows != _independent_regular_file_rows(
            root, "virtualenv_app_data") \
            or type(receipt.get("virtualenv_app_data_file_count")) is not int \
            or receipt["virtualenv_app_data_file_count"] != len(app_data_rows) \
            or receipt.get("virtualenv_app_data_tree_sha256") \
            != _digest(app_data_rows):
        raise RuntimeError("independent generic virtualenv app-data differs")

    evidence_rows = validate_rows(
        receipt.get("evidence_files"), "generic evidence")
    observed_evidence = [
        {"path": "plan.json", "bytes": plan_path.stat().st_size,
         "sha256": _sha(plan_path)},
    ]
    snapshot_path = root / "installed_packages.json"
    observed_evidence.append({
        "path": "installed_packages.json", "bytes": snapshot_path.stat().st_size,
        "sha256": _sha(snapshot_path),
    })
    observed_evidence.extend(
        _independent_regular_file_rows(root, "command_receipts"))
    if evidence_rows != observed_evidence:
        raise RuntimeError("independent generic evidence member set differs")

    members = _independent_combined_venv_members(root)
    if type(receipt.get("venv_member_count")) is not int \
            or receipt["venv_member_count"] != len(members) \
            or receipt.get("venv_member_tree_sha256") != _digest(members) \
            or receipt.get("venv_members") != members:
        raise RuntimeError("independent generic complete member tree differs")

    snapshot = _load_exact_canonical_json(
        snapshot_path, "generic installed-package snapshot")
    snapshot_body = dict(snapshot)
    snapshot_seal = snapshot_body.pop("snapshot_sha256", None)
    packages = snapshot.get("packages")
    if snapshot_seal != _digest(snapshot_body) \
            or snapshot.get("schema") \
            != "rtdl.goal5802.combined_runtime_package_snapshot.v1" \
            or snapshot.get("status") \
            != "PASS__COMPLETE_INSTALLED_DISTRIBUTION_SNAPSHOT" \
            or snapshot.get("site_module_imported") is not False \
            or not isinstance(packages, list) \
            or type(snapshot.get("package_count")) is not int \
            or snapshot["package_count"] != len(packages) \
            or receipt.get("installed_package_snapshot_sha256") \
            != snapshot_seal:
        raise RuntimeError("independent generic package snapshot differs")
    expected_distributions = {
        str(row.get("distribution")): str(row.get("version"))
        for row in wheels if isinstance(row, Mapping)
    }
    installed: dict[str, str] = {}
    owned_venv_files: set[str] = set()
    for package in packages:
        if not isinstance(package, Mapping) or set(package) != {
                "distribution", "metadata_name", "version", "file_count",
                "payload_bytes", "tree_sha256", "files"} \
                or not isinstance(package.get("distribution"), str) \
                or package["distribution"] in installed \
                or not isinstance(package.get("version"), str) \
                or not isinstance(package.get("files"), list):
            raise RuntimeError("independent generic package row differs")
        package_rows = []
        for row in package["files"]:
            if not isinstance(row, Mapping) \
                    or set(row) != {"path", "bytes", "sha256"}:
                raise RuntimeError(
                    "independent generic package file row differs")
            relative = PurePosixPath(str(row["path"]))
            path = root / "venv" / Path(*relative.parts)
            if relative.is_absolute() or ".." in relative.parts \
                    or path.is_symlink() or not path.is_file() \
                    or type(row.get("bytes")) is not int \
                    or path.stat().st_size != row["bytes"] \
                    or _sha(path) != row.get("sha256"):
                raise RuntimeError(
                    "independent generic package file identity differs")
            package_rows.append(dict(row))
            owned_venv_files.add(
                (PurePosixPath("venv") / relative).as_posix())
        if type(package.get("file_count")) is not int \
                or package["file_count"] != len(package_rows) \
                or type(package.get("payload_bytes")) is not int \
                or package["payload_bytes"] \
                != sum(int(row["bytes"]) for row in package_rows) \
                or package.get("tree_sha256") != _digest(package_rows):
            raise RuntimeError("independent generic package tree differs")
        installed[str(package["distribution"])] = str(package["version"])
    if receipt.get("expected_explicit_distributions") \
            != expected_distributions \
            or any(installed.get(name) != version
                   for name, version in expected_distributions.items()) \
            or set(installed) - set(expected_distributions) \
            - {"pip", "setuptools", "wheel"}:
        raise RuntimeError("independent generic distribution set differs")
    site_root = Path(str(snapshot.get("site_packages"))).resolve(strict=True)
    venv_root = (root / "venv").resolve(strict=True)
    try:
        site_relative = site_root.relative_to(venv_root)
    except ValueError as error:
        raise RuntimeError("independent generic site root escapes venv") from error
    actual_site_files = {
        path.relative_to(root).as_posix()
        for path in site_root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    site_prefix = (PurePosixPath("venv") / PurePosixPath(
        site_relative.as_posix())).as_posix().rstrip("/") + "/"
    owned_site_files = {
        path for path in owned_venv_files if path.startswith(site_prefix)
    }
    if not owned_site_files.issubset(actual_site_files) \
            or any((PurePosixPath(path).suffix == ".pyc"
                    or "__pycache__" in PurePosixPath(path).parts)
                   for package in packages
                   if isinstance(package, Mapping)
                   and package.get("distribution") in expected_distributions
                   for path in (
                       str(row.get("path"))
                       for row in package.get("files", [])
                       if isinstance(row, Mapping))):
        raise RuntimeError(
            "independent generic installed-package coverage differs: "
            f"unowned={sorted(actual_site_files - owned_site_files)[:8]},"
            f"missing={sorted(owned_site_files - actual_site_files)[:8]}")
    if not site_relative.parts:
        raise RuntimeError("independent generic site root differs")
    return receipt


def _validate_combined_runtime_independently(
        runtime: Mapping[str, Any]) -> dict[str, Any]:
    """Bind the manifest's executed Python/site to one complete venv receipt.

    This deliberately does not import the combined-runtime builder or its
    verifier.  It reconstructs the receipt seal and complete member tree from
    raw filesystem bytes, then proves that the interpreter and both installed
    packages named by the runtime manifest live inside that exact tree.
    """

    files = runtime.get("files")
    directories = runtime.get("directories")
    if not isinstance(files, Mapping) or not isinstance(directories, Mapping):
        raise RuntimeError("independent combined-runtime manifest rows absent")
    receipt_row = files.get("combined_runtime_receipt")
    if not isinstance(receipt_row, Mapping):
        raise RuntimeError("independent combined-runtime receipt row absent")
    receipt_path = Path(str(receipt_row.get("path")))
    if not receipt_path.is_absolute() \
            or receipt_path.name != "combined_runtime_receipt.json":
        raise RuntimeError("independent combined-runtime receipt path differs")
    combined_root = receipt_path.parent
    if combined_root.is_symlink() or not combined_root.is_dir():
        raise RuntimeError("independent combined-runtime root differs")
    _validate_combined_runtime_root_independently(combined_root)
    if (combined_root / "terminal_failure_receipt.json").exists():
        raise RuntimeError("independent combined-runtime is terminal-failed")
    receipt = _load_exact_canonical_json(
        receipt_path, "combined-runtime receipt")
    required_receipt_keys = {
        "schema", "status", "plan_sha256", "plan_file_sha256",
        "input_file_count", "input_tree_sha256", "input_files",
        "virtualenv_app_data_file_count",
        "virtualenv_app_data_tree_sha256", "virtualenv_app_data_files",
        "command_count", "commands_sha256",
        "installed_package_snapshot_sha256", "venv_member_count",
        "venv_member_tree_sha256", "venv_members",
        "expected_explicit_distributions",
        "unexpected_installed_distribution_count", "evidence_files",
        "pip_invocation_policy", "authority_boundary",
        "base_python_site_boundary", "execution_scope", "create_only",
        "receipt_sha256",
    }
    body = dict(receipt)
    seal = body.pop("receipt_sha256", None)
    if set(receipt) != required_receipt_keys \
            or receipt.get("schema") \
            != "rtdl.goal5802.combined_runtime_build_receipt.v1" \
            or receipt.get("status") \
            != "PASS__OFFLINE_CREATE_ONLY_COMBINED_RUNTIME_BUILT" \
            or seal != _digest(body) \
            or receipt.get("create_only") is not True \
            or receipt.get("unexpected_installed_distribution_count") != 0 \
            or receipt.get("execution_scope") != {
                "formal_worker_count": 0,
                "registered_performance_timing_count": 0,
                "gpu_kernel_launch_count": 0,
                "clock_read_count": 0,
                "measured_arm_import_count": 0,
                "execution_authority_consumed": False,
            }:
        raise RuntimeError("independent combined-runtime receipt differs")

    plan_path = combined_root / "plan.json"
    plan = _load_exact_canonical_json(plan_path, "combined-runtime plan")
    plan_body = dict(plan)
    plan_seal = plan_body.pop("plan_sha256", None)
    if plan_seal != _digest(plan_body) \
            or receipt.get("plan_sha256") != plan_seal \
            or receipt.get("plan_file_sha256") != _sha(plan_path):
        raise RuntimeError("independent combined-runtime plan binding differs")
    commands = plan.get("commands")
    policy = plan.get("pip_invocation_policy")
    install = (commands[1].get("argv")
               if isinstance(commands, list) and len(commands) == 4
               and isinstance(commands[1], dict) else None)
    if not isinstance(install, list) \
            or install.count("--no-compile") != 1 \
            or not isinstance(policy, dict) \
            or policy.get(
                "pip_bytecode_compilation_during_install_forbidden") is not True \
            or receipt.get("pip_invocation_policy") != policy \
            or receipt.get("command_count") != len(commands) \
            or receipt.get("commands_sha256") != _digest(commands):
        raise RuntimeError(
            "independent combined-runtime no-bytecode install policy differs")
    snapshot_path = combined_root / "installed_packages.json"
    snapshot = _load_exact_canonical_json(
        snapshot_path, "combined-runtime installed-package snapshot")
    snapshot_body = dict(snapshot)
    snapshot_seal = snapshot_body.pop("snapshot_sha256", None)
    if snapshot_seal != _digest(snapshot_body) \
            or receipt.get("installed_package_snapshot_sha256") \
            != snapshot_seal:
        raise RuntimeError(
            "independent combined-runtime package snapshot differs")

    members = _independent_combined_venv_members(combined_root)
    if receipt.get("venv_member_count") != len(members) \
            or receipt.get("venv_member_tree_sha256") != _digest(members) \
            or receipt.get("venv_members") != members:
        raise RuntimeError(
            "independent combined-runtime complete member tree differs")

    venv = combined_root / "venv"
    expected_python = (venv / "Scripts/python.exe" if os.name == "nt"
                       else venv / "bin/python")
    clean_python = Path(str(files.get("clean_python", {}).get("path")))
    package_root = Path(str(
        directories.get("rtdsl_package", {}).get("path")))
    pyoptix_initializer = Path(str(
        files.get("pyoptix_initializer", {}).get("path")))
    pyoptix_extension = Path(str(
        files.get("pyoptix_extension", {}).get("path")))
    rtdsl_init = Path(str(files.get("rtdsl_init", {}).get("path")))
    rtdlexe_module = Path(str(files.get("rtdlexe_module", {}).get("path")))
    site_packages = package_root.parent
    try:
        site_relative = site_packages.relative_to(venv)
    except ValueError as error:
        raise RuntimeError(
            "independent executed package site escapes combined runtime") \
            from error
    expected_site_shape = (
        len(site_relative.parts) == 2
        and tuple(part.lower() for part in site_relative.parts)
        == ("lib", "site-packages")
        if os.name == "nt" else
        len(site_relative.parts) == 3
        and site_relative.parts[0] == "lib"
        and re.fullmatch(r"python[0-9]+\.[0-9]+", site_relative.parts[1])
        is not None
        and site_relative.parts[2] == "site-packages"
    )
    if clean_python.absolute() != expected_python.absolute() \
            or not expected_site_shape \
            or package_root != site_packages / "rtdsl" \
            or rtdsl_init != package_root / "__init__.py" \
            or rtdlexe_module != package_root / "v4_rtdlexe.py" \
            or pyoptix_initializer != site_packages / "optix/__init__.py" \
            or pyoptix_extension.parent != site_packages / "optix":
        raise RuntimeError(
            "independent manifest interpreter/site is not the receipted venv")
    member_by_path = {str(row["path"]): row for row in members}
    for path in (
            expected_python, rtdsl_init, rtdlexe_module,
            pyoptix_initializer, pyoptix_extension):
        try:
            relative = path.relative_to(combined_root).as_posix()
        except ValueError as error:
            raise RuntimeError(
                "independent executed runtime file escapes combined root") \
                from error
        row = member_by_path.get(relative)
        record = next((value for value in files.values()
                       if isinstance(value, Mapping)
                       and Path(str(value.get("path"))) == path), None)
        if not isinstance(row, Mapping) or row.get("kind") != "REGULAR_FILE" \
                or not isinstance(record, Mapping) \
                or row.get("bytes") != record.get("bytes") \
                or row.get("sha256") != record.get("sha256"):
            raise RuntimeError(
                f"independent executed runtime file is outside receipt: {path}")
    return receipt


def _independent_controlled_python_command(
        runtime: Mapping[str, Any], *, import_root: Path,
        module: str | None = None, script: Path | None = None) -> list[str]:
    """Reconstruct the controller's site-disabled argv independently."""

    if (module is None) == (script is None):
        raise RuntimeError("independent controlled target cardinality differs")
    files = runtime["files"]
    directories = runtime["directories"]
    clean_python = Path(str(files["clean_python"]["path"])).absolute()
    clean_python.resolve(strict=True)
    source_root = import_root.resolve(strict=True)
    package_root = Path(str(directories["rtdsl_package"]["path"])).resolve(
        strict=True)
    site_packages = package_root.parent
    pyoptix_initializer = Path(
        str(files["pyoptix_initializer"]["path"])).resolve(strict=True)
    if package_root.name != "rtdsl" \
            or pyoptix_initializer.parent.parent != site_packages:
        raise RuntimeError("independent controlled package site differs")
    if module is not None:
        if not module or any(character.isspace() for character in module):
            raise RuntimeError("independent controlled module differs")
        target = module
        invoke = f"runpy.run_module({module!r},run_name='__main__')"
    else:
        assert script is not None
        target_path = script.resolve(strict=True)
        target = str(target_path)
        invoke = f"runpy.run_path({str(target_path)!r},run_name='__main__')"
    bootstrap = (
        "import runpy,sys;"
        "sys.dont_write_bytecode=True;"
        f"sys.path[:0]=[{str(source_root)!r},{str(site_packages)!r}];"
        f"sys.argv=[{target!r},*sys.argv[1:]];"
        f"{invoke}"
    )
    return [
        str(clean_python), "-I", "-S", "-B", "-P", "-c", bootstrap,
    ]


def _single_ptx_target_from_bytes(payload: bytes) -> str:
    """Read one actual PTX target directive, counting duplicate lines.

    A set-based parser would incorrectly accept two identical ``.target``
    directives.  The measurement authority requires exactly one directive in
    the retained PTX bytes, so preserve occurrence count before interpreting
    its value.
    """

    target_lines = [
        line.strip() for line in payload.splitlines()
        if line.lstrip().startswith(b".target")
    ]
    if len(target_lines) != 1:
        raise RuntimeError(
            "independent matched PTX target directive count differs")
    match = re.fullmatch(
        rb"\.target[ \t]+(sm_[0-9]+)(?:[ \t]*,[^\r\n]+)?[ \t]*",
        target_lines[0])
    if match is None:
        raise RuntimeError("independent matched PTX target is malformed")
    return match.group(1).decode("ascii")


def _validate_architecture_contract_independently(
        runtime: Mapping[str, Any], files: Mapping[str, Any],
        observation: Mapping[str, Any],
        ptx_receipt: Mapping[str, Any]) -> None:
    """Reconstruct architecture binding from raw PTX and RTDL artifacts."""

    cc_text = observation.get("compute_capability")
    if not isinstance(cc_text, str):
        raise RuntimeError("independent compute capability is absent")
    match = re.fullmatch(r"([0-9]+)\.([0-9]+)", cc_text)
    if match is None:
        raise RuntimeError("independent compute capability is not major.minor")
    major, minor = map(int, match.groups())
    if major <= 0 or minor < 0 or minor > 9 \
            or cc_text != f"{major}.{minor}":
        raise RuntimeError("independent compute capability is not canonical")
    cc_numbers = [major, minor]
    compute_target = f"compute_{major}{minor}"
    sm_target = f"sm_{major}{minor}"

    ptx_path = Path(str(files["matched_ptx"]["path"]))
    observed_ptx_target = _single_ptx_target_from_bytes(ptx_path.read_bytes())
    if observed_ptx_target != sm_target:
        raise RuntimeError("independent matched PTX target differs")

    artifact_rows: dict[str, object] = {}
    for prefix in ("relation", "triangle"):
        artifact = _load(Path(str(files[f"{prefix}_artifact"]["path"])))
        product = artifact.get("product_projection")
        toolchain = product.get("target_toolchain") \
            if isinstance(product, Mapping) else None
        metadata = product.get("ptx_metadata") \
            if isinstance(product, Mapping) else None
        provider = product.get("provider_key") \
            if isinstance(product, Mapping) else None
        if not all(isinstance(item, Mapping)
                   for item in (toolchain, metadata, provider)) \
                or toolchain.get("compute_capability") != cc_numbers \
                or metadata.get("target") != sm_target \
                or provider.get("target_compute_capability") != cc_numbers \
                or provider.get("ptx_target") != sm_target:
            raise RuntimeError(
                f"independent RTDL artifact architecture differs: {prefix}")
        artifact_rows[prefix] = {
            "artifact_sha256": files[f"{prefix}_artifact"]["sha256"],
            "target_toolchain_compute_capability": cc_numbers,
            "ptx_metadata_target": sm_target,
            "provider_target_compute_capability": cc_numbers,
            "provider_ptx_target": sm_target,
        }

    nvrtc = ptx_receipt.get("nvrtc_library")
    version = nvrtc.get("version") if isinstance(nvrtc, Mapping) else None
    if not isinstance(version, list) or len(version) != 2 \
            or not all(type(item) is int and item >= 0 for item in version):
        raise RuntimeError("independent NVRTC version differs")
    expected = {
        "compute_capability": cc_text,
        "nvrtc_compute_architecture": compute_target,
        "ptx_target": sm_target,
        "ptx_target_directive_count": 1,
        "rtdl_artifacts": artifact_rows,
        "libnvrtc_sha256": files["nvrtc_library"]["sha256"],
        "libnvrtc_builtins_sha256": files["nvrtc_builtins"]["sha256"],
        "libnvrtc_version": version,
        "fresh_process_projection_claim": FINAL_PROJECTION_CLAIM,
    }
    if runtime.get("architecture_contract") != expected:
        raise RuntimeError("independent architecture contract differs")


def _validate_runtime_envelope_independently(
        runtime: Mapping[str, Any]) -> None:
    unsigned = dict(runtime)
    observed = unsigned.pop("manifest_sha256", None)
    if set(runtime) != RUNTIME_TOP_LEVEL_KEYS \
            or runtime.get("schema") \
            != "rtdl.goal5802.target_runtime_manifest.v2" \
            or runtime.get("status") \
            != "PREPARED_UNTIMED__FORMAL_EXECUTION_LOCKED" \
            or not _plain_int(runtime.get(
                "registered_performance_timing_count")) \
            or runtime["registered_performance_timing_count"] != 0 \
            or runtime.get("formal_worker_zero") is not False \
            or observed != _digest(unsigned):
        raise RuntimeError("independent runtime manifest differs")


def _tree_identity(root: Path) -> dict[str, object]:
    root = root.resolve(strict=True)
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"independent runtime tree has symlink: {path}")
        if path.is_file():
            rows.append({
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha(path),
            })
        elif not path.is_dir():
            raise RuntimeError(f"independent runtime tree has special file: {path}")
    return {
        "file_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "tree_sha256": _digest(rows),
    }


def _independent_rtdsl_package_identity(root: Path) -> dict[str, object]:
    root = root.resolve(strict=True)
    if not root.is_dir() or root.name != "rtdsl":
        raise RuntimeError("independent installed rtdsl package root differs")
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(
                f"independent installed rtdsl package has symlink: {path}")
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            if relative.startswith("__pycache__/") or "/__pycache__/" in relative \
                    or relative.endswith((".pyc", ".pyo")):
                raise RuntimeError(
                    "independent installed rtdsl package has bytecode cache")
            rows.append({
                "path": f"rtdsl/{relative}",
                "bytes": path.stat().st_size,
                "sha256": _sha(path),
            })
        elif not path.is_dir():
            raise RuntimeError(
                "independent installed rtdsl package has special file")
    if not rows:
        raise RuntimeError("independent installed rtdsl package is empty")
    return {
        "file_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "tree_sha256": _digest(rows),
        "files": rows,
    }


def _independent_rtdsl_wheel_package_identity(wheel: Path) \
        -> dict[str, object]:
    wheel = wheel.resolve(strict=True)
    if not wheel.is_file() or wheel.is_symlink():
        raise RuntimeError("independent RTDL wheel path differs")
    dist = "rtdl_source_tree-4.0.0rc1.dist-info"
    allowed_dist = {
        f"{dist}/METADATA", f"{dist}/WHEEL", f"{dist}/top_level.txt",
        f"{dist}/RECORD",
    }
    rows: list[dict[str, object]] = []
    with zipfile.ZipFile(wheel) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or any(item.is_dir() for item in infos):
            raise RuntimeError("independent RTDL wheel member shape differs")
        for info in infos:
            name = info.filename
            posix = PurePosixPath(name)
            mode = info.external_attr >> 16
            if posix.is_absolute() or name != posix.as_posix() \
                    or not posix.parts or any(part in {"", ".", ".."}
                                              for part in posix.parts) \
                    or stat.S_ISLNK(mode):
                raise RuntimeError("independent RTDL wheel member unsafe")
            if name in allowed_dist:
                continue
            if not name.startswith("rtdsl/"):
                raise RuntimeError("independent RTDL wheel member escapes package")
            relative = name.removeprefix("rtdsl/")
            if not relative or relative.startswith("__pycache__/") \
                    or "/__pycache__/" in relative \
                    or relative.endswith((".pyc", ".pyo")):
                raise RuntimeError("independent RTDL wheel package member invalid")
            payload = archive.read(info)
            rows.append({
                "path": name, "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            })
    rows.sort(key=lambda row: str(row["path"]))
    if not rows:
        raise RuntimeError("independent RTDL wheel package empty")
    return {
        "file_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "tree_sha256": _digest(rows),
        "files": rows,
    }


def _independent_normalized_absolute(path: Path) -> Path:
    absolute = path.absolute()
    if not absolute.is_absolute() or not absolute.anchor:
        raise RuntimeError("independent dependency path is not absolute")
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        if part in {"", "."}:
            continue
        if part == "..":
            if current.is_symlink() or current.parent == current:
                raise RuntimeError(
                    "independent dependency parent normalization invalid")
            current = current.parent
        else:
            current = current / part
    return current


def _independent_symlink_chain(path: Path) -> list[dict[str, str]]:
    absolute = _independent_normalized_absolute(path)
    current = Path(absolute.anchor)
    pending = list(absolute.parts[1:])
    rows: list[dict[str, str]] = []
    steps = 0
    while pending:
        steps += 1
        if steps > 1024:
            raise RuntimeError("independent symlink chain exceeds bound")
        part = pending.pop(0)
        candidate = current / part
        if candidate.is_symlink():
            target = candidate.readlink()
            target_path = target if target.is_absolute() \
                else candidate.parent / target
            target_path = _independent_normalized_absolute(target_path)
            rows.append({
                "link_path": str(candidate),
                "link_target": str(target),
                "resolved_target": str(candidate.resolve(strict=True)),
            })
            pending = [*target_path.parts[1:], *pending]
            current = Path(target_path.anchor)
        else:
            current = candidate
    if current.resolve(strict=True) != absolute.resolve(strict=True):
        raise RuntimeError("independent dependency symlink chain differs")
    return rows


def _independent_projection_relative(path: Path) -> str:
    absolute = _independent_normalized_absolute(path)
    parts = list(absolute.parts)[1:]
    prefix = ["rootfs"]
    drive = absolute.drive.rstrip(":/\\")
    if drive:
        prefix.append(f"drive_{drive}")
    if any(part in {"", ".", ".."} or "/" in part or "\\" in part
           for part in parts):
        raise RuntimeError("independent dependency path is not projectable")
    return "/".join([*prefix, *parts])


def _parse_independent_make_dependencies(stdout: str) -> list[Path]:
    logical = stdout.replace("\\\r\n", " ").replace("\\\n", " ")
    if ":" not in logical:
        raise RuntimeError("independent dependency stdout lacks target")
    tokens = shlex.split(logical.split(":", 1)[1], posix=True)
    paths = [Path(token) for token in tokens]
    if not paths or any(not path.is_absolute() for path in paths):
        raise RuntimeError("independent dependency stdout paths invalid")
    return paths


def _validate_header_projection_independently(
        value: Mapping[str, Any], projection_root: Path) -> None:
    unsigned = dict(value)
    seal = unsigned.pop("receipt_sha256", None)
    required = {
        "schema", "status", "runs", "projection_root",
        "projection_file_count", "projection_payload_bytes",
        "projection_tree_sha256", "dependency_run_count", "closure_claim",
        "command_authority", "root_mappings",
        "clock_read_count", "gpu_kernel_launch_count", "formal_worker_count",
        "registered_performance_timing_count", "receipt_sha256",
    }
    root = projection_root.resolve(strict=True)
    if set(value) != required \
            or value.get("schema") \
            != "rtdl.goal5802.load_bearing_header_projection.v2" \
            or value.get("status") \
            != ("PASS__UNTIMED_OBSERVED_NVCC_SDK_HEADER_PROJECTION__"
                "FRESH_PROCESS_REPLAY_REQUIRED") \
            or value.get("closure_claim") != (
                "OBSERVED_NVCC_DEPENDENCY_SET_UNDER_MATCHED_ARCH_AND_"
                "EXACT_HOST_CXX__PROJECTED_SDK_HEADER_CANDIDATE__FRESH_"
                "PROCESS_EXACT_NVRTC_REPLAY_NOT_YET_ESTABLISHED__"
                "NOT_A_GENERAL_NVRTC_SUPERSET") \
            or value.get("projection_root") != str(root) \
            or value.get("dependency_run_count") != 3 \
            or any(not _plain_int(value.get(key)) or value[key] != 0 for key in (
                "clock_read_count", "gpu_kernel_launch_count",
                "formal_worker_count", "registered_performance_timing_count")) \
            or seal != _digest(unsigned):
        raise RuntimeError("independent header projection envelope differs")
    runs = value.get("runs")
    roles = (
        "matched_device_cuda_dependencies",
        "relation_compaction_cuda_dependencies",
        "direct_cpp_dependencies",
    )
    if not isinstance(runs, list) or [
            run.get("role") if isinstance(run, Mapping) else None
            for run in runs] != list(roles):
        raise RuntimeError("independent header projection runs differ")
    authority = value.get("command_authority")
    mappings = value.get("root_mappings")
    if not isinstance(authority, Mapping) or set(authority) != {
            "schema", "compute_capability", "nvcc_host_compiler_policy",
            "tools", "sources",
            "original_sdk_roots", "expected_commands"} \
            or authority.get("schema") \
            != "rtdl.goal5802.dependency_command_authority.v4" \
            or not isinstance(mappings, list) or len(mappings) != 2:
        raise RuntimeError("independent header authority differs")
    compute = authority.get("compute_capability")
    policy = authority.get("nvcc_host_compiler_policy")
    tools = authority.get("tools")
    sources = authority.get("sources")
    roots = authority.get("original_sdk_roots")
    expected_rows = authority.get("expected_commands")
    if not isinstance(compute, str) or not re.fullmatch(r"sm_[0-9]+", compute) \
            or policy != (
                "EXACT_CONFIGURED_CXX__NVCC_DEPENDENCY_ONLY__"
                "ALLOW_UNSUPPORTED_COMPILER_EXPLICIT") \
            or not isinstance(tools, Mapping) \
            or set(tools) != {"nvcc", "cxx"} \
            or not isinstance(sources, Mapping) \
            or set(sources) != {
                "matched_device_source", "relation_compaction_source",
                "direct_source"} \
            or not isinstance(roots, Mapping) \
            or set(roots) != {"optix_include", "cuda_include"} \
            or not isinstance(expected_rows, list):
        raise RuntimeError("independent header command inputs differ")

    def exact_file_record(record: object) -> dict[str, object]:
        if not isinstance(record, Mapping):
            raise RuntimeError("independent header file record malformed")
        path = _independent_normalized_absolute(Path(str(record.get("path"))))
        resolved = path.resolve(strict=True)
        observed = {
            "path": str(path), "resolved_path": str(resolved),
            "bytes": resolved.stat().st_size, "sha256": _sha(resolved),
        }
        if dict(record) != observed or not resolved.is_file():
            raise RuntimeError("independent header file identity differs")
        return observed

    for record in tools.values():
        exact_file_record(record)
    for record in sources.values():
        exact_file_record(record)
    root_paths: dict[str, Path] = {}
    for name, record in roots.items():
        if not isinstance(record, Mapping) or set(record) != {
                "path", "resolved_path"}:
            raise RuntimeError("independent SDK root record malformed")
        path = _independent_normalized_absolute(Path(str(record["path"])))
        resolved = path.resolve(strict=True)
        if not resolved.is_dir() or dict(record) != {
                "path": str(path), "resolved_path": str(resolved)}:
            raise RuntimeError("independent SDK root identity differs")
        root_paths[str(name)] = resolved
    cuda_common = [
        str(_independent_normalized_absolute(Path(str(tools["nvcc"]["path"])))),
        "-ccbin", str(Path(str(tools["cxx"]["resolved_path"]))),
        "-allow-unsupported-compiler", "-M", "-std=c++17",
        f"-arch={compute}",
        f"-I{root_paths['optix_include']}",
        f"-I{root_paths['cuda_include']}",
        f"-I{root_paths['cuda_include'] / 'nv'}",
    ]
    expected_commands = {
        roles[0]: [*cuda_common, str(Path(str(
            sources["matched_device_source"]["resolved_path"])))],
        roles[1]: [*cuda_common, str(Path(str(
            sources["relation_compaction_source"]["resolved_path"])))],
        roles[2]: [
            str(_independent_normalized_absolute(Path(str(
                tools["cxx"]["path"])))), "-M", "-std=c++17", "-O3",
            "-DNDEBUG", f"-I{root_paths['optix_include']}",
            f"-I{root_paths['cuda_include']}",
            f"-I{root_paths['cuda_include'] / 'nv'}",
            str(Path(str(sources["direct_source"]["resolved_path"])))],
    }
    rebuilt_rows = [{
        "role": role, "command": expected_commands[role],
        "command_sha256": _digest(expected_commands[role]),
    } for role in roles]
    if expected_rows != rebuilt_rows:
        raise RuntimeError("independent exact dependency commands differ")
    mapping_by_role: dict[str, Mapping[str, object]] = {}
    for mapping in mappings:
        if not isinstance(mapping, Mapping) or set(mapping) != {
                "role", "original_root", "projection_relative_root",
                "projected_root", "roots_distinct_and_nonoverlapping"} \
                or mapping.get("role") not in root_paths \
                or mapping.get("roots_distinct_and_nonoverlapping") is not True:
            raise RuntimeError("independent SDK root mapping malformed")
        role = str(mapping["role"])
        original = root_paths[role]
        relative = _independent_projection_relative(original)
        projected = root / Path(relative)
        if mapping.get("original_root") != str(original) \
                or mapping.get("projection_relative_root") != relative \
                or mapping.get("projected_root") != str(projected) \
                or original == projected \
                or original.is_relative_to(projected) \
                or projected.is_relative_to(original):
            raise RuntimeError("independent SDK root mapping differs")
        mapping_by_role[role] = mapping
    if set(mapping_by_role) != set(root_paths):
        raise RuntimeError("independent SDK root mapping roles differ")
    original_pair = [root_paths[name] for name in (
        "optix_include", "cuda_include")]
    projected_pair = [Path(str(mapping_by_role[name]["projected_root"]))
                      for name in ("optix_include", "cuda_include")]
    for first, second in (original_pair, projected_pair):
        if first == second or first.is_relative_to(second) \
                or second.is_relative_to(first):
            raise RuntimeError("independent SDK roots overlap")
    projected_paths: set[str] = set()
    for run in runs:
        if not isinstance(run, Mapping) or set(run) != {
                "role", "command", "tool", "exit_code", "stdout_utf8",
                "stdout_sha256", "stderr_utf8", "stderr_sha256",
                "dependency_occurrence_count", "unique_dependency_path_count",
                "duplicate_dependency_occurrence_count",
                "load_bearing_sdk_dependency_count",
                "provenance_only_dependency_count",
                "load_bearing_sdk_dependencies",
                "provenance_only_dependencies"}:
            raise RuntimeError("independent header projection run schema differs")
        command = run.get("command")
        stdout = run.get("stdout_utf8")
        stderr = run.get("stderr_utf8")
        tool = run.get("tool")
        if not isinstance(command, list) or not command \
                or not all(isinstance(item, str) and item for item in command) \
                or command != expected_commands.get(str(run.get("role"))) \
                or not isinstance(stdout, str) or not isinstance(stderr, str) \
                or run.get("exit_code") != 0 \
                or run.get("stdout_sha256") \
                != hashlib.sha256(stdout.encode()).hexdigest() \
                or run.get("stderr_sha256") \
                != hashlib.sha256(stderr.encode()).hexdigest() \
                or not isinstance(tool, Mapping) or set(tool) != {
                    "path", "resolved_path", "bytes", "sha256"}:
            raise RuntimeError("independent header projection process differs")
        tool_path = Path(command[0]).absolute()
        tool_resolved = tool_path.resolve(strict=True)
        if tool != {
                "path": str(tool_path), "resolved_path": str(tool_resolved),
                "bytes": tool_resolved.stat().st_size,
                "sha256": _sha(tool_resolved)}:
            raise RuntimeError("independent header projection tool differs")
        occurrences = _parse_independent_make_dependencies(stdout)
        unique: list[Path] = []
        seen: set[str] = set()
        for path in occurrences:
            key = str(_independent_normalized_absolute(path))
            if key not in seen:
                seen.add(key)
                unique.append(path)
        sdk_dependencies = run.get("load_bearing_sdk_dependencies")
        provenance_dependencies = run.get("provenance_only_dependencies")
        if run.get("dependency_occurrence_count") != len(occurrences) \
                or run.get("unique_dependency_path_count") != len(unique) \
                or run.get("duplicate_dependency_occurrence_count") \
                != len(occurrences) - len(unique) \
                or not isinstance(sdk_dependencies, list) \
                or not isinstance(provenance_dependencies, list) \
                or run.get("load_bearing_sdk_dependency_count") \
                != len(sdk_dependencies) \
                or run.get("provenance_only_dependency_count") \
                != len(provenance_dependencies) \
                or len(sdk_dependencies) + len(provenance_dependencies) \
                != len(unique):
            raise RuntimeError("independent header dependency count differs")
        dependency_rows = [*sdk_dependencies, *provenance_dependencies]
        by_original = {
            str(record.get("original_path")): record
            for record in dependency_rows if isinstance(record, Mapping)
        }
        if len(by_original) != len(dependency_rows) \
                or set(by_original) != {
                    str(_independent_normalized_absolute(path))
                    for path in unique}:
            raise RuntimeError("independent header dependency set differs")
        for raw_path in unique:
            original = _independent_normalized_absolute(raw_path)
            record = by_original[str(original)]
            if not isinstance(record, Mapping):
                raise RuntimeError("independent header dependency row differs")
            resolved = original.resolve(strict=True)
            root_roles = [
                role for role, sdk_root in root_paths.items()
                if original.is_relative_to(sdk_root)]
            if len(root_roles) > 1:
                raise RuntimeError("independent SDK roots overlap")
            classification = (
                "LOAD_BEARING_PROJECTED_SDK_HEADER" if root_roles
                else "PROVENANCE_ONLY_SOURCE_SYSTEM_OR_TOOLCHAIN")
            root_role = root_roles[0] if root_roles else None
            common_keys = {
                "original_path", "resolved_path", "symlink_chain", "bytes",
                "sha256", "classification", "sdk_root_role"}
            expected_keys = common_keys | ({
                "projection_path", "projected_bytes", "projected_sha256"}
                if root_roles else set())
            if set(record) != expected_keys \
                    or not resolved.is_file() \
                    or record.get("original_path") != str(original) \
                    or record.get("resolved_path") != str(resolved) \
                    or record.get("symlink_chain") \
                    != _independent_symlink_chain(original) \
                    or record.get("bytes") != resolved.stat().st_size \
                    or record.get("sha256") != _sha(resolved) \
                    or record.get("classification") != classification \
                    or record.get("sdk_root_role") != root_role:
                raise RuntimeError("independent header dependency bytes differ")
            if root_roles:
                relative = _independent_projection_relative(original)
                projected = root / Path(relative)
                if not projected.is_file() or projected.is_symlink() \
                        or record.get("projection_path") != relative \
                        or record.get("projected_bytes") \
                        != projected.stat().st_size \
                        or record.get("projected_sha256") != _sha(projected) \
                        or projected.read_bytes() != resolved.read_bytes():
                    raise RuntimeError(
                        "independent projected SDK dependency differs")
                projected_paths.add(relative)
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError("independent header projection has symlink")
        if path.is_file():
            rows.append({
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size, "sha256": _sha(path)})
        elif not path.is_dir():
            raise RuntimeError("independent header projection has special file")
    if {str(row["path"]) for row in rows} != projected_paths \
            or value.get("projection_file_count") != len(rows) \
            or value.get("projection_payload_bytes") \
            != sum(int(row["bytes"]) for row in rows) \
            or value.get("projection_tree_sha256") != _digest(rows):
        raise RuntimeError("independent header projection tree differs")


FRESH_TRACE_SELECTOR = (
    "open,openat,openat2,chdir,fchdir,execve,clone,clone3,fork,vfork")


def _plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _independent_regular_file_identity(path: Path) -> dict[str, object]:
    """Rehash one canonical, non-symlink regular file from raw bytes."""

    if not path.is_absolute() or path.is_symlink():
        raise RuntimeError("independent fresh replay file path is not canonical")
    resolved = path.resolve(strict=True)
    metadata = path.lstat()
    if resolved != path or not stat.S_ISREG(metadata.st_mode):
        raise RuntimeError("independent fresh replay payload is not regular")
    return {
        "path": str(path), "bytes": metadata.st_size, "sha256": _sha(path),
    }


def _independent_stable_regular_file_identity(
        path: Path) -> dict[str, object]:
    """Rehash a DSO through one no-follow descriptor with stability checks."""

    if not path.is_absolute():
        raise RuntimeError("independent DSO path is not absolute")
    before = path.lstat()
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode) \
            or path.resolve(strict=True) != path:
        raise RuntimeError("independent DSO path is not canonical regular file")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) \
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened_before = os.fstat(descriptor)
        identity = (opened_before.st_dev, opened_before.st_ino,
                    opened_before.st_size)
        if not stat.S_ISREG(opened_before.st_mode) \
                or identity != (before.st_dev, before.st_ino, before.st_size):
            raise RuntimeError("independent DSO path/open identities differ")
        digest_value = hashlib.sha256()
        byte_count = 0
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            digest_value.update(block)
            byte_count += len(block)
        opened_after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    after = path.lstat()
    if (opened_after.st_dev, opened_after.st_ino, opened_after.st_size) \
            != identity \
            or (after.st_dev, after.st_ino, after.st_size) != identity \
            or stat.S_ISLNK(after.st_mode) or not stat.S_ISREG(after.st_mode) \
            or byte_count != identity[2]:
        raise RuntimeError("independent DSO identity changed during rehash")
    return {
        "path": str(path), "bytes": byte_count,
        "sha256": digest_value.hexdigest(),
    }


def _independent_tree_rows(root: Path) -> list[dict[str, object]]:
    if not root.is_absolute() or root.is_symlink():
        raise RuntimeError("independent fresh replay tree root is not canonical")
    resolved = root.resolve(strict=True)
    if resolved != root or not root.is_dir():
        raise RuntimeError("independent fresh replay tree root differs")
    rows: list[dict[str, object]] = []
    # Reconstruct the manifest's POSIX string order rather than ``Path``
    # component order.  The two differ for real SDK layouts such as the
    # sibling pair ``bits/types.h`` and ``bits/types/FILE.h``.
    for path in sorted(
            root.rglob("*"),
            key=lambda item: item.relative_to(root).as_posix()):
        if path.is_symlink():
            raise RuntimeError("independent fresh replay tree has symlink")
        if path.is_file():
            rows.append({
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha(path),
            })
        elif not path.is_dir():
            raise RuntimeError("independent fresh replay tree has special file")
    return rows


def _decode_independent_strace_path(raw: str) -> str:
    try:
        value = ast.literal_eval(f'"{raw}"')
    except (SyntaxError, ValueError) as error:
        raise RuntimeError(
            "independent strace path escaping is not parseable") from error
    if not isinstance(value, str) or "\x00" in value:
        raise RuntimeError("independent strace path is invalid")
    return value


_INDEPENDENT_STABLE_PROC_OBSERVATIONS = {
    "/proc/self/maps", "/proc/thread-self/maps",
    "/proc/self/status", "/proc/thread-self/status",
}


def _independent_kernel_absolute(target: str) -> str:
    if not target.startswith("/"):
        raise RuntimeError(
            "independent successful-open target is not absolute")
    return str(PurePosixPath("/" + target.lstrip("/")))


def _independent_reject_dynamic_path(value: str, *, label: str) -> None:
    if not value.startswith("/"):
        return
    lexical = str(PurePosixPath("/" + value.lstrip("/")))
    if re.match(r"^/proc/[0-9]+(?:/|$)", lexical) \
            or lexical == "/proc/self" \
            or lexical.startswith("/proc/self/") \
            or lexical == "/proc/thread-self" \
            or lexical.startswith("/proc/thread-self/") \
            or lexical == "/dev/fd" \
            or lexical.startswith("/dev/fd/") \
            or lexical in {"/dev/stdin", "/dev/stdout", "/dev/stderr"}:
        raise RuntimeError(f"independent {label} uses dynamic procfs/fd path")


def _independent_kernel_target(
        raw_target: str, *, decoded_path: str, trace_pid: int) -> str:
    target = _decode_independent_strace_path(raw_target)
    normalized = _independent_kernel_absolute(target)
    if decoded_path in _INDEPENDENT_STABLE_PROC_OBSERVATIONS:
        leaf = decoded_path.rsplit("/", 1)[-1]
        if decoded_path.startswith("/proc/thread-self/"):
            match = re.fullmatch(
                r"/proc/[0-9]+/task/([0-9]+)/(maps|status)", normalized)
            if match is None or int(match.group(1)) != trace_pid \
                    or match.group(2) != leaf:
                raise RuntimeError(
                    "independent thread-self target differs")
        else:
            match = re.fullmatch(r"/proc/[0-9]+/(maps|status)", normalized)
            if match is None or match.group(1) != leaf:
                raise RuntimeError("independent self target differs")
        return normalized
    _independent_reject_dynamic_path(
        normalized, label="successful-open kernel target")
    return normalized


def _independent_failed_open_path(path: Path, *, decoded: str) -> str:
    if decoded in _INDEPENDENT_STABLE_PROC_OBSERVATIONS:
        return decoded
    _independent_reject_dynamic_path(decoded, label="failed-open spelling")
    normalized = str(path.resolve(strict=False))
    _independent_reject_dynamic_path(
        normalized, label="resolved failed-open spelling")
    return normalized


def _parse_independent_strace_accesses(
        payloads: Sequence[bytes], *, cwd: Path,
        trace_pids: Sequence[int]) -> list[dict[str, object]]:
    """Parse the preserved ``strace -ff`` bytes without a primary parser.

    Every access retains the PID from its trace filename.  Numeric-dirfd
    relative opens, truncated strings, unfinished calls, and a successful cwd
    change fail closed because their absolute authority cannot be reconstructed.
    """

    if len(payloads) != len(trace_pids) or not payloads \
            or len(set(trace_pids)) != len(trace_pids) \
            or any(not _plain_int(pid) or pid <= 0 for pid in trace_pids):
        raise RuntimeError("independent strace payload/PID cardinality differs")
    if not cwd.is_absolute() or not cwd.is_dir():
        raise RuntimeError("independent strace cwd differs")
    rows: list[dict[str, object]] = []
    for payload, filename_pid in zip(payloads, trace_pids):
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise RuntimeError("independent strace is not UTF-8") from error
        if "<unfinished ...>" in text or "resumed>" in text:
            raise RuntimeError("independent strace has unfinished syscall")
        for line in text.splitlines():
            prefix = re.match(r"^(?:\[pid\s+([0-9]+)\]\s+)?", line)
            assert prefix is not None
            inline_pid = int(prefix.group(1)) if prefix.group(1) else None
            if inline_pid is not None and inline_pid != filename_pid:
                raise RuntimeError("independent strace inline/file PID differs")
            body = line[prefix.end():]
            cwd_call = re.match(r"(chdir|fchdir)\(", body)
            if cwd_call is not None:
                if re.search(r"=\s*0\s*$", body):
                    raise RuntimeError("independent traced compiler changed cwd")
                continue
            call = re.match(r"(open|openat|openat2)\(", body)
            if call is None:
                continue
            syscall = call.group(1)
            if syscall == "open":
                match = re.match(r'open\("((?:\\.|[^"\\])*)"', body)
                dirfd = None
            else:
                match = re.match(
                    rf'{syscall}\(([^,]+),\s*"((?:\\.|[^"\\])*)"',
                    body)
                dirfd = match.group(1).strip() if match is not None else None
            result = re.search(
                r"=\s*(-?[0-9]+)(?:<(.*)>)?"
                r"(?:\s+[A-Z][A-Z0-9_]*(?:\s+\([^)]*\))?)?\s*$",
                body)
            if match is None or result is None:
                raise RuntimeError(
                    f"independent strace {syscall} line is not parseable")
            after_path = body[match.end():].lstrip()
            if not after_path.startswith(","):
                raise RuntimeError("independent strace path is truncated")
            raw = match.group(1) if syscall == "open" else match.group(2)
            decoded = _decode_independent_strace_path(raw)
            path = Path(decoded)
            if not path.is_absolute():
                if syscall != "open":
                    at_cwd = re.fullmatch(
                        r"AT_FDCWD(?:<(.*)>)?", str(dirfd))
                    if at_cwd is None or at_cwd.group(1) is None:
                        raise RuntimeError(
                            "independent relative open lacks -y cwd")
                    annotated = _decode_independent_strace_path(
                        at_cwd.group(1))
                    if _independent_kernel_absolute(annotated) != str(cwd):
                        raise RuntimeError(
                            "independent AT_FDCWD annotation differs")
                path = cwd / path
            result_code = int(result.group(1))
            raw_target = result.group(2)
            if result_code >= 0:
                if raw_target is None:
                    raise RuntimeError(
                        "independent successful open lacks -y target")
                normalized = _independent_kernel_target(
                    raw_target, decoded_path=decoded,
                    trace_pid=filename_pid)
            else:
                if raw_target is not None:
                    raise RuntimeError(
                        "independent failed open has kernel target")
                normalized = _independent_failed_open_path(
                    path, decoded=decoded)
            rows.append({
                "syscall": syscall,
                "path": decoded,
                "normalized_path": normalized,
                "kernel_target_path": (
                    normalized if raw_target is not None else None),
                "success": result_code >= 0,
                "result": result_code,
                "trace_pid": filename_pid,
            })
    if not rows:
        raise RuntimeError("independent strace has no file-open evidence")
    return rows


def _recount_independent_trace_document(
        value: object, *, cwd: Path, trace_prefix: Path,
        original_roots: Sequence[Path], projected_roots: Sequence[Path],
        required_projected: Sequence[Path], authority_pid: int,
        require_no_original_attempt: bool) -> dict[str, object]:
    if not isinstance(value, Mapping) or set(value) != {
            "trace_files", "trace_file_count", "traced_pids",
            "authority_pid", "file_open_attempt_count",
            "file_open_success_count", "successful_kernel_target_count",
            "all_successful_opens_kernel_resolved",
            "original_sdk_attempt_count",
            "original_sdk_success_count", "projected_sdk_attempt_count",
            "projected_sdk_success_count", "required_projected_header_paths",
            "required_projected_headers_observed_successfully",
            "normalized_access_sha256"}:
        raise RuntimeError("independent fresh replay trace schema differs")
    records = value.get("trace_files")
    if not isinstance(records, list) or not records:
        raise RuntimeError("independent fresh replay trace files absent")
    exact_records: list[dict[str, object]] = []
    pids: list[int] = []
    payloads: list[bytes] = []
    for record in records:
        if not isinstance(record, Mapping) or set(record) != {
                "path", "bytes", "sha256"}:
            raise RuntimeError("independent fresh replay trace row differs")
        path = Path(str(record.get("path")))
        exact = _independent_regular_file_identity(path)
        if dict(record) != exact or path.parent != trace_prefix.parent \
                or not path.name.startswith(trace_prefix.name + "."):
            raise RuntimeError("independent fresh replay trace path differs")
        suffix = path.name[len(trace_prefix.name) + 1:]
        if not suffix.isdigit() or str(int(suffix)) != suffix:
            raise RuntimeError("independent fresh replay trace PID differs")
        exact_records.append(exact)
        pids.append(int(suffix))
        payloads.append(path.read_bytes())
    if [str(row["path"]) for row in exact_records] \
            != sorted(str(row["path"]) for row in exact_records):
        raise RuntimeError("independent fresh replay trace order differs")
    accesses = _parse_independent_strace_accesses(
        payloads, cwd=cwd, trace_pids=pids)
    originals = [path.resolve(strict=True) for path in original_roots]
    projected = [path.resolve(strict=True) for path in projected_roots]
    original_rows = [
        row for row in accesses
        if any(Path(str(row["normalized_path"])).is_relative_to(root)
               for root in originals)]
    projected_rows = [
        row for row in accesses
        if any(Path(str(row["normalized_path"])).is_relative_to(root)
               for root in projected)]
    required = sorted(str(path.resolve(strict=True))
                      for path in required_projected)
    observed = {
        str(row["normalized_path"])
        for row in projected_rows
        if row["success"] is True and row["trace_pid"] == authority_pid
    }
    if authority_pid not in pids:
        raise RuntimeError("independent receipt PID absent from raw strace")
    if require_no_original_attempt and original_rows:
        raise RuntimeError(
            "independent projected child attempted original SDK access")
    if set(required) - observed:
        raise RuntimeError(
            "independent receipt PID did not open required projected headers")
    rebuilt = {
        "trace_files": exact_records,
        "trace_file_count": len(exact_records),
        "traced_pids": pids,
        "authority_pid": authority_pid,
        "file_open_attempt_count": len(accesses),
        "file_open_success_count": sum(
            row["success"] is True for row in accesses),
        "successful_kernel_target_count": sum(
            row["kernel_target_path"] is not None for row in accesses),
        "all_successful_opens_kernel_resolved": all(
            row["success"] is not True
            or row["kernel_target_path"] is not None for row in accesses),
        "original_sdk_attempt_count": len(original_rows),
        "original_sdk_success_count": sum(
            row["success"] is True for row in original_rows),
        "projected_sdk_attempt_count": len(projected_rows),
        "projected_sdk_success_count": sum(
            row["success"] is True for row in projected_rows),
        "required_projected_header_paths": required,
        "required_projected_headers_observed_successfully": (
            not bool(set(required) - observed)),
        "normalized_access_sha256": _digest(accesses),
    }
    if dict(value) != rebuilt:
        raise RuntimeError("independent raw strace recount differs")
    return rebuilt


def _validate_independent_loaded_nvrtc(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping) or set(value) != {
            "library", "builtins", "version"}:
        raise RuntimeError("independent loaded NVRTC schema differs")
    exact: dict[str, object] = {}
    for role in ("library", "builtins"):
        record = value.get(role)
        if not isinstance(record, Mapping) or set(record) != {
                "path", "bytes", "sha256", "canonical_regular_file",
                "symlink"}:
            raise RuntimeError("independent loaded NVRTC file row differs")
        observed = _independent_stable_regular_file_identity(
            Path(str(record.get("path"))))
        expected = {
            **observed, "canonical_regular_file": True, "symlink": False}
        if dict(record) != expected:
            raise RuntimeError("independent loaded NVRTC bytes differ")
        exact[role] = expected
    version = value.get("version")
    if not isinstance(version, list) or len(version) != 2 \
            or not all(_plain_int(item) and item >= 0 for item in version):
        raise RuntimeError("independent loaded NVRTC version differs")
    exact["version"] = list(version)
    if dict(value) != exact:
        raise RuntimeError("independent loaded NVRTC identity differs")
    return exact


def _validate_direct_loaded_nvrtc_independently(
        value: object) -> dict[str, object]:
    required = {
        "schema", "status", "discovery", "loaded_library_path",
        "loaded_library_bytes", "loaded_library_sha256",
        "loaded_builtins_path", "loaded_builtins_bytes",
        "loaded_builtins_sha256", "nvrtc_version", "nvrtc_compile_kat",
        "clock_read_count", "registered_performance_timing_count",
        "gpu_kernel_launch_count", "formal_worker_count",
    }
    if not isinstance(value, Mapping) or set(value) != required \
            or value.get("schema") \
            != "rtdl.goal5802.direct_loaded_nvrtc_identity.v2" \
            or value.get("status") != "PASS__UNTIMED_NO_GPU" \
            or value.get("discovery") != (
                "MINIMAL_NVRTC_COMPILE_THEN_DLADDR_NVRTCVERSION_AND_"
                "PROC_SELF_MAPS_UNIQUE_BUILTINS_REALPATH_OPEN_NOFOLLOW_FSTAT") \
            or any(not _plain_int(value.get(key)) or value[key] != 0 for key in (
                "clock_read_count", "registered_performance_timing_count",
                "gpu_kernel_launch_count", "formal_worker_count")):
        raise RuntimeError("independent Direct loaded NVRTC envelope differs")
    observed_library = _independent_stable_regular_file_identity(
        Path(str(value.get("loaded_library_path"))))
    observed_builtins = _independent_stable_regular_file_identity(
        Path(str(value.get("loaded_builtins_path"))))
    if Path(str(value.get("loaded_library_path"))).name != "libnvrtc.so" \
            and not Path(str(value.get("loaded_library_path"))).name.startswith(
                "libnvrtc.so.") \
            or Path(str(value.get("loaded_builtins_path"))).name \
            != "libnvrtc-builtins.so" \
            and not Path(str(value.get("loaded_builtins_path"))).name.startswith(
                "libnvrtc-builtins.so.") \
            or value.get("loaded_library_bytes") != observed_library["bytes"] \
            or value.get("loaded_library_sha256") != observed_library["sha256"] \
            or value.get("loaded_builtins_bytes") != observed_builtins["bytes"] \
            or value.get("loaded_builtins_sha256") \
            != observed_builtins["sha256"] \
            or os.stat(Path(str(value["loaded_library_path"]))).st_ino \
            == os.stat(Path(str(value["loaded_builtins_path"]))).st_ino \
            and os.stat(Path(str(value["loaded_library_path"]))).st_dev \
            == os.stat(Path(str(value["loaded_builtins_path"]))).st_dev:
        raise RuntimeError("independent Direct loaded NVRTC/builtins bytes differ")
    version = value.get("nvrtc_version")
    if not isinstance(version, Mapping) or set(version) != {"major", "minor"} \
            or not _plain_int(version.get("major")) \
            or not _plain_int(version.get("minor")) \
            or int(version["major"]) <= 0 or int(version["minor"]) < 0:
        raise RuntimeError("independent Direct loaded NVRTC version differs")
    kat = value.get("nvrtc_compile_kat")
    expected_source = (
        'extern "C" __global__ void goal5802_nvrtc_identity_probe() {}\n')
    if not isinstance(kat, Mapping) or set(kat) != {
            "source_utf8", "source_sha256", "compile_options",
            "product_bytes", "product_sha256", "compile_success",
            "program_destroyed"} \
            or kat.get("source_utf8") != expected_source \
            or kat.get("source_sha256") != hashlib.sha256(
                expected_source.encode()).hexdigest() \
            or kat.get("compile_options") != ["--std=c++11"] \
            or not _plain_int(kat.get("product_bytes")) \
            or int(kat["product_bytes"]) <= 0 \
            or not _valid_sha256(kat.get("product_sha256")) \
            or kat.get("compile_success") is not True \
            or kat.get("program_destroyed") is not True:
        raise RuntimeError("independent Direct minimal NVRTC compile KAT differs")
    return dict(value)


def _direct_nvrtc_identity_stdout_bytes(
        value: Mapping[str, Any]) -> bytes:
    """Rebuild the exact one-line stdout emitted by the Direct executable."""

    kat = value["nvrtc_compile_kat"]
    assert isinstance(kat, Mapping)
    return (
        '{"schema":"rtdl.goal5802.direct_loaded_nvrtc_identity.v2",'
        '"status":"PASS__UNTIMED_NO_GPU",'
        '"discovery":"MINIMAL_NVRTC_COMPILE_THEN_'
        'DLADDR_NVRTCVERSION_AND_PROC_SELF_MAPS_UNIQUE_BUILTINS_'
        'REALPATH_OPEN_NOFOLLOW_FSTAT",'
        '"loaded_library_path":'
        + json.dumps(value["loaded_library_path"], ensure_ascii=False)
        + ',"loaded_library_bytes":' + str(value["loaded_library_bytes"])
        + ',"loaded_library_sha256":"'
        + str(value["loaded_library_sha256"])
        + '","loaded_builtins_path":'
        + json.dumps(value["loaded_builtins_path"], ensure_ascii=False)
        + ',"loaded_builtins_bytes":' + str(value["loaded_builtins_bytes"])
        + ',"loaded_builtins_sha256":"'
        + str(value["loaded_builtins_sha256"])
        + '","nvrtc_version":{"major":'
        + str(value["nvrtc_version"]["major"])
        + ',"minor":' + str(value["nvrtc_version"]["minor"])
        + '},"nvrtc_compile_kat":{"source_utf8":'
        + json.dumps(kat["source_utf8"], ensure_ascii=False)
        + ',"source_sha256":"' + str(kat["source_sha256"])
        + '","compile_options":["--std=c++11"],"product_bytes":'
        + str(kat["product_bytes"])
        + ',"product_sha256":"' + str(kat["product_sha256"])
        + '","compile_success":true,"program_destroyed":true},'
        '"clock_read_count":0,"registered_performance_timing_count":0,'
        '"gpu_kernel_launch_count":0,"formal_worker_count":0}\n'
    ).encode("utf-8")


def _target_observation_projection_independently(
        value: object, *, files: Mapping[str, Any],
        expected_loader_environment: Mapping[str, object] | None = None,
        exact_frozen_document: Mapping[str, Any] | None = None,
        context: str = "target observation") -> dict[str, str]:
    """Reconstruct a v2 target observation without the primary validator."""

    observation_fields = (
        "gpu_name", "compute_capability", "driver_version",
        "cuda_driver_version", "cuda_toolkit_version", "optix_version")
    if not isinstance(value, Mapping):
        raise RuntimeError(f"independent {context} root differs")
    unsigned = dict(value)
    observed_seal = unsigned.pop("observation_sha256", None)
    if set(value) != {
            "schema", "status", "tools", "command_receipts",
            *observation_fields, "loader_environment", "clock_read_count",
            "registered_performance_timing_count", "gpu_kernel_launch_count",
            "formal_worker_count", "observation_sha256"} \
            or value.get("schema") \
            != "rtdl.goal5802.target_observation.v2" \
            or value.get("status") \
            != "PASS__UNTIMED_EXACT_TARGET_OBSERVATION" \
            or any(not _plain_int(value.get(key)) or value[key] != 0 for key in (
                "clock_read_count", "registered_performance_timing_count",
                "gpu_kernel_launch_count", "formal_worker_count")) \
            or observed_seal != _digest(unsigned):
        raise RuntimeError(f"independent {context} envelope differs")
    tools = value.get("tools")
    commands = value.get("command_receipts")
    if not isinstance(tools, Mapping) or set(tools) != {
            "nvidia_smi", "nvcc"} \
            or any(tools.get(role) != files[role]
                   for role in ("nvidia_smi", "nvcc")) \
            or not isinstance(commands, Mapping) \
            or set(commands) != {"nvidia_smi", "nvcc"}:
        raise RuntimeError(f"independent {context} tools differ")
    expected_commands = {
        "nvidia_smi": [
            files["nvidia_smi"]["path"],
            "--query-gpu=name,compute_cap,driver_version",
            "--format=csv,noheader,nounits"],
        "nvcc": [files["nvcc"]["path"], "--version"],
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
                f"independent {context} command differs: {role}")
    gpu_rows = str(commands["nvidia_smi"]["stdout_utf8"]).strip().splitlines()
    gpu_fields = ([item.strip() for item in gpu_rows[0].split(",")]
                  if len(gpu_rows) == 1 else [])
    nvcc_rows = str(commands["nvcc"]["stdout_utf8"]).strip().splitlines()
    projection = {
        "gpu_name": gpu_fields[0] if len(gpu_fields) == 3 else "",
        "compute_capability": gpu_fields[1] if len(gpu_fields) == 3 else "",
        "driver_version": gpu_fields[2] if len(gpu_fields) == 3 else "",
        "cuda_driver_version": value.get("cuda_driver_version"),
        "cuda_toolkit_version": nvcc_rows[-1] if nvcc_rows else "",
        "optix_version": value.get("optix_version"),
    }
    if any(not isinstance(item, str) or not item
           for item in projection.values()) \
            or any(value.get(key) != projection[key]
                   for key in observation_fields):
        raise RuntimeError(f"independent {context} projection differs")
    loader = value.get("loader_environment")
    if not isinstance(loader, Mapping) or set(loader) != {
            "LD_LIBRARY_PATH", "LD_PRELOAD"} \
            or loader.get("LD_PRELOAD") is not None \
            or any(item is not None and not isinstance(item, str)
                   for item in loader.values()) \
            or loader.get("LD_LIBRARY_PATH") is not None and (
                not loader["LD_LIBRARY_PATH"]
                or any(not item or not Path(item).is_absolute()
                       for item in loader["LD_LIBRARY_PATH"].split(os.pathsep))) \
            or expected_loader_environment is not None \
            and dict(loader) != dict(expected_loader_environment):
        raise RuntimeError(f"independent {context} loader environment differs")
    if exact_frozen_document is not None and dict(value) != dict(
            exact_frozen_document):
        raise RuntimeError(f"independent {context} frozen bytes differ")
    return projection


def _valid_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 \
        and all(ch in "0123456789abcdef" for ch in value)


def _independent_segment_intersects_box(
        query: Sequence[object], item: Sequence[object], *,
        reverse: bool) -> bool:
    if reverse:
        origin = (float(query[0]), float(query[1]))
        direction = (
            float(query[2]) - float(query[0]),
            float(query[3]) - float(query[1]))
    else:
        origin = (float(query[2]), float(query[1]))
        direction = (
            float(query[0]) - float(query[2]),
            float(query[3]) - float(query[1]))
    lower = (float(item[0]), float(item[1]))
    upper = (float(item[2]), float(item[3]))
    low, high = 0.0, 1.0
    for axis in range(2):
        if direction[axis] == 0.0:
            if origin[axis] < lower[axis] or origin[axis] > upper[axis]:
                return False
            continue
        first = (lower[axis] - origin[axis]) / direction[axis]
        second = (upper[axis] - origin[axis]) / direction[axis]
        low = max(low, min(first, second))
        high = min(high, max(first, second))
        if low > high:
            return False
    return True


def _independent_relation_row_counts(
        indexed: Sequence[Sequence[object]],
        sources: Sequence[Sequence[object]],
        minimum_overlap: float) -> dict[str, object]:
    rows: list[tuple[int, int]] = []
    counts = []
    for reverse in (False, True):
        boxes, queries = (sources, indexed) if reverse else (indexed, sources)
        before = len(rows)
        for query in queries:
            for item in boxes:
                if not _independent_segment_intersects_box(
                        query, item, reverse=reverse):
                    continue
                dx = max(0.0, min(float(query[2]), float(item[2]))
                         - max(float(query[0]), float(item[0])))
                dy = max(0.0, min(float(query[3]), float(item[3]))
                         - max(float(query[1]), float(item[1])))
                if dx * dy < minimum_overlap:
                    continue
                rows.append((
                    int(item[4]) if reverse else int(query[4]),
                    int(query[4]) if reverse else int(item[4])))
        counts.append(len(rows) - before)
    return {
        "kind": (
            "ROUTE_INDEPENDENT_CPU_SEGMENT_AABB_CANDIDATE_AND_"
            "CLOSED_OVERLAP_ENUMERATION"),
        "forward_raw_event_count": counts[0],
        "reverse_raw_event_count": counts[1],
        "raw_event_count": len(rows),
        "unique_event_count": len(set(rows)),
    }


def _independent_k_plus_one_authority() -> dict[str, object]:
    f32 = lambda item: struct.unpack("<f", struct.pack("<f", item))[0]
    maximum = (1 << 32) - 1
    indexed = [[f32(0.0), f32(0.0), f32(4.0), f32(4.0), maximum]]
    sources = [[f32(0.125), f32(2.0), f32(1.125), f32(3.0), item]
               for item in range(4097)]
    sources.append([f32(0.125), f32(2.0), f32(0.625), f32(3.0), 4097])
    minimum_overlap = f32(1.0)
    oracle = _independent_relation_row_counts(
        indexed, sources, minimum_overlap)
    zero_threshold = _independent_relation_row_counts(
        indexed, sources, f32(0.0))
    oracle.update({
        "minimum_overlap_f32_bits": struct.unpack(
            "<I", struct.pack("<f", minimum_overlap))[0],
        "sentinel_source_id": 4097,
        "sentinel_overlap_f32_bits": 0x3f000000,
        "zero_threshold_raw_event_count": zero_threshold["raw_event_count"],
        "zero_threshold_unique_event_count": zero_threshold[
            "unique_event_count"],
    })
    if oracle != {
            "kind": (
                "ROUTE_INDEPENDENT_CPU_SEGMENT_AABB_CANDIDATE_AND_"
                "CLOSED_OVERLAP_ENUMERATION"),
            "forward_raw_event_count": 4097,
            "reverse_raw_event_count": 0,
            "raw_event_count": 4097,
            "unique_event_count": 4097,
            "minimum_overlap_f32_bits": 0x3f800000,
            "sentinel_source_id": 4097,
            "sentinel_overlap_f32_bits": 0x3f000000,
            "zero_threshold_raw_event_count": 4098,
            "zero_threshold_unique_event_count": 4098,
            }:
        raise RuntimeError("independent K+1 CPU oracle differs")
    packed = bytearray(b"goal5802-relation-k-plus-one-v1\0")
    packed.extend(struct.pack("<II", len(indexed), len(sources)))
    packed.extend(struct.pack("<fII", minimum_overlap, 4096, 8192))
    for row in (*indexed, *sources):
        x0, y0, x1, y1, item = row
        packed.extend(struct.pack(
            "<ffffffI", x0, y0, f32(0.0), x1, y1, f32(0.0), item))
    value: dict[str, object] = {
        "task": TASKS[0], "indexed": indexed, "sources": sources,
        "minimum_overlap_f32": minimum_overlap, "semantic_capacity": 4096,
        "expected_rows": [],
        "expected_failure": {
            "raw_event_count": 4097, "unique_event_count": 4097,
            "overflowed": 1, "status": 0xffff5102,
            "semantic_capacity": 4096, "raw_capacity": 8192,
            "control_d2h_bytes": 16,
            "status_output_commit_blocking_boundary_count": 1,
            "application_output_exposed": False,
            "application_output_d2h_call_count": 0,
            "application_output_d2h_bytes": 0,
        },
        "oracle_derivation": oracle,
        "packed_input_sha256": hashlib.sha256(packed).hexdigest(),
    }
    value["workload_sha256"] = _digest(value)
    return value


def _validate_k_plus_one_independently(
        value: object, *, arm: str, extra_fields: set[str]) -> Mapping[str, Any]:
    authority = _independent_k_plus_one_authority()
    required = {
        "schema", "arm", "task", "workload_sha256",
        "packed_input_sha256", "indexed_count", "source_count",
        "raw_count_below_raw_capacity", "compact_control",
        "executed_parameter_projection",
        "status_output_commit_blocking_boundary_count",
        "application_output_exposed", "application_output_d2h_call_count",
        "application_output_d2h_bytes", "registered_performance_timing_count",
        "formal_worker_count", *extra_fields,
    }
    failure = authority["expected_failure"]
    assert isinstance(failure, dict)
    expected_control = {key: failure[key] for key in (
        "raw_event_count", "unique_event_count", "overflowed", "status",
        "semantic_capacity", "raw_capacity", "control_d2h_bytes")}
    if not isinstance(value, Mapping) or set(value) != required \
            or value.get("schema") \
            != "rtdl.goal5802.relation_k_plus_one_device_failure.v1" \
            or value.get("arm") != arm or value.get("task") != TASKS[0] \
            or value.get("workload_sha256") != authority["workload_sha256"] \
            or value.get("packed_input_sha256") \
            != authority["packed_input_sha256"] \
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
            or any(not _plain_int(value.get(key)) or value[key] != 0
                   for key in (
                       "application_output_d2h_call_count",
                       "application_output_d2h_bytes",
                       "registered_performance_timing_count",
                       "formal_worker_count")):
        raise RuntimeError(f"independent {arm} K+1 evidence differs")
    return value


def _sealed_receipt(path: Path, *, schema: str) -> dict[str, Any]:
    value = _load(path)
    if value.get("schema") != schema:
        raise RuntimeError(f"independent build receipt schema differs: {schema}")
    unsigned = dict(value)
    observed = unsigned.pop("receipt_sha256", None)
    if observed != _digest(unsigned):
        raise RuntimeError(f"independent build receipt seal differs: {schema}")
    return value


def _validate_operation_kat_independently(
        value: Mapping[str, Any], files: Mapping[str, Any], *,
        expected_source_sha256: str) -> None:
    """Recount the untimed guard receipt without importing the arm validator."""

    unsigned = dict(value)
    observed = unsigned.pop("receipt_sha256", None)
    if set(value) != {
            "schema", "status", "rows", "task_count",
            "guard_inside_comparative_timer", "source_boundary",
            "clock_read_count", "registered_performance_timing_count",
            "formal_worker_count", "untimed_optix_launch_count",
            "untimed_auxiliary_cuda_kernel_launch_count",
            "untimed_gpu_launch_count", "relation_k_plus_one_hostile",
            "receipt_sha256"} \
            or value.get("schema") \
            != "rtdl.goal5802.pyoptix_operation_guard_untimed_kat.v1" \
            or value.get("status") \
            != "PASS__UNTIMED_PREWORKER_OPERATION_GUARD" \
            or value.get("task_count") != 2 \
            or value.get("guard_inside_comparative_timer") is not False \
            or any(not _plain_int(value.get(key)) or value[key] != 0
                   for key in (
                       "clock_read_count",
                       "registered_performance_timing_count",
                       "formal_worker_count")) \
            or value.get("untimed_optix_launch_count") != 8 \
            or value.get("untimed_auxiliary_cuda_kernel_launch_count") != 3 \
            or value.get("untimed_gpu_launch_count") != 11 \
            or observed != _digest(unsigned):
        raise RuntimeError("independent PyOptiX operation KAT envelope differs")
    launcher = {
        "zero_on_stream": 1, "enqueue": 1, "enqueue_d2h": 2,
        "synchronize": 2,
    }
    class_names = ("DeferredRelationPrepared", "ScalarTrianglePrepared")
    boundary = value.get("source_boundary")
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
            or boundary.get("source_sha256") != expected_source_sha256 \
            or not _valid_sha256(boundary.get("method_ast_sha256")) \
            or boundary.get("launcher_call_shape") != launcher \
            or any(not _plain_int(boundary.get(key)) or boundary[key] != 0
                   for key in (
                       "direct_gpu_call_count",
                       "per_ray_host_materialization_count")) \
            or boundary.get("optix_validation_mode") != "OFF" \
            or boundary.get("optix_log_callback_mode") != "OFF" \
            or boundary.get("module_optimization_level") != "DEFAULT" \
            or boundary.get("module_debug_level") != "NONE" \
            or any(not _plain_int(boundary.get(key)) or boundary[key] != 0
                   for key in (
                       "formal_forensic_operation_count",
                       "formal_measurement_label_count")) \
            or boundary.get("relation_raw_capacity_policy") != (
                "2_TIMES_SEMANTIC_CAPACITY__RAW_STORAGE_SAFETY_ONLY__"
                "DEVICE_UNIQUE_GATE_REQUIRED") \
            or boundary.get("live_guard_shape") != {
                name: {
                    "timed_observer_count": 0,
                    "untimed_kat_observer_count": 1,
                    "timed_fast_core_call_count": 1,
                    "timed_observed_core_call_count": 0,
                    "untimed_observed_core_call_count": 1,
                    "observed_wrapper_common_fast_core_call_count": 1,
                    "timed_event_reset_count": 0,
                } for name in class_names} \
            or boundary.get("relation_canonicalization") != {
                "numpy_lexsort_call_count": 1,
                "numpy_adjacent_any_call_count": 0,
                "python_rowwise_builtin_calls": [],
            } \
            or boundary.get("execute_boundary_shape") != {
                "DeferredRelationPrepared": {
                    "launcher_calls": {
                        "zero_on_stream": 1, "fill_ff_on_stream": 1,
                        "enqueue_compaction": 1, "enqueue_d2d": 1,
                        "enqueue_d2h": 2, "synchronize": 2, "enqueue": 1,
                    },
                    "hidden_gpu_or_helper_calls": [],
                },
                "ScalarTrianglePrepared": {
                    "launcher_calls": launcher,
                    "hidden_gpu_or_helper_calls": [],
                }} \
            or boundary.get("formal_fast_result_shape") != {
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
        raise RuntimeError("independent PyOptiX operation KAT source differs")
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
        raise RuntimeError("independent PyOptiX dynamic boundary differs")
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
        raise RuntimeError("independent PyOptiX formal launcher differs")

    count_keys = {
        "prepare_device_allocation_call_count", "prepare_h2d_call_count",
        "prepare_pinned_host_allocation_call_count",
        "prepare_stream_creation_count", "execute_device_allocation_call_count",
        "execute_pinned_host_allocation_call_count",
        "execute_async_h2d_call_count", "execute_async_d2h_call_count",
        "execute_blocking_d2h_call_count", "execute_device_zero_fill_call_count",
        "execute_explicit_stream_sync_call_count", "execute_launch_call_count",
        "execute_stream_creation_call_count", "execute_stream_destroy_call_count",
    }

    def counts(**nonzero: int) -> dict[str, int]:
        result = {key: 0 for key in count_keys}
        result.update(nonzero)
        return result

    specs = {
        TASKS[0]: {
            "uploads": 2, "bytes": 212992, "builds": 1,
            "execute": counts(
                execute_async_h2d_call_count=2,
                execute_async_d2h_call_count=2,
                execute_device_zero_fill_call_count=4,
                execute_explicit_stream_sync_call_count=2,
                execute_launch_call_count=3),
            "prepare": counts(
                prepare_device_allocation_call_count=11,
                prepare_h2d_call_count=2,
                prepare_pinned_host_allocation_call_count=6,
                prepare_stream_creation_count=1),
            "order": [
                "control_reset", "max_key_reset", "unique_count_reset",
                "keys_fill_ff", "params0_h2d", "launch0",
                "params1_h2d", "launch1", "semantic_compaction",
                "unique_count_d2d", "control_d2h", "status_ready_sync",
                "unique_rows_d2h", "output_ready_sync"],
        },
        TASKS[1]: {
            "uploads": 2, "bytes": 524288, "builds": 0,
            "execute": counts(
                execute_async_h2d_call_count=1,
                execute_async_d2h_call_count=2,
                execute_device_zero_fill_call_count=3,
                execute_explicit_stream_sync_call_count=2,
                execute_launch_call_count=1),
            "prepare": counts(
                prepare_device_allocation_call_count=7,
                prepare_h2d_call_count=1,
                prepare_pinned_host_allocation_call_count=5,
                prepare_stream_creation_count=1),
            "order": [
                "per_ray_reset", "scalar_reset", "status_reset",
                "params_h2d", "launch", "status_d2h", "status_ready_sync",
                "scalar_d2h", "scalar_ready_sync"],
        },
    }
    guard = {
        "scope": "PYTHON_VISIBLE_TASK_OWNER_EXECUTE__NOT_CUPTI_OR_DRIVER_WIDE",
        "unapproved_device_allocation_call_count": 0,
        "unapproved_pinned_host_allocation_call_count": 0,
        "unapproved_blocking_asnumpy_call_count": 0,
        "unauthorized_direct_stream_sync_count": 0,
        "complete_driver_operation_observation_claimed": False,
    }
    rows = value.get("rows")
    if not isinstance(rows, list) or len(rows) != 2 \
            or [row.get("task") if isinstance(row, Mapping) else None
                for row in rows] != list(TASKS):
        raise RuntimeError("independent PyOptiX operation KAT tasks differ")
    expected_identity_common = {
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
        "prepare_operation_counts", "live_execute_guard_inside_timer"}
    dynamic_keys = {
        "prepared_input_reused", "dynamic_device_upload_call_count",
        "dynamic_device_upload_bytes", "dynamic_accel_build_count",
        "dynamic_explicit_sync_count", "dynamic_blocking_upload_call_count",
        "dynamic_input_generation"}
    for row in rows:
        expected_identity = dict(expected_identity_common)
        if row.get("task") == TASKS[0]:
            expected_identity.update({
                "compaction_cubin_path": files["compaction_cubin"]["path"],
                "compaction_cubin_sha256": files["compaction_cubin"]["sha256"],
                "retained_compaction_cubin_sha256": files[
                    "compaction_cubin"]["sha256"],
            })
        if not isinstance(row, Mapping) or set(row) != {
                "task", "first_execute", "reused_execute", "runtime_identity"} \
                or row.get("runtime_identity") != expected_identity:
            raise RuntimeError("independent PyOptiX operation KAT identity differs")
        spec = specs[str(row["task"])]
        for name, reused in (("first_execute", False), ("reused_execute", True)):
            projection = row.get(name)
            dynamic = projection.get("dynamic_input_receipt") \
                if isinstance(projection, Mapping) else None
            if not isinstance(projection, Mapping) \
                    or set(projection) != projection_keys \
                    or projection.get("independent_execute_guard") != guard \
                    or projection.get("execute_operation_counts") != spec["execute"] \
                    or projection.get("prepare_operation_counts") != spec["prepare"] \
                    or projection.get("operation_order") != spec["order"] \
                    or projection.get("live_execute_guard_inside_timer") is not True \
                    or not isinstance(dynamic, Mapping) \
                    or set(dynamic) != dynamic_keys \
                    or dict(dynamic) != {
                        "prepared_input_reused": reused,
                        "dynamic_device_upload_call_count": (
                            0 if reused else spec["uploads"]),
                        "dynamic_device_upload_bytes": (
                            0 if reused else spec["bytes"]),
                        "dynamic_accel_build_count": (
                            0 if reused else spec["builds"]),
                        "dynamic_explicit_sync_count": 0,
                        "dynamic_blocking_upload_call_count": 0,
                        "dynamic_input_generation": 1,
                    }:
                raise RuntimeError(
                    "independent PyOptiX operation KAT projection differs")
    hostile = _validate_k_plus_one_independently(
        value.get("relation_k_plus_one_hostile"), arm=PYOPTIX,
        extra_fields={
            "operation_order", "execute_operation_counts",
            "independent_execute_guard", "dynamic_input_receipt"})
    expected_counts = counts(
        execute_async_h2d_call_count=2,
        execute_async_d2h_call_count=1,
        execute_device_zero_fill_call_count=4,
        execute_explicit_stream_sync_call_count=1,
        execute_launch_call_count=3)
    if hostile.get("operation_order") != [
            "control_reset", "max_key_reset", "unique_count_reset",
            "keys_fill_ff", "params0_h2d", "launch0", "params1_h2d",
            "launch1", "semantic_compaction", "unique_count_d2d",
            "control_d2h", "status_ready_sync"] \
            or hostile.get("execute_operation_counts") != expected_counts \
            or hostile.get("independent_execute_guard") != guard \
            or hostile.get("dynamic_input_receipt") != {
                "prepared_input_reused": False,
                "dynamic_device_upload_call_count": 2,
                "dynamic_device_upload_bytes": 213096,
                "dynamic_accel_build_count": 1,
                "dynamic_explicit_sync_count": 0,
                "dynamic_blocking_upload_call_count": 0,
                "dynamic_input_generation": 1,
            }:
        raise RuntimeError("independent PyOptiX K+1 operation differs")


def _independent_direct_dynamic(*, relation: bool, reused: bool) \
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


def _independent_direct_operation(*, relation: bool) -> dict[str, object]:
    result: dict[str, object] = {
        **_expected_auxiliary_operation(DIRECT, TASKS[0] if relation else TASKS[1]),
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
        "dynamic_input_receipt": _independent_direct_dynamic(
            relation=relation, reused=True),
    }
    if relation:
        result["user_visible_output_bytes"] = 32768
    else:
        result.update({
            "device_intermediate_per_ray_bytes": 131072,
            "device_reset_bytes": 131084,
            "h2d_launch_parameter_bytes": 120,
        })
    return result


def _validate_direct_operation_kat_independently(
        value: Mapping[str, Any], files: Mapping[str, Any]) -> None:
    unsigned = dict(value)
    observed_seal = unsigned.pop("receipt_sha256", None)
    if set(value) != {
            "schema", "status", "rows", "task_count",
            "guard_inside_comparative_timer", "source_audit",
            "clock_read_count", "registered_performance_timing_count",
            "formal_worker_count", "untimed_optix_launch_count",
            "untimed_auxiliary_cuda_kernel_launch_count",
            "untimed_gpu_launch_count", "relation_k_plus_one_hostile",
            "receipt_sha256"} \
            or value.get("schema") \
            != "rtdl.goal5802.direct_operation_guard_untimed_kat.v1" \
            or value.get("status") \
            != "PASS__UNTIMED_PREWORKER_ACTUAL_DIRECT_OPERATION_GUARD" \
            or value.get("task_count") != 2 \
            or value.get("guard_inside_comparative_timer") is not False \
            or any(not _plain_int(value.get(key)) or value[key] != 0
                   for key in (
                       "clock_read_count",
                       "registered_performance_timing_count",
                       "formal_worker_count")) \
            or value.get("untimed_optix_launch_count") != 8 \
            or value.get("untimed_auxiliary_cuda_kernel_launch_count") != 3 \
            or value.get("untimed_gpu_launch_count") != 11 \
            or observed_seal != _digest(unsigned):
        raise RuntimeError("independent Direct operation KAT envelope differs")
    audit = value.get("source_audit")
    expected_wrapper_shape = {
        "upload_dynamic_async": {"cuMemcpyHtoDAsync": 1},
        "build_dynamic_custom_accel": {"optixAccelBuild": 1},
        "traced_h2d": {"cuMemcpyHtoDAsync": 1},
        "traced_d2h": {"cuMemcpyDtoHAsync": 1},
        "traced_d2d": {"cuMemcpyDtoDAsync": 1},
        "traced_sync": {"cuStreamSynchronize": 1},
        "traced_launch": {"optixLaunch": 1},
        "enqueue_relation_compaction": {"cuLaunchKernel": 1},
    }
    expected_observed_calls = {
        "cuMemcpyHtoDAsync": 2,
        "cuMemcpyDtoHAsync": 1,
        "cuMemcpyDtoDAsync": 1,
        "cuStreamSynchronize": 1,
        "cuLaunchKernel": 1,
        "optixLaunch": 1,
        "cuMemcpyHtoD": 0,
        "optixAccelBuild": 1,
        "optixDeviceContextSetCacheEnabled": 1,
        "sha256_bytes": 7,
        "cuMemsetD8Async": 7,
        "cuMemcpyDtoH": 0,
        "cuCtxSynchronize": 0,
        "cuEventSynchronize": 0,
        "download_vector": 0,
        "launch": 0,
        "run_relation": 0,
        "run_triangle": 0,
        "traced_h2d": 2,
        "traced_d2h": 5,
        "traced_sync": 5,
        "traced_launch": 2,
        "enqueue_launch": 3,
        "upload_dynamic_async": 5,
        "build_dynamic_custom_accel": 2,
    }
    if not isinstance(audit, Mapping) or set(audit) != {
            "schema", "status", "scope", "source_sha256",
            "wrapper_raw_call_shape", "loaded_nvrtc_identity_guard",
            "relation_raw_capacity_policy",
            "observed_call_shape", "relation_expected_dynamic",
            "triangle_expected_dynamic", "registered_performance_timing_count",
            "formal_worker_count"} \
            or audit.get("schema") \
            != "rtdl.goal5802.direct_source_operation_audit.v2" \
            or audit.get("status") \
            != "PASS__FORMAL_TRACE_FREE__UNTIMED_OBSERVER_SAME_TEMPLATE_CORE" \
            or audit.get("scope") != (
                "Goal5802-owned execute call graph; included Goal5796 "
                "preparation helpers remain outside this execute trace and "
                "are phase-reported") \
            or audit.get("source_sha256") \
            != files["direct_scalar_source"]["sha256"] \
            or audit.get("wrapper_raw_call_shape") != expected_wrapper_shape \
            or audit.get("loaded_nvrtc_identity_guard") != {
                "provenance": (
                    "MINIMAL_NVRTC_COMPILE_THEN_NVRTCVERSION_SYMBOL_TO_"
                    "DLADDR_AND_PROC_SELF_MAPS_UNIQUE_BUILTINS_TO_REALPATH_"
                    "TO_NOFOLLOW_REGULAR_FILE_EXACT_BYTES"),
                "accepts_caller_reported_path": False,
                "call_shape": {
                    "nvrtcVersion": 1,
                    "dladdr": 1,
                    "realpath": 1,
                    "lstat": 2,
                    "open": 1,
                    "fstat": 2,
                    "read": 2,
                    "sha256_bytes": 1,
                },
                "compile_kat_call_shape": {
                    "nvrtcCreateProgram": 1,
                    "nvrtcCompileProgram": 1,
                    "nvrtcGetProgramLogSize": 1,
                    "nvrtcGetProgramLog": 1,
                    "nvrtcGetPTXSize": 1,
                    "nvrtcGetPTX": 1,
                    "nvrtcDestroyProgram": 4,
                    "identity_sha256_bytes": 2,
                    "cuInit": 0,
                    "cuLaunchKernel": 0,
                    "optixLaunch": 0,
                },
                "builtins_maps_call_shape": {
                    "getline": 1,
                    "realpath": 1,
                    "sort": 1,
                    "unique": 1,
                    "loaded_regular_file_identity": 1,
                },
                "builtins_regular_file_call_shape": {
                    "realpath": 1,
                    "lstat": 2,
                    "open": 1,
                    "fstat": 2,
                    "read": 2,
                    "identity_sha256_bytes": 1,
                },
                "version_required": True,
                "minimal_compile_before_builtins_discovery_required": True,
                "builtins_current_process_maps_required": True,
                "builtins_unique_canonical_identity_required": True,
                "canonical_regular_file_required": True,
                "symlink_ambiguity_rejected": True,
                "clock_read_count": 0,
                "registered_performance_timing_count": 0,
                "gpu_kernel_launch_count": 0,
                "formal_worker_count": 0,
            } \
            or audit.get("relation_raw_capacity_policy") != (
                "2_TIMES_SEMANTIC_CAPACITY__RAW_STORAGE_SAFETY_ONLY__"
                "DEVICE_UNIQUE_GATE_REQUIRED") \
            or audit.get("observed_call_shape") != expected_observed_calls \
            or audit.get("relation_expected_dynamic") != {
                "dynamic_device_upload_call_count": 2,
                "dynamic_device_upload_bytes": 212992,
                "dynamic_blocking_upload_call_count": 0,
                "optix_launch_count": 2,
                "semantic_compaction_launch_count": 1,
                "semantic_compaction_key_capacity": 8192,
                "semantic_compaction_scratch_bytes": 98312,
                "total_auxiliary_cuda_kernel_launch_count": 1,
                "async_d2h_call_count": 2,
                "async_d2h_bytes": 32784,
                "status_output_commit_blocking_boundary_count": 2,
            } \
            or audit.get("triangle_expected_dynamic") != {
                "dynamic_device_upload_call_count": 2,
                "dynamic_device_upload_bytes": 524288,
                "dynamic_blocking_upload_call_count": 0,
                "optix_launch_count": 1,
                "total_auxiliary_cuda_kernel_launch_count": 0,
                "async_d2h_call_count": 2,
                "async_d2h_bytes": 12,
                "status_output_commit_blocking_boundary_count": 2,
            } \
            or not _plain_int(audit.get(
                "registered_performance_timing_count")) \
            or audit["registered_performance_timing_count"] != 0 \
            or not _plain_int(audit.get("formal_worker_count")) \
            or audit["formal_worker_count"] != 0:
        raise RuntimeError("independent Direct source audit differs")
    rows = value.get("rows")
    if not isinstance(rows, list) or len(rows) != 2 \
            or [row.get("task") if isinstance(row, Mapping) else None
                for row in rows] != list(TASKS):
        raise RuntimeError("independent Direct KAT tasks differ")
    optix_launches = auxiliary_launches = 0
    for row in rows:
        relation = row.get("task") == TASKS[0]
        command = [
            files["direct_scalar_worker"]["path"],
            "--local-untimed-functional", "--task", row.get("task"),
            "--ptx", files["matched_ptx"]["path"],
        ]
        if relation:
            command.extend([
                "--compaction-cubin", files["compaction_cubin"]["path"]])
        worker = row.get("worker_receipt") if isinstance(row, Mapping) else None
        if not isinstance(row, Mapping) or set(row) != {
                "task", "command", "exit_code", "stdout_utf8",
                "stdout_sha256", "stderr_utf8", "stderr_sha256",
                "worker_receipt"} \
                or row.get("command") != command \
                or row.get("exit_code") != 0 \
                or not isinstance(row.get("stdout_utf8"), str) \
                or row.get("stdout_sha256") != hashlib.sha256(
                    row["stdout_utf8"].encode("utf-8")).hexdigest() \
                or row.get("stderr_utf8") != "" \
                or row.get("stderr_sha256") != hashlib.sha256(b"").hexdigest() \
                or not isinstance(worker, Mapping):
            raise RuntimeError("independent Direct KAT process row differs")
        try:
            reconstructed_worker = json.loads(str(row["stdout_utf8"]))
        except json.JSONDecodeError as error:
            raise RuntimeError("independent Direct KAT stdout is not JSON") from error
        if reconstructed_worker != worker:
            raise RuntimeError("independent Direct KAT stdout differs")
        worker_fields = {
            "schema", "status", "arm", "worker_id", "freeze_file_sha256",
            "execution_authority_sha256", "runtime_manifest_sha256", "task",
            "regime", "registered_performance_timing_count",
            "phase_durations_ns", "execute_or_regime_durations_ns",
            "execution_lifecycle_receipts", "untimed_observed_operation_traces",
            "correctness", "operation_ledger",
            "receipt_serialization_inside_timer", "retained_executed_ptx_sha256",
            "close_inside_primary_timer",
        }
        if relation:
            worker_fields.update({
                "retained_compaction_cubin_sha256",
                "relation_k_plus_one_hostile"})
        phase_nulls = {
            "process_startup_and_admission": None,
            "input_materialization": None, "load_or_deploy": None,
            "prepare": None, "steady_warmups": None,
            "complete_execute": None,
            "measurement_evidence_materialization": None,
            "close": None, "post_execution_identity_validation": None,
        }
        if set(worker) != worker_fields \
                or worker.get("schema") \
                != "rtdl.goal5802.direct_scalar.worker.v1" \
                or worker.get("status") != "PASS" \
                or worker.get("arm") != DIRECT \
                or worker.get("task") != row["task"] \
                or worker.get("regime") != "LOCAL_UNTIMED" \
                or any(worker.get(key) != "" for key in (
                    "worker_id", "freeze_file_sha256",
                    "execution_authority_sha256", "runtime_manifest_sha256")) \
                or not _plain_int(worker.get(
                    "registered_performance_timing_count")) \
                or worker["registered_performance_timing_count"] != 0 \
                or worker.get("phase_durations_ns") != phase_nulls \
                or worker.get("execute_or_regime_durations_ns") != [] \
                or worker.get("receipt_serialization_inside_timer") is not False \
                or worker.get("close_inside_primary_timer") is not False \
                or worker.get("retained_executed_ptx_sha256") \
                != files["matched_ptx"]["sha256"] \
                or (relation and worker.get(
                    "retained_compaction_cubin_sha256")
                    != files["compaction_cubin"]["sha256"]):
            raise RuntimeError("independent Direct KAT worker differs")
        expected_lifecycle = [
            _independent_direct_dynamic(relation=relation, reused=False),
            _independent_direct_dynamic(relation=relation, reused=True),
        ]
        if worker.get("execution_lifecycle_receipts") != expected_lifecycle:
            raise RuntimeError("independent Direct KAT lifecycle differs")
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
        traces = worker.get("untimed_observed_operation_traces")
        if traces != [expected_trace, expected_trace]:
            raise RuntimeError("independent Direct KAT actual traces differ")
        optix_launches += sum(int(trace["optix_launch_count"]) for trace in traces)
        auxiliary_launches += sum(
            int(trace["compaction_launch_count"]) for trace in traces)
        if worker.get("operation_ledger") != _independent_direct_operation(
                relation=relation):
            raise RuntimeError("independent Direct KAT ledger differs")
        expected_correctness = ({
            "oracle_exact": True, "canonical_row_count": 4096,
            "canonical_rows": [[index, index] for index in range(4096)],
            "raw_event_count": 8192, "semantic_unique_count": 4096,
            "device_status": 0, "device_overflow": 0,
        } if relation else {
            "oracle_exact": True, "device_status": 0, "reduced_u64": 65530})
        if worker.get("correctness") != expected_correctness:
            raise RuntimeError("independent Direct KAT correctness differs")
    hostile = _validate_k_plus_one_independently(
        value.get("relation_k_plus_one_hostile"), arm=DIRECT,
        extra_fields={"observed_operation_trace", "dynamic_input_receipt"})
    expected_trace = {
        "optix_launch_count": 2, "compaction_launch_count": 1,
        "async_h2d_call_count": 2, "async_h2d_bytes": 240,
        "async_d2h_call_count": 1, "async_d2h_bytes": 16,
        "async_d2d_call_count": 1, "async_d2d_bytes": 4,
        "host_blocking_boundary_count": 1,
    }
    expected_dynamic = {
        "prepared_input_reused": False,
        "dynamic_device_upload_call_count": 2,
        "dynamic_device_upload_bytes": 213096,
        "dynamic_accel_build_count": 1,
        "dynamic_explicit_sync_count": 0,
        "dynamic_blocking_upload_call_count": 0,
        "dynamic_input_generation": 1,
    }
    if hostile.get("observed_operation_trace") != expected_trace \
            or hostile.get("dynamic_input_receipt") != expected_dynamic:
        raise RuntimeError("independent Direct K+1 operation differs")
    worker_hostile = rows[0]["worker_receipt"].get(
        "relation_k_plus_one_hostile")
    if worker_hostile != {
            key: item for key, item in hostile.items() if key not in {
                "arm", "workload_sha256",
                "registered_performance_timing_count", "formal_worker_count"}}:
        raise RuntimeError("independent Direct K+1 wrapper differs")
    optix_launches += 2
    auxiliary_launches += 1
    if optix_launches != value["untimed_optix_launch_count"] \
            or auxiliary_launches \
            != value["untimed_auxiliary_cuda_kernel_launch_count"] \
            or optix_launches + auxiliary_launches \
            != value["untimed_gpu_launch_count"]:
        raise RuntimeError("independent Direct KAT launch recount differs")


def _independent_rtdl_dynamic(*, task: str, reused: bool) \
        -> dict[str, object]:
    relation = task == TASKS[0]
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


def _independent_rtdl_native_operation(
        *, task: str, reused: bool) -> dict[str, object]:
    relation = task == TASKS[0]
    dynamic = _independent_rtdl_dynamic(task=task, reused=reused)
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
        **_expected_auxiliary_operation(RTDL, task),
        "status_d2h_copy_call_count": 1,
        "output_d2h_copy_call_count": 1,
    }


def _independent_rtdl_k_plus_one_operation() -> dict[str, object]:
    result = _independent_rtdl_native_operation(
        task=TASKS[0], reused=False)
    result.update({
        "host_blocking_boundary_count": 1,
        "output_d2h_bytes": 0,
        "dynamic_device_upload_bytes": 213096,
        "output_d2h_copy_call_count": 0,
    })
    return result


def _validate_rtdl_operation_kat_independently(
        value: Mapping[str, Any], files: Mapping[str, Any],
        deployment_ids: Mapping[str, Any], *,
        expected_executable_identities: Mapping[str, Any] | None = None) -> None:
    """Recount actual RTDL first/reuse receipts without primary validators."""

    unsigned = dict(value)
    observed = unsigned.pop("receipt_sha256", None)
    if set(value) != {
            "schema", "status", "rows", "task_count",
            "guard_inside_comparative_timer", "clock_read_count",
            "registered_performance_timing_count", "formal_worker_count",
            "untimed_optix_launch_count",
            "untimed_auxiliary_cuda_kernel_launch_count",
            "untimed_gpu_launch_count", "relation_k_plus_one_hostile",
            "receipt_sha256"} \
            or value.get("schema") \
            != "rtdl.goal5802.rtdl_operation_guard_untimed_kat.v1" \
            or value.get("status") \
            != "PASS__UNTIMED_PREWORKER_ACTUAL_RTDL_OPERATION_GUARD" \
            or value.get("task_count") != 2 \
            or value.get("guard_inside_comparative_timer") is not False \
            or any(not _plain_int(value.get(key)) or value[key] != 0
                   for key in (
                       "clock_read_count",
                       "registered_performance_timing_count",
                       "formal_worker_count")) \
            or value.get("untimed_optix_launch_count") != 8 \
            or value.get("untimed_auxiliary_cuda_kernel_launch_count") != 33 \
            or value.get("untimed_gpu_launch_count") != 41 \
            or observed != _digest(unsigned):
        raise RuntimeError("independent RTDL operation KAT envelope differs")
    if not isinstance(deployment_ids, Mapping) \
            or set(deployment_ids) != {"relation", "triangle"}:
        raise RuntimeError("independent RTDL KAT deployment ids differ")
    if expected_executable_identities is not None \
            and (set(expected_executable_identities) \
                 != {"relation", "triangle"}
                 or not all(_valid_sha256(item)
                            for item in expected_executable_identities.values())):
        raise RuntimeError("independent RTDL KAT expected identities differ")
    rows = value.get("rows")
    if not isinstance(rows, list) or len(rows) != 2 \
            or [row.get("task") if isinstance(row, Mapping) else None
                for row in rows] != list(TASKS):
        raise RuntimeError("independent RTDL KAT task rows differ")
    expected_output = {
        TASKS[0]: _digest([[index, index] for index in range(4096)]),
        TASKS[1]: _digest(65530),
    }
    summaries = {
        TASKS[0]: {
            "canonical_row_count": 4096,
            "raw_event_count": 8192,
            "semantic_unique_count": 4096,
        },
        TASKS[1]: {"reduced_u64": 65530},
    }
    optix_launches = auxiliary_launches = 0
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {
                "task", "deployment_identity", "runtime_identity",
                "first_execute", "reused_execute"}:
            raise RuntimeError("independent RTDL KAT row differs")
        task = str(row["task"])
        key = "relation" if task == TASKS[0] else "triangle"
        if row.get("deployment_identity") != {
                "artifact_sha256": files[f"{key}_artifact"]["sha256"],
                "authority_sha256": files[f"{key}_authority"]["sha256"],
                "trust_root_sha256": files["trust_root"]["sha256"],
                "trust_head_sha256": files["trust_head"]["sha256"],
                "trust_package_sha256": files["trust_package"]["sha256"],
                "native_sha256": files["native_library"]["sha256"],
                "deployment_id": deployment_ids[key],
                }:
            raise RuntimeError("independent RTDL KAT deployment differs")
        identity = row.get("runtime_identity")
        if not isinstance(identity, Mapping) or set(identity) != {
                "rtdsl_init_path", "rtdsl_init_sha256",
                "rtdlexe_module_path", "rtdlexe_module_sha256",
                "executed_executable_identity_sha256"} \
                or identity.get("rtdsl_init_path") \
                != files["rtdsl_init"]["path"] \
                or identity.get("rtdsl_init_sha256") \
                != files["rtdsl_init"]["sha256"] \
                or identity.get("rtdlexe_module_path") \
                != files["rtdlexe_module"]["path"] \
                or identity.get("rtdlexe_module_sha256") \
                != files["rtdlexe_module"]["sha256"] \
                or not _valid_sha256(identity.get(
                    "executed_executable_identity_sha256")):
            raise RuntimeError("independent RTDL KAT runtime identity differs")
        executable = identity["executed_executable_identity_sha256"]
        if expected_executable_identities is not None \
                and executable != expected_executable_identities[key]:
            raise RuntimeError("independent RTDL KAT executable differs")
        for field, reused in (("first_execute", False),
                              ("reused_execute", True)):
            projection = row.get(field)
            operation = _independent_rtdl_native_operation(
                task=task, reused=reused)
            if not isinstance(projection, Mapping) or set(projection) != {
                    "dynamic_input_receipt", "native_operation_receipt",
                    "output_canonical_sha256", "product_output_sha256",
                    "executable_identity_sha256", "oracle_exact",
                    "device_status_ok", "output_summary", "role_counters"} \
                    or projection.get("dynamic_input_receipt") \
                    != _independent_rtdl_dynamic(task=task, reused=reused) \
                    or projection.get("native_operation_receipt") != operation \
                    or projection.get("output_canonical_sha256") \
                    != expected_output[task] \
                    or projection.get("product_output_sha256") is not None \
                    or projection.get("executable_identity_sha256") != executable \
                    or projection.get("oracle_exact") is not True \
                    or projection.get("device_status_ok") is not True \
                    or projection.get("output_summary") != summaries[task] \
                    or projection.get("role_counters") != []:
                raise RuntimeError("independent RTDL KAT execution differs")
            optix_launches += int(operation["optix_launch_count"])
            auxiliary_launches += int(
                operation["total_auxiliary_cuda_kernel_launch_count"])
    hostile = _validate_k_plus_one_independently(
        value.get("relation_k_plus_one_hostile"), arm=RTDL,
        extra_fields={
            "product_compact_control", "failure_code",
            "native_operation_receipt", "deployment_identity"})
    if hostile.get("product_compact_control") != {
            "schema": "rtdl.v4.rtdlexe.relation_compact_control.v1",
            "raw_event_count": 4097, "unique_event_count": 4097,
            "overflowed": 1, "status": 0xffff5102,
            "semantic_capacity": 4096, "control_d2h_bytes": 16,
            } \
            or hostile.get("failure_code") != "RX035_DEVICE_STATUS_INVALID" \
            or hostile.get("native_operation_receipt") \
            != _independent_rtdl_k_plus_one_operation() \
            or hostile.get("deployment_identity") \
            != rows[0]["deployment_identity"]:
        raise RuntimeError("independent RTDL K+1 operation differs")
    optix_launches += 2
    auxiliary_launches += 7
    if optix_launches != value["untimed_optix_launch_count"] \
            or auxiliary_launches \
            != value["untimed_auxiliary_cuda_kernel_launch_count"] \
            or optix_launches + auxiliary_launches \
            != value["untimed_gpu_launch_count"]:
        raise RuntimeError("independent RTDL KAT launch recount differs")


def _independent_direct_command(
        recipe: Mapping[str, Any], runtime: Mapping[str, Any]) -> list[str]:
    if set(recipe) != {"schema", "argv_template", "recipe_sha256"} \
            or recipe.get("schema") != "rtdl.goal5802.direct_build_recipe.v2":
        raise RuntimeError("independent Direct recipe schema differs")
    unsigned = dict(recipe)
    observed = unsigned.pop("recipe_sha256")
    if observed != _digest(unsigned):
        raise RuntimeError("independent Direct recipe seal differs")
    template = recipe.get("argv_template")
    if not isinstance(template, list) or not template \
            or not all(isinstance(item, str) and item for item in template):
        raise RuntimeError("independent Direct recipe argv differs")
    fixed_prefix = [
        "{CXX}", "-std=c++17", "-O3", "-DNDEBUG",
        "-Wall", "-Wextra", "-Werror",
        "-I{OPTIX_INCLUDE}", "-I{CUDA_INCLUDE}",
        "-I{CUDA_INCLUDE}/nv", "{DIRECT_SOURCE}",
    ]
    fixed_suffix = ["-lcuda", "-lnvrtc", "-ldl", "-o", "{OUTPUT}"]
    library_tokens = template[len(fixed_prefix):-len(fixed_suffix)]
    if template[:len(fixed_prefix)] != fixed_prefix \
            or template[-len(fixed_suffix):] != fixed_suffix \
            or len(library_tokens) != len(set(library_tokens)) \
            or any(not token.startswith("-L")
                   or not Path(token[2:]).is_absolute()
                   or "{" in token or "}" in token
                   for token in library_tokens):
        raise RuntimeError("independent Direct compile-option grammar differs")
    files = runtime["files"]
    directories = runtime["directories"]
    replacements = {
        "{CXX}": str(files["cxx_compiler"]["path"]),
        "{DIRECT_SOURCE}": str(files["direct_scalar_source"]["path"]),
        "{OPTIX_INCLUDE}": str(directories["optix_include"]["path"]),
        "{CUDA_INCLUDE}": str(directories["cuda_include"]["path"]),
        "{OUTPUT}": str(files["direct_scalar_worker"]["path"]),
    }
    seen: set[str] = set()
    result: list[str] = []
    for token in template:
        expanded = token
        for marker, replacement in replacements.items():
            if marker in expanded:
                seen.add(marker)
                expanded = expanded.replace(marker, replacement)
        if "{" in expanded or "}" in expanded:
            raise RuntimeError("independent Direct recipe unknown marker")
        result.append(expanded)
    if seen != set(replacements) or result[0] != replacements["{CXX}"] \
            or result.count(replacements["{OUTPUT}"]) != 1:
        raise RuntimeError("independent Direct recipe binding differs")
    return result


def _validate_fresh_process_replay_independently(
        value: Mapping[str, Any], *, runtime: Mapping[str, Any],
        header_projection: Mapping[str, Any], projection_root: Path,
        direct_nvrtc: Mapping[str, Any],
        frozen_sources: Mapping[str, Mapping[str, object]] | None = None) -> None:
    """Reconstruct the v2 fresh-process PTX result from preserved raw bytes.

    This deliberately does not import the preparation script, its parser, or
    its receipt validator.  It treats each child JSON, product, and per-PID
    strace file as untrusted input and independently rebuilds all equalities.
    """

    files = runtime["files"]
    directories = runtime["directories"]
    expected_tree_fields = ("file_count", "payload_bytes", "tree_sha256")
    required_top = {
        "schema", "status", "projection_claim", "device_source_sha256",
        "compaction_source_sha256", "optix_include_tree",
        "cuda_include_tree", "header_projection_receipt_sha256",
        "header_projection_tree_sha256", "original_optix_include_path",
        "original_cuda_include_path", "original_ptx_compile_options",
        "original_ptx_sha256", "projected_ptx_byte_identical_to_original",
        "nvcc_only_ptx_byte_identical_to_original",
        "union_ptx_byte_identical_to_original", "nvrtc_library",
        "nvrtc_builtins", "fresh_process_replay", "compute_capability",
        "ptx_compile_options", "ptx_target", "ptx_bytes", "ptx_sha256",
        "compaction_cubin_architecture", "compaction_compile_options",
        "compaction_cubin_bytes", "compaction_cubin_sha256",
        "registered_performance_timing_count", "clock_read_count",
        "gpu_kernel_launch_count", "formal_worker_count", "receipt_sha256",
    }
    if set(value) != required_top \
            or value.get("schema") \
            != "rtdl.goal5802.matched_ptx_untimed_prepare.v3" \
            or value.get("status") \
            != "PASS__FRESH_PROCESS_TRACED_UNTIMED_PREPARE" \
            or value.get("projection_claim") != FINAL_PROJECTION_CLAIM \
            or any(not _plain_int(value.get(key)) or value[key] != 0 for key in (
                "registered_performance_timing_count", "clock_read_count",
                "gpu_kernel_launch_count", "formal_worker_count")):
        raise RuntimeError("independent fresh PTX envelope differs")

    cc = value.get("compute_capability")
    match = re.fullmatch(r"([0-9]+)\.([0-9]+)", str(cc))
    if match is None:
        raise RuntimeError("independent fresh PTX architecture malformed")
    major, minor = map(int, match.groups())
    if major <= 0 or minor < 0 or minor > 9 \
            or cc != f"{major}.{minor}" \
            or cc != runtime["target_observation"]["compute_capability"]:
        raise RuntimeError("independent fresh PTX architecture differs")
    compute_target = f"compute_{major}{minor}"
    sm_target = f"sm_{major}{minor}"

    # Bind the dependency authority's sources, tools, roots, and architecture
    # to the runtime-manifest identities rather than trusting repeated strings.
    authority = header_projection.get("command_authority")
    mappings = header_projection.get("root_mappings")
    if not isinstance(authority, Mapping) or not isinstance(mappings, list):
        raise RuntimeError("independent projection authority absent")
    source_roles = {
        "matched_device_source": "device_source",
        "relation_compaction_source": "compaction_source",
        "direct_source": "direct_scalar_source",
    }
    for authority_role, manifest_role in source_roles.items():
        record = authority["sources"][authority_role]
        manifest = files[manifest_role]
        if record.get("bytes") != manifest["bytes"] \
                or record.get("sha256") != manifest["sha256"] \
                or Path(str(record.get("resolved_path"))) \
                != Path(str(manifest["path"])).resolve(strict=True):
            raise RuntimeError(
                f"independent projection source crossbind differs: {authority_role}")
    frozen_source_roles = {
        "matched_device_source": (
            "experiments/goal5802_premeasurement/"
            "matched_device_semantic_capacity.cu"),
        "relation_compaction_source": (
            "experiments/goal5802_premeasurement/"
            "relation_semantic_compaction.cu"),
        "direct_source": (
            "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"),
    }
    if frozen_sources is not None:
        for authority_role, frozen_role in frozen_source_roles.items():
            authority_record = authority["sources"][authority_role]
            frozen_record = frozen_sources.get(frozen_role)
            if not isinstance(frozen_record, Mapping) \
                    or authority_record.get("bytes") \
                    != frozen_record.get("bytes") \
                    or authority_record.get("sha256") \
                    != frozen_record.get("sha256"):
                raise RuntimeError(
                    "independent projection/freeze source crossbind differs: "
                    + authority_role)
    for authority_role, manifest_role in {
            "nvcc": "nvcc", "cxx": "cxx_compiler"}.items():
        record = authority["tools"][authority_role]
        manifest = files[manifest_role]
        manifest_path = Path(str(
            manifest.get("resolved_path", manifest.get("path"))))
        if record.get("bytes") != manifest["bytes"] \
                or record.get("sha256") != manifest["sha256"] \
                or Path(str(record.get("resolved_path"))) != manifest_path:
            raise RuntimeError(
                f"independent projection tool crossbind differs: {authority_role}")
    if authority.get("compute_capability") != sm_target:
        raise RuntimeError("independent projection architecture crossbind differs")
    mapping_by_role = {
        str(row.get("role")): row for row in mappings
        if isinstance(row, Mapping)}
    if set(mapping_by_role) != {"optix_include", "cuda_include"}:
        raise RuntimeError("independent projection root mappings differ")
    original_roots = [
        Path(str(authority["original_sdk_roots"][role]["resolved_path"]))
        for role in ("optix_include", "cuda_include")]
    canonical_projected = [
        Path(str(mapping_by_role[role]["projected_root"]))
        for role in ("optix_include", "cuda_include")]
    root = projection_root.resolve(strict=True)
    if str(root) != header_projection.get("projection_root") \
            or original_roots != [
                Path(str(value.get("original_optix_include_path"))),
                Path(str(value.get("original_cuda_include_path")))] \
            or canonical_projected != [
                Path(str(directories["optix_include"]["path"])),
                Path(str(directories["cuda_include"]["path"]))]:
        raise RuntimeError("independent projection root crossbind differs")
    relative_roots = [path.relative_to(root) for path in canonical_projected]
    for role in (
            "matched_ptx", "compaction_cubin", "matched_ptx_prepare_receipt",
            "header_projection_receipt"):
        candidate = Path(str(files[role]["path"])).resolve(strict=True)
        if candidate == root or candidate.is_relative_to(root):
            raise RuntimeError(
                f"independent replay/provenance output enters projection: {role}")

    replay = value.get("fresh_process_replay")
    replay_keys = {
        "python", "strace", "child", "canonical_projection_root",
        "nvcc_only_projection_root", "negative_projection_root",
        "nvcc_only_sdk_paths", "direct_sdk_paths", "union_sdk_paths",
        "nvcc_only_tree", "negative_tree_rows", "negative_removed_path",
        "runs", "successful_child_pids", "all_successful_pids_distinct",
        "negative_pid_disjoint", "original_sdk_attempts_in_projected_runs",
        "negative_compile_failed_without_product",
    }
    if not isinstance(replay, Mapping) or set(replay) != replay_keys:
        raise RuntimeError("independent fresh replay schema differs")
    tool_records: dict[str, dict[str, object]] = {}
    python_record = replay.get("python")
    if not isinstance(python_record, Mapping) or set(python_record) != {
            "invocation_path", "path", "bytes", "sha256"}:
        raise RuntimeError("independent fresh replay Python row differs")
    python_invocation = Path(str(python_record.get("invocation_path")))
    if not python_invocation.is_absolute() or not python_invocation.is_file():
        raise RuntimeError(
            "independent fresh replay Python invocation differs")
    python_binary = _independent_regular_file_identity(
        python_invocation.resolve(strict=True))
    if dict(python_record) != {
            "invocation_path": str(python_invocation), **python_binary}:
        raise RuntimeError(
            "independent fresh replay Python invocation/binary differs")
    tool_records["python"] = dict(python_record)
    for role in ("strace", "child"):
        record = replay.get(role)
        if not isinstance(record, Mapping) or set(record) != {
                "path", "bytes", "sha256"}:
            raise RuntimeError("independent fresh replay tool row differs")
        observed = _independent_regular_file_identity(
            Path(str(record.get("path"))))
        if dict(record) != observed:
            raise RuntimeError("independent fresh replay tool bytes differ")
        tool_records[role] = observed
    clean_python = files["clean_python"]
    if tool_records["python"] != {
            "invocation_path": clean_python["path"],
            "path": clean_python.get("resolved_path", clean_python["path"]),
            "bytes": clean_python["bytes"], "sha256": clean_python["sha256"]}:
        raise RuntimeError("independent fresh replay Python crossbind differs")
    if replay.get("canonical_projection_root") != str(root):
        raise RuntimeError("independent canonical projection root differs")

    dependency_runs = header_projection.get("runs")
    if not isinstance(dependency_runs, list) or len(dependency_runs) != 3:
        raise RuntimeError("independent projection dependency runs differ")
    nvcc_paths = sorted({
        str(row["projection_path"])
        for run in dependency_runs[:2]
        for row in run["load_bearing_sdk_dependencies"]})
    direct_paths = sorted({
        str(row["projection_path"])
        for row in dependency_runs[2]["load_bearing_sdk_dependencies"]})
    union_paths = sorted(set(nvcc_paths) | set(direct_paths))
    if any(Path(path).is_absolute() or ".." in Path(path).parts
           for path in union_paths) \
            or replay.get("nvcc_only_sdk_paths") != nvcc_paths \
            or replay.get("direct_sdk_paths") != direct_paths \
            or replay.get("union_sdk_paths") != union_paths:
        raise RuntimeError("independent fresh replay SDK partitions differ")
    canonical_rows = _independent_tree_rows(root)
    if [str(row["path"]) for row in canonical_rows] != union_paths:
        raise RuntimeError("independent canonical projection is not exact union")

    nvcc_root = Path(str(replay.get("nvcc_only_projection_root")))
    negative_root = Path(str(replay.get("negative_projection_root")))
    if not nvcc_root.is_absolute() or not negative_root.is_absolute() \
            or nvcc_root.resolve(strict=True) != nvcc_root \
            or negative_root.resolve(strict=True) != negative_root:
        raise RuntimeError("independent fresh replay roots are not canonical")
    replay_root = nvcc_root.parent
    if negative_root.parent != replay_root \
            or nvcc_root.name != "nvcc_only_projection" \
            or negative_root.name != "negative_projection" \
            or replay_root == root or replay_root.is_relative_to(root) \
            or root.is_relative_to(replay_root):
        raise RuntimeError("independent fresh replay root layout differs")
    observed_nvcc_rows = _independent_tree_rows(nvcc_root)
    nvcc_tree = replay.get("nvcc_only_tree")
    expected_nvcc_tree = {
        "file_count": len(observed_nvcc_rows),
        "payload_bytes": sum(int(row["bytes"]) for row in observed_nvcc_rows),
        "tree_sha256": _digest(observed_nvcc_rows),
        "rows": observed_nvcc_rows,
    }
    if nvcc_tree != expected_nvcc_tree \
            or [str(row["path"]) for row in observed_nvcc_rows] != nvcc_paths:
        raise RuntimeError("independent NVCC-only projection tree differs")
    for row in observed_nvcc_rows:
        relative = Path(str(row["path"]))
        canonical = root / relative
        if canonical.read_bytes() != (nvcc_root / relative).read_bytes():
            raise RuntimeError("independent NVCC-only projection bytes differ")

    expected_removed = (relative_roots[0] / "optix.h").as_posix()
    removed = replay.get("negative_removed_path")
    negative_rows = _independent_tree_rows(negative_root)
    expected_negative_rows = [
        row for row in observed_nvcc_rows if row["path"] != expected_removed]
    if removed != expected_removed \
            or replay.get("negative_tree_rows") != negative_rows \
            or negative_rows != expected_negative_rows:
        raise RuntimeError("independent exact-one-file negative tree differs")
    if (negative_root / Path(expected_removed)).exists() \
            or (negative_root / Path(expected_removed)).is_symlink():
        raise RuntimeError("independent negative optix.h still exists")
    for row in negative_rows:
        relative = Path(str(row["path"]))
        if (negative_root / relative).read_bytes() \
                != (nvcc_root / relative).read_bytes():
            raise RuntimeError("independent negative tree changed extra bytes")

    nvcc_projected = [nvcc_root / relative for relative in relative_roots]
    negative_projected = [
        negative_root / relative for relative in relative_roots]
    required_nvcc = [
        nvcc_projected[0] / name for name in ("optix.h", "optix_device.h")]
    required_union = [
        canonical_projected[0] / name
        for name in ("optix.h", "optix_device.h")]
    for nvcc_header, union_header in zip(required_nvcc, required_union):
        if nvcc_header.read_bytes() != union_header.read_bytes():
            raise RuntimeError("independent required projected header differs")

    runs = replay.get("runs")
    if not isinstance(runs, Mapping) or set(runs) != {
            "original", "nvcc_only", "union", "compaction",
            "negative_missing_optix_h"}:
        raise RuntimeError("independent fresh replay run roles differ")
    device_source = _independent_regular_file_identity(
        Path(str(files["device_source"]["path"])))
    compaction_source = _independent_regular_file_identity(
        Path(str(files["compaction_source"]["path"])))
    ptx_options = lambda optix, cuda: [
        "--std=c++17", "--device-as-default-execution-space",
        "--relocatable-device-code=true",
        f"--gpu-architecture={compute_target}", f"-I{optix}", f"-I{cuda}",
        f"-I{cuda / 'nv'}",
    ]
    success_specs = {
        "original": {
            "mode": "ptx", "source": device_source,
            "includes": original_roots, "projected": [], "required": [],
            "options": ptx_options(*original_roots), "extension": "ptx"},
        "nvcc_only": {
            "mode": "ptx", "source": device_source,
            "includes": nvcc_projected, "projected": nvcc_projected,
            "required": required_nvcc,
            "options": ptx_options(*nvcc_projected), "extension": "ptx"},
        "union": {
            "mode": "ptx", "source": device_source,
            "includes": canonical_projected, "projected": canonical_projected,
            "required": required_union,
            "options": ptx_options(*canonical_projected), "extension": "ptx"},
        "compaction": {
            "mode": "cubin", "source": compaction_source,
            "includes": [None, None], "projected": [], "required": [],
            "options": [
                "--std=c++17", "--device-as-default-execution-space",
                f"--gpu-architecture={sm_target}"], "extension": "cubin"},
    }
    success_pids: list[int] = []
    success_trace_pids: set[int] = set()
    loaded_identities: list[dict[str, object]] = []
    ptx_payloads: list[bytes] = []
    trace_documents: dict[str, dict[str, object]] = {}
    common_cwd: str | None = None
    for label, spec in success_specs.items():
        row = runs[label]
        if not isinstance(row, Mapping) or set(row) != {
                "process", "trace", "receipt", "child", "product"}:
            raise RuntimeError(f"independent fresh replay row differs: {label}")
        process = row.get("process")
        child = row.get("child")
        receipt_record = row.get("receipt")
        product_record = row.get("product")
        if not isinstance(process, Mapping) or set(process) != {
                "label", "cwd", "command", "child_argv", "exit_code",
                "stdout_utf8", "stdout_sha256", "stderr_utf8",
                "stderr_sha256"} \
                or process.get("label") != label \
                or process.get("exit_code") != 0 \
                or not isinstance(process.get("stdout_utf8"), str) \
                or not isinstance(process.get("stderr_utf8"), str) \
                or process.get("stdout_sha256") != hashlib.sha256(
                    process["stdout_utf8"].encode()).hexdigest() \
                or process.get("stderr_sha256") != hashlib.sha256(
                    process["stderr_utf8"].encode()).hexdigest() \
                or not isinstance(child, Mapping):
            raise RuntimeError(
                f"independent fresh replay process differs: {label}")
        child_required = {
            "schema", "status", "pid", "parent_pid", "argv", "cwd",
            "mode", "source", "include_roots", "compute_capability",
            "compile_options", "target", "product", "loaded_nvrtc",
            "clock_read_count", "gpu_kernel_launch_count",
            "formal_worker_count", "registered_performance_timing_count",
            "receipt_sha256",
        }
        child_unsigned = dict(child)
        child_seal = child_unsigned.pop("receipt_sha256", None)
        if set(child) != child_required \
                or child.get("schema") \
                != "rtdl.goal5802.fresh_nvrtc_compile_child.v2" \
                or child.get("status") \
                != "PASS__FRESH_PROCESS_UNTIMED_NVRTC_COMPILE" \
                or not _plain_int(child.get("pid")) or int(child["pid"]) <= 0 \
                or not _plain_int(child.get("parent_pid")) \
                or int(child["parent_pid"]) <= 0 \
                or child["pid"] == child["parent_pid"] \
                or child_seal != _digest(child_unsigned) \
                or any(not _plain_int(child.get(key)) or child[key] != 0
                       for key in (
                    "clock_read_count", "gpu_kernel_launch_count",
                    "formal_worker_count", "registered_performance_timing_count")):
            raise RuntimeError(
                f"independent fresh replay child envelope differs: {label}")
        cwd_text = child.get("cwd")
        cwd_path = Path(str(cwd_text))
        if not cwd_path.is_absolute() or not cwd_path.is_dir() \
                or cwd_path.resolve(strict=True) != cwd_path \
                or process.get("cwd") != cwd_text:
            raise RuntimeError(f"independent fresh replay cwd differs: {label}")
        if common_cwd is None:
            common_cwd = str(cwd_path)
        elif common_cwd != str(cwd_path):
            raise RuntimeError("independent fresh replay process cwds differ")
        output_path = replay_root / "products" / (
            f"{label}.{spec['extension']}")
        receipt_path = replay_root / "child_receipts" / f"{label}.json"
        trace_prefix = replay_root / "traces" / label
        includes = spec["includes"]
        expected_argv = [
            tool_records["python"]["invocation_path"],
            tool_records["child"]["path"],
            "--mode", spec["mode"], "--source", spec["source"]["path"],
            "--compute-capability", cc, "--output", str(output_path),
            "--receipt", str(receipt_path),
        ]
        if includes[0] is not None:
            expected_argv.extend(["--optix-include", str(includes[0])])
        if includes[1] is not None:
            expected_argv.extend(["--cuda-include", str(includes[1])])
        expected_command = [
            tool_records["strace"]["path"], "-ff", "-y", "-qq", "-s", "65535",
            "-e", f"trace={FRESH_TRACE_SELECTOR}", "-o", str(trace_prefix),
            "--", *expected_argv,
        ]
        if process.get("child_argv") != expected_argv \
                or process.get("command") != expected_command \
                or child.get("argv") != expected_argv[1:] \
                or child.get("mode") != spec["mode"] \
                or child.get("source") != spec["source"] \
                or child.get("include_roots") != {
                    "optix": str(includes[0]) if includes[0] is not None else None,
                    "cuda": str(includes[1]) if includes[1] is not None else None} \
                or child.get("compute_capability") != cc \
                or child.get("compile_options") != spec["options"] \
                or child.get("target") != sm_target:
            raise RuntimeError(
                f"independent fresh replay argv/input differs: {label}")
        if not isinstance(receipt_record, Mapping) \
                or dict(receipt_record) != _independent_regular_file_identity(
                    receipt_path) \
                or _load(receipt_path) != child \
                or not isinstance(product_record, Mapping) \
                or dict(product_record) != _independent_regular_file_identity(
                    output_path) \
                or child.get("product") != product_record:
            raise RuntimeError(
                f"independent fresh replay receipt/product differs: {label}")
        expected_stdout = json.dumps({
            "status": child["status"], "pid": child["pid"],
            "product_sha256": product_record["sha256"],
            "receipt_sha256": child["receipt_sha256"],
        }, sort_keys=True) + "\n"
        if process.get("stdout_utf8") != expected_stdout \
                or process.get("stderr_utf8") != "":
            raise RuntimeError(
                f"independent fresh replay child stdio differs: {label}")
        trace = _recount_independent_trace_document(
            row.get("trace"), cwd=cwd_path, trace_prefix=trace_prefix,
            original_roots=original_roots,
            projected_roots=spec["projected"],
            required_projected=spec["required"],
            authority_pid=int(child["pid"]),
            require_no_original_attempt=bool(spec["projected"]))
        trace_documents[label] = trace
        success_pids.append(int(child["pid"]))
        success_trace_pids.update(int(pid) for pid in trace["traced_pids"])
        loaded_identities.append(
            _validate_independent_loaded_nvrtc(child.get("loaded_nvrtc")))
        payload = output_path.read_bytes()
        if spec["mode"] == "ptx":
            if _single_ptx_target_from_bytes(payload) != sm_target:
                raise RuntimeError(
                    f"independent fresh replay PTX target differs: {label}")
            ptx_payloads.append(payload)
        elif not payload.startswith(b"\x7fELF"):
            raise RuntimeError("independent fresh replay cubin is not ELF")

    if len(set(success_pids)) != len(success_pids) \
            or replay.get("successful_child_pids") != success_pids \
            or replay.get("all_successful_pids_distinct") is not True \
            or any(item != loaded_identities[0]
                   for item in loaded_identities[1:]) \
            or any(payload != ptx_payloads[0] for payload in ptx_payloads[1:]):
        raise RuntimeError("independent fresh replay cross-process result differs")

    negative = runs["negative_missing_optix_h"]
    if not isinstance(negative, Mapping) or set(negative) != {
            "process", "trace", "receipt", "failure", "receipt_created",
            "product_created", "missing_header_unsuccessful_open_count"}:
        raise RuntimeError("independent fresh replay negative row differs")
    negative_process = negative.get("process")
    failure = negative.get("failure")
    failure_receipt = negative.get("receipt")
    if not isinstance(negative_process, Mapping) or set(negative_process) != {
            "label", "cwd", "command", "child_argv", "exit_code",
            "stdout_utf8", "stdout_sha256", "stderr_utf8", "stderr_sha256"} \
            or negative_process.get("label") != "negative_missing_optix_h" \
            or negative_process.get("exit_code") != 17 \
            or not isinstance(negative_process.get("stdout_utf8"), str) \
            or not isinstance(negative_process.get("stderr_utf8"), str) \
            or negative_process.get("stdout_sha256") != hashlib.sha256(
                negative_process["stdout_utf8"].encode()).hexdigest() \
            or negative_process.get("stderr_sha256") != hashlib.sha256(
                negative_process["stderr_utf8"].encode()).hexdigest() \
            or not isinstance(failure, Mapping):
        raise RuntimeError("independent fresh replay negative process differs")
    failure_required = {
        "schema", "status", "pid", "parent_pid", "argv", "cwd", "mode",
        "source", "include_roots", "compute_capability", "error_type",
        "error_message", "loaded_nvrtc", "product_created",
        "clock_read_count", "gpu_kernel_launch_count", "formal_worker_count",
        "registered_performance_timing_count", "receipt_sha256",
    }
    failure_unsigned = dict(failure)
    failure_seal = failure_unsigned.pop("receipt_sha256", None)
    if set(failure) != failure_required \
            or failure.get("schema") \
            != "rtdl.goal5802.fresh_nvrtc_compile_failure.v2" \
            or failure.get("status") \
            != "FAIL__FRESH_PROCESS_NVRTC_COMPILE__NO_PRODUCT" \
            or not _plain_int(failure.get("pid")) or int(failure["pid"]) <= 0 \
            or not _plain_int(failure.get("parent_pid")) \
            or int(failure["parent_pid"]) <= 0 \
            or failure["pid"] == failure["parent_pid"] \
            or failure.get("product_created") is not False \
            or failure_seal != _digest(failure_unsigned) \
            or any(not _plain_int(failure.get(key)) or failure[key] != 0
                   for key in (
                "clock_read_count", "gpu_kernel_launch_count",
                "formal_worker_count", "registered_performance_timing_count")):
        raise RuntimeError("independent fresh replay negative receipt differs")
    negative_output = (
        replay_root / "products" / "negative_missing_optix_h.ptx")
    negative_receipt_path = (
        replay_root / "child_receipts" / "negative_missing_optix_h.json")
    negative_trace_prefix = replay_root / "traces" / "negative_missing_optix_h"
    negative_argv = [
        tool_records["python"]["invocation_path"],
        tool_records["child"]["path"],
        "--mode", "ptx", "--source", device_source["path"],
        "--compute-capability", cc, "--output", str(negative_output),
        "--receipt", str(negative_receipt_path), "--optix-include",
        str(negative_projected[0]), "--cuda-include",
        str(negative_projected[1]),
    ]
    negative_command = [
        tool_records["strace"]["path"], "-ff", "-y", "-qq", "-s", "65535",
        "-e", f"trace={FRESH_TRACE_SELECTOR}", "-o",
        str(negative_trace_prefix), "--", *negative_argv,
    ]
    if failure.get("argv") != negative_argv[1:] \
            or failure.get("cwd") != common_cwd \
            or negative_process.get("cwd") != common_cwd \
            or negative_process.get("child_argv") != negative_argv \
            or negative_process.get("command") != negative_command \
            or failure.get("mode") != "ptx" \
            or failure.get("source") != device_source \
            or failure.get("include_roots") != {
                "optix": str(negative_projected[0]),
                "cuda": str(negative_projected[1])} \
            or failure.get("compute_capability") != cc \
            or not isinstance(failure.get("error_type"), str) \
            or not failure.get("error_type") \
            or not isinstance(failure.get("error_message"), str) \
            or not failure.get("error_message"):
        raise RuntimeError("independent fresh replay negative input differs")
    if not isinstance(failure_receipt, Mapping) \
            or dict(failure_receipt) != _independent_regular_file_identity(
                negative_receipt_path) \
            or _load(negative_receipt_path) != failure \
            or negative.get("receipt_created") is not True \
            or negative.get("product_created") is not False \
            or negative_output.exists() or negative_output.is_symlink():
        raise RuntimeError("independent fresh replay negative product differs")
    expected_negative_stderr = json.dumps({
        "status": failure["status"], "pid": failure["pid"],
        "error_type": failure["error_type"],
        "error_message": failure["error_message"],
        "receipt_sha256": failure["receipt_sha256"],
    }, sort_keys=True) + "\n"
    if negative_process.get("stdout_utf8") != "" \
            or negative_process.get("stderr_utf8") \
            != expected_negative_stderr:
        raise RuntimeError("independent fresh replay negative stdio differs")
    negative_loaded = _validate_independent_loaded_nvrtc(
        failure.get("loaded_nvrtc"))
    if negative_loaded != loaded_identities[0]:
        raise RuntimeError("independent negative child loaded different NVRTC")
    negative_trace = _recount_independent_trace_document(
        negative.get("trace"), cwd=Path(str(common_cwd)),
        trace_prefix=negative_trace_prefix, original_roots=original_roots,
        projected_roots=negative_projected, required_projected=[],
        authority_pid=int(failure["pid"]), require_no_original_attempt=True)
    negative_accesses = _parse_independent_strace_accesses(
        [Path(str(row["path"])).read_bytes()
         for row in negative_trace["trace_files"]],
        cwd=Path(str(common_cwd)), trace_pids=negative_trace["traced_pids"])
    missing_path = str(
        (negative_root / Path(expected_removed)).resolve(strict=False))
    missing_count = sum(
        row["trace_pid"] == failure["pid"]
        and row["normalized_path"] == missing_path
        and row["success"] is False
        for row in negative_accesses)
    projected_original_attempts = sum(
        int(trace_documents[label]["original_sdk_attempt_count"])
        for label in ("nvcc_only", "union")) \
        + int(negative_trace["original_sdk_attempt_count"])
    if missing_count <= 0 \
            or negative.get("missing_header_unsuccessful_open_count") \
            != missing_count \
            or "optix.h" not in str(failure["error_message"]) \
            or "optix.h" not in negative_process["stderr_utf8"] \
            or success_trace_pids & set(negative_trace["traced_pids"]) \
            or int(failure["pid"]) in set(success_pids) \
            or replay.get("negative_pid_disjoint") is not True \
            or projected_original_attempts != 0 \
            or replay.get("original_sdk_attempts_in_projected_runs") != 0 \
            or replay.get("negative_compile_failed_without_product") is not True:
        raise RuntimeError("independent missing-optix.h causal KAT differs")

    # Reconstruct final products and loaded-tool equality from bytes, not flags.
    matched_ptx = Path(str(files["matched_ptx"]["path"])).read_bytes()
    compaction_cubin = Path(str(files["compaction_cubin"]["path"])).read_bytes()
    compaction_product = Path(str(
        runs["compaction"]["product"]["path"])).read_bytes()
    loaded = loaded_identities[0]
    expected_library = {
        **loaded["library"], "version": loaded["version"]}
    if not matched_ptx or matched_ptx != ptx_payloads[0] \
            or value.get("original_ptx_sha256") \
            != hashlib.sha256(ptx_payloads[0]).hexdigest() \
            or value.get("projected_ptx_byte_identical_to_original") is not True \
            or value.get("nvcc_only_ptx_byte_identical_to_original") is not True \
            or value.get("union_ptx_byte_identical_to_original") is not True \
            or value.get("ptx_bytes") != len(matched_ptx) \
            or value.get("ptx_sha256") != hashlib.sha256(matched_ptx).hexdigest() \
            or value.get("ptx_target") != sm_target \
            or value.get("ptx_compile_options") \
            != success_specs["union"]["options"] \
            or value.get("original_ptx_compile_options") \
            != success_specs["original"]["options"] \
            or compaction_cubin != compaction_product \
            or not compaction_cubin.startswith(b"\x7fELF") \
            or value.get("compaction_cubin_bytes") != len(compaction_cubin) \
            or value.get("compaction_cubin_sha256") \
            != hashlib.sha256(compaction_cubin).hexdigest() \
            or value.get("compaction_cubin_architecture") != sm_target \
            or value.get("compaction_compile_options") \
            != success_specs["compaction"]["options"] \
            or value.get("nvrtc_library") != expected_library \
            or value.get("nvrtc_builtins") != loaded["builtins"]:
        raise RuntimeError("independent fresh replay final product differs")
    if value.get("device_source_sha256") != files["device_source"]["sha256"] \
            or value.get("compaction_source_sha256") \
            != files["compaction_source"]["sha256"] \
            or value.get("optix_include_tree") != {
                key: directories["optix_include"][key]
                for key in expected_tree_fields} \
            or value.get("cuda_include_tree") != {
                key: directories["cuda_include"][key]
                for key in expected_tree_fields} \
            or value.get("header_projection_receipt_sha256") \
            != files["header_projection_receipt"]["sha256"] \
            or value.get("header_projection_tree_sha256") \
            != directories["header_projection"]["tree_sha256"] \
            or expected_library != {
                "path": files["nvrtc_library"]["path"],
                "bytes": files["nvrtc_library"]["bytes"],
                "sha256": files["nvrtc_library"]["sha256"],
                "canonical_regular_file": True, "symlink": False,
                "version": loaded["version"]} \
            or loaded["builtins"] != {
                "path": files["nvrtc_builtins"]["path"],
                "bytes": files["nvrtc_builtins"]["bytes"],
                "sha256": files["nvrtc_builtins"]["sha256"],
                "canonical_regular_file": True, "symlink": False}:
        raise RuntimeError("independent fresh replay manifest crossbind differs")
    if direct_nvrtc.get("loaded_library_path") != loaded["library"]["path"] \
            or direct_nvrtc.get("loaded_library_bytes") \
            != loaded["library"]["bytes"] \
            or direct_nvrtc.get("loaded_library_sha256") \
            != loaded["library"]["sha256"] \
            or direct_nvrtc.get("loaded_builtins_path") \
            != loaded["builtins"]["path"] \
            or direct_nvrtc.get("loaded_builtins_bytes") \
            != loaded["builtins"]["bytes"] \
            or direct_nvrtc.get("loaded_builtins_sha256") \
            != loaded["builtins"]["sha256"] \
            or direct_nvrtc.get("nvrtc_version") != {
                "major": loaded["version"][0], "minor": loaded["version"][1]}:
        raise RuntimeError(
            "independent Direct/Python loaded NVRTC identities differ")


def _median(values: Sequence[float | int]) -> float:
    ordered = sorted(float(item) for item in values)
    if not ordered:
        raise RuntimeError("empty median")
    middle = len(ordered) // 2
    return ordered[middle] if len(ordered) % 2 else (
        ordered[middle - 1] + ordered[middle]) / 2.0


def _phase_projection(receipt: Mapping[str, Any], row: Mapping[str, Any]) \
        -> dict[str, Any]:
    worker = receipt["worker_result"]
    phases = worker["phase_durations_ns"]
    envelope = receipt["controller_process_envelope_ns"]
    exclusive = sum(int(value) for value in phases.values())
    load = int(phases["load_or_deploy"])
    return {
        "worker_id": row["worker_id"],
        "process_startup_and_admission_ns": phases[
            "process_startup_and_admission"],
        "common_cache_conditioning_ns": receipt[
            "preworker_common_cache_conditioning"]["duration_ns"],
        "input_materialization_ns": phases["input_materialization"],
        "protocol_validation_and_code_generation_ns": (
            load if row["arm"] == RTDL else 0),
        "protocol_codegen_disposition": (
            "RTDL_COMBINED_WITH_DEPLOYMENT_LOAD__CODEGEN_NOT_EXECUTED"
            if row["arm"] == RTDL else "NOT_EXECUTED"),
        "deployment_load_ns": 0 if row["arm"] == RTDL else load,
        "device_compilation_ns": 0,
        "gas_static_preparation_ns": None,
        "module_program_pipeline_sbt_preparation_ns": None,
        "prepare_subphase_disposition": "COMBINED_NOT_SEPARATELY_OBSERVABLE",
        "combined_prepare_ns": phases["prepare"],
        "steady_warmups_ns": phases["steady_warmups"],
        "complete_execute_ns": phases["complete_execute"],
        "measurement_evidence_materialization_ns": phases[
            "measurement_evidence_materialization"],
        "close_ns": phases["close"],
        "post_execution_identity_validation_ns": phases[
            "post_execution_identity_validation"],
        "controller_process_envelope_ns": envelope,
        "postclose_serialization_and_unaccounted_residual_ns": (
            envelope - exclusive),
        "directly_metered_worker_fraction": exclusive / envelope,
    }


def _require_int(value: Any, expected: int, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value != expected:
        raise RuntimeError(f"{label} differs")


_OPERATION_COUNT_KEYS = (
    "prepare_device_allocation_call_count", "prepare_h2d_call_count",
    "prepare_pinned_host_allocation_call_count", "prepare_stream_creation_count",
    "execute_device_allocation_call_count",
    "execute_pinned_host_allocation_call_count",
    "execute_async_h2d_call_count", "execute_async_d2h_call_count",
    "execute_blocking_d2h_call_count", "execute_device_zero_fill_call_count",
    "execute_explicit_stream_sync_call_count", "execute_launch_call_count",
    "execute_stream_creation_call_count", "execute_stream_destroy_call_count",
)
_PYOPTIX_GUARD = {
    "scope": "PYTHON_VISIBLE_TASK_OWNER_EXECUTE__NOT_CUPTI_OR_DRIVER_WIDE",
    "unapproved_device_allocation_call_count": 0,
    "unapproved_pinned_host_allocation_call_count": 0,
    "unapproved_blocking_asnumpy_call_count": 0,
    "unauthorized_direct_stream_sync_count": 0,
    "complete_driver_operation_observation_claimed": False,
}


def _independent_exact_counts(**nonzero: int) -> dict[str, int]:
    result = {key: 0 for key in _OPERATION_COUNT_KEYS}
    if set(nonzero).difference(result):
        raise RuntimeError("independent operation-count vocabulary drift")
    result.update(nonzero)
    return result


def _independent_validate_lifecycle(
        worker: Mapping[str, Any], row: Mapping[str, Any]) -> None:
    receipts = worker.get("execution_lifecycle_receipts")
    expected_count = 72 if row.get("regime") == "STEADY_E2E" else 1
    exact_fields = {
        "prepared_input_reused", "dynamic_device_upload_call_count",
        "dynamic_device_upload_bytes", "dynamic_accel_build_count",
        "dynamic_explicit_sync_count", "dynamic_blocking_upload_call_count",
        "dynamic_input_generation",
    }
    if type(receipts) is not list or len(receipts) != expected_count:
        raise RuntimeError("independent dynamic lifecycle count differs")
    for index, item in enumerate(receipts):
        if type(item) is not dict or set(item) != exact_fields:
            raise RuntimeError("independent dynamic lifecycle fields differ")
        for key in exact_fields - {"prepared_input_reused"}:
            if type(item[key]) is not int or item[key] < 0:
                raise RuntimeError("independent dynamic lifecycle counter invalid")
        if index == 0:
            relation = row.get("task") == TASKS[0]
            rtdl_triangle = row.get("arm") == RTDL and not relation
            expected_first = {
                "prepared_input_reused": False,
                "dynamic_device_upload_call_count": (
                    8 if rtdl_triangle else 2),
                "dynamic_device_upload_bytes": (
                    212992 if relation else 589824 if rtdl_triangle else 524288),
                "dynamic_accel_build_count": 1 if relation else 0,
                "dynamic_explicit_sync_count": 0,
                "dynamic_blocking_upload_call_count": 0,
                "dynamic_input_generation": 1,
            }
            if item != expected_first:
                raise RuntimeError("independent first dynamic execute differs")
        elif item != {
                "prepared_input_reused": True,
                "dynamic_device_upload_call_count": 0,
                "dynamic_device_upload_bytes": 0,
                "dynamic_accel_build_count": 0,
                "dynamic_explicit_sync_count": 0,
                "dynamic_blocking_upload_call_count": 0,
                "dynamic_input_generation": 1,
        }:
            raise RuntimeError("independent later dynamic reuse differs")
    direct = row.get("arm") == DIRECT
    evidence = worker.get("operation_ledger") if direct else worker.get("result")
    if type(evidence) is not dict \
            or (direct and evidence.get("dynamic_input_receipt") != receipts[-1]):
        raise RuntimeError("independent final dynamic receipt differs")


def _independent_validate_pyoptix(
        evidence: Mapping[str, Any], task: str) -> None:
    if evidence.get("live_execute_guard_inside_timer") is not False \
            or "independent_execute_guard" in evidence:
        raise RuntimeError("independent PyOptiX comparative guard is live")
    forbidden = {
        "execute_operation_counts", "operation_order",
        "prepare_operation_counts", "operation_ledger_scope",
        "independent_execute_guard",
    }
    if forbidden.intersection(evidence) \
            or evidence.get("operation_evidence_source") != (
                "UNTIMED_PREWORKER_KAT_AND_EXACT_SOURCE_BOUNDARY") \
            or evidence.get("optix_validation_mode") != "OFF" \
            or evidence.get("optix_log_callback_mode") != "OFF" \
            or evidence.get("module_optimization_level") != "DEFAULT" \
            or evidence.get("module_debug_level") != "NONE" \
            or evidence.get("required_sync_count") != 2 \
            or evidence.get(
                "status_output_commit_blocking_boundary_count") != 2:
        raise RuntimeError("independent PyOptiX operation authority differs")


def _independent_validate_rtdl_native(
        evidence: Mapping[str, Any], task: str,
        dynamic: Mapping[str, Any]) -> None:
    native = evidence.get("native_operation_receipt")
    fields = {
        "schema", "optix_launch_count", "host_blocking_boundary_count",
        "control_d2h_bytes", "output_d2h_bytes", "status_before_output",
        "output_d2h_after_status_failure", "role_counters_materialized",
        "prepared_input_reused", "dynamic_device_upload_call_count",
        "dynamic_device_upload_bytes", "dynamic_accel_build_count",
        "dynamic_explicit_sync_count", "dynamic_blocking_upload_call_count",
        "dynamic_input_generation",
    } | AUXILIARY_OPERATION_KEYS
    if type(native) is not dict or set(native) != fields \
            or type(dynamic) is not dict \
            or native.get("schema") \
            != "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2" \
            or native.get("optix_launch_count") != (2 if task == TASKS[0] else 1) \
            or native.get("host_blocking_boundary_count") != 2 \
            or native.get("control_d2h_bytes") != (16 if task == TASKS[0] else 4) \
            or native.get("output_d2h_bytes") \
            != (32768 if task == TASKS[0] else 8) \
            or native.get("status_before_output") is not True \
            or native.get("output_d2h_after_status_failure") != 0 \
            or native.get("role_counters_materialized") is not False \
            or not _plain_int(native.get(
                "dynamic_blocking_upload_call_count")) \
            or native["dynamic_blocking_upload_call_count"] != 0:
        raise RuntimeError("independent RTDL native operation receipt differs")
    expected_auxiliary = _expected_auxiliary_operation(RTDL, task)
    if any(native.get(key) != value
           for key, value in expected_auxiliary.items()):
        raise RuntimeError("independent RTDL native auxiliary receipt differs")
    for key in (
            "prepared_input_reused", "dynamic_device_upload_call_count",
            "dynamic_device_upload_bytes", "dynamic_accel_build_count",
            "dynamic_explicit_sync_count", "dynamic_blocking_upload_call_count",
            "dynamic_input_generation"):
        if native.get(key) != dynamic.get(key):
            raise RuntimeError("independent RTDL native/dynamic projection differs")


def _validate_product_binding_independently(
        binding: object,
        source_by_path: Mapping[str, Mapping[str, object]]) -> str:
    required = {
        "schema", "status", "clean_install_verifier_status", "wheel_sha256",
        "clean_install_verifier_sha256", "clean_install_run_sha256",
        "clean_install_result_sha256", "native_sha256",
        "native_custody_verifier_status", "native_custody_verifier_sha256",
        "native_custody_manifest_sha256", "native_custody_custody_sha256",
        "native_custody_source_file_count",
        "native_custody_dependency_file_count",
        "native_custody_toolchain_payload_count",
        "native_custody_source_commit", "native_custody_source_tree",
        "native_custody_hermetic_native_rebuild_claimed",
        "trust_root_sha256", "trust_head_sha256",
        "trust_predecessor_package_sha256", "trust_package_sha256",
        "triangle_artifact_sha256", "triangle_authority_sha256",
        "triangle_deployment_id", "triangle_executable_identity_sha256",
        "relation_artifact_sha256", "relation_authority_sha256",
        "relation_deployment_id", "relation_executable_identity_sha256",
        "source_commit", "source_tree", "source_package_file_count",
        "rtdsl_package_file_count", "rtdsl_package_tree_sha256",
        "rtdsl_init_sha256", "rtdlexe_module_sha256",
    }
    if not isinstance(binding, Mapping) or set(binding) != required \
            or binding.get("schema") \
            != "rtdl.goal5802.final_clean_rtdlexe_binding.v4" \
            or binding.get("status") != "PASS__FINAL_CLEAN_INSTALLED_RTLEXE" \
            or binding.get("clean_install_verifier_status") \
            != "PASS__INDEPENDENT_CLEAN_INSTALL_V3_VERIFICATION" \
            or binding.get("native_custody_verifier_status") \
            != "PASS__INDEPENDENT_NATIVE_CUSTODY_VERIFICATION" \
            or binding.get("native_custody_hermetic_native_rebuild_claimed") \
            is not False:
        raise RuntimeError("independent final product binding envelope differs")
    for key in required:
        if key.endswith("_sha256") and not _valid_sha256(binding.get(key)):
            raise RuntimeError(
                f"independent final product binding digest differs: {key}")
    for key in (
            "source_package_file_count", "rtdsl_package_file_count",
            "native_custody_source_file_count",
            "native_custody_dependency_file_count",
            "native_custody_toolchain_payload_count"):
        if type(binding.get(key)) is not int or binding[key] <= 0:
            raise RuntimeError(
                f"independent final product binding count differs: {key}")
    if binding["source_package_file_count"] \
            != binding["rtdsl_package_file_count"]:
        raise RuntimeError(
            "independent wheel/source package file counts differ")
    for key in (
            "source_commit", "source_tree", "native_custody_source_commit",
            "native_custody_source_tree"):
        if not isinstance(binding.get(key), str) \
                or re.fullmatch(r"[0-9a-f]{40}", str(binding[key])) is None:
            raise RuntimeError(
                f"independent final product Git identity differs: {key}")
    if binding["native_custody_source_commit"] != binding["source_commit"] \
            or binding["native_custody_source_tree"] != binding["source_tree"]:
        raise RuntimeError("independent native custody/product Git identity differs")
    for key in ("triangle_deployment_id", "relation_deployment_id"):
        if not isinstance(binding.get(key), str) or not binding[key]:
            raise RuntimeError(
                f"independent final product deployment id differs: {key}")
    cross_bindings = {
        "clean_install_verifier_sha256": (
            "scripts/goal5801_a3_verify_clean_install.py"),
        "native_custody_verifier_sha256": (
            "scripts/goal5801_a3_verify_native_custody.py"),
        "rtdsl_init_sha256": "src/rtdsl/__init__.py",
        "rtdlexe_module_sha256": "src/rtdsl/v4_rtdlexe.py",
    }
    for key, path in cross_bindings.items():
        row = source_by_path.get(path)
        if not isinstance(row, Mapping) \
                or binding[key] != row.get("sha256"):
            raise RuntimeError(
                f"independent product/source cross-binding differs: {key}")
    return _digest(dict(binding))


def _forecast_exact_keys(
        value: object, expected: set[str], label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != expected:
        raise RuntimeError(f"independent successor forecast {label} keys differ")
    return value


def _forecast_finite(
        value: object, label: str, *, minimum: float | None = None,
        maximum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeError(
            f"independent successor forecast {label} is not numeric")
    result = float(value)
    if not math.isfinite(result) \
            or (minimum is not None and result < minimum) \
            or (maximum is not None and result > maximum):
        raise RuntimeError(
            f"independent successor forecast {label} is out of range")
    return result


def _forecast_interval(
        value: object, label: str, *, minimum: float,
        maximum: float | None = None) -> list[float]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) \
            or len(value) != 2:
        raise RuntimeError(
            f"independent successor forecast {label} interval differs")
    lower = _forecast_finite(
        value[0], f"{label}[0]", minimum=minimum, maximum=maximum)
    upper = _forecast_finite(
        value[1], f"{label}[1]", minimum=minimum, maximum=maximum)
    if lower > upper:
        raise RuntimeError(
            f"independent successor forecast {label} interval is reversed")
    return [lower, upper]


def _forecast_nonnegative_int(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise RuntimeError(
            f"independent successor forecast {label} integer differs")
    return value


def _forecast_change_ids(value: object, label: str) -> list[str]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) \
            or not value:
        raise RuntimeError(
            f"independent successor forecast {label} change ids differ")
    result = list(value)
    if any(not isinstance(item, str) for item in result) \
            or len(result) != len(set(result)) \
            or any(item not in SUCCESSOR_FORECAST_CHANGE_IDS for item in result) \
            or result != [item for item in SUCCESSOR_FORECAST_CHANGE_IDS
                          if item in result]:
        raise RuntimeError(
            f"independent successor forecast {label} change ids differ")
    return result


def _forecast_operation_row(
        operation: Mapping[str, object], task_name: str,
        task_key: str, arm: str) -> dict[str, object]:
    task = operation.get(task_key)
    unmatched = operation.get("unmatched_internal_work")
    lifecycle = operation.get("dynamic_input_lifecycle")
    if not isinstance(task, Mapping) or not isinstance(task.get(arm), Mapping) \
            or not isinstance(unmatched, Mapping) \
            or not isinstance(unmatched.get("exact_per_arm_success_path"), Mapping) \
            or not isinstance(
                unmatched["exact_per_arm_success_path"].get(arm), Mapping) \
            or not isinstance(lifecycle, Mapping) \
            or not isinstance(lifecycle.get("first_execute_by_arm"), Mapping) \
            or not isinstance(lifecycle["first_execute_by_arm"].get(arm), Mapping) \
            or not isinstance(
                lifecycle["first_execute_by_arm"][arm].get(task_key), Mapping):
        raise RuntimeError(
            "independent successor forecast operation cost path absent")
    common = task[arm]
    internal = unmatched["exact_per_arm_success_path"][arm]
    dynamic = lifecycle["first_execute_by_arm"][arm][task_key]
    prefix = "relation" if task_key == "relation" else "triangle"
    optix = _forecast_nonnegative_int(
        common.get("optix_launch_count"),
        f"{task_key}.{arm}.optix_launch_count")
    auxiliary = _forecast_nonnegative_int(
        internal.get(f"{prefix}_auxiliary_cuda_kernel_launch_count"),
        f"{task_key}.{arm}.auxiliary_cuda_kernel_launch_count")
    if task_key == "relation":
        compaction = _forecast_nonnegative_int(
            common.get("semantic_compaction_launch_count"),
            f"{task_key}.{arm}.semantic_compaction_launch_count")
        capacity = _forecast_nonnegative_int(
            common.get("semantic_compaction_key_capacity"),
            f"{task_key}.{arm}.semantic_compaction_key_capacity")
        scratch = _forecast_nonnegative_int(
            common.get("semantic_compaction_scratch_bytes"),
            f"{task_key}.{arm}.semantic_compaction_scratch_bytes")
    else:
        for field in (
                "semantic_compaction_launch_count",
                "semantic_compaction_key_capacity",
                "semantic_compaction_scratch_bytes"):
            if field in common and _forecast_nonnegative_int(
                    common[field], f"{task_key}.{arm}.{field}") != 0:
                raise RuntimeError(
                    "independent successor triangle compaction cost differs")
        compaction = capacity = scratch = 0
    return {
        "task": task_name,
        "arm": arm,
        "optix_traversal_launch_count": optix,
        "auxiliary_cuda_kernel_launch_count": auxiliary,
        "total_explicit_gpu_launch_count": optix + auxiliary,
        "semantic_compaction_launch_count": compaction,
        "semantic_compaction_key_capacity": capacity,
        "semantic_compaction_scratch_bytes": scratch,
        "stream_ordered_memset_call_count": _forecast_nonnegative_int(
            internal.get(f"{prefix}_stream_ordered_memset_call_count"),
            f"{task_key}.{arm}.stream_ordered_memset_call_count"),
        "execution_parameter_h2d_bytes": _forecast_nonnegative_int(
            internal.get(f"{prefix}_execution_parameter_h2d_bytes"),
            f"{task_key}.{arm}.execution_parameter_h2d_bytes"),
        "compact_status_control_d2h_bytes": _forecast_nonnegative_int(
            common.get("compact_status_control_d2h_bytes"),
            f"{task_key}.{arm}.compact_status_control_d2h_bytes"),
        "status_output_commit_blocking_boundary_count": (
            _forecast_nonnegative_int(
                common.get("status_output_commit_blocking_boundary_count"),
                f"{task_key}.{arm}.status_output_commit_boundary_count")),
        "first_execute_dynamic_upload_call_count": _forecast_nonnegative_int(
            dynamic.get("dynamic_device_upload_call_count"),
            f"{task_key}.{arm}.dynamic_device_upload_call_count"),
        "first_execute_dynamic_upload_bytes": _forecast_nonnegative_int(
            dynamic.get("dynamic_device_upload_bytes"),
            f"{task_key}.{arm}.dynamic_device_upload_bytes"),
        "first_execute_dynamic_accel_build_count": _forecast_nonnegative_int(
            dynamic.get("dynamic_accel_build_count"),
            f"{task_key}.{arm}.dynamic_accel_build_count"),
    }


def _forecast_cost_inventory(
        operation: Mapping[str, object]) -> dict[str, object]:
    if operation.get("schema") \
            != "rtdl.goal5802.three_arm_operation_contract.v1":
        raise RuntimeError(
            "independent successor forecast operation schema differs")
    projection = _forecast_exact_keys(
        operation.get("forecast_cost_projection"),
        set(SUCCESSOR_FORECAST_OPERATION_PROJECTION),
        "operation forecast projection")
    if dict(projection) != SUCCESSOR_FORECAST_OPERATION_PROJECTION:
        raise RuntimeError(
            "independent successor forecast operation projection differs")
    common = operation.get("common_semantics")
    lifecycle = operation.get("dynamic_input_lifecycle")
    if not isinstance(common, Mapping) \
            or common.get("receipt_serialization_inside_timer") is not False \
            or common.get("forensic_hashing_inside_timer") is not False \
            or not isinstance(lifecycle, Mapping) \
            or lifecycle.get(
                "machine_receipt_and_exact_source_guard_required") is not True:
        raise RuntimeError(
            "independent successor forecast receipt timer contract differs")
    receipt_counts = lifecycle.get("regime_receipt_counts")
    if not isinstance(receipt_counts, Mapping) \
            or set(receipt_counts) != set(REGIMES):
        raise RuntimeError(
            "independent successor forecast regime receipt counts differ")
    rows = [
        _forecast_operation_row(operation, task, task_key, arm)
        for task, task_key in ((TASKS[0], "relation"), (TASKS[1], "triangle"))
        for arm in ARMS
    ]
    receipt_rows = []
    for regime in REGIMES:
        count = _forecast_nonnegative_int(
            receipt_counts.get(regime), f"receipt count {regime}")
        if count < 1:
            raise RuntimeError(
                "independent successor forecast receipt count is zero")
        receipt_rows.append({
            "regime": regime,
            "operation_receipt_count": count,
        })
    return {
        "schema": "rtdl.goal5802.final_cost_inventory.v1",
        "status": "MACHINE_DERIVED_FROM_EXACT_OPERATION_CONTRACT",
        "operation_contract_sha256": _digest(dict(operation)),
        "rows": rows,
        "regime_receipt_counts": receipt_rows,
        "receipt_and_deployment_overheads": {
            **SUCCESSOR_FORECAST_OPERATION_PROJECTION,
            "operation_receipt_serialization_inside_primary_timer": False,
            "forensic_hashing_inside_primary_timer": False,
        },
    }


def _validate_successor_forecast_independently(
        forecast: object, *, expected_identity: Mapping[str, object],
        operation: Mapping[str, object]) -> None:
    top = _forecast_exact_keys(forecast, {
        "schema", "status", "authorization", "predecessor_authority",
        "identity_binding", "final_cost_inventory",
        "changes_since_predecessor", "primary_predictions",
        "joint_prediction", "direct_context_predictions",
        "calibration_policy", "forecast_sha256",
    }, "envelope")
    if top.get("schema") != SUCCESSOR_FORECAST_SCHEMA \
            or top.get("status") != SUCCESSOR_FORECAST_STATUS:
        raise RuntimeError("independent successor forecast envelope differs")
    expected_authorization = {
        "formal_worker_zero_authorized": False,
        "registered_gpu_timing_authorized": False,
        "pod_execution_authorized": False,
        "performance_claim_authorized": False,
        "forecast_generation_without_manual_probabilities_allowed": False,
        "postresult_probability_change_allowed": False,
        "required_at_seal_registered_performance_observation_count": 0,
        "formal_execution_requires_this_seal_before_worker_zero": True,
    }
    authorization = _forecast_exact_keys(
        top.get("authorization"), set(expected_authorization), "authorization")
    if dict(authorization) != expected_authorization:
        raise RuntimeError(
            "independent successor forecast authorization differs")
    predecessor = _forecast_exact_keys(
        top.get("predecessor_authority"),
        set(SUCCESSOR_FORECAST_PREDECESSOR_AUTHORITY),
        "predecessor authority")
    if dict(predecessor) != SUCCESSOR_FORECAST_PREDECESSOR_AUTHORITY:
        raise RuntimeError(
            "independent successor forecast predecessor differs")
    identity = _forecast_exact_keys(
        top.get("identity_binding"), SUCCESSOR_FORECAST_IDENTITY_KEYS,
        "identity binding")
    if any(not _valid_sha256(identity.get(key))
           for key in SUCCESSOR_FORECAST_IDENTITY_KEYS) \
            or dict(identity) != dict(expected_identity):
        raise RuntimeError(
            "independent successor forecast identity binding differs")
    if top.get("changes_since_predecessor") \
            != list(SUCCESSOR_FORECAST_CHANGE_ROWS):
        raise RuntimeError(
            "independent successor forecast change ledger differs")

    primary = top.get("primary_predictions")
    primary_keys = {
        "task", "regime", "gate", "noninferiority_threshold",
        "predicted_median_interval",
        "predicted_95_percent_ci_upper_interval",
        "subjective_gate_pass_probability",
        "predecessor_subjective_gate_pass_probability",
        "manual_successor_probability_entry",
        "probability_copied_or_defaulted_from_predecessor",
        "change_reason_ids",
    }
    expected_pairs = [(task, regime) for task in TASKS for regime in REGIMES]
    if not isinstance(primary, list) or len(primary) != len(expected_pairs):
        raise RuntimeError(
            "independent successor forecast primary row count differs")
    referenced_changes: set[str] = set()
    for index, (row_value, pair) in enumerate(zip(primary, expected_pairs)):
        row = _forecast_exact_keys(
            row_value, primary_keys, f"primary row {index}")
        task, regime = pair
        threshold = row.get("noninferiority_threshold")
        if row.get("task") != task or row.get("regime") != regime \
                or row.get("gate") != SUCCESSOR_FORECAST_GATES[regime] \
                or isinstance(threshold, bool) \
                or not isinstance(threshold, (int, float)) \
                or not math.isfinite(float(threshold)) \
                or float(threshold) != THRESHOLDS[regime] \
                or row.get("manual_successor_probability_entry") is not True \
                or row.get(
                    "probability_copied_or_defaulted_from_predecessor") is not False:
            raise RuntimeError(
                "independent successor forecast primary row identity differs")
        _forecast_interval(
            row.get("predicted_median_interval"),
            f"primary {index} median", minimum=0.0)
        _forecast_interval(
            row.get("predicted_95_percent_ci_upper_interval"),
            f"primary {index} CI upper", minimum=0.0)
        _forecast_finite(
            row.get("subjective_gate_pass_probability"),
            f"primary {index} probability", minimum=0.0, maximum=1.0)
        predecessor_probability = _forecast_finite(
            row.get("predecessor_subjective_gate_pass_probability"),
            f"primary {index} predecessor probability",
            minimum=0.0, maximum=1.0)
        if predecessor_probability \
                != SUCCESSOR_FORECAST_PREDECESSOR_PROBABILITIES[pair]:
            raise RuntimeError(
                "independent successor predecessor probability differs")
        referenced_changes.update(_forecast_change_ids(
            row.get("change_reason_ids"), f"primary {index}"))

    joint = _forecast_exact_keys(top.get("joint_prediction"), {
        "all_six_gates_pass_probability_interval",
        "predecessor_all_six_gates_pass_probability_interval",
        "manual_successor_probability_entry",
        "probability_copied_or_defaulted_from_predecessor",
        "independence_assumed", "highest_risk_regime", "change_reason_ids",
    }, "joint prediction")
    if joint.get("manual_successor_probability_entry") is not True \
            or joint.get(
                "probability_copied_or_defaulted_from_predecessor") is not False \
            or joint.get("independence_assumed") is not False \
            or joint.get("highest_risk_regime") not in REGIMES \
            or _forecast_interval(
                joint.get("predecessor_all_six_gates_pass_probability_interval"),
                "predecessor joint", minimum=0.0, maximum=1.0) != [0.25, 0.40]:
        raise RuntimeError(
            "independent successor forecast joint prediction differs")
    _forecast_interval(
        joint.get("all_six_gates_pass_probability_interval"),
        "joint probability", minimum=0.0, maximum=1.0)
    referenced_changes.update(_forecast_change_ids(
        joint.get("change_reason_ids"), "joint prediction"))

    direct = top.get("direct_context_predictions")
    direct_keys = {
        "task", "regime", "metric", "predicted_median_interval",
        "manual_interval_entry", "change_reason_ids",
    }
    if not isinstance(direct, list) or len(direct) != len(TASKS):
        raise RuntimeError(
            "independent successor direct-context row count differs")
    for index, (row_value, task) in enumerate(zip(direct, TASKS)):
        row = _forecast_exact_keys(
            row_value, direct_keys, f"direct context row {index}")
        if row.get("task") != task or row.get("regime") != "STEADY_E2E" \
                or row.get("metric") != "PYOPTIX_OVER_DIRECT" \
                or row.get("manual_interval_entry") is not True:
            raise RuntimeError(
                "independent successor direct-context identity differs")
        _forecast_interval(
            row.get("predicted_median_interval"),
            f"direct context {index}", minimum=0.0)
        referenced_changes.update(_forecast_change_ids(
            row.get("change_reason_ids"), f"direct context {index}"))
    if referenced_changes != set(SUCCESSOR_FORECAST_CHANGE_IDS):
        raise RuntimeError(
            "independent successor forecast omits a required change")

    expected_calibration = {
        "probability_semantics": (
            "SUBJECTIVE_ENGINEERING_FORECAST__NO_INFERENTIAL_WEIGHT"),
        "primary_metric": (
            "RTDL_BLOCK_NS_OVER_PYOPTIX_BLOCK_NS__GREATER_THAN_ONE_MEANS_"
            "RTDL_SLOWER"),
        "gate_statistic": "PAIRED_BLOCK_BOOTSTRAP_95_PERCENT_CI_UPPER",
        "predecessor_use": "CALIBRATION_RECORD_ONLY__NOT_CURRENT_FORECAST",
        "registered_thresholds_unchanged": True,
        "row_by_row_calibration_after_result_required": True,
        "brier_score_or_p_value_claimed": False,
        "all_valid_results_including_all_losses_accepted": True,
        "postresult_rewrite_allowed": False,
    }
    calibration = _forecast_exact_keys(
        top.get("calibration_policy"), set(expected_calibration),
        "calibration policy")
    if dict(calibration) != expected_calibration:
        raise RuntimeError(
            "independent successor forecast calibration policy differs")
    if top.get("final_cost_inventory") != _forecast_cost_inventory(operation):
        raise RuntimeError(
            "independent successor forecast cost inventory differs")
    unsigned = dict(top)
    observed_seal = unsigned.pop("forecast_sha256")
    if not _valid_sha256(observed_seal) \
            or observed_seal != hashlib.sha256(
                SUCCESSOR_FORECAST_SEAL_DOMAIN + b"\0"
                + _canonical(unsigned)).hexdigest():
        raise RuntimeError("independent successor forecast seal differs")


def _validate_freeze_bytes(
        freeze: Mapping[str, Any], *, freeze_file_sha256: str,
        root: Path | None = None) -> None:
    if freeze.get("schema") != "rtdl.goal5802.local_premeasurement_freeze.v3" \
            or freeze.get("status") \
            != "FROZEN_LOCAL_PREMEASUREMENT__FORMAL_WORKER_ZERO_LOCKED":
        raise RuntimeError("independent freeze envelope differs")
    unsigned = dict(freeze)
    observed = unsigned.pop("freeze_sha256", None)
    if observed != _digest(unsigned):
        raise RuntimeError("independent freeze self-digest mismatch")
    if freeze.get("schedule_sha256") != _digest(freeze.get("schedule")) \
            or freeze.get("build_cold_absolute_schedule_sha256") \
            != _digest(freeze.get("build_cold_absolute_schedule")):
        raise RuntimeError("independent schedule digest mismatch")
    if not isinstance(freeze_file_sha256, str) or len(freeze_file_sha256) != 64:
        raise RuntimeError("independent freeze file identity invalid")
    source_rows = freeze.get("source_manifest")
    if not isinstance(source_rows, list) or not source_rows:
        raise RuntimeError("independent frozen source manifest absent")
    source_by_path: dict[str, Mapping[str, object]] = {}
    for row in source_rows:
        if not isinstance(row, Mapping) or set(row) != {
                "path", "bytes", "sha256"} \
                or not isinstance(row.get("path"), str) \
                or Path(str(row["path"])).is_absolute() \
                or ".." in Path(str(row["path"])).parts \
                or type(row.get("bytes")) is not int or row["bytes"] < 0 \
                or not _valid_sha256(row.get("sha256")) \
                or row["path"] in source_by_path:
            raise RuntimeError("independent frozen source row differs")
        source_by_path[str(row["path"])] = row
        if root is not None:
            source_path = root / str(row["path"])
            if source_path.is_symlink() or not source_path.is_file() \
                    or source_path.stat().st_size != row["bytes"] \
                    or _sha(source_path) != row["sha256"]:
                raise RuntimeError(
                    f"independent frozen source drift: {row['path']}")
    complete_product_binding_sha256 = _validate_product_binding_independently(
        freeze.get("product_binding"), source_by_path)
    workload = freeze.get("workload_authority")
    operation = freeze.get("operation_contract")
    goal5799_record = freeze.get("goal5799_repaired_contract_whole_file")
    if not isinstance(workload, Mapping) or not isinstance(operation, Mapping) \
            or not isinstance(goal5799_record, Mapping) \
            or set(goal5799_record) != {"path", "bytes", "sha256"} \
            or not isinstance(goal5799_record.get("path"), str) \
            or goal5799_record.get("path") not in source_by_path \
            or dict(source_by_path[str(goal5799_record["path"])]) \
            != dict(goal5799_record) \
            or not _valid_sha256(goal5799_record.get("sha256")):
        raise RuntimeError(
            "independent successor forecast source authorities differ")
    expected_forecast_identity = {
        "complete_product_binding_sha256": complete_product_binding_sha256,
        "workload_authority_sha256": _digest(dict(workload)),
        "operation_contract_sha256": _digest(dict(operation)),
        "comparative_schedule_sha256": _digest(freeze.get("schedule")),
        "build_cold_absolute_schedule_sha256": _digest(
            freeze.get("build_cold_absolute_schedule")),
        "complete_instrument_source_manifest_sha256": _digest(source_rows),
        "goal5799_repaired_contract_sha256": goal5799_record["sha256"],
    }
    repair = freeze.get("postresult_instrument_repair")
    if repair is not None:
        inherited_forecast = freeze.get("successor_subjective_forecast")
        if not isinstance(repair, Mapping) \
                or repair.get("schema") \
                != "rtdl.goal5802.postresult_instrument_repair.v1" \
                or repair.get("status") \
                != "FROZEN_BEFORE_CORRECTIVE_SUCCESSOR_WORKER_ZERO" \
                or repair.get("postresult_probability_modified") is not False \
                or repair.get("confirmatory_performance_claim_authorized") \
                is not False \
                or repair.get("descriptive_performance_evidence_authorized") \
                is not True \
                or freeze.get("forecast_disposition") != (
                    "INHERITED_PREDECESSOR_FORECAST__CALIBRATION_ONLY__NOT_A_"
                    "BLIND_PREDICTION_FOR_CORRECTIVE_SUCCESSOR") \
                or not isinstance(inherited_forecast, Mapping) \
                or not isinstance(
                    inherited_forecast.get("identity_binding"), Mapping):
            raise RuntimeError(
                "independent postresult forecast disposition differs")
        expected_forecast_identity = dict(
            inherited_forecast["identity_binding"])
    _validate_successor_forecast_independently(
        freeze.get("successor_subjective_forecast"),
        expected_identity=expected_forecast_identity,
        operation=operation)
    if PREDICTION_AUTHORITY_PATH not in source_by_path:
        raise RuntimeError(
            "independent successor predecessor source is absent")
    if root is not None:
        prediction_raw = (root / PREDICTION_AUTHORITY_PATH).read_bytes()
        try:
            prediction_text = prediction_raw.decode("utf-8")
        except UnicodeError as error:
            raise RuntimeError("independent prediction is not UTF-8") from error
        prediction_canonical = prediction_text.replace("\r\n", "\n")
        if "\r" in prediction_canonical:
            raise RuntimeError("independent prediction contains bare CR")
        prediction_bytes = prediction_canonical.encode("utf-8")
        prediction_blob = hashlib.sha1(
            f"blob {len(prediction_bytes)}\0".encode("ascii")
            + prediction_bytes).hexdigest()
        if len(prediction_bytes) != PREDICTION_AUTHORITY_BYTES \
                or hashlib.sha256(prediction_bytes).hexdigest() \
                != PREDICTION_AUTHORITY_SHA256 \
                or prediction_blob != PREDICTION_AUTHORITY_GIT_BLOB:
            raise RuntimeError("independent prediction authority bytes differ")


def _validate_correctness(
        worker: Mapping[str, Any], row: Mapping[str, Any],
        freeze: Mapping[str, Any]) -> None:
    task, arm = row["task"], row["arm"]
    direct = arm == DIRECT
    evidence = worker.get("correctness") if direct else worker.get("result")
    if not isinstance(evidence, Mapping):
        raise RuntimeError("worker correctness evidence absent")
    operation = worker.get("operation_ledger") if direct else evidence
    if not isinstance(operation, Mapping):
        raise RuntimeError("worker operation ledger absent")
    if direct:
        expected_evidence_fields = (
            {"oracle_exact", "canonical_row_count", "canonical_rows",
             "raw_event_count", "semantic_unique_count", "device_status",
             "device_overflow"}
            if task == TASKS[0]
            else {"oracle_exact", "device_status", "reduced_u64"})
        expected_operation_fields = (
            {"optix_launch_count",
             "async_h2d_call_count", "async_h2d_bytes",
             "async_d2h_call_count", "compact_status_control_d2h_bytes",
             "application_output_d2h_bytes", "total_success_d2h_bytes",
             "user_visible_output_bytes",
             "status_output_commit_blocking_boundary_count",
             "per_ray_d2h_bytes", "dynamic_input_receipt",
              "operation_evidence_source", "live_operation_trace_inside_timer",
              "optix_module_disk_cache_enabled", "optix_validation_mode",
              "optix_log_callback_mode", "module_optimization_level",
              "module_debug_level"}
            if task == TASKS[0] else
            {"optix_launch_count", "async_h2d_call_count", "async_h2d_bytes",
             "async_d2h_call_count", "device_intermediate_per_ray_bytes",
             "device_reset_bytes", "h2d_launch_parameter_bytes",
             "compact_status_control_d2h_bytes",
             "application_output_d2h_bytes", "total_success_d2h_bytes",
             "status_output_commit_blocking_boundary_count",
             "per_ray_d2h_bytes",
              "operation_evidence_source", "live_operation_trace_inside_timer",
              "dynamic_input_receipt", "optix_module_disk_cache_enabled",
              "optix_validation_mode", "optix_log_callback_mode",
              "module_optimization_level", "module_debug_level"})
        expected_operation_fields |= AUXILIARY_OPERATION_KEYS
    elif arm == PYOPTIX:
        common = {
            "device_status", "required_sync_count",
            "total_success_d2h_bytes", "compact_status_control_d2h_bytes",
            "application_output_d2h_bytes",
            "status_output_commit_blocking_boundary_count",
            "per_ray_d2h_bytes",
            "per_ray_host_materialized",
            "live_execute_guard_inside_timer",
            "optix_module_disk_cache_enabled",
            "optix_validation_mode", "optix_log_callback_mode",
            "module_optimization_level", "module_debug_level",
            "operation_evidence_source",
        }
        expected_evidence_fields = (
            common | {"output", "raw_event_count", "semantic_unique_count",
                      "device_overflow", "optix_launch_count",
                      "control_d2h_bytes", "output_d2h_bytes"}
            if task == TASKS[0] else
            common | {"launch_count", "reduced_u64", "status_d2h_bytes", "scalar_d2h_bytes",
                      "per_ray_device_intermediate_bytes", "device_reset_bytes",
                      "h2d_launch_parameter_bytes"})
        expected_evidence_fields |= AUXILIARY_OPERATION_KEYS
        expected_operation_fields = expected_evidence_fields
    else:
        common = {
            "device_status", "optix_launch_count",
            "compact_status_control_d2h_bytes",
            "application_output_d2h_bytes", "total_success_d2h_bytes",
            "status_output_commit_blocking_boundary_count",
            "per_ray_d2h_bytes",
            "per_ray_host_materialized", "traversal_receipt", "output_sha256",
            "executable_identity_sha256", "role_counters",
            "native_operation_receipt", "dynamic_input_receipt",
        }
        expected_evidence_fields = (
            common | {"output", "raw_event_count", "semantic_unique_count",
                      "user_visible_output_bytes"}
            if task == TASKS[0] else common | {"reduced_u64"})
        expected_evidence_fields |= AUXILIARY_OPERATION_KEYS
        expected_operation_fields = expected_evidence_fields
    if set(evidence) != expected_evidence_fields \
            or set(operation) != expected_operation_fields:
        raise RuntimeError(
            "independent correctness/operation fields differ: "
            f"evidence={sorted(set(evidence) ^ expected_evidence_fields)} "
            f"operation={sorted(set(operation) ^ expected_operation_fields)}")
    _independent_validate_lifecycle(worker, row)
    if arm == PYOPTIX:
        _independent_validate_pyoptix(evidence, task)
    elif arm == RTDL:
        if evidence.get("dynamic_input_receipt") \
                != worker["execution_lifecycle_receipts"][-1]:
            raise RuntimeError(
                "independent RTDL duplicated dynamic receipt differs")
        _independent_validate_rtdl_native(
            evidence, task, worker["execution_lifecycle_receipts"][-1])
        family = "relation" if task == TASKS[0] else "triangle"
        if evidence.get("executable_identity_sha256") != freeze[
                "product_binding"][f"{family}_executable_identity_sha256"]:
            raise RuntimeError("independent RTDL executable identity differs")
    if task == TASKS[0]:
        rows = evidence.get("canonical_rows") if direct else evidence.get("output")
        authority = freeze.get("workload_authority")
        expected_digest = authority.get("relation", {}).get("expected_rows_sha256") \
            if isinstance(authority, Mapping) else None
        if not isinstance(rows, list) or len(rows) != 4096 \
                or _digest(rows) != expected_digest:
            raise RuntimeError("relation exact output differs")
        if direct:
            if evidence.get("oracle_exact") is not True:
                raise RuntimeError("Direct relation oracle flag absent")
            for key, value, label in (
                    ("canonical_row_count", 4096, "Direct relation row count"),
                    ("raw_event_count", 8192, "Direct relation raw count"),
                    ("semantic_unique_count", 4096,
                     "Direct relation semantic unique count"),
                    ("device_status", 0, "Direct relation status"),
                    ("device_overflow", 0, "Direct relation overflow")):
                _require_int(evidence.get(key), value, label)
            expected = {
                "optix_launch_count": 2,
                "async_h2d_call_count": 2,
                "async_h2d_bytes": 240,
                "async_d2h_call_count": 2,
                "compact_status_control_d2h_bytes": 16,
                "application_output_d2h_bytes": 32768,
                "total_success_d2h_bytes": 32784,
                "user_visible_output_bytes": 32768,
                "status_output_commit_blocking_boundary_count": 2,
                "per_ray_d2h_bytes": 0,
                "optix_module_disk_cache_enabled": False,
                "optix_validation_mode": "OFF",
                "optix_log_callback_mode": "OFF",
                "module_optimization_level": "DEFAULT",
                "module_debug_level": "NONE",
                "operation_evidence_source": (
                    "UNTIMED_OBSERVER_SAME_TEMPLATE_CORE_AND_EXACT_SOURCE_AUDIT"),
                "live_operation_trace_inside_timer": False,
            }
        elif arm == PYOPTIX:
            expected = {
                "optix_launch_count": 2, "raw_event_count": 8192,
                "semantic_unique_count": 4096,
                "device_status": 0, "device_overflow": 0,
                "compact_status_control_d2h_bytes": 16,
                "application_output_d2h_bytes": 32768,
                "total_success_d2h_bytes": 32784,
                "status_output_commit_blocking_boundary_count": 2,
                "per_ray_d2h_bytes": 0,
                "per_ray_host_materialized": False,
                "optix_module_disk_cache_enabled": False,
                "optix_validation_mode": "OFF",
                "optix_log_callback_mode": "OFF",
                "module_optimization_level": "DEFAULT",
                "module_debug_level": "NONE",
            }
        else:
            status = evidence.get("device_status")
            if not isinstance(status, Mapping) or status.get("ok") is not True:
                raise RuntimeError("RTDL relation status is not OK")
            expected = {
                "optix_launch_count": 2, "raw_event_count": 8192,
                "semantic_unique_count": 4096,
                "compact_status_control_d2h_bytes": 16,
                "application_output_d2h_bytes": 32768,
                "user_visible_output_bytes": 32768,
                "total_success_d2h_bytes": 32784,
                "status_output_commit_blocking_boundary_count": 2,
                "per_ray_d2h_bytes": 0,
                "per_ray_host_materialized": False,
            }
    else:
        if direct:
            if evidence.get("oracle_exact") is not True:
                raise RuntimeError("Direct triangle oracle flag absent")
            _require_int(evidence.get("device_status"), 0,
                         "Direct triangle status")
            _require_int(evidence.get("reduced_u64"), 65530,
                         "Direct triangle scalar")
            expected = {
                "optix_launch_count": 1,
                "async_h2d_call_count": 1,
                "async_h2d_bytes": 120,
                "async_d2h_call_count": 2,
                "device_intermediate_per_ray_bytes": 131072,
                "device_reset_bytes": 131084,
                "h2d_launch_parameter_bytes": 120,
                "compact_status_control_d2h_bytes": 4,
                "application_output_d2h_bytes": 8,
                "total_success_d2h_bytes": 12, "per_ray_d2h_bytes": 0,
                "status_output_commit_blocking_boundary_count": 2,
                "optix_module_disk_cache_enabled": False,
                "optix_validation_mode": "OFF",
                "optix_log_callback_mode": "OFF",
                "module_optimization_level": "DEFAULT",
                "module_debug_level": "NONE",
                "operation_evidence_source": (
                    "UNTIMED_OBSERVER_SAME_TEMPLATE_CORE_AND_EXACT_SOURCE_AUDIT"),
                "live_operation_trace_inside_timer": False,
            }
        elif arm == PYOPTIX:
            expected = {
                "launch_count": 1, "device_status": 0,
                "reduced_u64": 65530,
                "compact_status_control_d2h_bytes": 4,
                "application_output_d2h_bytes": 8,
                "total_success_d2h_bytes": 12, "per_ray_d2h_bytes": 0,
                "status_output_commit_blocking_boundary_count": 2,
                "per_ray_host_materialized": False,
                "optix_module_disk_cache_enabled": False,
                "optix_validation_mode": "OFF",
                "optix_log_callback_mode": "OFF",
                "module_optimization_level": "DEFAULT",
                "module_debug_level": "NONE",
            }
        else:
            status = evidence.get("device_status")
            if not isinstance(status, Mapping) or status.get("ok") is not True:
                raise RuntimeError("RTDL triangle status is not OK")
            expected = {
                "optix_launch_count": 1, "reduced_u64": 65530,
                "compact_status_control_d2h_bytes": 4,
                "application_output_d2h_bytes": 8,
                "total_success_d2h_bytes": 12, "per_ray_d2h_bytes": 0,
                "per_ray_host_materialized": False,
                "status_output_commit_blocking_boundary_count": 2,
            }
    expected.update(_expected_auxiliary_operation(arm, task))
    for key, expected_value in expected.items():
        if operation.get(key) != expected_value:
            raise RuntimeError(f"operation ledger differs: {key}")


def _validate_phases(worker: Mapping[str, Any], row: Mapping[str, Any],
                     values: list[int], envelope_ns: Any) -> None:
    phases = worker.get("phase_durations_ns")
    required = {
        "process_startup_and_admission", "input_materialization",
        "load_or_deploy", "prepare",
        "steady_warmups", "complete_execute",
        "measurement_evidence_materialization", "close",
        "post_execution_identity_validation",
    }
    if not isinstance(phases, Mapping) or set(phases) != required:
        raise RuntimeError("worker phase-attribution fields differ")
    for key in required:
        value = phases[key]
        if isinstance(value, bool) or not isinstance(value, int) \
                or value < 0 or (key != "steady_warmups" and value == 0):
            raise RuntimeError(f"worker phase duration invalid: {key}")
    if row["regime"] == "STEADY_E2E":
        if phases["steady_warmups"] <= 0 \
                or phases["complete_execute"] != sum(values):
            raise RuntimeError("steady phase attribution differs")
    elif phases["steady_warmups"] != 0:
        raise RuntimeError("non-steady row carries warmup time")
    if row["regime"] == "PREPARE" and phases["prepare"] != values[0]:
        raise RuntimeError("prepare primary duration differs from phase")
    if row["regime"] == "DEPLOYMENT_COLD" and (
            phases["load_or_deploy"] + phases["prepare"]
            + phases["complete_execute"] != values[0]):
        raise RuntimeError("deployment-cold primary duration differs from phases")
    exclusive = sum(int(phases[key]) for key in required)
    if isinstance(envelope_ns, bool) or not isinstance(envelope_ns, int) \
            or envelope_ns <= 0 or exclusive > envelope_ns:
        raise RuntimeError("worker phase envelope is invalid")


def _validate_cache_conditioning(
        receipt: Mapping[str, Any], runtime: Mapping[str, Any] | None) -> None:
    value = receipt.get("preworker_common_cache_conditioning")
    roles: list[str] = []
    if not isinstance(value, Mapping) or set(value) != {
            "policy", "roles", "payload_bytes", "rows_sha256", "duration_ns",
            "os_shared_library_and_driver_cache_state"} \
            or value.get("roles") != roles \
            or value.get("policy") != (
                "NO_MANUAL_FILE_PAGE_CONDITIONING__OS_PAGE_CACHE_"
                "UNCONTROLLED__BALANCED_SIX_ORDER") \
            or value.get("os_shared_library_and_driver_cache_state") \
            != "UNCONTROLLED__DISCLOSED" \
            or value.get("payload_bytes") != 0 \
            or value.get("duration_ns") != 0:
        raise RuntimeError("comparative common cache-conditioning receipt differs")
    if runtime is not None:
        files = runtime.get("files")
        if not isinstance(files, Mapping):
            raise RuntimeError("runtime files absent for cache-conditioning recount")
        rows = [{
            "role": role,
            "bytes": files[role]["bytes"],
            "sha256": files[role]["sha256"],
        } for role in roles]
        expected_bytes = sum(int(row["bytes"]) for row in rows)
        if value.get("payload_bytes") != expected_bytes \
                or value.get("rows_sha256") != _digest(rows):
            raise RuntimeError("cache-conditioning identity recount differs")


def _validate_isolated_process_caches(receipt: Mapping[str, Any]) -> None:
    policy = receipt.get("isolated_process_cache_policy")
    end = receipt.get("isolated_process_cache_end_state")
    if not isinstance(policy, Mapping) or set(policy) != {
            "policy", "cuda_cache_disabled", "optix_cache_disabled",
            "cuda_cache_path", "cupy_cache_dir", "optix_cache_path",
            "xdg_cache_home", "home", "tmp",
            "all_directories_empty_before_worker"} \
            or policy.get("policy") \
            != "FRESH_EMPTY_PER_WORKER_PROCESS_CACHE_ROOTS" \
            or policy.get("cuda_cache_disabled") is not True \
            or policy.get("optix_cache_disabled") is not True \
            or policy.get("all_directories_empty_before_worker") is not True \
            or not all(isinstance(policy.get(key), str) and policy[key]
                       for key in ("cuda_cache_path", "cupy_cache_dir",
                                   "optix_cache_path", "xdg_cache_home",
                                   "home", "tmp")):
        raise RuntimeError("independent isolated process-cache policy differs")
    if end != {
            "file_count": 0, "payload_bytes": 0,
            "rows_sha256": hashlib.sha256(b"[]").hexdigest(),
            "all_cache_roots_file_empty_after_worker": True}:
        raise RuntimeError("independent process cache was not empty after worker")


def _worker_value(
        receipt: Mapping[str, Any], *, row: Mapping[str, Any],
        freeze: Mapping[str, Any], freeze_sha: str, authority_sha: str,
        runtime_sha: str, runtime: Mapping[str, Any] | None = None) -> float:
    if receipt.get("status") != "PASS":
        raise RuntimeError("failed row has no accepted duration")
    worker = receipt.get("worker_result")
    if not isinstance(worker, Mapping):
        raise RuntimeError("worker result absent")
    expected_schema = (
        "rtdl.goal5802.direct_scalar.worker.v1" if row["arm"] == DIRECT
        else "rtdl.goal5802.python_arm_worker_result.v1")
    common_worker_fields = {
        "schema", "status", "worker_id", "arm", "task", "regime",
        "freeze_file_sha256", "execution_authority_sha256",
        "runtime_manifest_sha256", "execute_or_regime_durations_ns",
        "registered_performance_timing_count", "phase_durations_ns",
        "execution_lifecycle_receipts", "receipt_serialization_inside_timer",
        "close_inside_primary_timer",
    }
    python_boundary_fields = {
        "constructor_evidence_inside_primary_timer",
        "constructor_runtime_preload_receipt",
        "new_forbidden_module_load_inside_primary_timer",
        "primary_estimator_name", "primary_estimator_scope",
        "primary_timer_new_module_load_policy",
    }
    expected_worker_fields = (
        common_worker_fields | {"correctness", "operation_ledger",
                                "retained_executed_ptx_sha256"}
        | ({"retained_compaction_cubin_sha256"}
           if row["task"] == TASKS[0] else set())
        if row["arm"] == DIRECT else
        common_worker_fields | {"result", "loaded_runtime_identity"}
        | python_boundary_fields)
    if set(worker) != expected_worker_fields \
            or worker.get("schema") != expected_schema \
            or worker.get("status") != "PASS" \
            or worker.get("worker_id") != row["worker_id"] \
            or worker.get("arm") != row["arm"] \
            or worker.get("task") != row["task"] \
            or worker.get("regime") != row["regime"] \
            or worker.get("freeze_file_sha256") != freeze_sha \
            or worker.get("execution_authority_sha256") != authority_sha \
            or worker.get("runtime_manifest_sha256") != runtime_sha \
            or worker.get("receipt_serialization_inside_timer") is not False \
            or worker.get("close_inside_primary_timer") is not False:
        raise RuntimeError("comparative worker identity/boundary differs")
    if row["arm"] != DIRECT:
        expected_estimator = (
            "WARM_PROCESS_DEPLOYMENT_COLD"
            if row["regime"] == "DEPLOYMENT_COLD" else row["regime"])
        expected_scope = (
            "LOAD_OR_DEPLOY_PLUS_PREPARE_PLUS_COMPLETE_EXECUTE__EXCLUDES_"
            "PROCESS_STARTUP_ADMISSION_AND_ARM_RUNTIME_MODULE_PRELOAD"
            if row["regime"] == "DEPLOYMENT_COLD"
            else "REGIME_DEFINED_BY_GOAL5802_FREEZE")
        if worker.get("primary_estimator_name") != expected_estimator \
                or worker.get("primary_estimator_scope") != expected_scope \
                or worker.get("new_forbidden_module_load_inside_primary_timer") \
                is not False \
                or worker.get("primary_timer_new_module_load_policy") \
                != "REJECT_ALL_NOT_PRELOADED" \
                or worker.get("constructor_evidence_inside_primary_timer") \
                is not False \
                or not isinstance(worker.get(
                    "constructor_runtime_preload_receipt"), Mapping):
            raise RuntimeError("Python primary-boundary evidence differs")
    if row["arm"] == DIRECT:
        retained = worker.get("retained_executed_ptx_sha256")
        retained_compaction = worker.get("retained_compaction_cubin_sha256")
        if not isinstance(retained, str) or len(retained) != 64 \
                or any(ch not in "0123456789abcdef" for ch in retained) \
                or (row["task"] == TASKS[0] and (
                    not isinstance(retained_compaction, str)
                    or len(retained_compaction) != 64
                    or any(ch not in "0123456789abcdef"
                           for ch in retained_compaction))) \
                or (row["task"] != TASKS[0]
                    and retained_compaction is not None):
            raise RuntimeError("independent Direct retained PTX identity invalid")
        if runtime is not None and retained != runtime["files"][
                "matched_ptx"]["sha256"]:
            raise RuntimeError("independent Direct retained PTX differs from runtime")
        if runtime is not None and row["task"] == TASKS[0] \
                and retained_compaction != runtime["files"][
                    "compaction_cubin"]["sha256"]:
            raise RuntimeError(
                "independent Direct retained compaction cubin differs")
    elif runtime is not None:
        identity = worker.get("loaded_runtime_identity")
        expected_identity = (
            ({
                "distribution_version": runtime["pyoptix"][
                    "distribution_version"],
                "initializer_path": runtime["files"][
                    "pyoptix_initializer"]["path"],
                "initializer_sha256": runtime["files"][
                    "pyoptix_initializer"]["sha256"],
                "extension_path": runtime["files"][
                    "pyoptix_extension"]["path"],
                "extension_sha256": runtime["files"][
                    "pyoptix_extension"]["sha256"],
                "optix_api_version": runtime["pyoptix"]["optix_api_version"],
                "matched_ptx_path": runtime["files"]["matched_ptx"]["path"],
                "matched_ptx_sha256": runtime["files"]["matched_ptx"]["sha256"],
                "retained_matched_ptx_sha256": runtime["files"][
                    "matched_ptx"]["sha256"],
            } | ({
                "compaction_cubin_path": runtime["files"][
                    "compaction_cubin"]["path"],
                "compaction_cubin_sha256": runtime["files"][
                    "compaction_cubin"]["sha256"],
                "retained_compaction_cubin_sha256": runtime["files"][
                    "compaction_cubin"]["sha256"],
            } if row["task"] == TASKS[0] else {}))
            if row["arm"] == PYOPTIX else {
                "rtdsl_init_path": runtime["files"]["rtdsl_init"]["path"],
                "rtdsl_init_sha256": runtime["files"]["rtdsl_init"]["sha256"],
                "rtdlexe_module_path": runtime["files"]["rtdlexe_module"]["path"],
                "rtdlexe_module_sha256": runtime["files"][
                    "rtdlexe_module"]["sha256"],
                "executed_executable_identity_sha256": freeze[
                    "product_binding"][
                        ("relation" if row["task"] == TASKS[0] else "triangle")
                        + "_executable_identity_sha256"],
            })
        if not isinstance(identity, Mapping) or dict(identity) != expected_identity:
            raise RuntimeError("independent Python loaded identity absent")
    elif row["arm"] != DIRECT:
        identity = worker.get("loaded_runtime_identity")
        expected_fields = (
            {"distribution_version", "initializer_path", "initializer_sha256",
             "extension_path", "extension_sha256", "optix_api_version",
             "matched_ptx_path", "matched_ptx_sha256",
             "retained_matched_ptx_sha256"}
            | ({"compaction_cubin_path", "compaction_cubin_sha256",
                "retained_compaction_cubin_sha256"}
               if row["task"] == TASKS[0] else set())
            if row["arm"] == PYOPTIX else
            {"rtdsl_init_path", "rtdsl_init_sha256", "rtdlexe_module_path",
             "rtdlexe_module_sha256",
             "executed_executable_identity_sha256"})
        if not isinstance(identity, Mapping) or set(identity) != expected_fields:
            raise RuntimeError("independent Python loaded identity shape differs")
    values = worker.get("execute_or_regime_durations_ns")
    required = 64 if row["regime"] == "STEADY_E2E" else 1
    if not isinstance(values, list) or len(values) != required \
            or any(isinstance(item, bool) or not isinstance(item, int) or item <= 0
                   for item in values):
        raise RuntimeError("worker duration vector invalid")
    _require_int(worker.get("registered_performance_timing_count"), required,
                 "registered timing count")
    _validate_cache_conditioning(receipt, runtime)
    _validate_phases(
        worker, row, values, receipt.get("controller_process_envelope_ns"))
    _validate_correctness(worker, row, freeze)
    return _median(values)


def _compiler_runtime_authority_independently(
        value: Any, *, runtime: Mapping[str, Any] | None) \
        -> tuple[dict[str, Mapping[str, Any]],
                 dict[str, Mapping[str, Any]]]:
    required = {
        "schema", "status", "host_runtime_provenance_file_sha256",
        "host_runtime_provenance_receipt_sha256", "distributions",
        "loaded_module_files", "authority_sha256",
    }
    unsigned = dict(value) if isinstance(value, Mapping) else {}
    seal = unsigned.pop("authority_sha256", None)
    distributions = value.get("distributions") \
        if isinstance(value, Mapping) else None
    modules = value.get("loaded_module_files") \
        if isinstance(value, Mapping) else None
    if not isinstance(value, Mapping) or set(value) != required \
            or value.get("schema") \
            != "rtdl.goal5802.numba_llvmlite_runtime_authority.v1" \
            or value.get("status") != "EXACT_SEALED_BUILD_COMPILER_RUNTIME" \
            or not _valid_sha256(
                value.get("host_runtime_provenance_file_sha256")) \
            or not _valid_sha256(
                value.get("host_runtime_provenance_receipt_sha256")) \
            or seal != _digest(unsigned) \
            or not isinstance(distributions, list) \
            or not isinstance(modules, list) \
            or [row.get("name") for row in distributions
                if isinstance(row, Mapping)] != ["numba", "llvmlite"] \
            or [row.get("name") for row in modules
                if isinstance(row, Mapping)] != ["numba", "llvmlite"]:
        raise RuntimeError("independent compiler runtime authority differs")
    distribution_by_name: dict[str, Mapping[str, Any]] = {}
    module_by_name: dict[str, Mapping[str, Any]] = {}
    for row in distributions:
        if not isinstance(row, Mapping) or set(row) != {
                "name", "version", "file_count", "payload_bytes",
                "tree_sha256"} \
                or not isinstance(row.get("version"), str) or not row["version"] \
                or not _plain_int(row.get("file_count")) \
                or row["file_count"] <= 0 \
                or not _plain_int(row.get("payload_bytes")) \
                or row["payload_bytes"] <= 0 \
                or not _valid_sha256(row.get("tree_sha256")):
            raise RuntimeError("independent compiler distribution row differs")
        distribution_by_name[str(row["name"])] = row
    for row in modules:
        if not isinstance(row, Mapping) or set(row) != {
                "name", "path", "bytes", "sha256"} \
                or not isinstance(row.get("path"), str) \
                or not Path(row["path"]).is_absolute() \
                or not _plain_int(row.get("bytes")) or row["bytes"] <= 0 \
                or not _valid_sha256(row.get("sha256")):
            raise RuntimeError("independent compiler module row differs")
        module_by_name[str(row["name"])] = row

    if runtime is not None:
        files = runtime.get("files")
        file_record = files.get("host_runtime_provenance") \
            if isinstance(files, Mapping) else None
        if not isinstance(file_record, Mapping) \
                or value.get("host_runtime_provenance_file_sha256") \
                != file_record.get("sha256"):
            raise RuntimeError("independent compiler host-file binding differs")
        host_path = Path(str(file_record.get("path")))
        if not host_path.is_file() or host_path.is_symlink() \
                or _sha(host_path) != file_record.get("sha256"):
            raise RuntimeError("independent compiler host file differs")
        host = _load(host_path)
        host_unsigned = dict(host)
        host_seal = host_unsigned.pop("receipt_sha256", None)
        if host.get("schema") \
                != "rtdl.goal5802.host_runtime_provenance.v3" \
                or host_seal != _digest(host_unsigned) \
                or value.get("host_runtime_provenance_receipt_sha256") \
                != host_seal:
            raise RuntimeError("independent compiler host receipt differs")
        host_distributions = host.get("distributions")
        host_modules = host.get("loaded_module_files")
        host_by_distribution = {
            row.get("name"): row for row in host_distributions
            if isinstance(row, Mapping)} \
            if isinstance(host_distributions, list) else {}
        expected_distributions = []
        expected_modules = []
        for name in ("numba", "llvmlite"):
            source = host_by_distribution.get(name)
            module = host_modules.get(name) \
                if isinstance(host_modules, Mapping) else None
            distribution_files = source.get("files") \
                if isinstance(source, Mapping) else None
            matching_files = [
                item for item in distribution_files
                if isinstance(item, Mapping)
                and isinstance(module, Mapping)
                and item.get("path") == module.get("path")
            ] if isinstance(distribution_files, list) else []
            if not isinstance(source, Mapping) \
                    or not isinstance(module, Mapping) \
                    or len(matching_files) != 1 \
                    or matching_files[0].get("bytes") != module.get("bytes") \
                    or matching_files[0].get("sha256") != module.get("sha256"):
                raise RuntimeError("independent compiler host rows absent")
            expected_distributions.append({
                "name": name, "version": source.get("version"),
                "file_count": source.get("file_count"),
                "payload_bytes": source.get("payload_bytes"),
                "tree_sha256": source.get("tree_sha256"),
            })
            expected_modules.append({"name": name, **dict(module)})
        if distributions != expected_distributions \
                or modules != expected_modules:
            raise RuntimeError("independent compiler authority projection differs")
    return distribution_by_name, module_by_name


def _validate_build_compiler_runtime_independently(
        worker: Mapping[str, Any], *, row: Mapping[str, Any],
        authority: Any, runtime: Mapping[str, Any] | None) -> None:
    distribution_by_name, module_by_name = \
        _compiler_runtime_authority_independently(authority, runtime=runtime)
    identity = worker.get("compiler_runtime_identity")
    if row["arm"] != RTDL:
        if identity is not None:
            raise RuntimeError(
                "independent non-RTDL compiler runtime identity differs")
        return
    unsigned = dict(identity) if isinstance(identity, Mapping) else {}
    identity_seal = unsigned.pop("identity_sha256", None)
    modules = identity.get("actual_loaded_module_files") \
        if isinstance(identity, Mapping) else None
    if not isinstance(identity, Mapping) or set(identity) != {
            "schema", "status", "compiler_runtime_authority_sha256",
            "actual_loaded_module_files", "actual_loaded_module_files_sha256",
            "identity_sha256"} \
            or identity.get("schema") \
            != "rtdl.goal5802.build_cold_compiler_runtime_identity.v1" \
            or identity.get("status") \
            != "PASS__ACTUAL_NUMBA_LLVM_LITE_MATCH_SEALED_RUNTIME" \
            or identity.get("compiler_runtime_authority_sha256") \
            != authority.get("authority_sha256") \
            or not isinstance(modules, list) \
            or identity.get("actual_loaded_module_files_sha256") \
            != _digest(modules) \
            or identity_seal != _digest(unsigned) \
            or [item.get("name") for item in modules
                if isinstance(item, Mapping)] != ["numba", "llvmlite"]:
        raise RuntimeError("independent RTDL compiler runtime identity differs")
    for item in modules:
        name = item.get("name") if isinstance(item, Mapping) else None
        distribution = distribution_by_name.get(str(name))
        module = module_by_name.get(str(name))
        if not isinstance(item, Mapping) or set(item) != {
                "name", "version", "path", "bytes", "sha256"} \
                or not isinstance(distribution, Mapping) \
                or not isinstance(module, Mapping) \
                or item.get("version") != distribution.get("version") \
                or item.get("path") != module.get("path") \
                or item.get("bytes") != module.get("bytes") \
                or item.get("sha256") != module.get("sha256"):
            raise RuntimeError(
                "independent RTDL actual compiler module differs")


def _build_value(
        receipt: Mapping[str, Any], *, row: Mapping[str, Any],
        freeze_sha: str, authority_sha: str, runtime_sha: str,
        verify_output_files: bool, freeze: Mapping[str, Any],
        runtime: Mapping[str, Any] | None,
        compiler_runtime_authority: Any) -> float:
    if receipt.get("status") != "PASS":
        raise RuntimeError("failed build row")
    worker = receipt.get("worker_result")
    duration = worker.get("duration_ns") if isinstance(worker, Mapping) else None
    expected_outputs = {
        DIRECT: {"direct_executable", "matched_ptx"},
        PYOPTIX: {"matched_ptx"},
        RTDL: {"unsigned_rtdlexe", "detached_unsigned_authority"},
    }
    if row["task"] == TASKS[0] and row["arm"] in {DIRECT, PYOPTIX}:
        expected_outputs[row["arm"]].add(
            "relation_semantic_compaction_cubin")
    if not isinstance(worker, Mapping) \
            or worker.get("schema") \
            != "rtdl.goal5802.build_cold_worker_result.v1" \
            or worker.get("status") != "PASS" \
            or worker.get("worker_id") != row["worker_id"] \
            or worker.get("task") != row["task"] \
            or worker.get("arm") != row["arm"] \
            or worker.get("regime") != "BUILD_COLD_ABSOLUTE_DIAGNOSTIC" \
            or worker.get("freeze_file_sha256") != freeze_sha \
            or worker.get("execution_authority_sha256") != authority_sha \
            or worker.get("runtime_manifest_sha256") != runtime_sha \
            or worker.get("true_build_executed") is not True \
            or worker.get("prebuilt_product_read_as_build") is not False \
            or worker.get("build_boundary") \
            != "PRE_SIGNING_PRE_DEPLOYMENT_BUILD_PRODUCT" \
            or worker.get("deployable_product_claimed") is not False \
            or worker.get("signing_or_trust_governance_inside_timer") is not False \
            or worker.get("registered_performance_timing_count") != 1 \
            or set(worker.get("outputs", {})) != expected_outputs[row["arm"]] \
            or isinstance(duration, bool) or not isinstance(duration, int) \
            or duration <= 0:
        raise RuntimeError("BUILD_COLD identity or declared boundary differs")
    for output in worker["outputs"].values():
        if not isinstance(output, Mapping) or set(output) != {
                "path", "bytes", "sha256"} \
                or not isinstance(output.get("bytes"), int) \
                or isinstance(output.get("bytes"), bool) or output["bytes"] <= 0 \
                or not isinstance(output.get("sha256"), str) \
                or len(output["sha256"]) != 64:
            raise RuntimeError("BUILD_COLD output identity invalid")
        if verify_output_files:
            path = Path(output["path"])
            if not path.is_absolute() or not path.is_file() or path.is_symlink() \
                    or path.stat().st_size != output["bytes"] \
                    or _sha(path) != output["sha256"]:
                raise RuntimeError("BUILD_COLD output bytes differ")
    import_identity = worker.get("rtdsl_import_identity")
    if row["arm"] != RTDL:
        if import_identity is not None:
            raise RuntimeError(
                "independent non-RTDL BUILD_COLD import identity differs")
    else:
        product = freeze["product_binding"]
        required_names = {
            "rtdsl", "rtdsl.v4", "rtdsl.v4_callback_lifecycle",
            "rtdsl.v4_rtdlexe",
            ("rtdsl.v4_bounded_relation_optix_compiler"
             if row["task"] == TASKS[0]
             else "rtdsl.v4_triangle_standard_library"),
        }
        if row["task"] != TASKS[0]:
            required_names.add("rtdsl.v4_triangle_reduction_optix_compiler")
        modules = (import_identity.get("loaded_rtdsl_modules")
                   if isinstance(import_identity, Mapping) else None)
        if not isinstance(import_identity, Mapping) or set(import_identity) != {
                "schema", "status", "rtdsl_package_file_count",
                "rtdsl_package_tree_sha256", "required_module_names",
                "loaded_rtdsl_modules", "loaded_rtdsl_modules_sha256"} \
                or import_identity.get("schema") \
                != "rtdl.goal5802.build_cold_rtdsl_import_identity.v1" \
                or import_identity.get("status") \
                != "PASS__ALL_LOADED_RTDL_MODULES_FROM_SEALED_PACKAGE" \
                or import_identity.get("rtdsl_package_file_count") \
                != product["rtdsl_package_file_count"] \
                or import_identity.get("rtdsl_package_tree_sha256") \
                != product["rtdsl_package_tree_sha256"] \
                or import_identity.get("required_module_names") \
                != sorted(required_names) \
                or not isinstance(modules, list) or not modules \
                or import_identity.get("loaded_rtdsl_modules_sha256") \
                != _digest(modules):
            raise RuntimeError(
                "independent RTDL BUILD_COLD import identity differs")
        package_rows = None
        package_root = None
        if runtime is not None:
            package = runtime["directories"]["rtdsl_package"]
            package_rows = package.get("files")
            package_root = Path(str(package["path"]))
        by_relative = {
            item.get("path"): item for item in package_rows
            if isinstance(item, Mapping)} if isinstance(package_rows, list) \
            else None
        observed_names: set[str] = set()
        for module in modules:
            expected = (by_relative.get(module.get("relative_path"))
                        if isinstance(module, Mapping)
                        and by_relative is not None else None)
            if not isinstance(module, Mapping) or set(module) != {
                    "module", "path", "relative_path", "bytes", "sha256"} \
                    or not isinstance(module.get("module"), str) \
                    or module["module"] in observed_names \
                    or not isinstance(module.get("relative_path"), str) \
                    or not module["relative_path"].startswith("rtdsl/") \
                    or type(module.get("bytes")) is not int \
                    or module["bytes"] <= 0 \
                    or not _valid_sha256(module.get("sha256")) \
                    or by_relative is not None and (
                        not isinstance(expected, Mapping)
                        or module["bytes"] != expected.get("bytes")
                        or module["sha256"] != expected.get("sha256")
                        or Path(str(module.get("path"))) != package_root / str(
                            module["relative_path"]).removeprefix("rtdsl/")):
                raise RuntimeError(
                    "independent RTDL BUILD_COLD imported module row differs")
            observed_names.add(str(module["module"]))
        if not required_names.issubset(observed_names):
            raise RuntimeError(
                "independent RTDL BUILD_COLD required module absent")
    _validate_build_compiler_runtime_independently(
        worker, row=row, authority=compiler_runtime_authority,
        runtime=runtime)
    return float(duration)


def _validate_raw_receipt(
        receipt: Mapping[str, Any], *, row: Mapping[str, Any], raw_root: Path,
        kind: str, expected_command: list[str]) -> None:
    expected_name = (
        f"comparative_{int(row['ordinal']):04d}_{row['worker_id']}"
        if kind == "comparative" else
        f"build_cold_{int(row['ordinal']):04d}_{row['worker_id']}")
    if receipt.get("worker_directory_name") != expected_name:
        raise RuntimeError("raw worker directory name differs")
    directory = raw_root / expected_name
    if not directory.is_dir() or directory.is_symlink():
        raise RuntimeError("raw worker directory absent")
    receipt_path = directory / "receipt.json"
    stdout_path = directory / "stdout.bin"
    stderr_path = directory / "stderr.bin"
    command_path = directory / "command.json"
    if _load(receipt_path) != receipt:
        raise RuntimeError("raw receipt bytes differ from controller index")
    stdout = stdout_path.read_bytes()
    stderr = stderr_path.read_bytes()
    if len(stdout) != receipt.get("stdout_bytes") \
            or hashlib.sha256(stdout).hexdigest() != receipt.get("stdout_sha256") \
            or len(stderr) != receipt.get("stderr_bytes") \
            or hashlib.sha256(stderr).hexdigest() != receipt.get("stderr_sha256"):
        raise RuntimeError("raw stdout/stderr identity differs")
    try:
        parsed = json.loads(stdout)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError("raw stdout is not one JSON document") from error
    if parsed != receipt.get("worker_result"):
        raise RuntimeError("raw stdout parse differs from indexed worker result")
    command = json.loads(command_path.read_text(encoding="utf-8"))
    if command != expected_command \
            or any(literal in " ".join(command) for literal in LEGACY_LITERALS):
        raise RuntimeError("raw command identity/legacy exclusion differs")


def _validate_indexed_receipt(
        receipt: Mapping[str, Any], *, row: Mapping[str, Any], kind: str) -> None:
    expected_schema = (
        "rtdl.goal5802.comparative_controller_worker_receipt.v1"
        if kind == "comparative"
        else "rtdl.goal5802.build_cold_controller_worker_receipt.v1")
    expected_name = (
        f"comparative_{int(row['ordinal']):04d}_{row['worker_id']}"
        if kind == "comparative" else
        f"build_cold_{int(row['ordinal']):04d}_{row['worker_id']}")
    required = {
        "schema", "worker_directory_name", "schedule_row", "status",
        "exit_code", "timed_out", "spawn_error",
        "new_process_group_or_session", "orphan_process_group_detected",
        "controller_process_envelope_ns",
        "stdout_bytes", "stdout_sha256", "stderr_bytes", "stderr_sha256",
        "worker_result", "comparative_measurement_boundary",
        "preworker_common_cache_conditioning",
        "isolated_process_cache_policy", "isolated_process_cache_end_state",
    }
    digests = (receipt.get("stdout_sha256"), receipt.get("stderr_sha256"))
    if set(receipt) != required or receipt.get("schema") != expected_schema \
            or receipt.get("worker_directory_name") != expected_name \
            or receipt.get("schedule_row") != row \
            or receipt.get("status") not in {
                "PASS", "FAIL__NO_RETRY_OR_REPLACEMENT"} \
            or not isinstance(receipt.get("timed_out"), bool) \
            or receipt.get("new_process_group_or_session") is not True \
            or not isinstance(receipt.get("orphan_process_group_detected"), bool) \
            or (receipt.get("spawn_error") is not None
                and not isinstance(receipt.get("spawn_error"), str)) \
            or isinstance(receipt.get("controller_process_envelope_ns"), bool) \
            or not isinstance(receipt.get("controller_process_envelope_ns"), int) \
            or receipt["controller_process_envelope_ns"] <= 0 \
            or any(isinstance(receipt.get(key), bool)
                   or not isinstance(receipt.get(key), int)
                   or receipt[key] < 0 for key in ("stdout_bytes", "stderr_bytes")) \
            or any(not isinstance(item, str) or len(item) != 64
                   or any(ch not in "0123456789abcdef" for ch in item)
                   for item in digests):
        raise RuntimeError("indexed controller receipt envelope differs")
    if (kind == "comparative" and not isinstance(
            receipt.get("preworker_common_cache_conditioning"), Mapping)) \
            or (kind == "build" and receipt.get(
                "preworker_common_cache_conditioning") is not None):
        raise RuntimeError("indexed cache-conditioning envelope differs")
    boundary = receipt.get("comparative_measurement_boundary")
    if (kind == "build" and boundary is not None) \
            or (kind == "comparative" and receipt["status"] == "PASS"
                and not isinstance(boundary, Mapping)) \
            or (kind == "comparative" and receipt["status"] != "PASS"
                and boundary is not None and not isinstance(boundary, Mapping)):
        raise RuntimeError("indexed measurement boundary envelope differs")
    _validate_isolated_process_caches(receipt)
    if receipt["status"] == "PASS" and (
            receipt.get("exit_code") != 0 or receipt.get("timed_out") is not False
            or receipt.get("spawn_error") is not None
            or receipt.get("orphan_process_group_detected") is not False
            or not isinstance(receipt.get("worker_result"), Mapping)):
        raise RuntimeError("indexed PASS receipt process disposition differs")


def _expected_command(
        *, row: Mapping[str, Any], kind: str, runtime: Mapping[str, Any],
        root: Path, freeze_path: Path, authority_path: Path,
        runtime_path: Path, raw_root: Path) -> list[str]:
    files = runtime["files"]
    snapshot_root = (raw_root / "host_code_snapshot").resolve(strict=True)
    if kind == "build":
        name = f"build_cold_{int(row['ordinal']):04d}_{row['worker_id']}"
        return [
            *_independent_controlled_python_command(
                runtime, import_root=snapshot_root,
                module="experiments.goal5802_premeasurement.build_cold_worker"),
            "--arm", str(row["arm"]), "--task", str(row["task"]),
            "--worker-id", str(row["worker_id"]), "--root", str(root),
            "--freeze", str(freeze_path), "--execution-authority",
            str(authority_path), "--runtime-manifest", str(runtime_path),
            "--output-directory", str(raw_root / name / "built_product"),
        ]
    task = str(row["task"])
    regime = str(row["regime"])
    arm = str(row["arm"])
    common = [
        "--task", task, "--regime", regime,
        "--ptx", str(files["matched_ptx"]["path"]),
        "--ptx-sha256", str(files["matched_ptx"]["sha256"]),
    ]
    if task.startswith("CUSTOM_AABB"):
        common.extend([
            "--compaction-cubin", str(files["compaction_cubin"]["path"]),
            "--compaction-cubin-sha256",
            str(files["compaction_cubin"]["sha256"]),
        ])
    if arm == DIRECT:
        return [
            str(files["direct_scalar_worker"]["path"]),
            "--worker-id", str(row["worker_id"]),
            "--freeze-sha256", _sha(freeze_path),
            "--authority-sha256", _sha(authority_path),
            "--runtime-manifest-sha256", _sha(runtime_path),
            *common,
        ]
    command = [
        *_independent_controlled_python_command(
            runtime, import_root=snapshot_root,
            module="experiments.goal5802_premeasurement.python_worker"),
        "--arm", arm, "--task", task, "--regime", regime,
        "--root", str(root), "--freeze", str(freeze_path),
        "--execution-authority", str(authority_path),
        "--runtime-manifest", str(runtime_path),
        "--worker-id", str(row["worker_id"]),
    ]
    if arm == PYOPTIX:
        result = [*command, "--ptx", str(files["matched_ptx"]["path"])]
        if task.startswith("CUSTOM_AABB"):
            result.extend([
                "--compaction-cubin",
                str(files["compaction_cubin"]["path"]),
            ])
        return result
    family = "relation" if task.startswith("CUSTOM_AABB") else "triangle"
    return [
        *command,
        "--artifact", str(files[f"{family}_artifact"]["path"]),
        "--authority", str(files[f"{family}_authority"]["path"]),
        "--trust-root", str(files["trust_root"]["path"]),
        "--trust-head", str(files["trust_head"]["path"]),
        "--trust-package", str(files["trust_package"]["path"]),
        "--native-library", str(files["native_library"]["path"]),
        "--deployment-id", str(runtime["deployment_ids"][family]),
    ]


def _independent_preflight_file_record(
        value: object, *, expected_path: Path,
        expected_document: Mapping[str, Any] | None = None) -> dict[str, object]:
    """Rehash one raw preflight payload and, for JSON, its exact bytes."""

    if not isinstance(value, Mapping):
        raise RuntimeError("independent formal preflight file row absent")
    path = expected_path.resolve(strict=True)
    observed = _independent_regular_file_identity(path)
    if dict(value) != observed:
        raise RuntimeError("independent formal preflight file identity differs")
    if expected_document is not None:
        expected_bytes = json.dumps(
            expected_document, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        if path.read_bytes() != expected_bytes or _load(path) != dict(
                expected_document):
            raise RuntimeError(
                "independent formal preflight JSON bytes differ")
    return observed


def _validate_preflight_process_independently(
        value: object, *, expected_command: Sequence[str],
        expected_stdout: bytes, evidence: object,
        evidence_path: Path) -> None:
    """Rebuild one subprocess record and its separately preserved raw JSON."""

    if not isinstance(value, Mapping) or set(value) != {
            "command", "exit_code", "stdout_utf8", "stdout_sha256",
            "stderr_utf8", "stderr_sha256"} \
            or value.get("command") != list(expected_command) \
            or value.get("exit_code") != 0 \
            or not isinstance(value.get("stdout_utf8"), str) \
            or value["stdout_utf8"].encode("utf-8") != expected_stdout \
            or value.get("stdout_sha256") != hashlib.sha256(
                expected_stdout).hexdigest() \
            or value.get("stderr_utf8") != "" \
            or value.get("stderr_sha256") != hashlib.sha256(b"").hexdigest():
        raise RuntimeError("independent formal preflight process differs")
    _independent_preflight_file_record(
        evidence, expected_path=evidence_path, expected_document=value)


def _validate_formal_runtime_preflight_independently(
        value: object, *, runtime: Mapping[str, Any], runtime_sha: str,
        runtime_path: Path, freeze: Mapping[str, Any], raw_root: Path,
        root: Path) -> None:
    """Reconstruct the live worker-zero gate from raw target/compiler bytes."""

    required = {
        "schema", "status", "runtime_manifest_file_sha256",
        "loader_environment", "target_reobservation",
        "direct_nvrtc_compile_identity", "python_nvrtc_compile_identity",
        "rtdsl_package_import_identity",
        "cross_arm_libnvrtc_builtins_version_equal", "clock_read_count",
        "registered_performance_timing_count", "gpu_kernel_launch_count",
        "formal_worker_count", "preflight_sha256",
    }
    if not isinstance(value, Mapping):
        raise RuntimeError("independent formal runtime preflight absent")
    unsigned = dict(value)
    seal = unsigned.pop("preflight_sha256", None)
    if set(value) != required \
            or value.get("schema") \
            != "rtdl.goal5802.formal_runtime_preflight.v1" \
            or value.get("status") \
            != "PASS__LIVE_TARGET_AND_CROSS_ARM_NVRTC_BEFORE_WORKER_ZERO" \
            or value.get("runtime_manifest_file_sha256") != runtime_sha \
            or runtime_sha != _sha(runtime_path) \
            or value.get("cross_arm_libnvrtc_builtins_version_equal") \
            is not True \
            or any(not _plain_int(value.get(key)) or value[key] != 0
                   for key in (
                       "clock_read_count",
                       "registered_performance_timing_count",
                       "gpu_kernel_launch_count", "formal_worker_count")) \
            or seal != _digest(unsigned):
        raise RuntimeError("independent formal runtime preflight envelope differs")

    raw_root = raw_root.resolve(strict=True)
    root = root.resolve(strict=True)
    preflight_root = (raw_root / "runtime_preflight").resolve(strict=True)
    snapshot_root = (raw_root / "host_code_snapshot").resolve(strict=True)
    if preflight_root.parent != raw_root or snapshot_root.parent != raw_root:
        raise RuntimeError("independent formal preflight root binding differs")
    expected_preflight_files = {
        "direct_process.json", "fresh_python_matched.ptx",
        "fresh_python_nvrtc.json", "python_process.json", "receipt.json",
        "rtdsl_package_process.json", "target_observation.json",
        "target_process.json",
    }
    observed_preflight_files = {
        path.name for path in preflight_root.iterdir()
        if path.is_file() and not path.is_symlink()}
    if observed_preflight_files != expected_preflight_files \
            or any(path.is_symlink() or not path.is_file()
                   for path in preflight_root.iterdir()):
        raise RuntimeError("independent formal preflight payload set differs")
    receipt_path = preflight_root / "receipt.json"
    expected_receipt_bytes = json.dumps(
        value, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    if receipt_path.read_bytes() != expected_receipt_bytes \
            or _load(receipt_path) != dict(value):
        raise RuntimeError("independent formal preflight receipt bytes differ")

    source_rows = freeze.get("source_manifest")
    source_by_path = {
        str(row.get("path")): row for row in source_rows
        if isinstance(row, Mapping)} if isinstance(source_rows, list) else {}
    snapshot_sources: dict[str, dict[str, object]] = {}
    for relative in (
            "scripts/goal5802_capture_target_untimed.py",
            "scripts/goal5802_capture_rtdsl_package_import_untimed.py",
            "scripts/goal5802_nvrtc_compile_child.py"):
        frozen = source_by_path.get(relative)
        path = snapshot_root / Path(relative)
        observed = _independent_regular_file_identity(path)
        if not isinstance(frozen, Mapping) or set(frozen) != {
                "path", "bytes", "sha256"} \
                or observed["bytes"] != frozen.get("bytes") \
                or observed["sha256"] != frozen.get("sha256"):
            raise RuntimeError(
                f"independent preflight snapshot source differs: {relative}")
        snapshot_sources[relative] = observed

    files = runtime["files"]
    directories = runtime["directories"]
    loader = value.get("loader_environment")
    if not isinstance(loader, Mapping) or set(loader) != {
            "PATH", "LD_LIBRARY_PATH", "LD_PRELOAD"} \
            or loader.get("LD_PRELOAD") is not None \
            or not isinstance(loader.get("PATH"), str) or not loader["PATH"] \
            or any(not item or not Path(item).is_absolute()
                   for item in loader["PATH"].split(os.pathsep)) \
            or loader.get("LD_LIBRARY_PATH") is not None and (
                not isinstance(loader["LD_LIBRARY_PATH"], str)
                or not loader["LD_LIBRARY_PATH"]
                or any(not item or not Path(item).is_absolute()
                       for item in loader["LD_LIBRARY_PATH"].split(os.pathsep))):
        raise RuntimeError("independent formal preflight loader differs")
    host_runtime = _load(Path(str(files["host_runtime_provenance"]["path"])))
    frozen_environment = host_runtime.get("thread_and_visibility_environment")
    if not isinstance(frozen_environment, Mapping) \
            or any(loader.get(key) != frozen_environment.get(key)
                   for key in ("PATH", "LD_LIBRARY_PATH", "LD_PRELOAD")):
        raise RuntimeError("independent preflight/host loader crossbind differs")

    target = value.get("target_reobservation")
    if not isinstance(target, Mapping) or set(target) != {
            "process", "process_evidence", "receipt", "document",
            "all_frozen_fields_equal"} \
            or target.get("all_frozen_fields_equal") is not True:
        raise RuntimeError("independent formal target reobservation differs")
    target_path = preflight_root / "target_observation.json"
    target_document = target.get("document")
    frozen_target = _load(Path(str(
        files["target_observation_receipt"]["path"])))
    target_projection = _target_observation_projection_independently(
        target_document, files=files,
        expected_loader_environment={
            "LD_LIBRARY_PATH": loader["LD_LIBRARY_PATH"],
            "LD_PRELOAD": loader["LD_PRELOAD"]},
        exact_frozen_document=frozen_target,
        context="formal target reobservation")
    if runtime.get("target_observation") != {
            **target_projection,
            "observation_receipt_sha256": files[
                "target_observation_receipt"]["sha256"]}:
        raise RuntimeError("independent formal target/runtime crossbind differs")
    _independent_preflight_file_record(
        target.get("receipt"), expected_path=target_path,
        expected_document=target_document)
    capture = snapshot_root / "scripts/goal5802_capture_target_untimed.py"
    target_command = [
        *_independent_controlled_python_command(
            runtime, import_root=snapshot_root, script=capture),
        "--nvidia-smi", str(files["nvidia_smi"]["path"]),
        "--nvcc", str(files["nvcc"]["path"]),
        "--output", str(target_path),
    ]
    target_stdout = json.dumps(
        target_document, sort_keys=True).encode("utf-8") + b"\n"
    _validate_preflight_process_independently(
        target.get("process"), expected_command=target_command,
        expected_stdout=target_stdout, evidence=target.get("process_evidence"),
        evidence_path=preflight_root / "target_process.json")

    package = value.get("rtdsl_package_import_identity")
    if not isinstance(package, Mapping) or set(package) != {
            "process", "process_evidence", "document",
            "all_modules_match_sealed_package"} \
            or package.get("all_modules_match_sealed_package") is not True:
        raise RuntimeError("independent formal RTDL package preflight differs")
    package_document = package.get("document")
    package_record = directories["rtdsl_package"]
    package_rows = package_record.get("files")
    by_relative = {
        row.get("path"): row for row in package_rows
        if isinstance(row, Mapping)} if isinstance(package_rows, list) else {}
    if not isinstance(package_document, Mapping):
        raise RuntimeError("independent RTDL package preflight document absent")
    package_unsigned = dict(package_document)
    package_seal = package_unsigned.pop("receipt_sha256", None)
    imported = package_document.get("imported_modules")
    expected_python = Path(str(files["clean_python"].get(
        "resolved_path", files["clean_python"]["path"]))).resolve(strict=True)
    if set(package_document) != {
            "schema", "status", "python_executable", "package_root",
            "rtdsl_package_file_count", "rtdsl_package_tree_sha256",
            "required_module_names", "imported_modules", "clock_read_count",
            "registered_performance_timing_count", "gpu_kernel_launch_count",
            "formal_worker_count", "receipt_sha256"} \
            or package_document.get("schema") \
            != "rtdl.goal5802.rtdsl_package_import_preflight.v1" \
            or package_document.get("status") \
            != "PASS__CLEAN_PYTHON_IMPORTED_SEALED_RTDSL_PACKAGE" \
            or package_document.get("python_executable") != str(expected_python) \
            or package_document.get("package_root") != package_record["path"] \
            or package_document.get("rtdsl_package_file_count") \
            != package_record["file_count"] \
            or package_document.get("rtdsl_package_tree_sha256") \
            != package_record["tree_sha256"] \
            or package_document.get("required_module_names") \
            != list(RTDSL_PACKAGE_PREFLIGHT_MODULES) \
            or not isinstance(imported, list) \
            or len(imported) != len(RTDSL_PACKAGE_PREFLIGHT_MODULES) \
            or any(not _plain_int(package_document.get(key))
                   or package_document[key] != 0 for key in (
                       "clock_read_count", "registered_performance_timing_count",
                       "gpu_kernel_launch_count", "formal_worker_count")) \
            or package_seal != _digest(package_unsigned):
        raise RuntimeError("independent RTDL package preflight document differs")
    package_root = Path(str(package_record["path"]))
    for expected_name, row in zip(
            RTDSL_PACKAGE_PREFLIGHT_MODULES, imported, strict=True):
        expected = (by_relative.get(row.get("relative_path"))
                    if isinstance(row, Mapping) else None)
        if not isinstance(row, Mapping) or set(row) != {
                "module", "path", "relative_path", "bytes", "sha256"} \
                or row.get("module") != expected_name \
                or not isinstance(expected, Mapping) \
                or row.get("bytes") != expected.get("bytes") \
                or row.get("sha256") != expected.get("sha256") \
                or Path(str(row.get("path"))) != package_root / str(
                    row.get("relative_path")).removeprefix("rtdsl/"):
            raise RuntimeError(
                "independent RTDL package imported module differs")
    package_child = snapshot_root / (
        "scripts/goal5802_capture_rtdsl_package_import_untimed.py")
    package_command = [
        *_independent_controlled_python_command(
            runtime, import_root=snapshot_root, script=package_child),
        "--package-root", str(package_record["path"]),
        "--package-file-count", str(package_record["file_count"]),
        "--package-tree-sha256", str(package_record["tree_sha256"]),
    ]
    package_stdout = json.dumps(
        package_document, sort_keys=True).encode("utf-8") + b"\n"
    _validate_preflight_process_independently(
        package.get("process"), expected_command=package_command,
        expected_stdout=package_stdout,
        evidence=package.get("process_evidence"),
        evidence_path=preflight_root / "rtdsl_package_process.json")

    direct = value.get("direct_nvrtc_compile_identity")
    if not isinstance(direct, Mapping) or set(direct) != {
            "process", "process_evidence", "document",
            "prepare_document_byte_projection_equal"} \
            or direct.get("prepare_document_byte_projection_equal") is not True:
        raise RuntimeError("independent formal Direct preflight differs")
    direct_document = _validate_direct_loaded_nvrtc_independently(
        direct.get("document"))
    direct_build = _load(Path(str(
        files["direct_worker_build_receipt"]["path"])))
    if direct_build.get("schema") \
            != "rtdl.goal5802.direct_worker_untimed_build_receipt.v2" \
            or direct_build.get("loaded_nvrtc_identity_document") \
            != direct_document:
        raise RuntimeError("independent formal Direct prepare crossbind differs")
    direct_command = [
        str(files["direct_scalar_worker"]["path"]),
        "--local-nvrtc-identity"]
    _validate_preflight_process_independently(
        direct.get("process"), expected_command=direct_command,
        expected_stdout=_direct_nvrtc_identity_stdout_bytes(direct_document),
        evidence=direct.get("process_evidence"),
        evidence_path=preflight_root / "direct_process.json")

    python = value.get("python_nvrtc_compile_identity")
    if not isinstance(python, Mapping) or set(python) != {
            "process", "process_evidence", "receipt", "document", "product",
            "matched_ptx_byte_identical"} \
            or python.get("matched_ptx_byte_identical") is not True:
        raise RuntimeError("independent formal Python preflight differs")
    child = snapshot_root / "scripts/goal5802_nvrtc_compile_child.py"
    product_path = preflight_root / "fresh_python_matched.ptx"
    child_receipt_path = preflight_root / "fresh_python_nvrtc.json"
    cc = str(runtime["target_observation"]["compute_capability"])
    cc_match = re.fullmatch(r"([0-9]+)\.([0-9]+)", cc)
    if cc_match is None:
        raise RuntimeError("independent formal preflight architecture differs")
    compute = "compute_" + "".join(cc_match.groups())
    sm = "sm_" + "".join(cc_match.groups())
    python_command = [
        *_independent_controlled_python_command(
            runtime, import_root=snapshot_root, script=child),
        "--mode", "ptx", "--source", str(files["device_source"]["path"]),
        "--compute-capability", cc, "--nvrtc-library",
        str(files["nvrtc_library"]["path"]), "--output", str(product_path),
        "--receipt", str(child_receipt_path), "--optix-include",
        str(directories["optix_include"]["path"]), "--cuda-include",
        str(directories["cuda_include"]["path"]),
    ]
    python_document = python.get("document")
    if not isinstance(python_document, Mapping):
        raise RuntimeError("independent formal Python child absent")
    child_unsigned = dict(python_document)
    child_seal = child_unsigned.pop("receipt_sha256", None)
    child_required = {
        "schema", "status", "pid", "parent_pid", "argv", "cwd", "mode",
        "source", "include_roots", "compute_capability", "compile_options",
        "target", "product", "loaded_nvrtc", "clock_read_count",
        "gpu_kernel_launch_count", "formal_worker_count",
        "registered_performance_timing_count", "receipt_sha256",
    }
    expected_product = _independent_regular_file_identity(product_path)
    expected_source = _independent_regular_file_identity(
        Path(str(files["device_source"]["path"])))
    loaded = _validate_independent_loaded_nvrtc(
        python_document.get("loaded_nvrtc"))
    if set(python_document) != child_required \
            or python_document.get("schema") \
            != "rtdl.goal5802.fresh_nvrtc_compile_child.v2" \
            or python_document.get("status") \
            != "PASS__FRESH_PROCESS_UNTIMED_NVRTC_COMPILE" \
            or not _plain_int(python_document.get("pid")) \
            or int(python_document["pid"]) <= 0 \
            or not _plain_int(python_document.get("parent_pid")) \
            or int(python_document["parent_pid"]) <= 0 \
            or python_document["pid"] == python_document["parent_pid"] \
            or python_document.get("argv") != [
                str(child), *python_command[7:]] \
            or python_document.get("cwd") != str(root) \
            or python_document.get("mode") != "ptx" \
            or python_document.get("source") != expected_source \
            or python_document.get("include_roots") != {
                "optix": directories["optix_include"]["path"],
                "cuda": directories["cuda_include"]["path"]} \
            or python_document.get("compute_capability") != cc \
            or python_document.get("compile_options") != [
                "--std=c++17", "--device-as-default-execution-space",
                "--relocatable-device-code=true",
                f"--gpu-architecture={compute}",
                f"-I{directories['optix_include']['path']}",
                f"-I{directories['cuda_include']['path']}",
                f"-I{Path(str(directories['cuda_include']['path'])) / 'nv'}"] \
            or python_document.get("target") != sm \
            or python_document.get("product") != expected_product \
            or child_seal != _digest(child_unsigned) \
            or any(not _plain_int(python_document.get(key))
                   or python_document[key] != 0 for key in (
                       "clock_read_count", "gpu_kernel_launch_count",
                       "formal_worker_count",
                       "registered_performance_timing_count")):
        raise RuntimeError("independent formal Python child differs")
    _independent_preflight_file_record(
        python.get("receipt"), expected_path=child_receipt_path,
        expected_document=python_document)
    if python.get("product") != expected_product \
            or product_path.read_bytes() != Path(str(
                files["matched_ptx"]["path"])).read_bytes() \
            or _single_ptx_target_from_bytes(product_path.read_bytes()) != sm:
        raise RuntimeError("independent formal Python PTX differs")
    python_stdout = json.dumps({
        "status": python_document["status"], "pid": python_document["pid"],
        "product_sha256": expected_product["sha256"],
        "receipt_sha256": python_document["receipt_sha256"],
    }, sort_keys=True).encode("utf-8") + b"\n"
    _validate_preflight_process_independently(
        python.get("process"), expected_command=python_command,
        expected_stdout=python_stdout, evidence=python.get("process_evidence"),
        evidence_path=preflight_root / "python_process.json")

    expected_loaded = {
        "library": {
            "path": files["nvrtc_library"]["path"],
            "bytes": files["nvrtc_library"]["bytes"],
            "sha256": files["nvrtc_library"]["sha256"],
            "canonical_regular_file": True, "symlink": False},
        "builtins": {
            "path": files["nvrtc_builtins"]["path"],
            "bytes": files["nvrtc_builtins"]["bytes"],
            "sha256": files["nvrtc_builtins"]["sha256"],
            "canonical_regular_file": True, "symlink": False},
        "version": runtime["architecture_contract"]["libnvrtc_version"],
    }
    if loaded != expected_loaded \
            or direct_document["loaded_library_path"] \
            != loaded["library"]["path"] \
            or direct_document["loaded_library_bytes"] \
            != loaded["library"]["bytes"] \
            or direct_document["loaded_library_sha256"] \
            != loaded["library"]["sha256"] \
            or direct_document["loaded_builtins_path"] \
            != loaded["builtins"]["path"] \
            or direct_document["loaded_builtins_bytes"] \
            != loaded["builtins"]["bytes"] \
            or direct_document["loaded_builtins_sha256"] \
            != loaded["builtins"]["sha256"] \
            or direct_document["nvrtc_version"] != {
                "major": loaded["version"][0],
                "minor": loaded["version"][1]}:
        raise RuntimeError("independent formal cross-arm NVRTC differs")


def _validate_formal_runtime_preflight_failure_independently(
        value: object, *, failure_path: Path, runtime_sha: str,
        expected_loader_environment: Mapping[str, object] | None = None) -> None:
    """Recount a terminal worker-zero preflight failure from preserved bytes.

    A failed preflight intentionally has no controller result.  This verifier
    therefore operates directly on its durable failure receipt and the exact
    sibling payload set it names; it does not import the controller validator.
    """

    required = {
        "schema", "status", "failed_stage", "error",
        "runtime_manifest_file_sha256", "loader_environment",
        "preserved_preflight_payloads", "retry_count", "replacement_count",
        "clock_read_count", "registered_performance_timing_count",
        "gpu_kernel_launch_count", "formal_worker_count", "failure_sha256",
    }
    stages = {
        "PREFLIGHT_ROOT_CREATED", "TARGET_REOBSERVATION_PROCESS",
        "TARGET_REOBSERVATION_VALIDATE", "RTDSL_PACKAGE_IMPORT_PROCESS",
        "RTDSL_PACKAGE_IMPORT_VALIDATE", "DIRECT_NVRTC_IDENTITY_PROCESS",
        "DIRECT_NVRTC_IDENTITY_VALIDATE", "PYTHON_NVRTC_IDENTITY_PROCESS",
        "PYTHON_NVRTC_IDENTITY_VALIDATE",
        "CROSS_ARM_NVRTC_IDENTITY_COMPARE",
        "LOADER_AND_TOOL_ENVIRONMENT_COMPARE", "SUCCESS_RECEIPT_SEAL",
    }
    if not isinstance(value, Mapping):
        raise RuntimeError("independent formal preflight failure absent")
    unsigned = dict(value)
    seal = unsigned.pop("failure_sha256", None)
    error = value.get("error")
    loader = value.get("loader_environment")
    if set(value) != required \
            or value.get("schema") \
            != "rtdl.goal5802.formal_runtime_preflight_failure.v1" \
            or value.get("status") \
            != "FAIL__TERMINATED_BEFORE_FORMAL_WORKER_ZERO" \
            or value.get("failed_stage") not in stages \
            or not isinstance(error, Mapping) \
            or set(error) != {"type", "message"} \
            or not all(isinstance(error.get(key), str) and error[key]
                       for key in ("type", "message")) \
            or value.get("runtime_manifest_file_sha256") != runtime_sha \
            or not isinstance(loader, Mapping) \
            or set(loader) != {"PATH", "LD_LIBRARY_PATH", "LD_PRELOAD"} \
            or loader.get("LD_PRELOAD") is not None \
            or not isinstance(loader.get("PATH"), str) or not loader["PATH"] \
            or any(not item or not Path(item).is_absolute()
                   for item in loader["PATH"].split(os.pathsep)) \
            or loader.get("LD_LIBRARY_PATH") is not None and (
                not isinstance(loader["LD_LIBRARY_PATH"], str)
                or not loader["LD_LIBRARY_PATH"]
                or any(not item or not Path(item).is_absolute()
                       for item in loader["LD_LIBRARY_PATH"].split(os.pathsep))) \
            or expected_loader_environment is not None \
            and dict(loader) != dict(expected_loader_environment) \
            or any(not _plain_int(value.get(key)) or value[key] != 0
                   for key in (
                       "retry_count", "replacement_count", "clock_read_count",
                       "registered_performance_timing_count",
                       "gpu_kernel_launch_count", "formal_worker_count")) \
            or seal != _digest(unsigned):
        raise RuntimeError("independent formal preflight failure differs")
    path = failure_path.resolve(strict=True)
    if path.name != "failure_receipt.json" or path.is_symlink() \
            or path.read_bytes() != json.dumps(
                value, indent=2, sort_keys=True).encode("utf-8") + b"\n" \
            or _load(path) != dict(value):
        raise RuntimeError("independent formal failure receipt bytes differ")
    preflight_root = path.parent
    if (preflight_root / "receipt.json").exists() \
            or (preflight_root / "receipt.json").is_symlink():
        raise RuntimeError("independent formal success/failure receipts coexist")
    observed_rows: list[dict[str, object]] = []
    for payload in sorted(preflight_root.iterdir(), key=lambda item: item.name):
        if payload == path:
            continue
        if payload.is_symlink() or not payload.is_file():
            raise RuntimeError("independent formal failure has special payload")
        observed_rows.append({
            "name": payload.name,
            **_independent_regular_file_identity(payload.resolve(strict=True)),
        })
        if payload.name.endswith("_process.json"):
            process = _load(payload)
            if set(process) != {
                    "command", "exit_code", "stdout_utf8", "stdout_sha256",
                    "stderr_utf8", "stderr_sha256"} \
                    or not isinstance(process.get("command"), list) \
                    or not process["command"] \
                    or not all(isinstance(item, str) and item
                               for item in process["command"]) \
                    or not _plain_int(process.get("exit_code")) \
                    or not isinstance(process.get("stdout_utf8"), str) \
                    or not isinstance(process.get("stderr_utf8"), str) \
                    or process.get("stdout_sha256") != hashlib.sha256(
                        process["stdout_utf8"].encode("utf-8")).hexdigest() \
                    or process.get("stderr_sha256") != hashlib.sha256(
                        process["stderr_utf8"].encode("utf-8")).hexdigest() \
                    or payload.read_bytes() != json.dumps(
                        process, indent=2, sort_keys=True).encode("utf-8") + b"\n":
                raise RuntimeError(
                    "independent formal failure process bytes differ")
    if value.get("preserved_preflight_payloads") != observed_rows:
        raise RuntimeError("independent formal failure payload manifest differs")


def _validate_controller_envelope(
        controller: Mapping[str, Any], *, freeze_sha: str,
        authority_sha: str, runtime_sha: str,
        comparative_count: int, build_count: int,
        freeze: Mapping[str, Any], runtime: Mapping[str, Any] | None = None,
        raw_root: Path | None = None, root: Path | None = None,
        runtime_path: Path | None = None) -> None:
    required = {
        "schema", "status", "freeze_file_sha256",
        "execution_authority_sha256", "runtime_manifest_sha256",
        "worker_count", "comparative_worker_count",
        "build_cold_absolute_worker_count", "passed_worker_count",
        "failed_worker_count", "retry_count", "replacement_count",
        "comparative_rows", "build_cold_absolute_rows",
        "build_cold_enters_comparative_gate",
        "host_code_snapshot", "runtime_preflight",
        "preworker_combined_runtime_revalidation",
        "numba_llvmlite_runtime_authority",
        "post_execution_runtime_revalidation",
        "measurement_boundary_contract",
    }
    if set(controller) != required \
            or controller.get("schema") \
            != "rtdl.goal5802.formal_controller_result.v2" \
            or controller.get("freeze_file_sha256") != freeze_sha \
            or controller.get("execution_authority_sha256") != authority_sha \
            or controller.get("runtime_manifest_sha256") != runtime_sha \
            or controller.get("worker_count") != comparative_count + build_count \
            or controller.get("comparative_worker_count") != comparative_count \
            or controller.get("build_cold_absolute_worker_count") != build_count \
            or any(not _plain_int(controller.get(key)) or controller[key] != 0
                   for key in ("retry_count", "replacement_count")) \
            or controller.get("build_cold_enters_comparative_gate") is not False:
        raise RuntimeError("independent controller envelope differs")
    expected_measurement_boundary = {
        "DEPLOYMENT_COLD_primary_estimator": "WARM_PROCESS_DEPLOYMENT_COLD",
        "process_cold_claimed": False,
        "process_startup_and_admission_required_for_all_three_arms": True,
        "process_startup_and_admission_separately_published": True,
        "direct_pre_main_dso_loading": (
            "SEPARATE_PROCESS_STARTUP_AND_ADMISSION_PHASE__NOT_PRIMARY"),
        "python_interpreter_imports_and_selected_runtime_preload": (
            "SEPARATE_PROCESS_STARTUP_AND_ADMISSION_PHASE__NOT_PRIMARY"),
        "python_adapter_load_scope": (
            "DEPLOYED_BYTES_AND_PUBLIC_RUNTIME_DEPLOYMENT_LOAD_ONLY"),
        "python_primary_timer_new_module_load_policy": (
            "REJECT_ALL_NOT_PRELOADED"),
        "python_startup_flags_exact": ["-I", "-S", "-B", "-P", "-c"],
        "pth_execution_in_build_kat_preflight_or_formal": False,
    }
    if controller.get("measurement_boundary_contract") \
            != expected_measurement_boundary:
        raise RuntimeError("independent controller measurement boundary differs")
    _compiler_runtime_authority_independently(
        controller.get("numba_llvmlite_runtime_authority"), runtime=runtime)
    product = freeze.get("product_binding")
    pre_runtime = controller.get("preworker_combined_runtime_revalidation")
    post_runtime = controller.get("post_execution_runtime_revalidation")
    combined_receipt = (
        _validate_combined_runtime_independently(runtime)
        if isinstance(runtime, Mapping) else None)
    if combined_receipt is not None:
        combined_receipt_path = Path(str(
            runtime["files"]["combined_runtime_receipt"]["path"]))
        combined_receipt_sha = _sha(combined_receipt_path)
        combined_tree_sha = str(
            combined_receipt["venv_member_tree_sha256"])
    else:
        combined_receipt_sha = (
            str(pre_runtime.get("receipt_sha256"))
            if isinstance(pre_runtime, Mapping) else "")
        combined_tree_sha = (
            str(pre_runtime.get("venv_member_tree_sha256"))
            if isinstance(pre_runtime, Mapping) else "")
    if not _valid_sha256(combined_receipt_sha) \
            or not _valid_sha256(combined_tree_sha) \
            or pre_runtime != {
                "receipt_sha256": combined_receipt_sha,
                "venv_member_tree_sha256": combined_tree_sha,
            } \
            or not isinstance(product, Mapping) \
            or not isinstance(post_runtime, Mapping) \
            or post_runtime != {
                "status": (
                    "PASS__ALL_RUNTIME_PAYLOADS_REHASHED_AFTER_FINAL_WORKER"),
                "runtime_manifest_file_sha256": runtime_sha,
                "combined_runtime_receipt_sha256": combined_receipt_sha,
                "combined_runtime_full_venv_member_tree_sha256": (
                    combined_tree_sha),
                "rtdsl_package_file_count": product[
                    "rtdsl_package_file_count"],
                "rtdsl_package_tree_sha256": product[
                    "rtdsl_package_tree_sha256"],
            }:
        raise RuntimeError(
            "independent post-execution runtime revalidation differs")
    preflight = controller.get("runtime_preflight")
    preflight_unsigned = dict(preflight) if isinstance(preflight, Mapping) else {}
    preflight_seal = preflight_unsigned.pop("preflight_sha256", None)
    if not isinstance(preflight, Mapping) \
            or preflight.get("schema") \
            != "rtdl.goal5802.formal_runtime_preflight.v1" \
            or preflight.get("status") \
            != "PASS__LIVE_TARGET_AND_CROSS_ARM_NVRTC_BEFORE_WORKER_ZERO" \
            or preflight.get("runtime_manifest_file_sha256") != runtime_sha \
            or preflight_seal != _digest(preflight_unsigned):
        raise RuntimeError("independent controller preflight binding differs")
    snapshot = controller.get("host_code_snapshot")
    if not isinstance(snapshot, Mapping) or set(snapshot) != {
            "schema", "file_count", "payload_bytes", "rows_sha256",
            "pycache_file_count", "readonly"} \
            or snapshot.get("schema") != "rtdl.goal5802.host_code_snapshot.v1" \
            or snapshot.get("file_count", 0) <= 0 \
            or snapshot.get("payload_bytes", 0) <= 0 \
            or not _valid_sha256(snapshot.get("rows_sha256")) \
            or not _plain_int(snapshot.get("pycache_file_count")) \
            or snapshot["pycache_file_count"] != 0 \
            or snapshot.get("readonly") is not True:
        raise RuntimeError("independent host-code snapshot differs")
    snapshot_rows = [
        {"path": row["path"], "bytes": row["bytes"],
         "sha256": row["sha256"]}
        for row in freeze["source_manifest"]
        if str(row["path"]).endswith(".py") and (
            str(row["path"]).startswith("experiments/")
            or str(row["path"]).startswith("scripts/"))]
    if snapshot.get("file_count") != len(snapshot_rows) \
            or snapshot.get("payload_bytes") \
            != sum(int(row["bytes"]) for row in snapshot_rows) \
            or snapshot.get("rows_sha256") != _digest(snapshot_rows):
        raise RuntimeError("independent host-code snapshot identity differs")
    if raw_root is not None:
        snapshot_root = (
            raw_root.resolve(strict=True) / "host_code_snapshot").resolve(
                strict=True)
        actual_by_path: dict[str, dict[str, object]] = {}
        for path in sorted(snapshot_root.rglob("*")):
            if path.is_symlink() or (not path.is_file() and not path.is_dir()):
                raise RuntimeError(
                    "independent host-code snapshot has special path")
            if path.is_file():
                relative = path.relative_to(snapshot_root).as_posix()
                actual_by_path[relative] = {
                    "path": relative, "bytes": path.stat().st_size,
                    "sha256": _sha(path)}
        actual_rows = [actual_by_path.get(str(row["path"]))
                       for row in snapshot_rows]
        if set(actual_by_path) != {
                str(row["path"]) for row in snapshot_rows}:
            raise RuntimeError("independent host-code snapshot set differs")
        if actual_rows != snapshot_rows:
            raise RuntimeError("independent host-code snapshot bytes differ")
    context_values = (runtime, raw_root, root, runtime_path)
    if any(item is not None for item in context_values):
        if not all(item is not None for item in context_values):
            raise RuntimeError("independent formal preflight context incomplete")
        assert runtime is not None and raw_root is not None \
            and root is not None and runtime_path is not None
        _validate_formal_runtime_preflight_independently(
            preflight, runtime=runtime, runtime_sha=runtime_sha,
            runtime_path=runtime_path, freeze=freeze, raw_root=raw_root,
            root=root)
    rows = [*controller["comparative_rows"],
            *controller["build_cold_absolute_rows"]]
    passed = sum(item.get("status") == "PASS" for item in rows)
    failed = len(rows) - passed
    expected_status = (
        "COMPLETE" if failed == 0
        else "COMPLETE_WITH_FAILED_ROWS__NO_RETRY_OR_REPLACEMENT")
    if controller.get("passed_worker_count") != passed \
            or controller.get("failed_worker_count") != failed \
            or controller.get("status") != expected_status:
        raise RuntimeError("independent controller count/status differs")


def recount(
        freeze: Mapping[str, Any], controller: Mapping[str, Any], *,
        freeze_file_sha256: str | None = None,
        execution_authority_sha256: str | None = None,
        runtime_manifest_sha256: str | None = None,
        raw_root: Path | None = None,
        runtime: Mapping[str, Any] | None = None,
        root: Path | None = None, freeze_path: Path | None = None,
        authority_path: Path | None = None,
        runtime_path: Path | None = None) -> dict[str, Any]:
    comparative = controller.get("comparative_rows")
    build = controller.get("build_cold_absolute_rows")
    if not isinstance(comparative, list) or len(comparative) != 432 \
            or not isinstance(build, list) or len(build) != 72:
        raise RuntimeError("raw controller cardinality differs")
    expected_comp = freeze.get("schedule")
    expected_build = freeze.get("build_cold_absolute_schedule")
    if not isinstance(expected_comp, list) or not isinstance(expected_build, list) \
            or [item.get("schedule_row") for item in comparative] != expected_comp \
            or [item.get("schedule_row") for item in build] != expected_build:
        raise RuntimeError("raw receipt order differs from frozen rows")
    freeze_sha = freeze_file_sha256 or str(controller.get("freeze_file_sha256"))
    authority_sha = execution_authority_sha256 or str(
        controller.get("execution_authority_sha256"))
    runtime_sha = runtime_manifest_sha256 or str(
        controller.get("runtime_manifest_sha256"))
    _validate_freeze_bytes(
        freeze, freeze_file_sha256=freeze_sha, root=root)
    _validate_controller_envelope(
        controller, freeze_sha=freeze_sha, authority_sha=authority_sha,
        runtime_sha=runtime_sha, comparative_count=len(expected_comp),
        build_count=len(expected_build), freeze=freeze, runtime=runtime,
        raw_root=raw_root, root=root, runtime_path=runtime_path)

    comparative_values: dict[str, float] = {}
    comparative_errors: dict[str, str] = {}
    for item, row in zip(comparative, expected_comp, strict=True):
        try:
            _validate_indexed_receipt(item, row=row, kind="comparative")
            if item.get("status") != "PASS":
                raise RuntimeError("failed row has no accepted duration")
            if raw_root is not None:
                if runtime is None or root is None or freeze_path is None \
                        or authority_path is None or runtime_path is None:
                    raise RuntimeError("formal raw command context absent")
                _validate_raw_receipt(
                    item, row=row, raw_root=raw_root, kind="comparative",
                    expected_command=_expected_command(
                        row=row, kind="comparative", runtime=runtime,
                        root=root, freeze_path=freeze_path,
                        authority_path=authority_path, runtime_path=runtime_path,
                        raw_root=raw_root))
            comparative_values[row["worker_id"]] = _worker_value(
                item, row=row, freeze=freeze, freeze_sha=freeze_sha,
                authority_sha=authority_sha, runtime_sha=runtime_sha,
                runtime=runtime)
        except (KeyError, OSError, RuntimeError, TypeError, ValueError) as error:
            comparative_errors[row["worker_id"]] = str(error)
    build_values: dict[str, float] = {}
    build_errors: dict[str, str] = {}
    for item, row in zip(build, expected_build, strict=True):
        try:
            _validate_indexed_receipt(item, row=row, kind="build")
            if item.get("status") != "PASS":
                raise RuntimeError("failed build row")
            if raw_root is not None:
                if runtime is None or root is None or freeze_path is None \
                        or authority_path is None or runtime_path is None:
                    raise RuntimeError("formal raw command context absent")
                _validate_raw_receipt(
                    item, row=row, raw_root=raw_root, kind="build",
                    expected_command=_expected_command(
                        row=row, kind="build", runtime=runtime, root=root,
                        freeze_path=freeze_path, authority_path=authority_path,
                        runtime_path=runtime_path, raw_root=raw_root))
            build_values[row["worker_id"]] = _build_value(
                item, row=row, freeze_sha=freeze_sha,
                authority_sha=authority_sha, runtime_sha=runtime_sha,
                verify_output_files=raw_root is not None,
                freeze=freeze, runtime=runtime,
                compiler_runtime_authority=controller.get(
                    "numba_llvmlite_runtime_authority"))
        except (KeyError, OSError, RuntimeError, TypeError, ValueError) as error:
            build_errors[row["worker_id"]] = str(error)

    cells: dict[tuple[str, str, int, str], float] = {}
    for row in expected_comp:
        if row["worker_id"] in comparative_values:
            cells[(row["task"], row["regime"], int(row["block"]), row["arm"])] \
                = comparative_values[row["worker_id"]]
    comparative_absolute: list[dict[str, Any]] = []
    phase_attribution: list[dict[str, Any]] = []
    arm_medians: dict[tuple[str, str, str], float] = {}
    for task in TASKS:
        for regime in REGIMES:
            for arm in ARMS:
                rows = [row for row in expected_comp
                        if row["task"] == task and row["regime"] == regime
                        and row["arm"] == arm]
                values = [comparative_values[row["worker_id"]] for row in rows
                          if row["worker_id"] in comparative_values]
                failures = [row["worker_id"] for row in rows
                            if row["worker_id"] not in comparative_values]
                established = len(values) == 24 and not failures
                center = _median(values) if established else None
                if center is not None:
                    arm_medians[(task, regime, arm)] = center
                comparative_absolute.append({
                    "task": task, "regime": regime, "arm": arm,
                    "status": "ESTABLISHED" if established else "NOT_ESTABLISHED",
                    "successful_block_count": len(values),
                    "failure_worker_ids": failures,
                    "raw_block_duration_ns": values,
                    "median_ns": center, "unconditional_publication": True,
                })
                projections = [
                    _phase_projection(
                        comparative[expected_comp.index(row)], row)
                    for row in rows if row["worker_id"] in comparative_values]
                phase_attribution.append({
                    "task": task, "regime": regime, "arm": arm,
                    "status": "ESTABLISHED" if established else "NOT_ESTABLISHED",
                    "failure_worker_ids": failures,
                    "raw_rows": projections,
                    "minimum_directly_metered_worker_fraction": (
                        min(item["directly_metered_worker_fraction"]
                            for item in projections) if projections else None),
                    "prepare_subphases_separately_observable": False,
                    "subtraction_residual_is_causal_attribution": False,
                    "unconditional_publication": True,
                })

    ratios: list[dict[str, Any]] = []
    for task_index, task in enumerate(TASKS):
        for regime_index, regime in enumerate(REGIMES):
            for ratio_index, (name, numerator, denominator) in enumerate(RATIO_SPECS):
                paired: list[float] = []
                failed: list[str] = []
                for block_index in range(1, 25):
                    n_key = (task, regime, block_index, numerator)
                    d_key = (task, regime, block_index, denominator)
                    if n_key not in cells or d_key not in cells:
                        failed.extend([
                            row["worker_id"] for row in expected_comp
                            if row["task"] == task and row["regime"] == regime
                            and int(row["block"]) == block_index
                            and row["arm"] in {numerator, denominator}
                            and row["worker_id"] not in comparative_values])
                    else:
                        paired.append(cells[n_key] / cells[d_key])
                established = len(paired) == 24 and not failed
                point = lower = upper = None
                if established:
                    point = _median(paired)
                    generator = random.Random(
                        58_020_000 + 1000 * task_index
                        + 100 * regime_index + ratio_index)
                    draws = [_median(generator.choices(paired, k=24))
                             for _ in range(10_000)]
                    draws.sort()
                    lower, upper = draws[249], draws[9749]
                gate = name == "RTDL_OVER_PYOPTIX"
                threshold = THRESHOLDS[regime] if gate else None
                ratios.append({
                    "task": task, "regime": regime, "ratio": name,
                    "status": "ESTABLISHED" if established else "NOT_ESTABLISHED",
                    "failure_worker_ids": sorted(set(failed)),
                    "paired_block_ratios": paired, "median": point,
                    "ci95_lower": lower, "ci95_upper": upper,
                    "comparative_gate": gate, "threshold": threshold,
                    "passes": upper <= threshold if established and gate else None,
                })

    build_rows: list[dict[str, Any]] = []
    build_medians: dict[tuple[str, str], float] = {}
    for task in TASKS:
        for arm in ARMS:
            rows = [row for row in expected_build
                    if row["task"] == task and row["arm"] == arm]
            values = [build_values[row["worker_id"]] for row in rows
                      if row["worker_id"] in build_values]
            failures = [row["worker_id"] for row in rows
                        if row["worker_id"] not in build_values]
            established = len(values) == 12 and not failures
            center = _median(values) if established else None
            if center is not None:
                build_medians[(task, arm)] = center
            build_rows.append({
                "task": task, "arm": arm,
                "status": "ESTABLISHED" if established else "NOT_ESTABLISHED",
                "successful_build_count": len(values),
                "failure_worker_ids": failures,
                "raw_duration_ns": values, "median_ns": center,
                "minimum_ns": min(values) if values else None,
                "maximum_ns": max(values) if values else None,
                "comparative_gate": False,
                "build_boundary": "PRE_SIGNING_PRE_DEPLOYMENT_BUILD_PRODUCT",
                "unconditional_publication": True,
            })

    amortization = []
    for task in TASKS:
        dependencies = [
            (task, RTDL), (task, "DEPLOYMENT_COLD", RTDL),
            (task, "DEPLOYMENT_COLD", PYOPTIX),
            (task, "STEADY_E2E", RTDL),
            (task, "STEADY_E2E", PYOPTIX),
        ]
        established = dependencies[0] in build_medians \
            and all(key in arm_medians for key in dependencies[1:])
        b_r = build_medians.get((task, RTDL))
        b_p = build_medians.get((task, PYOPTIX))
        d_r = arm_medians.get((task, "DEPLOYMENT_COLD", RTDL))
        d_p = arm_medians.get((task, "DEPLOYMENT_COLD", PYOPTIX))
        s_r = arm_medians.get((task, "STEADY_E2E", RTDL))
        s_p = arm_medians.get((task, "STEADY_E2E", PYOPTIX))
        crossing: int | str | None = None
        if established:
            assert None not in (b_r, d_r, d_p, s_r, s_p)
            crossing = "NEVER" if s_p <= s_r else int(math.ceil(
                max(0.0, b_r + d_r - d_p) / (s_p - s_r)))
        amortization.append({
            "task": task,
            "status": "ESTABLISHED" if established else "NOT_ESTABLISHED",
            "B_RTDL_ns": b_r, "B_PYOPTIX_diagnostic_ns": b_p,
            "B_PYOPTIX_excluded_from_registered_equation": True,
            "D_RTDL_ns": d_r, "D_PYOPTIX_ns": d_p,
            "S_RTDL_ns": s_r, "S_PYOPTIX_ns": s_p,
            "break_even_N": crossing,
            "registered_equation": (
                "B_RTDL + D_RTDL + N*S_RTDL <= "
                "D_PYOPTIX + N*S_PYOPTIX"),
            "scenario_assumption": (
                "one RTDL pre-signing build, one deployment, then N steady "
                "executions; PyOptiX BUILD_COLD is published but excluded by "
                "the exact Goal5799 registered equation"),
        })

    primary = [row for row in ratios if row["comparative_gate"]]
    comparative_failures = list(comparative_errors)
    build_failures = list(build_errors)
    return {
        "status": (
            "COMPLETE" if not comparative_failures and not build_failures
            else "COMPLETE_WITH_FAILED_ROWS__OBJECTIVES_NOT_ESTABLISHED"),
        "comparative_failure_worker_ids": comparative_failures,
        "build_cold_failure_worker_ids": build_failures,
        "comparative_validation_failures": [
            {"worker_id": key, "reason": value}
            for key, value in comparative_errors.items()],
        "build_cold_validation_failures": [
            {"worker_id": key, "reason": value}
            for key, value in build_errors.items()],
        "comparative_absolute": comparative_absolute,
        "phase_attribution": phase_attribution,
        "comparative_ratios": ratios,
        "build_cold_absolute": build_rows,
        "build_cold_enters_comparative_gate": False,
        "amortization": amortization,
        "all_primary_noninferiority_gates_pass": (
            len(primary) == len(TASKS) * len(REGIMES)
            and all(row["status"] == "ESTABLISHED" and row["passes"] is True
                    for row in primary)),
        "retry_count": 0, "replacement_count": 0,
    }


def _validate_execution_authority_bytes(
        authority: Mapping[str, Any], *, freeze_sha: str,
        runtime_sha: str) -> None:
    external_schema = "rtdl.goal5802.formal_execution_authority.v1"
    owner_waiver_schema = (
        "rtdl.goal5802.owner_waiver_formal_execution_authority.v1")
    owner_waiver_reason = (
        "OWNER_DIRECTED_EXECUTION_WITHOUT_EXTERNAL_PREEXECUTION_REVIEW__"
        "MUST_DISCLOSE_AND_MUST_NOT_RELABEL")
    schema = authority.get("schema")
    common = {
        "schema", "freeze_file_sha256", "runtime_manifest_file_sha256",
        "owner_execution_authorized", "formal_worker_zero_authorized",
        "pod_gpu_timing_authorized", "execution_authority_sha256",
    }
    if schema == external_schema:
        required = common | {
            "external_cfr_sha256", "external_review_p0",
            "external_review_p1", "external_exact_byte_approval",
        }
    elif schema == owner_waiver_schema:
        required = common | {
            "preexecution_cfr_sha256",
            "external_preexecution_review_claimed",
            "external_exact_byte_approval",
            "owner_explicit_external_review_waiver",
            "owner_waiver_reason",
        }
    else:
        raise RuntimeError("independent execution authority schema differs")
    unsigned = dict(authority)
    observed = unsigned.pop("execution_authority_sha256", None)
    if set(authority) != required or observed != _digest(unsigned) \
            or authority.get("freeze_file_sha256") != freeze_sha \
            or authority.get("runtime_manifest_file_sha256") != runtime_sha \
            or authority.get("owner_execution_authorized") is not True \
            or authority.get("formal_worker_zero_authorized") is not True \
            or authority.get("pod_gpu_timing_authorized") is not True:
        raise RuntimeError("independent execution authority differs")
    if schema == external_schema:
        valid_branch = (
            authority.get("external_review_p0") == 0
            and authority.get("external_review_p1") == 0
            and authority.get("external_exact_byte_approval") is True)
        document_key = "external_cfr_sha256"
    else:
        valid_branch = (
            authority.get("external_preexecution_review_claimed") is False
            and authority.get("external_exact_byte_approval") is False
            and authority.get("owner_explicit_external_review_waiver") is True
            and authority.get("owner_waiver_reason") == owner_waiver_reason)
        document_key = "preexecution_cfr_sha256"
    document_sha = authority.get(document_key)
    if not valid_branch or not isinstance(document_sha, str) \
            or len(document_sha) != 64 \
            or any(ch not in "0123456789abcdef" for ch in document_sha):
        raise RuntimeError("independent execution authority branch differs")


def _validate_pyoptix_header_lineage_independently(
        headers: Mapping[str, Any], *, directories: Mapping[str, Any],
        header_projection: Mapping[str, Any]) -> None:
    """Bind the wheel's original SDK headers to the projected runtime tree.

    The PyOptiX extension is built against the original OptiX SDK.  Formal
    Goal5802 compilation deliberately consumes a disjoint, load-bearing
    projection of that SDK.  Those paths must therefore differ; the projection
    authority, rather than path equality, is the chain joining them.
    """
    sdk_record = directories.get("optix_sdk")
    projected_record = directories.get("optix_include")
    authority = header_projection.get("command_authority")
    mappings = header_projection.get("root_mappings")
    if not isinstance(sdk_record, Mapping) \
            or not isinstance(projected_record, Mapping) \
            or not isinstance(authority, Mapping) \
            or not isinstance(mappings, list):
        raise RuntimeError("independent PyOptiX header lineage malformed")
    roots = authority.get("original_sdk_roots")
    if not isinstance(roots, Mapping) \
            or not isinstance(roots.get("optix_include"), Mapping):
        raise RuntimeError("independent PyOptiX original header root absent")
    matching = [row for row in mappings
                if isinstance(row, Mapping)
                and row.get("role") == "optix_include"]
    if len(matching) != 1:
        raise RuntimeError("independent PyOptiX projected header root absent")
    mapping = matching[0]

    sdk_root = Path(str(headers.get("root"))).resolve(strict=True)
    manifest_sdk_root = Path(str(sdk_record.get("path"))).resolve(strict=True)
    original_include = Path(str(
        roots["optix_include"].get("resolved_path"))).resolve(strict=True)
    projected_include = Path(str(mapping.get(
        "projected_root"))).resolve(strict=True)
    manifest_projected_include = Path(str(
        projected_record.get("path"))).resolve(strict=True)
    if headers.get("commit") != OPTIX_HEADERS_COMMIT \
            or headers.get("tree") != OPTIX_HEADERS_TREE \
            or sdk_root != manifest_sdk_root \
            or (sdk_root / "include").resolve(strict=True) != original_include \
            or mapping.get("original_root") != str(original_include) \
            or projected_include != manifest_projected_include \
            or mapping.get("roots_distinct_and_nonoverlapping") is not True \
            or original_include == projected_include \
            or original_include.is_relative_to(projected_include) \
            or projected_include.is_relative_to(original_include):
        raise RuntimeError("independent PyOptiX header lineage differs")


def _validate_pyoptix_clean_install_copies_independently(
        clean_install: Mapping[str, Any],
        files: Mapping[str, Mapping[str, Any]]) -> None:
    """Rehash the historical install and bind content to the active venv.

    Goal5800 and Goal5802 use separate clean environments.  Their absolute
    paths are intentionally different; the portable invariant is exact file
    content, independently rehashed at both locations.
    """
    rows = (
        ("wheel", "pyoptix_wheel", {"path", "bytes", "sha256"}),
        ("loaded_optix_extension", "pyoptix_extension",
         {"module", "path", "bytes", "sha256"}),
        ("loaded_optix_package_initializer", "pyoptix_initializer",
         {"path", "bytes", "sha256"}),
    )
    for receipt_role, runtime_role, expected_fields in rows:
        record = clean_install.get(receipt_role)
        current = files.get(runtime_role)
        if not isinstance(record, Mapping) \
                or not isinstance(current, Mapping) \
                or set(record) != expected_fields:
            raise RuntimeError(
                f"independent PyOptiX clean-install row malformed: {receipt_role}")
        path = Path(str(record.get("path")))
        if not path.is_absolute() or not path.is_file() or path.is_symlink() \
                or path.stat().st_size != record.get("bytes") \
                or _sha(path) != record.get("sha256") \
                or record.get("bytes") != current.get("bytes") \
                or record.get("sha256") != current.get("sha256"):
            raise RuntimeError(
                f"independent PyOptiX clean-install copy differs: {receipt_role}")
    if clean_install["loaded_optix_extension"].get("module") != "optix._optix":
        raise RuntimeError("independent PyOptiX clean-install module differs")


def _validate_pyoptix_wheel_build_copy_independently(
        receipt_path: Path, wheel: Mapping[str, Any],
        build: Mapping[str, Any],
        files: Mapping[str, Mapping[str, Any]]) -> None:
    expected_fields = {
        "path", "bytes", "sha256", "extension_member",
        "extension_bytes", "extension_sha256",
    }
    current = files.get("pyoptix_wheel")
    if set(wheel) != expected_fields or not isinstance(current, Mapping) \
            or not _plain_int(build.get("exit_code")) \
            or build["exit_code"] != 0:
        raise RuntimeError("independent PyOptiX wheel-build row malformed")
    source = (receipt_path.resolve(strict=True).parent /
              str(wheel.get("path"))).resolve(strict=True)
    if not source.is_file() \
            or source.stat().st_size != wheel.get("bytes") \
            or _sha(source) != wheel.get("sha256") \
            or wheel.get("bytes") != current.get("bytes") \
            or wheel.get("sha256") != current.get("sha256"):
        raise RuntimeError("independent PyOptiX wheel-build copy differs")


def _exact_scalar_mapping(
        value: object, expected: Mapping[str, object], label: str) \
        -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != set(expected) \
            or any(type(value.get(key)) is not type(wanted)
                   or value[key] != wanted for key, wanted in expected.items()):
        raise RuntimeError(f"independent {label} differs")
    return value


def _validate_materialization_file_record_independently(
        value: object, label: str, *, executable: bool = False) -> Path:
    if not isinstance(value, Mapping):
        raise RuntimeError(f"independent {label} record is absent")
    kind = value.get("path_kind")
    expected = ({"invocation_path", "resolved_path", "path_kind", "bytes",
                 "sha256"}
                if kind == "REGULAR_FILE" else
                {"invocation_path", "resolved_path", "path_kind",
                 "symlink_target", "bytes", "sha256"})
    if set(value) != expected:
        raise RuntimeError(f"independent {label} record envelope differs")
    invocation = Path(str(value.get("invocation_path")))
    if not invocation.is_absolute():
        raise RuntimeError(f"independent {label} invocation path differs")
    if kind == "REGULAR_FILE":
        if invocation.is_symlink() or not invocation.is_file():
            raise RuntimeError(f"independent {label} is absent or symbolic")
        resolved = invocation.resolve(strict=True)
    elif kind == "SYMLINK_TO_REGULAR_FILE":
        if not invocation.is_symlink() \
                or str(invocation.readlink()) != value.get("symlink_target"):
            raise RuntimeError(f"independent {label} symlink differs")
        resolved = invocation.resolve(strict=True)
        if not resolved.is_file():
            raise RuntimeError(f"independent {label} target differs")
    else:
        raise RuntimeError(f"independent {label} path kind differs")
    if str(resolved) != value.get("resolved_path") \
            or type(value.get("bytes")) is not int \
            or value["bytes"] < 0 \
            or resolved.stat().st_size != value["bytes"] \
            or not _valid_sha256(value.get("sha256")) \
            or _sha(resolved) != value["sha256"] \
            or (executable and not os.access(resolved, os.X_OK)):
        raise RuntimeError(f"independent {label} identity differs")
    return resolved


def _materialized_header_identity_independently(
        checkout: Path) -> dict[str, object]:
    """Rebuild Git blob/tree identities without trusting the recorded Git."""

    checkout = checkout.resolve(strict=True)
    git_dir = checkout / ".git"
    if git_dir.is_symlink() or not git_dir.is_dir():
        raise RuntimeError("independent materialized header Git dir differs")
    try:
        commit = (git_dir / "HEAD").read_text(encoding="ascii").strip()
        config_text = (git_dir / "config").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise RuntimeError(
            "independent materialized header Git metadata differs") from error
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise RuntimeError("independent materialized header HEAD is not detached")
    match = re.search(
        r"(?im)^\s*autocrlf\s*=\s*([^\s#;]+)\s*$", config_text)
    autocrlf = match.group(1).lower() if match else ""

    def object_digest(kind: bytes, payload: bytes) -> bytes:
        header = kind + b" " + str(len(payload)).encode("ascii") + b"\0"
        return hashlib.sha1(
            header + payload, usedforsecurity=False).digest()

    def tree_digest(root: Path) -> bytes:
        entries: list[tuple[bytes, bytes]] = []
        children = [path for path in root.iterdir() if path.name != ".git"]
        for path in sorted(
                children,
                key=lambda item: os.fsencode(item.name)
                + (b"/" if item.is_dir() else b"")):
            if path.is_symlink():
                raise RuntimeError(
                    "independent materialized header tree has symlink")
            name = os.fsencode(path.name)
            if path.is_dir():
                mode = b"40000"
                digest_bytes = tree_digest(path)
            elif path.is_file():
                executable = os.name == "posix" \
                    and bool(path.stat().st_mode & stat.S_IXUSR)
                mode = b"100755" if executable else b"100644"
                digest_bytes = object_digest(b"blob", path.read_bytes())
            else:
                raise RuntimeError(
                    "independent materialized header tree has special member")
            entries.append((name, mode + b" " + name + b"\0" + digest_bytes))
        return object_digest(b"tree", b"".join(row for _, row in entries))

    tree = tree_digest(checkout).hex()
    rows: list[dict[str, object]] = []
    observed_paths: set[str] = set()
    payload_bytes = 0
    paths = [
        path for path in checkout.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(checkout).parts
    ]
    for path in sorted(paths, key=lambda item: item.relative_to(
            checkout).as_posix()):
        relative_text = path.relative_to(checkout).as_posix()
        if path.is_symlink() or relative_text in observed_paths:
            raise RuntimeError("independent materialized header payload differs")
        payload = path.read_bytes()
        executable = os.name == "posix" \
            and bool(path.stat().st_mode & stat.S_IXUSR)
        mode = "100755" if executable else "100644"
        blob = object_digest(b"blob", payload).hex()
        observed_paths.add(relative_text)
        payload_bytes += len(payload)
        rows.append({
            "path": relative_text, "mode": mode, "blob_sha1": blob,
            "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
        })
    worktree_paths = {
        path.relative_to(checkout).as_posix()
        for path in checkout.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(checkout).parts
    }
    if observed_paths != worktree_paths:
        raise RuntimeError("independent materialized header checkout differs")
    return {
        "path": str(checkout.resolve(strict=True)),
        "commit": commit, "tree": tree, "core_autocrlf": autocrlf,
        "file_count": len(rows), "payload_bytes": payload_bytes,
        "inventory_sha256": _digest(rows),
    }


def _validate_current_pyoptix_materialization_envelope_independently(
        value: Mapping[str, Any]) -> Mapping[str, Any]:
    required = {
        "schema", "status", "original_build_receipt", "headers_bundle",
        "git_tool", "frozen_historical_receipt_authority",
        "historical_build_projection", "materialized_headers",
        "pyoptix_wheel", "claim_boundaries", "formal_worker_count",
        "registered_performance_timing_count", "gpu_kernel_launch_count",
        "clock_read_count", "receipt_sha256",
    }
    body = dict(value)
    seal = body.pop("receipt_sha256", None)
    if set(value) != required \
            or value.get("schema") \
            != "rtdl.goal5802.pyoptix_wheel_build_materialization_receipt.v1" \
            or value.get("status") \
            != "PASS__HISTORICAL_BUILD_PRESERVED__EXACT_HEADERS_MATERIALIZED" \
            or seal != _digest(body):
        raise RuntimeError(
            "independent PyOptiX materialization receipt differs")
    zero_lock = {
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
        "clock_read_count": 0,
    }
    _exact_scalar_mapping(
        {key: value.get(key) for key in zero_lock}, zero_lock,
        "PyOptiX materialization zero lock")
    _exact_scalar_mapping(value.get("claim_boundaries"), {
        "historical_build_path_rewritten": False,
        "historical_build_reexecuted": False,
        "target_header_materialization_is_not_a_rebuild": True,
        "network_access_required_on_target": False,
        "performance_claim_authorized": False,
        "execution_authority_consumed": False,
    }, "PyOptiX materialization claim boundary")
    _exact_scalar_mapping(value.get("frozen_historical_receipt_authority"), {
        "bytes": PYOPTIX_HISTORICAL_BUILD_RECEIPT_BYTES,
        "sha256": PYOPTIX_HISTORICAL_BUILD_RECEIPT_SHA256,
        "source_projection_file_count": PYOPTIX_HISTORICAL_SOURCE_FILE_COUNT,
        "source_projection_sha256": PYOPTIX_HISTORICAL_SOURCE_SHA256,
        "historical_headers_root": PYOPTIX_HISTORICAL_HEADERS_ROOT,
    }, "frozen historical PyOptiX receipt authority")
    return value


def _validate_current_pyoptix_materialization_independently(
        receipt_path: Path, *, files: Mapping[str, Mapping[str, Any]],
        directories: Mapping[str, Any],
        header_projection: Mapping[str, Any]) -> Mapping[str, Any]:
    value = _load_exact_canonical_json(
        receipt_path, "PyOptiX provenance materialization receipt")
    _validate_current_pyoptix_materialization_envelope_independently(value)
    original_path = _validate_materialization_file_record_independently(
        value.get("original_build_receipt"), "historical build receipt")
    _validate_materialization_file_record_independently(
        value.get("headers_bundle"), "OptiX headers bundle")
    _validate_materialization_file_record_independently(
        value.get("git_tool"), "Git tool", executable=True)
    active_wheel = _validate_materialization_file_record_independently(
        value.get("pyoptix_wheel"), "PyOptiX wheel")
    runtime_wheel = files.get("pyoptix_wheel")
    if not isinstance(runtime_wheel, Mapping) \
            or original_path.stat().st_size \
            != PYOPTIX_HISTORICAL_BUILD_RECEIPT_BYTES \
            or _sha(original_path) != PYOPTIX_HISTORICAL_BUILD_RECEIPT_SHA256 \
            or active_wheel.stat().st_size != PYOPTIX_WHEEL_BYTES \
            or _sha(active_wheel) != PYOPTIX_WHEEL_SHA256 \
            or runtime_wheel.get("bytes") != PYOPTIX_WHEEL_BYTES \
            or runtime_wheel.get("sha256") != PYOPTIX_WHEEL_SHA256:
        raise RuntimeError(
            "independent PyOptiX materialization input identity differs")
    historical = _load(original_path)
    wheel = historical.get("wheel")
    source = historical.get("pyoptix_source")
    headers = historical.get("optix_headers")
    build = historical.get("build")
    rows = source.get("archive_projection_files") \
        if isinstance(source, Mapping) else None
    if set(historical) != {
            "schema", "status", "transaction_kind", "pyoptix_source",
            "optix_headers", "build", "wheel",
            "registered_performance_timing_count"} \
            or historical.get("schema") \
            != "rtdl.goal5800.pyoptix_clean_wheel_build_receipt.v1" \
            or historical.get("status") \
            != "PASS__CLEAN_SOURCE_TO_WHEEL_BUILD__UNTIMED" \
            or historical.get("transaction_kind") \
            != "build_provenance_not_performance" \
            or type(historical.get("registered_performance_timing_count")) \
            is not int \
            or historical["registered_performance_timing_count"] != 0 \
            or not all(isinstance(item, Mapping)
                       for item in (wheel, source, headers, build)) \
            or source.get("commit") != PYOPTIX_COMMIT \
            or source.get("tree") != PYOPTIX_TREE \
            or source.get("archive_projection_file_count") \
            != PYOPTIX_HISTORICAL_SOURCE_FILE_COUNT \
            or not isinstance(rows, list) \
            or len(rows) != PYOPTIX_HISTORICAL_SOURCE_FILE_COUNT \
            or _digest(rows) != PYOPTIX_HISTORICAL_SOURCE_SHA256 \
            or headers.get("commit") != OPTIX_HEADERS_COMMIT \
            or headers.get("tree") != OPTIX_HEADERS_TREE \
            or headers.get("root") != PYOPTIX_HISTORICAL_HEADERS_ROOT \
            or type(headers.get("api_macro")) is not int \
            or headers["api_macro"] != 90000:
        raise RuntimeError(
            "independent historical PyOptiX build receipt differs")
    if set(wheel) != {
            "path", "bytes", "sha256", "extension_member",
            "extension_bytes", "extension_sha256"} \
            or PurePosixPath(str(wheel.get("path"))).is_absolute() \
            or ".." in PurePosixPath(str(wheel.get("path"))).parts \
            or type(build.get("exit_code")) is not int \
            or build["exit_code"] != 0 \
            or type(wheel.get("bytes")) is not int \
            or wheel["bytes"] != PYOPTIX_WHEEL_BYTES \
            or wheel.get("sha256") != PYOPTIX_WHEEL_SHA256 \
            or wheel.get("extension_member") != PYOPTIX_EXTENSION_MEMBER \
            or type(wheel.get("extension_bytes")) is not int \
            or wheel["extension_bytes"] != PYOPTIX_EXTENSION_BYTES \
            or wheel.get("extension_sha256") != PYOPTIX_EXTENSION_SHA256:
        raise RuntimeError(
            "independent historical PyOptiX wheel projection differs")
    projection = value.get("historical_build_projection")
    _exact_scalar_mapping(projection, {
        "historical_optix_headers_root": PYOPTIX_HISTORICAL_HEADERS_ROOT,
        "source_projection_sha256": PYOPTIX_HISTORICAL_SOURCE_SHA256,
        "source_projection_file_count": PYOPTIX_HISTORICAL_SOURCE_FILE_COUNT,
        "frozen_historical_receipt_sha256": (
            PYOPTIX_HISTORICAL_BUILD_RECEIPT_SHA256),
        "frozen_historical_receipt_bytes": (
            PYOPTIX_HISTORICAL_BUILD_RECEIPT_BYTES),
    }, "historical PyOptiX build projection")
    materialized = value.get("materialized_headers")
    if not isinstance(materialized, Mapping) \
            or set(materialized) != {
                "path", "commit", "tree", "core_autocrlf", "file_count",
                "payload_bytes", "inventory_sha256"}:
        raise RuntimeError(
            "independent materialized PyOptiX headers projection differs")
    checkout = Path(str(materialized.get("path")))
    observed_headers = _materialized_header_identity_independently(checkout)
    if observed_headers != materialized:
        raise RuntimeError(
            "independent materialized PyOptiX headers identity differs")
    _validate_pyoptix_header_lineage_independently(
        {"root": str(checkout), "commit": materialized["commit"],
         "tree": materialized["tree"]},
        directories=directories, header_projection=header_projection)
    return historical


def _relative_file_record_independently(
        root: Path, value: object, label: str) -> Path:
    if not isinstance(value, Mapping) \
            or set(value) != {"path", "bytes", "sha256"} \
            or type(value.get("bytes")) is not int or value["bytes"] < 0 \
            or not _valid_sha256(value.get("sha256")):
        raise RuntimeError(f"independent {label} record differs")
    relative = PurePosixPath(str(value.get("path")))
    if relative.is_absolute() or ".." in relative.parts \
            or relative.as_posix() != value.get("path"):
        raise RuntimeError(f"independent {label} path differs")
    path = root / Path(*relative.parts)
    if path.is_symlink() or not path.is_file() \
            or path.stat().st_size != value["bytes"] \
            or _sha(path) != value["sha256"]:
        raise RuntimeError(f"independent {label} identity differs")
    return path


def _validate_current_offline_pyoptix_envelope_independently(
        receipt: Mapping[str, Any]) -> Mapping[str, Any]:
    required = {
        "schema", "status", "plan_sha256", "specialization_sha256",
        "plan_file_sha256", "wheelhouse_manifest_sha256",
        "wheel_set_sha256", "required_distributions",
        "generic_combined_runtime_receipt",
        "generic_combined_runtime_receipt_sha256",
        "installed_package_snapshot", "installed_package_snapshot_sha256",
        "generic_input_tree_sha256", "generic_commands_sha256",
        "generic_venv_member_count", "generic_venv_member_tree_sha256",
        "generic_base_python_site_boundary", "install_command",
        "provenance_files", "provenance_tree_sha256", "pip_policy",
        "validation_boundary", "create_only", "receipt_sha256",
    }
    body = dict(receipt)
    seal = body.pop("receipt_sha256", None)
    if set(receipt) != required \
            or receipt.get("schema") \
            != "rtdl.goal5802.offline_pyoptix_clean_install_receipt.v1" \
            or receipt.get("status") \
            != "PASS__OFFLINE_CREATE_ONLY_PYOPTIX_RUNTIME_INSTALLED" \
            or seal != _digest(body) \
            or receipt.get("create_only") is not True \
            or receipt.get("required_distributions") \
            != PYOPTIX_REQUIRED_DISTRIBUTIONS:
        raise RuntimeError(
            "independent offline PyOptiX receipt envelope differs")
    _exact_scalar_mapping(
        receipt.get("validation_boundary"),
        OFFLINE_PYOPTIX_VALIDATION_BOUNDARY,
        "offline PyOptiX no-execution boundary")
    _exact_scalar_mapping(
        receipt.get("pip_policy"), OFFLINE_PYOPTIX_PIP_POLICY,
        "offline PyOptiX pip policy")
    return receipt


def _validate_current_offline_pyoptix_install_independently(
        receipt_path: Path) -> Mapping[str, Any]:
    root = receipt_path.parent.resolve(strict=True)
    if receipt_path.name != "offline_pyoptix_clean_install_receipt.json" \
            or receipt_path.is_symlink() or root.is_symlink() \
            or not root.is_dir() \
            or (root / "offline_pyoptix_terminal_failure_receipt.json").exists() \
            or (root / "terminal_failure_receipt.json").exists():
        raise RuntimeError("independent offline PyOptiX root differs")
    receipt = _load_exact_canonical_json(
        receipt_path, "offline PyOptiX clean-install receipt")
    _validate_current_offline_pyoptix_envelope_independently(receipt)
    generic_runtime = _validate_combined_runtime_root_independently(root)
    plan_path = root / "plan.json"
    plan = _load_exact_canonical_json(plan_path, "offline PyOptiX plan")
    plan_body = dict(plan)
    plan_seal = plan_body.pop("plan_sha256", None)
    commands = plan.get("commands")
    specialization = plan.get("offline_pyoptix_specialization")
    specialization_body = dict(specialization) \
        if isinstance(specialization, Mapping) else {}
    specialization_seal = specialization_body.pop(
        "specialization_sha256", None)
    install = (commands[1].get("argv")
               if isinstance(commands, list) and len(commands) == 4
               and isinstance(commands[1], Mapping) else None)
    required_flags = (
        "--no-index", "--no-deps", "--no-cache-dir", "--no-compile",
        "--disable-pip-version-check", "--target",
    )
    if plan_seal != _digest(plan_body) \
            or receipt.get("plan_sha256") != plan_seal \
            or receipt.get("plan_file_sha256") != _sha(plan_path) \
            or plan.get("output_directory") != str(root) \
            or not isinstance(specialization, Mapping) \
            or specialization.get("schema") \
            != "rtdl.goal5802.offline_pyoptix_clean_install_specialization.v1" \
            or specialization.get("status") \
            != "PLANNED_EXACT_OFFLINE_PYOPTIX_CLEAN_INSTALL_PROFILE" \
            or specialization.get("profile") \
            != "GOAL5802_PYOPTIX_AND_RTDL_SHARED_RUNTIME_V1" \
            or specialization.get("required_distributions") \
            != PYOPTIX_REQUIRED_DISTRIBUTIONS \
            or type(specialization.get("wheel_count")) is not int \
            or specialization["wheel_count"] != 8 \
            or specialization_seal != _digest(specialization_body) \
            or receipt.get("specialization_sha256") \
            != specialization_seal \
            or not isinstance(specialization.get("pip_policy"), Mapping) \
            or not isinstance(
                specialization.get("validation_boundary"), Mapping) \
            or not isinstance(install, list) \
            or receipt.get("install_command") != install \
            or any(install.count(flag) != 1 for flag in required_flags) \
            or "--prefix" in install:
        raise RuntimeError("independent offline PyOptiX plan differs")
    _exact_scalar_mapping(
        specialization["pip_policy"], OFFLINE_PYOPTIX_PIP_POLICY,
        "offline PyOptiX planned pip policy")
    _exact_scalar_mapping(
        specialization["validation_boundary"],
        OFFLINE_PYOPTIX_VALIDATION_BOUNDARY,
        "offline PyOptiX planned no-execution boundary")
    generic_path = _relative_file_record_independently(
        root, receipt.get("generic_combined_runtime_receipt"),
        "offline PyOptiX generic receipt")
    snapshot_path = _relative_file_record_independently(
        root, receipt.get("installed_package_snapshot"),
        "offline PyOptiX installed snapshot")
    if generic_path.name != "combined_runtime_receipt.json" \
            or snapshot_path.name != "installed_packages.json" \
            or receipt.get("generic_combined_runtime_receipt_sha256") \
            != generic_runtime.get("receipt_sha256") \
            or receipt.get("installed_package_snapshot_sha256") \
            != generic_runtime.get("installed_package_snapshot_sha256") \
            or receipt.get("generic_input_tree_sha256") \
            != generic_runtime.get("input_tree_sha256") \
            or receipt.get("generic_commands_sha256") \
            != generic_runtime.get("commands_sha256") \
            or receipt.get("generic_venv_member_count") \
            != generic_runtime.get("venv_member_count") \
            or receipt.get("generic_venv_member_tree_sha256") \
            != generic_runtime.get("venv_member_tree_sha256") \
            or receipt.get("generic_base_python_site_boundary") \
            != generic_runtime.get("base_python_site_boundary"):
        raise RuntimeError(
            "independent offline PyOptiX generic-runtime projection differs")
    rows = receipt.get("provenance_files")
    if not isinstance(rows, list) or len(rows) != 4 \
            or rows != sorted(rows, key=lambda row: str(row.get("path"))
                              if isinstance(row, Mapping) else ""):
        raise RuntimeError(
            "independent offline PyOptiX provenance rows differ")
    paths = [
        _relative_file_record_independently(
            root, row, "offline PyOptiX provenance") for row in rows]
    if receipt.get("provenance_tree_sha256") != _digest(rows) \
            or {path.name for path in paths} != {
                "wheelhouse_manifest.json",
                "goal5802_clean_install_pyoptix_offline.py",
                "goal5802_build_offline_python_wheelhouse.py",
                "goal5802_build_combined_runtime_untimed.py",
            }:
        raise RuntimeError(
            "independent offline PyOptiX provenance tree differs")
    copied_manifest_path = next(
        path for path in paths if path.name == "wheelhouse_manifest.json")
    wheelhouse_manifest = _load_exact_canonical_json(
        copied_manifest_path, "offline PyOptiX wheelhouse manifest")
    wheelhouse_body = dict(wheelhouse_manifest)
    wheelhouse_seal = wheelhouse_body.pop("manifest_sha256", None)
    wheels = wheelhouse_manifest.get("wheels")
    observed_versions = {
        str(row.get("distribution")): str(row.get("version"))
        for row in wheels if isinstance(row, Mapping)
    } if isinstance(wheels, list) else {}
    if wheelhouse_seal != _digest(wheelhouse_body) \
            or wheelhouse_manifest.get("schema") \
            != "rtdl.goal5802.offline_python_wheelhouse_manifest.v1" \
            or wheelhouse_manifest.get("status") \
            != "PASS__EXACT_PINNED_WHEELS_COLLECTED__NO_DOWNLOAD" \
            or wheelhouse_manifest.get("profile") \
            != "GOAL5802_PYOPTIX_AND_RTDL_SHARED_RUNTIME_V1" \
            or wheelhouse_manifest.get("required_distributions") \
            != PYOPTIX_REQUIRED_DISTRIBUTIONS \
            or type(wheelhouse_manifest.get("wheel_count")) is not int \
            or wheelhouse_manifest["wheel_count"] != 8 \
            or not isinstance(wheels, list) or len(wheels) != 8 \
            or receipt.get("wheelhouse_manifest_sha256") != wheelhouse_seal \
            or receipt.get("wheel_set_sha256") \
            != wheelhouse_manifest.get("wheel_set_sha256") \
            or wheelhouse_manifest.get("wheel_set_sha256") != _digest(wheels) \
            or observed_versions != PYOPTIX_REQUIRED_DISTRIBUTIONS:
        raise RuntimeError(
            "independent offline PyOptiX wheelhouse projection differs")
    return receipt


def _validate_runtime_bytes(
        runtime: Mapping[str, Any], *,
        expected_pyoptix_scalar_source_sha256: str,
        expected_rtdl_executable_identities: Mapping[str, Any],
        expected_rtdsl_package_file_count: int,
        expected_rtdsl_package_tree_sha256: str,
        frozen_sources: Mapping[str, Mapping[str, object]] | None = None) -> None:
    _validate_runtime_envelope_independently(runtime)
    files = runtime.get("files")
    if not isinstance(files, Mapping) or set(files) != RUNTIME_FILE_ROLES:
        raise RuntimeError("independent runtime file-role set differs")
    for role, record in files.items():
        if not isinstance(record, Mapping):
            raise RuntimeError(f"independent runtime file row invalid: {role}")
        path = Path(str(record.get("path")))
        if record.get("path_kind") == "REGULAR_FILE":
            fields_ok = set(record) == {"path", "path_kind", "bytes", "sha256"}
            resolved = path
            path_ok = path.is_absolute() and path.is_file() and not path.is_symlink()
        elif record.get("path_kind") == "EXACT_SYMLINK_TO_REGULAR_FILE":
            fields_ok = set(record) == {
                "path", "path_kind", "symlink_target", "resolved_path",
                "bytes", "sha256"}
            resolved = path.resolve(strict=True) if path.is_symlink() else path
            path_ok = role in SYMLINK_FILE_ROLES \
                and path.is_absolute() and path.is_symlink() \
                and str(path.readlink()) == record.get("symlink_target") \
                and str(resolved) == record.get("resolved_path") \
                and resolved.is_file()
        else:
            fields_ok = path_ok = False
            resolved = path
        if not fields_ok or not path_ok \
                or resolved.stat().st_size != record.get("bytes") \
                or _sha(resolved) != record.get("sha256"):
            raise RuntimeError(f"independent runtime file differs: {role}")
    directories = runtime.get("directories")
    if not isinstance(directories, Mapping) \
            or set(directories) != {
                "optix_include", "cuda_include", "optix_sdk",
                "header_projection", "rtdsl_package"}:
        raise RuntimeError("independent runtime directory-role set differs")
    for role, record in directories.items():
        expected_fields = ({
            "path", "file_count", "payload_bytes", "tree_sha256", "files"}
            if role == "rtdsl_package" else {
                "path", "file_count", "payload_bytes", "tree_sha256"})
        if not isinstance(record, Mapping) or set(record) != expected_fields:
            raise RuntimeError(f"independent runtime tree row invalid: {role}")
        path = Path(str(record.get("path")))
        observed = (_independent_rtdsl_package_identity(path)
                    if role == "rtdsl_package" else _tree_identity(path))
        if not path.is_absolute() or not path.is_dir() or path.is_symlink() \
                or observed != {key: record.get(key) for key in observed}:
            raise RuntimeError(f"independent runtime tree differs: {role}")
    combined_runtime = _validate_combined_runtime_independently(runtime)
    package = directories["rtdsl_package"]
    package_root = Path(str(package["path"]))
    wheel_package = _independent_rtdsl_wheel_package_identity(
        Path(str(files["rtdl_wheel"]["path"])))
    if wheel_package != {key: package[key] for key in wheel_package} \
            or package["file_count"] != expected_rtdsl_package_file_count \
            or package["tree_sha256"] \
            != expected_rtdsl_package_tree_sha256 \
            or Path(str(files["rtdsl_init"]["path"])) \
            != package_root / "__init__.py" \
            or Path(str(files["rtdlexe_module"]["path"])) \
            != package_root / "v4_rtdlexe.py":
        raise RuntimeError("independent installed rtdsl product binding differs")
    header_projection = _load(Path(str(
        files["header_projection_receipt"]["path"])))
    projection_root = Path(str(directories["header_projection"]["path"]))
    _validate_header_projection_independently(
        header_projection, projection_root)
    if header_projection.get("projection_file_count") \
            != directories["header_projection"]["file_count"] \
            or header_projection.get("projection_payload_bytes") \
            != directories["header_projection"]["payload_bytes"] \
            or header_projection.get("projection_tree_sha256") \
            != directories["header_projection"]["tree_sha256"] \
            or any(not Path(str(directories[role]["path"])).is_relative_to(
                projection_root) for role in ("optix_include", "cuda_include")):
        raise RuntimeError("independent header projection binding differs")

    deployment_ids = runtime.get("deployment_ids")
    if not isinstance(deployment_ids, Mapping) \
            or set(deployment_ids) != {"relation", "triangle"} \
            or not all(isinstance(item, str) and item
                       for item in deployment_ids.values()):
        raise RuntimeError("independent runtime deployment ids differ")
    pyoptix = runtime.get("pyoptix")
    if not isinstance(pyoptix, Mapping) or set(pyoptix) != {
            "distribution_version", "optix_api_version", "source_commit",
            "source_tree", "goal5800_v7_source_sha256"} \
            or pyoptix.get("distribution_version") != "9.1.0" \
            or pyoptix.get("optix_api_version") != "9.0.0" \
            or pyoptix.get("source_commit") != PYOPTIX_COMMIT \
            or pyoptix.get("source_tree") != PYOPTIX_TREE \
            or pyoptix.get("goal5800_v7_source_sha256") \
            != files["goal5800_v7_source"]["sha256"]:
        raise RuntimeError("independent PyOptiX runtime identity differs")
    expected_policy = {
        "gpu_model_or_driver_preselection_allowed": False,
        "eligibility": "FIRST_OWNER_PROVIDED_TARGET_PASSING_UNTIMED_GATE",
        "result_conditioned_replacement_allowed": False,
        "driver_or_gpu_failure_disposition": "PRESERVE_FAILED_ROW__NO_REPLACEMENT",
    }
    if runtime.get("target_policy") != expected_policy:
        raise RuntimeError("independent target policy differs")
    if runtime.get("formal_preflight_contract") != {
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
    }:
        raise RuntimeError("independent formal preflight contract differs")

    expected_loader_environment = {
        "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH"),
        "LD_PRELOAD": os.environ.get("LD_PRELOAD"),
    }
    observation = _load(Path(str(files["target_observation_receipt"]["path"])))
    observed_projection = _target_observation_projection_independently(
        observation, files=files,
        expected_loader_environment=expected_loader_environment)
    if runtime.get("target_observation") != {
            **observed_projection,
            "observation_receipt_sha256": files[
                "target_observation_receipt"]["sha256"]}:
        raise RuntimeError("independent target observation projection differs")

    direct_receipt = _sealed_receipt(
        Path(str(files["direct_worker_build_receipt"]["path"])),
        schema="rtdl.goal5802.direct_worker_untimed_build_receipt.v2")
    direct_recipe = _load(Path(str(files["direct_build_recipe"]["path"])))
    expected_direct_command = _independent_direct_command(direct_recipe, runtime)
    direct_template = direct_recipe.get("argv_template")
    expected_loader_linkage = {
        "schema": "rtdl.goal5802.direct_nvrtc_loader_linkage.v1",
        "nvrtc_link_flag": "-lnvrtc", "dl_link_flag": "-ldl",
        "nvrtc_link_flag_count": 1, "dl_link_flag_count": 1,
        "both_before_output_flag": True,
    }
    expected_tree_fields = ("file_count", "payload_bytes", "tree_sha256")
    expected_sha256_kat_stdout = (
        b'{"schema":"rtdl.goal5802.direct_sha256_kat.v1",'
        b'"status":"PASS__UNTIMED_NO_GPU","input_utf8":"abc",'
        b'"sha256":"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",'
        b'"registered_performance_timing_count":0,"gpu_kernel_launch_count":0}\n')
    if set(direct_receipt) != {
            "schema", "status", "recipe_sha256", "cxx_path", "cxx_sha256",
            "direct_source_sha256", "optix_include_tree", "cuda_include_tree",
            "direct_source_operation_audit", "command", "loader_linkage",
            "exit_code", "stdout_sha256", "stderr_sha256",
            "output_bytes", "output_sha256",
            "sha256_kat_command", "sha256_kat_exit_code",
            "sha256_kat_stdout_sha256", "sha256_kat_stderr_sha256",
            "sha256_kat_document",
            "loaded_nvrtc_identity_command",
            "loaded_nvrtc_identity_exit_code",
            "loaded_nvrtc_identity_stdout_sha256",
            "loaded_nvrtc_identity_stderr_sha256",
            "loaded_nvrtc_identity_document",
            "registered_performance_timing_count", "gpu_kernel_launch_count",
            "receipt_sha256"} \
            or direct_receipt.get("status") \
            != "PASS__SOURCE_TO_DIRECT_WORKER__UNTIMED" \
            or direct_receipt.get("recipe_sha256") \
            != files["direct_build_recipe"]["sha256"] \
            or direct_receipt.get("cxx_path") != files["cxx_compiler"]["path"] \
            or direct_receipt.get("cxx_sha256") != files["cxx_compiler"]["sha256"] \
            or direct_receipt.get("direct_source_sha256") \
            != files["direct_scalar_source"]["sha256"] \
            or not isinstance(direct_template, list) \
            or direct_template.count("-lnvrtc") != 1 \
            or direct_template.count("-ldl") != 1 \
            or direct_template.index("-lnvrtc") >= direct_template.index("-ldl") \
            or direct_template.index("-ldl") >= direct_template.index("-o") \
            or expected_direct_command.count("-lnvrtc") != 1 \
            or expected_direct_command.count("-ldl") != 1 \
            or expected_direct_command.index("-lnvrtc") \
            >= expected_direct_command.index("-ldl") \
            or expected_direct_command.index("-ldl") \
            >= expected_direct_command.index("-o") \
            or direct_receipt.get("loader_linkage") != expected_loader_linkage \
            or direct_receipt.get("optix_include_tree") != {
                key: directories["optix_include"][key]
                for key in expected_tree_fields} \
            or direct_receipt.get("cuda_include_tree") != {
                key: directories["cuda_include"][key]
                for key in expected_tree_fields} \
            or direct_receipt.get("command") != expected_direct_command \
            or direct_receipt.get("exit_code") != 0 \
            or not _valid_sha256(direct_receipt.get("stdout_sha256")) \
            or not _valid_sha256(direct_receipt.get("stderr_sha256")) \
            or direct_receipt.get("output_bytes") \
            != files["direct_scalar_worker"]["bytes"] \
            or direct_receipt.get("output_sha256") \
            != files["direct_scalar_worker"]["sha256"] \
            or direct_receipt.get("sha256_kat_command") != [
                files["direct_scalar_worker"]["path"], "--local-sha256-kat"] \
            or direct_receipt.get("sha256_kat_exit_code") != 0 \
            or direct_receipt.get("sha256_kat_stdout_sha256") \
            != hashlib.sha256(expected_sha256_kat_stdout).hexdigest() \
            or direct_receipt.get("sha256_kat_stderr_sha256") \
            != hashlib.sha256(b"").hexdigest() \
            or direct_receipt.get("sha256_kat_document") != {
                "schema": "rtdl.goal5802.direct_sha256_kat.v1",
                "status": "PASS__UNTIMED_NO_GPU",
                "input_utf8": "abc",
                "sha256": (
                    "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
                "registered_performance_timing_count": 0,
                "gpu_kernel_launch_count": 0,
            } \
            or direct_receipt.get("loaded_nvrtc_identity_command") != [
                files["direct_scalar_worker"]["path"],
                "--local-nvrtc-identity"] \
            or direct_receipt.get("loaded_nvrtc_identity_exit_code") != 0 \
            or direct_receipt.get("loaded_nvrtc_identity_stderr_sha256") \
            != hashlib.sha256(b"").hexdigest() \
            or any(not _plain_int(direct_receipt.get(key))
                   or direct_receipt[key] != 0 for key in (
                       "registered_performance_timing_count",
                       "gpu_kernel_launch_count")):
        raise RuntimeError("independent Direct build provenance differs")

    direct_nvrtc = _validate_direct_loaded_nvrtc_independently(
        direct_receipt.get("loaded_nvrtc_identity_document"))
    expected_identity_stdout = _direct_nvrtc_identity_stdout_bytes(
        direct_nvrtc)
    if direct_receipt.get("loaded_nvrtc_identity_stdout_sha256") \
            != hashlib.sha256(expected_identity_stdout).hexdigest() \
            or direct_nvrtc.get("loaded_library_path") \
            != files["nvrtc_library"]["path"] \
            or direct_nvrtc.get("loaded_library_bytes") \
            != files["nvrtc_library"]["bytes"] \
            or direct_nvrtc.get("loaded_library_sha256") \
            != files["nvrtc_library"]["sha256"] \
            or direct_nvrtc.get("loaded_builtins_path") \
            != files["nvrtc_builtins"]["path"] \
            or direct_nvrtc.get("loaded_builtins_bytes") \
            != files["nvrtc_builtins"]["bytes"] \
            or direct_nvrtc.get("loaded_builtins_sha256") \
            != files["nvrtc_builtins"]["sha256"]:
        raise RuntimeError("independent Direct loaded NVRTC provenance differs")

    ptx_receipt = _sealed_receipt(
        Path(str(files["matched_ptx_prepare_receipt"]["path"])),
        schema="rtdl.goal5802.matched_ptx_untimed_prepare.v3")
    _validate_fresh_process_replay_independently(
        ptx_receipt, runtime=runtime, header_projection=header_projection,
        projection_root=projection_root, direct_nvrtc=direct_nvrtc,
        frozen_sources=frozen_sources)

    _validate_architecture_contract_independently(
        runtime, files, observation, ptx_receipt)

    wheel_build_path = Path(str(
        files["pyoptix_wheel_build_receipt"]["path"]))
    historical_build = _validate_current_pyoptix_materialization_independently(
        wheel_build_path, files=files, directories=directories,
        header_projection=header_projection)
    wheel = historical_build["wheel"]
    extension_member = wheel.get("extension_member")
    if extension_member != PYOPTIX_EXTENSION_MEMBER:
        raise RuntimeError("independent PyOptiX wheel extension absent")
    try:
        with zipfile.ZipFile(
                Path(str(files["pyoptix_wheel"]["path"]))) as archive:
            extension_bytes = archive.read(extension_member)
            initializer_bytes = archive.read("optix/__init__.py")
    except (OSError, KeyError, zipfile.BadZipFile) as error:
        raise RuntimeError("independent PyOptiX wheel members differ") from error
    if wheel.get("extension_bytes") != len(extension_bytes) \
            or len(extension_bytes) != PYOPTIX_EXTENSION_BYTES \
            or wheel.get("extension_sha256") != PYOPTIX_EXTENSION_SHA256 \
            or hashlib.sha256(extension_bytes).hexdigest() \
            != PYOPTIX_EXTENSION_SHA256 \
            or files["pyoptix_extension"]["sha256"] \
            != PYOPTIX_EXTENSION_SHA256 \
            or files["pyoptix_initializer"]["bytes"] \
            != len(initializer_bytes) \
            or files["pyoptix_initializer"]["sha256"] \
            != hashlib.sha256(initializer_bytes).hexdigest():
        raise RuntimeError("independent PyOptiX wheel extension differs")

    clean_install_path = Path(str(
        files["pyoptix_clean_install_receipt"]["path"]))
    if clean_install_path.name != "offline_pyoptix_clean_install_receipt.json" \
            or clean_install_path.is_symlink():
        raise RuntimeError("independent offline PyOptiX receipt path differs")
    _validate_current_offline_pyoptix_install_independently(
        clean_install_path)

    operation_kat = _sealed_receipt(
        Path(str(files["pyoptix_operation_kat"]["path"])),
        schema="rtdl.goal5802.pyoptix_operation_guard_untimed_kat.v1")
    _validate_operation_kat_independently(
        operation_kat, files,
        expected_source_sha256=expected_pyoptix_scalar_source_sha256)
    direct_operation_kat = _sealed_receipt(
        Path(str(files["direct_operation_kat"]["path"])),
        schema="rtdl.goal5802.direct_operation_guard_untimed_kat.v1")
    _validate_direct_operation_kat_independently(
        direct_operation_kat, files)
    if direct_receipt.get("direct_source_operation_audit") \
            != direct_operation_kat.get("source_audit"):
        raise RuntimeError(
            "independent Direct build/KAT source-audit crossbind differs")
    rtdl_operation_kat = _sealed_receipt(
        Path(str(files["rtdl_operation_kat"]["path"])),
        schema="rtdl.goal5802.rtdl_operation_guard_untimed_kat.v1")
    _validate_rtdl_operation_kat_independently(
        rtdl_operation_kat, files, deployment_ids,
        expected_executable_identities=expected_rtdl_executable_identities)

    host_runtime = _sealed_receipt(
        Path(str(files["host_runtime_provenance"]["path"])),
        schema="rtdl.goal5802.host_runtime_provenance.v3")
    distribution_rows = host_runtime.get("distributions")
    distributions_exact = isinstance(distribution_rows, list) and all(
        isinstance(row, Mapping)
        and set(row) == {"name", "version", "file_count", "payload_bytes",
                        "tree_sha256", "files"}
        and isinstance(row["name"], str)
        and isinstance(row["version"], str) and bool(row["version"])
        and _plain_int(row["file_count"]) and row["file_count"] > 0
        and _plain_int(row["payload_bytes"]) and row["payload_bytes"] > 0
        and _valid_sha256(row["tree_sha256"])
        and isinstance(row["files"], list)
        and all(isinstance(item, Mapping) and set(item) == {
                    "relative_path", "path", "bytes", "sha256"}
                and isinstance(item["relative_path"], str)
                and isinstance(item["path"], str)
                and _plain_int(item["bytes"]) and item["bytes"] >= 0
                and _valid_sha256(item["sha256"])
                and Path(str(item["path"])).is_absolute()
                and Path(str(item["path"])).is_file()
                and not Path(str(item["path"])).is_symlink()
                and Path(str(item["path"])).stat().st_size == item["bytes"]
                and _sha(Path(str(item["path"]))) == item["sha256"]
                for item in row["files"])
        and row["file_count"] == len(row["files"])
        and row["payload_bytes"] == sum(
            int(item["bytes"]) for item in row["files"])
        and row["tree_sha256"] == _digest(row["files"])
        for row in distribution_rows)
    modules = host_runtime.get("loaded_module_files")
    modules_exact = isinstance(modules, Mapping) and all(
        isinstance(record, Mapping)
        and set(record) == {"path", "bytes", "sha256"}
        and isinstance(record["path"], str)
        and _plain_int(record["bytes"]) and record["bytes"] > 0
        and _valid_sha256(record["sha256"])
        and Path(str(record["path"])).is_absolute()
        and Path(str(record["path"])).is_file()
        and not Path(str(record["path"])).is_symlink()
        and Path(str(record["path"])).stat().st_size == record["bytes"]
        and _sha(Path(str(record["path"]))) == record["sha256"]
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
    if set(host_runtime) != {
            "schema", "status", "python", "distributions",
            "loaded_module_files", "host", "thread_and_visibility_environment",
            "registered_performance_timing_count", "formal_worker_count",
            "receipt_sha256"} \
            or host_runtime.get("status") \
            != "PASS__UNTIMED_EXACT_HOST_RUNTIME_CAPTURE" \
            or host_runtime.get("schema") \
            != "rtdl.goal5802.host_runtime_provenance.v3" \
            or any(not _plain_int(host_runtime.get(key))
                   or host_runtime[key] != 0 for key in (
                       "registered_performance_timing_count",
                       "formal_worker_count")) \
            or [row.get("name") for row in host_runtime.get(
                "distributions", []) if isinstance(row, Mapping)] != [
                    "numpy", "cupy-cuda12x", "cuda-python", "numba",
                    "llvmlite"] \
            or not distributions_exact \
            or not modules_exact \
            or set(modules or {}) != {
                "numpy", "cupy", "cuda.bindings.driver",
                "cuda.bindings.nvrtc", "optix", "numba", "llvmlite"} \
            or not python_exact \
            or not isinstance(host_runtime.get("host"), Mapping) \
            or set(host_runtime["host"]) != {
                "system", "release", "machine", "libc", "cpu_model",
                "affinity", "cpu_governors"} \
            or not isinstance(
                host_runtime.get("thread_and_visibility_environment"), Mapping) \
            or set(host_runtime["thread_and_visibility_environment"]) != {
                "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
                "PYTHONHASHSEED", "CUDA_VISIBLE_DEVICES",
                "PATH", "LD_LIBRARY_PATH", "LD_PRELOAD"} \
            or host_runtime["thread_and_visibility_environment"] != {
                key: os.environ.get(key) for key in (
                    "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                    "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                    "VECLIB_MAXIMUM_THREADS", "PYTHONHASHSEED",
                    "CUDA_VISIBLE_DEVICES", "PATH", "LD_LIBRARY_PATH",
                    "LD_PRELOAD")} \
            or not host_runtime["thread_and_visibility_environment"].get(
                "PATH") \
            or any(not item or not Path(item).is_absolute()
                   for item in host_runtime[
                       "thread_and_visibility_environment"]["PATH"].split(
                           os.pathsep)) \
            or host_runtime["thread_and_visibility_environment"].get(
                "LD_PRELOAD") is not None:
        raise RuntimeError("independent host/runtime provenance differs")

    combined_receipt_path = Path(str(
        files["combined_runtime_receipt"]["path"]))
    combined_root = combined_receipt_path.parent
    extension_path = Path(str(files["pyoptix_extension"]["path"]))
    combined_path_projection = {
        "root_path": str(combined_root),
        "clean_python_relative": "venv/bin/python",
        "site_packages_relative": "venv/lib/python3.12/site-packages",
        "rtdsl_package_relative": (
            "venv/lib/python3.12/site-packages/rtdsl"),
        "pyoptix_initializer_relative": (
            "venv/lib/python3.12/site-packages/optix/__init__.py"),
        "pyoptix_extension_relative": extension_path.relative_to(
            combined_root).as_posix(),
        "all_runtime_paths_inside_receipted_combined_root": True,
    }
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
        "combined_runtime_full_venv_member_tree_sha256": combined_runtime[
            "venv_member_tree_sha256"],
        "combined_runtime_path_projection": combined_path_projection,
        "header_projection_tree_sha256": directories[
            "header_projection"]["tree_sha256"],
        "fresh_process_projection_replay_verified": True,
        "all_source_to_runtime_links_verified_untimed": True,
    }
    if runtime.get("build_provenance") != expected_provenance:
        raise RuntimeError("independent build-provenance binding differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--runtime-manifest", type=Path, required=True)
    parser.add_argument("--controller-result", type=Path, required=True)
    parser.add_argument("--primary-evaluation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    freeze = _load(args.freeze)
    authority = _load(args.execution_authority)
    runtime = _load(args.runtime_manifest)
    controller = _load(args.controller_result)
    primary = _load(args.primary_evaluation)
    freeze_sha = _sha(args.freeze)
    authority_sha = _sha(args.execution_authority)
    runtime_sha = _sha(args.runtime_manifest)
    root = args.root.resolve(strict=True)
    freeze_path = args.freeze.resolve(strict=True)
    authority_path = args.execution_authority.resolve(strict=True)
    runtime_path = args.runtime_manifest.resolve(strict=True)
    _validate_execution_authority_bytes(
        authority, freeze_sha=freeze_sha, runtime_sha=runtime_sha)
    source_path = (
        "experiments/goal5802_premeasurement/pyoptix_scalar_arm.py")
    source_rows = freeze.get("source_manifest")
    if not isinstance(source_rows, list) or not source_rows:
        raise RuntimeError("independent frozen source manifest is absent")
    frozen_sources: dict[str, Mapping[str, object]] = {}
    for row in source_rows:
        if not isinstance(row, Mapping) or set(row) != {
                "path", "bytes", "sha256"}:
            raise RuntimeError("independent frozen source row differs")
        relative = row.get("path")
        if not isinstance(relative, str) or not relative \
                or Path(relative).is_absolute() or ".." in Path(relative).parts \
                or Path(relative).as_posix() != relative \
                or relative in frozen_sources:
            raise RuntimeError("independent frozen source path differs")
        source_file = root / Path(relative)
        if not source_file.is_file() or source_file.is_symlink() \
                or not source_file.resolve(strict=True).is_relative_to(root) \
                or source_file.stat().st_size != row.get("bytes") \
                or _sha(source_file) != row.get("sha256"):
            raise RuntimeError(
                f"independent frozen source bytes differ: {relative}")
        frozen_sources[relative] = {
            "absolute_path": str(source_file.resolve(strict=True)),
            "bytes": row["bytes"], "sha256": row["sha256"],
        }
    required_frozen = {
        source_path,
        "experiments/goal5802_premeasurement/direct_scalar_worker.cpp",
        ("experiments/goal5802_premeasurement/"
         "matched_device_semantic_capacity.cu"),
        ("experiments/goal5802_premeasurement/"
         "relation_semantic_compaction.cu"),
        "experiments/goal5802_premeasurement/independent_recount.py",
        "scripts/goal5802_build_header_projection_untimed.py",
        "scripts/goal5802_nvrtc_compile_child.py",
        "scripts/goal5802_prepare_matched_ptx_untimed.py",
    }
    if not required_frozen.issubset(frozen_sources):
        raise RuntimeError("independent required frozen source set differs")
    _validate_runtime_bytes(
        runtime,
        expected_pyoptix_scalar_source_sha256=str(
            frozen_sources[source_path]["sha256"]),
        expected_rtdl_executable_identities={
            "relation": freeze["product_binding"][
                "relation_executable_identity_sha256"],
            "triangle": freeze["product_binding"][
                "triangle_executable_identity_sha256"],
        },
        expected_rtdsl_package_file_count=freeze["product_binding"][
            "rtdsl_package_file_count"],
        expected_rtdsl_package_tree_sha256=freeze["product_binding"][
            "rtdsl_package_tree_sha256"],
        frozen_sources=frozen_sources)
    independent = recount(
        freeze, controller, freeze_file_sha256=freeze_sha,
        execution_authority_sha256=authority_sha,
        runtime_manifest_sha256=runtime_sha,
        raw_root=args.controller_result.resolve(strict=True).parent,
        runtime=runtime, root=root, freeze_path=freeze_path,
        authority_path=authority_path, runtime_path=runtime_path)
    projection_keys = (
        "status", "comparative_failure_worker_ids",
        "build_cold_failure_worker_ids", "comparative_validation_failures",
        "build_cold_validation_failures", "comparative_absolute",
        "phase_attribution", "comparative_ratios", "build_cold_absolute",
        "build_cold_enters_comparative_gate", "amortization",
        "all_primary_noninferiority_gates_pass", "retry_count",
        "replacement_count",
    )
    primary_projection = {key: primary.get(key) for key in projection_keys}
    if independent != primary_projection:
        raise RuntimeError("independent raw recount differs from primary evaluation")
    result = {
        "schema": "rtdl.goal5802.independent_raw_recount.v2",
        "status": "PASS__RAW_BYTES_AND_EXACT_PRIMARY_SEMANTIC_PROJECTION",
        "freeze_file_sha256": freeze_sha,
        "execution_authority_file_sha256": authority_sha,
        "runtime_manifest_file_sha256": runtime_sha,
        "primary_evaluation_sha256": _sha(args.primary_evaluation),
        "controller_result_sha256": _sha(args.controller_result),
        "projection": independent,
    }
    result["recount_sha256"] = hashlib.sha256(_canonical(result)).hexdigest()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({"status": result["status"],
                      "recount_sha256": result["recount_sha256"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
