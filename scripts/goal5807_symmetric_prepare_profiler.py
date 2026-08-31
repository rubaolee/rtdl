#!/usr/bin/env python3
"""Symmetric, non-formal Goal5807 load/prepare phase profiler.

This tool profiles the two frozen Goal5806 adapters at the same fresh-process
boundary.  It does not change either adapter or the RTDL product.  Every
reported duration is a host wall-clock diagnostic, never a registered
performance sample.

The event tree distinguishes inclusive from exclusive time.  Exclusive event
time and the phase's unclassified remainder are the only additive quantities.
RTDL module/program-group/pipeline/SBT/GAS/allocation work is deliberately
reported as folded into the opaque native owner upper bound: the public native
prepare export does not expose those subphases, and this profiler must not
invent zeroes for them.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
import functools
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import threading
import time
from typing import Any

from experiments.goal5802_premeasurement.workload import (
    RELATION_TASK,
    TRIANGLE_TASK,
    relation_workload,
    triangle_workload,
)


SCHEMA = "rtdl.goal5807.symmetric_prepare_profile.v1"
STATUS = "PASS__POSTRESULT_DIAGNOSTIC_ONLY__NOT_FORMAL"
REQUIRED_CATEGORIES = (
    "provider_native_acquisition",
    "driver_context",
    "artifact_verification",
    "native_prepare_abi",
    "module_create",
    "program_groups",
    "pipeline_link_stack",
    "sbt",
    "gas",
    "allocations",
    "owner_remainder",
)
PRIMARY_PHASES = ("load", "prepare")
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
    return _sha_bytes(path.read_bytes())


def _require_sha256(value: str, label: str) -> str:
    if len(value) != 64 or any(item not in _SHA256_HEX for item in value):
        raise RuntimeError(f"{label} is not lowercase SHA-256")
    return value


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def _plain(value: object) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return {"bytes": len(value), "sha256": _sha_bytes(value)}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    item = getattr(value, "item", None)
    if callable(item):
        converted = item()
        if converted is not value:
            return _plain(converted)
    return repr(value)


class _TraceRecorder:
    """Single-threaded strict-nesting event recorder."""

    def __init__(self, *, clock_ns: Callable[[], int] = time.perf_counter_ns):
        self._clock_ns = clock_ns
        self._origin_ns = int(clock_ns())
        self._thread_id = threading.get_ident()
        self._events: list[dict[str, Any]] = []
        self._stack: list[int] = []
        self._coverage: dict[tuple[str, str], dict[str, Any]] = {}
        self._hook_availability: dict[str, dict[str, str]] = {}
        self._finalized = False

    def _assert_thread(self) -> None:
        if threading.get_ident() != self._thread_id:
            raise RuntimeError("Goal5807 profiler event entered from another thread")

    def current_phase(self) -> str:
        if not self._stack:
            raise RuntimeError("Goal5807 timed hook executed outside a phase")
        return str(self._events[self._stack[-1]]["phase"])

    @contextmanager
    def span(
        self, *, phase: str, category: str | None, label: str,
        accounting_quality: str = "EXACT_HOST_BOUNDARY",
    ) -> Iterator[None]:
        if self._finalized:
            raise RuntimeError("Goal5807 profiler recorder is already finalized")
        self._assert_thread()
        if category is not None and category not in REQUIRED_CATEGORIES:
            raise RuntimeError(f"unknown Goal5807 category: {category}")
        parent = self._stack[-1] if self._stack else None
        if parent is not None and self._events[parent]["phase"] != phase:
            raise RuntimeError("Goal5807 nested event crosses phase boundary")
        event_id = len(self._events)
        event = {
            "event_id": event_id,
            "parent_event_id": parent,
            "phase": phase,
            "category": category,
            "label": label,
            "accounting_quality": accounting_quality,
            "start_ns": int(self._clock_ns()),
            "end_ns": None,
        }
        self._events.append(event)
        self._stack.append(event_id)
        try:
            yield
        finally:
            self._assert_thread()
            if not self._stack or self._stack[-1] != event_id:
                raise RuntimeError("Goal5807 event nesting is not LIFO")
            event["end_ns"] = int(self._clock_ns())
            self._stack.pop()

    @contextmanager
    def phase(self, name: str) -> Iterator[None]:
        if self._stack:
            raise RuntimeError("Goal5807 phase root cannot be nested")
        with self.span(
                phase=name, category=None, label=f"{name}_wall",
                accounting_quality="PHASE_WALL"):
            yield

    def declare_coverage(
        self, *, phase: str, category: str, status: str, reason: str,
        folded_into: str | None = None,
    ) -> None:
        if phase not in PRIMARY_PHASES:
            raise RuntimeError("coverage declarations are load/prepare-only")
        if category not in REQUIRED_CATEGORIES:
            raise RuntimeError(f"unknown Goal5807 category: {category}")
        if (phase, category) in self._coverage:
            raise RuntimeError(
                f"duplicate Goal5807 coverage declaration: {phase}/{category}")
        row: dict[str, Any] = {"status": status, "reason": reason}
        if folded_into is not None:
            row["folded_into"] = folded_into
        self._coverage[(phase, category)] = row

    def declare_hook_availability(
        self, *, label: str, status: str, reason: str,
    ) -> None:
        if label in self._hook_availability:
            raise RuntimeError(
                f"duplicate Goal5807 hook availability declaration: {label}")
        self._hook_availability[label] = {
            "status": status,
            "reason": reason,
        }

    def finalize(self) -> dict[str, Any]:
        if self._finalized:
            raise RuntimeError("Goal5807 profiler recorder finalized twice")
        if self._stack:
            raise RuntimeError("Goal5807 profiler has open events")
        self._finalized = True

        children: dict[int, list[int]] = {
            index: [] for index in range(len(self._events))}
        for event in self._events:
            parent = event["parent_event_id"]
            if parent is not None:
                children[parent].append(event["event_id"])

        rendered_events: list[dict[str, Any]] = []
        inclusive: dict[int, int] = {}
        exclusive: dict[int, int] = {}
        for event in self._events:
            end = event["end_ns"]
            if not isinstance(end, int) or end < event["start_ns"]:
                raise RuntimeError("Goal5807 event has invalid clock interval")
            inclusive[event["event_id"]] = end - event["start_ns"]
        for event in reversed(self._events):
            event_id = event["event_id"]
            ordered_children = children[event_id]
            previous_end = event["start_ns"]
            child_total = 0
            for child_id in ordered_children:
                child = self._events[child_id]
                if child["start_ns"] < previous_end \
                        or child["end_ns"] > event["end_ns"]:
                    raise RuntimeError(
                        "Goal5807 child intervals overlap or escape their parent")
                previous_end = child["end_ns"]
                child_total += inclusive[child_id]
            value = inclusive[event_id] - child_total
            if value < 0:
                raise RuntimeError("Goal5807 exclusive event time is negative")
            exclusive[event_id] = value

        for event in self._events:
            event_id = event["event_id"]
            rendered_events.append({
                "event_id": event_id,
                "parent_event_id": event["parent_event_id"],
                "phase": event["phase"],
                "category": event["category"],
                "label": event["label"],
                "accounting_quality": event["accounting_quality"],
                "start_offset_ns": event["start_ns"] - self._origin_ns,
                "inclusive_ns": inclusive[event_id],
                "exclusive_ns": exclusive[event_id],
            })

        phases: dict[str, Any] = {}
        phase_names = []
        for event in self._events:
            if event["parent_event_id"] is None:
                phase_names.append(event["phase"])
        if len(phase_names) != len(set(phase_names)):
            raise RuntimeError("Goal5807 phase root is duplicated")
        for phase in phase_names:
            roots = [
                event for event in rendered_events
                if event["phase"] == phase and event["parent_event_id"] is None]
            if len(roots) != 1:
                raise RuntimeError("Goal5807 phase does not have one root")
            root = roots[0]
            descendants = [
                event for event in rendered_events
                if event["phase"] == phase and event["event_id"] != root["event_id"]]
            category_rows: dict[str, Any] = {}
            category_exclusive_total = 0
            for category in REQUIRED_CATEGORIES:
                matches = [
                    event for event in descendants
                    if event["category"] == category]
                observed_exclusive = sum(
                    int(event["exclusive_ns"]) for event in matches)
                observed_inclusive = sum(
                    int(event["inclusive_ns"]) for event in matches)
                declaration = self._coverage.get((phase, category))
                if matches:
                    if declaration is not None and (
                            declaration["status"].startswith("NOT_APPLICABLE")
                            or declaration["status"].startswith("FOLDED_")):
                        raise RuntimeError(
                            "Goal5807 observed a category declared unobservable: "
                            f"{phase}/{category}")
                    status = (
                        declaration["status"] if declaration is not None
                        else "OBSERVED")
                    reason = (
                        declaration["reason"] if declaration is not None
                        else "one or more host-call boundaries were observed")
                    row = {
                        "status": status,
                        "reason": reason,
                        "event_count": len(matches),
                        "inclusive_sum_ns_nonadditive": observed_inclusive,
                        "exclusive_sum_ns_additive": observed_exclusive,
                    }
                    if declaration is not None and "folded_into" in declaration:
                        row["folded_into"] = declaration["folded_into"]
                    category_exclusive_total += observed_exclusive
                else:
                    if declaration is None and phase in PRIMARY_PHASES:
                        raise RuntimeError(
                            f"Goal5807 coverage absent for {phase}/{category}")
                    if declaration is not None \
                            and declaration["status"].startswith("OBSERVED"):
                        raise RuntimeError(
                            "Goal5807 observed hook is absent: "
                            f"{phase}/{category}")
                    declaration = declaration or {
                        "status": "NOT_REPORTED_OUTSIDE_PRIMARY_PHASES",
                        "reason": "category accounting is load/prepare-only",
                    }
                    row = {
                        **declaration,
                        "event_count": 0,
                        "inclusive_sum_ns_nonadditive": None,
                        "exclusive_sum_ns_additive": None,
                    }
                category_rows[category] = row
            unclassified = int(root["exclusive_ns"])
            if category_exclusive_total + unclassified != root["inclusive_ns"]:
                raise RuntimeError(
                    f"Goal5807 additive accounting does not close for {phase}")
            phases[phase] = {
                "wall_ns": root["inclusive_ns"],
                "unclassified_exclusive_ns_additive": unclassified,
                "observed_category_exclusive_ns_additive":
                    category_exclusive_total,
                "additive_closure_ns": category_exclusive_total + unclassified,
                "categories": category_rows,
            }

        return {
            "clock": "time.perf_counter_ns",
            "single_host_thread_trace": True,
            "exclusive_time_is_only_additive_event_quantity": True,
            "inclusive_category_sums_may_double_count_nested_events": True,
            "events": rendered_events,
            "phases": phases,
            "hook_availability": dict(sorted(self._hook_availability.items())),
        }


class _Patches:
    def __init__(self) -> None:
        self._rows: list[tuple[object, str, object]] = []

    def set(self, owner: object, name: str, value: object) -> None:
        if not hasattr(owner, name):
            raise RuntimeError(f"Goal5807 instrumentation hook is absent: {name}")
        self._rows.append((owner, name, getattr(owner, name)))
        setattr(owner, name, value)

    def close(self) -> None:
        while self._rows:
            owner, name, value = self._rows.pop()
            setattr(owner, name, value)

    def __enter__(self) -> "_Patches":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()


def _timed(
    recorder: _TraceRecorder, category: str, label: str,
    function: Callable[..., Any], *,
    accounting_quality: str = "EXACT_HOST_BOUNDARY",
) -> Callable[..., Any]:
    @functools.wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        phase = recorder.current_phase()
        with recorder.span(
                phase=phase, category=category, label=label,
                accounting_quality=accounting_quality):
            return function(*args, **kwargs)
    return wrapper


class _CTypesFunctionProxy:
    """Time one ctypes call while preserving the configured call interface."""

    def __init__(
        self, function: Callable[..., Any], recorder: _TraceRecorder,
        *, label: str,
    ) -> None:
        self._function = function
        self._recorder = recorder
        self._label = label

    @property
    def argtypes(self) -> object:
        return getattr(self._function, "argtypes", None)

    @argtypes.setter
    def argtypes(self, value: object) -> None:
        setattr(self._function, "argtypes", value)

    @property
    def restype(self) -> object:
        return getattr(self._function, "restype", None)

    @restype.setter
    def restype(self, value: object) -> None:
        setattr(self._function, "restype", value)

    def __getattr__(self, name: str) -> object:
        return getattr(self._function, name)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        with self._recorder.span(
                phase=self._recorder.current_phase(),
                category="native_prepare_abi", label=self._label,
                accounting_quality=(
                    "EXACT_PRODUCTION_NATIVE_ABI_WALL__INTERNAL_BREAKDOWN_UNKNOWN")):
            return self._function(*args, **kwargs)


class _PyOptixContextProxy:
    """Forwarding proxy that times the public PyOptiX construction calls."""

    def __init__(self, context: object, recorder: _TraceRecorder):
        self._context = context
        self._recorder = recorder

    def __getattr__(self, name: str) -> object:
        return getattr(self._context, name)

    def _call(self, category: str, label: str, name: str,
              *args: Any, **kwargs: Any) -> Any:
        function = getattr(self._context, name)
        return _timed(self._recorder, category, label, function)(
            *args, **kwargs)

    def moduleCreate(self, *args: Any, **kwargs: Any) -> Any:
        return self._call(
            "module_create", "pyoptix_context_moduleCreate", "moduleCreate",
            *args, **kwargs)

    def programGroupCreate(self, *args: Any, **kwargs: Any) -> Any:
        return self._call(
            "program_groups", "pyoptix_context_programGroupCreate",
            "programGroupCreate", *args, **kwargs)

    def pipelineCreate(self, *args: Any, **kwargs: Any) -> Any:
        return self._call(
            "pipeline_link_stack", "pyoptix_context_pipelineCreate",
            "pipelineCreate", *args, **kwargs)

    def setCacheEnabled(self, *args: Any, **kwargs: Any) -> Any:
        return self._call(
            "driver_context", "pyoptix_context_disk_cache_control",
            "setCacheEnabled", *args, **kwargs)


def _install_rtdl_hooks(
    patches: _Patches, recorder: _TraceRecorder, runtime: object,
    implementation: object, task_key: str,
) -> None:
    patches.set(runtime, "install_rtdlexe_deployment", _timed(
        recorder, "artifact_verification", "rtdl_install_trust_slot",
        getattr(runtime, "install_rtdlexe_deployment")))
    patches.set(runtime, "load_rtdlexe", _timed(
        recorder, "artifact_verification", "rtdl_load_and_verify_artifact",
        getattr(runtime, "load_rtdlexe")))
    patches.set(implementation, "_initialize_cuda_and_get_capability", _timed(
        recorder, "driver_context", "rtdl_python_cuda_capability_admission",
        getattr(implementation, "_initialize_cuda_and_get_capability"),
        accounting_quality=(
            "LOWER_BOUND__NATIVE_OPTIX_CONTEXT_IS_FOLDED_INTO_OWNER")))
    for name, label in (
        ("_read_descriptor_bytes", "rtdl_native_descriptor_bytes_read"),
        ("_sealed_native_image_descriptor", "rtdl_native_memfd_create_write_seal"),
        ("_create_unique_native_loader_alias", "rtdl_native_loader_alias_create"),
        ("_validate_cached_native_image", "rtdl_native_cached_image_validate"),
        ("_load_verified_native_file_descriptor", "rtdl_native_verify_memfd_dlopen"),
        ("_query_native_producer_descriptor", "rtdl_native_producer_descriptor_query"),
    ):
        patches.set(implementation, name, _timed(
            recorder, "provider_native_acquisition", label,
            getattr(implementation, name)))

    original_cdll = implementation.ctypes.CDLL

    def timed_cdll(name: object, *args: Any, **kwargs: Any) -> Any:
        return _timed(
            recorder, "provider_native_acquisition",
            "rtdl_ctypes_cdll", original_cdll)(name, *args, **kwargs)

    patches.set(implementation.ctypes, "CDLL", timed_cdll)
    patches.set(implementation, "_sha_bytes", _timed(
        recorder, "artifact_verification", "rtdl_bytes_sha256",
        implementation._sha_bytes))
    patches.set(implementation.LoadedRTDLExecutable, "prepare", _timed(
        recorder, "owner_remainder", "rtdl_loaded_executable_prepare_aggregate",
        implementation.LoadedRTDLExecutable.prepare,
        accounting_quality=(
            "AGGREGATE__EXCLUSIVE_TIME_IS_PYTHON_REMAINDER_AFTER_CHILDREN")))

    original_load_native = implementation._load_native_library
    native_prepare_symbol = (
        "rtdl_optix_v4_prepare_bounded_relation_callback_v1"
        if task_key == "relation" else
        "rtdl_optix_v4_prepare_triangle_reduction_callback_v1")

    def timed_load_native(*args: Any, **kwargs: Any) -> Any:
        with recorder.span(
                phase=recorder.current_phase(),
                category="provider_native_acquisition",
                label="rtdl_native_load_and_target_check"):
            lease = original_load_native(*args, **kwargs)
            native_prepare = getattr(lease, native_prepare_symbol, None)
            if native_prepare is None:
                raise RuntimeError(
                    f"Goal5807 native prepare symbol absent: {native_prepare_symbol}")
            setattr(lease, native_prepare_symbol, _CTypesFunctionProxy(
                native_prepare, recorder,
                label=f"rtdl_{task_key}_production_native_prepare_abi"))
            return lease

    patches.set(implementation, "_load_native_library", timed_load_native)
    owner_name = (
        "_PreparedBoundedOwner" if task_key == "relation"
        else "_PreparedTriangleOwner")
    patches.set(implementation, owner_name, _timed(
        recorder, "owner_remainder", "rtdl_native_owner_opaque_aggregate",
        getattr(implementation, owner_name),
        accounting_quality=(
            "UPPER_BOUND__INCLUDES_NATIVE_CONTEXT_MODULE_PG_PIPELINE_"
            "STACK_SBT_GAS_ALLOCATIONS")))


def _install_pyoptix_hooks(
    patches: _Patches, recorder: _TraceRecorder, arm: object,
    baseline: object, task_key: str,
) -> None:
    original_context = arm._make_validation_off_context

    @functools.wraps(original_context)
    def context_wrapper(*args: Any, **kwargs: Any) -> Any:
        phase = recorder.current_phase()
        with recorder.span(
                phase=phase, category="driver_context",
                label="pyoptix_cuda_optix_context_create"):
            context, logger = original_context(*args, **kwargs)
        return _PyOptixContextProxy(context, recorder), logger

    patches.set(arm, "_make_validation_off_context", context_wrapper)
    patches.set(baseline.cp.cuda.runtime, "free", _timed(
        recorder, "driver_context", "pyoptix_cuda_runtime_free_zero",
        baseline.cp.cuda.runtime.free,
        accounting_quality="EXACT_HOST_BOUNDARY__MAY_INITIALIZE_CUDA_CONTEXT"))
    optix_init = getattr(baseline.optix, "init", None)
    if callable(optix_init):
        patches.set(baseline.optix, "init", _timed(
            recorder, "driver_context", "pyoptix_optix_init", optix_init))
        recorder.declare_hook_availability(
            label="pyoptix_optix_init",
            status="EXPOSED_AND_INSTRUMENTED",
            reason="installed binding exposes a callable optix.init")
    else:
        recorder.declare_hook_availability(
            label="pyoptix_optix_init",
            status="NOT_EXPOSED_BY_INSTALLED_BINDING",
            reason=(
                "installed binding has no callable optix.init; no zero-duration "
                "event is imputed"))
    patches.set(baseline.optix, "deviceContextCreate", _timed(
        recorder, "driver_context", "pyoptix_optix_device_context_create",
        baseline.optix.deviceContextCreate))
    patches.set(arm, "_build_comparative_pipeline", _timed(
        recorder, "pipeline_link_stack", "pyoptix_pipeline_aggregate",
        arm._build_comparative_pipeline))
    patches.set(baseline, "make_sbt", _timed(
        recorder, "sbt", "pyoptix_sbt_create", baseline.make_sbt))
    patches.set(baseline, "build_custom_gas", _timed(
        recorder, "gas", "pyoptix_static_custom_gas_host_submission",
        baseline.build_custom_gas,
        accounting_quality="HOST_SUBMISSION_ONLY__NOT_GPU_COMPLETION"))
    patches.set(baseline, "build_triangle_gas", _timed(
        recorder, "gas", "pyoptix_static_triangle_gas_host_submission",
        baseline.build_triangle_gas,
        accounting_quality="HOST_SUBMISSION_ONLY__NOT_GPU_COMPLETION"))
    owner_name = (
        "DeferredRelationPrepared" if task_key == "relation"
        else "ScalarTrianglePrepared")
    patches.set(arm, owner_name, _timed(
        recorder, "owner_remainder", "pyoptix_owner_aggregate",
        getattr(arm, owner_name)))

    cp = baseline.cp
    for owner, name, label in (
        (cp, "zeros", "pyoptix_cupy_zeros"),
        (cp, "empty", "pyoptix_cupy_empty"),
        (cp, "asarray", "pyoptix_cupy_asarray"),
        (cp.cuda, "alloc", "pyoptix_cupy_device_alloc"),
        (cp.cuda, "alloc_pinned_memory", "pyoptix_cupy_pinned_alloc"),
        (cp.cuda, "Stream", "pyoptix_cupy_stream_create"),
    ):
        patches.set(owner, name, _timed(
            recorder, "allocations", label, getattr(owner, name)))
    patches.set(cp, "RawModule", _timed(
        recorder, "module_create", "pyoptix_relation_compaction_module",
        cp.RawModule))
    patches.set(baseline, "to_device", _timed(
        recorder, "allocations", "pyoptix_static_input_to_device",
        baseline.to_device))


def _declare_primary_coverage(
    recorder: _TraceRecorder, *, arm: str,
) -> None:
    for category in REQUIRED_CATEGORIES:
        if category != "artifact_verification" \
                and not (arm == "RTDL" and category == "provider_native_acquisition"):
            recorder.declare_coverage(
                phase="load", category=category, status="NOT_APPLICABLE",
                reason="this category is not part of the frozen adapter load boundary")
    if arm == "RTDL":
        recorder.declare_coverage(
            phase="load", category="provider_native_acquisition",
            status="OPTIONAL_OBSERVED__LOAD_DEPENDENCY_CDLL_BOUNDARY",
            reason=(
                "a globally intercepted ctypes.CDLL call may occur while the "
                "signed deployment/artifact loader resolves a native dependency; "
                "absence is also valid on an already-resolved process image"))
        recorder.declare_coverage(
            phase="load", category="artifact_verification",
            status="OBSERVED",
            reason="trust-slot installation and complete .rtdlexe verification")
        for category in (
            "module_create", "program_groups", "pipeline_link_stack", "sbt",
            "gas", "allocations",
        ):
            recorder.declare_coverage(
                phase="prepare", category=category,
                status="FOLDED_INTO_OWNER_UPPER_BOUND",
                reason=(
                    "the production RTDL native prepare export does not expose "
                    "this subphase at the Python boundary"),
                folded_into="native_prepare_abi")
        recorder.declare_coverage(
            phase="prepare", category="driver_context",
            status="OBSERVED_LOWER_BOUND",
            reason=(
                "Python CUDA capability admission is observed; native primary/"
                "OptiX context creation remains folded into owner_remainder"),
            folded_into="native_prepare_abi")
        recorder.declare_coverage(
            phase="prepare", category="provider_native_acquisition",
            status="OBSERVED",
            reason="native read/hash/memfd/alias/dlopen and descriptor boundaries")
        recorder.declare_coverage(
            phase="prepare", category="artifact_verification",
            status="OBSERVED",
            reason=(
                "native image and product PTX identity hashes are observed; "
                "signed artifact verification itself completed during load"))
        recorder.declare_coverage(
            phase="prepare", category="native_prepare_abi",
            status="OBSERVED_EXACT_PRODUCTION_ABI_BOUNDARY",
            reason=(
                "exact native prepare export wall is observed; its context, "
                "module, PG, pipeline, stack, SBT, GAS, and allocation internals "
                "are not separately observable"))
        recorder.declare_coverage(
            phase="prepare", category="owner_remainder",
            status="OBSERVED_EXCLUSIVE_REMAINDER",
            reason=(
                "loaded-executable and owner construction exclusive of observed "
                "provider, verification, and production native ABI children"))
    else:
        recorder.declare_coverage(
            phase="load", category="artifact_verification",
            status="OBSERVED",
            reason="prebuilt PTX/cubin read and frozen adapter validation")
        recorder.declare_coverage(
            phase="prepare", category="provider_native_acquisition",
            status="NOT_APPLICABLE_IN_PREPARE",
            reason="CuPy and PyOptiX provider modules are acquired in runtime_preload")
        recorder.declare_coverage(
            phase="prepare", category="artifact_verification",
            status="NOT_APPLICABLE",
            reason="prebuilt PTX/cubin were read during load")
        recorder.declare_coverage(
            phase="prepare", category="native_prepare_abi",
            status="NOT_APPLICABLE",
            reason="the PyOptiX arm invokes public Python OptiX construction calls")
        for category in (
            "driver_context", "module_create", "program_groups",
            "pipeline_link_stack", "sbt", "allocations",
            "owner_remainder",
        ):
            recorder.declare_coverage(
                phase="prepare", category=category, status="OBSERVED",
                reason="public Python/PyOptiX host-call boundary observed")
        recorder.declare_coverage(
            phase="prepare", category="gas",
            status="OBSERVED_HOST_SUBMISSION_ONLY__NOT_GPU_COMPLETION",
            reason=(
                "PyOptiX accelBuild is enqueued on a nonblocking stream and is "
                "not synchronized before prepare returns"))


def _fresh_process_admission(arm: str) -> dict[str, Any]:
    forbidden = (
        ("rtdsl", "rtdsl.v4_rtdlexe") if arm == "RTDL" else
        ("cupy", "optix", "optix._optix",
         "experiments.goal5796_matched.pyoptix_baseline"))
    present = [name for name in forbidden if name in sys.modules]
    if present:
        raise RuntimeError({"arm_provider_modules_preloaded": present})
    return {
        "status": "PASS__ARM_PROVIDER_MODULES_ABSENT_BEFORE_RUNTIME_PRELOAD",
        "forbidden_modules": list(forbidden),
    }


def _build_adapter(
    args: argparse.Namespace, target: dict[str, Any], recorder: _TraceRecorder,
) -> tuple[object, object, object, dict[str, Any]]:
    files = target["files"]
    task = RELATION_TASK if args.task == "relation" else TRIANGLE_TASK
    workload = relation_workload() if args.task == "relation" else triangle_workload()
    if args.arm == "RTDL":
        with recorder.phase("runtime_preload"):
            with recorder.span(
                    phase="runtime_preload",
                    category="provider_native_acquisition",
                    label="rtdl_arm_and_python_runtime_preload",
                    accounting_quality="AGGREGATE__PYTHON_RUNTIME_IMPORTS"):
                arm = importlib.import_module(
                    "experiments.goal5802_premeasurement.rtdlexe_arm")
                runtime, implementation, preload = arm.preload_rtdl_runtime()
        candidate_manifest = _read(Path(files["candidate_manifest"]["path"]))
        candidate = candidate_manifest["candidates"][args.task]
        with recorder.phase("adapter_construct"):
            adapter = arm.RTDLExecutableAdapter(
                task, workload,
                arm.RTDLDeploymentPaths(
                    artifact=Path(candidate["artifact_path"]),
                    authority=Path(candidate["authority_path"]),
                    trust_root=Path(files["trust_root"]["path"]),
                    trust_head=Path(files["trust_head"]["path"]),
                    trust_package=Path(files["trust_package"]["path"]),
                    native_library=Path(files["native_library"]["path"]),
                    deployment_id=candidate["deployment_id"],
                ),
                preloaded_runtime=runtime,
                preloaded_implementation=implementation,
                runtime_preload_receipt=preload,
            )
        identities = {
            "candidate_manifest_sha256": _sha(
                Path(files["candidate_manifest"]["path"])),
            "artifact_sha256": candidate["artifact_sha256"],
            "native_library_sha256": files["native_library"]["sha256"],
            "runtime_preload_receipt_sha256": _digest(_plain(preload)),
        }
        return adapter, runtime, implementation, identities

    with recorder.phase("runtime_preload"):
        with recorder.span(
                phase="runtime_preload",
                category="provider_native_acquisition",
                label="pyoptix_arm_cupy_optix_runtime_preload",
                accounting_quality="AGGREGATE__PYTHON_AND_NATIVE_IMPORTS"):
            arm = importlib.import_module(
                "experiments.goal5802_premeasurement.pyoptix_scalar_arm")
            baseline, preload = arm.preload_pyoptix_runtime()
    with recorder.phase("adapter_construct"):
        adapter = arm.PyOptixScalarAdapter(
            task, workload,
            ptx_path=Path(files["matched_ptx"]["path"]),
            compaction_cubin_path=(
                Path(files["relation_compaction_cubin"]["path"])
                if args.task == "relation" else None),
            preloaded_runtime=baseline,
            runtime_preload_receipt=preload,
        )
    identities = {
        "matched_ptx_sha256": files["matched_ptx"]["sha256"],
        "relation_compaction_cubin_sha256": (
            files["relation_compaction_cubin"]["sha256"]
            if args.task == "relation" else None),
        "runtime_preload_receipt_sha256": _digest(_plain(preload)),
    }
    return adapter, arm, baseline, identities


def _run(args: argparse.Namespace) -> dict[str, Any]:
    target_path = args.target_manifest.resolve(strict=True)
    target_sha256 = _sha(target_path)
    if target_sha256 != _require_sha256(
            args.expected_target_manifest_sha256,
            "expected_target_manifest_sha256"):
        raise RuntimeError({
            "target_manifest_sha256_mismatch": {
                "expected": args.expected_target_manifest_sha256,
                "observed": target_sha256,
            }
        })
    target = _read(target_path)
    admission = _fresh_process_admission(args.arm)
    recorder = _TraceRecorder()
    adapter, hook_owner, hook_runtime, identities = _build_adapter(
        args, target, recorder)

    with _Patches() as patches:
        if args.arm == "RTDL":
            _install_rtdl_hooks(
                patches, recorder, hook_owner, hook_runtime, args.task)
        else:
            _install_pyoptix_hooks(
                patches, recorder, hook_owner, hook_runtime, args.task)

        with recorder.phase("load"):
            with recorder.span(
                    phase="load", category="artifact_verification",
                    label=(
                        "rtdl_adapter_load_aggregate" if args.arm == "RTDL"
                        else "pyoptix_adapter_load_aggregate")):
                adapter.load()
                if args.arm == "PYOPTIX":
                    loaded_ptx_sha256 = _sha_bytes(adapter.ptx)
                    if loaded_ptx_sha256 \
                            != target["files"]["matched_ptx"]["sha256"]:
                        raise RuntimeError("Goal5807 loaded PyOptiX PTX mismatch")
                    identities["loaded_matched_ptx_sha256"] = loaded_ptx_sha256
                    if args.task == "relation" \
                            and adapter.compaction_cubin is not None:
                        loaded_cubin_sha256 = _sha_bytes(
                            adapter.compaction_cubin)
                        if loaded_cubin_sha256 != target["files"] \
                                ["relation_compaction_cubin"]["sha256"]:
                            raise RuntimeError(
                                "Goal5807 loaded relation compaction cubin mismatch")
                        identities["loaded_relation_compaction_cubin_sha256"] = (
                            loaded_cubin_sha256)
        with recorder.phase("prepare"):
            adapter.prepare()
        # Instrumentation is deliberately limited to load/prepare.  Restoring
        # every module attribute here also proves no profiling wrapper can
        # change the validation execute or close paths.
        patches.close()
        execute = adapter.measurement_execution_callable()
        with recorder.phase("first_execute_validation"):
            result = execute()
            lifecycle = adapter.measurement_lifecycle_receipt(result)
        evidence = adapter.finalize_measurement_evidence(result)
        with recorder.phase("close"):
            adapter.close()

    _declare_primary_coverage(recorder, arm=args.arm)
    trace = recorder.finalize()
    phases = trace["phases"]
    deployment_host_wall_ns = sum(
        int(phases[name]["wall_ns"])
        for name in ("load", "prepare", "first_execute_validation"))
    source_path = Path(__file__).resolve(strict=True)
    body: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "arm": args.arm,
        "task": args.task,
        "task_constant": (
            RELATION_TASK if args.task == "relation" else TRIANGLE_TASK),
        "pid": os.getpid(),
        "target_manifest": {
            "path": str(target_path),
            "bytes": target_path.stat().st_size,
            "sha256": target_sha256,
        },
        "profiler_source": {
            "path": str(source_path),
            "bytes": source_path.stat().st_size,
            "sha256": _sha(source_path),
        },
        "fresh_process_admission": admission,
        "identities": identities,
        "measurement_contract": {
            "same_fresh_process_boundary_per_arm": True,
            "runtime_preload_measured_separately": True,
            "load_prepare_phase_names_match_across_arms": True,
            "host_wall_clock_only": True,
            "gpu_kernel_duration_claimed": False,
            "inclusive_values_additive": False,
            "exclusive_values_additive": True,
            "rtdl_native_subphase_zero_imputed": False,
            "rtdl_native_internal_breakdown_claimed": False,
            "pyoptix_gas_host_submission_is_gpu_completion": False,
            "prepare_phase_gas_duration_comparable_across_arms": False,
            "deployment_load_prepare_first_execute_is_comparable_across_arms": True,
            "instrumentation_removed_before_validation_execute": True,
            "instrumentation_overhead_subtracted": False,
            "single_observation_per_fresh_process": True,
            "medians_or_confidence_intervals_computed": False,
            "environment_gated_instrumented_native_data_included": False,
            "exact_frozen_production_target_used": True,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
        },
        "trace": trace,
        "diagnostic_deployment_host_wall_ns": deployment_host_wall_ns,
        "validation": {
            "output_matches_route_independent_oracle": bool(evidence),
            "final_evidence_sha256": _digest(_plain(evidence)),
            "first_lifecycle_sha256": _digest(_plain(lifecycle)),
        },
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "may_replace_goal5806_formal_result": False,
    }
    return {**body, "profile_sha256": _digest(body)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument(
        "--expected-target-manifest-sha256", required=True)
    parser.add_argument("--arm", choices=("RTDL", "PYOPTIX"), required=True)
    parser.add_argument("--task", choices=("relation", "triangle"), required=True)
    args = parser.parse_args()
    result = _run(args)
    sys.stdout.buffer.write(_canonical(result) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
