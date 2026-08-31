#!/usr/bin/env python3
"""Non-formal two-application RTDL runtime-session pilot.

This diagnostic executes the frozen Goal5802 relation and triangle workloads
through the public RTDL lifecycle.  Both executable artifacts are loaded, one
``RTDLRuntimeSession`` is opened from the first application, and that same
session prepares both applications.  Each application executes exactly once;
there is no warmup, repetition, threshold, inference, or paper claim.

The output reports absolute phase durations.  In particular, the first
application retains all process-first-use cost while each application's
prepare and first exact execute are reported as adjacent phase rows.  The
ledger records (and continuous boundaries include) the real interphase gaps;
it does not claim that two separate clock intervals have a zero-width gap.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping
from contextlib import contextmanager
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace
from typing import Any, Iterator

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

from experiments.goal5805_successor.protocol import (
    TARGET_SCHEMA,
    validate_target_manifest,
)
from scripts.goal5809_execution_identity import (
    admit_execution_identity,
    verify_loaded_modules,
    verify_loaded_rtdl,
    verify_loaded_runtime_dependencies,
)


SCHEMA = "rtdl.goal5809.runtime_session_two_app_pilot.v2"
STATUS = "COMPLETE__DIAGNOSTIC_TWO_APPLICATION_RUNTIME_SESSION_PILOT"
TASK_KEYS = ("relation", "triangle")
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
_SHA256_HEX = frozenset("0123456789abcdef")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _require_sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 \
            or any(character not in _SHA256_HEX for character in value):
        raise RuntimeError(f"{label} is not a lowercase SHA-256")
    return value


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {path}")
    return value


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


class _PhaseLedger:
    """Record non-overlapping absolute monotonic-clock phase intervals."""

    def __init__(
        self, clock: Callable[[], int], *,
        required_phases: tuple[str, ...] = REQUIRED_PHASES,
    ) -> None:
        self._clock = clock
        self._required_phases = required_phases
        self._rows: dict[str, dict[str, object]] = {}
        self._order: list[str] = []
        self._active = False

    @contextmanager
    def phase(self, name: str) -> Iterator[None]:
        if name in self._rows or name in self._order:
            raise RuntimeError(f"duplicate phase: {name}")
        if self._active:
            raise RuntimeError(f"nested phase: {name}")
        self._active = True
        self._order.append(name)
        start = self._clock()
        try:
            yield
        finally:
            end = self._clock()
            self._active = False
            self._rows[name] = {
                "ordinal": len(self._order) - 1,
                "start_perf_counter_ns": start,
                "end_perf_counter_ns": end,
                "duration_ns": end - start,
                "duration_ms": (end - start) / 1_000_000.0,
            }

    def finish(self) -> dict[str, object]:
        if tuple(self._order) != self._required_phases:
            raise RuntimeError({
                "runtime_session_pilot_phase_order": self._order,
                "required": list(self._required_phases),
            })
        rows = [self._rows[name] for name in self._order]
        if any(int(row["duration_ns"]) <= 0 for row in rows):
            raise RuntimeError("runtime-session pilot phase is not positive")
        if any(
            int(rows[index]["end_perf_counter_ns"])
            > int(rows[index + 1]["start_perf_counter_ns"])
            for index in range(len(rows) - 1)
        ):
            raise RuntimeError("runtime-session pilot phases overlap")
        gaps = {
            f"{self._order[index]}->{self._order[index + 1]}": (
                int(rows[index + 1]["start_perf_counter_ns"])
                - int(rows[index]["end_perf_counter_ns"]))
            for index in range(len(rows) - 1)
        }
        prepare_execute_pairs = (
            ("first_app_prepare", "first_app_first_exact_execute"),
            ("second_app_prepare", "second_app_first_exact_execute"),
        )
        adjacent = all(
            self._order.index(execute) == self._order.index(prepare) + 1
            for prepare, execute in prepare_execute_pairs)
        if not adjacent or any(value < 0 for value in gaps.values()):
            raise RuntimeError("runtime-session pilot phase adjacency differs")
        return {
            "clock": "time.perf_counter_ns",
            "phase_order": list(self._order),
            "phases": {name: dict(self._rows[name]) for name in self._order},
            "required_absolute_phase_count": len(self._required_phases),
            "required_absolute_phases_all_observed": True,
            "phases_nonoverlapping": True,
            "interphase_gaps_ns": gaps,
            "interphase_gap_count": len(gaps),
            "interphase_gaps_all_nonnegative": True,
            "prepare_and_first_exact_execute_phase_rows_adjacent": True,
            "zero_interphase_gap_claimed": False,
        }


def _validate_candidate_manifest(
    value: Mapping[str, Any], *, target: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    candidates = value.get("candidates")
    if not isinstance(candidates, Mapping) \
            or not set(TASK_KEYS).issubset(candidates):
        raise RuntimeError("candidate manifest lacks relation and triangle")
    if value.get("registered_timing_count", 0) != 0:
        raise RuntimeError("candidate manifest carries registered timing")
    target_native = _require_sha256(
        target["files"]["native_library"]["sha256"],
        "target native SHA-256")
    if "native_sha256" in value and value["native_sha256"] != target_native:
        raise RuntimeError("candidate and target native identities differ")

    result: dict[str, dict[str, Any]] = {}
    deployment_ids: set[str] = set()
    for task_key in TASK_KEYS:
        row = candidates[task_key]
        if not isinstance(row, Mapping):
            raise RuntimeError(f"candidate row is not an object: {task_key}")
        required = {
            "artifact_path", "artifact_sha256", "authority_path",
            "authority_sha256", "deployment_id",
            "executable_identity_sha256",
        }
        if not required.issubset(row):
            raise RuntimeError(f"candidate row is incomplete: {task_key}")
        artifact = Path(str(row["artifact_path"])).resolve(strict=True)
        authority = Path(str(row["authority_path"])).resolve(strict=True)
        artifact_sha256 = _require_sha256(
            row["artifact_sha256"], f"{task_key} artifact SHA-256")
        authority_sha256 = _require_sha256(
            row["authority_sha256"], f"{task_key} authority SHA-256")
        executable_identity_sha256 = _require_sha256(
            row["executable_identity_sha256"],
            f"{task_key} executable identity")
        if _sha(artifact) != artifact_sha256:
            raise RuntimeError(f"{task_key} artifact bytes differ")
        if _sha(authority) != authority_sha256:
            raise RuntimeError(f"{task_key} authority bytes differ")
        deployment_id = row["deployment_id"]
        if not isinstance(deployment_id, str) or not deployment_id:
            raise RuntimeError(f"{task_key} deployment id is invalid")
        if deployment_id in deployment_ids:
            raise RuntimeError("candidate deployment ids are not distinct")
        deployment_ids.add(deployment_id)
        result[task_key] = {
            "artifact_path": artifact,
            "artifact_sha256": artifact_sha256,
            "authority_path": authority,
            "authority_sha256": authority_sha256,
            "deployment_id": deployment_id,
            "executable_identity_sha256": executable_identity_sha256,
        }
    return result


def _admit_target(
    target_manifest_path: Path, *, expected_file_sha256: str,
) -> dict[str, Any]:
    path = target_manifest_path.resolve(strict=True)
    file_sha256 = _sha(path)
    if file_sha256 != _require_sha256(
            expected_file_sha256, "expected target manifest SHA-256"):
        raise RuntimeError("target manifest file SHA-256 differs")
    target = _read_json(path)
    if target.get("schema") != TARGET_SCHEMA:
        raise RuntimeError("target manifest schema differs")
    validate_target_manifest(target, rehash=True)
    candidate_descriptor = target["files"]["candidate_manifest"]
    candidate_path = Path(str(candidate_descriptor["path"])).resolve(
        strict=True)
    candidate = _read_json(candidate_path)
    candidate_rows = _validate_candidate_manifest(candidate, target=target)
    return {
        "target_path": path,
        "target_file_sha256": file_sha256,
        "target": target,
        "candidate_path": candidate_path,
        "candidate_file_sha256": _sha(candidate_path),
        "candidates": candidate_rows,
    }


def _preload_runtime() -> tuple[Any, Any, Any, dict[str, Any], Any]:
    workload_module = importlib.import_module(
        "experiments.goal5802_premeasurement.workload")
    arm_module = importlib.import_module(
        "experiments.goal5802_premeasurement.rtdlexe_arm")
    bulk_input_module = importlib.import_module(
        "experiments.goal5809_pyoptix_bulk_input")
    runtime, implementation, receipt = arm_module.preload_rtdl_runtime()
    return workload_module, runtime, implementation, receipt, bulk_input_module


def _load_application(
    *, task_key: str, admitted: Mapping[str, Any], runtime: Any,
) -> Any:
    row = admitted["candidates"][task_key]
    files = admitted["target"]["files"]
    deployment = runtime.install_rtdlexe_deployment(
        trust_root_path=Path(files["trust_root"]["path"]),
        trust_head_path=Path(files["trust_head"]["path"]),
        trust_package_path=Path(files["trust_package"]["path"]),
        deployment_id=row["deployment_id"],
    )
    loaded = runtime.load_rtdlexe(
        artifact_path=row["artifact_path"],
        authority_path=row["authority_path"],
        deployment=deployment,
    )
    observed_identity = str(loaded.executable_identity_sha256)
    if observed_identity != row["executable_identity_sha256"]:
        raise RuntimeError(f"{task_key} loaded executable identity differs")
    return loaded


def _build_public_inputs(
    *, task_key: str, workload: Mapping[str, Any], runtime: Any, numpy: Any,
    bulk_input: Any,
) -> tuple[Any, Any, object, dict[str, Any]]:
    bulk_abi = SimpleNamespace(
        np=numpy,
        BOX_DTYPE=numpy.dtype([
            ("lower_x", "f4"), ("lower_y", "f4"), ("lower_z", "f4"),
            ("upper_x", "f4"), ("upper_y", "f4"), ("upper_z", "f4"),
            ("item_id", "u4"),
        ], align=True),
        RAY_DTYPE=numpy.dtype([
            ("origin_x", "f4"), ("origin_y", "f4"),
            ("origin_z", "f4"), ("direction_x", "f4"),
            ("direction_y", "f4"), ("direction_z", "f4"),
        ], align=True),
    )
    if task_key == "relation":
        packed = bulk_input.pack_relation_host_inputs(bulk_abi, workload)
        indexed, sources = packed.checked_arrays(bulk_abi)

        def columns(value: Any) -> tuple[Any, Any]:
            bounds = numpy.empty((len(value), 4), dtype="<f4")
            bounds[:, 0] = value["lower_x"]
            bounds[:, 1] = value["lower_y"]
            bounds[:, 2] = value["upper_x"]
            bounds[:, 3] = value["upper_y"]
            ids = numpy.ascontiguousarray(value["item_id"], dtype="<u4")
            return bounds, ids

        indexed_bounds, indexed_ids = columns(indexed)
        source_bounds, source_ids = columns(sources)
        static = runtime.BoundedRelationBufferStaticInput(
            indexed_bounds_f32le=indexed_bounds,
            indexed_ids_u32le=indexed_ids,
            indexed_count=len(indexed),
        )
        batch = runtime.BoundedRelationBufferBatch(
            source_bounds_f32le=source_bounds,
            source_ids_u32le=source_ids,
            source_count=len(sources),
            expected_rows=None,
        )
        oracle = tuple(tuple(row) for row in workload["expected_rows"])
        return static, batch, oracle, {
            **packed.receipt(),
            "rtdl_public_column_projection": "NUMPY_FIXED_COLUMN_VECTORIZED",
        }

    packed = bulk_input.pack_triangle_host_inputs(bulk_abi, workload)
    vertices, rays, weights, maximum = packed.checked_arrays(bulk_abi)
    triangle_count = len(vertices) // 3
    triangles = numpy.arange(
        3 * triangle_count, dtype="<u4").reshape(triangle_count, 3)
    origins = numpy.empty((len(rays), 3), dtype="<f4")
    origins[:, 0] = rays["origin_x"]
    origins[:, 1] = rays["origin_y"]
    origins[:, 2] = rays["origin_z"]
    directions = numpy.empty((len(rays), 3), dtype="<f4")
    directions[:, 0] = rays["direction_x"]
    directions[:, 1] = rays["direction_y"]
    directions[:, 2] = rays["direction_z"]
    maxima = numpy.full(len(rays), maximum, dtype="<f4")
    static = runtime.TriangleReductionBufferStaticInput(
        vertices_f32le=vertices,
        triangles_u32le=triangles,
        vertex_count=len(vertices),
        triangle_count=triangle_count,
        event_capacity=len(rays),
    )
    oracle = int(workload["expected_reduced_u64"])
    batch = runtime.TriangleReductionBufferBatch(
        query_origins_f32le=origins,
        query_directions_f32le=directions,
        query_tmax_f32le=maxima,
        query_count=len(rays),
        query_weights_u64le=weights,
        expected_reduced_u64=oracle,
    )
    return static, batch, oracle, {
        **packed.receipt(),
        "rtdl_public_column_projection": "NUMPY_FIXED_COLUMN_VECTORIZED",
    }


def _prepare_once(
    *, task_key: str, session: Any, loaded: Any,
    workload: Mapping[str, Any], runtime: Any, numpy: Any, bulk_input: Any,
) -> tuple[Any, Any, object, dict[str, Any]]:
    static, batch, oracle, packing_receipt = _build_public_inputs(
        task_key=task_key, workload=workload, runtime=runtime, numpy=numpy,
        bulk_input=bulk_input)
    prepared = session.prepare(loaded, static)
    return prepared, batch, oracle, packing_receipt


def _execute_once(
    *, task_key: str, prepared: Any, batch: Any, oracle: object,
    packing_receipt: Mapping[str, Any], loaded: Any,
) -> dict[str, Any]:
    result = prepared.execute(batch, include_diagnostics=False)
    if task_key == "relation":
        output = result.output
        exact = output == oracle
        output_count = len(output) if isinstance(output, tuple) else None
    else:
        output = int(result.output)
        exact = output == oracle
        output_count = 1
    if not exact:
        raise RuntimeError(f"{task_key} exact oracle mismatch")
    status = result.device_status
    if status.get("ok") is not True:
        raise RuntimeError(f"{task_key} device status is not OK")
    executable_identity = str(result.executable_identity_sha256)
    if executable_identity != str(loaded.executable_identity_sha256):
        raise RuntimeError(f"{task_key} execution identity differs")
    evidence = {
        "task": task_key,
        "execute_call_count": 1,
        "warmup_execute_call_count": 0,
        "exact_oracle_passed": True,
        "device_status_ok": True,
        "output_count": output_count,
        "executable_identity_sha256": executable_identity,
        "include_diagnostics": False,
        "evidence_hashing_inside_prepare_or_first_exact_execute_phase": False,
        "input_packing": packing_receipt,
    }
    return evidence


def _close_all(prepared: list[Any], session: Any | None) -> None:
    errors: list[BaseException] = []
    for owner in reversed(prepared):
        try:
            owner.close()
        except BaseException as error:
            errors.append(error)
    if session is not None:
        try:
            session.close()
        except BaseException as error:
            errors.append(error)
    if errors:
        raise RuntimeError({
            "runtime_session_pilot_close_errors": [repr(row) for row in errors],
        }) from errors[0]


def _run_impl(
    args: argparse.Namespace, *, clock: Callable[[], int],
) -> dict[str, Any]:
    ledger = _PhaseLedger(clock)
    with ledger.phase("input_admission"):
        admitted = _admit_target(
            args.target_manifest,
            expected_file_sha256=args.expected_target_manifest_sha256)
        admitted_execution_identity = admit_execution_identity(
            args.execution_identity_manifest,
            expected_file_sha256=(
                args.expected_execution_identity_manifest_sha256),
            require_runtime_environment=True)
        first_task = args.first_app
        second_task = "triangle" if first_task == "relation" else "relation"

    with ledger.phase("runtime_preload"):
        workload_module, runtime, implementation, preload_receipt, \
            bulk_input = _preload_runtime()
        numpy = importlib.import_module("numpy")

    with ledger.phase("workload_materialization"):
        workloads = {
            "relation": workload_module.relation_workload(),
            "triangle": workload_module.triangle_workload(),
        }

    loaded: dict[str, Any] = {}
    # Keep both artifact-load phases in one stable order.  ``first_app`` only
    # selects which loaded executable pays provider/session first use.
    for task_key in TASK_KEYS:
        with ledger.phase(f"load_{task_key}"):
            loaded[task_key] = _load_application(
                task_key=task_key, admitted=admitted, runtime=runtime)

    session = None
    prepared: list[Any] = []
    app_evidence: dict[str, dict[str, Any]] = {}
    primary_error: BaseException | None = None
    close_error: BaseException | None = None
    try:
        with ledger.phase("first_session_admission"):
            native_path = Path(
                admitted["target"]["files"]["native_library"]["path"])
            session = loaded[first_task].open_runtime_session(native_path)

        for ordinal, task_key in enumerate((first_task, second_task)):
            ordinal_name = "first_app" if ordinal == 0 else "second_app"
            with ledger.phase(f"{ordinal_name}_prepare"):
                owner, batch, oracle, packing_receipt = _prepare_once(
                    task_key=task_key, session=session,
                    loaded=loaded[task_key],
                    workload=workloads[task_key], runtime=runtime,
                    numpy=numpy, bulk_input=bulk_input)
                prepared.append(owner)
            with ledger.phase(f"{ordinal_name}_first_exact_execute"):
                app_evidence[task_key] = _execute_once(
                    task_key=task_key, prepared=owner, batch=batch,
                    oracle=oracle, packing_receipt=packing_receipt,
                    loaded=loaded[task_key])
    except BaseException as error:
        primary_error = error
    finally:
        with ledger.phase("close"):
            try:
                _close_all(prepared, session)
            except BaseException as error:
                close_error = error
    if primary_error is not None and close_error is not None:
        raise RuntimeError({
            "runtime_session_pilot_primary_error": repr(primary_error),
            "runtime_session_pilot_close_error": repr(close_error),
        }) from primary_error
    if primary_error is not None:
        raise primary_error
    if close_error is not None:
        raise close_error

    phase_ledger = ledger.finish()
    loaded_identity = verify_loaded_rtdl(
        admitted_execution_identity, rtdl_module=runtime,
        implementation_module=implementation)
    extra_modules = {
        "goal5809_execution_identity_helper": sys.modules[
            "scripts.goal5809_execution_identity"],
        "goal5809_rtdl_worker": sys.modules[__name__],
        "goal5805_protocol_source": sys.modules[
            "experiments.goal5805_successor.protocol"],
        "physical_execution_provenance_module": sys.modules[
            "rtdsl.physical_execution_provenance"],
        "rtdlexe_arm_source": sys.modules[
            "experiments.goal5802_premeasurement.rtdlexe_arm"],
        "goal5809_pyoptix_bulk_input_source": bulk_input,
        "workload_source": workload_module,
    }
    extra_loaded_identity = verify_loaded_modules(
        admitted_execution_identity, modules_by_role=extra_modules)
    runtime_versions: dict[str, object] = {
        "numpy": str(numpy.__version__),
    }
    if "cupy" in sys.modules:
        runtime_versions["cupy"] = str(sys.modules["cupy"].__version__)
    if "cuda" in sys.modules:
        runtime_versions["cuda-python"] = importlib.metadata.version(
            "cuda-python")
    if "optix" in sys.modules:
        runtime_versions["pyoptix"] = importlib.metadata.version("pyoptix")
        optix_version = getattr(sys.modules["optix"], "version", None)
        if callable(optix_version):
            runtime_versions["optix-api"] = [
                int(item) for item in optix_version()]
    runtime_dependency_identity = verify_loaded_runtime_dependencies(
        admitted_execution_identity,
        required_module_roots=("numpy",),
        observed_versions=runtime_versions)
    loaded_identity = {
        **loaded_identity,
        "loaded_modules": {
            **loaded_identity["loaded_modules"],
            **extra_loaded_identity["loaded_modules"],
        },
        "selected_goal5809_source_modules_verified": True,
        "complete_runtime_environment_tree_verified": True,
        "runtime_dependency_identity": runtime_dependency_identity,
    }
    target = admitted["target"]
    workload_source = Path(workload_module.__file__).resolve(strict=True)
    workload_bundle_sha256 = _digest(_plain(workloads))
    composed_ptx_sha256 = {
        task_key: hashlib.sha256(
            str(loaded[task_key].composed_ptx).encode("utf-8")).hexdigest()
        for task_key in TASK_KEYS
    }
    body: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "process_pid": os.getpid(),
        "scope": {
            "diagnostic_pilot_only": True,
            "nonformal_diagnostic": True,
            "formal_evidence": False,
            "paper_evidence": False,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "paper_claim_authorized": False,
            "inferential_claim_authorized": False,
            "threshold_or_noninferiority_claim_authorized": False,
            "ratio_computation_authorized": False,
        },
        "lifecycle": {
            "public_api": [
                "install_rtdlexe_deployment", "load_rtdlexe",
                "LoadedRTDLExecutable.open_runtime_session",
                "RTDLRuntimeSession.prepare",
                "PreparedRTDLExecutable.execute",
                "PreparedRTDLExecutable.close", "RTDLRuntimeSession.close",
            ],
            "app_order": [first_task, second_task],
            "loaded_executable_count": 2,
            "open_runtime_session_call_count": 1,
            "runtime_session_count": 1,
            "prepare_call_count": 2,
            "execute_call_count": 2,
            "warmup_execute_call_count": 0,
            "prepared_owner_close_count": 2,
            "runtime_session_close_count": 1,
            "cuda_provider_first_use_preserved": True,
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
            "prepared_owners_retained_until_final_close_phase": True,
            "one_provider_shared_across_both_loaded_executables": True,
            "clean_interpreter_product_start_verified": True,
            "startup_forbidden_product_modules_observed": list(
                _STARTUP_PRODUCT_MODULES),
        },
        "phase_times_absolute": phase_ledger,
        "applications": {
            task_key: {
                **app_evidence[task_key],
                "artifact_sha256": admitted["candidates"][task_key][
                    "artifact_sha256"],
                "authority_sha256": admitted["candidates"][task_key][
                    "authority_sha256"],
                "deployment_id": admitted["candidates"][task_key][
                    "deployment_id"],
                "composed_ptx_sha256": composed_ptx_sha256[task_key],
            }
            for task_key in TASK_KEYS
        },
        "session_identity": {
            "native_library_path": str(session.native_library_path),
            "native_library_sha256": session.native_library_sha256,
            "cache_entry_identity": session.cache_entry_identity,
            "owner_pid": session.owner_pid,
            "closed_after_close_phase": bool(session.closed),
        },
        "inputs": {
            "target_manifest_path": str(admitted["target_path"]),
            "target_manifest_file_sha256": admitted["target_file_sha256"],
            "target_manifest_semantic_sha256": target[
                "target_manifest_sha256"],
            "candidate_manifest_path": str(admitted["candidate_path"]),
            "candidate_manifest_file_sha256": admitted[
                "candidate_file_sha256"],
            "native_library_sha256": target["files"]["native_library"][
                "sha256"],
            "pyoptix_matched_baseline_ptx_sha256": target["files"][
                "matched_ptx"]["sha256"],
            "workload_source_path": str(workload_source),
            "workload_source_sha256": _sha(workload_source),
            "workload_bundle_sha256": workload_bundle_sha256,
            "runtime_preload_receipt": _plain(preload_receipt),
            "runtime_module": runtime.__name__,
            "implementation_module": implementation.__name__,
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
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    if body["session_identity"]["native_library_sha256"] \
            != body["inputs"]["native_library_sha256"]:
        raise RuntimeError("runtime session admitted a different native image")
    if body["session_identity"]["closed_after_close_phase"] is not True:
        raise RuntimeError("runtime session remained open after close phase")
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
        raise RuntimeError("Goal5809 output already exists")
    result = _run(args)
    payload = _canonical(result) + b"\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as handle:
        handle.write(payload)
    sys.stdout.write(json.dumps({
        "output": str(args.output.resolve()),
        "output_bytes": len(payload),
        "output_sha256": hashlib.sha256(payload).hexdigest(),
        "pilot_sha256": result["pilot_sha256"],
        "registered_performance_timing_count": 0,
    }, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
