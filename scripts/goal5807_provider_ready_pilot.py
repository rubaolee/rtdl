#!/usr/bin/env python3
"""Non-formal Goal5807 provider-ready lifecycle pilot.

RTDL runs the explicit ``load -> bind_provider -> prepare`` public lifecycle.
PyOptiX preloads its extension/provider, explicitly admits CUDA primary
readiness, and loads the exact program before prepare.  The comparable state
therefore begins with provider + primary + program ready while neither arm has
created an OptixDeviceContext or pipeline.  Only application prepare plus the
first exact execution is authorized for comparison; preload/load/bind and both
delayed close phases stay separate.
"""

from __future__ import annotations

import time

_PROCESS_ENTRY_NS = time.perf_counter_ns()

import argparse
import ast
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager, ExitStack
import ctypes
import hashlib
import importlib
import inspect
import json
import os
from pathlib import Path
import sys
import textwrap
import threading
from typing import Any


SCHEMA = "rtdl.goal5807.provider_ready_pilot.v3"
STATUS = (
    "PASS__DIAGNOSTIC_PILOT__DEVICE0_PRIMARY_AND_PREFIX_TIMERS_REPAIRED__"
    "FORMAL_DESIGN_INPUT_ONLY")
ARMS = (
    "RTDL_PROVIDER_READY",
    "PYOPTIX_RUNTIME_PROVIDER_PROGRAM_READY",
)
TASKS = ("relation", "triangle")
EXPECTED_TARGET_COMPUTE_CAPABILITY = (8, 6)
PHASES = (
    "input_admission",
    "runtime_preload",
    "adapter_construct",
    "install_load",
    "provider_bind",
    "app_prepare",
    "first_exact_execute",
    "steady",
    "evidence_identity",
    "prepared_close",
    "provider_session_close",
)
_SHA256_HEX = frozenset("0123456789abcdef")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Goal5807 JSON root is not an object: {path}")
    return value


def _require_sha256(value: str, label: str) -> str:
    if len(value) != 64 or any(item not in _SHA256_HEX for item in value):
        raise RuntimeError(f"{label} is not lowercase SHA-256")
    return value


def _require_equal(label: str, observed: object, expected: object) -> None:
    if observed != expected:
        raise RuntimeError({label: {"expected": expected, "observed": observed}})


def _plain(value: object) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, bytes):
        return {"bytes": len(value), "sha256": _sha_bytes(value)}
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    tolist = getattr(value, "tolist", None)
    if callable(tolist):
        return _plain(tolist())
    item = getattr(value, "item", None)
    if callable(item):
        return _plain(item())
    raise RuntimeError(
        f"Goal5807 canonical projection does not support {type(value).__name__}")


def _call_leaf_names(function: Callable[..., Any]) -> tuple[str, ...]:
    source = textwrap.dedent(inspect.getsource(function))
    tree = ast.parse(source)
    leaves: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        callee = node.func
        if isinstance(callee, ast.Name):
            leaves.add(callee.id)
        elif isinstance(callee, ast.Attribute):
            leaves.add(callee.attr)
    return tuple(sorted(leaves))


def _load_cuda_driver() -> Any:
    try:
        driver = ctypes.CDLL("libcuda.so.1")
    except OSError as error:
        raise RuntimeError("Goal5807 cannot load libcuda.so.1") from error
    driver.cuInit.argtypes = [ctypes.c_uint]
    driver.cuInit.restype = ctypes.c_int
    driver.cuCtxGetCurrent.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
    driver.cuCtxGetCurrent.restype = ctypes.c_int
    driver.cuCtxSetCurrent.argtypes = [ctypes.c_void_p]
    driver.cuCtxSetCurrent.restype = ctypes.c_int
    driver.cuCtxGetDevice.argtypes = [ctypes.POINTER(ctypes.c_int)]
    driver.cuCtxGetDevice.restype = ctypes.c_int
    driver.cuDeviceGet.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
    driver.cuDeviceGet.restype = ctypes.c_int
    driver.cuDeviceComputeCapability.argtypes = [
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
        ctypes.c_int,
    ]
    driver.cuDeviceComputeCapability.restype = ctypes.c_int
    driver.cuDevicePrimaryCtxRetain.argtypes = [
        ctypes.POINTER(ctypes.c_void_p), ctypes.c_int,
    ]
    driver.cuDevicePrimaryCtxRetain.restype = ctypes.c_int
    driver.cuDevicePrimaryCtxRelease.argtypes = [ctypes.c_int]
    driver.cuDevicePrimaryCtxRelease.restype = ctypes.c_int
    initialization_status = int(driver.cuInit(0))
    if initialization_status != 0:
        raise RuntimeError({"cuInit_status": initialization_status})
    return driver


def _current_cuda_context(driver: Any) -> int:
    current = ctypes.c_void_p()
    status = int(driver.cuCtxGetCurrent(ctypes.byref(current)))
    if status != 0:
        raise RuntimeError({"cuCtxGetCurrent_status": status})
    return int(current.value or 0)


def _current_cuda_device(driver: Any) -> int:
    device = ctypes.c_int()
    status = int(driver.cuCtxGetDevice(ctypes.byref(device)))
    if status != 0:
        raise RuntimeError({"cuCtxGetDevice_status": status})
    return int(device.value)


def _set_current_cuda_context(driver: Any, value: int) -> None:
    status = int(driver.cuCtxSetCurrent(ctypes.c_void_p(value)))
    if status != 0:
        raise RuntimeError({"cuCtxSetCurrent_status": status})


