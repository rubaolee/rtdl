from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import subprocess
import sys
from types import MappingProxyType, SimpleNamespace
import unittest
from unittest import mock

from experiments.goal5802_premeasurement import contract
from experiments.goal5802_premeasurement.build_cold_worker import (
    _recipe_argv,
    run_true_build,
)
from experiments.goal5802_premeasurement.controller import (
    OWNER_WAIVER_AUTHORITY_SCHEMA,
    OWNER_WAIVER_REASON,
    _execute_one,
    command_templates,
    local_plan,
    reject_qualification_only_trust_root_for_formal,
    validate_execution_authority,
)
from experiments.goal5802_premeasurement.direct_source_audit import (
    DirectSourceAuditError,
    audit_direct_source,
)
from experiments.goal5802_premeasurement.pyoptix_scalar_arm import (
    _ObservedCompatiblePreparedLaunch,
    DeferredRelationPrepared,
    DeviceStatusFailure,
    plan as pyoptix_plan,
    validate_scalar_execute_source,
)
from experiments.goal5802_premeasurement.python_worker import run_adapter
from experiments.goal5802_premeasurement.evaluate import evaluate
from experiments.goal5802_premeasurement.independent_recount import (
    _validate_architecture_contract_independently,
    _validate_header_projection_independently,
    _validate_direct_operation_kat_independently,
    _validate_operation_kat_independently,
    _validate_rtdl_operation_kat_independently,
    _validate_runtime_envelope_independently,
    _validate_pyoptix_header_lineage_independently,
    _validate_pyoptix_clean_install_copies_independently,
    _validate_pyoptix_wheel_build_copy_independently,
    _validate_freeze_bytes,
    recount,
)
from experiments.goal5802_premeasurement.rtdlexe_arm import (
    _plain_measurement_evidence,
    plan as rtdlexe_plan,
)
from experiments.goal5802_premeasurement.runtime_manifest import (
    HOST_RUNTIME_DISTRIBUTIONS,
    HOST_RUNTIME_MODULES,
    _current_host_projection,
    _direct_dynamic_receipt,
    _direct_operation_ledger,
    _rtdl_dynamic_receipt,
    _rtdl_k_plus_one_native_operation_receipt,
    _rtdl_native_operation_receipt,
    digest as runtime_digest,
    numba_llvmlite_runtime_authority,
    validate_direct_operation_kat,
    validate_host_runtime_provenance,
    validate_pyoptix_operation_kat,
    validate_rtdl_operation_kat,
)
from experiments.goal5802_premeasurement.successor_forecast import (
    PREDECESSOR_AUTHORITY,
    PREDECESSOR_PROBABILITIES,
    REGIMES as FORECAST_REGIMES,
    REQUIRED_CHANGE_IDS,
    SEAL_DOMAIN as FORECAST_SEAL_DOMAIN,
    SCHEMA as FORECAST_SCHEMA,
    STATUS as FORECAST_STATUS,
    THRESHOLDS as FORECAST_THRESHOLDS,
    build_successor_forecast,
)
from experiments.goal5802_premeasurement.workload import (
    RELATION_TASK,
    TRIANGLE_TASK,
    derive_relation_rows_cpu,
    relation_k_plus_one_workload,
    relation_workload,
    triangle_workload,
    workload_authority,
)
from scripts.goal5802_bind_final_clean_install import (
    _verify_goal5802_candidate_manifest,
    _verify_full_package_source,
)
from scripts.goal5802_verify_local_premeasurement_freeze import (
    verify_final_product_binding_from_evidence,
)
from scripts.goal5802_build_header_projection_untimed import (
    DependencyCommandFailure,
    RUN_ROLES as HEADER_RUN_ROLES,
    _canonical as header_canonical,
    _sha as header_sha,
    build_command_authority,
    materialize_captured_runs,
    validate_header_projection,
    validate_projection_only,
    validate_provenance,
    _write_dependency_failure,
    _write_materialization_failure,
)


ROOT = Path(__file__).resolve().parents[1]


def synthetic_k_plus_one_common(
        *, arm: str, extra: dict[str, object]) -> dict[str, object]:
    workload = relation_k_plus_one_workload()
    expected = workload["expected_failure"]
    return {
        "schema": "rtdl.goal5802.relation_k_plus_one_device_failure.v1",
        "arm": arm, "task": RELATION_TASK,
        "workload_sha256": workload["workload_sha256"],
        "packed_input_sha256": workload["packed_input_sha256"],
        "indexed_count": 1, "source_count": 4098,
        "raw_count_below_raw_capacity": True,
        "compact_control": {key: expected[key] for key in (
            "raw_event_count", "unique_event_count", "overflowed", "status",
            "semantic_capacity", "raw_capacity", "control_d2h_bytes")},
        "executed_parameter_projection": {
            "orientation_count": 2,
            "minimum_overlap_f32_bits": 0x3f800000,
            "semantic_capacity": 4096,
            "raw_capacity": 8192,
        },
        "status_output_commit_blocking_boundary_count": 1,
        "application_output_exposed": False,
        "application_output_d2h_call_count": 0,
        "application_output_d2h_bytes": 0,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        **extra,
    }


def product_binding() -> dict[str, object]:
    keys = {
        "wheel_sha256", "native_sha256", "trust_root_sha256",
        "trust_head_sha256", "trust_predecessor_package_sha256",
        "trust_package_sha256",
        "triangle_artifact_sha256", "triangle_authority_sha256",
        "triangle_executable_identity_sha256",
        "relation_artifact_sha256", "relation_authority_sha256",
        "relation_executable_identity_sha256",
        "rtdsl_package_tree_sha256", "rtdsl_init_sha256",
        "rtdlexe_module_sha256",
        "clean_install_verifier_sha256", "clean_install_run_sha256",
        "clean_install_result_sha256",
        "native_custody_verifier_sha256",
        "native_custody_manifest_sha256",
        "native_custody_custody_sha256",
    }
    result: dict[str, object] = {
        "schema": "rtdl.goal5802.final_clean_rtdlexe_binding.v4",
        "status": "PASS__FINAL_CLEAN_INSTALLED_RTLEXE",
        "clean_install_verifier_status": "PASS__INDEPENDENT_CLEAN_INSTALL_V3_VERIFICATION",
        "native_custody_verifier_status": (
            "PASS__INDEPENDENT_NATIVE_CUSTODY_VERIFICATION"),
        "native_custody_source_commit": "1" * 40,
        "native_custody_source_tree": "2" * 40,
        "native_custody_source_file_count": 997,
        "native_custody_dependency_file_count": 111,
        "native_custody_toolchain_payload_count": 13,
        "native_custody_hermetic_native_rebuild_claimed": False,
        "triangle_deployment_id": "test/triangle",
        "relation_deployment_id": "test/relation",
        "source_commit": "1" * 40,
        "source_tree": "2" * 40,
        "source_package_file_count": 293,
        "rtdsl_package_file_count": 293,
    }
    for index, key in enumerate(sorted(keys), 1):
        result[key] = f"{index:064x}"
    for key, relative in {
            "clean_install_verifier_sha256": (
                "scripts/goal5801_a3_verify_clean_install.py"),
            "native_custody_verifier_sha256": (
                "scripts/goal5801_a3_verify_native_custody.py"),
            "rtdsl_init_sha256": "src/rtdsl/__init__.py",
            "rtdlexe_module_sha256": "src/rtdsl/v4_rtdlexe.py",
            }.items():
        result[key] = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
    return result


def engineering_ledger() -> dict[str, object]:
    per_arm_files = {
        contract.ARMS[0]: [
            "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"],
        contract.ARMS[1]: [
            "experiments/goal5802_premeasurement/pyoptix_scalar_arm.py"],
        contract.ARMS[2]: [
            "src/rtdsl/v4_rtdlexe.py",
            "experiments/goal5802_premeasurement/rtdlexe_arm.py"],
    }
    return {
        "schema": "rtdl.goal5802.per_arm_engineering_effort_ledger.v1",
        "status": "FINAL_VALUES_FOR_EXACT_FREEZE",
        "goal5798_result_seen_before_successor_work": True,
        "active_minutes_are_best_effort_human_or_agent_time_not_wall_time": True,
        "engineering_time_comparability_established": False,
        "rtdl_received_approximately_one_week_product_engineering_before_baseline_successor": True,
        "baseline_successors_built_after_goal5798_result": True,
        "rows": [{
            "arm": arm,
            "engineer_or_agent": "TEST_FIXTURE_NOT_A_FORMAL_LEDGER",
            "start_utc": None,
            "stop_utc": None,
            "active_minutes": None,
            "files_changed": files,
            "purpose": (
                "Historical test fixture; time was not instrumented and is not estimated"),
            "result_seen_before_change": True,
            "evidence_kind": "HISTORICAL_UNINSTRUMENTED__UNKNOWN_NOT_ESTIMATED",
        } for arm, files in per_arm_files.items()],
    }


def successor_forecast(
        binding: dict[str, object] | None = None) -> dict[str, object]:
    """Build the explicit manual v2 forecast used by freeze-path tests."""

    final_binding = product_binding() if binding is None else binding
    identity = contract.successor_forecast_identity_binding(
        ROOT, final_binding)
    primary = []
    for index, (task, regime) in enumerate(
            (pair for task in contract.TASKS for pair in
             ((task, regime) for regime in FORECAST_REGIMES))):
        threshold = FORECAST_THRESHOLDS[regime]
        primary.append({
            "task": task,
            "regime": regime,
            "gate": f"CI_UPPER_LE_{threshold:.2f}",
            "noninferiority_threshold": threshold,
            "predicted_median_interval": [
                0.90 + index / 100, 1.10 + index / 100],
            "predicted_95_percent_ci_upper_interval": [
                1.00, 1.20 + index / 100],
            "subjective_gate_pass_probability": 0.41 + index / 100,
            "predecessor_subjective_gate_pass_probability": (
                PREDECESSOR_PROBABILITIES[(task, regime)]),
            "manual_successor_probability_entry": True,
            "probability_copied_or_defaulted_from_predecessor": False,
            "change_reason_ids": list(REQUIRED_CHANGE_IDS),
        })
    joint = {
        "all_six_gates_pass_probability_interval": [0.10, 0.22],
        "predecessor_all_six_gates_pass_probability_interval": [0.25, 0.40],
        "manual_successor_probability_entry": True,
        "probability_copied_or_defaulted_from_predecessor": False,
        "independence_assumed": False,
        "highest_risk_regime": "DEPLOYMENT_COLD",
        "change_reason_ids": list(REQUIRED_CHANGE_IDS),
    }
    direct = [{
        "task": task,
        "regime": "STEADY_E2E",
        "metric": "PYOPTIX_OVER_DIRECT",
        "predicted_median_interval": interval,
        "manual_interval_entry": True,
        "change_reason_ids": list(REQUIRED_CHANGE_IDS),
    } for task, interval in (
        (RELATION_TASK, [4.5, 6.5]),
        (TRIANGLE_TASK, [8.0, 13.0]),
    )]
    return build_successor_forecast(
        identity_binding=identity,
        operation_contract=contract.operation_contract(),
        primary_predictions=primary,
        joint_prediction=joint,
        direct_context_predictions=direct,
    )


def reseal_successor_forecast(freeze: dict[str, object]) -> None:
    forecast = freeze["successor_subjective_forecast"]
    assert isinstance(forecast, dict)
    unsigned_forecast = dict(forecast)
    unsigned_forecast.pop("forecast_sha256")
    forecast["forecast_sha256"] = hashlib.sha256(
        FORECAST_SEAL_DOMAIN + b"\0"
        + contract.canonical(unsigned_forecast)).hexdigest()


def reseal_freeze(freeze: dict[str, object]) -> None:
    unsigned = dict(freeze)
    unsigned.pop("freeze_sha256")
    freeze["freeze_sha256"] = contract.digest(unsigned)


