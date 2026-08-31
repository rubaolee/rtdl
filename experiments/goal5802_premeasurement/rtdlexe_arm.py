#!/usr/bin/env python3
"""Final clean-installed ``.rtdlexe`` adapter for Goal5802.

The adapter uses only the public ``install -> load -> prepare -> execute ->
close`` lifecycle.  It intentionally performs no build/materialize/compiler
operation and does not fall back to the Goal5798 ``rtdsl.v4`` route.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np

from .workload import RELATION_TASK, TRIANGLE_TASK


ARM = "D_RTDL_CLEAN_INSTALLED_RTLEXE"
RTDL_ROOT_MODULE = "rtdsl"
RTDL_IMPLEMENTATION_MODULE = "rtdsl.v4_rtdlexe"
RTDL_PLATFORM_PRELOADED_MODULES = ("fcntl",) if os.name == "posix" else ()
RTDL_REQUIRED_PRELOADED_MODULES = (
    RTDL_ROOT_MODULE,
    RTDL_IMPLEMENTATION_MODULE,
    "rtdsl.physical_execution_provenance",
    "atexit",
    "numpy",
    *RTDL_PLATFORM_PRELOADED_MODULES,
)
PRIMARY_TIMER_FORBIDDEN_ABSENT_MODULES = (
    "cuda.bindings.nvrtc",
    "experiments.goal5796_matched.pyoptix_baseline",
)


def _plain_measurement_evidence(value: Any) -> Any:
    """Materialize product-owned read-only views after the primary clock."""

    if isinstance(value, Mapping):
        return {
            str(key): _plain_measurement_evidence(item)
            for key, item in value.items()
        }
    if isinstance(value, tuple):
        return tuple(_plain_measurement_evidence(item) for item in value)
    if isinstance(value, list):
        return [_plain_measurement_evidence(item) for item in value]
    return value


def preload_rtdl_runtime() -> tuple[Any, Any, dict[str, Any]]:
    """Resolve the public RTDL runtime and its lazy dependencies pre-clock."""

    if any(name in sys.modules for name in PRIMARY_TIMER_FORBIDDEN_ABSENT_MODULES):
        raise RuntimeError(
            "Goal5802 RTDL admission found compiler/baseline module preloaded")
    try:
        module = importlib.import_module(RTDL_ROOT_MODULE)
        implementation = importlib.import_module(RTDL_IMPLEMENTATION_MODULE)
        for name in RTDL_REQUIRED_PRELOADED_MODULES[2:]:
            importlib.import_module(name)
        # Force the package's intentionally lazy public surface now, not after
        # the primary clock starts.
        required_public_symbols = (
            "install_rtdlexe_deployment", "load_rtdlexe",
            "BoundedRelationStaticInput", "BoundedRelationBatch",
            "BoundedRelationBufferStaticInput",
            "BoundedRelationBufferBatch",
            "TriangleReductionStaticInput", "TriangleReductionBatch",
            "TriangleReductionBufferStaticInput",
            "TriangleReductionBufferBatch",
        )
        public_symbols = {
            name: getattr(module, name) for name in required_public_symbols
        }
    except BaseException as error:
        raise RuntimeError(
            "Goal5802 RTDL runtime preload failed before primary clock") \
            from error
    missing_modules = sorted(
        name for name in RTDL_REQUIRED_PRELOADED_MODULES
        if name not in sys.modules)
    forbidden_present = sorted(
        name for name in PRIMARY_TIMER_FORBIDDEN_ABSENT_MODULES
        if name in sys.modules)
    identity_mismatches = sorted(
        name for name, value in public_symbols.items()
        if value is not getattr(implementation, name))
    if missing_modules or forbidden_present or identity_mismatches:
        raise RuntimeError({
            "rtdl_runtime_preload_missing_modules": missing_modules,
            "compiler_or_baseline_modules_present": forbidden_present,
            "public_implementation_identity_mismatches": identity_mismatches,
        })
    if "rtdsl.v4" in sys.modules:
        raise RuntimeError("legacy rtdsl.v4 route entered Goal5802 admission")
    receipt = {
        "schema": "rtdl.goal5802.python_runtime_preload.v1",
        "status": "PASS__BEFORE_PRIMARY_CLOCK",
        "arm": ARM,
        "runtime_module": RTDL_ROOT_MODULE,
        "implementation_module": RTDL_IMPLEMENTATION_MODULE,
        "required_preloaded_modules": list(RTDL_REQUIRED_PRELOADED_MODULES),
        "forbidden_absent_modules": list(
            PRIMARY_TIMER_FORBIDDEN_ABSENT_MODULES),
        "public_symbol_identity_match_count": len(public_symbols),
        "legacy_rtdsl_v4_loaded": False,
        "runtime_import_inside_primary_timer": False,
    }
    return module, implementation, receipt


def _sha(path: Path) -> str:
    with path.open("rb") as handle:
        value = hashlib.sha256()
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


@dataclass(frozen=True)
class RTDLDeploymentPaths:
    artifact: Path
    authority: Path
    trust_root: Path
    trust_head: Path
    trust_package: Path
    native_library: Path
    deployment_id: str

    def identities(self) -> dict[str, object]:
        return {
            "artifact_sha256": _sha(self.artifact),
            "authority_sha256": _sha(self.authority),
            "trust_root_sha256": _sha(self.trust_root),
            "trust_head_sha256": _sha(self.trust_head),
            "trust_package_sha256": _sha(self.trust_package),
            "native_sha256": _sha(self.native_library),
            "deployment_id": self.deployment_id,
        }


class RTDLExecutableAdapter:
    """One task-specific public lifecycle with explicit load/prepare phases."""

    def __init__(self, task: str, workload: dict[str, Any],
                 paths: RTDLDeploymentPaths, *,
                 preloaded_runtime: Any | None = None,
                 preloaded_implementation: Any | None = None,
                 runtime_preload_receipt: dict[str, Any] | None = None):
        if task not in {RELATION_TASK, TRIANGLE_TASK}:
            raise ValueError(f"unsupported Goal5802 task: {task}")
        self.task = task
        self.workload = workload
        self.paths = paths
        if preloaded_runtime is None or preloaded_implementation is None:
            preloaded_runtime, preloaded_implementation, \
                runtime_preload_receipt = preload_rtdl_runtime()
        if runtime_preload_receipt is None:
            raise RuntimeError("RTDL runtime preload receipt is absent")
        if preloaded_runtime.__name__ != RTDL_ROOT_MODULE \
                or preloaded_implementation.__name__ \
                != RTDL_IMPLEMENTATION_MODULE:
            raise RuntimeError("RTDL preloaded runtime module differs")
        self.module: Any = preloaded_runtime
        self.implementation_module: Any = preloaded_implementation
        self._runtime_preload_receipt = dict(runtime_preload_receipt)
        self._loaded = False
        self.loaded: Any | None = None
        self.provider: Any | None = None
        self.prepared: Any | None = None
        self._prepared_closed = False
        self._provider_closed = False
        self.batch: Any | None = None
        self._measurement_execute: Any | None = None
        self.executed_executable_identity_sha256: str | None = None
        self.expected_relation_rows = (
            tuple(tuple(row) for row in workload["expected_rows"])
            if task == RELATION_TASK else None)

    def load(self) -> None:
        if self._loaded:
            raise RuntimeError("RTDL adapter load called twice")
        module = self.module
        module_path = Path(module.__file__).resolve()
        if "experiments/goal5798" in module_path.as_posix():
            raise RuntimeError("legacy Goal5798 RTDL route imported")
        deployment = module.install_rtdlexe_deployment(
            trust_root_path=self.paths.trust_root,
            trust_head_path=self.paths.trust_head,
            trust_package_path=self.paths.trust_package,
            deployment_id=self.paths.deployment_id,
        )
        self.loaded = module.load_rtdlexe(
            artifact_path=self.paths.artifact,
            authority_path=self.paths.authority,
            deployment=deployment,
        )
        self._loaded = True

    def bind_provider(self) -> Any:
        """Explicitly acquire the Goal5807 provider-ready capability.

        The Goal5802 default remains the raw ``loaded.prepare(..., path)``
        lifecycle.  Only a caller that invokes this method opts into the new
        provider-ready boundary.
        """

        if self.loaded is None or not self._loaded:
            raise RuntimeError("RTDL adapter provider bind precedes load")
        if self.prepared is not None:
            raise RuntimeError("RTDL adapter provider bind follows prepare")
        if self.provider is not None:
            raise RuntimeError("RTDL adapter provider bind called twice")
        bind = getattr(self.loaded, "bind_provider", None)
        if not callable(bind):
            raise RuntimeError("RTDL runtime lacks provider-ready public API")
        self.provider = bind(native_library_path=self.paths.native_library)
        return self.provider

    def prepare(self) -> None:
        if self.loaded is None or not self._loaded:
            raise RuntimeError("RTDL adapter prepare precedes load")
        if self.prepared is not None:
            raise RuntimeError("RTDL adapter prepare called twice")
        module = self.module
        if self.task == RELATION_TASK:
            indexed_rows = self.workload["indexed"]
            source_rows = self.workload["sources"]
            indexed_bounds = np.asarray(
                [row[:4] for row in indexed_rows], dtype="<f4", order="C")
            indexed_ids = np.asarray(
                [row[4] for row in indexed_rows], dtype="<u4", order="C")
            source_bounds = np.asarray(
                [row[:4] for row in source_rows], dtype="<f4", order="C")
            source_ids = np.asarray(
                [row[4] for row in source_rows], dtype="<u4", order="C")
            static = module.BoundedRelationBufferStaticInput(
                indexed_bounds_f32le=indexed_bounds,
                indexed_ids_u32le=indexed_ids,
                indexed_count=len(indexed_rows),
            )
            self.batch = module.BoundedRelationBufferBatch(
                source_bounds_f32le=source_bounds,
                source_ids_u32le=source_ids,
                source_count=len(source_rows),
                # Goal5802 applies exactly one route-independent oracle below.
                # Supplying it here would make the public product compare once
                # and this adapter compare the same rows a second time.
                expected_rows=None,
            )
        else:
            # Use the public typed-buffer front door, matching the ordinary
            # NumPy/CuPy preparation style of the PyOptiX arm.  RTDL freezes
            # the bytes and the native boundary still validates every finite
            # vertex, triangle index, ray and tmax before any OptiX launch.
            vertices = np.asarray(
                self.workload["vertices"], dtype="<f4", order="C")
            triangle_count = len(vertices) // 3
            triangles = np.arange(
                3 * triangle_count, dtype="<u4").reshape(triangle_count, 3)
            query_rows = self.workload["queries"]
            origins = np.asarray(
                [row[0] for row in query_rows], dtype="<f4", order="C")
            directions = np.asarray(
                [row[1] for row in query_rows], dtype="<f4", order="C")
            maxima = np.asarray(
                [row[2] for row in query_rows], dtype="<f4", order="C")
            weights = np.asarray(
                self.workload["weights"], dtype="<u8", order="C")
            static = module.TriangleReductionBufferStaticInput(
                vertices_f32le=vertices,
                triangles_u32le=triangles,
                vertex_count=len(vertices),
                triangle_count=triangle_count,
                event_capacity=len(self.workload["queries"]),
            )
            self.batch = module.TriangleReductionBufferBatch(
                query_origins_f32le=origins,
                query_directions_f32le=directions,
                query_tmax_f32le=maxima,
                query_count=len(query_rows),
                query_weights_u64le=weights,
                # The public owner performs the one route-independent scalar
                # oracle in the same place as the PyOptiX prepared owner.
                expected_reduced_u64=self.workload["expected_reduced_u64"],
            )
        if self.provider is None:
            self.prepared = self.loaded.prepare(
                static, native_library_path=self.paths.native_library)
        else:
            self.prepared = self.provider.prepare(static)
        self._prepared_closed = False

        # Bind the actual public prepared execution path once, outside every
        # steady-state timer.  The matched PyOptiX arm binds an equivalent
        # zero-argument closure around its prepared owner.  This prevents the
        # evaluation adapter itself from adding an RTDL-only Python frame.
        prepared = self.prepared
        batch = self.batch
        expected_relation_rows = self.expected_relation_rows
        if self.task == RELATION_TASK:
            def execute_prepared() -> Any:
                result = prepared.execute(batch, include_diagnostics=False)
                if result.output != expected_relation_rows:
                    raise RuntimeError(
                        "RTDL relation route-independent-oracle mismatch")
                return result
        else:
            def execute_prepared() -> Any:
                return prepared.execute(batch, include_diagnostics=False)
        self._measurement_execute = execute_prepared

    def measurement_execution_callable(self) -> Any:
        """Return the matched zero-argument prepared execution boundary."""

        if self._measurement_execute is None:
            raise RuntimeError("RTDL measurement execution precedes prepare")
        return self._measurement_execute

    def execute(self, *, diagnostics: bool = False) -> Any:
        """Run the product plus the one common, route-independent oracle.

        Measurement receipts, identity strings, schema copies and operation
        ledgers are deliberately materialized only after the caller stops the
        primary clock (see ``measurement_lifecycle_receipt`` and
        ``finalize_measurement_evidence``).
        """

        if self._measurement_execute is None:
            raise RuntimeError("RTDL adapter execute precedes prepare")
        if diagnostics:
            if self.prepared is None or self.batch is None:
                raise RuntimeError("RTDL adapter execute precedes prepare")
            result = self.prepared.execute(
                self.batch, include_diagnostics=True)
            if self.task == RELATION_TASK \
                    and result.output != self.expected_relation_rows:
                raise RuntimeError(
                    "RTDL relation route-independent-oracle mismatch")
            return result
        return self._measurement_execute()

    def _record_executed_identity(self, result: Any) -> None:
        observed_executable_identity = str(result.executable_identity_sha256)
        if self.executed_executable_identity_sha256 is None:
            self.executed_executable_identity_sha256 = observed_executable_identity
        elif self.executed_executable_identity_sha256 \
                != observed_executable_identity:
            raise RuntimeError("RTDL executed identity changed within one owner")

    def _validated_status_and_operation(
            self, result: Any) -> tuple[dict[str, Any], dict[str, Any]]:
        status = dict(result.device_status)
        if status.get("ok") is not True:
            raise RuntimeError(f"RTDL device status failure: {status}")
        operation = status.get("operation_receipt")
        if not isinstance(operation, dict) and not hasattr(operation, "items"):
            raise RuntimeError("RTDL execution lacks native operation receipt")
        operation = dict(operation)
        operation_fields = {
            "schema", "optix_launch_count", "host_blocking_boundary_count",
            "control_d2h_bytes", "output_d2h_bytes", "status_before_output",
            "output_d2h_after_status_failure", "role_counters_materialized",
            "prepared_input_reused", "dynamic_device_upload_call_count",
            "dynamic_device_upload_bytes", "dynamic_accel_build_count",
            "dynamic_explicit_sync_count", "dynamic_blocking_upload_call_count",
            "dynamic_input_generation",
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
        if set(operation) != operation_fields \
                or operation.get("schema") \
                != "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2" \
                or operation.get("status_before_output") is not True \
                or operation.get("output_d2h_after_status_failure") != 0 \
                or operation.get("role_counters_materialized") is not False \
                or operation.get("dynamic_blocking_upload_call_count") != 0:
            raise RuntimeError("RTDL native operation receipt schema differs")
        expected_machine = (
            {
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
            }
            if self.task == RELATION_TASK else
            {
                "semantic_compaction_launch_count": 0,
                "semantic_compaction_key_capacity": 0,
                "semantic_compaction_scratch_bytes": 0,
                "callback_status_kernel_launch_count": 0,
                "checked_product_kernel_launch_count": 0,
                "compact_control_finalizer_kernel_launch_count": 0,
                "total_auxiliary_cuda_kernel_launch_count": 0,
                "execution_parameter_h2d_bytes": 224,
                "execution_parameter_h2d_copy_call_count": 1,
                "stream_ordered_memset_call_count": 2,
                "status_d2h_copy_call_count": 1,
                "output_d2h_copy_call_count": 1,
            })
        if any(operation.get(key) != value
               for key, value in expected_machine.items()):
            raise RuntimeError("RTDL native auxiliary-operation receipt differs")
        return status, operation

    @staticmethod
    def _dynamic_receipt(operation: dict[str, Any]) -> dict[str, Any]:
        dynamic_fields = {
            "prepared_input_reused",
            "dynamic_device_upload_call_count",
            "dynamic_device_upload_bytes",
            "dynamic_accel_build_count",
            "dynamic_explicit_sync_count",
            "dynamic_blocking_upload_call_count",
            "dynamic_input_generation",
        }
        if not dynamic_fields.issubset(operation):
            raise RuntimeError(
                "RTDL native receipt lacks Goal5802 dynamic-input counters")
        dynamic_receipt = {
            key: operation[key] for key in sorted(dynamic_fields)
        }
        reused = dynamic_receipt["prepared_input_reused"]
        if type(reused) is not bool:
            raise RuntimeError("RTDL native prepared-input reuse flag is invalid")
        for key in dynamic_fields - {"prepared_input_reused"}:
            value = dynamic_receipt[key]
            if type(value) is not int or value < 0:
                raise RuntimeError(f"RTDL native dynamic counter invalid: {key}")
        if reused:
            if any(dynamic_receipt[key] != 0 for key in (
                    "dynamic_device_upload_call_count",
                    "dynamic_device_upload_bytes",
                    "dynamic_accel_build_count",
                    "dynamic_explicit_sync_count",
                    "dynamic_blocking_upload_call_count")):
                raise RuntimeError("RTDL reused input performed dynamic setup")
        elif dynamic_receipt["dynamic_device_upload_call_count"] <= 0:
            raise RuntimeError("RTDL first execute did not upload dynamic input")
        return dynamic_receipt

    def measurement_lifecycle_receipt(
            self, raw_result: Any) -> dict[str, Any]:
        """Build the per-execute lifecycle row after the primary clock."""

        self._record_executed_identity(raw_result)
        _status, operation = self._validated_status_and_operation(raw_result)
        return self._dynamic_receipt(operation)

    def finalize_measurement_evidence(
            self, result: Any) -> dict[str, Any]:
        """Validate/copy measurement-only evidence after the primary clock."""

        self._record_executed_identity(result)
        status, operation = self._validated_status_and_operation(result)
        dynamic_receipt = self._dynamic_receipt(operation)
        if status.get("role_counters_materialized") is not False \
                or tuple(result.role_counters):
            raise RuntimeError(
                "RTDL fast route role-counter transfer boundary differs")
        if self.task == RELATION_TASK:
            output = result.output
            expected = self.expected_relation_rows
            if not isinstance(output, tuple) \
                    or any(not isinstance(row, tuple) for row in output):
                raise RuntimeError("RTDL relation public output container drift")
            expected_raw_events = 2 * len(expected)
            observed_raw_events = status.get("validated_raw_event_count")
            if type(observed_raw_events) is not int \
                    or observed_raw_events != expected_raw_events:
                raise RuntimeError(
                    "RTDL relation compact-control raw-event count drift")
            raw_output_d2h_bytes = int(operation["output_d2h_bytes"])
            compact_control_d2h_bytes = int(
                operation["control_d2h_bytes"])
            host_boundaries = int(
                operation["host_blocking_boundary_count"])
            total_success_d2h_bytes = (
                compact_control_d2h_bytes + raw_output_d2h_bytes)
            if compact_control_d2h_bytes != 28 \
                    or raw_output_d2h_bytes != 32768 \
                    or host_boundaries != 2:
                raise RuntimeError(
                    "RTDL relation compact-status ABI is not Goal5799 symmetric")
            ledger = {
                "device_status": status,
                "output": output,
                "optix_launch_count": int(operation["optix_launch_count"]),
                "compact_status_control_d2h_bytes": compact_control_d2h_bytes,
                "raw_event_count": observed_raw_events,
                "semantic_unique_count": len(output),
                "semantic_compaction_launch_count": int(
                    operation["semantic_compaction_launch_count"]),
                "semantic_compaction_key_capacity": int(
                    operation["semantic_compaction_key_capacity"]),
                "semantic_compaction_scratch_bytes": int(
                    operation["semantic_compaction_scratch_bytes"]),
                "application_output_d2h_bytes": raw_output_d2h_bytes,
                "user_visible_output_bytes": len(output) * 8,
                "total_success_d2h_bytes": total_success_d2h_bytes,
                "status_output_commit_blocking_boundary_count": host_boundaries,
                "per_ray_d2h_bytes": 0,
                "per_ray_host_materialized": False,
                "traversal_receipt": result.traversal_receipt,
            }
        else:
            reduced = int(result.output)
            compact_status_d2h_bytes = int(
                operation["control_d2h_bytes"])
            scalar_d2h_bytes = int(operation["output_d2h_bytes"])
            host_boundaries = int(
                operation["host_blocking_boundary_count"])
            if compact_status_d2h_bytes != 12 or scalar_d2h_bytes != 8 \
                    or host_boundaries != 2 \
                    or int(status["success_total_product_d2h_bytes"]) != 20:
                raise RuntimeError(
                    "RTDL triangle compact-status ABI is not Goal5799 symmetric")
            ledger = {
                "device_status": status,
                "reduced_u64": reduced,
                "optix_launch_count": int(operation["optix_launch_count"]),
                "compact_status_control_d2h_bytes": compact_status_d2h_bytes,
                "application_output_d2h_bytes": scalar_d2h_bytes,
                "total_success_d2h_bytes": status[
                    "success_total_product_d2h_bytes"],
                "per_ray_d2h_bytes": 0,
                "per_ray_host_materialized": False,
                "status_output_commit_blocking_boundary_count": host_boundaries,
                "traversal_receipt": result.traversal_receipt,
            }
        ledger.update({
            "output_sha256": result.output_sha256,
            "executable_identity_sha256": result.executable_identity_sha256,
            "role_counters": list(result.role_counters),
            "dynamic_input_receipt": dynamic_receipt,
            "native_operation_receipt": operation,
        })
        for key in (
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
                "output_d2h_copy_call_count"):
            ledger[key] = int(operation[key])
        return _plain_measurement_evidence(ledger)

    def close_prepared(self) -> None:
        """Close only the application-prepared owner, at most once."""

        if self.prepared is None or self._prepared_closed:
            return
        self.prepared.close()
        self._prepared_closed = True

    def close_provider(self) -> None:
        """Close only an explicitly bound provider, after its owner."""

        if self.provider is None or self._provider_closed:
            return
        if self.prepared is not None and not self._prepared_closed:
            raise RuntimeError("RTDL provider close precedes prepared close")
        self.provider.close()
        self._provider_closed = True

    def close(self) -> None:
        # Preserve the exact Goal5802 raw behavior when no provider capability
        # was explicitly bound.
        if self.provider is None:
            if self.prepared is not None:
                self.prepared.close()
            return

        prepared_error: BaseException | None = None
        try:
            self.close_prepared()
        except BaseException as error:
            prepared_error = error
        provider_error: BaseException | None = None
        try:
            # If prepared close failed, the provider capability still must be
            # released.  This exceptional cleanup is the sole bypass of the
            # ordinary close_provider ordering check.
            if prepared_error is not None:
                self.provider.close()
                self._provider_closed = True
            else:
                self.close_provider()
        except BaseException as error:
            provider_error = error
        if prepared_error is not None and provider_error is not None:
            raise RuntimeError({
                "rtdl_prepared_close_error": repr(prepared_error),
                "rtdl_provider_close_error": repr(provider_error),
            }) from prepared_error
        if prepared_error is not None:
            raise prepared_error
        if provider_error is not None:
            raise provider_error

    def constructor_runtime_preload_receipt(self) -> dict[str, Any]:
        """Return already-materialized admission evidence outside the clock."""

        return dict(self._runtime_preload_receipt)

    def primary_timer_import_contract(self) -> dict[str, Any]:
        return {
            "required_preloaded_modules": list(RTDL_REQUIRED_PRELOADED_MODULES),
            "forbidden_absent_modules": list(
                PRIMARY_TIMER_FORBIDDEN_ABSENT_MODULES),
        }

    def runtime_identity(self) -> dict[str, object]:
        if not self._loaded:
            raise RuntimeError("RTDL runtime identity precedes load")
        package_path = Path(self.module.__file__).resolve(strict=True)
        implementation_path = Path(
            self.implementation_module.__file__).resolve(strict=True)
        if self.executed_executable_identity_sha256 is None:
            raise RuntimeError("RTDL runtime identity precedes execute")
        return {
            "rtdsl_init_path": str(package_path),
            "rtdsl_init_sha256": _sha(package_path),
            "rtdlexe_module_path": str(implementation_path),
            "rtdlexe_module_sha256": _sha(implementation_path),
            "executed_executable_identity_sha256": (
                self.executed_executable_identity_sha256),
        }


def plan() -> dict[str, object]:
    source = Path(__file__).resolve()
    text = source.read_text(encoding="utf-8")
    forbidden = [
        "experiments.goal5798" + "_premeasurement.rtdl_worker",
        "from rtdsl." + "v4 import",
        "materialize_" + "executable",
        "compile_callback_" + "program",
    ]
    hits = [literal for literal in forbidden if literal in text]
    if hits:
        raise RuntimeError(f"legacy/compiler route entered RTDL arm: {hits}")
    return {
        "schema": "rtdl.goal5802.rtdlexe_arm.plan.v1",
        "status": "PASS__PUBLIC_CLEAN_INSTALL_LIFECYCLE_SOURCE_PLAN_ONLY",
        "arm": ARM,
        "public_lifecycle": ["install", "load", "prepare", "execute", "close"],
        "compiler_or_materializer_call_count": 0,
        "runtime_module_preloaded_before_primary_clock": True,
        "adapter_load_imports_runtime_module": False,
        "deployment_cold_estimator_scope": "WARM_PROCESS",
        "triangle_output": "status_plus_checked_u64_scalar_only",
        "triangle_per_ray_d2h_bytes": 0,
        "source_sha256": _sha(source),
        "registered_performance_timing_count": 0,
        "formal_execution_authorized": False,
    }


if __name__ == "__main__":
    print(json.dumps(plan(), sort_keys=True))