class _Device0PrimaryCurrentLease:
    """Harness retain kept live through prepare, execute, and close."""

    def __init__(
        self, driver: Any, *,
        expected_compute_capability: tuple[int, int] = (8, 6),
        expected_preexisting_primary_handle: int | None = None,
        persistent_owner: str,
    ) -> None:
        self.driver = driver
        self.expected_compute_capability = tuple(
            expected_compute_capability)
        self.expected_preexisting_primary_handle = (
            expected_preexisting_primary_handle)
        self.persistent_owner = persistent_owner
        self.device: int | None = None
        self.previous: int | None = None
        self.primary: int | None = None
        self.retain_calls = 0
        self.release_calls = 0
        self.owner_pid = os.getpid()
        self.owner_thread_ident = threading.get_ident()
        self.evidence: dict[str, Any] = {}

    def __enter__(self) -> "_Device0PrimaryCurrentLease":
        requested_ordinal = 0
        device = ctypes.c_int()
        status = int(self.driver.cuDeviceGet(
            ctypes.byref(device), requested_ordinal))
        if status != 0:
            raise RuntimeError({"cuDeviceGet_status": status})
        major = ctypes.c_int()
        minor = ctypes.c_int()
        status = int(self.driver.cuDeviceComputeCapability(
            ctypes.byref(major), ctypes.byref(minor), device.value))
        if status != 0:
            raise RuntimeError({"cuDeviceComputeCapability_status": status})
        observed_capability = (major.value, minor.value)
        if observed_capability != self.expected_compute_capability:
            raise RuntimeError({
                "goal5807_target_compute_capability_mismatch": {
                    "expected": list(self.expected_compute_capability),
                    "observed": list(observed_capability),
                },
            })

        self.device = int(device.value)
        self.previous = _current_cuda_context(self.driver)
        primary = ctypes.c_void_p()
        try:
            self.retain_calls += 1
            status = int(self.driver.cuDevicePrimaryCtxRetain(
                ctypes.byref(primary), self.device))
            if status != 0 or not primary.value:
                raise RuntimeError({
                    "cuDevicePrimaryCtxRetain_status": status,
                    "primary_handle": int(primary.value or 0),
                })
            self.primary = int(primary.value)
            if self.expected_preexisting_primary_handle is not None \
                    and self.primary \
                    != self.expected_preexisting_primary_handle:
                raise RuntimeError({
                    "goal5807_preexisting_primary_handle_mismatch": {
                        "expected": self.expected_preexisting_primary_handle,
                        "observed": self.primary,
                    },
                })
            if _current_cuda_context(self.driver) != self.primary:
                _set_current_cuda_context(self.driver, self.primary)
            self.verify_current("APP_TIMER_ENTRY")
        except BaseException as admission_error:
            restore_error: BaseException | None = None
            release_error: BaseException | None = None
            release_status: int | None = None
            if primary.value and self.release_calls == 0:
                try:
                    _set_current_cuda_context(
                        self.driver, int(self.previous or 0))
                except BaseException as error:
                    restore_error = error
                finally:
                    self.release_calls += 1
                    try:
                        release_status = int(
                            self.driver.cuDevicePrimaryCtxRelease(self.device))
                    except BaseException as error:
                        release_error = error
            if restore_error is not None or release_error is not None \
                    or release_status not in (None, 0):
                raise RuntimeError({
                    "goal5807_primary_admission_cleanup_failed": {
                        "admission_error": repr(admission_error),
                        "restore_error": repr(restore_error),
                        "release_error": repr(release_error),
                        "release_status": release_status,
                    },
                }) from admission_error
            raise

        self.evidence.update({
            "cuDeviceGet_requested_ordinal": requested_ordinal,
            "cuDeviceGet_device_handle": self.device,
            "cuDeviceComputeCapability": list(observed_capability),
            "expected_target_compute_capability": list(
                self.expected_compute_capability),
            "cuCtxGetCurrent_before_normalization": self.previous,
            "cuDevicePrimaryCtxRetain_handle": self.primary,
            "cuCtxGetCurrent_at_app_timer_entry": self.primary,
            "cuDevicePrimaryCtxRetain_call_count": self.retain_calls,
            "cuDevicePrimaryCtxRelease_call_count": self.release_calls,
            "temporary_primary_retain_live": True,
            "temporary_primary_retain_balanced": False,
            "retained_primary_handle_equals_current": True,
            "expected_preexisting_primary_handle": (
                self.expected_preexisting_primary_handle),
            "expected_preexisting_primary_handle_matched": (
                self.expected_preexisting_primary_handle is None
                or self.primary == self.expected_preexisting_primary_handle),
            "persistent_primary_owner": self.persistent_owner,
            "lease_owner_pid": self.owner_pid,
            "lease_owner_thread_ident": self.owner_thread_ident,
            "current_handle_verifications": [
                {
                    "event": "APP_TIMER_ENTRY",
                    "current": self.primary,
                    "current_device": self.device,
                    "pid": self.owner_pid,
                    "thread_ident": self.owner_thread_ident,
                },
            ],
            "normalized_state": "DEVICE0_PRIMARY_CURRENT",
        })
        return self

    def verify_current(self, event: str) -> None:
        if self.primary is None or self.release_calls:
            raise RuntimeError("Goal5807 primary-current lease is not live")
        if os.getpid() != self.owner_pid \
                or threading.get_ident() != self.owner_thread_ident:
            raise RuntimeError({
                "goal5807_primary_lease_owner_drift": {
                    "event": event,
                    "expected_pid": self.owner_pid,
                    "observed_pid": os.getpid(),
                    "expected_thread": self.owner_thread_ident,
                    "observed_thread": threading.get_ident(),
                },
            })
        current = _current_cuda_context(self.driver)
        current_device = _current_cuda_device(self.driver)
        if current != self.primary or current_device != self.device:
            raise RuntimeError({
                "goal5807_primary_current_drift": {
                    "event": event,
                    "expected_context": self.primary,
                    "observed_context": current,
                    "expected_device": self.device,
                    "observed_device": current_device,
                },
            })
        rows = self.evidence.get("current_handle_verifications")
        if isinstance(rows, list):
            rows.append({
                "event": event,
                "current": current,
                "current_device": current_device,
                "pid": os.getpid(),
                "thread_ident": threading.get_ident(),
            })

    def __exit__(self, *_error: object) -> None:
        if self.primary is None or self.device is None \
                or self.previous is None:
            return
        verification_error: BaseException | None = None
        restore_error: BaseException | None = None
        release_error: BaseException | None = None
        restored: int | None = None
        release_status: int | None = None
        try:
            self.verify_current("AFTER_PROVIDER_AND_PREPARED_CLOSE")
        except BaseException as error:
            verification_error = error
        try:
            _set_current_cuda_context(self.driver, self.previous)
            restored = _current_cuda_context(self.driver)
            if restored != self.previous:
                raise RuntimeError({
                    "goal5807_prior_current_restore_failed": {
                        "expected": self.previous,
                        "observed": restored,
                    },
                })
        except BaseException as error:
            restore_error = error
        finally:
            self.release_calls += 1
            try:
                release_status = int(
                    self.driver.cuDevicePrimaryCtxRelease(self.device))
            except BaseException as error:
                release_error = error
        self.evidence.update({
            "cuCtxGetCurrent_after_exact_restore": restored,
            "exact_prior_current_restored": restored == self.previous,
            "cuDevicePrimaryCtxRelease_call_count": self.release_calls,
            "cuDevicePrimaryCtxRelease_status": release_status,
            "temporary_primary_retain_live": False,
            "temporary_primary_retain_live_through_close": (
                any(
                    row.get("event")
                    == "AFTER_PROVIDER_AND_PREPARED_CLOSE"
                    for row in self.evidence[
                        "current_handle_verifications"])),
            "temporary_primary_retain_balanced": (
                self.retain_calls == self.release_calls == 1
                and release_status == 0 and release_error is None),
            "cleanup_order": [
                "cuCtxSetCurrent(previous)",
                "cuCtxGetCurrent",
                "cuDevicePrimaryCtxRelease(device0)",
            ],
        })
        if verification_error is not None or restore_error is not None \
                or release_error is not None or release_status != 0:
            raise RuntimeError({
                "goal5807_primary_current_cleanup_failed": {
                    "verification_error": repr(verification_error),
                    "restore_error": repr(restore_error),
                    "release_error": repr(release_error),
                    "release_status": release_status,
                },
            }) from (restore_error or verification_error or release_error)


