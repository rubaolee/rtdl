#!/usr/bin/env python3
"""Non-formal idiomatic PyOptiX two-application lifecycle pilot.

One process preloads the deployed PyOptiX runtime exactly once, then loads,
prepares, and executes the frozen Goal5802 relation and triangle workloads
exactly once each.  The process owns one natural OptixDeviceContext shared by
both applications; each application owns its pipeline, SBT, and prepared
owner.  This worker does not invent an RTDL-like session abstraction for the
baseline.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Callable, Mapping

_STARTUP_FORBIDDEN_MODULE_ROOTS = (
    "cuda", "cupy", "numpy", "optix", "rtdsl",
    "experiments.goal5796_matched.pyoptix_baseline",
    "experiments.goal5802_premeasurement.pyoptix_scalar_arm",
    "experiments.goal5802_premeasurement.rtdlexe_arm",
    "experiments.goal5802_premeasurement.workload",
)
_STARTUP_PRODUCT_MODULES = tuple(sorted(
    name for name in sys.modules
    if __name__ == "__main__" and any(
        name == root or name.startswith(root + ".")
        for root in _STARTUP_FORBIDDEN_MODULE_ROOTS)
))
if _STARTUP_PRODUCT_MODULES:
    raise RuntimeError({
        "goal5809_unclean_interpreter_start": _STARTUP_PRODUCT_MODULES,
    })

from scripts.goal5809_execution_identity import (
    admit_execution_identity,
    verify_loaded_modules,
    verify_loaded_pyoptix,
    verify_loaded_runtime_dependencies,
)
from scripts.goal5809_runtime_session_two_app_pilot import (
    TASK_KEYS,
    _PhaseLedger,
    _admit_target,
    _canonical,
    _digest,
    _plain,
    _sha,
)


SCHEMA = "rtdl.goal5809.pyoptix_two_app_pilot.v2"
STATUS = (
    "COMPLETE__DIAGNOSTIC_IDIOMATIC_PYOPTIX_"
    "TWO_APPLICATION_PILOT")
REQUIRED_PHASES = (
    "input_admission",
    "runtime_preload",
    "workload_materialization",
    "load_relation",
    "load_triangle",
    "first_session_admission",
    "first_app_prepare",
    "first_app_first_exact_execute",
    "second_app_prepare",
    "second_app_first_exact_execute",
    "close",
)


def _preload_runtime() -> tuple[Any, Any, Any, dict[str, Any], Any]:
    workload_module = importlib.import_module(
        "experiments.goal5802_premeasurement.workload")
    arm_module = importlib.import_module(
        "experiments.goal5802_premeasurement.pyoptix_scalar_arm")
    bulk_input_module = importlib.import_module(
        "experiments.goal5809_pyoptix_bulk_input")
    baseline, receipt = arm_module.preload_pyoptix_runtime()
    return workload_module, arm_module, baseline, receipt, bulk_input_module


def _load_application(
    *, task_key: str, target: Mapping[str, Any], workload: Mapping[str, Any],
    arm: Any, baseline: Any, preload_receipt: Mapping[str, Any],
) -> Any:
    files = target["files"]
    adapter = arm.PyOptixScalarAdapter(
        workload["task"], dict(workload),
        ptx_path=Path(files["matched_ptx"]["path"]),
        compaction_cubin_path=(
            Path(files["relation_compaction_cubin"]["path"])
            if task_key == "relation" else None),
        preloaded_runtime=baseline,
        runtime_preload_receipt=dict(preload_receipt),
    )
    adapter.load()
    if adapter.ptx is None:
        raise RuntimeError(f"{task_key} PyOptiX PTX was not loaded")
    observed_ptx_sha256 = hashlib.sha256(adapter.ptx).hexdigest()
    if observed_ptx_sha256 != files["matched_ptx"]["sha256"]:
        raise RuntimeError(f"{task_key} loaded PyOptiX PTX identity differs")
    observed_compaction_cubin_sha256 = None
    if task_key == "relation":
        if adapter.compaction_cubin is None:
            raise RuntimeError("relation compaction cubin was not retained")
        observed_compaction_cubin_sha256 = hashlib.sha256(
            adapter.compaction_cubin).hexdigest()
        if observed_compaction_cubin_sha256 \
                != files["relation_compaction_cubin"]["sha256"]:
            raise RuntimeError("loaded relation compaction cubin differs")
    adapter.goal5809_loaded_binary_identity = {
        "observed_loaded_matched_ptx_sha256": observed_ptx_sha256,
        "observed_loaded_relation_compaction_cubin_sha256": (
            observed_compaction_cubin_sha256),
        "retained_bytes_checked_before_prepare": True,
    }
    return adapter


def _admit_shared_context(*, arm: Any, baseline: Any) -> tuple[Any, Any]:
    """Create the sole natural PyOptiX device context for both apps."""

    context, logger = arm._make_validation_off_context(baseline)
    set_cache_enabled = getattr(context, "setCacheEnabled", None)
    if not callable(set_cache_enabled):
        raise RuntimeError(
            "PyOptiX context does not expose disk-cache disable control")
    set_cache_enabled(False)
    return context, logger


def _prepare_on_shared_context(
    *, task_key: str, adapter: Any, arm: Any, bulk_input: Any,
    shared_context: Any,
) -> None:
    """Build one task owner on the already admitted shared context.

    This is the existing idiomatic adapter's preparation body with its
    hard-coded per-call context creation removed.  All pipeline, SBT, GAS,
    compaction, and owner implementations remain the reviewed Goal5802 ones.
    """

    if not adapter._loaded or adapter.ptx is None:
        raise RuntimeError("PyOptiX shared-context prepare precedes load")
    if adapter.owner is not None or adapter.context is not None:
        raise RuntimeError("PyOptiX shared-context prepare called twice")
    baseline = adapter.baseline
    adapter.context = shared_context
    task_kind = "relation" if task_key == "relation" else "triangle"
    adapter.pipeline, adapter.pipeline_keepalive, _logs = \
        arm._build_comparative_pipeline(
            baseline, shared_context, adapter.ptx, task=task_kind)
    adapter.sbt, adapter.sbt_keepalive = baseline.make_sbt(
        adapter.pipeline_keepalive)
    if task_key == "relation":
        if adapter.compaction_cubin is None \
                or adapter._compaction_cubin_memfd is None:
            raise RuntimeError("relation compaction cubin was not loaded")
        arm._validate_write_sealed_memfd(adapter._compaction_cubin_memfd)
        adapter.compaction_module = baseline.cp.RawModule(
            path=adapter._compaction_cubin_memfd["proc_fd_path"])
        adapter.compaction_kernel = adapter.compaction_module.get_function(
            "goal5802_relation_unique_compact")
        fixture = {
            "indexed": adapter.workload["indexed"],
            "sources": adapter.workload["sources"],
            "minimum_overlap": adapter.workload["minimum_overlap_f32"],
            "capacity": adapter.workload["semantic_capacity"],
            "expected_rows": adapter.workload["expected_rows"],
        }
        host_inputs = bulk_input.pack_relation_host_inputs(
            baseline, adapter.workload)
        adapter.owner = arm.DeferredRelationPrepared(
            baseline, shared_context, adapter.pipeline, adapter.sbt, fixture,
            pipeline_keepalive=adapter.pipeline_keepalive,
            sbt_keepalive=adapter.sbt_keepalive,
            compaction_kernel=adapter.compaction_kernel,
            host_inputs=host_inputs,
            validate_expected_rows=False,
            record_operation_evidence=adapter.record_operation_evidence)
    else:
        host_inputs = bulk_input.pack_triangle_host_inputs(
            baseline, adapter.workload)
        adapter.owner = arm.ScalarTrianglePrepared(
            baseline, shared_context, adapter.pipeline, adapter.sbt,
            adapter.workload,
            pipeline_keepalive=adapter.pipeline_keepalive,
            sbt_keepalive=adapter.sbt_keepalive,
            host_inputs=host_inputs,
            record_operation_evidence=adapter.record_operation_evidence)
    owner = adapter.owner
    adapter._measurement_execute = lambda: owner.execute()


def _prepare_once(
    *, task_key: str, adapter: Any,
    arm: Any, bulk_input: Any, shared_context: Any,
) -> None:
    _prepare_on_shared_context(
        task_key=task_key, adapter=adapter, arm=arm,
        bulk_input=bulk_input,
        shared_context=shared_context)


def _execute_once(
    *, task_key: str, adapter: Any, workload: Mapping[str, Any],
) -> dict[str, Any]:
    result = adapter.execute()
    if task_key == "relation":
        expected = workload["expected_rows"]
        output = result.output
        if type(output) is not list \
                or any(type(row) is not list for row in output):
            raise RuntimeError("relation PyOptiX output type differs")
        # Goal5809 disables the owner's default equality so this worker is the
        # sole oracle site.  That makes the receipt independently meaningful
        # without charging PyOptiX for a second 4,096-row comparison.
        exact = output == expected
        oracle_validation_site = "GOAL5809_WORKER_EXACT_ROW_EQUALITY"
        oracle_validation_count = 1
        status_ok = int(result.device_status) == 0 \
            and int(result.device_overflow) == 0
        output_count = len(output) if isinstance(output, list) else None
    else:
        expected = int(workload["expected_reduced_u64"])
        output = int(result.reduced_u64)
        exact = output == expected
        oracle_validation_site = "OWNER_AND_PILOT_SCALAR_CHECK"
        oracle_validation_count = 2
        status_ok = int(result.device_status) == 0
        output_count = 1
    if not exact:
        raise RuntimeError(f"{task_key} PyOptiX exact oracle mismatch")
    if not status_ok:
        raise RuntimeError(f"{task_key} PyOptiX device status is not OK")
    return {
        "task": task_key,
        "execute_call_count": 1,
        "warmup_execute_call_count": 0,
        "exact_oracle_passed": True,
        "device_status_ok": True,
        "output_count": output_count,
        "oracle_validation_site": oracle_validation_site,
        "oracle_validation_count": oracle_validation_count,
        "evidence_hashing_inside_first_exact_execute_phase": False,
        **dict(adapter.goal5809_loaded_binary_identity),
    }


def _close_all(adapters: list[Any]) -> None:
    errors: list[BaseException] = []
    for adapter in reversed(adapters):
        try:
            adapter.close()
        except BaseException as error:
            errors.append(error)
    if errors:
        raise RuntimeError({
            "pyoptix_two_app_close_errors": [repr(row) for row in errors],
        }) from errors[0]


def _run_impl(
    args: argparse.Namespace, *, clock: Callable[[], int],
) -> dict[str, Any]:
    ledger = _PhaseLedger(clock, required_phases=REQUIRED_PHASES)
    with ledger.phase("input_admission"):
        admitted = _admit_target(
            args.target_manifest,
            expected_file_sha256=args.expected_target_manifest_sha256)
        admitted_execution_identity = admit_execution_identity(
            args.execution_identity_manifest,
            expected_file_sha256=(
                args.expected_execution_identity_manifest_sha256),
            require_runtime_environment=True)
        if args.first_app not in TASK_KEYS:
            raise RuntimeError("unsupported first application")
        first_task = args.first_app
        second_task = "triangle" if first_task == "relation" else "relation"

    with ledger.phase("runtime_preload"):
        workload_module, arm, baseline, preload_receipt, bulk_input = \
            _preload_runtime()

    with ledger.phase("workload_materialization"):
        workloads = {
            "relation": workload_module.relation_workload(),
            "triangle": workload_module.triangle_workload(),
        }

    adapters: dict[str, Any] = {}
    shared_context = None
    shared_logger = None
    app_evidence: dict[str, dict[str, Any]] = {}
    primary_error: BaseException | None = None
    close_error: BaseException | None = None
    try:
        for task_key in TASK_KEYS:
            with ledger.phase(f"load_{task_key}"):
                adapters[task_key] = _load_application(
                    task_key=task_key, target=admitted["target"],
                    workload=workloads[task_key], arm=arm, baseline=baseline,
                    preload_receipt=preload_receipt)
        with ledger.phase("first_session_admission"):
            shared_context, shared_logger = _admit_shared_context(
                arm=arm, baseline=baseline)
        for ordinal, task_key in enumerate((first_task, second_task)):
            ordinal_name = "first_app" if ordinal == 0 else "second_app"
            with ledger.phase(f"{ordinal_name}_prepare"):
                _prepare_once(
                    task_key=task_key, adapter=adapters[task_key], arm=arm,
                    bulk_input=bulk_input,
                    shared_context=shared_context)
            with ledger.phase(f"{ordinal_name}_first_exact_execute"):
                app_evidence[task_key] = _execute_once(
                    task_key=task_key, adapter=adapters[task_key],
                    workload=workloads[task_key])
    except BaseException as error:
        primary_error = error
    finally:
        with ledger.phase("close"):
            try:
                _close_all([
                    adapters[task_key]
                    for task_key in (first_task, second_task)
                    if task_key in adapters
                ])
            except BaseException as error:
                close_error = error
    if primary_error is not None and close_error is not None:
        raise RuntimeError({
            "pyoptix_two_app_primary_error": repr(primary_error),
            "pyoptix_two_app_close_error": repr(close_error),
        }) from primary_error
    if primary_error is not None:
        raise primary_error
    if close_error is not None:
        raise close_error

    if any(adapter.owner is not None for adapter in adapters.values()):
        raise RuntimeError("PyOptiX prepared owner remained after close")
    if adapters["relation"].compaction_cubin_loader_closed is not True:
        raise RuntimeError("PyOptiX relation cubin loader remained open")
    if shared_context is None \
            or any(adapter.context is not shared_context
                   for adapter in adapters.values()):
        raise RuntimeError("PyOptiX apps did not retain one shared context")

    phase_ledger = ledger.finish()
    loaded_identity = verify_loaded_pyoptix(
        admitted_execution_identity, optix_module=baseline.optix)
    extra_modules = {
        "goal5809_execution_identity_helper": sys.modules[
            "scripts.goal5809_execution_identity"],
        "goal5809_pyoptix_worker": sys.modules[__name__],
        "goal5809_rtdl_worker": sys.modules[
            "scripts.goal5809_runtime_session_two_app_pilot"],
        "goal5805_protocol_source": sys.modules[
            "experiments.goal5805_successor.protocol"],
        "goal5809_pyoptix_bulk_input_source": bulk_input,
        "goal5800_pyoptix_idiomatic_arm_source": sys.modules[
            "experiments.goal5800_pyoptix_owl.pyoptix_idiomatic_arm"],
        "pyoptix_baseline_source": baseline,
        "pyoptix_scalar_arm_source": arm,
        "workload_source": workload_module,
    }
    extra_loaded_identity = verify_loaded_modules(
        admitted_execution_identity, modules_by_role=extra_modules)
    runtime_dependency_identity = verify_loaded_runtime_dependencies(
        admitted_execution_identity,
        required_module_roots=(
            "numpy", "cupy", "cupy_backends", "cuda", "optix"),
        observed_versions={
            "numpy": str(baseline.np.__version__),
            "cupy": str(baseline.cp.__version__),
            "cuda-python": importlib.metadata.version("cuda-python"),
            "pyoptix": loaded_identity["distribution_version"],
            "optix-api": loaded_identity["api_version"],
        })
    loaded_identity = {
        **loaded_identity,
        "loaded_modules": extra_loaded_identity["loaded_modules"],
        "selected_goal5809_source_modules_verified": True,
        "complete_runtime_environment_tree_verified": True,
        "runtime_dependency_identity": runtime_dependency_identity,
    }
    target = admitted["target"]
    workload_source = Path(workload_module.__file__).resolve(strict=True)
    workload_bundle_sha256 = _digest(_plain(workloads))
    body: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "process_pid": os.getpid(),
        "scope": {
            "diagnostic_pilot_only": True,
            "nonformal_diagnostic": True,
            "paper_evidence": False,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "paper_claim_authorized": False,
            "inferential_claim_authorized": False,
            "threshold_or_noninferiority_claim_authorized": False,
            "ratio_computation_authorized": False,
            "direct_arm_count": 0,
            "direct_arm_present": False,
            "host_language_control_present": False,
            "design_attribution_authorized": False,
        },
        "lifecycle": {
            "arm": "PYOPTIX_IDIOMATIC_NATURAL_OWNERSHIP",
            "app_order": [first_task, second_task],
            "runtime_preload_call_count": 1,
            "loaded_application_count": 2,
            "prepare_call_count": 2,
            "execute_call_count": 2,
            "warmup_execute_call_count": 0,
            "application_close_count": 2,
            "runtime_session_count": 0,
            "runtime_session_admission_phase": (
                "NOT_APPLICABLE__ONE_SHARED_OPTIX_DEVICE_CONTEXT_INSTEAD"),
            "existing_adapter_prepare_call_count": 0,
            "shared_optix_device_context_admission_call_count": 1,
            "natural_device_context_owner_count": 1,
            "per_application_pipeline_build_count": 2,
            "per_application_sbt_build_count": 2,
            "per_application_prepared_owner_count": 2,
            "both_application_owners_use_exact_shared_context": True,
            "shared_context_retained_to_process_teardown": True,
            "shared_context_injection_scope": (
                "HARNESS_ONLY__EXISTING_GOAL5802_PIPELINE_SBT_AND_OWNER_"
                "IMPLEMENTATIONS_UNCHANGED"),
            "cuda_context_first_use_preserved": True,
            "application_prepare_first_use_preserved": True,
            "artifact_file_cache_coldness_preserved": False,
            "post_custody_admission_file_bytes_already_rehashed": True,
            "each_app_prepare_and_first_exact_execute_separately_observed": (
                True),
            "prepare_and_first_exact_execute_phase_rows_adjacent": (
                phase_ledger[
                    "prepare_and_first_exact_execute_phase_rows_adjacent"]),
            "zero_interphase_gap_claimed": False,
            "interphase_gaps_explicitly_recorded": True,
            "application_owners_retained_until_final_close_phase": True,
            "clean_interpreter_product_start_verified": True,
            "startup_forbidden_product_modules_observed": list(
                _STARTUP_PRODUCT_MODULES),
        },
        "phase_times_absolute": phase_ledger,
        "applications": {
            task_key: {
                **app_evidence[task_key],
                "matched_ptx_sha256": target["files"]["matched_ptx"][
                    "sha256"],
                "relation_compaction_cubin_sha256": (
                    target["files"]["relation_compaction_cubin"]["sha256"]
                    if task_key == "relation" else None),
            }
            for task_key in TASK_KEYS
        },
        "inputs": {
            "target_manifest_path": str(admitted["target_path"]),
            "target_manifest_file_sha256": admitted["target_file_sha256"],
            "target_manifest_semantic_sha256": target[
                "target_manifest_sha256"],
            "matched_ptx_sha256": target["files"]["matched_ptx"]["sha256"],
            "relation_compaction_cubin_sha256": target["files"][
                "relation_compaction_cubin"]["sha256"],
            "runtime_preload_receipt": _plain(preload_receipt),
            "runtime_module": baseline.__name__,
            "arm_module": arm.__name__,
            "shared_context_python_identity": id(shared_context),
            "shared_context_logger_present": shared_logger is not None,
            "workload_source_path": str(workload_source),
            "workload_source_sha256": _sha(workload_source),
            "workload_bundle_sha256": workload_bundle_sha256,
        },
        "execution_identity": {
            "manifest_file_sha256": admitted_execution_identity[
                "manifest_file_sha256"],
            "execution_identity_sha256": admitted_execution_identity[
                "execution_identity_sha256"],
            "file_count": admitted_execution_identity["file_count"],
            "files_rehashed": admitted_execution_identity["files_rehashed"],
            "runtime_environment_admission": (
                admitted_execution_identity["runtime_environment_admission"]),
            "loaded_module_verification_performed_after_phase_ledger": True,
            **loaded_identity,
        },
        "direct_arm_count": 0,
        "direct_arm_present": False,
        "host_language_control_present": False,
        "design_attribution_authorized": False,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    return {**body, "pilot_sha256": _digest(body)}


def _run(
    args: argparse.Namespace, *, clock: Callable[[], int] | None = None,
) -> dict[str, Any]:
    return _run_impl(args, clock=clock or time.perf_counter_ns)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument(
        "--expected-target-manifest-sha256", required=True)
    parser.add_argument(
        "--execution-identity-manifest", type=Path, required=True)
    parser.add_argument(
        "--expected-execution-identity-manifest-sha256", required=True)
    parser.add_argument(
        "--first-app", choices=TASK_KEYS, default="relation")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError("Goal5809 PyOptiX output already exists")
    result = _run(args)
    payload = _canonical(result) + b"\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as handle:
        handle.write(payload)
    sys.stdout.write(json.dumps({
        "output": str(args.output.resolve()),
        "output_bytes": len(payload),
        "pilot_sha256": result["pilot_sha256"],
        "registered_performance_timing_count": 0,
    }, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
