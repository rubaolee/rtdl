#!/usr/bin/env python3
"""Post-result lifecycle decomposition for the frozen Goal5805 target.

This is deliberately not a formal worker.  It emits no registered performance
sample and cannot update or replace the frozen Goal5805 matrix.  Its purpose is
to locate lifecycle cost inside the two already-measured adapters so a later
successor changes a demonstrated cause rather than tuning a result blindly.
"""

from __future__ import annotations

import argparse
import ctypes
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable

from experiments.goal5802_premeasurement.workload import (
    RELATION_TASK,
    TRIANGLE_TASK,
    relation_workload,
    triangle_workload,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


class _DiagnosticPrimaryContextRetain:
    """Post-result readiness alignment; never a formal/product path."""

    def __init__(self) -> None:
        self.cuda = ctypes.CDLL("libcuda.so.1")
        self.cuda.cuInit.argtypes = [ctypes.c_uint]
        self.cuda.cuInit.restype = ctypes.c_int
        self.cuda.cuDeviceGet.argtypes = [
            ctypes.POINTER(ctypes.c_int), ctypes.c_int]
        self.cuda.cuDeviceGet.restype = ctypes.c_int
        self.cuda.cuCtxGetCurrent.argtypes = [
            ctypes.POINTER(ctypes.c_void_p)]
        self.cuda.cuCtxGetCurrent.restype = ctypes.c_int
        self.cuda.cuCtxSetCurrent.argtypes = [ctypes.c_void_p]
        self.cuda.cuCtxSetCurrent.restype = ctypes.c_int
        self.cuda.cuDevicePrimaryCtxRetain.argtypes = [
            ctypes.POINTER(ctypes.c_void_p), ctypes.c_int]
        self.cuda.cuDevicePrimaryCtxRetain.restype = ctypes.c_int
        self.cuda.cuDevicePrimaryCtxRelease.argtypes = [ctypes.c_int]
        self.cuda.cuDevicePrimaryCtxRelease.restype = ctypes.c_int
        self.device = ctypes.c_int()
        self.context = ctypes.c_void_p()
        self.prior = ctypes.c_void_p()
        self.closed = False
        self.selected = False
        self._require(self.cuda.cuInit(0), "cuInit")
        self._require(self.cuda.cuDeviceGet(ctypes.byref(self.device), 0),
                      "cuDeviceGet")
        self._require(self.cuda.cuCtxGetCurrent(ctypes.byref(self.prior)),
                      "cuCtxGetCurrent")
        self._require(self.cuda.cuDevicePrimaryCtxRetain(
            ctypes.byref(self.context), self.device.value),
            "cuDevicePrimaryCtxRetain")
        try:
            self._require(self.cuda.cuCtxSetCurrent(self.context),
                          "cuCtxSetCurrent")
            self.selected = True
        except BaseException:
            self.cuda.cuDevicePrimaryCtxRelease(self.device.value)
            raise

    @staticmethod
    def _require(status: int, label: str) -> None:
        if int(status) != 0:
            raise RuntimeError(
                f"Goal5807 diagnostic {label} failed with status {status}")

    def restore_caller(self) -> None:
        if self.closed or not self.selected:
            return
        self._require(self.cuda.cuCtxSetCurrent(self.prior),
                      "cuCtxSetCurrent(prior)")
        self.selected = False

    def close(self) -> None:
        if self.closed:
            return
        self.restore_caller()
        self._require(self.cuda.cuDevicePrimaryCtxRelease(self.device.value),
                      "cuDevicePrimaryCtxRelease")
        self.closed = True


def _timed(spans: dict[str, int], name: str, function: Callable[..., Any]) \
        -> Callable[..., Any]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter_ns()
        try:
            return function(*args, **kwargs)
        finally:
            spans[name] = spans.get(name, 0) + time.perf_counter_ns() - start
    return wrapper


def _strip_ptx_entries(ptx: str, names: tuple[str, ...]) -> str:
    """Remove complete PTX entry definitions for a diagnostic-only probe."""

    chunks: list[tuple[int, int]] = []
    for name in names:
        marker = f".visible .entry {name}"
        entry = ptx.find(marker)
        if entry < 0:
            raise RuntimeError(f"diagnostic PTX entry is absent: {name}")
        opening = ptx.find("{", entry)
        if opening < 0:
            raise RuntimeError(f"diagnostic PTX entry lacks body: {name}")
        depth = 0
        closing = -1
        for index in range(opening, len(ptx)):
            if ptx[index] == "{":
                depth += 1
            elif ptx[index] == "}":
                depth -= 1
                if depth == 0:
                    closing = index + 1
                    break
        if closing < 0:
            raise RuntimeError(f"diagnostic PTX entry body is unterminated: {name}")
        line_start = ptx.rfind("\n", 0, entry) + 1
        prior_start = ptx.rfind("\n", 0, max(0, line_start - 1)) + 1
        if ".globl" in ptx[prior_start:line_start] and name in ptx[prior_start:line_start]:
            line_start = prior_start
        while closing < len(ptx) and ptx[closing] in "\r\n":
            closing += 1
        chunks.append((line_start, closing))
    for start, end in sorted(chunks, reverse=True):
        ptx = ptx[:start] + ptx[end:]
    for name in names:
        if name in ptx:
            raise RuntimeError(f"diagnostic PTX symbol survived removal: {name}")
    return ptx


def _rtdl_adapter(task_key: str, task: str, workload: dict[str, Any],
                  target: dict[str, Any], spans: dict[str, int]) \
        -> tuple[Any, dict[str, Any]]:
    from experiments.goal5802_premeasurement.rtdlexe_arm import (
        RTDLDeploymentPaths,
        RTDLExecutableAdapter,
        preload_rtdl_runtime,
    )

    files = target["files"]
    candidate_manifest = _read(Path(files["candidate_manifest"]["path"]))
    candidate = candidate_manifest["candidates"][task_key]
    preload_start = time.perf_counter_ns()
    runtime, implementation, preload = preload_rtdl_runtime()
    spans["runtime_preload"] = time.perf_counter_ns() - preload_start

    implementation._initialize_cuda_and_get_capability = _timed(
        spans, "cuda_capability_admission",
        implementation._initialize_cuda_and_get_capability)
    implementation._sealed_native_image_descriptor = _timed(
        spans, "sealed_native_image_create",
        implementation._sealed_native_image_descriptor)
    implementation._create_unique_native_loader_alias = _timed(
        spans, "native_loader_alias_create",
        implementation._create_unique_native_loader_alias)
    implementation._read_descriptor_bytes = _timed(
        spans, "descriptor_bytes_read_aggregate",
        implementation._read_descriptor_bytes)
    original_cdll = implementation.ctypes.CDLL

    def timed_cdll(name: Any, *args: Any, **kwargs: Any) -> Any:
        label = ("native_dso_dlopen" if str(name).endswith(".so")
                 else "other_cdll_load")
        return _timed(spans, label, original_cdll)(name, *args, **kwargs)

    implementation.ctypes.CDLL = timed_cdll
    implementation._load_native_library = _timed(
        spans, "native_library_load_and_target_check",
        implementation._load_native_library)
    implementation._query_native_producer_descriptor = _timed(
        spans, "native_producer_descriptor_query",
        implementation._query_native_producer_descriptor)
    if task_key == "relation":
        implementation._PreparedBoundedOwner = _timed(
            spans, "prepared_owner_constructor",
            implementation._PreparedBoundedOwner)
    else:
        implementation._PreparedTriangleOwner = _timed(
            spans, "prepared_owner_constructor",
            implementation._PreparedTriangleOwner)

    construct_start = time.perf_counter_ns()
    adapter = RTDLExecutableAdapter(
        task, workload,
        RTDLDeploymentPaths(
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
    spans["adapter_constructor"] = time.perf_counter_ns() - construct_start
    return adapter, {
        "candidate_manifest_sha256": _sha(
            Path(files["candidate_manifest"]["path"])),
        "artifact_sha256": candidate["artifact_sha256"],
        "native_library_sha256": files["native_library"]["sha256"],
    }


def _pyoptix_adapter(task_key: str, task: str, workload: dict[str, Any],
                     target: dict[str, Any], spans: dict[str, int]) \
        -> tuple[Any, dict[str, Any]]:
    import experiments.goal5802_premeasurement.pyoptix_scalar_arm as arm

    files = target["files"]
    preload_start = time.perf_counter_ns()
    runtime, preload = arm.preload_pyoptix_runtime()
    spans["runtime_preload"] = time.perf_counter_ns() - preload_start
    arm._make_validation_off_context = _timed(
        spans, "context_create", arm._make_validation_off_context)
    arm._build_comparative_pipeline = _timed(
        spans, "module_program_groups_pipeline", arm._build_comparative_pipeline)
    runtime.make_sbt = _timed(spans, "sbt_create", runtime.make_sbt)
    if task_key == "relation":
        arm.DeferredRelationPrepared = _timed(
            spans, "prepared_owner_constructor", arm.DeferredRelationPrepared)
    else:
        arm.ScalarTrianglePrepared = _timed(
            spans, "prepared_owner_constructor", arm.ScalarTrianglePrepared)

    construct_start = time.perf_counter_ns()
    adapter = arm.PyOptixScalarAdapter(
        task, workload,
        ptx_path=Path(files["matched_ptx"]["path"]),
        compaction_cubin_path=(
            Path(files["relation_compaction_cubin"]["path"])
            if task_key == "relation" else None),
        preloaded_runtime=runtime,
        runtime_preload_receipt=preload,
    )
    spans["adapter_constructor"] = time.perf_counter_ns() - construct_start
    return adapter, {
        "matched_ptx_sha256": files["matched_ptx"]["sha256"],
        "relation_compaction_cubin_sha256": (
            files["relation_compaction_cubin"]["sha256"]
            if task == "relation" else None),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--arm", choices=("RTDL", "PYOPTIX"), required=True)
    parser.add_argument("--task", choices=("relation", "triangle"), required=True)
    parser.add_argument("--diagnostic-native-override", type=Path)
    parser.add_argument("--diagnostic-native-optimization-level", type=int)
    parser.add_argument(
        "--diagnostic-strip-triangle-diagnostic-entries", action="store_true")
    parser.add_argument(
        "--diagnostic-prewarm-rtdl-primary-context", action="store_true")
    parser.add_argument(
        "--diagnostic-restore-primary-context-before-load",
        action="store_true")
    parser.add_argument(
        "--diagnostic-prewarm-rtdl-native-provider", action="store_true")
    parser.add_argument(
        "--diagnostic-handoff-prewarmed-rtdl-native-provider",
        action="store_true")
    parser.add_argument("--diagnostic-execute-full-after-fast", action="store_true")
    args = parser.parse_args()

    target_path = args.target_manifest.resolve(strict=True)
    target = _read(target_path)
    task_value = RELATION_TASK if args.task == "relation" else TRIANGLE_TASK
    workload = relation_workload() if args.task == "relation" else triangle_workload()
    spans: dict[str, int] = {}
    if args.arm == "RTDL":
        adapter, identities = _rtdl_adapter(
            args.task, task_value, workload, target, spans)
    else:
        adapter, identities = _pyoptix_adapter(
            args.task, task_value, workload, target, spans)

    diagnostic_primary_context = None
    if args.diagnostic_prewarm_rtdl_primary_context:
        if args.arm != "RTDL":
            raise RuntimeError("RTDL primary-context prewarm is RTDL-only")
        prewarm_start = time.perf_counter_ns()
        diagnostic_primary_context = _DiagnosticPrimaryContextRetain()
        spans["excluded_runtime_ready_primary_context_prewarm"] = \
            time.perf_counter_ns() - prewarm_start
        identities["diagnostic_primary_context_prewarm"] = True
        identities["diagnostic_primary_context_prewarm_is_not_formal"] = True
        if args.diagnostic_restore_primary_context_before_load:
            diagnostic_primary_context.restore_caller()
            identities[
                "diagnostic_primary_context_restored_before_load"] = True
    elif args.diagnostic_restore_primary_context_before_load:
        raise RuntimeError(
            "primary-context restore requires primary-context prewarm")

    load_start = time.perf_counter_ns()
    adapter.load()
    load_end = time.perf_counter_ns()
    diagnostic_native_provider_lease = None
    diagnostic_native_provider_handed_off = False
    if args.arm == "RTDL":
        spans["composed_ptx_bytes"] = len(adapter.loaded.composed_ptx.encode())
        if args.diagnostic_strip_triangle_diagnostic_entries:
            if args.task != "triangle":
                raise RuntimeError("triangle diagnostic stripping is triangle-only")
            original_ptx = adapter.loaded.composed_ptx
            stripped_ptx = _strip_ptx_entries(original_ptx, (
                "__raygen__rtdl_v4_triangle_reduction_diagnostic",
                "__anyhit__rtdl_v4_triangle_reduction_diagnostic",
                "__miss__rtdl_v4_triangle_reduction_diagnostic",
            ))
            adapter.loaded = replace(adapter.loaded, composed_ptx=stripped_ptx)
            identities["diagnostic_ptx_override_bypasses_artifact_binding"] = True
            identities["original_composed_ptx_bytes"] = len(original_ptx.encode())
            identities["stripped_composed_ptx_bytes"] = len(stripped_ptx.encode())
            identities["stripped_composed_ptx_sha256"] = hashlib.sha256(
                stripped_ptx.encode()).hexdigest()
        if args.diagnostic_native_override is not None:
            override = args.diagnostic_native_override.resolve(strict=True)
            projection = adapter.implementation_module._plain(
                adapter.loaded.product_projection)
            projection["target_toolchain"]["native_library_sha256"] = _sha(override)
            if args.diagnostic_native_optimization_level is not None:
                projection["execution_schema"]["native_producer_descriptor"] \
                    ["module_compile"]["optimization_level"] = \
                    args.diagnostic_native_optimization_level
            adapter.loaded = replace(
                adapter.loaded, product_projection=projection)
            adapter.paths = replace(adapter.paths, native_library=override)
            identities["diagnostic_native_override_sha256"] = _sha(override)
            identities["diagnostic_native_override_bypasses_artifact_target_binding"] = True
            identities["diagnostic_native_optimization_level"] = \
                args.diagnostic_native_optimization_level
        elif args.diagnostic_native_optimization_level is not None:
            raise RuntimeError("native optimization override requires a native override")
    elif args.diagnostic_native_override is not None \
            or args.diagnostic_strip_triangle_diagnostic_entries:
        raise RuntimeError("RTDL diagnostic override was supplied to PyOptiX")
    if args.diagnostic_handoff_prewarmed_rtdl_native_provider \
            and not args.diagnostic_prewarm_rtdl_native_provider:
        raise RuntimeError(
            "native-provider handoff requires native-provider prewarm")
    if args.diagnostic_prewarm_rtdl_native_provider:
        if args.arm != "RTDL":
            raise RuntimeError("RTDL native-provider prewarm is RTDL-only")
        implementation = adapter.implementation_module
        target_projection = adapter.loaded.product_projection["target_toolchain"]
        native_path = adapter.paths.native_library.resolve(strict=True)
        expected_native_sha256 = target_projection["native_library_sha256"]
        provider_expected_compute_capability = tuple(
            target_projection["compute_capability"])
        provider_start = time.perf_counter_ns()
        diagnostic_native_provider_lease = implementation._load_native_library(
            native_path,
            expected_sha256=expected_native_sha256,
            expected_compute_capability=provider_expected_compute_capability,
        )
        spans["excluded_runtime_ready_native_provider_prewarm"] = \
            time.perf_counter_ns() - provider_start
        identities["diagnostic_native_provider_prewarm"] = True
        identities["diagnostic_native_provider_prewarm_is_not_formal"] = True
        if args.diagnostic_handoff_prewarmed_rtdl_native_provider:
            def handoff_native_provider(
                path: Path, *, expected_sha256: str,
                expected_compute_capability: tuple[int, int],
            ) -> Any:
                nonlocal diagnostic_native_provider_lease
                nonlocal diagnostic_native_provider_handed_off
                if diagnostic_native_provider_handed_off \
                        or diagnostic_native_provider_lease is None:
                    raise RuntimeError(
                        "Goal5807 diagnostic native provider was already handed off")
                if path.resolve(strict=True) != native_path \
                        or expected_sha256 != expected_native_sha256 \
                        or tuple(expected_compute_capability) != \
                        provider_expected_compute_capability:
                    raise RuntimeError(
                        "Goal5807 diagnostic native-provider handoff identity drift")
                lease = diagnostic_native_provider_lease
                diagnostic_native_provider_lease = None
                diagnostic_native_provider_handed_off = True
                return lease

            implementation._load_native_library = handoff_native_provider
            identities[
                "diagnostic_native_provider_handoff_bypasses_public_reverification"] = True
            identities[
                "diagnostic_native_provider_handoff_requires_authenticated_session"] = True
    adapter.prepare()
    prepare_end = time.perf_counter_ns()
    execute = adapter.measurement_execution_callable()
    result = execute()
    execute_end = time.perf_counter_ns()
    lifecycle = adapter.measurement_lifecycle_receipt(result)
    diagnostic_execute_ns = None
    if args.diagnostic_execute_full_after_fast:
        if args.arm != "RTDL":
            raise RuntimeError("full diagnostic execution is RTDL-only")
        diagnostic_start = time.perf_counter_ns()
        diagnostic_result = adapter.execute(diagnostics=True)
        diagnostic_execute_ns = time.perf_counter_ns() - diagnostic_start
        if diagnostic_result.output != result.output:
            raise RuntimeError("diagnostic and fast outputs differ")
    evidence = adapter.finalize_measurement_evidence(result)
    close_start = time.perf_counter_ns()
    adapter.close()
    close_end = time.perf_counter_ns()
    if diagnostic_native_provider_lease is not None:
        adapter.implementation_module._release_native_library_image(
            diagnostic_native_provider_lease)
        diagnostic_native_provider_lease = None
    if diagnostic_primary_context is not None:
        diagnostic_primary_context.close()

    output = {
        "schema": "rtdl.goal5805.postresult_lifecycle_profile.v1",
        "status": "PASS__POSTRESULT_DIAGNOSTIC_ONLY__NOT_FORMAL",
        "arm": args.arm,
        "task": args.task,
        "task_constant": task_value,
        "target_manifest_sha256": _sha(target_path),
        "identities": identities,
        "phases_ns": {
            "load": load_end - load_start,
            "prepare": prepare_end - load_end,
            "first_execute": execute_end - prepare_end,
            "first_full_diagnostic_execute": diagnostic_execute_ns,
            "close": close_end - close_start,
        },
        "instrumented_spans_ns": spans,
        "first_lifecycle": lifecycle,
        "output_matches_oracle": bool(evidence),
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "may_replace_goal5805_formal_result": False,
    }
    print(json.dumps(output, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