def _pyoptix_primary_ready_preserving_current(
    cupy_runtime: Any, *, driver: Any | None = None,
) -> dict[str, Any]:
    """Admit the primary context while restoring the caller's exact current."""

    driver = _load_cuda_driver() if driver is None else driver
    before = _current_cuda_context(driver)
    action_error: BaseException | None = None
    try:
        cupy_runtime.free(0)
    except BaseException as error:
        action_error = error
    restore_error: BaseException | None = None
    try:
        _set_current_cuda_context(driver, before)
    except BaseException as error:
        restore_error = error
    after: int | None = None
    if restore_error is None:
        after = _current_cuda_context(driver)
    if restore_error is not None or after != before:
        raise RuntimeError({
            "goal5807_cuda_current_context_restore_failed": True,
            "current_before": before,
            "current_after": after,
            "readiness_error": repr(action_error),
            "restore_error": repr(restore_error),
        }) from (restore_error or action_error)
    if action_error is not None:
        raise action_error
    return {
        "cuCtxGetCurrent_before": before,
        "cuCtxGetCurrent_after_restore": after,
        "cupy_free_zero_completed": True,
        "cuCtxSetCurrent_restore_completed": True,
        "exact_current_context_restored": True,
    }


def _call_requiring_current_unchanged(
    operation: Callable[[], Any], *, driver: Any | None = None,
) -> tuple[Any, dict[str, Any]]:
    """Call an RTDL operation and reject any current-context side effect."""

    driver = _load_cuda_driver() if driver is None else driver
    before = _current_cuda_context(driver)
    try:
        result = operation()
    except BaseException as error:
        after_failure = _current_cuda_context(driver)
        if after_failure != before:
            raise RuntimeError({
                "goal5807_rtdl_failed_bind_changed_current_context": True,
                "current_before": before,
                "current_after": after_failure,
            }) from error
        raise
    after = _current_cuda_context(driver)
    if after != before:
        raise RuntimeError({
            "goal5807_rtdl_bind_changed_current_context": True,
            "current_before": before,
            "current_after": after,
        })
    return result, {
        "cuCtxGetCurrent_before": before,
        "cuCtxGetCurrent_after": after,
        "exact_current_context_unchanged": True,
    }


class _PhaseLedger:
    """Strict sequential phase ledger with a full-lifecycle closure."""

    def __init__(
        self, *, process_entry_ns: int,
        clock_ns: Callable[[], int] = time.perf_counter_ns,
    ) -> None:
        self._process_entry_ns = int(process_entry_ns)
        self._clock_ns = clock_ns
        self._rows: dict[str, dict[str, Any]] = {}
        self._active: str | None = None
        self._next_phase_index = 0
        self._last_end_ns = self._process_entry_ns
        self._finalized = False

    def _claim_next(self, name: str) -> None:
        if self._next_phase_index >= len(PHASES) \
                or PHASES[self._next_phase_index] != name:
            expected = (
                PHASES[self._next_phase_index]
                if self._next_phase_index < len(PHASES) else None)
            raise RuntimeError({
                "goal5807_phase_order_drift": {
                    "expected": expected,
                    "observed": name,
                }
            })
        self._next_phase_index += 1

    @contextmanager
    def phase(self, name: str) -> Iterator[None]:
        if self._finalized:
            raise RuntimeError("Goal5807 phase ledger is finalized")
        if name not in PHASES:
            raise RuntimeError(f"Goal5807 unknown phase: {name}")
        if self._active is not None:
            raise RuntimeError("Goal5807 lifecycle phases cannot nest")
        if name in self._rows:
            raise RuntimeError(f"Goal5807 phase repeated: {name}")
        self._claim_next(name)
        start = int(self._clock_ns())
        if start < self._last_end_ns:
            raise RuntimeError("Goal5807 phase clock moved backwards")
        self._active = name
        try:
            yield
        finally:
            end = int(self._clock_ns())
            if end < start:
                raise RuntimeError("Goal5807 phase duration is negative")
            self._rows[name] = {
                "status": "OBSERVED",
                "start_offset_ns": start - self._process_entry_ns,
                "duration_ns": end - start,
            }
            self._last_end_ns = end
            self._active = None

    def unavailable(self, name: str, *, reason: str) -> None:
        if name not in PHASES:
            raise RuntimeError(f"Goal5807 unknown phase: {name}")
        if self._active is not None or name in self._rows:
            raise RuntimeError(f"Goal5807 phase cannot be unavailable: {name}")
        self._claim_next(name)
        self._rows[name] = {
            "status": "UNAVAILABLE__NO_EQUIVALENT_PUBLIC_STATE",
            "reason": reason,
            "start_offset_ns": None,
            "duration_ns": None,
        }

    def absorbed(self, name: str, *, absorbed_into: str, reason: str) -> None:
        if name not in PHASES or absorbed_into not in PHASES:
            raise RuntimeError(f"Goal5807 unknown absorbed phase: {name}")
        if self._active is not None or name in self._rows:
            raise RuntimeError(f"Goal5807 phase cannot be absorbed: {name}")
        self._claim_next(name)
        self._rows[name] = {
            "status": "SATISFIED_INSIDE_ANOTHER_REPORTED_PHASE",
            "absorbed_into": absorbed_into,
            "reason": reason,
            "start_offset_ns": None,
            "duration_ns": None,
        }

    def finalize(self, *, process_stop_ns: int) -> dict[str, Any]:
        if self._finalized:
            raise RuntimeError("Goal5807 phase ledger finalized twice")
        if self._active is not None:
            raise RuntimeError("Goal5807 phase ledger has an active phase")
        missing = sorted(set(PHASES) - set(self._rows))
        if missing:
            raise RuntimeError({"goal5807_missing_phases": missing})
        self._finalized = True
        stop = int(process_stop_ns)
        if stop < self._last_end_ns:
            raise RuntimeError("Goal5807 process stop precedes the final phase")
        total = stop - self._process_entry_ns
        observed_sum = sum(
            int(row["duration_ns"])
            for row in self._rows.values()
            if row["duration_ns"] is not None)
        between = total - observed_sum
        if between < 0 or observed_sum + between != total:
            raise RuntimeError("Goal5807 full-lifecycle accounting does not close")
        return {
            "clock": "time.perf_counter_ns",
            "phases_are_sequential_and_nonoverlapping": True,
            "nonobserved_phase_zero_imputed": False,
            "phases": {
                name: self._rows[name] for name in PHASES
            },
            "observed_phase_sum_ns_additive": observed_sum,
            "between_phase_unclassified_ns_additive": between,
            "total_profiled_full_process_ns": total,
            "additive_closure_ns": observed_sum + between,
            "total_boundary": (
                "FIRST_PYTHON_STATEMENT_AFTER_TIME_IMPORT_TO_POST_CLOSE__"
                "EXCLUDES_INTERPRETER_STARTUP_JSON_SERIALIZATION_AND_TEARDOWN"),
        }