def synthetic_pyoptix_operation_kat() \
        -> tuple[dict[str, object], dict[str, object]]:
    files: dict[str, object] = {
        "pyoptix_initializer": {
            "path": "/synthetic/optix/__init__.py", "sha256": "1" * 64},
        "pyoptix_extension": {
            "path": "/synthetic/optix/_optix.so", "sha256": "2" * 64},
        "matched_ptx": {
            "path": "/synthetic/matched.ptx", "sha256": "3" * 64},
        "compaction_cubin": {
            "path": "/synthetic/relation_compaction.cubin",
            "sha256": "4" * 64},
    }
    keys = (
        "prepare_device_allocation_call_count", "prepare_h2d_call_count",
        "prepare_pinned_host_allocation_call_count",
        "prepare_stream_creation_count", "execute_device_allocation_call_count",
        "execute_pinned_host_allocation_call_count",
        "execute_async_h2d_call_count", "execute_async_d2h_call_count",
        "execute_blocking_d2h_call_count",
        "execute_device_zero_fill_call_count",
        "execute_explicit_stream_sync_call_count", "execute_launch_call_count",
        "execute_stream_creation_call_count", "execute_stream_destroy_call_count",
    )

    def counts(**nonzero):
        result = {key: 0 for key in keys}
        result.update(nonzero)
        return result

    guard = {
        "scope": "PYTHON_VISIBLE_TASK_OWNER_EXECUTE__NOT_CUPTI_OR_DRIVER_WIDE",
        "unapproved_device_allocation_call_count": 0,
        "unapproved_pinned_host_allocation_call_count": 0,
        "unapproved_blocking_asnumpy_call_count": 0,
        "unauthorized_direct_stream_sync_count": 0,
        "complete_driver_operation_observation_claimed": False,
    }
    specs = {
        RELATION_TASK: {
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
        TRIANGLE_TASK: {
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
    identity = {
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
    rows = []
    for task, spec in specs.items():
        projections = {}
        for name, reused in (("first_execute", False), ("reused_execute", True)):
            projections[name] = {
                "independent_execute_guard": guard,
                "dynamic_input_receipt": {
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
                },
                "execute_operation_counts": spec["execute"],
                "operation_order": spec["order"],
                "prepare_operation_counts": spec["prepare"],
                "live_execute_guard_inside_timer": True,
            }
        task_identity = dict(identity)
        if task == RELATION_TASK:
            task_identity.update({
                "compaction_cubin_path": files["compaction_cubin"]["path"],
                "compaction_cubin_sha256": files["compaction_cubin"]["sha256"],
                "retained_compaction_cubin_sha256": files[
                    "compaction_cubin"]["sha256"],
            })
        rows.append({
            "task": task, **projections, "runtime_identity": task_identity})
    hostile = synthetic_k_plus_one_common(
        arm=contract.ARMS[1], extra={
            "operation_order": [
                "control_reset", "max_key_reset", "unique_count_reset",
                "keys_fill_ff", "params0_h2d", "launch0", "params1_h2d",
                "launch1", "semantic_compaction", "unique_count_d2d",
                "control_d2h", "status_ready_sync"],
            "execute_operation_counts": counts(
                execute_async_h2d_call_count=2,
                execute_async_d2h_call_count=1,
                execute_device_zero_fill_call_count=4,
                execute_explicit_stream_sync_call_count=1,
                execute_launch_call_count=3),
            "independent_execute_guard": guard,
            "dynamic_input_receipt": {
                "prepared_input_reused": False,
                "dynamic_device_upload_call_count": 2,
                "dynamic_device_upload_bytes": 213096,
                "dynamic_accel_build_count": 1,
                "dynamic_explicit_sync_count": 0,
                "dynamic_blocking_upload_call_count": 0,
                "dynamic_input_generation": 1,
            },
        })
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.pyoptix_operation_guard_untimed_kat.v1",
        "status": "PASS__UNTIMED_PREWORKER_OPERATION_GUARD",
        "rows": rows,
        "task_count": 2,
        "guard_inside_comparative_timer": False,
        "source_boundary": validate_scalar_execute_source(),
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "untimed_optix_launch_count": 8,
        "untimed_auxiliary_cuda_kernel_launch_count": 3,
        "untimed_gpu_launch_count": 11,
        "relation_k_plus_one_hostile": hostile,
    }
    value["receipt_sha256"] = runtime_digest(value)
    return value, files


def synthetic_direct_operation_kat() \
        -> tuple[dict[str, object], dict[str, object]]:
    source = ROOT / "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"
    files: dict[str, object] = {
        "direct_scalar_worker": {
            "path": "/synthetic/direct_scalar_worker", "sha256": "a" * 64},
        "direct_scalar_source": {
            "path": str(source),
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest()},
        "matched_ptx": {
            "path": "/synthetic/matched.ptx", "sha256": "b" * 64},
        "compaction_cubin": {
            "path": "/synthetic/relation_compaction.cubin",
            "sha256": "c" * 64},
    }
    hostile_trace = {
        "optix_launch_count": 2, "compaction_launch_count": 1,
        "async_h2d_call_count": 2, "async_h2d_bytes": 240,
        "async_d2h_call_count": 1, "async_d2h_bytes": 16,
        "async_d2d_call_count": 1, "async_d2d_bytes": 4,
        "host_blocking_boundary_count": 1,
    }
    hostile_dynamic = {
        "prepared_input_reused": False,
        "dynamic_device_upload_call_count": 2,
        "dynamic_device_upload_bytes": 213096,
        "dynamic_accel_build_count": 1,
        "dynamic_explicit_sync_count": 0,
        "dynamic_blocking_upload_call_count": 0,
        "dynamic_input_generation": 1,
    }
    hostile = synthetic_k_plus_one_common(
        arm=contract.ARMS[0], extra={
            "observed_operation_trace": hostile_trace,
            "dynamic_input_receipt": hostile_dynamic,
        })
    worker_hostile = {
        key: item for key, item in hostile.items() if key not in {
            "arm", "workload_sha256",
            "registered_performance_timing_count", "formal_worker_count"}}
    rows = []
    for task in (RELATION_TASK, TRIANGLE_TASK):
        relation = task == RELATION_TASK
        lifecycle = [
            _direct_dynamic_receipt(relation=relation, reused=False),
            _direct_dynamic_receipt(relation=relation, reused=True),
        ]
        trace = {
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
        worker: dict[str, object] = {
            "schema": "rtdl.goal5802.direct_scalar.worker.v1",
            "status": "PASS", "arm": contract.ARMS[0],
            "worker_id": "", "freeze_file_sha256": "",
            "execution_authority_sha256": "", "runtime_manifest_sha256": "",
            "task": task, "regime": "LOCAL_UNTIMED",
            "registered_performance_timing_count": 0,
            "phase_durations_ns": {
                "process_startup_and_admission": None,
                "input_materialization": None, "load_or_deploy": None,
                "prepare": None, "steady_warmups": None,
                "complete_execute": None,
                "measurement_evidence_materialization": None,
                "close": None, "post_execution_identity_validation": None,
            },
            "execute_or_regime_durations_ns": [],
            "execution_lifecycle_receipts": lifecycle,
            "untimed_observed_operation_traces": [trace, trace],
            "correctness": ({
                "oracle_exact": True, "canonical_row_count": 4096,
                "canonical_rows": [[index, index] for index in range(4096)],
                "raw_event_count": 8192, "semantic_unique_count": 4096,
                "device_status": 0, "device_overflow": 0,
            } if relation else {
                "oracle_exact": True, "device_status": 0,
                "reduced_u64": 65530}),
            "operation_ledger": _direct_operation_ledger(relation=relation),
            "receipt_serialization_inside_timer": False,
            "retained_executed_ptx_sha256": files["matched_ptx"]["sha256"],
            "close_inside_primary_timer": False,
        }
        if relation:
            worker["retained_compaction_cubin_sha256"] = files[
                "compaction_cubin"]["sha256"]
            worker["relation_k_plus_one_hostile"] = worker_hostile
        stdout = json.dumps(
            worker, sort_keys=True, separators=(",", ":")) + "\n"
        command = [
            files["direct_scalar_worker"]["path"],
            "--local-untimed-functional", "--task", task,
            "--ptx", files["matched_ptx"]["path"],
        ]
        if relation:
            command.extend([
                "--compaction-cubin", files["compaction_cubin"]["path"]])
        rows.append({
            "task": task, "command": command, "exit_code": 0,
            "stdout_utf8": stdout,
            "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
            "stderr_utf8": "",
            "stderr_sha256": hashlib.sha256(b"").hexdigest(),
            "worker_receipt": worker,
        })
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.direct_operation_guard_untimed_kat.v1",
        "status": "PASS__UNTIMED_PREWORKER_ACTUAL_DIRECT_OPERATION_GUARD",
        "rows": rows, "task_count": 2,
        "guard_inside_comparative_timer": False,
        "source_audit": audit_direct_source(source),
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "untimed_optix_launch_count": 8,
        "untimed_auxiliary_cuda_kernel_launch_count": 3,
        "untimed_gpu_launch_count": 11,
        "relation_k_plus_one_hostile": hostile,
    }
    value["receipt_sha256"] = runtime_digest(value)
    return value, files


def synthetic_rtdl_operation_kat() \
        -> tuple[dict[str, object], dict[str, object],
                 dict[str, str], dict[str, str]]:
    files: dict[str, object] = {}
    for index, role in enumerate((
            "relation_artifact", "relation_authority",
            "triangle_artifact", "triangle_authority",
            "trust_root", "trust_head", "trust_package", "native_library",
            "rtdsl_init", "rtdlexe_module"), 1):
        files[role] = {
            "path": f"/synthetic/{role}",
            "sha256": f"{index:064x}",
        }
    deployment_ids = {
        "relation": "goal5802/test/relation",
        "triangle": "goal5802/test/triangle",
    }
    executable_ids = {"relation": "d" * 64, "triangle": "e" * 64}
    rows = []
    for task in (RELATION_TASK, TRIANGLE_TASK):
        key = "relation" if task == RELATION_TASK else "triangle"
        projections = {}
        for name, reused in (("first_execute", False),
                             ("reused_execute", True)):
            projections[name] = {
                "dynamic_input_receipt": _rtdl_dynamic_receipt(
                    task=task, reused=reused),
                "native_operation_receipt": _rtdl_native_operation_receipt(
                    task=task, reused=reused),
                "output_canonical_sha256": (
                    runtime_digest([[index, index] for index in range(4096)])
                    if task == RELATION_TASK else runtime_digest(65530)),
                "product_output_sha256": None,
                "executable_identity_sha256": executable_ids[key],
                "oracle_exact": True,
                "device_status_ok": True,
                "output_summary": ({
                    "canonical_row_count": 4096,
                    "raw_event_count": 8192,
                    "semantic_unique_count": 4096,
                } if task == RELATION_TASK else {"reduced_u64": 65530}),
                "role_counters": [],
            }
        rows.append({
            "task": task,
            "deployment_identity": {
                "artifact_sha256": files[f"{key}_artifact"]["sha256"],
                "authority_sha256": files[f"{key}_authority"]["sha256"],
                "trust_root_sha256": files["trust_root"]["sha256"],
                "trust_head_sha256": files["trust_head"]["sha256"],
                "trust_package_sha256": files["trust_package"]["sha256"],
                "native_sha256": files["native_library"]["sha256"],
                "deployment_id": deployment_ids[key],
            },
            "runtime_identity": {
                "rtdsl_init_path": files["rtdsl_init"]["path"],
                "rtdsl_init_sha256": files["rtdsl_init"]["sha256"],
                "rtdlexe_module_path": files["rtdlexe_module"]["path"],
                "rtdlexe_module_sha256": files["rtdlexe_module"]["sha256"],
                "executed_executable_identity_sha256": executable_ids[key],
            },
            **projections,
        })
    hostile = synthetic_k_plus_one_common(
        arm=contract.ARMS[2], extra={
            "product_compact_control": {
                "schema": "rtdl.v4.rtdlexe.relation_compact_control.v1",
                "raw_event_count": 4097, "unique_event_count": 4097,
                "overflowed": 1, "status": 0xffff5102,
                "semantic_capacity": 4096, "control_d2h_bytes": 16,
            },
            "failure_code": "RX035_DEVICE_STATUS_INVALID",
            "native_operation_receipt": (
                _rtdl_k_plus_one_native_operation_receipt()),
            "deployment_identity": rows[0]["deployment_identity"],
        })
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.rtdl_operation_guard_untimed_kat.v1",
        "status": "PASS__UNTIMED_PREWORKER_ACTUAL_RTDL_OPERATION_GUARD",
        "rows": rows, "task_count": 2,
        "guard_inside_comparative_timer": False,
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "untimed_optix_launch_count": 8,
        "untimed_auxiliary_cuda_kernel_launch_count": 33,
        "untimed_gpu_launch_count": 41,
        "relation_k_plus_one_hostile": hostile,
    }
    value["receipt_sha256"] = runtime_digest(value)
    return value, files, deployment_ids, executable_ids


class FakeAdapter:
    def __init__(self):
        self.events: list[str] = []
        self.executions = 0

    def load(self):
        self.events.append("load")

    def prepare(self):
        self.events.append("prepare")

    def execute(self):
        self.events.append("execute")
        self.executions += 1
        reused = self.executions > 1
        return {
            "device_status": 0,
            "reduced_u64": 65530,
            "per_ray_d2h_bytes": 0,
            "dynamic_input_receipt": {
                "prepared_input_reused": reused,
                "dynamic_device_upload_call_count": 0 if reused else 1,
                "dynamic_device_upload_bytes": 0 if reused else 1,
                "dynamic_accel_build_count": 0,
                "dynamic_explicit_sync_count": 0,
                "dynamic_input_generation": 1,
            },
        }

    def close(self):
        self.events.append("close")


class CounterClock:
    def __init__(self):
        self.value = 0

    def __call__(self):
        self.value += 10
        return self.value


class Goal5802LocalPremeasurementTest(unittest.TestCase):
    def test_rtdlexe_measurement_evidence_materializes_nested_readonly_views(self):
        observed = _plain_measurement_evidence({
            "status": MappingProxyType({
                "operation_receipt": MappingProxyType({"launches": 1}),
            }),
            "rows": (MappingProxyType({"value": 2}),),
        })
        self.assertEqual(observed, {
            "status": {"operation_receipt": {"launches": 1}},
            "rows": ({"value": 2},),
        })
        json.dumps(observed)

    def test_formal_controller_rejects_home_qualification_trust_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            qualification_root = root / "qualification.json"
            qualification_root.write_text(json.dumps({
                "key_id": (
                    "TEST_ONLY_goal5802_final_home_qualification_unit"),
            }), encoding="utf-8")
            with self.assertRaisesRegex(
                    RuntimeError, "qualification-only trust root"):
                reject_qualification_only_trust_root_for_formal(
                    qualification_root)

            formal_root = root / "formal.json"
            formal_root.write_text(json.dumps({
                "key_id": "TEST_ONLY_goal5802_rtx_measurement_root_v5_20260826",
            }), encoding="utf-8")
            reject_qualification_only_trust_root_for_formal(formal_root)

    def test_goal5802_forbids_legacy_or_mismatched_relation_candidate(self):
        current = {
            "schema": "rtdl.goal5801.lx1_untimed_candidate_manifest.v2",
            "relation_protocol": {
                "capacity": 4096,
                "minimum_overlap_boundary": "inclusive",
                "minimum_overlap_f32": 1.0,
                "minimum_overlap_f32_bits": 0x3F800000,
            },
        }
        _verify_goal5802_candidate_manifest(current)
        for hostile in (
                {**current, "schema": (
                    "rtdl.goal5801.lx1_untimed_candidate_manifest.v1")},
                {**current, "relation_protocol": {
                    **current["relation_protocol"],
                    "minimum_overlap_f32": 0.0,
                    "minimum_overlap_f32_bits": 0,
                }},
                {**current, "relation_protocol": {
                    **current["relation_protocol"], "capacity": 4095,
                }},
                {**current, "relation_protocol": {
                    **current["relation_protocol"],
                    "minimum_overlap_f32": True,
                }}):
            with self.assertRaises(RuntimeError):
                _verify_goal5802_candidate_manifest(hostile)

    def test_observed_sync_labels_match_each_task_contract(self):
        class FakePreparedLaunch:
            def __init__(self, _pipeline, _sbt, *, operation_counts):
                self.operation_counts = operation_counts
                self.execution_events = []

            def synchronize(self, *, event):
                self.execution_events.append(event)

        baseline = SimpleNamespace(PreparedLaunch=FakePreparedLaunch)
        for kind, expected in (
                ("relation", ["status_ready_sync", "output_ready_sync"]),
                ("triangle", ["status_ready_sync", "scalar_ready_sync"])):
            with self.subTest(kind=kind):
                launcher = _ObservedCompatiblePreparedLaunch(
                    baseline, object(), object(), kind=kind,
                    operation_counts={})
                launcher.synchronize()
                launcher.synchronize()
                self.assertEqual(launcher.execution_events, expected)

    def test_clean_binding_proves_every_saved_package_file_against_git(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = root / "repository"
            source = repository / "src/rtdsl"
            source.mkdir(parents=True)
            (source / "a.py").write_bytes(b"A\n")
            (source / "b.py").write_bytes(b"B\n")
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            subprocess.run([
                "git", "-C", str(repository), "-c", "core.autocrlf=false",
                "add", "."], check=True)
            subprocess.run([
                "git", "-C", str(repository), "-c", "user.name=Goal5802 Test",
                "-c", "user.email=goal5802@example.invalid", "commit", "-qm",
                "fixture"], check=True)
            commit = subprocess.run([
                "git", "-C", str(repository), "rev-parse", "HEAD"],
                check=True, capture_output=True, text=True).stdout.strip()
            tree = subprocess.run([
                "git", "-C", str(repository), "rev-parse", "HEAD^{tree}"],
                check=True, capture_output=True, text=True).stdout.strip()
            clean = root / "clean"
            saved = clean / "saved"
            saved.mkdir(parents=True)
            rows = []
            for name in ("a.py", "b.py"):
                payload = (source / name).read_bytes()
                (saved / name).write_bytes(payload)
                rows.append({
                    "role": f"source_package/{name}",
                    "saved_path": f"saved/{name}",
                    "sha256": hashlib.sha256(payload).hexdigest(),
                })
            self.assertEqual(_verify_full_package_source(
                repository, commit, tree, clean, rows), 2)
            (saved / "a.py").write_bytes(b"tampered\n")
            with self.assertRaises(RuntimeError):
                _verify_full_package_source(
                    repository, commit, tree, clean, rows)

    def test_product_binding_requires_exact_native_custody_projection_schema(self):
        valid = product_binding()
        contract._validate_product_binding(valid)
        contract._validate_product_binding(valid, ROOT)
        for label, mutate in (
                ("retired schema", lambda value: value.update({
                    "schema": "rtdl.goal5802.final_clean_rtdlexe_binding.v1"})),
                ("stale native source tree", lambda value: value.update({
                    "native_custody_source_tree": "3" * 40})),
                ("bool source count", lambda value: value.update({
                    "native_custody_source_file_count": True})),
                ("unsupported hermetic claim", lambda value: value.update({
                    "native_custody_hermetic_native_rebuild_claimed": True}))):
            with self.subTest(label=label):
                changed = copy.deepcopy(valid)
                mutate(changed)
                with self.assertRaises(contract.ContractError):
                    contract._validate_product_binding(changed)
        for key in (
                "clean_install_verifier_sha256",
                "native_custody_verifier_sha256",
                "rtdsl_init_sha256", "rtdlexe_module_sha256"):
            changed = copy.deepcopy(valid)
            changed[key] = "f" * 64
            with self.subTest(cross_binding=key):
                with self.assertRaisesRegex(
                        contract.ContractError, "source cross-binding"):
                    contract._validate_product_binding(changed, ROOT)

    def test_final_freeze_entrypoint_rebuilds_complete_product_binding(self):
        valid = product_binding()
        with mock.patch(
                "scripts.goal5802_verify_local_premeasurement_freeze."
                "final_binder.build_binding",
                return_value=copy.deepcopy(valid)):
            rebuilt = verify_final_product_binding_from_evidence(
                valid, clean_install_root=Path("/clean"),
                repository_root=ROOT,
                standalone_clean_verifier=Path("/clean-verifier"),
                native_custody_root=Path("/custody"),
                standalone_native_custody_verifier=Path("/custody-verifier"))
        self.assertEqual(rebuilt, valid)
        hostile = copy.deepcopy(valid)
        hostile["trust_package_sha256"] = "f" * 64
        with mock.patch(
                "scripts.goal5802_verify_local_premeasurement_freeze."
                "final_binder.build_binding", return_value=hostile), \
                self.assertRaisesRegex(
                    RuntimeError, "differs from evidence rebuild"):
            verify_final_product_binding_from_evidence(
                valid, clean_install_root=Path("/clean"),
                repository_root=ROOT,
                standalone_clean_verifier=Path("/clean-verifier"),
                native_custody_root=Path("/custody"),
                standalone_native_custody_verifier=Path("/custody-verifier"))

    def test_all_three_build_routes_bind_nested_cuda_include(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "recipe.json"
            completed = subprocess.run([
                sys.executable,
                str(ROOT / "scripts/goal5802_build_direct_recipe.py"),
                "--output", str(output),
            ], check=False, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            recipe = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(
                recipe["schema"], "rtdl.goal5802.direct_build_recipe.v2")
            runtime = {
                "files": {
                    "cxx_compiler": {"path": "/tool/cxx"},
                    "direct_scalar_source": {"path": "/source/direct.cpp"},
                },
                "directories": {
                    "optix_include": {"path": "/sdk/optix/include"},
                    "cuda_include": {"path": "/sdk/cuda/include"},
                },
            }
            argv = _recipe_argv(
                recipe, runtime=runtime, output_binary=Path("/out/direct"))
            self.assertEqual(argv.count("-I/sdk/cuda/include/nv"), 1)
            hostile = copy.deepcopy(recipe)
            hostile["argv_template"].insert(-5, "-DRESULT_DIRECTED_REWRITE=1")
            hostile.pop("recipe_sha256")
            hostile["recipe_sha256"] = hashlib.sha256(json.dumps(
                hostile, sort_keys=True, separators=(",", ":"),
                allow_nan=False).encode("utf-8")).hexdigest()
            with self.assertRaisesRegex(RuntimeError, "compile-option grammar"):
                _recipe_argv(
                    hostile, runtime=runtime,
                    output_binary=Path("/out/direct"))

            forbidden_cli = subprocess.run([
                sys.executable,
                str(ROOT / "scripts/goal5802_build_direct_recipe.py"),
                "--extra-argument=-DRESULT_DIRECTED_REWRITE=1",
                "--output", str(Path(temporary) / "forbidden.json"),
            ], check=False, capture_output=True, text=True)
            self.assertNotEqual(forbidden_cli.returncode, 0)
        expected_source = "f\"-I{Path(cuda_include).resolve() / 'nv'}\""
        for relative in (
                "src/rtdsl/v4_bounded_relation_optix_compiler.py",
                "src/rtdsl/v4_triangle_reduction_optix_compiler.py"):
            source = (ROOT / relative).read_text(encoding="utf-8")
            self.assertEqual(source.count(expected_source), 1, relative)

    def test_triangle_authority_is_scalar_only(self):
        task = triangle_workload()
        authority = workload_authority()
        self.assertEqual(task["expected_reduced_u64"], 65530)
        self.assertNotIn("expected_per_ray", task)
        self.assertFalse(authority["triangle"]["expected_per_ray_field_present"])
        output = authority["user_visible_output_contract"][TRIANGLE_TASK]
        self.assertFalse(output["per_ray_host_output"])
        self.assertEqual(output["per_ray_d2h_bytes"], 0)

    def test_schedule_is_complete_balanced_and_deterministic(self):
        first = contract.build_schedule()
        second = contract.build_schedule()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 432)
        self.assertEqual(
            [row["ordinal"] for row in first], list(range(1, 433)))
        for task in contract.TASKS:
            for regime in contract.REGIMES:
                rows = [row for row in first
                        if row["task"] == task and row["regime"] == regime]
                self.assertEqual(len(rows), 72)
                for arm in contract.ARMS:
                    self.assertEqual(sum(row["arm"] == arm for row in rows), 24)
                    for position in (1, 2, 3):
                        self.assertEqual(sum(
                            row["arm"] == arm and row["position"] == position
                            for row in rows), 8)
        build = contract.build_cold_schedule()
        self.assertEqual(len(build), 72)
        for task in contract.TASKS:
            rows = [row for row in build if row["task"] == task]
            self.assertEqual(len(rows), 36)
            for arm in contract.ARMS:
                self.assertEqual(sum(row["arm"] == arm for row in rows), 12)
                for position in (1, 2, 3):
                    self.assertEqual(sum(
                        row["arm"] == arm and row["position"] == position
                        for row in rows), 4)

    def test_operation_contract_requires_exact_three_arm_dynamic_work(self):
        value = contract.operation_contract()
        triangle = value["triangle"]
        self.assertEqual(len({
            json.dumps(triangle[arm], sort_keys=True) for arm in contract.ARMS
        }), 1)
        self.assertEqual(triangle[contract.ARMS[2]][
            "total_success_d2h_bytes"], 12)
        self.assertEqual(triangle[contract.ARMS[2]][
            "status_output_commit_blocking_boundary_count"], 2)
        relation = value["relation"]
        self.assertEqual(len({
            json.dumps(relation[arm], sort_keys=True) for arm in contract.ARMS
        }), 1)
        self.assertEqual(relation["D_RTDL_CLEAN_INSTALLED_RTLEXE"][
            "total_success_d2h_bytes"], 32784)
        self.assertEqual(relation["D_RTDL_CLEAN_INSTALLED_RTLEXE"][
            "status_output_commit_blocking_boundary_count"], 2)
        self.assertFalse(value["synchronization_ruling"][
            "raw_host_blocking_boundary_counts_claimed_equal"])
        self.assertTrue(value["synchronization_ruling"][
            "goal5799_same_sync_counts_literal_narrowed"])
        self.assertFalse(value["synchronization_ruling"][
            "baseline_padding_to_match_rtdl_allowed"])
        lifecycle = value["dynamic_input_lifecycle"]
        self.assertTrue(lifecycle[
            "dynamic_host_batch_materialized_and_retained_during_prepare"])
        self.assertTrue(lifecycle[
            "dynamic_device_representation_absent_at_prepare_return"])
        self.assertTrue(lifecycle[
            "dynamic_device_upload_and_dynamic_gas_first_execute"])
        self.assertNotIn(
            "dynamic_batch_first_enters_owner_on_execute", lifecycle)

    def test_pyoptix_scalar_source_has_no_per_ray_host_materialization(self):
        value = pyoptix_plan()
        self.assertEqual(value["source_boundary"][
            "per_ray_host_materialization_count"], 0)
        self.assertEqual(value["source_boundary"]["launcher_call_shape"], {
            "zero_on_stream": 1,
            "enqueue": 1,
            "enqueue_d2h": 2,
            "synchronize": 2,
        })
        self.assertFalse(value["output"]["per_ray_host_output"])
        self.assertTrue(value["comparative_load_uses_prebuilt_ptx"])
        self.assertFalse(value["comparative_load_invokes_nvrtc"])

    def test_pyoptix_timed_path_uses_label_free_fast_core(self):
        boundary = validate_scalar_execute_source()
        for shape in boundary["live_guard_shape"].values():
            self.assertEqual(shape, {
                "timed_observer_count": 0,
                "untimed_kat_observer_count": 1,
                "timed_fast_core_call_count": 1,
                "timed_observed_core_call_count": 0,
                "untimed_observed_core_call_count": 1,
                "observed_wrapper_common_fast_core_call_count": 1,
                "timed_event_reset_count": 0,
            })
        self.assertEqual(boundary["formal_measurement_label_count"], 0)
        self.assertTrue(boundary["dynamic_helper_shape"]
                        ["copy_uses_owned_raw_stream"])
        self.assertEqual(boundary["dynamic_materialization_shape"]
                         ["ScalarTrianglePrepared"]["calls"]
                         ["_enqueue_pinned_dynamic_h2d"], 2)
        source = ROOT / "experiments/goal5802_premeasurement/pyoptix_scalar_arm.py"
        with tempfile.TemporaryDirectory() as temporary:
            tampered = Path(temporary) / "pyoptix_scalar_arm.py"
            tampered.write_text(
                source.read_text(encoding="utf-8").replace(
                    "        return self._execute_fast(reused=reused)\n",
                    "        self.launcher.begin_execution()\n"
                    "        return self._execute_fast(reused=reused)\n", 1),
                encoding="utf-8")
            with self.assertRaises(RuntimeError):
                validate_scalar_execute_source(tampered)
            third_copy = Path(temporary) / "pyoptix_scalar_arm_third_copy.py"
            call = (
                "        self.d_weights = _enqueue_pinned_dynamic_h2d(\n"
                "            self.b, self.launcher, self.h_dynamic_weights, trace)\n")
            third_copy.write_text(
                source.read_text(encoding="utf-8").replace(call, call + call, 1),
                encoding="utf-8")
            with self.assertRaises(RuntimeError):
                validate_scalar_execute_source(third_copy)
            pointer_stream = Path(temporary) / "pyoptix_scalar_arm_pointer.py"
            pointer_stream.write_text(
                source.read_text(encoding="utf-8").replace(
                    "        raw_stream)\n", "        int(launcher.stream.ptr))\n",
                    1),
                encoding="utf-8")
            with self.assertRaises(RuntimeError):
                validate_scalar_execute_source(pointer_stream)
            fixture_shadow = Path(temporary) / "pyoptix_scalar_arm_fixture_shadow.py"
            fixture_shadow.write_text(
                source.read_text(encoding="utf-8").replace(
                    "        reused, _ = self._materialize_dynamic_input()\n",
                    "        self.fixture[\"minimum_overlap\"] = 0.0\n"
                    "        reused, _ = self._materialize_dynamic_input()\n",
                    1),
                encoding="utf-8")
            with self.assertRaises(RuntimeError):
                validate_scalar_execute_source(fixture_shadow)
            parameter_shadow = Path(temporary) / "pyoptix_scalar_arm_param_shadow.py"
            parameter_shadow.write_text(
                source.read_text(encoding="utf-8").replace(
                    "            launches.append((params, len(query_host)))\n",
                    "            params[0][\"minimum_overlap\"] = "
                    "self.b.np.float32(0.0)\n"
                    "            launches.append((params, len(query_host)))\n",
                    1),
                encoding="utf-8")
            with self.assertRaises(RuntimeError):
                validate_scalar_execute_source(parameter_shadow)

    def test_pyoptix_operation_kat_uses_relation_only_compaction_cubin(self):
        source = (ROOT / "scripts" /
                  "goal5802_run_pyoptix_operation_kat_untimed.py").read_text(
                      encoding="utf-8")
        self.assertIn(
            "args.compaction_cubin if task == RELATION_TASK else None",
            source)
        self.assertNotIn(
            "compaction_cubin_path=args.compaction_cubin,", source)

    def test_pyoptix_operation_kat_exact_schema_rejects_resealed_weakening(self):
        value, files = synthetic_pyoptix_operation_kat()
        validate_pyoptix_operation_kat(
            value, files,
            expected_source_sha256=value["source_boundary"]["source_sha256"])
        _validate_operation_kat_independently(
            value, files,
            expected_source_sha256=value["source_boundary"]["source_sha256"])
        for mutation in (
                "observer", "blocking_upload", "source",
                "pre_k_plus_one_launch_envelope"):
            tampered = copy.deepcopy(value)
            if mutation == "observer":
                tampered["rows"][0]["first_execute"][
                    "independent_execute_guard"][
                        "complete_driver_operation_observation_claimed"] = True
            elif mutation == "blocking_upload":
                tampered["rows"][0]["first_execute"][
                    "dynamic_input_receipt"][
                        "dynamic_blocking_upload_call_count"] = 1
            else:
                if mutation == "source":
                    tampered["source_boundary"]["source_sha256"] = "f" * 64
                else:
                    tampered["untimed_optix_launch_count"] = 6
                    tampered[
                        "untimed_auxiliary_cuda_kernel_launch_count"] = 2
                    tampered["untimed_gpu_launch_count"] = 8
            tampered.pop("receipt_sha256")
            tampered["receipt_sha256"] = runtime_digest(tampered)
            with self.assertRaises(RuntimeError, msg=mutation):
                validate_pyoptix_operation_kat(
                    tampered, files,
                    expected_source_sha256=value[
                        "source_boundary"]["source_sha256"])
            with self.assertRaises(RuntimeError, msg=f"independent-{mutation}"):
                _validate_operation_kat_independently(
                    tampered, files,
                    expected_source_sha256=value[
                        "source_boundary"]["source_sha256"])

    def test_target_manifest_uses_complete_post_k_plus_one_pyoptix_validator(self):
        source = (ROOT / "scripts" /
                  "goal5802_build_target_runtime_manifest.py").read_text(
                      encoding="utf-8")
        self.assertIn(
            "validate_pyoptix_operation_kat(operation_kat, files)", source)
        self.assertNotIn(
            'operation_kat.get("untimed_optix_launch_count") != 6', source)
        self.assertNotIn(
            '"untimed_auxiliary_cuda_kernel_launch_count") != 2', source)
        self.assertNotIn(
            'operation_kat.get("untimed_gpu_launch_count") != 8', source)

    def test_direct_operation_kat_recounts_actual_first_and_reuse_traces(self):
        value, files = synthetic_direct_operation_kat()
        validate_direct_operation_kat(value, files)
        _validate_direct_operation_kat_independently(value, files)
        for mutation in ("actual_trace", "reuse", "source_wrapper"):
            tampered = copy.deepcopy(value)
            if mutation == "actual_trace":
                worker = tampered["rows"][0]["worker_receipt"]
                worker["untimed_observed_operation_traces"][1][
                    "host_blocking_boundary_count"] = 1
                stdout = json.dumps(
                    worker, sort_keys=True, separators=(",", ":")) + "\n"
                tampered["rows"][0]["stdout_utf8"] = stdout
                tampered["rows"][0]["stdout_sha256"] = hashlib.sha256(
                    stdout.encode()).hexdigest()
            elif mutation == "reuse":
                worker = tampered["rows"][0]["worker_receipt"]
                worker["execution_lifecycle_receipts"][1][
                    "dynamic_device_upload_call_count"] = 1
                stdout = json.dumps(
                    worker, sort_keys=True, separators=(",", ":")) + "\n"
                tampered["rows"][0]["stdout_utf8"] = stdout
                tampered["rows"][0]["stdout_sha256"] = hashlib.sha256(
                    stdout.encode()).hexdigest()
            else:
                tampered["source_audit"]["wrapper_raw_call_shape"][
                    "traced_sync"]["cuStreamSynchronize"] = 0
            tampered.pop("receipt_sha256")
            tampered["receipt_sha256"] = runtime_digest(tampered)
            with self.assertRaises(RuntimeError, msg=mutation):
                validate_direct_operation_kat(tampered, files)
            with self.assertRaises(RuntimeError, msg=f"independent-{mutation}"):
                _validate_direct_operation_kat_independently(tampered, files)

    def test_rtdl_operation_kat_binds_actual_first_reuse_and_final_identity(self):
        product_source = (
            ROOT / "src/rtdsl/v4_rtdlexe.py").read_text(encoding="utf-8")
        self.assertEqual(product_source.count(
            'self._minimum_overlap = float(runtime["minimum_overlap_f32"])'),
            1)
        self.assertEqual(product_source.count(
            "self._minimum_overlap, self._capacity,"), 1)
        value, files, deployment_ids, executable_ids = \
            synthetic_rtdl_operation_kat()
        validate_rtdl_operation_kat(
            value, files, deployment_ids,
            expected_executable_identities=executable_ids)
        _validate_rtdl_operation_kat_independently(
            value, files, deployment_ids,
            expected_executable_identities=executable_ids)
        for mutation in (
                "auxiliary", "reuse", "executable", "trust",
                "diagnostic_hash"):
            tampered = copy.deepcopy(value)
            if mutation == "auxiliary":
                tampered["rows"][0]["first_execute"][
                    "native_operation_receipt"][
                        "total_auxiliary_cuda_kernel_launch_count"] = 6
            elif mutation == "reuse":
                tampered["rows"][1]["reused_execute"][
                    "dynamic_input_receipt"][
                        "dynamic_device_upload_call_count"] = 1
            elif mutation == "executable":
                tampered["rows"][0]["runtime_identity"][
                    "executed_executable_identity_sha256"] = "a" * 64
                tampered["rows"][0]["first_execute"][
                    "executable_identity_sha256"] = "a" * 64
                tampered["rows"][0]["reused_execute"][
                    "executable_identity_sha256"] = "a" * 64
            elif mutation == "trust":
                tampered["rows"][0]["deployment_identity"][
                    "trust_root_sha256"] = "b" * 64
            else:
                tampered["rows"][0]["first_execute"][
                    "product_output_sha256"] = "f" * 64
            tampered.pop("receipt_sha256")
            tampered["receipt_sha256"] = runtime_digest(tampered)
            with self.assertRaises(RuntimeError, msg=mutation):
                validate_rtdl_operation_kat(
                    tampered, files, deployment_ids,
                    expected_executable_identities=executable_ids)
            with self.assertRaises(RuntimeError, msg=f"independent-{mutation}"):
                _validate_rtdl_operation_kat_independently(
                    tampered, files, deployment_ids,
                    expected_executable_identities=executable_ids)

    def test_three_arm_k_plus_one_device_failure_is_input_bound_and_output_closed(self):
        workload = relation_k_plus_one_workload()
        self.assertEqual(len(workload["indexed"]), 1)
        self.assertEqual(len(workload["sources"]), 4098)
        self.assertEqual(workload["minimum_overlap_f32"], 1.0)
        self.assertEqual(workload["expected_failure"]["status"], 0xffff5102)
        self.assertLess(
            workload["expected_failure"]["raw_event_count"],
            workload["expected_failure"]["raw_capacity"])
        derived = derive_relation_rows_cpu(
            workload["indexed"], workload["sources"],
            workload["minimum_overlap_f32"])
        self.assertEqual(
            derived,
            {key: workload["oracle_derivation"][key] for key in derived})
        self.assertEqual(derived["forward_raw_event_count"], 4097)
        self.assertEqual(derived["reverse_raw_event_count"], 0)
        zero_threshold = derive_relation_rows_cpu(
            workload["indexed"], workload["sources"], 0.0)
        self.assertEqual(zero_threshold["raw_event_count"], 4098)
        self.assertEqual(
            workload["oracle_derivation"]["zero_threshold_raw_event_count"],
            4098)

        py_value, py_files = synthetic_pyoptix_operation_kat()
        direct_value, direct_files = synthetic_direct_operation_kat()
        rtdl_value, rtdl_files, deployment_ids, executable_ids = \
            synthetic_rtdl_operation_kat()
        cases = (
            ("pyoptix", py_value, lambda value: (
                validate_pyoptix_operation_kat(
                    value, py_files,
                    expected_source_sha256=py_value[
                        "source_boundary"]["source_sha256"]),
                _validate_operation_kat_independently(
                    value, py_files,
                    expected_source_sha256=py_value[
                        "source_boundary"]["source_sha256"]))),
            ("direct", direct_value, lambda value: (
                validate_direct_operation_kat(value, direct_files),
                _validate_direct_operation_kat_independently(
                    value, direct_files))),
            ("rtdl", rtdl_value, lambda value: (
                validate_rtdl_operation_kat(
                    value, rtdl_files, deployment_ids,
                    expected_executable_identities=executable_ids),
                _validate_rtdl_operation_kat_independently(
                    value, rtdl_files, deployment_ids,
                    expected_executable_identities=executable_ids))),
        )
        for name, value, validate in cases:
            with self.subTest(arm=name, phase="valid"):
                validate(value)
            for mutation in ("status", "output", "input", "parameter"):
                tampered = copy.deepcopy(value)
                hostile = tampered["relation_k_plus_one_hostile"]
                if mutation == "status":
                    hostile["compact_control"]["status"] = 0
                    if name == "direct":
                        tampered["rows"][0]["worker_receipt"][
                            "relation_k_plus_one_hostile"][
                                "compact_control"]["status"] = 0
                elif mutation == "output":
                    hostile["application_output_d2h_call_count"] = 1
                    hostile["application_output_d2h_bytes"] = 8
                    if name == "direct":
                        worker_hostile = tampered["rows"][0]["worker_receipt"][
                            "relation_k_plus_one_hostile"]
                        worker_hostile["application_output_d2h_call_count"] = 1
                        worker_hostile["application_output_d2h_bytes"] = 8
                elif mutation == "input":
                    hostile["packed_input_sha256"] = "0" * 64
                    if name == "direct":
                        tampered["rows"][0]["worker_receipt"][
                            "relation_k_plus_one_hostile"][
                                "packed_input_sha256"] = "0" * 64
                else:
                    hostile["executed_parameter_projection"][
                        "minimum_overlap_f32_bits"] = 0
                    if name == "direct":
                        tampered["rows"][0]["worker_receipt"][
                            "relation_k_plus_one_hostile"][
                                "executed_parameter_projection"][
                                    "minimum_overlap_f32_bits"] = 0
                if name == "direct":
                    worker = tampered["rows"][0]["worker_receipt"]
                    stdout = json.dumps(
                        worker, sort_keys=True, separators=(",", ":")) + "\n"
                    tampered["rows"][0]["stdout_utf8"] = stdout
                    tampered["rows"][0]["stdout_sha256"] = hashlib.sha256(
                        stdout.encode()).hexdigest()
                tampered.pop("receipt_sha256")
                tampered["receipt_sha256"] = runtime_digest(tampered)
                with self.subTest(arm=name, mutation=mutation):
                    with self.assertRaises(RuntimeError):
                        validate(tampered)

    def test_independent_architecture_contract_recounts_raw_ptx_and_artifacts(
            self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ptx = root / "matched.ptx"
            ptx.write_bytes(
                b".version 8.7\n.target sm_89\n.address_size 64\n")
            artifact_template = {
                "product_projection": {
                    "target_toolchain": {"compute_capability": [8, 9]},
                    "ptx_metadata": {"target": "sm_89"},
                    "provider_key": {
                        "target_compute_capability": [8, 9],
                        "ptx_target": "sm_89",
                    },
                },
            }
            artifact_paths = {}
            for prefix in ("relation", "triangle"):
                path = root / f"{prefix}.rtdlexe.json"
                path.write_text(
                    json.dumps(artifact_template, sort_keys=True),
                    encoding="utf-8")
                artifact_paths[prefix] = path
            files = {
                "matched_ptx": {
                    "path": str(ptx),
                    "sha256": hashlib.sha256(ptx.read_bytes()).hexdigest(),
                },
                "nvrtc_library": {"sha256": "a" * 64},
                "nvrtc_builtins": {"sha256": "b" * 64},
            }
            for prefix, path in artifact_paths.items():
                files[f"{prefix}_artifact"] = {
                    "path": str(path),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            observation = {"compute_capability": "8.9"}
            ptx_receipt = {"nvrtc_library": {"version": [12, 9]}}
            artifact_rows = {
                prefix: {
                    "artifact_sha256": files[f"{prefix}_artifact"]["sha256"],
                    "target_toolchain_compute_capability": [8, 9],
                    "ptx_metadata_target": "sm_89",
                    "provider_target_compute_capability": [8, 9],
                    "provider_ptx_target": "sm_89",
                }
                for prefix in ("relation", "triangle")
            }
            runtime = {"architecture_contract": {
                "compute_capability": "8.9",
                "nvrtc_compute_architecture": "compute_89",
                "ptx_target": "sm_89",
                "ptx_target_directive_count": 1,
                "rtdl_artifacts": artifact_rows,
                "libnvrtc_sha256": "a" * 64,
                "libnvrtc_builtins_sha256": "b" * 64,
                "libnvrtc_version": [12, 9],
                "fresh_process_projection_claim": (
                    "OBSERVED_NVCC_DEPENDENCY_SET_UNDER_MATCHED_ARCH_AND_"
                    "EXACT_HOST_CXX__EMPIRICALLY_SUFFICIENT_FOR_FRESH_PROCESS_"
                    "EXACT_NVRTC_REPLAY__NOT_A_GENERAL_NVRTC_SUPERSET"),
            }}
            _validate_architecture_contract_independently(
                runtime, files, observation, ptx_receipt)

            old_claim = copy.deepcopy(runtime)
            old_claim["architecture_contract"][
                "fresh_process_projection_claim"] = (
                    "OBSERVED_NVCC_DEPENDENCY_SET_UNDER_MATCHED_ARCH_AND_"
                    "CUDACC_RTC__EMPIRICALLY_SUFFICIENT_FOR_FRESH_PROCESS_"
                    "EXACT_NVRTC_REPLAY__NOT_A_GENERAL_NVRTC_SUPERSET")
            with self.assertRaises(RuntimeError):
                _validate_architecture_contract_independently(
                    old_claim, files, observation, ptx_receipt)

            ptx.write_bytes(
                b".version 8.7\n.target sm_89\n.target sm_89\n"
                b".address_size 64\n")
            with self.assertRaises(RuntimeError):
                _validate_architecture_contract_independently(
                    runtime, files, observation, ptx_receipt)
            ptx.write_bytes(
                b".version 8.7\n.target sm_89\n.address_size 64\n")

            bad_runtime = copy.deepcopy(runtime)
            bad_runtime["architecture_contract"]["ptx_target"] = "sm_90"
            with self.assertRaises(RuntimeError):
                _validate_architecture_contract_independently(
                    bad_runtime, files, observation, ptx_receipt)

            artifact = copy.deepcopy(artifact_template)
            artifact["product_projection"]["ptx_metadata"]["target"] = "sm_90"
            artifact_paths["relation"].write_text(
                json.dumps(artifact, sort_keys=True), encoding="utf-8")
            with self.assertRaises(RuntimeError):
                _validate_architecture_contract_independently(
                    runtime, files, observation, ptx_receipt)

    def test_independent_runtime_envelope_requires_architecture_contract(self):
        runtime = {
            "schema": "rtdl.goal5802.target_runtime_manifest.v2",
            "status": "PREPARED_UNTIMED__FORMAL_EXECUTION_LOCKED",
            "files": {}, "directories": {}, "deployment_ids": {},
            "pyoptix": {}, "target_observation": {}, "target_policy": {},
            "architecture_contract": {}, "build_provenance": {},
            "formal_preflight_contract": {},
            "registered_performance_timing_count": 0,
            "formal_worker_zero": False,
        }
        runtime["manifest_sha256"] = runtime_digest(runtime)
        _validate_runtime_envelope_independently(runtime)
        missing = copy.deepcopy(runtime)
        missing.pop("architecture_contract")
        missing.pop("manifest_sha256")
        missing["manifest_sha256"] = runtime_digest(missing)
        with self.assertRaises(RuntimeError):
            _validate_runtime_envelope_independently(missing)

    def test_host_runtime_provenance_rehashes_actual_dependency_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            payload = root / "runtime_payload.bin"
            payload.write_bytes(b"goal5802-runtime")
            payload_row = {
                "relative_path": "runtime_payload.bin",
                "path": str(payload), "bytes": payload.stat().st_size,
                "sha256": hashlib.sha256(payload.read_bytes()).hexdigest(),
            }
            empty = root / "legal_empty_package_marker"
            empty.write_bytes(b"")
            empty_row = {
                "relative_path": "legal_empty_package_marker",
                "path": str(empty), "bytes": 0,
                "sha256": hashlib.sha256(b"").hexdigest(),
            }
            distributions = []
            for name in (
                    "numpy", "cupy-cuda12x", "cuda-python", "numba",
                    "llvmlite"):
                files = [dict(payload_row), dict(empty_row)]
                distributions.append({
                    "name": name, "version": "synthetic",
                    "file_count": 2, "payload_bytes": payload.stat().st_size,
                    "tree_sha256": runtime_digest(files), "files": files,
                })
            python = Path(sys.executable).resolve(strict=True)
            python_record = {
                "path": str(python), "bytes": python.stat().st_size,
                "sha256": hashlib.sha256(python.read_bytes()).hexdigest(),
            }
            value: dict[str, object] = {
                "schema": "rtdl.goal5802.host_runtime_provenance.v3",
                "status": "PASS__UNTIMED_EXACT_HOST_RUNTIME_CAPTURE",
                "python": {
                    "version": sys.version, "implementation": "CPython",
                    "executable": python_record},
                "distributions": distributions,
                "loaded_module_files": {
                    name: {
                        "path": str(payload), "bytes": payload.stat().st_size,
                        "sha256": hashlib.sha256(payload.read_bytes()).hexdigest(),
                    } for name in (
                        "numpy", "cupy", "cuda.bindings.driver",
                        "cuda.bindings.nvrtc", "optix", "numba",
                        "llvmlite")},
                "host": _current_host_projection(),
                "thread_and_visibility_environment": {
                    key: os.environ.get(key) for key in (
                        "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                        "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                        "VECLIB_MAXIMUM_THREADS", "PYTHONHASHSEED",
                        "CUDA_VISIBLE_DEVICES", "PATH", "LD_LIBRARY_PATH",
                        "LD_PRELOAD")},
                "registered_performance_timing_count": 0,
                "formal_worker_count": 0,
            }
            value["receipt_sha256"] = runtime_digest(value)
            runtime_files = {"clean_python": {
                "path": str(python), "bytes": python.stat().st_size,
                "sha256": python_record["sha256"]}}
            validate_host_runtime_provenance(value, runtime_files)

            runtime_files["host_runtime_provenance"] = {
                "path": str(root / "host_runtime.json"), "bytes": 1,
                "sha256": "f" * 64}
            compiler_authority = numba_llvmlite_runtime_authority(
                value, runtime_files)
            self.assertEqual(
                [row["name"] for row in compiler_authority["distributions"]],
                ["numba", "llvmlite"])
            for key, hostile_value in (
                    ("PATH", "relative"),
                    ("LD_LIBRARY_PATH", "relative"),
                    ("LD_PRELOAD", "")):
                hostile = copy.deepcopy(value)
                hostile["thread_and_visibility_environment"][key] = hostile_value
                hostile.pop("receipt_sha256")
                hostile["receipt_sha256"] = runtime_digest(hostile)
                with self.assertRaises(RuntimeError):
                    validate_host_runtime_provenance(hostile, runtime_files)
            empty_compiler_version = copy.deepcopy(value)
            next(row for row in empty_compiler_version["distributions"]
                 if row["name"] == "numba")["version"] = ""
            empty_compiler_version.pop("receipt_sha256")
            empty_compiler_version["receipt_sha256"] = runtime_digest(
                empty_compiler_version)
            with self.assertRaises(RuntimeError):
                validate_host_runtime_provenance(
                    empty_compiler_version, runtime_files)
            shadow = root / "shadow_numba.py"
            shadow.write_bytes(b"shadow-numba")
            shadowed_module = copy.deepcopy(value)
            shadowed_module["loaded_module_files"]["numba"] = {
                "path": str(shadow), "bytes": shadow.stat().st_size,
                "sha256": hashlib.sha256(shadow.read_bytes()).hexdigest(),
            }
            shadowed_module.pop("receipt_sha256")
            shadowed_module["receipt_sha256"] = runtime_digest(shadowed_module)
            validate_host_runtime_provenance(shadowed_module, runtime_files)
            with self.assertRaises(RuntimeError):
                numba_llvmlite_runtime_authority(
                    shadowed_module, runtime_files)
            empty_distribution = copy.deepcopy(value)
            first_distribution = empty_distribution["distributions"][0]
            first_distribution["files"] = [dict(empty_row)]
            first_distribution["file_count"] = 1
            first_distribution["payload_bytes"] = 0
            first_distribution["tree_sha256"] = runtime_digest(
                first_distribution["files"])
            empty_distribution.pop("receipt_sha256")
            empty_distribution["receipt_sha256"] = runtime_digest(
                empty_distribution)
            with self.assertRaises(RuntimeError):
                validate_host_runtime_provenance(
                    empty_distribution, runtime_files)
            payload.write_bytes(b"goal5802-mutated")
            with self.assertRaises(RuntimeError):
                validate_host_runtime_provenance(value, runtime_files)

    def test_runtime_manifest_builder_accepts_complete_v3_compiler_runtime(self):
        source = (ROOT / "scripts/goal5802_build_target_runtime_manifest.py"
                  ).read_text(encoding="utf-8")
        self.assertIn("HOST_RUNTIME_DISTRIBUTIONS", source)
        self.assertIn("HOST_RUNTIME_MODULES", source)
        self.assertIn("!= list(HOST_RUNTIME_DISTRIBUTIONS)", source)
        self.assertIn("!= set(HOST_RUNTIME_MODULES)", source)
        self.assertNotIn('len(host_runtime["distributions"]) != 3', source)

    def test_goal5802_exact_bytes_disable_checkout_newline_conversion(self):
        attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        for rule in (
                "/.gitattributes -text",
                "/src/rtdsl/** -text",
                "/experiments/goal5802_premeasurement/** -text",
                "/scripts/goal5802_* -text",
                "/tests/goal5802_* -text",
                "/scripts/goal5801_a3_run_clean_install.py -text",
                "/scripts/goal5801_a3_verify_clean_install.py -text",
                "/scripts/goal5801_a3_verify_native_custody.py -text",
                "/tests/goal5801_a3_custody_and_clean_install_test.py -text",
                "/history/internal_docs/goal5802_* -text",
                "/history/internal_docs/goal5802_*/** -text"):
            self.assertEqual(attributes.count(rule), 1, msg=rule)
        _, source_paths = contract._instrument_context()
        self.assertIn(".gitattributes", source_paths)

    def test_pyoptix_original_sdk_and_projected_headers_are_bound_not_equal(
            self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sdk = root / "original-sdk"
            original_include = sdk / "include"
            original_include.mkdir(parents=True)
            (original_include / "optix.h").write_bytes(b"original-header")
            projection = root / "projection" / "rootfs" / "optix" / "include"
            projection.mkdir(parents=True)
            (projection / "optix.h").write_bytes(b"original-header")
            other_sdk = root / "wrong-sdk"
            (other_sdk / "include").mkdir(parents=True)
            (other_sdk / "include" / "optix.h").write_bytes(b"wrong-header")
            other_projection = root / "wrong-projection"
            other_projection.mkdir()

            headers = {
                "root": str(sdk),
                "commit": "fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd",
                "tree": "c30f1b41cb64f6cba6290d7ad82686cc84922267",
            }
            directories = {
                "optix_sdk": {"path": str(sdk)},
                "optix_include": {"path": str(projection)},
            }
            header_projection = {
                "command_authority": {"original_sdk_roots": {
                    "optix_include": {
                        "path": str(original_include),
                        "resolved_path": str(original_include.resolve()),
                    }}},
                "root_mappings": [{
                    "role": "optix_include",
                    "original_root": str(original_include.resolve()),
                    "projection_relative_root": "rootfs/optix/include",
                    "projected_root": str(projection.resolve()),
                    "roots_distinct_and_nonoverlapping": True,
                }],
            }

            # This is the intended production shape: the wheel used the
            # original SDK while runtime compilation uses a byte-governed,
            # disjoint projection.  Direct path equality would reject it.
            self.assertNotEqual(original_include.resolve(), projection.resolve())
            _validate_pyoptix_header_lineage_independently(
                headers, directories=directories,
                header_projection=header_projection)

            for field in ("commit", "tree"):
                wrong_headers = copy.deepcopy(headers)
                wrong_headers[field] = "0" * 40
                with self.assertRaises(RuntimeError, msg=field):
                    _validate_pyoptix_header_lineage_independently(
                        wrong_headers, directories=directories,
                        header_projection=header_projection)

            wrong_sdk = copy.deepcopy(directories)
            wrong_sdk["optix_sdk"]["path"] = str(other_sdk)
            with self.assertRaises(RuntimeError):
                _validate_pyoptix_header_lineage_independently(
                    headers, directories=wrong_sdk,
                    header_projection=header_projection)

            wrong_original = copy.deepcopy(header_projection)
            wrong_original["command_authority"]["original_sdk_roots"][
                "optix_include"]["resolved_path"] = str(
                    (other_sdk / "include").resolve())
            with self.assertRaises(RuntimeError):
                _validate_pyoptix_header_lineage_independently(
                    headers, directories=directories,
                    header_projection=wrong_original)

            wrong_projected = copy.deepcopy(header_projection)
            wrong_projected["root_mappings"][0]["projected_root"] = str(
                other_projection.resolve())
            with self.assertRaises(RuntimeError):
                _validate_pyoptix_header_lineage_independently(
                    headers, directories=directories,
                    header_projection=wrong_projected)

    def test_pyoptix_historical_and_active_clean_installs_bind_by_content(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            historical = root / "goal5800-venv"
            active = root / "goal5802-venv"
            historical.mkdir()
            active.mkdir()
            roles = {
                "wheel": ("pyoptix_wheel", b"wheel-bytes"),
                "loaded_optix_extension": (
                    "pyoptix_extension", b"extension-bytes"),
                "loaded_optix_package_initializer": (
                    "pyoptix_initializer", b"initializer-bytes"),
            }
            clean_install: dict[str, object] = {}
            files: dict[str, dict[str, object]] = {}
            historical_paths: dict[str, Path] = {}
            for receipt_role, (runtime_role, payload) in roles.items():
                old_path = historical / receipt_role
                current_path = active / receipt_role
                old_path.write_bytes(payload)
                current_path.write_bytes(payload)
                identity: dict[str, object] = {
                    "path": str(old_path.resolve()),
                    "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }
                if receipt_role == "loaded_optix_extension":
                    identity["module"] = "optix._optix"
                clean_install[receipt_role] = identity
                files[runtime_role] = {
                    "path": str(current_path.resolve()),
                    "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }
                historical_paths[receipt_role] = old_path

            self.assertTrue(all(
                clean_install[receipt_role]["path"]
                != files[runtime_role]["path"]
                for receipt_role, (runtime_role, _) in roles.items()))
            _validate_pyoptix_clean_install_copies_independently(
                clean_install, files)

            wrong_active = copy.deepcopy(files)
            wrong_active["pyoptix_extension"]["sha256"] = "0" * 64
            with self.assertRaises(RuntimeError):
                _validate_pyoptix_clean_install_copies_independently(
                    clean_install, wrong_active)

            wrong_module = copy.deepcopy(clean_install)
            wrong_module["loaded_optix_extension"]["module"] = "optix.fake"
            with self.assertRaises(RuntimeError):
                _validate_pyoptix_clean_install_copies_independently(
                    wrong_module, files)

            historical_paths["loaded_optix_package_initializer"].write_bytes(
                b"mutated-after-receipt")
            with self.assertRaises(RuntimeError):
                _validate_pyoptix_clean_install_copies_independently(
                    clean_install, files)

    def test_pyoptix_wheel_build_rehashes_relative_path_and_rejects_bool_exit(
            self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / "build_receipt.json"
            receipt.write_text("{}\n", encoding="utf-8")
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            historical_wheel = wheelhouse / "pyoptix.whl"
            active_wheel = root / "active" / "pyoptix.whl"
            active_wheel.parent.mkdir()
            payload = b"exact-wheel-content"
            historical_wheel.write_bytes(payload)
            active_wheel.write_bytes(payload)
            wheel = {
                "path": "wheelhouse/pyoptix.whl",
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "extension_member": "optix/_optix.so",
                "extension_bytes": 123,
                "extension_sha256": "a" * 64,
            }
            files = {"pyoptix_wheel": {
                "path": str(active_wheel.resolve()),
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }}
            _validate_pyoptix_wheel_build_copy_independently(
                receipt, wheel, {"exit_code": 0}, files)

            for invalid_exit in (False, True, 1):
                with self.assertRaises(RuntimeError, msg=repr(invalid_exit)):
                    _validate_pyoptix_wheel_build_copy_independently(
                        receipt, wheel, {"exit_code": invalid_exit}, files)

            wrong_record = copy.deepcopy(wheel)
            wrong_record["sha256"] = "0" * 64
            with self.assertRaises(RuntimeError):
                _validate_pyoptix_wheel_build_copy_independently(
                    receipt, wrong_record, {"exit_code": 0}, files)

            historical_wheel.write_bytes(b"mutated-wheel")
            with self.assertRaises(RuntimeError):
                _validate_pyoptix_wheel_build_copy_independently(
                    receipt, wheel, {"exit_code": 0}, files)

    def test_header_projection_rejects_omission_extra_change_and_symlink_relabel(
            self):
        def fixture(root: Path) -> tuple[dict[str, object], Path, Path]:
            original = root / "original"
            original.mkdir()
            cuda = root / "cuda"
            sources = root / "sources"
            cuda.mkdir()
            sources.mkdir()
            tool = root / "compiler"
            tool.write_bytes(b"compiler-identity")
            source_paths = [sources / name for name in (
                "matched.cu", "compaction.cu", "direct.cpp")]
            for source in source_paths:
                source.write_bytes(source.name.encode())
            first = original / "first.h"
            second = original / "second.h"
            first.write_bytes(b"first-header")
            second.write_bytes(b"second-header")
            dependency_text = " ".join(
                str(path.absolute()).replace("\\", "/")
                for path in (first, second))
            authority = build_command_authority(
                nvcc=tool, cxx=tool, matched_device_source=source_paths[0],
                relation_compaction_source=source_paths[1],
                direct_source=source_paths[2], optix_include=original,
                cuda_include=cuda, compute_capability="sm_89")
            expected = authority["expected_commands"]
            captured = [{
                "role": role,
                "command": list(expected[index]["command"]),
                "exit_code": 0,
                "stdout_utf8": f"{role}.o: {dependency_text}\n",
                "stderr_utf8": "",
            } for index, role in enumerate(HEADER_RUN_ROLES)]
            projection = root / "projection"
            value = materialize_captured_runs(
                captured, projection_root=projection,
                receipt_path=root / "receipt.json",
                command_authority=authority)
            _validate_header_projection_independently(value, projection)
            validate_header_projection(value, projection)
            validate_projection_only(value, projection)
            validate_provenance(value, projection)
            return value, projection, first

        with tempfile.TemporaryDirectory() as temporary:
            value, projection, _ = fixture(Path(temporary))
            tampered = copy.deepcopy(value)
            tampered["runs"][0]["load_bearing_sdk_dependencies"].pop()
            tampered.pop("receipt_sha256")
            tampered["receipt_sha256"] = header_sha(
                header_canonical(tampered))
            with self.assertRaises(RuntimeError):
                validate_header_projection(tampered, projection)
            with self.assertRaises(RuntimeError):
                _validate_header_projection_independently(
                    tampered, projection)

        # Exercise a real symlink retarget when the host permits unprivileged
        # symlink creation.  The synthetic chain mutation above remains the
        # platform-independent guard.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = root / "original"
            original.mkdir()
            cuda = root / "cuda"
            sources = root / "sources"
            cuda.mkdir()
            sources.mkdir()
            tool = root / "compiler"
            tool.write_bytes(b"compiler-identity")
            source_paths = [sources / name for name in (
                "matched.cu", "compaction.cu", "direct.cpp")]
            for source in source_paths:
                source.write_bytes(source.name.encode())
            first = original / "first.h"
            second = original / "second.h"
            alias = original / "alias.h"
            first.write_bytes(b"first-header")
            second.write_bytes(b"second-header")
            try:
                alias.symlink_to(first.name)
            except OSError:
                alias = None
            if alias is not None:
                dependency = str(alias.absolute()).replace("\\", "/")
                authority = build_command_authority(
                    nvcc=tool, cxx=tool,
                    matched_device_source=source_paths[0],
                    relation_compaction_source=source_paths[1],
                    direct_source=source_paths[2], optix_include=original,
                    cuda_include=cuda, compute_capability="sm_89")
                expected = authority["expected_commands"]
                captured = [{
                    "role": role,
                    "command": list(expected[index]["command"]),
                    "exit_code": 0,
                    "stdout_utf8": f"{role}.o: {dependency}\n",
                    "stderr_utf8": "",
                } for index, role in enumerate(HEADER_RUN_ROLES)]
                projection = root / "projection"
                value = materialize_captured_runs(
                    captured, projection_root=projection,
                    receipt_path=root / "receipt.json",
                    command_authority=authority)
                alias.unlink()
                alias.symlink_to(second.name)
                with self.assertRaises(RuntimeError):
                    validate_header_projection(value, projection)

        with tempfile.TemporaryDirectory() as temporary:
            value, projection, _ = fixture(Path(temporary))
            extra = projection / "rootfs" / "unregistered.h"
            extra.write_bytes(b"not-in-dependency-stdout")
            with self.assertRaises(RuntimeError):
                validate_header_projection(value, projection)

        with tempfile.TemporaryDirectory() as temporary:
            value, projection, first = fixture(Path(temporary))
            first.write_bytes(b"changed-after-capture")
            with self.assertRaises(RuntimeError):
                validate_header_projection(value, projection)

        with tempfile.TemporaryDirectory() as temporary:
            value, projection, _ = fixture(Path(temporary))
            tampered = copy.deepcopy(value)
            tampered["runs"][0]["load_bearing_sdk_dependencies"][0][
                "symlink_chain"] = [{
                "link_path": "/synthetic/include/alias.h",
                "link_target": "replacement.h",
                "resolved_target": "/synthetic/include/replacement.h",
            }]
            tampered.pop("receipt_sha256")
            tampered["receipt_sha256"] = header_sha(
                header_canonical(tampered))
            with self.assertRaises(RuntimeError):
                validate_header_projection(tampered, projection)

    def test_header_projection_failure_preserves_raw_process_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tool = root / "compiler"
            tool.write_bytes(b"compiler-identity")
            successful = {
                "role": HEADER_RUN_ROLES[0],
                "command": [str(tool), "-M", "first.cu"],
                "exit_code": 0,
                "stdout_utf8": "first.o: /synthetic/first.h\n",
                "stderr_utf8": "",
            }
            failed = {
                "role": HEADER_RUN_ROLES[1],
                "command": [str(tool), "-M", "second.cu"],
                "exit_code": 17,
                "stdout_utf8": "partial dependency stdout\n",
                "stderr_utf8": "fatal exact dependency error\n",
            }
            receipt = root / "failure.json"
            value = _write_dependency_failure(
                receipt_path=receipt, completed=[successful],
                failure=DependencyCommandFailure(failed))
            self.assertEqual(
                value["status"],
                "FAIL__DEPENDENCY_COMMAND__NO_PROJECTION_CREATED")
            self.assertEqual(value["failed_run"]["exit_code"], 17)
            self.assertEqual(
                value["failed_run"]["stderr_utf8"],
                "fatal exact dependency error\n")
            self.assertEqual(json.loads(receipt.read_text()), value)
            self.assertEqual(value["clock_read_count"], 0)
            self.assertEqual(value["gpu_kernel_launch_count"], 0)
            self.assertEqual(value["formal_worker_count"], 0)
            self.assertEqual(value["registered_performance_timing_count"], 0)

    def test_header_projection_exact_commands_split_and_offline_verifier(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            optix = root / "optix"
            cuda = root / "cuda"
            sources = root / "sources"
            for directory in (optix, cuda, sources):
                directory.mkdir()
            tool = root / "compiler"
            tool.write_bytes(b"compiler")
            source_paths = [sources / name for name in (
                "matched.cu", "compaction.cu", "direct.cpp")]
            for source in source_paths:
                source.write_bytes(source.name.encode())
            sdk_header = optix / "optix.h"
            system_header = root / "system.h"
            sdk_header.write_bytes(b"sdk")
            system_header.write_bytes(b"system")
            authority = build_command_authority(
                nvcc=tool, cxx=tool, matched_device_source=source_paths[0],
                relation_compaction_source=source_paths[1],
                direct_source=source_paths[2], optix_include=optix,
                cuda_include=cuda, compute_capability="sm_89")
            expected = authority["expected_commands"]
            self.assertEqual(
                authority["schema"],
                "rtdl.goal5802.dependency_command_authority.v4")
            self.assertEqual(
                authority["nvcc_host_compiler_policy"],
                "EXACT_CONFIGURED_CXX__NVCC_DEPENDENCY_ONLY__"
                "ALLOW_UNSUPPORTED_COMPILER_EXPLICIT")
            nested_cuda_include = f"-I{cuda.resolve() / 'nv'}"
            self.assertTrue(all(
                nested_cuda_include in row["command"] for row in expected))
            for row in expected[:2]:
                self.assertEqual(row["command"].count("-ccbin"), 1)
                ccbin = row["command"].index("-ccbin")
                self.assertEqual(row["command"][ccbin + 1], str(tool.resolve()))
                self.assertEqual(
                    row["command"].count("-allow-unsupported-compiler"), 1)
                self.assertNotIn("-D__CUDACC_RTC__=1", row["command"])
            self.assertNotIn(
                "-allow-unsupported-compiler", expected[2]["command"])
            dependency_text = " ".join(
                str(path.absolute()).replace("\\", "/")
                for path in (sdk_header, system_header))
            captured = [{
                "role": role, "command": list(expected[index]["command"]),
                "exit_code": 0,
                "stdout_utf8": f"{role}.o: {dependency_text}\n",
                "stderr_utf8": "",
            } for index, role in enumerate(HEADER_RUN_ROLES)]
            projection = root / "projection"
            value = materialize_captured_runs(
                captured, projection_root=projection,
                receipt_path=root / "receipt.json",
                command_authority=authority)
            self.assertEqual(value["projection_file_count"], 1)
            for run in value["runs"]:
                self.assertEqual(run[
                    "load_bearing_sdk_dependency_count"], 1)
                self.assertEqual(run[
                    "provenance_only_dependency_count"], 1)
            validate_projection_only(value, projection)
            validate_provenance(value, projection)

            command_tamper = copy.deepcopy(value)
            command = command_tamper["runs"][0]["command"]
            ccbin = command.index("-ccbin")
            del command[ccbin:ccbin + 2]
            command_tamper.pop("receipt_sha256")
            command_tamper["receipt_sha256"] = header_sha(
                header_canonical(command_tamper))
            with self.assertRaises(RuntimeError):
                validate_projection_only(command_tamper, projection)

            coordinated = copy.deepcopy(value)
            command = coordinated["runs"][0]["command"]
            ccbin = command.index("-ccbin")
            del command[ccbin:ccbin + 2]
            command_row = coordinated["command_authority"][
                "expected_commands"][0]
            ccbin = command_row["command"].index("-ccbin")
            del command_row["command"][ccbin:ccbin + 2]
            command_row["command_sha256"] = header_sha(
                header_canonical(command_row["command"]))
            coordinated.pop("receipt_sha256")
            coordinated["receipt_sha256"] = header_sha(
                header_canonical(coordinated))
            with self.assertRaises(RuntimeError):
                validate_projection_only(coordinated, projection)

            policy_leaf_removed = copy.deepcopy(value)
            policy_leaf_removed["runs"][0]["command"].remove(
                "-allow-unsupported-compiler")
            command_row = policy_leaf_removed["command_authority"][
                "expected_commands"][0]
            command_row["command"].remove("-allow-unsupported-compiler")
            command_row["command_sha256"] = header_sha(
                header_canonical(command_row["command"]))
            policy_leaf_removed.pop("receipt_sha256")
            policy_leaf_removed["receipt_sha256"] = header_sha(
                header_canonical(policy_leaf_removed))
            with self.assertRaises(RuntimeError):
                validate_projection_only(policy_leaf_removed, projection)
            with self.assertRaises(RuntimeError):
                _validate_header_projection_independently(
                    policy_leaf_removed, projection)

            policy_relabelled = copy.deepcopy(value)
            policy_relabelled["command_authority"][
                "nvcc_host_compiler_policy"] = (
                    "IMPLICIT_TOOL_DEFAULT__NOT_EXACT")
            policy_relabelled.pop("receipt_sha256")
            policy_relabelled["receipt_sha256"] = header_sha(
                header_canonical(policy_relabelled))
            with self.assertRaises(RuntimeError):
                validate_projection_only(policy_relabelled, projection)
            with self.assertRaises(RuntimeError):
                _validate_header_projection_independently(
                    policy_relabelled, projection)

            retired_schema = copy.deepcopy(value)
            retired_schema["command_authority"]["schema"] = (
                "rtdl.goal5802.dependency_command_authority.v2")
            retired_schema.pop("receipt_sha256")
            retired_schema["receipt_sha256"] = header_sha(
                header_canonical(retired_schema))
            with self.assertRaises(RuntimeError):
                validate_projection_only(retired_schema, projection)

            relabelled = copy.deepcopy(value)
            row = relabelled["runs"][0][
                "load_bearing_sdk_dependencies"].pop()
            for key in (
                    "projection_path", "projected_bytes", "projected_sha256"):
                row.pop(key)
            row["classification"] = (
                "PROVENANCE_ONLY_SOURCE_SYSTEM_OR_TOOLCHAIN")
            row["sdk_root_role"] = None
            relabelled["runs"][0]["load_bearing_sdk_dependency_count"] = 0
            relabelled["runs"][0]["provenance_only_dependency_count"] = 2
            relabelled["runs"][0]["provenance_only_dependencies"].append(row)
            relabelled.pop("receipt_sha256")
            relabelled["receipt_sha256"] = header_sha(
                header_canonical(relabelled))
            with self.assertRaises(RuntimeError):
                validate_projection_only(relabelled, projection)

            shutil.rmtree(optix)
            shutil.rmtree(cuda)
            shutil.rmtree(sources)
            tool.unlink()
            system_header.unlink()
            validate_projection_only(value, projection)
            with self.assertRaises((RuntimeError, FileNotFoundError)):
                validate_provenance(value, projection)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            projection = root / "projection"
            with self.assertRaises(RuntimeError):
                materialize_captured_runs(
                    [], projection_root=projection,
                    receipt_path=projection / "receipt.json",
                    command_authority={})

    def test_header_projection_records_duplicate_mentions_without_duplicate_files(
            self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tool = root / "compiler"
            optix = root / "optix"
            cuda = root / "cuda"
            sources = root / "sources"
            optix.mkdir()
            cuda.mkdir()
            sources.mkdir()
            header = optix / "repeated.h"
            subdirectory = optix / "subdirectory"
            tool.write_bytes(b"compiler-identity")
            header.write_bytes(b"load-bearing-header")
            subdirectory.mkdir()
            source_paths = [sources / name for name in (
                "matched.cu", "compaction.cu", "direct.cpp")]
            for source in source_paths:
                source.write_bytes(source.name.encode())
            token = str(header.absolute()).replace("\\", "/")
            lexical_alias = str(
                (subdirectory / ".." / header.name).absolute()).replace(
                    "\\", "/")
            authority = build_command_authority(
                nvcc=tool, cxx=tool, matched_device_source=source_paths[0],
                relation_compaction_source=source_paths[1],
                direct_source=source_paths[2], optix_include=optix,
                cuda_include=cuda, compute_capability="sm_89")
            expected = authority["expected_commands"]
            captured = [{
                "role": role,
                "command": list(expected[index]["command"]),
                "exit_code": 0,
                "stdout_utf8": f"{role}.o: {token} {lexical_alias}\n",
                "stderr_utf8": "",
            } for index, role in enumerate(HEADER_RUN_ROLES)]
            projection = root / "projection"
            value = materialize_captured_runs(
                captured, projection_root=projection,
                receipt_path=root / "receipt.json",
                command_authority=authority)
            for run in value["runs"]:
                self.assertEqual(run["dependency_occurrence_count"], 2)
                self.assertEqual(run["unique_dependency_path_count"], 1)
                self.assertEqual(
                    run["duplicate_dependency_occurrence_count"], 1)
                self.assertEqual(
                    len(run["load_bearing_sdk_dependencies"]), 1)
            self.assertEqual(value["projection_file_count"], 1)
            tampered = copy.deepcopy(value)
            tampered["runs"][0][
                "duplicate_dependency_occurrence_count"] = 0
            tampered.pop("receipt_sha256")
            tampered["receipt_sha256"] = header_sha(
                header_canonical(tampered))
            with self.assertRaises(RuntimeError):
                validate_header_projection(tampered, projection)

    def test_header_projection_materialization_failure_is_quarantined(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tool = root / "compiler"
            optix = root / "optix"
            cuda = root / "cuda"
            sources = root / "sources"
            optix.mkdir()
            cuda.mkdir()
            sources.mkdir()
            first = optix / "first.h"
            missing = optix / "missing.h"
            tool.write_bytes(b"compiler-identity")
            first.write_bytes(b"first-header")
            source_paths = [sources / name for name in (
                "matched.cu", "compaction.cu", "direct.cpp")]
            for source in source_paths:
                source.write_bytes(source.name.encode())
            paths = [
                str(first.absolute()).replace("\\", "/"),
                str(missing.absolute()).replace("\\", "/"),
            ]
            authority = build_command_authority(
                nvcc=tool, cxx=tool, matched_device_source=source_paths[0],
                relation_compaction_source=source_paths[1],
                direct_source=source_paths[2], optix_include=optix,
                cuda_include=cuda, compute_capability="sm_89")
            expected = authority["expected_commands"]
            captured = [{
                "role": role,
                "command": list(expected[index]["command"]),
                "exit_code": 0,
                "stdout_utf8": f"{role}.o: {paths[index % 2]}\n",
                "stderr_utf8": "",
            } for index, role in enumerate(HEADER_RUN_ROLES)]
            projection = root / "projection"
            receipt = root / "failure.json"
            with self.assertRaises(RuntimeError) as caught:
                materialize_captured_runs(
                    captured, projection_root=projection,
                    receipt_path=receipt, command_authority=authority)
            value = _write_materialization_failure(
                receipt_path=receipt, captured=captured,
                projection_root=projection, error=caught.exception)
            self.assertEqual(
                value["status"],
                "FAIL__MATERIALIZATION__PARTIAL_PROJECTION_QUARANTINED")
            self.assertTrue(value["projection_created"])
            self.assertEqual(value["partial_projection_file_count"], 1)
            self.assertEqual(len(value["completed_runs"]), 3)
            self.assertIn("does not resolve", value[
                "materialization_error"]["message"])
            self.assertEqual(json.loads(receipt.read_text()), value)
            self.assertEqual(value["clock_read_count"], 0)
            self.assertEqual(value["gpu_kernel_launch_count"], 0)
            self.assertEqual(value["formal_worker_count"], 0)
            self.assertEqual(value["registered_performance_timing_count"], 0)

    def test_pyoptix_fast_failure_preserves_status_before_output(self):
        class SliceArray(SimpleNamespace):
            def __getitem__(self, _key):
                return self

        class FailureLauncher:
            def __init__(self):
                self.d2h_calls = 0

            def zero_on_stream(self, *_arrays):
                return None

            def fill_ff_on_stream(self, _array):
                return None

            def enqueue(self, _params, _width):
                return None

            def enqueue_compaction(self, _kernel, _args, *, element_count):
                self.compaction_element_count = element_count

            def enqueue_d2d(self, _destination, _source, _nbytes):
                return None

            def enqueue_d2h(self, _device, _host, _nbytes):
                self.d2h_calls += 1

            def synchronize(self):
                return None

        owner = DeferredRelationPrepared.__new__(DeferredRelationPrepared)
        owner.closed = False
        owner.prepared_launches = [(object(), 1), (object(), 1)]
        owner.launcher = FailureLauncher()
        owner.d_rows = object()
        owner.d_unique_rows = SimpleNamespace(nbytes=32768)
        owner.d_control = SliceArray(nbytes=16)
        owner.d_max_key_seen = SimpleNamespace(nbytes=4)
        owner.d_unique_count = SimpleNamespace(nbytes=4)
        owner.d_keys = SimpleNamespace(nbytes=65536)
        owner.compaction_kernel = object()
        owner.h_control = [1, 1, 0, 7]
        owner.raw_capacity = 8192
        owner.semantic_capacity = 4096
        owner.b = SimpleNamespace(
            ROW_DTYPE=SimpleNamespace(itemsize=8),
            np=SimpleNamespace(uint32=lambda value: value))
        owner.fixture = {"capacity": 4096, "expected_rows": []}
        with self.assertRaises(DeviceStatusFailure) as caught:
            owner._execute_fast(reused=False)
        self.assertEqual(owner.launcher.d2h_calls, 1)
        self.assertFalse(caught.exception.evidence[
            "application_output_exposed"])
        self.assertEqual(caught.exception.evidence[
            "application_output_d2h_call_count"], 0)

    def test_rtdlexe_plan_is_public_lifecycle_only(self):
        value = rtdlexe_plan()
        self.assertEqual(
            value["public_lifecycle"],
            ["install", "load", "prepare", "execute", "close"])
        self.assertEqual(value["compiler_or_materializer_call_count"], 0)
        self.assertEqual(value["triangle_per_ray_d2h_bytes"], 0)

    def test_local_untimed_adapter_never_reads_clock(self):
        adapter = FakeAdapter()

        def forbidden_clock():
            raise AssertionError("local untimed path read a clock")

        result = run_adapter(
            adapter, "STEADY_E2E", clock=forbidden_clock,
            local_untimed=True)
        self.assertEqual(result["registered_performance_timing_count"], 0)
        self.assertEqual(adapter.events, ["load", "prepare", "execute", "close"])

    def test_local_untimed_true_build_never_reads_clock(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "fresh.bin"

            def builder():
                output.write_bytes(b"fresh-source-product")
                return {"product": output}

            def forbidden_clock():
                raise AssertionError("local untimed BUILD_COLD read a clock")

            result = run_true_build(
                builder, clock=forbidden_clock, local_untimed=True)
        self.assertTrue(result["true_build_executed"])
        self.assertFalse(result["prebuilt_product_read_as_build"])
        self.assertEqual(result["registered_performance_timing_count"], 0)
        self.assertIsNone(result["duration_ns"])

    def test_symmetric_phase_runner_boundaries(self):
        deployment = FakeAdapter()
        result = run_adapter(
            deployment, "DEPLOYMENT_COLD", clock=CounterClock(),
            input_materialization_ns=7,
            process_startup_and_admission_ns=9)
        self.assertEqual(deployment.events, ["load", "prepare", "execute", "close"])
        self.assertEqual(result["execute_or_regime_durations_ns"], [30])
        self.assertEqual(result["phase_durations_ns"]["load_or_deploy"], 10)
        self.assertEqual(result["phase_durations_ns"]["prepare"], 10)
        self.assertEqual(result["phase_durations_ns"]["complete_execute"], 10)
        self.assertEqual(result["phase_durations_ns"]["close"], 10)

        prepare = FakeAdapter()
        result = run_adapter(
            prepare, "PREPARE", clock=CounterClock(),
            input_materialization_ns=7,
            process_startup_and_admission_ns=9)
        self.assertEqual(result["execute_or_regime_durations_ns"], [10])
        self.assertEqual(prepare.events, ["load", "prepare", "execute", "close"])

        steady = FakeAdapter()
        result = run_adapter(
            steady, "STEADY_E2E", clock=CounterClock(),
            input_materialization_ns=7,
            process_startup_and_admission_ns=9)
        self.assertEqual(len(result["execute_or_regime_durations_ns"]), 64)
        self.assertTrue(all(
            value == 10 for value in result["execute_or_regime_durations_ns"]))
        self.assertEqual(steady.executions, 8 + 64)

    def test_freeze_roundtrip_and_mutations_fail_closed(self):
        freeze = contract.build_freeze(
            ROOT, product_binding(), engineering_ledger(),
            successor_forecast())
        contract.validate_freeze(freeze, ROOT)
        self.assertEqual(
            freeze["schema"], "rtdl.goal5802.local_premeasurement_freeze.v3")
        self.assertEqual(freeze["worker_row_count"], 432)
        self.assertEqual(freeze["build_cold_absolute_worker_row_count"], 72)
        self.assertFalse(freeze["authorization"]["formal_worker_zero"])
        self.assertEqual(freeze["registered_performance_timing_count"], 0)
        paths = {row["path"] for row in freeze["source_manifest"]}
        self.assertFalse(paths.intersection(contract.LEGACY_WORKERS))
        self.assertIn("src/rtdsl/v4_rtdlexe.py", paths)
        self.assertIn("scripts/goal5801_a3_verify_native_custody.py", paths)
        self.assertIn("scripts/goal5802_build_successor_forecast.py", paths)
        self.assertIn("tests/goal5802_successor_forecast_cli_test.py", paths)
        self.assertIn(contract.PREDICTION_FREEZE, paths)
        forecast = freeze["successor_subjective_forecast"]
        self.assertEqual(forecast["schema"], FORECAST_SCHEMA)
        self.assertEqual(forecast["status"], FORECAST_STATUS)
        self.assertEqual(
            forecast["identity_binding"],
            {key: value for key, value in sorted(
                contract.successor_forecast_identity_binding(
                    ROOT, freeze["product_binding"]).items())})
        self.assertEqual(forecast["predecessor_authority"], PREDECESSOR_AUTHORITY)
        self.assertEqual(len(forecast["primary_predictions"]), 6)
        self.assertTrue(all(
            row["manual_successor_probability_entry"] is True
            and row["probability_copied_or_defaulted_from_predecessor"] is False
            for row in forecast["primary_predictions"]))
        self.assertTrue(
            forecast["joint_prediction"]["manual_successor_probability_entry"])
        self.assertEqual(len(forecast["forecast_sha256"]), 64)

        tampered = copy.deepcopy(freeze)
        tampered["authorization"]["formal_worker_zero"] = True
        with self.assertRaises(contract.ContractError):
            contract.validate_freeze(tampered, ROOT)

        independently_tampered = copy.deepcopy(freeze)
        independently_tampered["successor_subjective_forecast"][
            "identity_binding"]["complete_product_binding_sha256"] = "0" * 64
        reseal_successor_forecast(independently_tampered)
        reseal_freeze(independently_tampered)
        with self.assertRaisesRegex(
                RuntimeError, "identity binding"):
            _validate_freeze_bytes(
                independently_tampered, freeze_file_sha256="a" * 64,
                root=ROOT)

        predecessor_tampered = copy.deepcopy(freeze)
        predecessor_tampered["successor_subjective_forecast"][
            "predecessor_authority"]["canonical_utf8_lf_bytes"] += 1
        reseal_successor_forecast(predecessor_tampered)
        reseal_freeze(predecessor_tampered)
        with self.assertRaisesRegex(RuntimeError, "predecessor"):
            _validate_freeze_bytes(
                predecessor_tampered, freeze_file_sha256="a" * 64,
                root=ROOT)

        for label, key, value in (
                ("forged clean verifier", "clean_install_verifier_sha256",
                 "e" * 64),
                ("forged native verifier", "native_custody_verifier_sha256",
                 "f" * 64),
                ("retired product schema", "schema", "ATTACK")):
            attacked = copy.deepcopy(freeze)
            attacked["product_binding"][key] = value
            attacked_unsigned = dict(attacked)
            attacked_unsigned.pop("freeze_sha256")
            attacked["freeze_sha256"] = contract.digest(attacked_unsigned)
            with self.subTest(label=label):
                with self.assertRaisesRegex(RuntimeError, "product"):
                    _validate_freeze_bytes(
                        attacked, freeze_file_sha256="a" * 64, root=ROOT)

    def test_successor_manual_probability_and_source_manifest_fail_closed(self):
        freeze = contract.build_freeze(
            ROOT, product_binding(), engineering_ledger(),
            successor_forecast())
        tampered = copy.deepcopy(freeze)
        tampered["successor_subjective_forecast"][
            "primary_predictions"][0][
                "manual_successor_probability_entry"] = False
        reseal_successor_forecast(tampered)
        reseal_freeze(tampered)
        with self.assertRaises(contract.ContractError):
            contract.validate_freeze(tampered, ROOT)
        with self.assertRaisesRegex(RuntimeError, "successor forecast"):
            _validate_freeze_bytes(
                tampered, freeze_file_sha256="a" * 64, root=ROOT)

        seal_tampered = copy.deepcopy(freeze)
        seal_tampered["successor_subjective_forecast"][
            "primary_predictions"][0][
                "subjective_gate_pass_probability"] = 0.99
        reseal_freeze(seal_tampered)
        with self.assertRaisesRegex(RuntimeError, "seal"):
            _validate_freeze_bytes(
                seal_tampered, freeze_file_sha256="a" * 64, root=ROOT)

        tampered = copy.deepcopy(freeze)
        tampered["source_manifest"][0]["sha256"] = "0" * 64
        tampered["successor_subjective_forecast"]["identity_binding"][
            "complete_instrument_source_manifest_sha256"] = contract.digest(
                tampered["source_manifest"])
        reseal_successor_forecast(tampered)
        reseal_freeze(tampered)
        with self.assertRaises(contract.ContractError):
            contract.validate_freeze(tampered, ROOT)
        with self.assertRaisesRegex(RuntimeError, "source drift"):
            _validate_freeze_bytes(
                tampered, freeze_file_sha256="a" * 64, root=ROOT)

    def test_local_controller_plan_never_uses_goal5798_worker(self):
        freeze = contract.build_freeze(
            ROOT, product_binding(), engineering_ledger(),
            successor_forecast())
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "freeze.json"
            path.write_bytes(json.dumps(
                freeze, indent=2, sort_keys=True).encode("utf-8") + b"\n")
            plan = local_plan(path, ROOT)
        self.assertFalse(plan["formal_worker_zero"])
        flattened = json.dumps(command_templates(), sort_keys=True)
        for legacy in contract.LEGACY_WORKERS:
            self.assertNotIn(legacy, flattened)
        for template in command_templates().values():
            if template and template[0] == "<clean_python>":
                self.assertEqual(
                    template[1:6], ["-I", "-S", "-B", "-P", "-c"])
                self.assertEqual(
                    template[6], "<controlled_runpy_module_bootstrap>")

    def test_execution_authority_requires_both_keys_and_zero_findings(self):
        authority = {
            "schema": "rtdl.goal5802.formal_execution_authority.v1",
            "freeze_file_sha256": "a" * 64,
            "runtime_manifest_file_sha256": "c" * 64,
            "external_cfr_sha256": "b" * 64,
            "external_review_p0": 0,
            "external_review_p1": 0,
            "external_exact_byte_approval": True,
            "owner_execution_authorized": True,
            "formal_worker_zero_authorized": True,
            "pod_gpu_timing_authorized": True,
        }
        authority["execution_authority_sha256"] = hashlib.sha256(
            contract.canonical(authority)).hexdigest()
        validate_execution_authority(
            authority, freeze_sha256="a" * 64,
            runtime_manifest_sha256="c" * 64)
        for key in (
                "external_exact_byte_approval", "owner_execution_authorized",
                "formal_worker_zero_authorized", "pod_gpu_timing_authorized"):
            bad = dict(authority)
            bad[key] = False
            bad.pop("execution_authority_sha256")
            bad["execution_authority_sha256"] = hashlib.sha256(
                contract.canonical(bad)).hexdigest()
            with self.assertRaises(RuntimeError, msg=key):
                validate_execution_authority(
                    bad, freeze_sha256="a" * 64,
                    runtime_manifest_sha256="c" * 64)

    def test_owner_waiver_authority_is_explicitly_not_external_review(self):
        authority = {
            "schema": OWNER_WAIVER_AUTHORITY_SCHEMA,
            "freeze_file_sha256": "a" * 64,
            "runtime_manifest_file_sha256": "c" * 64,
            "preexecution_cfr_sha256": "b" * 64,
            "external_preexecution_review_claimed": False,
            "external_exact_byte_approval": False,
            "owner_explicit_external_review_waiver": True,
            "owner_waiver_reason": OWNER_WAIVER_REASON,
            "owner_execution_authorized": True,
            "formal_worker_zero_authorized": True,
            "pod_gpu_timing_authorized": True,
        }
        authority["execution_authority_sha256"] = hashlib.sha256(
            contract.canonical(authority)).hexdigest()
        validate_execution_authority(
            authority, freeze_sha256="a" * 64,
            runtime_manifest_sha256="c" * 64)
        for key, replacement in (
                ("external_preexecution_review_claimed", True),
                ("external_exact_byte_approval", True),
                ("owner_explicit_external_review_waiver", False),
                ("owner_waiver_reason", "EXTERNAL_REVIEW_APPROVED")):
            bad = dict(authority)
            bad[key] = replacement
            bad.pop("execution_authority_sha256")
            bad["execution_authority_sha256"] = hashlib.sha256(
                contract.canonical(bad)).hexdigest()
            with self.assertRaises(RuntimeError, msg=key):
                validate_execution_authority(
                    bad, freeze_sha256="a" * 64,
                    runtime_manifest_sha256="c" * 64)

    def test_direct_source_is_new_scalar_worker(self):
        path = ROOT / "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"
        text = path.read_text(encoding="utf-8")
        self.assertIn("triangle_status_d2h_bytes\\\":4", text)
        self.assertIn("triangle_scalar_d2h_bytes\\\":8", text)
        self.assertIn("per_ray_d2h_bytes\\\":0", text)
        self.assertIn("h_rows(kRelationSize)", text)
        self.assertIn("d_rows(sizeof(RelationRow) * kRelationRawCapacity)", text)
        self.assertIn("const std::string ptx = read_file(args.ptx)", text)
        self.assertNotIn(
            "const std::string source = read_file(args.device_source);\n"
            "        const std::string ptx = compile_ptx(\n"
            "            source, args.device_source", text)
        self.assertNotIn(
            '#include "../goal5798_premeasurement/direct_measurement.cpp"', text)
        self.assertIn('#include "../goal5796_matched/direct_optix.cpp"', text)

    def test_direct_operation_trace_rejects_unobserved_extra_sync(self):
        source = ROOT / "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"
        audit = audit_direct_source(source)
        self.assertEqual(audit["relation_expected_dynamic"][
            "status_output_commit_blocking_boundary_count"], 2)
        with tempfile.TemporaryDirectory() as temporary:
            tampered = Path(temporary) / "direct_scalar_worker.cpp"
            text = source.read_text(encoding="utf-8")
            tampered.write_text(
                text.replace(
                    "Trace trace;\n        CU_CHECK(cuMemsetD8Async",
                    "Trace trace;\n"
                    "        CU_CHECK(cuStreamSynchronize(0));\n"
                    "        CU_CHECK(cuMemsetD8Async",
                    1),
                encoding="utf-8")
            with self.assertRaises(DirectSourceAuditError):
                audit_direct_source(tampered)
            moved = Path(temporary) / "direct_scalar_worker_moved_sync.cpp"
            moved_text = text.replace(
                "CU_CHECK(cuStreamSynchronize(stream));",
                "(void)stream;", 1).replace(
                    "Trace trace;",
                    "Trace trace;\n"
                    "        CU_CHECK(cuStreamSynchronize(0));", 1)
            self.assertNotEqual(moved_text, text)
            self.assertEqual(
                moved_text.count("cuStreamSynchronize"),
                text.count("cuStreamSynchronize"))
            moved.write_text(moved_text, encoding="utf-8")
            with self.assertRaises(DirectSourceAuditError):
                audit_direct_source(moved)

    def test_direct_k_plus_one_minimum_overlap_reaches_device_params(self):
        source = ROOT / "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"
        audit_direct_source(source)
        text = source.read_text(encoding="utf-8")
        assignment = "params.minimum_overlap = minimum_overlap;"
        self.assertEqual(text.count(assignment), 1)
        hostile_literal = (
            "relation_k_plus_one_sources(),\n"
            "                        kRelationMinimumOverlap);")
        self.assertEqual(text.count(hostile_literal), 1)
        with tempfile.TemporaryDirectory() as temporary:
            tampered = Path(temporary) / "direct_scalar_worker.cpp"
            tampered.write_text(
                text.replace(hostile_literal,
                             "relation_k_plus_one_sources(), 0.0f);", 1),
                encoding="utf-8")
            with self.assertRaises(DirectSourceAuditError):
                audit_direct_source(tampered)
            shadowed = Path(temporary) / "direct_scalar_worker_shadowed.cpp"
            shadowed.write_text(
                text.replace(
                    assignment,
                    assignment + "\n            params.minimum_overlap = 0.0f;",
                    1),
                encoding="utf-8")
            with self.assertRaises(DirectSourceAuditError):
                audit_direct_source(shadowed)

    def test_direct_formal_core_is_trace_free_and_host_runtime_is_pinned(self):
        from scripts.goal5802_capture_host_runtime_provenance import (
            DISTRIBUTIONS as CAPTURE_DISTRIBUTIONS,
            MODULES as CAPTURE_MODULES,
        )

        source = ROOT / "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"
        audit = audit_direct_source(source)
        self.assertEqual(
            audit["status"],
            "PASS__FORMAL_TRACE_FREE__UNTIMED_OBSERVER_SAME_TEMPLATE_CORE")
        text = source.read_text(encoding="utf-8")
        self.assertIn("execute() { return execute_core<false>(); }", text)
        self.assertEqual(text.count(
            "execute_observed() { return execute_core<true>(); }"), 2)
        with tempfile.TemporaryDirectory() as temporary:
            tampered = Path(temporary) / "direct_scalar_worker.cpp"
            tampered.write_text(text.replace(
                "RelationOutput execute() { return execute_core<false>(); }",
                "RelationOutput execute() { return execute_core<true>(); }"),
                encoding="utf-8")
            with self.assertRaises(DirectSourceAuditError):
                audit_direct_source(tampered)
        capture = (ROOT / "scripts/goal5802_capture_host_runtime_provenance.py"
                   ).read_text(encoding="utf-8")
        self.assertEqual(
            HOST_RUNTIME_DISTRIBUTIONS,
            ("numpy", "cupy-cuda12x", "cuda-python", "numba", "llvmlite"))
        self.assertEqual(
            HOST_RUNTIME_MODULES,
            ("numpy", "cupy", "cuda.bindings.driver", "cuda.bindings.nvrtc",
             "optix", "numba", "llvmlite"))
        self.assertEqual(CAPTURE_DISTRIBUTIONS, HOST_RUNTIME_DISTRIBUTIONS)
        self.assertEqual(CAPTURE_MODULES, HOST_RUNTIME_MODULES)
        for literal in (
                '"numpy", "cupy-cuda12x", "cuda-python", "numba", "llvmlite"',
                '"cuda.bindings.driver"', '"cuda.bindings.nvrtc"',
                '"cpu_governors"', '"affinity"',
                '"thread_and_visibility_environment"'):
            self.assertIn(literal, capture)

    def test_controller_contains_spawn_timeout_and_cache_failures(self):
        row = {
            "ordinal": 1,
            "worker_id": "goal5802-hostile-controller-row",
            "arm": contract.ARMS[1],
            "task": TRIANGLE_TASK,
            "regime": "STEADY_E2E",
        }
        environment = {
            "GOAL5802_FREEZE_FILE_SHA256": "1" * 64,
            "GOAL5802_EXECUTION_AUTHORITY_SHA256": "2" * 64,
            "GOAL5802_RUNTIME_MANIFEST_SHA256": "3" * 64,
            "GOAL5802_RUNTIME_PREFLIGHT_RECEIPT_FILE_SHA256": "4" * 64,
            "GOAL5802_RUNTIME_PREFLIGHT_SHA256": "5" * 64,
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            missing = root / "definitely_missing_goal5802_executable"
            spawn = _execute_one(
                row=row, command=[str(missing)], root=root,
                environment=environment, worker_dir=root / "spawn",
                timeout_seconds=1,
                receipt_schema=(
                    "rtdl.goal5802.comparative_controller_worker_receipt.v1"),
            )
            self.assertEqual(spawn["status"],
                             "FAIL__NO_RETRY_OR_REPLACEMENT")
            self.assertIsInstance(spawn["spawn_error"], str)
            self.assertFalse(spawn["timed_out"])

            timeout = _execute_one(
                row=row,
                command=[sys.executable, "-c", "import time; time.sleep(30)"],
                root=root, environment=environment,
                worker_dir=root / "timeout", timeout_seconds=1,
                receipt_schema=(
                    "rtdl.goal5802.comparative_controller_worker_receipt.v1"),
            )
            self.assertEqual(timeout["status"],
                             "FAIL__NO_RETRY_OR_REPLACEMENT")
            self.assertTrue(timeout["timed_out"])

            leak_program = (
                "import json,os,pathlib;"
                "pathlib.Path(os.environ['CUDA_CACHE_PATH'],'leak.bin')."
                "write_bytes(b'x');"
                "print(json.dumps({'status':'PASS','arm':" +
                repr(row["arm"]) + ",'worker_id':" +
                repr(row["worker_id"]) + ",'task':" +
                repr(row["task"]) + ",'regime':" +
                repr(row["regime"]) +
                ",'freeze_file_sha256':os.environ["
                "'GOAL5802_FREEZE_FILE_SHA256'],"
                "'execution_authority_sha256':os.environ["
                "'GOAL5802_EXECUTION_AUTHORITY_SHA256'],"
                "'runtime_manifest_sha256':os.environ["
                "'GOAL5802_RUNTIME_MANIFEST_SHA256']}))"
            )
            cache = _execute_one(
                row=row, command=[sys.executable, "-c", leak_program],
                root=root, environment=environment,
                worker_dir=root / "cache", timeout_seconds=5,
                receipt_schema=(
                    "rtdl.goal5802.comparative_controller_worker_receipt.v1"),
            )
            self.assertEqual(cache["status"],
                             "FAIL__NO_RETRY_OR_REPLACEMENT")
            self.assertFalse(cache["isolated_process_cache_end_state"]
                             ["all_cache_roots_file_empty_after_worker"])

    def test_primary_and_independent_recount_include_build_cold(self):
        freeze = contract.build_freeze(
            ROOT, product_binding(), engineering_ledger(),
            successor_forecast())
        comparative = []
        relation_rows = relation_workload()["expected_rows"]
        arm_ns = {
            contract.ARMS[0]: 100,
            contract.ARMS[1]: 105,
            contract.ARMS[2]: 100,
        }
        freeze_sha = "a" * 64
        authority_sha = "b" * 64
        runtime_sha = "c" * 64
        operation_keys = (
            "prepare_device_allocation_call_count", "prepare_h2d_call_count",
            "prepare_pinned_host_allocation_call_count",
            "prepare_stream_creation_count", "execute_device_allocation_call_count",
            "execute_pinned_host_allocation_call_count",
            "execute_async_h2d_call_count", "execute_async_d2h_call_count",
            "execute_blocking_d2h_call_count",
            "execute_device_zero_fill_call_count",
            "execute_explicit_stream_sync_call_count", "execute_launch_call_count",
            "execute_stream_creation_call_count", "execute_stream_destroy_call_count",
        )

        def counts(**nonzero):
            value = {key: 0 for key in operation_keys}
            value.update(nonzero)
            return value

        guard = {
            "scope": "PYTHON_VISIBLE_TASK_OWNER_EXECUTE__NOT_CUPTI_OR_DRIVER_WIDE",
            "unapproved_device_allocation_call_count": 0,
            "unapproved_pinned_host_allocation_call_count": 0,
            "unapproved_blocking_asnumpy_call_count": 0,
            "unauthorized_direct_stream_sync_count": 0,
            "complete_driver_operation_observation_claimed": False,
        }
        isolated_cache_policy = {
            "policy": "FRESH_EMPTY_PER_WORKER_PROCESS_CACHE_ROOTS",
            "cuda_cache_disabled": True,
            "optix_cache_disabled": True,
            "cuda_cache_path": "/synthetic/cache/cuda",
            "cupy_cache_dir": "/synthetic/cache/cupy",
            "optix_cache_path": "/synthetic/cache/optix",
            "xdg_cache_home": "/synthetic/cache/xdg",
            "home": "/synthetic/home",
            "tmp": "/synthetic/tmp",
            "all_directories_empty_before_worker": True,
        }
        isolated_cache_end = {
            "file_count": 0, "payload_bytes": 0,
            "rows_sha256": hashlib.sha256(b"[]").hexdigest(),
            "all_cache_roots_file_empty_after_worker": True,
        }
        for row in freeze["schedule"]:
            length = 64 if row["regime"] == "STEADY_E2E" else 1
            worker = {
                "schema": (
                    "rtdl.goal5802.direct_scalar.worker.v1"
                    if row["arm"] == contract.ARMS[0]
                    else "rtdl.goal5802.python_arm_worker_result.v1"),
                "status": "PASS",
                "worker_id": row["worker_id"],
                "arm": row["arm"],
                "task": row["task"],
                "regime": row["regime"],
                "freeze_file_sha256": freeze_sha,
                "execution_authority_sha256": authority_sha,
                "runtime_manifest_sha256": runtime_sha,
                "execute_or_regime_durations_ns": [arm_ns[row["arm"]]] * length,
                "registered_performance_timing_count": length,
                "receipt_serialization_inside_timer": False,
                "close_inside_primary_timer": False,
            }
            if row["arm"] == contract.ARMS[0]:
                worker["retained_executed_ptx_sha256"] = "8" * 64
                if row["task"] == RELATION_TASK:
                    worker["retained_compaction_cubin_sha256"] = "9" * 64
            elif row["arm"] == contract.ARMS[1]:
                worker["loaded_runtime_identity"] = {
                    "distribution_version": "9.1.0",
                    "initializer_path": "/synthetic/optix/__init__.py",
                    "initializer_sha256": "1" * 64,
                    "extension_path": "/synthetic/optix/_optix.so",
                    "extension_sha256": "2" * 64,
                    "optix_api_version": "9.0.0",
                    "matched_ptx_path": "/synthetic/matched.ptx",
                    "matched_ptx_sha256": "3" * 64,
                    "retained_matched_ptx_sha256": "3" * 64,
                }
                if row["task"] == RELATION_TASK:
                    worker["loaded_runtime_identity"].update({
                        "compaction_cubin_path": "/synthetic/compaction.cubin",
                        "compaction_cubin_sha256": "9" * 64,
                        "retained_compaction_cubin_sha256": "9" * 64,
                    })
            else:
                family = (
                    "relation" if row["task"] == RELATION_TASK else "triangle")
                worker["loaded_runtime_identity"] = {
                    "rtdsl_init_path": "/synthetic/rtdsl/__init__.py",
                    "rtdsl_init_sha256": "4" * 64,
                    "rtdlexe_module_path": "/synthetic/rtdsl/v4_rtdlexe.py",
                    "rtdlexe_module_sha256": "5" * 64,
                    "executed_executable_identity_sha256": freeze[
                        "product_binding"][
                            f"{family}_executable_identity_sha256"],
                }
            if row["arm"] != contract.ARMS[0]:
                worker.update({
                    "constructor_evidence_inside_primary_timer": False,
                    "constructor_runtime_preload_receipt": {
                        "schema": "rtdl.goal5802.synthetic_preload.v1",
                        "status": "PASS__BEFORE_PRIMARY_CLOCK",
                    },
                    "new_forbidden_module_load_inside_primary_timer": False,
                    "primary_estimator_name": (
                        "WARM_PROCESS_DEPLOYMENT_COLD"
                        if row["regime"] == "DEPLOYMENT_COLD"
                        else row["regime"]),
                    "primary_estimator_scope": (
                        "LOAD_OR_DEPLOY_PLUS_PREPARE_PLUS_COMPLETE_EXECUTE__"
                        "EXCLUDES_PROCESS_STARTUP_ADMISSION_AND_ARM_RUNTIME_"
                        "MODULE_PRELOAD"
                        if row["regime"] == "DEPLOYMENT_COLD"
                        else "REGIME_DEFINED_BY_GOAL5802_FREEZE"),
                    "primary_timer_new_module_load_policy":
                        "REJECT_ALL_NOT_PRELOADED",
                })
            lifecycle_count = 72 if row["regime"] == "STEADY_E2E" else 1
            rtdl_triangle = (
                row["arm"] == contract.ARMS[2] and row["task"] == TRIANGLE_TASK)
            first_dynamic = {
                "prepared_input_reused": False,
                "dynamic_device_upload_call_count": 8 if rtdl_triangle else 2,
                "dynamic_device_upload_bytes": (
                    212992 if row["task"] == RELATION_TASK
                    else 589824 if rtdl_triangle else 524288),
                "dynamic_accel_build_count": (
                    1 if row["task"] == RELATION_TASK else 0),
                "dynamic_explicit_sync_count": 0,
                "dynamic_blocking_upload_call_count": 0,
                "dynamic_input_generation": 1,
            }
            reused_dynamic = {
                "prepared_input_reused": True,
                "dynamic_device_upload_call_count": 0,
                "dynamic_device_upload_bytes": 0,
                "dynamic_accel_build_count": 0,
                "dynamic_explicit_sync_count": 0,
                "dynamic_blocking_upload_call_count": 0,
                "dynamic_input_generation": 1,
            }
            lifecycle = [first_dynamic] + [
                reused_dynamic for _ in range(lifecycle_count - 1)]
            worker["execution_lifecycle_receipts"] = lifecycle
            final_dynamic = lifecycle[-1]
            native_operation = {
                "schema": "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2",
                "optix_launch_count": (
                    2 if row["task"] == RELATION_TASK else 1),
                "host_blocking_boundary_count": 2,
                "control_d2h_bytes": (
                    16 if row["task"] == RELATION_TASK else 4),
                "output_d2h_bytes": (
                    32768 if row["task"] == RELATION_TASK else 8),
                "status_before_output": True,
                "output_d2h_after_status_failure": 0,
                "role_counters_materialized": False,
                "prepared_input_reused": final_dynamic[
                    "prepared_input_reused"],
                "dynamic_device_upload_call_count": final_dynamic[
                    "dynamic_device_upload_call_count"],
                "dynamic_device_upload_bytes": final_dynamic[
                    "dynamic_device_upload_bytes"],
                "dynamic_accel_build_count": final_dynamic[
                    "dynamic_accel_build_count"],
                "dynamic_explicit_sync_count": final_dynamic[
                    "dynamic_explicit_sync_count"],
                "dynamic_blocking_upload_call_count": 0,
                "dynamic_input_generation": final_dynamic[
                    "dynamic_input_generation"],
            }
            baseline_auxiliary = ({
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
            } if row["task"] == RELATION_TASK else {
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
            rtdl_auxiliary = ({
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
                } if row["task"] == RELATION_TASK else {
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
            native_operation.update(rtdl_auxiliary)
            if row["regime"] == "DEPLOYMENT_COLD":
                worker["phase_durations_ns"] = {
                    "process_startup_and_admission": 10,
                    "input_materialization": 5,
                    "load_or_deploy": 20,
                    "prepare": 30,
                    "steady_warmups": 0,
                    "complete_execute": arm_ns[row["arm"]] - 50,
                    "measurement_evidence_materialization": 1,
                    "close": 10,
                    "post_execution_identity_validation": 10,
                }
            elif row["regime"] == "PREPARE":
                worker["phase_durations_ns"] = {
                    "process_startup_and_admission": 10,
                    "input_materialization": 5,
                    "load_or_deploy": 20,
                    "prepare": arm_ns[row["arm"]],
                    "steady_warmups": 0,
                    "complete_execute": 50,
                    "measurement_evidence_materialization": 1,
                    "close": 10,
                    "post_execution_identity_validation": 10,
                }
            else:
                worker["phase_durations_ns"] = {
                    "process_startup_and_admission": 10,
                    "input_materialization": 5,
                    "load_or_deploy": 20,
                    "prepare": 30,
                    "steady_warmups": 8 * arm_ns[row["arm"]],
                    "complete_execute": 64 * arm_ns[row["arm"]],
                    "measurement_evidence_materialization": 1,
                    "close": 10,
                    "post_execution_identity_validation": 10,
                }
            if row["task"] == RELATION_TASK:
                if row["arm"] == contract.ARMS[0]:
                    worker["correctness"] = {
                        "oracle_exact": True,
                        "canonical_row_count": 4096,
                        "canonical_rows": relation_rows,
                        "raw_event_count": 8192,
                        "semantic_unique_count": 4096,
                        "device_status": 0,
                        "device_overflow": 0,
                    }
                    worker["operation_ledger"] = {
                        **baseline_auxiliary,
                        "operation_evidence_source": (
                            "UNTIMED_OBSERVER_SAME_TEMPLATE_CORE_AND_"
                            "EXACT_SOURCE_AUDIT"),
                        "live_operation_trace_inside_timer": False,
                        "optix_launch_count": 2,
                        "semantic_compaction_launch_count": 1,
                        "semantic_compaction_key_capacity": 8192,
                        "semantic_compaction_scratch_bytes": 98312,
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
                        "dynamic_input_receipt": final_dynamic,
                    }
                elif row["arm"] == contract.ARMS[1]:
                    worker["result"] = {
                        **baseline_auxiliary,
                        "output": relation_rows,
                        "optix_launch_count": 2,
                        "semantic_compaction_launch_count": 1,
                        "semantic_compaction_key_capacity": 8192,
                        "semantic_compaction_scratch_bytes": 98312,
                        "required_sync_count": 2,
                        "raw_event_count": 8192,
                        "semantic_unique_count": 4096,
                        "device_status": 0,
                        "device_overflow": 0,
                        "control_d2h_bytes": 16,
                        "output_d2h_bytes": 32768,
                        "compact_status_control_d2h_bytes": 16,
                        "application_output_d2h_bytes": 32768,
                        "total_success_d2h_bytes": 32784,
                        "status_output_commit_blocking_boundary_count": 2,
                        "per_ray_d2h_bytes": 0,
                        "per_ray_host_materialized": False,
                        "optix_module_disk_cache_enabled": False,
                        "live_execute_guard_inside_timer": False,
                        "operation_evidence_source": (
                            "UNTIMED_PREWORKER_KAT_AND_EXACT_SOURCE_BOUNDARY"),
                        "optix_validation_mode": "OFF",
                        "optix_log_callback_mode": "OFF",
                        "module_optimization_level": "DEFAULT",
                        "module_debug_level": "NONE",
                    }
                else:
                    worker["result"] = {
                        **rtdl_auxiliary,
                        "output": relation_rows,
                        "device_status": {"ok": True},
                        "optix_launch_count": 2,
                        "raw_event_count": 8192,
                        "semantic_unique_count": 4096,
                        "semantic_compaction_launch_count": 1,
                        "semantic_compaction_key_capacity": 8192,
                        "semantic_compaction_scratch_bytes": 98312,
                        "compact_status_control_d2h_bytes": 16,
                        "application_output_d2h_bytes": 32768,
                        "user_visible_output_bytes": 32768,
                        "total_success_d2h_bytes": 32784,
                        "status_output_commit_blocking_boundary_count": 2,
                        "per_ray_d2h_bytes": 0,
                        "per_ray_host_materialized": False,
                        "dynamic_input_receipt": final_dynamic,
                        "native_operation_receipt": native_operation,
                        "traversal_receipt": {"synthetic": True},
                        "output_sha256": "6" * 64,
                        "role_counters": [],
                        "executable_identity_sha256": freeze[
                            "product_binding"][
                                "relation_executable_identity_sha256"],
                    }
            else:
                if row["arm"] == contract.ARMS[0]:
                    worker["correctness"] = {
                        "oracle_exact": True, "device_status": 0,
                        "reduced_u64": 65530,
                    }
                    worker["operation_ledger"] = {
                        **baseline_auxiliary,
                        "operation_evidence_source": (
                            "UNTIMED_OBSERVER_SAME_TEMPLATE_CORE_AND_"
                            "EXACT_SOURCE_AUDIT"),
                        "live_operation_trace_inside_timer": False,
                        "optix_launch_count": 1,
                        "async_h2d_call_count": 1,
                        "async_h2d_bytes": 120,
                        "async_d2h_call_count": 2,
                        "device_intermediate_per_ray_bytes": 131072,
                        "device_reset_bytes": 131084,
                        "h2d_launch_parameter_bytes": 120,
                        "compact_status_control_d2h_bytes": 4,
                        "application_output_d2h_bytes": 8,
                        "total_success_d2h_bytes": 12,
                        "per_ray_d2h_bytes": 0,
                        "status_output_commit_blocking_boundary_count": 2,
                        "optix_module_disk_cache_enabled": False,
                        "optix_validation_mode": "OFF",
                        "optix_log_callback_mode": "OFF",
                        "module_optimization_level": "DEFAULT",
                        "module_debug_level": "NONE",
                        "dynamic_input_receipt": final_dynamic,
                    }
                elif row["arm"] == contract.ARMS[1]:
                    worker["result"] = {
                        **baseline_auxiliary,
                        "launch_count": 1, "device_status": 0,
                        "required_sync_count": 2,
                        "reduced_u64": 65530,
                        "status_d2h_bytes": 4,
                        "scalar_d2h_bytes": 8,
                        "compact_status_control_d2h_bytes": 4,
                        "application_output_d2h_bytes": 8,
                        "total_success_d2h_bytes": 12,
                        "per_ray_d2h_bytes": 0,
                        "status_output_commit_blocking_boundary_count": 2,
                        "per_ray_host_materialized": False,
                        "per_ray_device_intermediate_bytes": 131072,
                        "device_reset_bytes": 131084,
                        "h2d_launch_parameter_bytes": 120,
                        "optix_module_disk_cache_enabled": False,
                        "live_execute_guard_inside_timer": False,
                        "operation_evidence_source": (
                            "UNTIMED_PREWORKER_KAT_AND_EXACT_SOURCE_BOUNDARY"),
                        "optix_validation_mode": "OFF",
                        "optix_log_callback_mode": "OFF",
                        "module_optimization_level": "DEFAULT",
                        "module_debug_level": "NONE",
                    }
                else:
                    worker["result"] = {
                        **rtdl_auxiliary,
                        "device_status": {"ok": True},
                        "optix_launch_count": 1, "reduced_u64": 65530,
                        "compact_status_control_d2h_bytes": 4,
                        "application_output_d2h_bytes": 8,
                        "total_success_d2h_bytes": 12,
                        "per_ray_d2h_bytes": 0,
                        "per_ray_host_materialized": False,
                        "status_output_commit_blocking_boundary_count": 2,
                        "dynamic_input_receipt": final_dynamic,
                        "native_operation_receipt": native_operation,
                        "traversal_receipt": {"synthetic": True},
                        "output_sha256": "7" * 64,
                        "role_counters": [],
                        "executable_identity_sha256": freeze[
                            "product_binding"][
                                "triangle_executable_identity_sha256"],
                    }
            comparative.append({
                "schema": "rtdl.goal5802.comparative_controller_worker_receipt.v1",
                "worker_directory_name": (
                    f"comparative_{row['ordinal']:04d}_{row['worker_id']}"),
                "status": "PASS", "schedule_row": row,
                "exit_code": 0, "timed_out": False, "spawn_error": None,
                "new_process_group_or_session": True,
                "orphan_process_group_detected": False,
                "controller_process_envelope_ns": (
                    sum(worker["phase_durations_ns"].values()) + 1),
                "preworker_common_cache_conditioning": {
                    "policy": (
                        "NO_MANUAL_FILE_PAGE_CONDITIONING__OS_PAGE_CACHE_"
                        "UNCONTROLLED__BALANCED_SIX_ORDER"),
                    "roles": [],
                    "payload_bytes": 0,
                    "rows_sha256": hashlib.sha256(b"[]").hexdigest(),
                    "duration_ns": 0,
                    "os_shared_library_and_driver_cache_state": (
                        "UNCONTROLLED__DISCLOSED"),
                },
                "isolated_process_cache_policy": isolated_cache_policy,
                "isolated_process_cache_end_state": isolated_cache_end,
                "stdout_bytes": 1, "stdout_sha256": "d" * 64,
                "stderr_bytes": 0, "stderr_sha256": "e" * 64,
                "worker_result": worker,
                "comparative_measurement_boundary": {
                    "schema": (
                        "rtdl.goal5802.comparative_measurement_boundary.v1"),
                    "primary_estimator_name": (
                        "WARM_PROCESS_DEPLOYMENT_COLD"
                        if row["regime"] == "DEPLOYMENT_COLD"
                        else row["regime"]),
                    "primary_estimator_excludes_process_startup_and_admission":
                        True,
                    "process_startup_and_admission_separately_published": True,
                    "process_startup_and_admission_ns": worker[
                        "phase_durations_ns"]["process_startup_and_admission"],
                    "controller_process_envelope_separately_published": True,
                    "direct_pre_main_dso_boundary": (
                        "INCLUDED_IN_PROCESS_STARTUP_AND_ADMISSION__OUTSIDE_PRIMARY"
                        if row["arm"] == contract.ARMS[0]
                        else "NOT_APPLICABLE"),
                    "python_interpreter_import_and_arm_runtime_preload_boundary":
                        ("NOT_APPLICABLE"
                         if row["arm"] == contract.ARMS[0]
                         else (
                             "INCLUDED_IN_PROCESS_STARTUP_AND_ADMISSION__"
                             "OUTSIDE_PRIMARY")),
                    "deployment_cold_is_process_cold_claimed": False,
                    "boundary_valid": True,
                },
            })
        compiler_runtime_authority: dict[str, object] = {
            "schema": "rtdl.goal5802.numba_llvmlite_runtime_authority.v1",
            "status": "EXACT_SEALED_BUILD_COMPILER_RUNTIME",
            "host_runtime_provenance_file_sha256": "1" * 64,
            "host_runtime_provenance_receipt_sha256": "2" * 64,
            "distributions": [{
                "name": name, "version": version,
                "file_count": 10, "payload_bytes": 1000,
                "tree_sha256": sha,
            } for name, version, sha in (
                ("numba", "0.61.0", "3" * 64),
                ("llvmlite", "0.44.0", "4" * 64))],
            "loaded_module_files": [{
                "name": name,
                "path": str((ROOT / "synthetic" / name / "__init__.py").resolve()),
                "bytes": 100, "sha256": sha,
            } for name, sha in (
                ("numba", "5" * 64), ("llvmlite", "6" * 64))],
        }
        compiler_runtime_authority["authority_sha256"] = contract.digest(
            compiler_runtime_authority)
        build = []
        build_ns = {
            contract.ARMS[0]: 1000,
            contract.ARMS[1]: 1100,
            contract.ARMS[2]: 1500,
        }
        for row in freeze["build_cold_absolute_schedule"]:
            output_roles = {
                contract.ARMS[0]: ("direct_executable", "matched_ptx"),
                contract.ARMS[1]: ("matched_ptx",),
                contract.ARMS[2]: (
                    "unsigned_rtdlexe", "detached_unsigned_authority"),
            }[row["arm"]]
            if row["task"] == RELATION_TASK and row["arm"] in {
                    contract.ARMS[0], contract.ARMS[1]}:
                output_roles = (*output_roles,
                                "relation_semantic_compaction_cubin")
            rtdsl_import_identity = None
            compiler_runtime_identity = None
            if row["arm"] == contract.ARMS[2]:
                required_module_names = {
                    "rtdsl", "rtdsl.v4", "rtdsl.v4_callback_lifecycle",
                    "rtdsl.v4_rtdlexe",
                    ("rtdsl.v4_bounded_relation_optix_compiler"
                     if row["task"] == RELATION_TASK
                     else "rtdsl.v4_triangle_standard_library"),
                }
                if row["task"] != RELATION_TASK:
                    required_module_names.add(
                        "rtdsl.v4_triangle_reduction_optix_compiler")
                module_rows = [{
                    "module": name,
                    "path": str((ROOT / "synthetic" / "rtdsl" /
                                 f"{name.replace('.', '/')}.py").resolve()),
                    "relative_path": (
                        "rtdsl/__init__.py" if name == "rtdsl" else
                        f"rtdsl/{name.removeprefix('rtdsl.').replace('.', '/')}.py"),
                    "bytes": 1,
                    "sha256": "a" * 64,
                } for name in sorted(required_module_names)]
                rtdsl_import_identity = {
                    "schema": (
                        "rtdl.goal5802.build_cold_rtdsl_import_identity.v1"),
                    "status": (
                        "PASS__ALL_LOADED_RTDL_MODULES_FROM_SEALED_PACKAGE"),
                    "rtdsl_package_file_count": freeze["product_binding"][
                        "rtdsl_package_file_count"],
                    "rtdsl_package_tree_sha256": freeze["product_binding"][
                        "rtdsl_package_tree_sha256"],
                    "required_module_names": sorted(required_module_names),
                    "loaded_rtdsl_modules": module_rows,
                    "loaded_rtdsl_modules_sha256": contract.digest(module_rows),
                }
                compiler_module_rows = [{
                    "name": item["name"],
                    "version": next(
                        distribution["version"]
                        for distribution in compiler_runtime_authority[
                            "distributions"]
                        if distribution["name"] == item["name"]),
                    "path": item["path"], "bytes": item["bytes"],
                    "sha256": item["sha256"],
                } for item in compiler_runtime_authority[
                    "loaded_module_files"]]
                compiler_runtime_identity = {
                    "schema": (
                        "rtdl.goal5802."
                        "build_cold_compiler_runtime_identity.v1"),
                    "status": (
                        "PASS__ACTUAL_NUMBA_LLVM_LITE_MATCH_SEALED_RUNTIME"),
                    "compiler_runtime_authority_sha256": (
                        compiler_runtime_authority["authority_sha256"]),
                    "actual_loaded_module_files": compiler_module_rows,
                    "actual_loaded_module_files_sha256": contract.digest(
                        compiler_module_rows),
                }
                compiler_runtime_identity["identity_sha256"] = contract.digest(
                    compiler_runtime_identity)
            build.append({
                "schema": "rtdl.goal5802.build_cold_controller_worker_receipt.v1",
                "worker_directory_name": (
                    f"build_cold_{row['ordinal']:04d}_{row['worker_id']}"),
                "status": "PASS", "schedule_row": row,
                "exit_code": 0, "timed_out": False, "spawn_error": None,
                "new_process_group_or_session": True,
                "orphan_process_group_detected": False,
                "controller_process_envelope_ns": 1,
                "preworker_common_cache_conditioning": None,
                "isolated_process_cache_policy": isolated_cache_policy,
                "isolated_process_cache_end_state": isolated_cache_end,
                "stdout_bytes": 1, "stdout_sha256": "d" * 64,
                "stderr_bytes": 0, "stderr_sha256": "e" * 64,
                "comparative_measurement_boundary": None,
                "worker_result": {
                    "schema": "rtdl.goal5802.build_cold_worker_result.v1",
                    "status": "PASS",
                    "worker_id": row["worker_id"],
                    "task": row["task"],
                    "arm": row["arm"],
                    "regime": "BUILD_COLD_ABSOLUTE_DIAGNOSTIC",
                    "freeze_file_sha256": freeze_sha,
                    "execution_authority_sha256": authority_sha,
                    "runtime_manifest_sha256": runtime_sha,
                    "duration_ns": build_ns[row["arm"]],
                    "true_build_executed": True,
                    "prebuilt_product_read_as_build": False,
                    "build_boundary": "PRE_SIGNING_PRE_DEPLOYMENT_BUILD_PRODUCT",
                    "deployable_product_claimed": False,
                     "signing_or_trust_governance_inside_timer": False,
                     "registered_performance_timing_count": 1,
                    "rtdsl_import_identity": rtdsl_import_identity,
                    "compiler_runtime_identity": compiler_runtime_identity,
                     "outputs": {
                        role: {"path": f"/synthetic/{role}", "bytes": 1,
                               "sha256": "f" * 64}
                        for role in output_roles},
                },
            })
        snapshot_rows = [
            {"path": item["path"], "bytes": item["bytes"],
             "sha256": item["sha256"]}
            for item in freeze["source_manifest"]
            if item["path"].endswith(".py") and (
                item["path"].startswith("experiments/")
                or item["path"].startswith("scripts/"))]
        def preflight_process(document: object) -> dict[str, object]:
            stdout = json.dumps(document, sort_keys=True)
            return {
                "command": ["/synthetic/preflight"], "exit_code": 0,
                "stdout_utf8": stdout,
                "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
                "stderr_utf8": "",
                "stderr_sha256": hashlib.sha256(b"").hexdigest(),
            }

        def preflight_file(name: str) -> dict[str, object]:
            return {"path": str(ROOT / f"synthetic_{name}"), "bytes": 1,
                    "sha256": "f" * 64}

        target_document: dict[str, object] = {}
        target_document["observation_sha256"] = runtime_digest(
            target_document)
        direct_document: dict[str, object] = {}
        python_document: dict[str, object] = {
            "status": "PASS__FRESH_PROCESS_UNTIMED_NVRTC_COMPILE",
            "pid": 1234, "product": {"sha256": "e" * 64},
        }
        python_document["receipt_sha256"] = runtime_digest(python_document)
        python_summary = {
            "status": python_document["status"],
            "pid": python_document["pid"],
            "product_sha256": python_document["product"]["sha256"],
            "receipt_sha256": python_document["receipt_sha256"],
        }
        package_document: dict[str, object] = {
            "schema": "rtdl.goal5802.rtdsl_package_import_preflight.v1",
            "status": "PASS__CLEAN_PYTHON_IMPORTED_SEALED_RTDSL_PACKAGE",
        }
        package_document["receipt_sha256"] = runtime_digest(package_document)
        runtime_preflight: dict[str, object] = {
            "schema": "rtdl.goal5802.formal_runtime_preflight.v1",
            "status": (
                "PASS__LIVE_TARGET_AND_CROSS_ARM_NVRTC_BEFORE_WORKER_ZERO"),
            "runtime_manifest_file_sha256": runtime_sha,
            "loader_environment": {
                "PATH": str(ROOT), "LD_LIBRARY_PATH": None,
                "LD_PRELOAD": None},
            "target_reobservation": {
                "process": preflight_process(target_document),
                "process_evidence": preflight_file("target_process.json"),
                "receipt": preflight_file("target.json"),
                "document": target_document,
                "all_frozen_fields_equal": True,
            },
            "direct_nvrtc_compile_identity": {
                "process": preflight_process(direct_document),
                "process_evidence": preflight_file("direct_process.json"),
                "document": direct_document,
                "prepare_document_byte_projection_equal": True,
            },
            "python_nvrtc_compile_identity": {
                "process": preflight_process(python_summary),
                "process_evidence": preflight_file("python_process.json"),
                "receipt": preflight_file("python.json"),
                "document": python_document,
                "product": preflight_file("matched.ptx"),
                "matched_ptx_byte_identical": True,
            },
            "rtdsl_package_import_identity": {
                "process": preflight_process(package_document),
                "process_evidence": preflight_file("rtdsl_package_process.json"),
                "document": package_document,
                "all_modules_match_sealed_package": True,
            },
            "cross_arm_libnvrtc_builtins_version_equal": True,
            "clock_read_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "formal_worker_count": 0,
        }
        runtime_preflight["preflight_sha256"] = runtime_digest(
            runtime_preflight)
        controller = {
            "schema": "rtdl.goal5802.formal_controller_result.v2",
            "status": "COMPLETE",
            "freeze_file_sha256": freeze_sha,
            "execution_authority_sha256": authority_sha,
            "runtime_manifest_sha256": runtime_sha,
            "worker_count": 504,
            "comparative_worker_count": 432,
            "build_cold_absolute_worker_count": 72,
            "passed_worker_count": 504,
            "failed_worker_count": 0,
            "retry_count": 0,
            "replacement_count": 0,
            "comparative_rows": comparative,
            "build_cold_absolute_rows": build,
            "build_cold_enters_comparative_gate": False,
            "host_code_snapshot": {
                "schema": "rtdl.goal5802.host_code_snapshot.v1",
                "file_count": len(snapshot_rows),
                "payload_bytes": sum(item["bytes"] for item in snapshot_rows),
                "rows_sha256": contract.digest(snapshot_rows),
                "pycache_file_count": 0, "readonly": True,
            },
            "runtime_preflight": runtime_preflight,
            "preworker_combined_runtime_revalidation": {
                "receipt_sha256": "8" * 64,
                "venv_member_tree_sha256": "9" * 64,
            },
            "numba_llvmlite_runtime_authority": compiler_runtime_authority,
            "post_execution_runtime_revalidation": {
                "status": (
                    "PASS__ALL_RUNTIME_PAYLOADS_REHASHED_AFTER_FINAL_WORKER"),
                "runtime_manifest_file_sha256": runtime_sha,
                "combined_runtime_receipt_sha256": "8" * 64,
                "combined_runtime_full_venv_member_tree_sha256": "9" * 64,
                "rtdsl_package_file_count": freeze["product_binding"][
                    "rtdsl_package_file_count"],
                "rtdsl_package_tree_sha256": freeze["product_binding"][
                    "rtdsl_package_tree_sha256"],
            },
            "measurement_boundary_contract": {
                "DEPLOYMENT_COLD_primary_estimator":
                    "WARM_PROCESS_DEPLOYMENT_COLD",
                "process_cold_claimed": False,
                "process_startup_and_admission_required_for_all_three_arms":
                    True,
                "process_startup_and_admission_separately_published": True,
                "direct_pre_main_dso_loading": (
                    "SEPARATE_PROCESS_STARTUP_AND_ADMISSION_PHASE__NOT_PRIMARY"),
                "python_interpreter_imports_and_selected_runtime_preload": (
                    "SEPARATE_PROCESS_STARTUP_AND_ADMISSION_PHASE__NOT_PRIMARY"),
                "python_adapter_load_scope": (
                    "DEPLOYED_BYTES_AND_PUBLIC_RUNTIME_DEPLOYMENT_LOAD_ONLY"),
                "python_primary_timer_new_module_load_policy":
                    "REJECT_ALL_NOT_PRELOADED",
                "python_startup_flags_exact": [
                    "-I", "-S", "-B", "-P", "-c"],
                "pth_execution_in_build_kat_preflight_or_formal": False,
            },
        }
        primary = evaluate(freeze, controller)
        independent = recount(freeze, controller)
        projection_keys = (
            "status", "comparative_failure_worker_ids",
            "build_cold_failure_worker_ids", "comparative_validation_failures",
            "build_cold_validation_failures", "comparative_absolute",
            "phase_attribution", "comparative_ratios",
            "build_cold_absolute", "build_cold_enters_comparative_gate",
            "amortization", "all_primary_noninferiority_gates_pass",
            "retry_count", "replacement_count",
        )
        self.assertEqual(
            {key: primary[key] for key in projection_keys}, independent)
        self.assertEqual(len(primary["build_cold_absolute"]), 6)
        self.assertFalse(primary["build_cold_enters_comparative_gate"])
        self.assertEqual(len(primary["amortization"]), 2)
        self.assertTrue(all(row[
            "B_PYOPTIX_excluded_from_registered_equation"]
                            for row in primary["amortization"]))

        compiler_drift = copy.deepcopy(controller)
        drift_receipt = next(
            item for item in compiler_drift["build_cold_absolute_rows"]
            if item["schedule_row"]["arm"] == contract.ARMS[2])
        drift_identity = drift_receipt["worker_result"][
            "compiler_runtime_identity"]
        drift_identity["actual_loaded_module_files"][0]["sha256"] = "9" * 64
        drift_identity["actual_loaded_module_files_sha256"] = contract.digest(
            drift_identity["actual_loaded_module_files"])
        drift_identity.pop("identity_sha256")
        drift_identity["identity_sha256"] = contract.digest(drift_identity)
        primary_drift = evaluate(freeze, compiler_drift)
        independent_drift = recount(freeze, compiler_drift)
        drift_worker_id = drift_receipt["schedule_row"]["worker_id"]
        self.assertIn(
            drift_worker_id, primary_drift["build_cold_failure_worker_ids"])
        self.assertIn(
            drift_worker_id,
            independent_drift["build_cold_failure_worker_ids"])

        one_build_failure = copy.deepcopy(controller)
        one_build_failure["build_cold_absolute_rows"][0]["status"] = \
            "FAIL__NO_RETRY_OR_REPLACEMENT"
        one_build_failure["status"] = \
            "COMPLETE_WITH_FAILED_ROWS__NO_RETRY_OR_REPLACEMENT"
        one_build_failure["passed_worker_count"] = 503
        one_build_failure["failed_worker_count"] = 1
        partial = evaluate(freeze, one_build_failure)
        self.assertEqual(len(partial["comparative_ratios"]), 18)
        self.assertTrue(all(row["status"] == "ESTABLISHED"
                            for row in partial["comparative_ratios"]))
        self.assertEqual(len(partial["build_cold_absolute"]), 6)


if __name__ == "__main__":
    unittest.main()
