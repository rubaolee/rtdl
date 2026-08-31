#!/usr/bin/env python3
"""Factorial Home diagnosis of RTDL session-admission cost.

This is deliberately an engineering diagnostic, not a benchmark.  Four arms
move the existing CUDA-primary readiness operation, the existing sealed-native
DSO acquisition, or both immediately before the unchanged public
``open_runtime_session`` call.  A fifth causal arm removes only Python's CUDA
readiness operation after loading the same driver DSO; the exact sealed native
provider must still initialize CUDA/OptiX and exactly execute both Goal5810
applications.

The complete wall through the second exact output is always reported.  Thus
work shifted from session admission into first prepare remains visible.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
import ctypes
import functools
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

from scripts import goal5810_home_two_app_phase_diagnostic as home
from scripts import goal5809_runtime_session_two_app_pilot as worker


SCHEMA = "rtdl.goal5811.home_rtdl_session_causal_diagnostic.v4"
STATUS = "COMPLETE__HOME_PASCAL_NONFORMAL_CAUSAL_DIAGNOSTIC"
TREATMENTS = (
    "natural",
    "primary_context_preplaced",
    "sealed_dso_preplaced",
    "primary_context_and_sealed_dso_preplaced",
    "native_primary_after_python_cuinit",
)
PHASES = (
    "input_admission", "runtime_preload", "workload_materialization",
    "load_relation", "load_triangle", "causal_preplacement",
    "first_session_admission", "first_app_prepare",
    "first_app_first_exact_execute", "second_app_prepare",
    "second_app_first_exact_execute", "close",
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _mapped_driver_bridge() -> list[dict[str, object]]:
    """Bind the real driver-side DSOs mapped by the diagnostic process."""

    maps = Path("/proc/self/maps")
    if os.name != "posix" or not maps.is_file():
        raise RuntimeError("Goal5811 requires Linux procfs driver identity")
    markers = (
        "libcuda.so", "libnvoptix.so", "libnvidia-ptxjitcompiler.so",
    )
    paths: set[Path] = set()
    for line in maps.read_text(encoding="utf-8").splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) == 6 and fields[5].startswith("/") \
                and any(marker in fields[5] for marker in markers):
            paths.add(Path(fields[5]).resolve(strict=True))
    rows = [home._file_row(path) for path in sorted(paths, key=str)]
    if not any("libcuda.so" in str(row["path"]) for row in rows) \
            or not any("libnvoptix.so" in str(row["path"]) for row in rows):
        raise RuntimeError({"Goal5811_driver_bridge_incomplete": rows})
    return rows


class _CallTrace:
    """Record selected Python/FFI ownership boundaries without nesting loss."""

    def __init__(self) -> None:
        self.phase_name: str | None = None
        self.rows: list[dict[str, object]] = []
        self._patches: list[tuple[object, str, object]] = []

    @contextmanager
    def phase(self, name: str) -> Iterator[None]:
        if self.phase_name is not None:
            raise RuntimeError("Goal5811 trace phase nested")
        self.phase_name = name
        try:
            yield
        finally:
            self.phase_name = None

    def patch(self, owner: object, name: str, category: str) -> None:
        original = getattr(owner, name)

        @functools.wraps(original)
        def timed(*args: Any, **kwargs: Any) -> Any:
            phase = self.phase_name
            if phase is None:
                raise RuntimeError(
                    f"Goal5811 traced call outside a phase: {name}")
            start = time.perf_counter_ns()
            outcome = "RETURNED"
            try:
                return original(*args, **kwargs)
            except BaseException:
                outcome = "RAISED"
                raise
            finally:
                end = time.perf_counter_ns()
                self.rows.append({
                    "ordinal": len(self.rows),
                    "phase": phase,
                    "category": category,
                    "function": name,
                    "start_perf_counter_ns": start,
                    "end_perf_counter_ns": end,
                    "duration_ns": end - start,
                    "outcome": outcome,
                })

        self._patches.append((owner, name, original))
        setattr(owner, name, timed)

    def close(self) -> None:
        while self._patches:
            owner, name, original = self._patches.pop()
            setattr(owner, name, original)

    def summary(self) -> dict[str, object]:
        categories = sorted({str(row["category"]) for row in self.rows})
        phases = sorted({str(row["phase"]) for row in self.rows})
        return {
            "clock": "time.perf_counter_ns",
            "events": list(self.rows),
            "category_phase_totals_ns_nonadditive_when_nested": {
                category: {
                    phase: sum(
                        int(row["duration_ns"]) for row in self.rows
                        if row["category"] == category
                        and row["phase"] == phase)
                    for phase in phases
                }
                for category in categories
            },
            "nested_event_durations_are_not_summed_into_phase_wall": True,
        }


class _NativeProviderOwnedReadinessLease:
    """Diagnostic substitute proving whether Python CUDA admission is redundant.

    This is intentionally not a product capability.  The exact sealed native
    provider remains responsible for the real CUDA/OptiX initialization used
    by both exact executions.  The treatment is valid only as a causal probe.
    """

    def __init__(self, expected_compute_capability: tuple[int, int]) -> None:
        self.expected_compute_capability = tuple(expected_compute_capability)
        self.owner_pid = os.getpid()
        self.released = False
        # The retained Home driver bridge must be selected before the exact
        # native DSO is loaded.  Loading is not CUDA initialization: the exact
        # native provider still performs cuInit, primary retain/select,
        # optixInit and optixDeviceContextCreate during first prepare.
        self.driver = ctypes.CDLL(
            "libcuda.so.1", mode=getattr(ctypes, "RTLD_GLOBAL", 0))
        self.driver.cuInit.argtypes = [ctypes.c_uint]
        self.driver.cuInit.restype = ctypes.c_int
        if int(self.driver.cuInit(0)) != 0:
            raise RuntimeError(
                "Goal5811 Python cuInit-only compatibility bootstrap failed")

    def check(self) -> None:
        if self.released or os.getpid() != self.owner_pid:
            raise RuntimeError(
                "Goal5811 diagnostic native-owned readiness is unusable")

    def close(self) -> None:
        if os.getpid() != self.owner_pid:
            raise RuntimeError(
                "Goal5811 diagnostic native-owned readiness crossed a fork")
        self.released = True


@contextmanager
def _phase(
    ledger: worker._PhaseLedger, trace: _CallTrace, name: str,
) -> Iterator[None]:
    with trace.phase(name):
        with ledger.phase(name):
            yield


def _state(implementation: Any, native_sha256: str) -> dict[str, object]:
    readiness = implementation._CUDA_PRIMARY_READY_STATE
    cache = implementation._NATIVE_IMAGE_CACHE
    return {
        "process_pid": os.getpid(),
        "cuda_primary_readiness_published": readiness is not None,
        "cuda_primary_readiness_owner_pid": (
            None if readiness is None else readiness.owner_pid),
        "native_image_cache_entry_count": len(cache),
        "target_native_image_cached": native_sha256 in cache,
        "native_image_cache_sha256s": sorted(cache),
    }


def _assert_preplacement_state(
    treatment: str, state: Mapping[str, object],
) -> None:
    context_expected = treatment in {
        "primary_context_preplaced",
        "primary_context_and_sealed_dso_preplaced",
    }
    dso_expected = treatment in {
        "sealed_dso_preplaced",
        "primary_context_and_sealed_dso_preplaced",
    }
    if state["cuda_primary_readiness_published"] is not context_expected \
            or state["target_native_image_cached"] is not dso_expected:
        raise RuntimeError({
            "Goal5811_preplacement_state_differs": dict(state),
            "treatment": treatment,
        })


def _run(
    *, target_path: Path, target_sha256: str, first_task: str,
    treatment: str,
) -> dict[str, Any]:
    ledger = worker._PhaseLedger(
        time.perf_counter_ns, required_phases=PHASES)
    trace = _CallTrace()
    overall_start = time.perf_counter_ns()

    with _phase(ledger, trace, "input_admission"):
        admitted = worker._admit_target(
            target_path, expected_file_sha256=target_sha256)
        second_task = "triangle" if first_task == "relation" else "relation"

    with _phase(ledger, trace, "runtime_preload"):
        workload_module, runtime, implementation, preload_receipt, bulk_input = \
            worker._preload_runtime()
        numpy = __import__("numpy")
        original_readiness_acquire = (
            implementation._acquire_cuda_primary_context_readiness)
        if treatment == "native_primary_after_python_cuinit":
            def native_provider_owned_readiness(
                *, expected_compute_capability: tuple[int, int],
            ) -> _NativeProviderOwnedReadinessLease:
                return _NativeProviderOwnedReadinessLease(
                    expected_compute_capability)

            implementation._acquire_cuda_primary_context_readiness = (
                native_provider_owned_readiness)
        trace.patch(
            runtime, "install_rtdlexe_deployment", "trust_slot_admission")
        trace.patch(runtime, "load_rtdlexe", "artifact_authority_verification")
        trace.patch(
            implementation, "_acquire_cuda_primary_context_readiness",
            "cuda_primary_context_readiness")
        trace.patch(
            implementation, "_load_verified_native_file_descriptor",
            "sealed_native_dso_acquisition")
        trace.patch(
            implementation, "_query_native_producer_descriptor",
            "native_producer_descriptor_verification")
        trace.patch(
            implementation, "_require_runtime_session_loaded_capability",
            "loaded_capability_revalidation")
        trace.patch(
            implementation, "_loaded_runtime_session_snapshot_seal",
            "loaded_capability_snapshot_seal")
        trace.patch(
            implementation, "_admit_provider_ready_native_image_lease",
            "provider_ready_lease_admission")
        trace.patch(
            implementation.LoadedRTDLExecutable, "_build_prepared_owner",
            "native_owner_construction")

    with _phase(ledger, trace, "workload_materialization"):
        workloads = {
            "relation": workload_module.relation_workload(),
            "triangle": workload_module.triangle_workload(),
        }

    loaded: dict[str, Any] = {}
    for task in home.TASKS:
        with _phase(ledger, trace, f"load_{task}"):
            loaded[task] = worker._load_application(
                task_key=task, admitted=admitted, runtime=runtime)

    native = Path(admitted["target"]["files"]["native_library"]["path"])
    expected_native, expected_capability = loaded[
        first_task]._native_admission_parameters()
    if implementation._CUDA_PRIMARY_READY_STATE is not None \
            or implementation._NATIVE_IMAGE_CACHE:
        raise RuntimeError(
            "Goal5811 process was not fresh before causal preplacement")

    state_before = _state(implementation, expected_native)
    with _phase(ledger, trace, "causal_preplacement"):
        if treatment in {
                "primary_context_preplaced",
                "primary_context_and_sealed_dso_preplaced"}:
            readiness = implementation._acquire_cuda_primary_context_readiness(
                expected_compute_capability=expected_capability)
            readiness.close()
        if treatment in {
                "sealed_dso_preplaced",
                "primary_context_and_sealed_dso_preplaced"}:
            lease = implementation._load_verified_native_file_descriptor(
                native, expected_sha256=expected_native,
                code="RX032_NATIVE_IDENTITY_MISMATCH",
                identity_path="goal5811.causal_preplacement.native")
            implementation._release_native_library_image(lease)
    state_after_preplacement = _state(implementation, expected_native)
    _assert_preplacement_state(treatment, state_after_preplacement)

    session = None
    prepared: list[Any] = []
    applications: dict[str, Any] = {}
    primary_error: BaseException | None = None
    close_error: BaseException | None = None
    try:
        with _phase(ledger, trace, "first_session_admission"):
            session = loaded[first_task].open_runtime_session(native)
        for ordinal, task in enumerate((first_task, second_task)):
            label = "first_app" if ordinal == 0 else "second_app"
            with _phase(ledger, trace, f"{label}_prepare"):
                owner, batch, oracle, packing = worker._prepare_once(
                    task_key=task, session=session, loaded=loaded[task],
                    workload=workloads[task], runtime=runtime, numpy=numpy,
                    bulk_input=bulk_input)
                prepared.append(owner)
            with _phase(ledger, trace, f"{label}_first_exact_execute"):
                applications[task] = worker._execute_once(
                    task_key=task, prepared=owner, batch=batch, oracle=oracle,
                    packing_receipt=packing, loaded=loaded[task])
    except BaseException as error:
        primary_error = error
    finally:
        with _phase(ledger, trace, "close"):
            try:
                worker._close_all(prepared, session)
            except BaseException as error:
                close_error = error
        trace.close()
        implementation._acquire_cuda_primary_context_readiness = (
            original_readiness_acquire)
    if primary_error is not None:
        if close_error is not None:
            raise RuntimeError({
                "primary_error": repr(primary_error),
                "close_error": repr(close_error),
            }) from primary_error
        raise primary_error
    if close_error is not None:
        raise close_error
    if session is None or not session.closed:
        raise RuntimeError("Goal5811 RTDL runtime session did not close")

    phase_rows = ledger.finish()
    phase = phase_rows["phases"]
    preplacement_start = int(
        phase["causal_preplacement"]["start_perf_counter_ns"])
    session_end = int(
        phase["first_session_admission"]["end_perf_counter_ns"])
    overall_end = time.perf_counter_ns()
    state_after_session = _state(implementation, expected_native)
    native_owned = treatment == "native_primary_after_python_cuinit"
    expected_python_readiness_published = not native_owned
    if state_after_session["cuda_primary_readiness_published"] \
            is not expected_python_readiness_published \
            or not state_after_session["target_native_image_cached"]:
        raise RuntimeError("Goal5811 public session did not admit provider state")

    return {
        "treatment": treatment,
        "app_order": [first_task, second_task],
        "phase_times_absolute": phase_rows,
        "causal_accounting": {
            "overall_run_wall_ns": overall_end - overall_start,
            "causal_preplacement_wall_ns": phase[
                "causal_preplacement"]["duration_ns"],
            "public_first_session_admission_wall_ns": phase[
                "first_session_admission"]["duration_ns"],
            "preplacement_start_through_public_session_end_wall_ns":
                session_end - preplacement_start,
            "preplacement_and_session_phase_walls_reported": True,
            "three_preplacement_treatments_shift_without_erasure": True,
            "interphase_gap_included_in_contiguous_wall": True,
            "native_internal_driver_work_retained_in_enclosing_phase_wall":
                True,
            "no_native_internal_cuda_time_zero_imputed": True,
            "native_provider_owned_readiness_bypass_active": native_owned,
            "native_provider_owned_readiness_is_product_api": False,
            "python_compatibility_bootstrap": (
                "libcuda_load_and_cuInit_only" if native_owned else None),
            "python_primary_context_retain_in_native_owned_treatment": False,
            "native_provider_owned_treatment_retains_exact_native_cuda_optix_work":
                True,
            "causal_result_must_use_total_through_second_exact_output": True,
        },
        "selected_call_trace": trace.summary(),
        "provider_state": {
            "before_preplacement": state_before,
            "after_preplacement_before_public_session":
                state_after_preplacement,
            "after_public_session_and_close": state_after_session,
        },
        "applications": applications,
        "lifecycle": {
            "loaded_executable_count": 2,
            "runtime_session_count": 1,
            "provider_admission_count": 1,
            "prepare_call_count": 2,
            "execute_call_count": 2,
            "one_provider_shared_across_both_apps": True,
            "all_owners_and_session_closed": True,
        },
        "runtime": {
            "preload_receipt": worker._plain(preload_receipt),
            "runtime_module": home._module_row(runtime),
            "implementation_module": home._module_row(implementation),
            "workload_module": home._module_row(workload_module),
            "bulk_input_module": home._module_row(bulk_input),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treatment", choices=TREATMENTS, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--expected-target-manifest-sha256", required=True)
    parser.add_argument("--first-app", choices=home.TASKS, required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError("Goal5811 output already exists")
    cache_environment = home._isolate_caches(args.cache_root)
    result = _run(
        target_path=args.target_manifest,
        target_sha256=args.expected_target_manifest_sha256,
        first_task=args.first_app, treatment=args.treatment)
    cuda_identity = home._cuda_identity()
    driver_bridge = _mapped_driver_bridge()
    body = {
        "schema": SCHEMA,
        "status": STATUS,
        "process_pid": os.getpid(),
        "python": {
            "executable": str(Path(sys.executable).absolute()),
            "version": sys.version,
        },
        "cuda": cuda_identity,
        "actual_loaded_driver_bridge": driver_bridge,
        "loader_environment": {
            "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH"),
            "LD_PRELOAD": os.environ.get("LD_PRELOAD"),
        },
        "isolated_cache_environment": cache_environment,
        "target_manifest": home._file_row(args.target_manifest),
        "worker_source": home._file_row(Path(__file__)),
        "scope": {
            "diagnostic_only": True,
            "home_pascal_only": True,
            "rt_core_evidence": False,
            "formal_evidence": False,
            "paper_evidence": False,
            "claim_authorized": False,
            "threshold_or_pass_fail_gate_present": False,
            "a4500_relabeling_authorized": False,
            "product_source_edited_by_experiment": False,
            "all_structurally_valid_treatments_must_be_retained": True,
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
        },
        **result,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    sealed = {**body, "diagnostic_sha256": _digest(body)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as handle:
        handle.write(_canonical(sealed) + b"\n")
    print(json.dumps({
        "status": STATUS,
        "treatment": args.treatment,
        "first_app": args.first_app,
        "output": str(args.output.resolve(strict=True)),
        "diagnostic_sha256": sealed["diagnostic_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