def _comparable_app_boundary_ns(phase_ledger: Mapping[str, Any]) -> int:
    """Return only the Goal5806-matched prepare plus first-execute boundary."""
    phases = phase_ledger.get("phases")
    if not isinstance(phases, Mapping):
        raise RuntimeError("Goal5807 phase ledger has no phase mapping")
    duration = 0
    for name in ("app_prepare", "first_exact_execute"):
        row = phases.get(name)
        if not isinstance(row, Mapping) or row.get("status") != "OBSERVED":
            raise RuntimeError(f"Goal5807 comparable phase is unobserved: {name}")
        value = row.get("duration_ns")
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise RuntimeError(f"Goal5807 comparable phase duration invalid: {name}")
        duration += value
    return duration


def _contiguous_prefix_boundaries(
    *, harness_run_entry_ns: int, post_runtime_preload_entry_ns: int,
    first_exact_output_validated_ns: int,
) -> dict[str, dict[str, Any]]:
    values = (
        harness_run_entry_ns,
        post_runtime_preload_entry_ns,
        first_exact_output_validated_ns,
    )
    if any(type(value) is not int for value in values) \
            or not harness_run_entry_ns <= post_runtime_preload_entry_ns \
            < first_exact_output_validated_ns:
        raise RuntimeError({
            "goal5807_contiguous_prefix_clock_invalid": list(values),
        })
    rows = {
        "HARNESS_RUN_ENTRY_TO_FIRST_EXACT_OUTPUT": {
            "duration_ns": (
                first_exact_output_validated_ns - harness_run_entry_ns),
            "start_event": "HARNESS_RUN_ENTRY",
            "stop_event": "FIRST_EXACT_OUTPUT_VALIDATED",
            "single_contiguous_timer": True,
        },
        "POST_RUNTIME_PRELOAD_TO_FIRST_EXACT_OUTPUT": {
            "duration_ns": (
                first_exact_output_validated_ns
                - post_runtime_preload_entry_ns),
            "start_event": "RUNTIME_PRELOAD_RETURNED",
            "stop_event": "FIRST_EXACT_OUTPUT_VALIDATED",
            "single_contiguous_timer": True,
        },
    }
    if any(row["duration_ns"] <= 0 for row in rows.values()):
        raise RuntimeError("Goal5807 contiguous prefix duration is not positive")
    return rows


def _runtime_preload(arm_name: str) -> tuple[Any, Any, Any, dict[str, Any]]:
    workload_module = importlib.import_module(
        "experiments.goal5802_premeasurement.workload")
    if arm_name == "RTDL_PROVIDER_READY":
        arm = importlib.import_module(
            "experiments.goal5802_premeasurement.rtdlexe_arm")
        runtime, implementation, receipt = arm.preload_rtdl_runtime()
        return workload_module, arm, (runtime, implementation), receipt
    arm = importlib.import_module(
        "experiments.goal5802_premeasurement.pyoptix_scalar_arm")
    baseline, receipt = arm.preload_pyoptix_runtime()
    return workload_module, arm, baseline, receipt


def _sealed_target_compute_capability(
    target: Mapping[str, Any],
) -> tuple[tuple[int, int], dict[str, Any]]:
    descriptor = target["files"]["target_observation"]
    path = Path(descriptor["path"]).resolve(strict=True)
    observed_sha256 = _sha(path)
    _require_equal(
        "target_observation_sha256", observed_sha256,
        descriptor["sha256"])
    value = _read(path)
    _require_equal(
        "target_observation_schema", value.get("schema"),
        "rtdl.goal5802.target_observation.v2")
    capability_text = value.get("compute_capability")
    if capability_text != "8.6":
        raise RuntimeError({
            "goal5807_sealed_target_compute_capability_not_8_6":
                capability_text,
        })
    projection = tuple(int(item) for item in capability_text.split("."))
    if projection != EXPECTED_TARGET_COMPUTE_CAPABILITY:
        raise RuntimeError("Goal5807 target capability projection drifted")
    return projection, {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": observed_sha256,
        "compute_capability_text": capability_text,
        "compute_capability_projection": list(projection),
    }


def _make_provider_ready_validation_off_context(
    baseline: Any,
) -> tuple[Any, None]:
    """Create PyOptiX context without redundant primary admission."""

    if hasattr(baseline.optix, "init"):
        baseline.optix.init()
    options = baseline.optix.DeviceContextOptions()
    validation_off = getattr(
        baseline.optix, "DEVICE_CONTEXT_VALIDATION_MODE_OFF", None)
    if validation_off is None:
        raise RuntimeError("PyOptiX does not expose validation-mode OFF")
    options.validationMode = validation_off
    return baseline.optix.deviceContextCreate(0, options), None


