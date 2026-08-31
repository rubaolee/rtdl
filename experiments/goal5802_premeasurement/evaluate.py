#!/usr/bin/env python3
"""Primary frozen evaluator for Goal5802 comparative and BUILD_COLD rows."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
from typing import Any, Mapping

from .contract import (
    ARMS,
    BOOTSTRAP_DRAWS,
    BOOTSTRAP_SEED_BASE,
    REGIMES,
    TASKS,
    build_cold_schedule,
    build_schedule,
    digest,
    validate_freeze,
)
from .controller import validate_formal_runtime_preflight_receipt


DIRECT, PYOPTIX, RTDL = ARMS
RATIO_ROWS = (
    ("RTDL_OVER_PYOPTIX", RTDL, PYOPTIX),
    ("DIRECT_OVER_PYOPTIX", DIRECT, PYOPTIX),
    ("RTDL_OVER_DIRECT", RTDL, DIRECT),
)
GATE = {"DEPLOYMENT_COLD": 1.10, "PREPARE": 1.10, "STEADY_E2E": 1.05}
OPERATION_COUNT_KEYS = (
    "prepare_device_allocation_call_count", "prepare_h2d_call_count",
    "prepare_pinned_host_allocation_call_count", "prepare_stream_creation_count",
    "execute_device_allocation_call_count",
    "execute_pinned_host_allocation_call_count",
    "execute_async_h2d_call_count", "execute_async_d2h_call_count",
    "execute_blocking_d2h_call_count", "execute_device_zero_fill_call_count",
    "execute_explicit_stream_sync_call_count", "execute_launch_call_count",
    "execute_stream_creation_call_count", "execute_stream_destroy_call_count",
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
PYOPTIX_GUARD = {
    "scope": "PYTHON_VISIBLE_TASK_OWNER_EXECUTE__NOT_CUPTI_OR_DRIVER_WIDE",
    "unapproved_device_allocation_call_count": 0,
    "unapproved_pinned_host_allocation_call_count": 0,
    "unapproved_blocking_asnumpy_call_count": 0,
    "unauthorized_direct_stream_sync_count": 0,
    "complete_driver_operation_observation_claimed": False,
}


def _expected_build_rtdsl_modules(task: str) -> list[str]:
    names = {
        "rtdsl", "rtdsl.v4", "rtdsl.v4_callback_lifecycle",
        "rtdsl.v4_rtdlexe",
        ("rtdsl.v4_bounded_relation_optix_compiler"
         if task == TASKS[0]
         else "rtdsl.v4_triangle_standard_library"),
    }
    if task != TASKS[0]:
        names.add("rtdsl.v4_triangle_reduction_optix_compiler")
    return sorted(names)


def _validate_build_rtdsl_import_identity(
        worker: Mapping[str, Any], *, row: Mapping[str, Any],
        freeze: Mapping[str, Any]) -> None:
    identity = worker.get("rtdsl_import_identity")
    if row["arm"] != RTDL:
        if identity is not None:
            raise RuntimeError("non-RTDL BUILD_COLD carries RTDL import identity")
        return
    product = freeze["product_binding"]
    required = {
        "schema", "status", "rtdsl_package_file_count",
        "rtdsl_package_tree_sha256", "required_module_names",
        "loaded_rtdsl_modules", "loaded_rtdsl_modules_sha256",
    }
    modules = identity.get("loaded_rtdsl_modules") \
        if isinstance(identity, Mapping) else None
    if not isinstance(identity, Mapping) or set(identity) != required \
            or identity.get("schema") \
            != "rtdl.goal5802.build_cold_rtdsl_import_identity.v1" \
            or identity.get("status") \
            != "PASS__ALL_LOADED_RTDL_MODULES_FROM_SEALED_PACKAGE" \
            or identity.get("rtdsl_package_file_count") \
            != product["rtdsl_package_file_count"] \
            or identity.get("rtdsl_package_tree_sha256") \
            != product["rtdsl_package_tree_sha256"] \
            or identity.get("required_module_names") \
            != _expected_build_rtdsl_modules(str(row["task"])) \
            or not isinstance(modules, list) or not modules \
            or identity.get("loaded_rtdsl_modules_sha256") \
            != digest(modules):
        raise RuntimeError("RTDL BUILD_COLD import identity differs")
    observed: set[str] = set()
    for module in modules:
        if not isinstance(module, Mapping) or set(module) != {
                "module", "path", "relative_path", "bytes", "sha256"} \
                or not isinstance(module.get("module"), str) \
                or module["module"] in observed \
                or not isinstance(module.get("path"), str) \
                or not Path(module["path"]).is_absolute() \
                or not isinstance(module.get("relative_path"), str) \
                or not module["relative_path"].startswith("rtdsl/") \
                or type(module.get("bytes")) is not int \
                or module["bytes"] <= 0 \
                or not _valid_sha256(module.get("sha256")):
            raise RuntimeError("RTDL BUILD_COLD imported module row differs")
        observed.add(str(module["module"]))
    if not set(identity["required_module_names"]).issubset(observed):
        raise RuntimeError("RTDL BUILD_COLD required imported module absent")


def _validate_compiler_runtime_authority(
        value: Any) -> tuple[dict[str, Mapping[str, Any]],
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
            or seal != digest(unsigned) \
            or not isinstance(distributions, list) \
            or not isinstance(modules, list) \
            or [row.get("name") for row in distributions
                if isinstance(row, Mapping)] != ["numba", "llvmlite"] \
            or [row.get("name") for row in modules
                if isinstance(row, Mapping)] != ["numba", "llvmlite"]:
        raise RuntimeError("BUILD_COLD compiler runtime authority differs")
    distribution_by_name: dict[str, Mapping[str, Any]] = {}
    module_by_name: dict[str, Mapping[str, Any]] = {}
    for row in distributions:
        if not isinstance(row, Mapping) or set(row) != {
                "name", "version", "file_count", "payload_bytes",
                "tree_sha256"} \
                or not isinstance(row.get("version"), str) or not row["version"] \
                or type(row.get("file_count")) is not int \
                or row["file_count"] <= 0 \
                or type(row.get("payload_bytes")) is not int \
                or row["payload_bytes"] <= 0 \
                or not _valid_sha256(row.get("tree_sha256")):
            raise RuntimeError("BUILD_COLD compiler distribution row differs")
        distribution_by_name[str(row["name"])] = row
    for row in modules:
        if not isinstance(row, Mapping) or set(row) != {
                "name", "path", "bytes", "sha256"} \
                or not isinstance(row.get("path"), str) \
                or not Path(row["path"]).is_absolute() \
                or type(row.get("bytes")) is not int or row["bytes"] <= 0 \
                or not _valid_sha256(row.get("sha256")):
            raise RuntimeError("BUILD_COLD compiler module authority row differs")
        module_by_name[str(row["name"])] = row
    return distribution_by_name, module_by_name


def _validate_build_compiler_runtime_identity(
        worker: Mapping[str, Any], *, row: Mapping[str, Any],
        controller: Mapping[str, Any]) -> None:
    identity = worker.get("compiler_runtime_identity")
    authority = controller.get("numba_llvmlite_runtime_authority")
    distribution_by_name, module_by_name = \
        _validate_compiler_runtime_authority(authority)
    if row["arm"] != RTDL:
        if identity is not None:
            raise RuntimeError(
                "non-RTDL BUILD_COLD carries compiler runtime identity")
        return
    required = {
        "schema", "status", "compiler_runtime_authority_sha256",
        "actual_loaded_module_files", "actual_loaded_module_files_sha256",
        "identity_sha256",
    }
    unsigned = dict(identity) if isinstance(identity, Mapping) else {}
    seal = unsigned.pop("identity_sha256", None)
    modules = identity.get("actual_loaded_module_files") \
        if isinstance(identity, Mapping) else None
    if not isinstance(identity, Mapping) or set(identity) != required \
            or identity.get("schema") \
            != "rtdl.goal5802.build_cold_compiler_runtime_identity.v1" \
            or identity.get("status") \
            != "PASS__ACTUAL_NUMBA_LLVM_LITE_MATCH_SEALED_RUNTIME" \
            or identity.get("compiler_runtime_authority_sha256") \
            != authority["authority_sha256"] \
            or not isinstance(modules, list) \
            or identity.get("actual_loaded_module_files_sha256") \
            != digest(modules) \
            or seal != digest(unsigned) \
            or [item.get("name") for item in modules
                if isinstance(item, Mapping)] != ["numba", "llvmlite"]:
        raise RuntimeError("RTDL BUILD_COLD compiler runtime identity differs")
    for item in modules:
        name = item.get("name") if isinstance(item, Mapping) else None
        distribution = distribution_by_name.get(str(name))
        expected_module = module_by_name.get(str(name))
        if not isinstance(item, Mapping) or set(item) != {
                "name", "version", "path", "bytes", "sha256"} \
                or not isinstance(distribution, Mapping) \
                or not isinstance(expected_module, Mapping) \
                or item.get("version") != distribution.get("version") \
                or item.get("path") != expected_module.get("path") \
                or item.get("bytes") != expected_module.get("bytes") \
                or item.get("sha256") != expected_module.get("sha256"):
            raise RuntimeError(
                "RTDL BUILD_COLD actual compiler module differs")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_int(value: Any, expected: int, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value != expected:
        raise RuntimeError(f"{label} differs")


def _valid_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 \
        and all(character in "0123456789abcdef" for character in value)


def _validate_controller_envelope(
        controller: Mapping[str, Any], *, comparative_count: int,
        build_count: int, freeze: Mapping[str, Any]) -> None:
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
            or not all(_valid_sha256(controller.get(key)) for key in (
                "freeze_file_sha256", "execution_authority_sha256",
                "runtime_manifest_sha256")) \
            or controller.get("worker_count") != comparative_count + build_count \
            or controller.get("comparative_worker_count") != comparative_count \
            or controller.get("build_cold_absolute_worker_count") != build_count \
            or controller.get("retry_count") != 0 \
            or controller.get("replacement_count") != 0 \
            or controller.get("build_cold_enters_comparative_gate") is not False:
        raise RuntimeError("primary controller envelope differs")
    expected_boundary = {
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
        "python_primary_timer_new_module_load_policy": "REJECT_ALL_NOT_PRELOADED",
        "python_startup_flags_exact": ["-I", "-S", "-B", "-P", "-c"],
        "pth_execution_in_build_kat_preflight_or_formal": False,
    }
    if controller.get("measurement_boundary_contract") != expected_boundary:
        raise RuntimeError("primary measurement boundary contract differs")
    _validate_compiler_runtime_authority(
        controller.get("numba_llvmlite_runtime_authority"))
    runtime_preflight = controller.get("runtime_preflight")
    if not isinstance(runtime_preflight, Mapping):
        raise RuntimeError("primary runtime preflight is absent")
    validate_formal_runtime_preflight_receipt(
        runtime_preflight,
        runtime_manifest_sha256=str(controller["runtime_manifest_sha256"]),
        rehash_files=False)
    preworker_combined = controller.get(
        "preworker_combined_runtime_revalidation")
    if not isinstance(preworker_combined, Mapping) \
            or set(preworker_combined) != {
                "receipt_sha256", "venv_member_tree_sha256"} \
            or not all(_valid_sha256(preworker_combined.get(key)) for key in (
                "receipt_sha256", "venv_member_tree_sha256")):
        raise RuntimeError(
            "primary preworker combined-runtime revalidation differs")
    post_runtime = controller.get("post_execution_runtime_revalidation")
    product = freeze.get("product_binding")
    if not isinstance(post_runtime, Mapping) or not isinstance(product, Mapping) \
            or post_runtime != {
                "status": (
                    "PASS__ALL_RUNTIME_PAYLOADS_REHASHED_AFTER_FINAL_WORKER"),
                "runtime_manifest_file_sha256": controller[
                    "runtime_manifest_sha256"],
                "combined_runtime_receipt_sha256": preworker_combined[
                    "receipt_sha256"],
                "combined_runtime_full_venv_member_tree_sha256": (
                    preworker_combined["venv_member_tree_sha256"]),
                "rtdsl_package_file_count": product[
                    "rtdsl_package_file_count"],
                "rtdsl_package_tree_sha256": product[
                    "rtdsl_package_tree_sha256"],
            }:
        raise RuntimeError("primary post-execution runtime revalidation differs")
    snapshot = controller.get("host_code_snapshot")
    if not isinstance(snapshot, Mapping) or set(snapshot) != {
            "schema", "file_count", "payload_bytes", "rows_sha256",
            "pycache_file_count", "readonly"} \
            or snapshot.get("schema") != "rtdl.goal5802.host_code_snapshot.v1" \
            or snapshot.get("file_count", 0) <= 0 \
            or snapshot.get("payload_bytes", 0) <= 0 \
            or not _valid_sha256(snapshot.get("rows_sha256")) \
            or snapshot.get("pycache_file_count") != 0 \
            or snapshot.get("readonly") is not True:
        raise RuntimeError("primary host-code snapshot differs")
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
            or snapshot.get("rows_sha256") != digest(snapshot_rows):
        raise RuntimeError("primary host-code snapshot identity differs")
    rows = [*controller["comparative_rows"],
            *controller["build_cold_absolute_rows"]]
    passed = sum(row.get("status") == "PASS" for row in rows)
    failed = len(rows) - passed
    expected_status = (
        "COMPLETE" if failed == 0
        else "COMPLETE_WITH_FAILED_ROWS__NO_RETRY_OR_REPLACEMENT")
    if controller.get("passed_worker_count") != passed \
            or controller.get("failed_worker_count") != failed \
            or controller.get("status") != expected_status:
        raise RuntimeError("primary controller count/status differs")


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
        "controller_process_envelope_ns", "stdout_bytes", "stdout_sha256",
        "stderr_bytes", "stderr_sha256", "worker_result",
        "comparative_measurement_boundary",
        "preworker_common_cache_conditioning",
        "isolated_process_cache_policy", "isolated_process_cache_end_state",
    }
    if not isinstance(receipt, Mapping) or set(receipt) != required \
            or receipt.get("schema") != expected_schema \
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
                   or receipt[key] < 0 for key in (
                       "stdout_bytes", "stderr_bytes")) \
            or not _valid_sha256(receipt.get("stdout_sha256")) \
            or not _valid_sha256(receipt.get("stderr_sha256")):
        raise RuntimeError("primary indexed controller receipt differs")
    if (kind == "comparative" and not isinstance(
            receipt.get("preworker_common_cache_conditioning"), Mapping)) \
            or (kind == "build" and receipt.get(
                "preworker_common_cache_conditioning") is not None):
        raise RuntimeError("primary indexed cache-conditioning differs")
    boundary = receipt.get("comparative_measurement_boundary")
    if (kind == "build" and boundary is not None) \
            or (kind == "comparative" and receipt["status"] == "PASS"
                and not isinstance(boundary, Mapping)) \
            or (kind == "comparative" and receipt["status"] != "PASS"
                and boundary is not None and not isinstance(boundary, Mapping)):
        raise RuntimeError("primary indexed measurement boundary differs")
    _validate_isolated_process_caches(receipt)
    if receipt["status"] == "PASS" and (
            receipt.get("exit_code") != 0
            or receipt.get("timed_out") is not False
            or receipt.get("spawn_error") is not None
            or receipt.get("orphan_process_group_detected") is not False
            or not isinstance(receipt.get("worker_result"), Mapping)):
        raise RuntimeError("primary PASS process disposition differs")


def _exact_operation_counts(**nonzero: int) -> dict[str, int]:
    result = {key: 0 for key in OPERATION_COUNT_KEYS}
    if set(nonzero).difference(result):
        raise RuntimeError("evaluator operation-count vocabulary drift")
    result.update(nonzero)
    return result


def _validate_execution_lifecycle(
        worker: Mapping[str, Any], row: Mapping[str, Any]) -> None:
    receipts = worker.get("execution_lifecycle_receipts")
    expected_count = 72 if row["regime"] == "STEADY_E2E" else 1
    fields = {
        "prepared_input_reused", "dynamic_device_upload_call_count",
        "dynamic_device_upload_bytes", "dynamic_accel_build_count",
        "dynamic_explicit_sync_count", "dynamic_blocking_upload_call_count",
        "dynamic_input_generation",
    }
    if not isinstance(receipts, list) or len(receipts) != expected_count:
        raise RuntimeError("dynamic-input lifecycle receipt count differs")
    for index, receipt in enumerate(receipts):
        if not isinstance(receipt, Mapping) or set(receipt) != fields:
            raise RuntimeError("dynamic-input lifecycle receipt fields differ")
        for key in fields - {"prepared_input_reused"}:
            value = receipt[key]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise RuntimeError(f"dynamic-input counter invalid: {key}")
        if index == 0:
            relation = row["task"] == TASKS[0]
            rtdl_triangle = row["arm"] == RTDL and not relation
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
            if dict(receipt) != expected_first:
                raise RuntimeError("first execute did not build exact dynamic input")
        elif receipt != {
                "prepared_input_reused": True,
                "dynamic_device_upload_call_count": 0,
                "dynamic_device_upload_bytes": 0,
                "dynamic_accel_build_count": 0,
                "dynamic_explicit_sync_count": 0,
                "dynamic_blocking_upload_call_count": 0,
                "dynamic_input_generation": 1,
        }:
            raise RuntimeError("later execute did not exactly reuse dynamic input")
    if row["arm"] == DIRECT:
        evidence = worker.get("operation_ledger")
    else:
        evidence = worker.get("result")
    if not isinstance(evidence, Mapping) \
            or (row["arm"] == DIRECT
                and evidence.get("dynamic_input_receipt") != receipts[-1]):
        raise RuntimeError("final result/lifecycle dynamic receipt differs")


def _validate_pyoptix_operation_receipt(
        evidence: Mapping[str, Any], task: str) -> None:
    if evidence.get("live_execute_guard_inside_timer") is not False \
            or "independent_execute_guard" in evidence:
        raise RuntimeError("PyOptiX comparative execute contains live forensic guard")
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
        raise RuntimeError("PyOptiX post-timer operation authority differs")


def _validate_rtdl_native_operation_receipt(
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
    if not isinstance(native, Mapping) or set(native) != fields \
            or not isinstance(dynamic, Mapping) \
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
            or native.get("dynamic_blocking_upload_call_count") != 0:
        raise RuntimeError("RTDL native operation receipt differs")
    expected_auxiliary = (
        {
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
        } if task == TASKS[0] else {
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
    if any(native.get(key) != value
           for key, value in expected_auxiliary.items()):
        raise RuntimeError("RTDL native auxiliary-operation receipt differs")
    for key in (
            "prepared_input_reused", "dynamic_device_upload_call_count",
            "dynamic_device_upload_bytes", "dynamic_accel_build_count",
            "dynamic_explicit_sync_count", "dynamic_blocking_upload_call_count",
            "dynamic_input_generation"):
        if native.get(key) != dynamic.get(key):
            raise RuntimeError("RTDL native/dynamic receipt projection differs")


def _validate_correctness(
        worker: Mapping[str, Any], row: Mapping[str, Any],
        freeze: Mapping[str, Any]) -> None:
    task = row["task"]
    arm = row["arm"]
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
            if task == TASKS[0]
            else {"optix_launch_count", "async_h2d_call_count",
                  "async_h2d_bytes", "async_d2h_call_count",
                  "device_intermediate_per_ray_bytes", "device_reset_bytes",
                  "h2d_launch_parameter_bytes",
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
            if task == TASKS[0]
            else common | {"launch_count", "reduced_u64", "status_d2h_bytes",
                           "scalar_d2h_bytes", "per_ray_device_intermediate_bytes",
                           "device_reset_bytes", "h2d_launch_parameter_bytes"})
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
            "worker correctness/operation field set differs: "
            f"evidence={sorted(set(evidence) ^ expected_evidence_fields)} "
            f"operation={sorted(set(operation) ^ expected_operation_fields)}")
    _validate_execution_lifecycle(worker, row)
    if arm == PYOPTIX:
        _validate_pyoptix_operation_receipt(evidence, task)
    elif arm == RTDL:
        if evidence.get("dynamic_input_receipt") \
                != worker["execution_lifecycle_receipts"][-1]:
            raise RuntimeError(
                "RTDL duplicated dynamic receipt differs from lifecycle")
        _validate_rtdl_native_operation_receipt(
            evidence, task, worker["execution_lifecycle_receipts"][-1])
        family = "relation" if task == TASKS[0] else "triangle"
        if evidence.get("executable_identity_sha256") != freeze[
                "product_binding"][f"{family}_executable_identity_sha256"]:
            raise RuntimeError("RTDL executed executable identity differs")
    if task == TASKS[0]:
        rows = evidence.get("canonical_rows") if direct else evidence.get("output")
        if not isinstance(rows, list) or len(rows) != 4096 \
                or digest(rows) != freeze["workload_authority"]["relation"][
                    "expected_rows_sha256"]:
            raise RuntimeError("relation exact output differs")
        if direct:
            if evidence.get("oracle_exact") is not True:
                raise RuntimeError("Direct relation oracle flag absent")
            _require_int(evidence.get("canonical_row_count"), 4096,
                         "Direct relation row count")
            _require_int(evidence.get("raw_event_count"), 8192,
                         "Direct relation raw count")
            _require_int(evidence.get("semantic_unique_count"), 4096,
                         "Direct relation semantic unique count")
            _require_int(evidence.get("device_status"), 0,
                         "Direct relation status")
            _require_int(evidence.get("device_overflow"), 0,
                         "Direct relation overflow")
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


def _validate_cache_conditioning(receipt: Mapping[str, Any]) -> None:
    value = receipt.get("preworker_common_cache_conditioning")
    required = {
        "policy", "roles", "payload_bytes", "rows_sha256", "duration_ns",
        "os_shared_library_and_driver_cache_state",
    }
    expected_roles: list[str] = []
    if not isinstance(value, Mapping) or set(value) != required \
            or value.get("policy") != (
                "NO_MANUAL_FILE_PAGE_CONDITIONING__OS_PAGE_CACHE_"
                "UNCONTROLLED__BALANCED_SIX_ORDER") \
            or value.get("roles") != expected_roles \
            or value.get("os_shared_library_and_driver_cache_state") \
            != "UNCONTROLLED__DISCLOSED" \
            or value.get("payload_bytes") != 0 \
            or value.get("duration_ns") != 0 \
            or not isinstance(value.get("rows_sha256"), str) \
            or len(value["rows_sha256"]) != 64:
        raise RuntimeError("comparative common cache-conditioning receipt differs")


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
        raise RuntimeError("isolated process-cache policy differs")
    if end != {
            "file_count": 0, "payload_bytes": 0,
            "rows_sha256": hashlib.sha256(b"[]").hexdigest(),
            "all_cache_roots_file_empty_after_worker": True}:
        raise RuntimeError("isolated process cache was not empty after worker")


def _duration(
        receipt: Mapping[str, Any], *, row: Mapping[str, Any],
        freeze: Mapping[str, Any], controller: Mapping[str, Any]) -> float:
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
        if row["arm"] == DIRECT
        else common_worker_fields | {"result", "loaded_runtime_identity"}
        | python_boundary_fields)
    if set(worker) != expected_worker_fields \
            or worker.get("schema") != expected_schema \
            or worker.get("status") != "PASS" \
            or worker.get("worker_id") != row["worker_id"] \
            or worker.get("arm") != row["arm"] \
            or worker.get("task") != row["task"] \
            or worker.get("regime") != row["regime"] \
            or worker.get("freeze_file_sha256") \
            != controller.get("freeze_file_sha256") \
            or worker.get("execution_authority_sha256") \
            != controller.get("execution_authority_sha256") \
            or worker.get("runtime_manifest_sha256") \
            != controller.get("runtime_manifest_sha256") \
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
        if not _valid_sha256(retained) \
                or (row["task"] == TASKS[0]
                    and not _valid_sha256(retained_compaction)) \
                or (row["task"] != TASKS[0] and retained_compaction is not None):
            raise RuntimeError("Direct retained executed PTX identity invalid")
    else:
        identity = worker.get("loaded_runtime_identity")
        expected_identity_fields = (
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
        digest_fields = (
            {"initializer_sha256", "extension_sha256", "matched_ptx_sha256",
             "retained_matched_ptx_sha256"}
            | ({"compaction_cubin_sha256",
                "retained_compaction_cubin_sha256"}
               if row["task"] == TASKS[0] else set())
            if row["arm"] == PYOPTIX else
            {"rtdsl_init_sha256", "rtdlexe_module_sha256",
             "executed_executable_identity_sha256"})
        if not isinstance(identity, Mapping) \
                or set(identity) != expected_identity_fields \
                or any(not _valid_sha256(identity.get(key))
                       for key in digest_fields):
            raise RuntimeError("Python arm loaded-runtime identity differs")
    values = worker.get("execute_or_regime_durations_ns")
    expected = 64 if row["regime"] == "STEADY_E2E" else 1
    if not isinstance(values, list) or len(values) != expected \
            or any(isinstance(item, bool) or not isinstance(item, int) or item <= 0
                   for item in values):
        raise RuntimeError("worker duration vector invalid")
    _require_int(worker.get("registered_performance_timing_count"), expected,
                 "registered timing count")
    _validate_cache_conditioning(receipt)
    _validate_isolated_process_caches(receipt)
    _validate_phases(
        worker, row, values, receipt.get("controller_process_envelope_ns"))
    _validate_correctness(worker, row, freeze)
    return float(statistics.median(values))


def _build_duration(
        receipt: Mapping[str, Any], *, row: Mapping[str, Any],
        controller: Mapping[str, Any], freeze: Mapping[str, Any]) -> float:
    if receipt.get("status") != "PASS":
        raise RuntimeError("failed build row")
    _validate_isolated_process_caches(receipt)
    worker = receipt.get("worker_result")
    value = worker.get("duration_ns") if isinstance(worker, Mapping) else None
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
            or worker.get("freeze_file_sha256") \
            != controller.get("freeze_file_sha256") \
            or worker.get("execution_authority_sha256") \
            != controller.get("execution_authority_sha256") \
            or worker.get("runtime_manifest_sha256") \
            != controller.get("runtime_manifest_sha256") \
            or worker.get("true_build_executed") is not True \
            or worker.get("prebuilt_product_read_as_build") is not False \
            or worker.get("build_boundary") \
            != "PRE_SIGNING_PRE_DEPLOYMENT_BUILD_PRODUCT" \
            or worker.get("deployable_product_claimed") is not False \
            or worker.get("signing_or_trust_governance_inside_timer") is not False \
            or worker.get("registered_performance_timing_count") != 1 \
            or set(worker.get("outputs", {})) != expected_outputs[row["arm"]] \
            or isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise RuntimeError("BUILD_COLD identity or declared boundary differs")
    for output in worker["outputs"].values():
        if not isinstance(output, Mapping) or set(output) != {
                "path", "bytes", "sha256"} \
                or not isinstance(output.get("bytes"), int) \
                or isinstance(output.get("bytes"), bool) \
                or output["bytes"] <= 0 \
                or not isinstance(output.get("sha256"), str) \
                or len(output["sha256"]) != 64:
            raise RuntimeError("BUILD_COLD output identity invalid")
    _validate_build_rtdsl_import_identity(worker, row=row, freeze=freeze)
    _validate_build_compiler_runtime_identity(
        worker, row=row, controller=controller)
    return float(value)


def _bootstrap(values: list[float], seed: int) -> tuple[float, float]:
    if len(values) != 24 or any(not math.isfinite(item) or item <= 0 for item in values):
        raise RuntimeError("paired-ratio vector invalid")
    generator = random.Random(seed)
    draws = [statistics.median(generator.choices(values, k=len(values)))
             for _ in range(BOOTSTRAP_DRAWS)]
    draws.sort()
    return float(draws[249]), float(draws[9749])


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
        "prepare_subphase_disposition": (
            "COMBINED_NOT_SEPARATELY_OBSERVABLE"),
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


def evaluate(freeze: Mapping[str, Any], controller: Mapping[str, Any]) -> dict[str, Any]:
    expected_comparative = build_schedule()
    expected_build = build_cold_schedule()
    comparative_receipts = controller.get("comparative_rows")
    build_receipts = controller.get("build_cold_absolute_rows")
    if not isinstance(comparative_receipts, list) \
            or not isinstance(build_receipts, list) \
            or [row.get("schedule_row") for row in comparative_receipts] \
            != expected_comparative \
            or [row.get("schedule_row") for row in build_receipts] != expected_build:
        raise RuntimeError("controller rows differ from frozen schedules")
    _validate_controller_envelope(
        controller, comparative_count=len(expected_comparative),
        build_count=len(expected_build), freeze=freeze)
    for receipt, row in zip(
            comparative_receipts, expected_comparative, strict=True):
        _validate_indexed_receipt(receipt, row=row, kind="comparative")
    for receipt, row in zip(build_receipts, expected_build, strict=True):
        _validate_indexed_receipt(receipt, row=row, kind="build")
    comparative_by_id = {
        row["schedule_row"]["worker_id"]: row for row in comparative_receipts}
    build_by_id = {row["schedule_row"]["worker_id"]: row for row in build_receipts}
    comparative_values: dict[str, float] = {}
    comparative_errors: dict[str, str] = {}
    for row in expected_comparative:
        try:
            comparative_values[row["worker_id"]] = _duration(
                comparative_by_id[row["worker_id"]], row=row,
                freeze=freeze, controller=controller)
        except (KeyError, RuntimeError, TypeError, ValueError) as error:
            comparative_errors[row["worker_id"]] = str(error)
    build_values: dict[str, float] = {}
    build_errors: dict[str, str] = {}
    for row in expected_build:
        try:
            build_values[row["worker_id"]] = _build_duration(
                build_by_id[row["worker_id"]], row=row,
                controller=controller, freeze=freeze)
        except (KeyError, RuntimeError, TypeError, ValueError) as error:
            build_errors[row["worker_id"]] = str(error)

    comparative_absolute: list[dict[str, Any]] = []
    phase_attribution: list[dict[str, Any]] = []
    arm_medians: dict[tuple[str, str, str], float] = {}
    cells: dict[tuple[str, str, int, str], float] = {}
    for row in expected_comparative:
        if row["worker_id"] in comparative_values:
            cells[(row["task"], row["regime"], int(row["block"]), row["arm"])] \
                = comparative_values[row["worker_id"]]
    for task in TASKS:
        for regime in REGIMES:
            for arm in ARMS:
                rows = [row for row in expected_comparative
                        if row["task"] == task and row["regime"] == regime
                        and row["arm"] == arm]
                values = [comparative_values[row["worker_id"]] for row in rows
                          if row["worker_id"] in comparative_values]
                failures = [row["worker_id"] for row in rows
                            if row["worker_id"] not in comparative_values]
                established = len(values) == 24 and not failures
                center = float(statistics.median(values)) if established else None
                if center is not None:
                    arm_medians[(task, regime, arm)] = center
                comparative_absolute.append({
                    "task": task, "regime": regime, "arm": arm,
                    "status": "ESTABLISHED" if established else "NOT_ESTABLISHED",
                    "successful_block_count": len(values),
                    "failure_worker_ids": failures,
                    "raw_block_duration_ns": values,
                    "median_ns": center,
                    "unconditional_publication": True,
                })
                projections = [
                    _phase_projection(comparative_by_id[row["worker_id"]], row)
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
            for ratio_index, (label, numerator, denominator) in enumerate(RATIO_ROWS):
                failed = []
                paired = []
                for block in range(1, 25):
                    n_key = (task, regime, block, numerator)
                    d_key = (task, regime, block, denominator)
                    if n_key not in cells or d_key not in cells:
                        failed.extend([
                            row["worker_id"] for row in expected_comparative
                            if row["task"] == task and row["regime"] == regime
                            and int(row["block"]) == block
                            and row["arm"] in {numerator, denominator}
                            and row["worker_id"] not in comparative_values])
                    else:
                        paired.append(cells[n_key] / cells[d_key])
                established = len(paired) == 24 and not failed
                lower = upper = point = None
                if established:
                    point = float(statistics.median(paired))
                    lower, upper = _bootstrap(
                        paired, BOOTSTRAP_SEED_BASE + 1000 * task_index
                        + 100 * regime_index + ratio_index)
                threshold = GATE[regime] if label == "RTDL_OVER_PYOPTIX" else None
                ratios.append({
                    "task": task, "regime": regime, "ratio": label,
                    "status": "ESTABLISHED" if established else "NOT_ESTABLISHED",
                    "failure_worker_ids": sorted(set(failed)),
                    "paired_block_ratios": paired,
                    "median": point, "ci95_lower": lower, "ci95_upper": upper,
                    "comparative_gate": threshold is not None,
                    "threshold": threshold,
                    "passes": (upper <= threshold) if established
                    and threshold is not None else None,
                })

    absolute_build: list[dict[str, Any]] = []
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
            center = float(statistics.median(values)) if established else None
            if center is not None:
                build_medians[(task, arm)] = center
            absolute_build.append({
                "task": task, "arm": arm,
                "status": "ESTABLISHED" if established else "NOT_ESTABLISHED",
                "successful_build_count": len(values),
                "failure_worker_ids": failures,
                "raw_duration_ns": values,
                "median_ns": center,
                "minimum_ns": min(values) if values else None,
                "maximum_ns": max(values) if values else None,
                "comparative_gate": False,
                "build_boundary": "PRE_SIGNING_PRE_DEPLOYMENT_BUILD_PRODUCT",
                "unconditional_publication": True,
            })

    amortization = []
    for task in TASKS:
        required = [
            (task, RTDL),
            (task, "DEPLOYMENT_COLD", RTDL),
            (task, "DEPLOYMENT_COLD", PYOPTIX),
            (task, "STEADY_E2E", RTDL),
            (task, "STEADY_E2E", PYOPTIX),
        ]
        established = required[0] in build_medians \
            and all(key in arm_medians for key in required[1:])
        b_r = build_medians.get((task, RTDL))
        b_p = build_medians.get((task, PYOPTIX))
        d_r = arm_medians.get((task, "DEPLOYMENT_COLD", RTDL))
        d_p = arm_medians.get((task, "DEPLOYMENT_COLD", PYOPTIX))
        s_r = arm_medians.get((task, "STEADY_E2E", RTDL))
        s_p = arm_medians.get((task, "STEADY_E2E", PYOPTIX))
        break_even: int | str | None = None
        if established:
            assert None not in (b_r, d_r, d_p, s_r, s_p)
            if s_p <= s_r:
                break_even = "NEVER"
            else:
                break_even = int(math.ceil(
                    max(0.0, b_r + d_r - d_p) / (s_p - s_r)))
        amortization.append({
            "task": task,
            "status": "ESTABLISHED" if established else "NOT_ESTABLISHED",
            "B_RTDL_ns": b_r, "B_PYOPTIX_diagnostic_ns": b_p,
            "B_PYOPTIX_excluded_from_registered_equation": True,
            "D_RTDL_ns": d_r, "D_PYOPTIX_ns": d_p,
            "S_RTDL_ns": s_r, "S_PYOPTIX_ns": s_p,
            "break_even_N": break_even,
            "registered_equation": (
                "B_RTDL + D_RTDL + N*S_RTDL <= "
                "D_PYOPTIX + N*S_PYOPTIX"),
            "scenario_assumption": (
                "one RTDL pre-signing build, one deployment, then N steady "
                "executions; PyOptiX BUILD_COLD is published but excluded by "
                "the exact Goal5799 registered equation"),
        })

    comparative_failures = list(comparative_errors)
    build_failures = list(build_errors)
    primary = [row for row in ratios if row["comparative_gate"]]
    result = {
        "schema": "rtdl.goal5802.formal_evaluation.v1",
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
        "build_cold_absolute": absolute_build,
        "build_cold_enters_comparative_gate": False,
        "amortization": amortization,
        "all_primary_noninferiority_gates_pass": (
            len(primary) == len(TASKS) * len(REGIMES)
            and all(row["status"] == "ESTABLISHED" and row["passes"] is True
                    for row in primary)),
        "retry_count": 0, "replacement_count": 0,
    }
    encoded = json.dumps(
        result, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode("utf-8")
    result["evaluation_sha256"] = hashlib.sha256(encoded).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--controller-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    freeze = _load(args.freeze)
    validate_freeze(freeze, args.root.resolve())
    controller = _load(args.controller_result)
    result = evaluate(freeze, controller)
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": result["status"], "evaluation_sha256": result["evaluation_sha256"],
        "output_sha256": _sha(args.output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