def _construct_adapter(
    *, arm_name: str, task_key: str, target: dict[str, Any],
    workload_module: Any, arm: Any, runtime: Any,
    preload_receipt: dict[str, Any],
) -> tuple[Any, dict[str, Any]]:
    files = target["files"]
    task = (
        workload_module.RELATION_TASK
        if task_key == "relation" else workload_module.TRIANGLE_TASK)
    workload = (
        workload_module.relation_workload()
        if task_key == "relation" else workload_module.triangle_workload())
    if arm_name == "RTDL_PROVIDER_READY":
        candidate_path = Path(files["candidate_manifest"]["path"])
        candidate_sha256 = _sha(candidate_path)
        _require_equal(
            "candidate_manifest_sha256", candidate_sha256,
            files["candidate_manifest"]["sha256"])
        candidate = _read(candidate_path)["candidates"][task_key]
        paths = arm.RTDLDeploymentPaths(
            artifact=Path(candidate["artifact_path"]),
            authority=Path(candidate["authority_path"]),
            trust_root=Path(files["trust_root"]["path"]),
            trust_head=Path(files["trust_head"]["path"]),
            trust_package=Path(files["trust_package"]["path"]),
            native_library=Path(files["native_library"]["path"]),
            deployment_id=candidate["deployment_id"],
        )
        adapter = arm.RTDLExecutableAdapter(
            task, workload, paths,
            preloaded_runtime=runtime[0],
            preloaded_implementation=runtime[1],
            runtime_preload_receipt=preload_receipt)
        return adapter, {
            "candidate_manifest_path": str(candidate_path),
            "candidate_manifest_sha256": candidate_sha256,
            "candidate_artifact_sha256": candidate["artifact_sha256"],
            "candidate_authority_sha256": candidate["authority_sha256"],
        }
    adapter = arm.PyOptixScalarAdapter(
        task, workload,
        ptx_path=Path(files["matched_ptx"]["path"]),
        compaction_cubin_path=(
            Path(files["relation_compaction_cubin"]["path"])
            if task_key == "relation" else None),
        preloaded_runtime=runtime,
        runtime_preload_receipt=preload_receipt)
    return adapter, {
        "matched_ptx_expected_sha256": files["matched_ptx"]["sha256"],
        "relation_compaction_cubin_expected_sha256": (
            files["relation_compaction_cubin"]["sha256"]
            if task_key == "relation" else None),
    }


def _input_identities(
    *, arm_name: str, task_key: str, target: dict[str, Any], adapter: Any,
) -> dict[str, Any]:
    files = target["files"]
    if arm_name == "RTDL_PROVIDER_READY":
        observed = adapter.paths.identities()
        checks = {
            "native_sha256": files["native_library"]["sha256"],
            "trust_root_sha256": files["trust_root"]["sha256"],
            "trust_head_sha256": files["trust_head"]["sha256"],
            "trust_package_sha256": files["trust_package"]["sha256"],
        }
        for key, expected in checks.items():
            _require_equal(f"rtdl_{key}", observed[key], expected)
        return observed
    ptx_path = Path(files["matched_ptx"]["path"])
    observed: dict[str, Any] = {
        "matched_ptx_sha256": _sha(ptx_path),
    }
    _require_equal(
        "pyoptix_matched_ptx_sha256", observed["matched_ptx_sha256"],
        files["matched_ptx"]["sha256"])
    if task_key == "relation":
        binding = adapter.compaction_cubin_binding_identity()
        if not isinstance(binding, Mapping):
            raise RuntimeError("Goal5807 relation cubin binding is absent")
        observed["relation_compaction_cubin_sha256"] = binding[
            "source_sha256_observed_at_load"]
        observed["relation_compaction_loader_object_sha256"] = binding[
            "loader_object"]["sha256"]
        _require_equal(
            "pyoptix_relation_compaction_cubin_sha256",
            observed["relation_compaction_cubin_sha256"],
            files["relation_compaction_cubin"]["sha256"])
    return observed


def _run(args: argparse.Namespace) -> dict[str, Any]:
    harness_run_entry_ns = time.perf_counter_ns()
    primary_stack = ExitStack()
    try:
        return _run_impl(
            args, harness_run_entry_ns=harness_run_entry_ns,
            primary_stack=primary_stack)
    finally:
        primary_stack.close()


def _run_impl(
    args: argparse.Namespace, *, harness_run_entry_ns: int,
    primary_stack: ExitStack,
) -> dict[str, Any]:
    ledger = _PhaseLedger(process_entry_ns=_PROCESS_ENTRY_NS)
    with ledger.phase("input_admission"):
        target_path = args.target_manifest.resolve(strict=True)
        target_sha256 = _sha(target_path)
        _require_equal(
            "target_manifest_sha256", target_sha256,
            _require_sha256(
                args.expected_target_manifest_sha256,
                "expected_target_manifest_sha256"))
        target = _read(target_path)
        target_compute_capability, target_capability_source = \
            _sealed_target_compute_capability(target)

    with ledger.phase("runtime_preload"):
        workload_module, arm, runtime, preload_receipt = _runtime_preload(
            args.arm)
    post_runtime_preload_entry_ns = time.perf_counter_ns()

    with ledger.phase("adapter_construct"):
        adapter, construction_identities = _construct_adapter(
            arm_name=args.arm, task_key=args.task, target=target,
            workload_module=workload_module, arm=arm, runtime=runtime,
            preload_receipt=preload_receipt)

    with ledger.phase("install_load"):
        adapter.load()

    provider_identity: dict[str, Any] | None = None
    sealed_cubin_binding: dict[str, Any] | None = None
    relation_cubin_loader_closed_after_close: bool | None = None
    prepared_close_observation: dict[str, Any] | None = None
    if args.arm == "RTDL_PROVIDER_READY":
        with ledger.phase("provider_bind"):
            boundary_driver = _load_cuda_driver()
            provider, current_context_evidence = \
                _call_requiring_current_unchanged(
                    adapter.bind_provider, driver=boundary_driver)
            provider_primary_handle = int(
                provider._cuda_readiness.context_handle)
            primary_lease = primary_stack.enter_context(
                _Device0PrimaryCurrentLease(
                    boundary_driver,
                    expected_compute_capability=(
                        target_compute_capability),
                    expected_preexisting_primary_handle=(
                        provider_primary_handle),
                    persistent_owner="RTDL_PROCESS_LIFETIME_RETAIN"))
            timer_entry_context = primary_lease.evidence
            bind_call_leaves = _call_leaf_names(
                type(adapter.loaded).bind_provider)
            forbidden_bind_calls = sorted(set(bind_call_leaves) & {
                "prepare", "_build_prepared_owner",
                "_PreparedBoundedOwner", "_PreparedTriangleOwner",
            })
            if forbidden_bind_calls:
                raise RuntimeError({
                    "rtdl_bind_provider_constructed_application_owner":
                        forbidden_bind_calls,
                })
            ready_program_identity = {
                "composed_ptx_bytes": len(adapter.loaded.composed_ptx.encode()),
                "composed_ptx_sha256": _sha_bytes(
                    adapter.loaded.composed_ptx.encode()),
            }
        provider_identity = {
            "native_library_path": str(provider.native_library_path),
            "native_library_sha256": provider.native_library_sha256,
            "cache_entry_identity": provider.cache_entry_identity,
            "owner_pid": provider.owner_pid,
            "closed_before_prepare": bool(provider.closed),
        }
        _require_equal(
            "provider_native_library_sha256",
            provider_identity["native_library_sha256"],
            target["files"]["native_library"]["sha256"])
        readiness_assertions = {
            "runtime_provider_loaded": adapter.provider is provider,
            "cuda_primary_ready": provider.owner_pid > 0,
            "exact_program_bytes_loaded": bool(adapter.loaded.composed_ptx),
            "optix_device_context_absent": adapter.prepared is None,
            "pipeline_absent": adapter.prepared is None,
            "bind_provider_has_no_prepare_owner_call": not forbidden_bind_calls,
            "cuda_current_context_restored_before_app_prepare": (
                current_context_evidence["exact_current_context_unchanged"]),
            "cuda_current_context_is_device0_primary_at_app_timer_entry": (
                timer_entry_context["normalized_state"]
                == "DEVICE0_PRIMARY_CURRENT"),
            "cuda_current_context_matches_retained_primary_handle": (
                timer_entry_context[
                    "retained_primary_handle_equals_current"]),
            "device_ordinal_is_zero": (
                timer_entry_context["cuDeviceGet_requested_ordinal"] == 0),
            "target_compute_capability_is_8_6": (
                timer_entry_context["cuDeviceComputeCapability"] == [8, 6]),
            "temporary_primary_retain_live_before_app_prepare": (
                timer_entry_context["temporary_primary_retain_live"]),
        }
        readiness_source = {
            "bind_provider_call_leaf_names": list(bind_call_leaves),
            "forbidden_prepare_owner_call_names": forbidden_bind_calls,
            "binding_contract": (
                "CUDA_PRIMARY_RETAIN_ACTIVATE_RESTORE_PLUS_SEALED_DSO_AND_"
                "PRODUCER_DESCRIPTOR_ONLY__NO_NATIVE_PREPARE_SYMBOL"),
            "cuda_current_context_evidence": current_context_evidence,
            "app_timer_entry_context_normalization": timer_entry_context,
        }
    else:
        with ledger.phase("provider_bind"):
            boundary_driver = _load_cuda_driver()
            current_context_evidence = \
                _pyoptix_primary_ready_preserving_current(
                    runtime.cp.cuda.runtime, driver=boundary_driver)
            primary_lease = primary_stack.enter_context(
                _Device0PrimaryCurrentLease(
                    boundary_driver,
                    expected_compute_capability=(
                        target_compute_capability),
                    persistent_owner="CUPY_RUNTIME_PRIMARY_CONTEXT"))
            timer_entry_context = primary_lease.evidence
            provider_ready_context_factory_leaves = _call_leaf_names(
                _make_provider_ready_validation_off_context)
            if "free" in provider_ready_context_factory_leaves:
                raise RuntimeError(
                    "Goal5807 provider-ready context repeats primary admission")
            loaded_ptx_sha256 = _sha_bytes(adapter.ptx)
            _require_equal(
                "provider_ready_pyoptix_ptx_sha256", loaded_ptx_sha256,
                target["files"]["matched_ptx"]["sha256"])
            ready_program_identity = {
                "matched_ptx_bytes": len(adapter.ptx),
                "matched_ptx_sha256": loaded_ptx_sha256,
                "relation_compaction_cubin_sha256": None,
            }
            if args.task == "relation":
                loaded_cubin_sha256 = _sha_bytes(adapter.compaction_cubin)
                _require_equal(
                    "provider_ready_pyoptix_compaction_cubin_sha256",
                    loaded_cubin_sha256,
                    target["files"]["relation_compaction_cubin"]["sha256"])
                ready_program_identity[
                    "relation_compaction_cubin_sha256"] = loaded_cubin_sha256
                sealed_cubin_binding = \
                    adapter.compaction_cubin_binding_identity()
                if sealed_cubin_binding is None:
                    raise RuntimeError("Goal5807 sealed cubin binding is absent")
                ready_program_identity[
                    "sealed_relation_compaction_cubin_binding"] = \
                    sealed_cubin_binding
        readiness_assertions = {
            "runtime_provider_loaded": all(
                name in sys.modules
                for name in ("cupy", "optix", "optix._optix")),
            "cuda_primary_ready": True,
            "exact_program_bytes_loaded": bool(adapter.ptx),
            "optix_device_context_absent": adapter.context is None,
            "pipeline_absent": adapter.pipeline is None and adapter.owner is None,
            "cuda_current_context_restored_before_app_prepare": (
                current_context_evidence["exact_current_context_restored"]),
            "cuda_current_context_is_device0_primary_at_app_timer_entry": (
                timer_entry_context["normalized_state"]
                == "DEVICE0_PRIMARY_CURRENT"),
            "cuda_current_context_matches_retained_primary_handle": (
                timer_entry_context[
                    "retained_primary_handle_equals_current"]),
            "device_ordinal_is_zero": (
                timer_entry_context["cuDeviceGet_requested_ordinal"] == 0),
            "target_compute_capability_is_8_6": (
                timer_entry_context["cuDeviceComputeCapability"] == [8, 6]),
            "temporary_primary_retain_live_before_app_prepare": (
                timer_entry_context["temporary_primary_retain_live"]),
            "pyoptix_redundant_primary_admission_skipped": (
                "free" not in provider_ready_context_factory_leaves),
            "relation_cubin_write_sealed_or_not_applicable": (
                args.task != "relation"
                or sealed_cubin_binding["loader_object"]["write_sealed"]),
            "relation_cubin_prepare_uses_held_object_or_not_applicable": (
                args.task != "relation"
                or not sealed_cubin_binding["original_path_reopened_by_prepare"]),
        }
        readiness_source = {
            "preload_required_modules": list(
                preload_receipt["required_preloaded_modules"]),
            "primary_readiness_assertion": (
                "cuCtxGetCurrent -> cupy.cuda.runtime.free(0) -> "
                "cuCtxSetCurrent(previous) -> cuCtxGetCurrent"),
            "cuda_current_context_evidence": current_context_evidence,
            "app_timer_entry_context_normalization": timer_entry_context,
            "provider_ready_context_factory": {
                "function": "_make_provider_ready_validation_off_context",
                "call_leaf_names": list(
                    provider_ready_context_factory_leaves),
                "cupy_cuda_runtime_free_zero_call_count": 0,
                "raw_adapter_default_factory_changed": False,
            },
            "adapter_context_is_none": adapter.context is None,
            "adapter_pipeline_is_none": adapter.pipeline is None,
            "adapter_owner_is_none": adapter.owner is None,
        }
    if not all(readiness_assertions.values()):
        raise RuntimeError({
            "goal5807_provider_program_ready_assertion_failed":
                readiness_assertions,
        })

    primary_lease.verify_current("IMMEDIATELY_BEFORE_APP_PREPARE_CLOCK")
    original_pyoptix_context_factory: Any | None = None
    if args.arm == "PYOPTIX_RUNTIME_PROVIDER_PROGRAM_READY":
        original_pyoptix_context_factory = arm._make_validation_off_context
        arm._make_validation_off_context = \
            _make_provider_ready_validation_off_context
    try:
        with ledger.phase("app_prepare"):
            adapter.prepare()
    finally:
        if original_pyoptix_context_factory is not None:
            arm._make_validation_off_context = original_pyoptix_context_factory
    primary_lease.verify_current("IMMEDIATELY_AFTER_APP_PREPARE_CLOCK")
    execute = adapter.measurement_execution_callable()

    with ledger.phase("first_exact_execute"):
        first_result = execute()
        first_exact_output_validated_ns = time.perf_counter_ns()
    primary_lease.verify_current(
        "IMMEDIATELY_AFTER_FIRST_EXACT_OUTPUT_CLOCK")

    contiguous_prefix_boundaries = _contiguous_prefix_boundaries(
        harness_run_entry_ns=harness_run_entry_ns,
        post_runtime_preload_entry_ns=post_runtime_preload_entry_ns,
        first_exact_output_validated_ns=first_exact_output_validated_ns)

    steady_results: list[Any] = []
    steady_samples_ns: list[int] = []
    with ledger.phase("steady"):
        for _index in range(args.steady_repetitions):
            start = time.perf_counter_ns()
            result = execute()
            stop = time.perf_counter_ns()
            steady_results.append(result)
            steady_samples_ns.append(stop - start)
    primary_lease.verify_current("AFTER_STEADY")

    with ledger.phase("evidence_identity"):
        first_lifecycle = adapter.measurement_lifecycle_receipt(first_result)
        first_evidence = adapter.finalize_measurement_evidence(first_result)
        steady_lifecycles = [
            adapter.measurement_lifecycle_receipt(result)
            for result in steady_results
        ]
        steady_evidence = [
            adapter.finalize_measurement_evidence(result)
            for result in steady_results
        ]
        runtime_identity = adapter.runtime_identity()
        input_identities = _input_identities(
            arm_name=args.arm, task_key=args.task, target=target,
            adapter=adapter)
        if args.arm == "RTDL_PROVIDER_READY":
            _require_equal(
                "rtdl_candidate_artifact_sha256",
                input_identities["artifact_sha256"],
                construction_identities["candidate_artifact_sha256"])
            _require_equal(
                "rtdl_candidate_authority_sha256",
                input_identities["authority_sha256"],
                construction_identities["candidate_authority_sha256"])
    primary_lease.verify_current("AFTER_EVIDENCE_IDENTITY")

    if args.arm == "RTDL_PROVIDER_READY":
        with ledger.phase("prepared_close"):
            adapter.close_prepared()
        with ledger.phase("provider_session_close"):
            adapter.close_provider()
        pyoptix_prepared_close_semantics = "COMPLETE_PROVIDER_OWNER_CLOSE"
    else:
        retained_context = adapter.context
        retained_pipeline = adapter.pipeline
        retained_sbt = adapter.sbt
        if any(item is None for item in (
                retained_context, retained_pipeline, retained_sbt)):
            raise RuntimeError(
                "Goal5807 PyOptiX close precondition lacks context/pipeline/SBT")
        with ledger.phase("prepared_close"):
            adapter.close()
        prepared_close_observation = {
            "owner_released": adapter.owner is None,
            "context_retained": adapter.context is retained_context,
            "pipeline_retained": adapter.pipeline is retained_pipeline,
            "sbt_retained": adapter.sbt is retained_sbt,
        }
        if not all(prepared_close_observation.values()):
            raise RuntimeError({
                "goal5807_pyoptix_partial_close_semantics_drift":
                    prepared_close_observation,
            })
        pyoptix_prepared_close_semantics = (
            "PARTIAL_OWNER_CLOSE__PROCESS_TEARDOWN_RETAINS_CONTEXT_PIPELINE_SBT")
        relation_cubin_loader_closed_after_close = \
            adapter.compaction_cubin_loader_closed
        if args.task == "relation" \
                and relation_cubin_loader_closed_after_close is not True:
            raise RuntimeError("Goal5807 sealed cubin loader fd was not closed")
        ledger.unavailable(
            "provider_session_close",
            reason=(
                "frozen PyOptiX adapter exposes no separate provider/session "
                "close; extension lifetime continues to process teardown"))
    primary_stack.close()
    readiness_assertions.update({
        "temporary_primary_retain_balanced": (
            timer_entry_context["temporary_primary_retain_balanced"]),
        "temporary_primary_retain_live_through_close": (
            timer_entry_context[
                "temporary_primary_retain_live_through_close"]),
        "exact_prior_current_restored_after_lifecycle": (
            timer_entry_context["exact_prior_current_restored"]),
    })
    if not all(readiness_assertions.values()):
        raise RuntimeError({
            "goal5807_provider_lifecycle_context_assertion_failed":
                readiness_assertions,
        })
    if provider_identity is not None:
        provider_identity["closed_after_adapter_close"] = bool(provider.closed)
        if provider_identity["closed_before_prepare"] \
                or not provider_identity["closed_after_adapter_close"]:
            raise RuntimeError("Goal5807 provider capability close state differs")

    process_stop_ns = time.perf_counter_ns()
    phase_ledger = ledger.finalize(process_stop_ns=process_stop_ns)
    phase_ledger["phases"]["prepared_close"]["semantic_scope"] = (
        pyoptix_prepared_close_semantics)
    steady_phase_ns = phase_ledger["phases"]["steady"]["duration_ns"]
    steady_sample_sum_ns = sum(steady_samples_ns)
    if not isinstance(steady_phase_ns, int) \
            or steady_sample_sum_ns > steady_phase_ns:
        raise RuntimeError("Goal5807 steady call accounting does not close")

    comparable_app_boundary_ns = _comparable_app_boundary_ns(phase_ledger)

    source_path = Path(__file__).resolve(strict=True)
    comparison_reason = (
        "both arms admit provider/primary readiness, restore the caller state "
        "after readiness work, then mechanically select the retained device-0 "
        "primary context with one balanced temporary retain; both hold exact "
        "program bytes while neither has created its OptixDeviceContext or pipeline; "
        "only prepare + first exact execute is comparable")
    body: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "arm": args.arm,
        "task": args.task,
        "steady_repetitions": args.steady_repetitions,
        "target_manifest": {
            "path": str(target_path),
            "bytes": target_path.stat().st_size,
            "sha256": target_sha256,
            "sealed_target_compute_capability_source": (
                target_capability_source),
        },
        "pilot_source": {
            "path": str(source_path),
            "bytes": source_path.stat().st_size,
            "sha256": _sha(source_path),
        },
        "state": (
            "RTDL_PROVIDER_BOUND__PROGRAM_BYTES_HELD__"
            "DEVICE0_PRIMARY_CURRENT"
            if args.arm == "RTDL_PROVIDER_READY" else
            "PYOPTIX_EXTENSION_LOADED__PRIMARY_ADMITTED__PROGRAM_BYTES_HELD__"
            "DEVICE0_PRIMARY_CURRENT"),
        "provider_program_ready_assertions": readiness_assertions,
        "provider_program_ready_assertion_source": readiness_source,
        "ready_program_identity": ready_program_identity,
        "comparison_contract": {
            "comparison_authorized": True,
            "app_boundary_comparison_authorized": True,
            "app_boundary_ratio_computation_authorized": True,
            "timer_entry_state_mechanically_matched": True,
            "provider_or_runtime_operation_restored_caller_current_before_"
            "normalization": True,
            "app_timer_entry_cuda_context": (
                "DEVICE0_PRIMARY_CURRENT"),
            "pilot_is_formal_or_paper_evidence": False,
            "provider_bind_phase_comparison_authorized": False,
            "delayed_prepared_close_comparison_authorized": False,
            "full_profiled_process_comparison_authorized": False,
            "reason": comparison_reason,
        },
        "phase_ledger": phase_ledger,
        "contiguous_prefix_boundaries": contiguous_prefix_boundaries,
        "comparable_app_boundary": {
            "definition": (
                "APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE"),
            "duration_ns_additive": comparable_app_boundary_ns,
            "component_sum_not_one_contiguous_timer": True,
            "prepared_close_excluded_because_it_occurs_after_steady_and_evidence": (
                True),
        },
        "steady_detail": {
            "samples_ns_nonformal": steady_samples_ns,
            "sample_sum_ns_additive_inside_steady_phase": steady_sample_sum_ns,
            "steady_loop_remainder_ns_additive": (
                steady_phase_ns - steady_sample_sum_ns),
            "statistics_computed": False,
        },
        "identities": {
            "construction": construction_identities,
            "preload_receipt_sha256": _digest(_plain(preload_receipt)),
            "runtime": _plain(runtime_identity),
            "inputs": _plain(input_identities),
            "provider": _plain(provider_identity),
        },
        "validation": {
            "oracle_validated_execution_count": 1 + args.steady_repetitions,
            "first_lifecycle": _plain(first_lifecycle),
            "steady_lifecycles": _plain(steady_lifecycles),
            "first_evidence": _plain(first_evidence),
            "first_evidence_sha256": _digest(_plain(first_evidence)),
            "steady_evidence_sha256": [
                _digest(_plain(item)) for item in steady_evidence
            ],
            "relation_cubin_loader_fd_closed_after_adapter_close": (
                relation_cubin_loader_closed_after_close),
            "pyoptix_prepared_close_semantics": (
                pyoptix_prepared_close_semantics),
            "prepared_close_observation": _plain(
                prepared_close_observation),
        },
        "measurement_contract": {
            "diagnostic_pilot_only": True,
            "paper_claim_authorized": False,
            "inferential_claim_authorized": False,
            "threshold_claim_authorized": False,
            "formal_design_input_only": True,
            "single_fresh_process": True,
            "provider_bind_explicit_for_rtdl": (
                args.arm == "RTDL_PROVIDER_READY"),
            "raw_rtdl_prepare_default_changed": False,
            "pyoptix_natural_public_provider_ready_boundary_claimed": False,
            "pyoptix_harness_constructed_provider_program_ready_boundary": (
                args.arm == "PYOPTIX_RUNTIME_PROVIDER_PROGRAM_READY"),
            "app_timer_entry_state": "DEVICE0_PRIMARY_CURRENT",
            "pilot_performance_claim_authorized": False,
            "exact_program_bytes_loaded_before_comparable_boundary": True,
            "current_cuda_context_restored_before_comparable_boundary": True,
            "pyoptix_relation_cubin_prepare_reopens_original_path": (
                False if args.arm != "RTDL_PROVIDER_READY"
                and args.task == "relation" else None),
            "pyoptix_relation_cubin_loader_object_write_sealed": (
                sealed_cubin_binding["loader_object"]["write_sealed"]
                if sealed_cubin_binding is not None else None),
            "optix_device_context_created_before_comparable_boundary": False,
            "pipeline_created_before_comparable_boundary": False,
            "pyoptix_prepared_close_semantics": (
                pyoptix_prepared_close_semantics),
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "may_replace_goal5806": False,
        },
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    return {**body, "pilot_sha256": _digest(body)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument(
        "--expected-target-manifest-sha256", required=True)
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--task", choices=TASKS, required=True)
    parser.add_argument("--steady-repetitions", type=int, required=True)
    args = parser.parse_args()
    if not 1 <= args.steady_repetitions <= 32:
        raise RuntimeError("steady repetitions must be in [1, 32]")
    result = _run(args)
    sys.stdout.buffer.write(_canonical(result) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
