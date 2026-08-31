#!/usr/bin/env python3
"""Scalar-only successor to the executed Goal5800 v7 PyOptiX arm.

The device program and low-level PyOptiX construction remain the Goal5796/
Goal5800 implementation.  The only semantic change is removal of the per-ray
host product: the device intermediate remains allocated because the frozen
device program writes it, but successful execution transfers only status and
one weighted U64 scalar.

This module contains no timer and does not authorize a performance run.
"""

from __future__ import annotations

import ast
import ctypes
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
from typing import Any, NamedTuple

try:
    import fcntl as _fcntl
except ImportError:
    _fcntl = None

from experiments.goal5800_pyoptix_owl.pyoptix_idiomatic_arm import (
    ARM as GOAL5800_V7_ARM,
    DeviceStatusFailure,
    OPERATION_LEDGER_SCOPE,
    exact_counts,
    require_execution_contract,
)
from experiments.goal5809_pyoptix_bulk_input import (
    RelationBulkHostInputs,
    TriangleBulkHostInputs,
)

from .workload import RELATION_TASK, TRIANGLE_TASK


ARM = "B_NVIDIA_PYOPTIX_9_1_SOURCE_OPTIX_9_0_COMPAT_SCALAR_ONLY"
LINEAGE = "GOAL5800_V7_PERSISTENT_IDIOMATIC_OWNER__SCALAR_OUTPUT_SUCCESSOR"
PYOPTIX_BASELINE_MODULE = "experiments.goal5796_matched.pyoptix_baseline"
PYOPTIX_REQUIRED_PRELOADED_MODULES = (
    PYOPTIX_BASELINE_MODULE,
    "cupy",
    "numpy",
    "optix",
    "optix._optix",
)
PRIMARY_TIMER_FORBIDDEN_ABSENT_MODULES = ("cuda.bindings.nvrtc",)


def preload_pyoptix_runtime() -> tuple[Any, dict[str, Any]]:
    """Load the deployed PyOptiX runtime before the comparative clock.

    The Goal5802 deployment path consumes prebuilt PTX.  Importing the
    compiler-only NVRTC binding here, or later in ``load``/``prepare``/
    ``execute``, would charge PyOptiX for work that this path does not need.
    The fresh formal worker therefore fails closed if NVRTC is present.
    """

    if any(name in sys.modules for name in PRIMARY_TIMER_FORBIDDEN_ABSENT_MODULES):
        raise RuntimeError(
            "Goal5802 prebuilt-PTX PyOptiX admission found NVRTC preloaded")
    try:
        baseline = importlib.import_module(PYOPTIX_BASELINE_MODULE)
    except BaseException as error:
        raise RuntimeError(
            "Goal5802 PyOptiX runtime preload failed before primary clock") \
            from error
    required_attributes = {
        "cp", "np", "optix", "PARAM_DTYPE", "make_sbt",
        "pipeline_options", "PreparedLaunch",
    }
    missing_attributes = sorted(
        name for name in required_attributes if not hasattr(baseline, name))
    missing_modules = sorted(
        name for name in PYOPTIX_REQUIRED_PRELOADED_MODULES
        if name not in sys.modules)
    forbidden_present = sorted(
        name for name in PRIMARY_TIMER_FORBIDDEN_ABSENT_MODULES
        if name in sys.modules)
    if missing_attributes or missing_modules or forbidden_present:
        raise RuntimeError({
            "pyoptix_runtime_preload_missing_attributes": missing_attributes,
            "pyoptix_runtime_preload_missing_modules": missing_modules,
            "compiler_only_modules_present": forbidden_present,
        })
    receipt = {
        "schema": "rtdl.goal5802.python_runtime_preload.v1",
        "status": "PASS__BEFORE_PRIMARY_CLOCK",
        "arm": ARM,
        "runtime_module": PYOPTIX_BASELINE_MODULE,
        "required_preloaded_modules": list(
            PYOPTIX_REQUIRED_PRELOADED_MODULES),
        "forbidden_absent_modules": list(
            PRIMARY_TIMER_FORBIDDEN_ABSENT_MODULES),
        "compiler_only_nvrtc_loaded": False,
        "prebuilt_ptx_deployment": True,
        "runtime_import_inside_primary_timer": False,
    }
    return baseline, receipt


def _make_validation_off_context(baseline: Any) -> tuple[Any, None]:
    """Create a comparative context with validation and callbacks both OFF."""

    baseline.cp.cuda.runtime.free(0)
    if hasattr(baseline.optix, "init"):
        baseline.optix.init()
    options = baseline.optix.DeviceContextOptions()
    validation_off = getattr(
        baseline.optix, "DEVICE_CONTEXT_VALIDATION_MODE_OFF", None)
    if validation_off is None:
        raise RuntimeError("PyOptiX does not expose validation-mode OFF")
    options.validationMode = validation_off
    return baseline.optix.deviceContextCreate(0, options), None


def _build_comparative_pipeline(
        baseline: Any, context: Any, ptx: bytes, *, task: str,
        ) -> tuple[Any, list[Any], dict[str, Any]]:
    """Goal5802 pipeline with Direct/RTDL-matched module debug settings."""

    optix = baseline.optix
    custom = task == "relation"
    options = baseline.pipeline_options(custom=custom)
    module_options = optix.ModuleCompileOptions(
        maxRegisterCount=optix.COMPILE_DEFAULT_MAX_REGISTER_COUNT,
        optLevel=optix.COMPILE_OPTIMIZATION_DEFAULT,
        debugLevel=optix.COMPILE_DEBUG_LEVEL_NONE,
    )
    module, module_log = context.moduleCreate(module_options, options, ptx)
    raygen = optix.ProgramGroupDesc()
    raygen.raygenModule = module
    raygen.raygenEntryFunctionName = (
        "__raygen__goal5796_relation"
        if custom else "__raygen__goal5796_triangle")
    raygen_group, raygen_log = context.programGroupCreate([raygen])
    miss = optix.ProgramGroupDesc()
    miss.missModule = module
    miss.missEntryFunctionName = (
        "__miss__goal5796_relation" if custom else "__miss__goal5796_triangle")
    miss_group, miss_log = context.programGroupCreate([miss])
    hit = optix.ProgramGroupDesc()
    hit.hitgroupModuleAH = module
    hit.hitgroupEntryFunctionNameAH = (
        "__anyhit__goal5796_relation"
        if custom else "__anyhit__goal5796_triangle")
    if custom:
        hit.hitgroupModuleIS = module
        hit.hitgroupEntryFunctionNameIS = "__intersection__goal5796_relation"
    hit_group, hit_log = context.programGroupCreate([hit])
    groups = [raygen_group[0], miss_group[0], hit_group[0]]
    link = optix.PipelineLinkOptions()
    link.maxTraceDepth = 1
    pipeline = context.pipelineCreate(options, link, groups, "")
    stack = optix.StackSizes()
    for group in groups:
        if optix.version()[:2] >= (7, 7):
            optix.util.accumulateStackSizes(group, stack, pipeline)
        else:
            optix.util.accumulateStackSizes(group, stack)
    dc_trav, dc_state, cc = optix.util.computeStackSizes(stack, 1, 0, 0)
    pipeline.setStackSize(dc_trav, dc_state, cc, 1)
    return pipeline, groups, {
        "module": module_log, "raygen": raygen_log,
        "miss": miss_log, "hitgroup": hit_log,
    }


def _enqueue_pinned_dynamic_h2d(
        baseline: Any, launcher: Any, host_array: Any,
        trace: dict[str, Any] | None) -> Any:
    """Allocate device storage and enqueue one truly asynchronous H2D copy."""

    device = baseline.cp.cuda.alloc(int(host_array.nbytes))
    raw_stream = getattr(launcher, "_raw_stream", None)
    if raw_stream is None:
        raise RuntimeError("PreparedLaunch does not expose its owned CuPy stream")
    device.copy_from_async(
        ctypes.c_void_p(int(host_array.ctypes.data)), int(host_array.nbytes),
        raw_stream)
    if trace is not None:
        trace["dynamic_device_upload_call_count"] += 1
        trace["dynamic_device_upload_bytes"] += int(host_array.nbytes)
    return device


def _build_dynamic_custom_gas_async(
        baseline: Any, context: Any, launcher: Any, boxes: Any,
        pinned_aabbs: Any, trace: dict[str, Any] | None,
        ) -> tuple[Any, tuple[Any, Any, Any]]:
    """Enqueue the dynamic AABB upload and GAS build on the owner stream."""

    pinned_aabbs[:, 0:2] = baseline.np.stack(
        (boxes["lower_x"], boxes["lower_y"]), axis=1)
    pinned_aabbs[:, 2] = baseline.np.float32(-0.001)
    pinned_aabbs[:, 3:5] = baseline.np.stack(
        (boxes["upper_x"], boxes["upper_y"]), axis=1)
    pinned_aabbs[:, 5] = baseline.np.float32(0.001)
    device_aabbs = _enqueue_pinned_dynamic_h2d(
        baseline, launcher, pinned_aabbs.reshape(-1), trace)
    build_input = baseline.optix.BuildInputCustomPrimitiveArray(
        aabbBuffers=[device_aabbs.ptr], numPrimitives=len(boxes),
        flags=[baseline.optix.GEOMETRY_FLAG_NONE], numSbtRecords=1)
    options = baseline.optix.AccelBuildOptions(
        buildFlags=int(baseline.optix.BUILD_FLAG_NONE),
        operation=baseline.optix.BUILD_OPERATION_BUILD)
    sizes = context.accelComputeMemoryUsage([options], [build_input])
    temporary = baseline.cp.cuda.alloc(sizes.tempSizeInBytes)
    output = baseline.cp.cuda.alloc(sizes.outputSizeInBytes)
    handle = context.accelBuild(
        int(launcher.stream.ptr), [options], [build_input],
        temporary.ptr, sizes.tempSizeInBytes,
        output.ptr, sizes.outputSizeInBytes, [])
    if trace is not None:
        trace["dynamic_accel_build_count"] += 1
    return handle, (device_aabbs, temporary, output)


def _dynamic_trace(*, reused: bool, generation: int) -> dict[str, Any]:
    """Create the live per-execute trace populated only by executed helpers."""

    return {
        "prepared_input_reused": reused,
        "dynamic_device_upload_call_count": 0,
        "dynamic_device_upload_bytes": 0,
        "dynamic_accel_build_count": 0,
        "dynamic_explicit_sync_count": 0,
        "dynamic_blocking_upload_call_count": 0,
        "dynamic_input_generation": generation,
    }


class _RelationFastResult(NamedTuple):
    output: list[list[int]]
    raw_event_count: int
    semantic_unique_count: int
    device_status: int
    device_overflow: int
    prepared_input_reused: bool
    dynamic_input_generation: int


class _TriangleFastResult(NamedTuple):
    reduced_u64: int
    device_status: int
    prepared_input_reused: bool
    dynamic_input_generation: int


class _ComparativePreparedLaunch:
    """Minimal product path: no observer, counter dict, or label-list work."""

    def __init__(self, baseline: Any, pipeline: Any, sbt: Any):
        self.b = baseline
        self.pipeline = pipeline
        self.sbt = sbt
        self._raw_stream = baseline.cp.cuda.Stream(non_blocking=True)
        self.stream = self._raw_stream
        self.device_params = baseline.cp.cuda.alloc(baseline.PARAM_DTYPE.itemsize)
        self._pinned_keepalive: list[tuple[Any, Any]] = []
        self._pinned_by_array_id: dict[int, Any] = {}
        self._pending = False
        self._closed = False

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("comparative prepared launch is closed")

    def zero_on_stream(self, *arrays: Any) -> None:
        self._require_open()
        with self._raw_stream:
            for array in arrays:
                self.b.cp.cuda.runtime.memsetAsync(
                    int(array.data.ptr), 0, int(array.nbytes),
                    int(self._raw_stream.ptr))

    def fill_ff_on_stream(self, array: Any) -> None:
        self._require_open()
        self.b.cp.cuda.runtime.memsetAsync(
            int(array.data.ptr), 0xff, int(array.nbytes),
            int(self._raw_stream.ptr))

    def pinned_array(self, shape: Any, dtype: Any) -> Any:
        self._require_open()
        dtype = self.b.np.dtype(dtype)
        item_count = int(self.b.np.prod(shape))
        pinned = self.b.cp.cuda.alloc_pinned_memory(
            item_count * dtype.itemsize)
        array = self.b.np.frombuffer(
            pinned, dtype=dtype, count=item_count).reshape(shape)
        array.fill(0)
        self._pinned_keepalive.append((pinned, array))
        self._pinned_by_array_id[id(array)] = pinned
        return array

    def enqueue(self, params: Any, width: int) -> None:
        self._require_open()
        if params.shape != (1,) or params.dtype != self.b.PARAM_DTYPE \
                or params.nbytes != self.b.PARAM_DTYPE.itemsize \
                or not params.flags.c_contiguous:
            raise ValueError("prepared launch parameter ABI mismatch")
        pinned = self._pinned_by_array_id.get(id(params))
        if pinned is None:
            raise ValueError("launch parameters are not owned pinned memory")
        self.device_params.copy_from_async(
            ctypes.c_void_p(pinned.ptr), params.nbytes, self._raw_stream)
        self.b.optix.launch(
            self.pipeline, self._raw_stream.ptr, self.device_params.ptr,
            params.dtype.itemsize, self.sbt, width, 1, 1)
        self._pending = True

    def enqueue_compaction(
            self, kernel: Any, arguments: tuple[Any, ...],
            *, element_count: int) -> None:
        self._require_open()
        block_size = 256
        grid_size = (int(element_count) + block_size - 1) // block_size
        kernel(
            (grid_size,), (block_size,), arguments,
            stream=self._raw_stream)
        self._pending = True

    def enqueue_d2d(self, destination: Any, source: Any, nbytes: int) -> None:
        self._require_open()
        nbytes = int(nbytes)
        if nbytes < 0 or nbytes > int(destination.nbytes) \
                or nbytes > int(source.nbytes):
            raise ValueError("prepared D2D byte count is out of bounds")
        self.b.cp.cuda.runtime.memcpyAsync(
            int(destination.data.ptr), int(source.data.ptr), nbytes,
            int(self.b.cp.cuda.runtime.memcpyDeviceToDevice),
            int(self._raw_stream.ptr))
        self._pending = True

    def enqueue_d2h(
            self, device_array: Any, host_array: Any, nbytes: int) -> None:
        self._require_open()
        nbytes = int(nbytes)
        if nbytes < 0 or nbytes > int(device_array.nbytes) \
                or nbytes > int(host_array.nbytes):
            raise ValueError("prepared D2H byte count is out of bounds")
        pinned = self._pinned_by_array_id.get(id(host_array))
        if pinned is None:
            raise ValueError("D2H destination is not owned pinned memory")
        device_array.data.copy_to_host_async(
            ctypes.c_void_p(pinned.ptr), nbytes, self._raw_stream)
        self._pending = True

    def synchronize(self) -> None:
        self._require_open()
        self._raw_stream.synchronize()
        self._pending = False

    def close(self) -> None:
        if self._closed:
            return
        if self._pending:
            self._raw_stream.synchronize()
        self._closed = True
        self.device_params = None
        self.stream = None
        self._pinned_by_array_id = {}
        self._pinned_keepalive = []


class _ObservedCompatiblePreparedLaunch:
    """Untimed observer facade over the exact comparative launcher vocabulary.

    The owner executes the same ``_execute_fast`` core in formal and KAT
    modes.  This facade adds counters and labels only around the same primitive
    calls; it does not retain a second semantic execution implementation.
    """

    def __init__(
            self, baseline: Any, pipeline: Any, sbt: Any, *, kind: str,
            operation_counts: dict[str, int]):
        if kind not in {"relation", "triangle"}:
            raise ValueError("invalid observed launcher kind")
        self.b = baseline
        self.kind = kind
        self.operation_counts = operation_counts
        self._owner = baseline.PreparedLaunch(
            pipeline, sbt, operation_counts=self.operation_counts)
        self._enqueue_index = 0
        self._d2h_index = 0
        self._sync_index = 0

    @property
    def _raw_stream(self) -> Any:
        return self._owner._raw_stream

    @property
    def stream(self) -> Any:
        return self._owner.stream

    @property
    def execution_events(self) -> list[str]:
        return self._owner.execution_events

    def pinned_array(self, shape: Any, dtype: Any) -> Any:
        return self._owner.pinned_array(shape, dtype)

    def observe_execution(self) -> Any:
        self._enqueue_index = 0
        self._d2h_index = 0
        self._sync_index = 0
        return self._owner.observe_execution()

    def zero_on_stream(self, *arrays: Any) -> None:
        labels = (
            ("control_reset", "max_key_reset", "unique_count_reset")
            if self.kind == "relation" else
            ("per_ray_reset", "scalar_reset", "status_reset"))
        if len(arrays) != len(labels):
            raise RuntimeError("observed reset call shape differs")
        self._owner.zero_on_stream(*arrays, events=labels)

    def fill_ff_on_stream(self, array: Any) -> None:
        self.b.cp.cuda.runtime.memsetAsync(
            int(array.data.ptr), 0xff, int(array.nbytes),
            int(self._raw_stream.ptr))
        self.operation_counts["execute_device_zero_fill_call_count"] += 1
        self.execution_events.append("keys_fill_ff")

    def enqueue(self, params: Any, width: int) -> None:
        index = self._enqueue_index
        self._enqueue_index += 1
        if self.kind == "relation":
            h2d_event, launch_event = f"params{index}_h2d", f"launch{index}"
        else:
            h2d_event, launch_event = "params_h2d", "launch"
        self._owner.enqueue(
            params, width, h2d_event=h2d_event, launch_event=launch_event)

    def enqueue_compaction(
            self, kernel: Any, arguments: tuple[Any, ...],
            *, element_count: int) -> None:
        block_size = 256
        grid_size = (int(element_count) + block_size - 1) // block_size
        kernel(
            (grid_size,), (block_size,), arguments,
            stream=self._raw_stream)
        self.operation_counts["execute_launch_call_count"] += 1
        self.execution_events.append("semantic_compaction")
        self._owner._pending = True

    def enqueue_d2d(self, destination: Any, source: Any, nbytes: int) -> None:
        nbytes = int(nbytes)
        if nbytes < 0 or nbytes > int(destination.nbytes) \
                or nbytes > int(source.nbytes):
            raise ValueError("observed D2D byte count is out of bounds")
        self.b.cp.cuda.runtime.memcpyAsync(
            int(destination.data.ptr), int(source.data.ptr), nbytes,
            int(self.b.cp.cuda.runtime.memcpyDeviceToDevice),
            int(self._raw_stream.ptr))
        self.execution_events.append("unique_count_d2d")
        self._owner._pending = True

    def enqueue_d2h(
            self, device_array: Any, host_array: Any, nbytes: int) -> None:
        labels = (
            ("control_d2h", "unique_rows_d2h")
            if self.kind == "relation" else
            ("status_d2h", "scalar_d2h"))
        if self._d2h_index >= len(labels):
            raise RuntimeError("observed D2H call shape differs")
        event = labels[self._d2h_index]
        self._d2h_index += 1
        self._owner.enqueue_d2h(
            device_array, host_array, nbytes, event=event)

    def synchronize(self) -> None:
        labels = (
            ("status_ready_sync", "output_ready_sync")
            if self.kind == "relation" else
            ("status_ready_sync", "scalar_ready_sync"))
        if self._sync_index >= len(labels):
            raise RuntimeError("observed sync call shape differs")
        event = labels[self._sync_index]
        self._sync_index += 1
        self._owner.synchronize(event=event)

    def close(self) -> None:
        self._owner.close()


def _attribute_path(node: ast.AST) -> str | None:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    parts.append(node.id)
    return ".".join(reversed(parts))


def validate_scalar_execute_source(source: Path | None = None) -> dict[str, object]:
    source = Path(__file__).resolve() if source is None else source.resolve()
    raw = source.read_bytes()
    tree = ast.parse(raw, filename=str(source))
    classes = {
        node.name: node for node in tree.body if isinstance(node, ast.ClassDef)
        and node.name in {"DeferredRelationPrepared", "ScalarTrianglePrepared"}
    }
    if set(classes) != {"DeferredRelationPrepared", "ScalarTrianglePrepared"}:
        raise RuntimeError("PyOptiX owner classes absent/ambiguous")
    fast_launchers = [
        node for node in tree.body if isinstance(node, ast.ClassDef)
        and node.name == "_ComparativePreparedLaunch"]
    if len(fast_launchers) != 1:
        raise RuntimeError("PyOptiX comparative launcher absent/ambiguous")

    module_functions = {
        node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    context_factory = module_functions.get("_make_validation_off_context")
    context_source = (
        ast.get_source_segment(raw.decode("utf-8"), context_factory) or ""
        if context_factory is not None else "")
    if context_factory is None \
            or "DEVICE_CONTEXT_VALIDATION_MODE_OFF" not in context_source \
            or "DEVICE_CONTEXT_VALIDATION_MODE_ALL" in context_source \
            or "logCallbackFunction" in context_source \
            or "logCallbackLevel" in context_source:
        raise RuntimeError("PyOptiX comparative validation mode is not OFF")
    pipeline_factory = module_functions.get("_build_comparative_pipeline")
    pipeline_source = (
        ast.get_source_segment(raw.decode("utf-8"), pipeline_factory) or ""
        if pipeline_factory is not None else "")
    if pipeline_factory is None \
            or "COMPILE_OPTIMIZATION_DEFAULT" not in pipeline_source \
            or "COMPILE_DEBUG_LEVEL_NONE" not in pipeline_source \
            or "COMPILE_DEBUG_LEVEL_DEFAULT" in pipeline_source:
        raise RuntimeError("PyOptiX comparative module settings differ")

    def method(class_name: str, method_name: str) -> ast.FunctionDef:
        matches = [
            node for node in classes[class_name].body
            if isinstance(node, ast.FunctionDef) and node.name == method_name]
        if len(matches) != 1:
            raise RuntimeError(
                f"PyOptiX {class_name}.{method_name} absent/ambiguous")
        return matches[0]

    relation_init_source = ast.get_source_segment(
        raw.decode("utf-8"), method("DeferredRelationPrepared", "__init__")) or ""
    if '2 * self.semantic_capacity' not in relation_init_source \
            or "8194" in relation_init_source:
        raise RuntimeError("PyOptiX relation device raw-capacity policy differs")

    methods = [method("ScalarTrianglePrepared", "_execute_fast")]
    calls: dict[str, int] = {}
    forbidden: list[str] = []
    for node in ast.walk(methods[0]):
        if not isinstance(node, ast.Call):
            continue
        path = _attribute_path(node.func)
        key = path if path is not None else "<dynamic>"
        calls[key] = calls.get(key, 0) + 1
        if path is not None and path.startswith((
                "b.cp.", "b.optix.", "cp.", "cuda.", "optix.", "self.d_")):
            forbidden.append(path)
        if path in {"self.h_per_ray.tolist", "cp.asnumpy"}:
            forbidden.append(path)
    launcher = {
        key.removeprefix("self.launcher."): count
        for key, count in calls.items() if key.startswith("self.launcher.")
    }
    expected_launcher = {
        "zero_on_stream": 1,
        "enqueue": 1,
        "enqueue_d2h": 2,
        "synchronize": 2,
    }
    if forbidden or launcher != expected_launcher:
        raise RuntimeError({
            "forbidden": sorted(forbidden),
            "launcher": launcher,
            "expected_launcher": expected_launcher,
        })
    text = raw.decode("utf-8")
    method_source = ast.get_source_segment(text, methods[0]) or ""
    for literal in (
            "h_per_ray", "expected_per_ray", "cp.asnumpy"):
        if literal in method_source:
            raise RuntimeError(f"per-ray host path entered scalar execute: {literal}")

    live_guard_shape: dict[str, dict[str, int]] = {}
    for class_name in sorted(classes):
        execute_method = method(class_name, "execute")
        guarded_method = method(class_name, "execute_with_operation_guard")
        execute_paths = [
            _attribute_path(node.func) for node in ast.walk(execute_method)
            if isinstance(node, ast.Call)]
        guarded_paths = [
            _attribute_path(node.func) for node in ast.walk(guarded_method)
            if isinstance(node, ast.Call)]
        live_count = sum(path == "self.launcher.observe_execution"
                         for path in execute_paths)
        kat_count = sum(path == "self.launcher.observe_execution"
                        for path in guarded_paths)
        fast_count = sum(path == "self._execute_fast"
                         for path in execute_paths)
        observed_count = sum(path == "self._execute_observed"
                             for path in execute_paths)
        kat_core_count = sum(path == "self._execute_observed"
                             for path in guarded_paths)
        observed_core_fast_count = sum(
            path == "self._execute_fast"
            for path in [
                _attribute_path(node.func)
                for node in ast.walk(method(class_name, "_execute_observed"))
                if isinstance(node, ast.Call)])
        reset_count = sum(path == "self.launcher.begin_execution"
                          for path in execute_paths)
        if (live_count, kat_count, fast_count, observed_count,
                kat_core_count, observed_core_fast_count, reset_count) \
                != (0, 1, 1, 0, 1, 1, 0):
            raise RuntimeError({
                "class": class_name,
                "timed_observer_count": live_count,
                "untimed_kat_observer_count": kat_count,
                "timed_fast_core_call_count": fast_count,
                "timed_observed_core_call_count": observed_count,
                "untimed_observed_core_call_count": kat_core_count,
                "observed_wrapper_common_fast_core_call_count":
                    observed_core_fast_count,
                "timed_event_reset_count": reset_count,
            })
        live_guard_shape[class_name] = {
            "timed_observer_count": live_count,
            "untimed_kat_observer_count": kat_count,
            "timed_fast_core_call_count": fast_count,
            "timed_observed_core_call_count": observed_count,
            "untimed_observed_core_call_count": kat_core_count,
            "observed_wrapper_common_fast_core_call_count":
                observed_core_fast_count,
            "timed_event_reset_count": reset_count,
        }

    relation_method = method("DeferredRelationPrepared", "_execute_fast")
    relation_calls: list[str] = []
    forbidden_rowwise: list[str] = []
    for node in ast.walk(relation_method):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            path = node.func.id
        else:
            path = _attribute_path(node.func) or "<dynamic>"
        relation_calls.append(path)
        if path in {"set", "map", "sorted"}:
            forbidden_rowwise.append(path)
    canonicalization = {
        "numpy_lexsort_call_count": relation_calls.count("b.np.lexsort"),
        "numpy_adjacent_any_call_count": relation_calls.count("b.np.any"),
        "python_rowwise_builtin_calls": sorted(forbidden_rowwise),
    }
    if canonicalization != {
            "numpy_lexsort_call_count": 1,
            "numpy_adjacent_any_call_count": 0,
            "python_rowwise_builtin_calls": []}:
        raise RuntimeError({"relation_canonicalization": canonicalization})

    expected_launcher_by_class = {
        "DeferredRelationPrepared": {
            "zero_on_stream": 1, "fill_ff_on_stream": 1,
            "enqueue": 1, "enqueue_compaction": 1, "enqueue_d2d": 1,
            "enqueue_d2h": 2, "synchronize": 2,
        },
        "ScalarTrianglePrepared": expected_launcher,
    }
    execute_boundary_shape: dict[str, dict[str, object]] = {}
    fast_result_shape: dict[str, dict[str, object]] = {}
    expected_result_constructor = {
        "DeferredRelationPrepared": "_RelationFastResult",
        "ScalarTrianglePrepared": "_TriangleFastResult",
    }
    for class_name in sorted(classes):
        core = method(class_name, "_execute_fast")
        launcher_calls: dict[str, int] = {}
        hidden_gpu_or_helper_calls: list[str] = []
        for node in ast.walk(core):
            if not isinstance(node, ast.Call):
                continue
            path = _attribute_path(node.func)
            if path is None:
                continue
            if path.startswith("self.launcher."):
                key = path.removeprefix("self.launcher.")
                launcher_calls[key] = launcher_calls.get(key, 0) + 1
            elif path.startswith("self."):
                # No execute-time helper may hide a launch, transfer, sync, or
                # observer outside the audited PreparedLaunch vocabulary.
                hidden_gpu_or_helper_calls.append(path)
            elif path.startswith(("b.cp.", "b.optix.", "cp.", "cuda.",
                                  "optix.")):
                hidden_gpu_or_helper_calls.append(path)
            elif path.startswith("b.") and path not in {
                    "b.operation_count_delta", "b.np.lexsort", "b.np.empty",
                    "b.np.any", "b.np.uint32"}:
                hidden_gpu_or_helper_calls.append(path)
        if launcher_calls != expected_launcher_by_class[class_name] \
                or hidden_gpu_or_helper_calls:
            raise RuntimeError({
                "class": class_name,
                "launcher_calls": launcher_calls,
                "expected": expected_launcher_by_class[class_name],
                "hidden_gpu_or_helper_calls": sorted(
                    hidden_gpu_or_helper_calls),
            })
        execute_boundary_shape[class_name] = {
            "launcher_calls": launcher_calls,
            "hidden_gpu_or_helper_calls": [],
        }
        success_returns = [
            node.value for node in ast.walk(core)
            if isinstance(node, ast.Return)]
        constructors = [
            value.func.id for value in success_returns
            if isinstance(value, ast.Call) and isinstance(value.func, ast.Name)]
        return_dict_count = sum(
            isinstance(value, ast.Dict) for value in success_returns)
        timed_execute = method(class_name, "execute")
        timed_dict_count = sum(
            isinstance(node, ast.Dict) for node in ast.walk(timed_execute))
        timed_trace_call_count = sum(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_dynamic_trace"
            for node in ast.walk(timed_execute))
        if constructors != [expected_result_constructor[class_name]] \
                or return_dict_count != 0 or timed_dict_count != 0 \
                or timed_trace_call_count != 0:
            raise RuntimeError({
                "class": class_name,
                "formal_result_constructors": constructors,
                "formal_return_dict_count": return_dict_count,
                "timed_execute_dict_count": timed_dict_count,
                "timed_execute_trace_call_count": timed_trace_call_count,
            })
        fast_result_shape[class_name] = {
            "constructor": constructors[0],
            "formal_return_dict_count": 0,
            "timed_execute_dict_count": 0,
            "timed_execute_trace_call_count": 0,
        }

    enqueue_helper = module_functions.get("_enqueue_pinned_dynamic_h2d")
    gas_helper = module_functions.get("_build_dynamic_custom_gas_async")
    if enqueue_helper is None or gas_helper is None:
        raise RuntimeError("PyOptiX dynamic-input helper boundary is absent")
    enqueue_paths = [
        _attribute_path(node.func) for node in ast.walk(enqueue_helper)
        if isinstance(node, ast.Call)]
    gas_paths = [
        _attribute_path(node.func) for node in ast.walk(gas_helper)
        if isinstance(node, ast.Call)]
    enqueue_source = ast.get_source_segment(text, enqueue_helper) or ""
    gas_source = ast.get_source_segment(text, gas_helper) or ""
    helper_shape = {
        "device_alloc_call_count": enqueue_paths.count("baseline.cp.cuda.alloc"),
        "async_copy_call_count": enqueue_paths.count("device.copy_from_async"),
        "copy_uses_owned_raw_stream": "raw_stream)" in enqueue_source,
        "upload_count_trace_increment_count": enqueue_source.count(
            'trace["dynamic_device_upload_call_count"] += 1'),
        "upload_bytes_trace_increment_count": enqueue_source.count(
            'trace["dynamic_device_upload_bytes"] += int(host_array.nbytes)'),
        "gas_build_call_count": gas_paths.count("context.accelBuild"),
        "gas_upload_helper_call_count": gas_paths.count(
            "_enqueue_pinned_dynamic_h2d"),
        "gas_trace_increment_count": gas_source.count(
            'trace["dynamic_accel_build_count"] += 1'),
    }
    if helper_shape != {
            "device_alloc_call_count": 1,
            "async_copy_call_count": 1,
            "copy_uses_owned_raw_stream": True,
            "upload_count_trace_increment_count": 1,
            "upload_bytes_trace_increment_count": 1,
            "gas_build_call_count": 1,
            "gas_upload_helper_call_count": 1,
            "gas_trace_increment_count": 1,
            }:
        raise RuntimeError({"dynamic_helper_shape": helper_shape})

    expected_materializers = {
        "DeferredRelationPrepared": {
            "_enqueue_pinned_dynamic_h2d": 1,
            "_build_dynamic_custom_gas_async": 1,
            "self.b.np.copyto": 1,
        },
        "ScalarTrianglePrepared": {
            "_enqueue_pinned_dynamic_h2d": 2,
            "_build_dynamic_custom_gas_async": 0,
            "self.b.np.copyto": 2,
        },
    }

    # The hostile relation K+1 KAT is meaningful only if the threshold and
    # capacity values that enter the two pinned launch-parameter records cannot
    # be shadowed between owner construction and materialization.  Inspect all
    # post-construction methods, rather than only the materializer, so an
    # additive write immediately before ``_materialize_dynamic_input`` cannot
    # evade the source boundary while leaving the expected assignment present.
    critical_owner_roots = {
        "self.fixture", "self.semantic_capacity", "self.raw_capacity",
        "self.params", "self.__dict__",
    }
    forbidden_owner_parameter_writes: list[str] = []

    def rooted_target(target: ast.AST) -> tuple[str | None, int]:
        node = target
        depth = 0
        while isinstance(node, ast.Subscript):
            depth += 1
            node = node.value
        return _attribute_path(node), depth

    for class_node in classes["DeferredRelationPrepared"].body:
        if not isinstance(class_node, ast.FunctionDef) \
                or class_node.name == "__init__":
            continue
        for node in ast.walk(class_node):
            targets: list[ast.AST] = []
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
            elif isinstance(node, ast.AnnAssign):
                targets = [node.target]
            elif isinstance(node, ast.AugAssign):
                targets = [node.target]
            elif isinstance(node, ast.Delete):
                targets = list(node.targets)
            for target in targets:
                root, depth = rooted_target(target)
                if root in critical_owner_roots:
                    forbidden_owner_parameter_writes.append(
                        f"{class_node.name}:{root}:subscript_depth={depth}")
            if isinstance(node, ast.Call):
                path = _attribute_path(node.func)
                if path is not None and any(
                        path.startswith(root + ".")
                        for root in critical_owner_roots):
                    forbidden_owner_parameter_writes.append(
                        f"{class_node.name}:mutating_or_ambiguous_call={path}")
                if isinstance(node.func, ast.Name) \
                        and node.func.id == "setattr" \
                        and len(node.args) >= 2 \
                        and isinstance(node.args[0], ast.Name) \
                        and node.args[0].id == "self" \
                        and isinstance(node.args[1], ast.Constant) \
                        and node.args[1].value in {
                            "fixture", "semantic_capacity", "raw_capacity",
                            "params"}:
                    forbidden_owner_parameter_writes.append(
                        f"{class_node.name}:setattr={node.args[1].value}")
    if forbidden_owner_parameter_writes:
        raise RuntimeError({
            "forbidden_post_init_relation_parameter_writes":
                forbidden_owner_parameter_writes})

    materialization_shape: dict[str, dict[str, object]] = {}
    for class_name, expected in expected_materializers.items():
        materializer = method(class_name, "_materialize_dynamic_input")
        materializer_paths = [
            (_attribute_path(node.func)
             if not isinstance(node.func, ast.Name) else node.func.id)
            for node in ast.walk(materializer) if isinstance(node, ast.Call)]
        observed = {
            key: materializer_paths.count(key) for key in expected}
        forbidden_materializer_calls = sorted(
            path for path in materializer_paths
            if isinstance(path, str) and (
                "copy_from" in path or "accelBuild" in path
                or path.endswith(".alloc")))
        if observed != expected or forbidden_materializer_calls:
            raise RuntimeError({
                "class": class_name,
                "dynamic_materializer_calls": observed,
                "expected": expected,
                "forbidden_direct_calls": forbidden_materializer_calls,
            })
        if class_name == "DeferredRelationPrepared":
            parameter_record_writes = 0
            forbidden_parameter_writes: list[str] = []

            def inspect_target(target: ast.AST) -> None:
                nonlocal parameter_record_writes
                node = target
                depth = 0
                while isinstance(node, ast.Subscript):
                    depth += 1
                    node = node.value
                root = _attribute_path(node)
                if root == "params" and depth == 1:
                    parameter_record_writes += 1
                elif root == "params" or root in {
                        "self.fixture", "self.semantic_capacity",
                        "self.raw_capacity"}:
                    forbidden_parameter_writes.append(
                        f"{root}:subscript_depth={depth}")

            for node in ast.walk(materializer):
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    targets = (node.targets if isinstance(node, ast.Assign)
                               else [node.target])
                    for target in targets:
                        inspect_target(target)
                elif isinstance(node, ast.AugAssign):
                    inspect_target(node.target)
            if parameter_record_writes != 1 or forbidden_parameter_writes:
                raise RuntimeError({
                    "relation_parameter_record_write_count":
                        parameter_record_writes,
                    "forbidden_relation_parameter_writes":
                        forbidden_parameter_writes,
                })
        materialization_shape[class_name] = {
            "calls": observed,
            "forbidden_direct_calls": [],
        }
    fast_source = ast.get_source_segment(text, fast_launchers[0]) or ""
    if "operation_counts" in fast_source or "execution_events" in fast_source \
            or "observe_execution" in fast_source or "event" in fast_source:
        raise RuntimeError("formal PyOptiX launcher contains forensic work")
    fast_methods = {
        node.name: node for node in fast_launchers[0].body
        if isinstance(node, ast.FunctionDef)}
    fast_expected_calls = {
        "zero_on_stream": {"self.b.cp.cuda.runtime.memsetAsync": 1},
        "fill_ff_on_stream": {
            "self.b.cp.cuda.runtime.memsetAsync": 1},
        "enqueue": {
            "self.device_params.copy_from_async": 1,
            "self.b.optix.launch": 1,
        },
        "enqueue_d2h": {"device_array.data.copy_to_host_async": 1},
        "enqueue_compaction": {"kernel": 1},
        "enqueue_d2d": {"self.b.cp.cuda.runtime.memcpyAsync": 1},
        "synchronize": {"self._raw_stream.synchronize": 1},
    }
    fast_shape: dict[str, dict[str, int]] = {}
    for method_name, expected_calls in fast_expected_calls.items():
        method_node = fast_methods.get(method_name)
        if method_node is None:
            raise RuntimeError(f"formal launcher method absent: {method_name}")
        paths = [
            _attribute_path(node.func) for node in ast.walk(method_node)
            if isinstance(node, ast.Call)]
        observed_calls = {
            name: paths.count(name) for name in expected_calls}
        if observed_calls != expected_calls:
            raise RuntimeError({
                "formal_launcher_method": method_name,
                "observed": observed_calls,
                "expected": expected_calls,
            })
        fast_shape[method_name] = observed_calls
    return {
        "schema": "rtdl.goal5802.pyoptix_scalar_execute_boundary.v1",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "method_ast_sha256": hashlib.sha256(ast.dump(
            methods[0], include_attributes=False).encode("utf-8")).hexdigest(),
        "launcher_call_shape": launcher,
        "direct_gpu_call_count": 0,
        "per_ray_host_materialization_count": 0,
        "live_guard_shape": live_guard_shape,
        "relation_canonicalization": canonicalization,
        "execute_boundary_shape": execute_boundary_shape,
        "formal_fast_result_shape": fast_result_shape,
        "dynamic_helper_shape": helper_shape,
        "dynamic_materialization_shape": materialization_shape,
        "optix_validation_mode": "OFF",
        "optix_log_callback_mode": "OFF",
        "module_optimization_level": "DEFAULT",
        "module_debug_level": "NONE",
        "formal_forensic_operation_count": 0,
        "formal_measurement_label_count": 0,
        "relation_raw_capacity_policy": (
            "2_TIMES_SEMANTIC_CAPACITY__RAW_STORAGE_SAFETY_ONLY__"
            "DEVICE_UNIQUE_GATE_REQUIRED"),
        "formal_launcher_call_shape": fast_shape,
    }


class DeferredRelationPrepared:
    """Static relation owner whose batch-side GAS is built by first execute.

    This matches the public RTDL boundary: ``prepare`` owns the indexed/static
    geometry, while the source/query batch is admitted on the first execute and
    then reused without another upload or GAS build.
    """

    def __init__(self, baseline: Any, context: Any, pipeline: Any, sbt: Any,
                 fixture: dict[str, Any], *, pipeline_keepalive: Any,
                 sbt_keepalive: Any, compaction_kernel: Any,
                 raw_capacity: int | None = None,
                 host_inputs: Any | None = None,
                 validate_expected_rows: bool = True,
                 record_operation_evidence: bool = False):
        self.b = baseline
        self.context = context
        self.pipeline = pipeline
        self.sbt = sbt
        self.pipeline_keepalive = pipeline_keepalive
        self.sbt_keepalive = sbt_keepalive
        self.compaction_kernel = compaction_kernel
        self.fixture = fixture
        self.semantic_capacity = int(fixture["capacity"])
        self.raw_capacity = (
            2 * self.semantic_capacity
            if raw_capacity is None else int(raw_capacity))
        if self.semantic_capacity <= 0 \
                or self.raw_capacity != 2 * self.semantic_capacity \
                or self.raw_capacity & (self.raw_capacity - 1):
            raise ValueError(
                "relation capacities must be K>0 and raw/key capacity "
                "must be the power-of-two value 2*K")
        self.record_operation_evidence = bool(record_operation_evidence)
        self.validate_expected_rows = bool(validate_expected_rows)
        self.operation_counts = (
            baseline.new_operation_counts()
            if self.record_operation_evidence else None)
        self.closed = False
        if host_inputs is None:
            self.indexed = baseline.boxes_array(fixture["indexed"])
            self.sources = baseline.boxes_array(fixture["sources"])
            self.goal5809_bulk_input_receipt = None
        else:
            if type(host_inputs) is not RelationBulkHostInputs:
                raise TypeError("relation bulk host input authority differs")
            self.indexed, self.sources = host_inputs.checked_arrays(baseline)
            self.goal5809_bulk_input_receipt = host_inputs.receipt()
        self.d_indexed = baseline.to_device(
            self.indexed, operation_counts=self.operation_counts)
        cp = baseline.cp
        self.d_rows = cp.zeros(self.raw_capacity * 2, dtype=cp.uint32)
        self.d_unique_rows = cp.zeros(
            self.semantic_capacity * 2, dtype=cp.uint32)
        self.d_keys = cp.empty(self.raw_capacity, dtype=cp.uint64)
        self.d_max_key_seen = cp.zeros(1, dtype=cp.uint32)
        self.d_unique_count = cp.zeros(1, dtype=cp.uint32)
        self.d_control = cp.zeros(4, dtype=cp.uint32)
        self.d_count = self.d_control[0:1]
        self.d_overflow = self.d_control[2:3]
        self.d_status = self.d_control[3:4]
        if self.operation_counts is not None:
            self.operation_counts["prepare_device_allocation_call_count"] += 6
        self.launcher = (
            _ObservedCompatiblePreparedLaunch(
                baseline, pipeline, sbt, kind="relation",
                operation_counts=self.operation_counts)
            if self.record_operation_evidence
            else _ComparativePreparedLaunch(baseline, pipeline, sbt))
        self.indexed_handle, self.indexed_gas = baseline.build_custom_gas(
            context, self.indexed, operation_counts=self.operation_counts,
            stream=self.launcher.stream)
        self.h_control = self.launcher.pinned_array(
            (4,), baseline.np.uint32)
        self.h_rows = self.launcher.pinned_array(
            (self.semantic_capacity * 2,), baseline.np.uint32)
        # Allocate capacity during prepare, but do not admit/copy the dynamic
        # source batch until the first execute.  Pinned storage lets that first
        # execute enqueue H2D on the same stream as GAS construction without a
        # hidden blocking MemoryPointer.copy_from call.
        self.h_dynamic_sources = self.launcher.pinned_array(
            self.sources.shape, self.sources.dtype)
        self.h_dynamic_aabbs = self.launcher.pinned_array(
            (len(self.sources), 6), baseline.np.float32)
        self.params = (
            self.launcher.pinned_array((1,), baseline.PARAM_DTYPE),
            self.launcher.pinned_array((1,), baseline.PARAM_DTYPE),
        )
        self.d_sources = None
        self.source_handle = None
        self.source_gas = None
        self.prepared_launches: list[tuple[Any, int]] | None = None
        self.dynamic_input_generation = 0
        self.prepare_operation_counts = (
            dict(self.operation_counts)
            if self.operation_counts is not None else None)
        expected_prepare = exact_counts(
            baseline,
            prepare_device_allocation_call_count=11,
            prepare_h2d_call_count=2,
            prepare_pinned_host_allocation_call_count=6,
            prepare_stream_creation_count=1,
        )
        if self.record_operation_evidence \
                and self.prepare_operation_counts != expected_prepare:
            raise RuntimeError({
                "relation_static_prepare_operation_count_drift":
                    self.prepare_operation_counts,
                "expected": expected_prepare,
            })

    def _materialize_dynamic_input(
            self) -> tuple[bool, dict[str, Any] | None]:
        reused = self.prepared_launches is not None
        if reused:
            trace = (
                _dynamic_trace(
                    reused=True, generation=self.dynamic_input_generation)
                if self.record_operation_evidence else None)
            return True, trace
        trace = (
            _dynamic_trace(
                reused=False, generation=self.dynamic_input_generation)
            if self.record_operation_evidence else None)
        self.b.np.copyto(self.h_dynamic_sources, self.sources)
        self.d_sources = _enqueue_pinned_dynamic_h2d(
            self.b, self.launcher, self.h_dynamic_sources, trace)
        self.source_handle, self.source_gas = _build_dynamic_custom_gas_async(
            self.b, self.context, self.launcher, self.sources,
            self.h_dynamic_aabbs, trace)
        launches: list[tuple[Any, int]] = []
        for reverse, primitive_host, query_host, d_primitive, d_query, handle, params in (
            (0, self.indexed, self.sources, self.d_indexed, self.d_sources,
             self.indexed_handle, self.params[0]),
            (1, self.sources, self.indexed, self.d_sources, self.d_indexed,
             self.source_handle, self.params[1]),
        ):
            params[0] = (
                handle, d_primitive.ptr, d_query.ptr, self.d_rows.data.ptr,
                self.d_count.data.ptr, self.d_overflow.data.ptr,
                len(primitive_host), len(query_host), self.raw_capacity,
                reverse, self.b.np.float32(self.fixture["minimum_overlap"]),
                self.b.np.float32(0.0), self.b.np.float32(1.0),
                self.semantic_capacity,
                0, 0, 0, 0, self.d_status.data.ptr,
            )
            launches.append((params, len(query_host)))
        self.prepared_launches = launches
        self.dynamic_input_generation += 1
        if trace is not None:
            trace["dynamic_input_generation"] = self.dynamic_input_generation
            expected = {
                **_dynamic_trace(reused=False, generation=1),
                "dynamic_device_upload_call_count": 2,
                "dynamic_device_upload_bytes": int(
                    self.h_dynamic_sources.nbytes
                    + self.h_dynamic_aabbs.nbytes),
                "dynamic_accel_build_count": 1,
            }
            if trace != expected:
                raise RuntimeError({
                    "relation_dynamic_materialization_trace": trace,
                    "expected": expected,
                })
        return False, trace

    def execute(self) -> _RelationFastResult:
        if self.record_operation_evidence:
            raise RuntimeError(
                "operation-evidence owner must use the untimed guard entrypoint")
        reused, _ = self._materialize_dynamic_input()
        return self._execute_fast(reused=reused)

    def execute_with_operation_guard(self) -> dict[str, Any]:
        """Untimed preworker KAT; never called by the comparative worker."""
        if not self.record_operation_evidence:
            raise RuntimeError("operation guard is disabled in comparative mode")
        reused, dynamic_receipt = self._materialize_dynamic_input()
        if dynamic_receipt is None:
            raise RuntimeError("relation untimed dynamic trace is absent")
        try:
            with self.launcher.observe_execution() as observer:
                result = self._execute_observed(reused=reused)
        except DeviceStatusFailure as failure:
            failure.evidence["independent_execute_guard"] = observer.receipt
            failure.evidence["dynamic_input_receipt"] = dynamic_receipt
            raise
        result["independent_execute_guard"] = observer.receipt
        result["dynamic_input_receipt"] = dynamic_receipt
        result["live_execute_guard_inside_timer"] = True
        return result

    def _execute_fast(self, *, reused: bool) -> _RelationFastResult:
        """Comparative path with no measurement labels, counters, or lists."""

        if self.closed or self.prepared_launches is None:
            raise RuntimeError("relation dynamic input absent or owner closed")
        b = self.b
        self.launcher.zero_on_stream(
            self.d_control, self.d_max_key_seen, self.d_unique_count)
        self.launcher.fill_ff_on_stream(self.d_keys)
        for params, width in self.prepared_launches:
            self.launcher.enqueue(params, width)
        self.launcher.enqueue_compaction(
            self.compaction_kernel,
            (
                self.d_rows, self.d_unique_rows, self.d_control,
                self.d_keys, self.d_max_key_seen, self.d_unique_count,
                b.np.uint32(self.raw_capacity),
                b.np.uint32(self.semantic_capacity),
                b.np.uint32(self.raw_capacity),
            ),
            element_count=self.raw_capacity,
        )
        self.launcher.enqueue_d2d(
            self.d_control[1:2], self.d_unique_count, 4)
        control_d2h_bytes = int(self.d_control.nbytes)
        self.launcher.enqueue_d2h(
            self.d_control, self.h_control, control_d2h_bytes)
        self.launcher.synchronize()
        raw_count = int(self.h_control[0])
        unique_count = int(self.h_control[1])
        overflow = int(self.h_control[2])
        status = int(self.h_control[3])
        if overflow or status or raw_count > self.raw_capacity \
                or unique_count > self.semantic_capacity:
            raise DeviceStatusFailure(
                "relation device failure: "
                f"raw={raw_count} unique={unique_count} "
                f"overflow={overflow} status={status}",
                {
                    "raw_event_count": raw_count,
                    "semantic_unique_count": unique_count,
                    "device_overflow": overflow,
                    "device_status": status,
                    "raw_capacity": self.raw_capacity,
                    "semantic_capacity": self.semantic_capacity,
                    "application_output_exposed": False,
                    "application_output_d2h_call_count": 0,
                    "status_output_commit_blocking_boundary_count": 1,
                },
            )
        output_d2h_bytes = unique_count * int(b.ROW_DTYPE.itemsize)
        self.launcher.enqueue_d2h(
            self.d_unique_rows, self.h_rows, output_d2h_bytes)
        self.launcher.synchronize()
        raw = self.h_rows[:unique_count * 2].reshape((-1, 2))
        if unique_count:
            order = b.np.lexsort((raw[:, 1], raw[:, 0]))
            ordered = raw[order]
            output = ordered.tolist()
        else:
            output = []
        if len(output) != unique_count:
            raise RuntimeError("relation device compaction count mismatch")
        if self.validate_expected_rows \
                and output != self.fixture["expected_rows"]:
            raise RuntimeError("relation route-independent-oracle mismatch")
        return _RelationFastResult(
            output=output,
            raw_event_count=raw_count,
            semantic_unique_count=unique_count,
            device_status=status,
            device_overflow=overflow,
            prepared_input_reused=reused,
            dynamic_input_generation=self.dynamic_input_generation,
        )

    def _measurement_evidence(
            self, result: _RelationFastResult) -> dict[str, Any]:
        control_d2h_bytes = int(self.d_control.nbytes)
        output_d2h_bytes = (
            result.semantic_unique_count * int(self.b.ROW_DTYPE.itemsize))
        return {
            "output": result.output,
            "raw_event_count": result.raw_event_count,
            "semantic_unique_count": result.semantic_unique_count,
            "device_status": result.device_status,
            "device_overflow": result.device_overflow,
            "optix_launch_count": 2,
            "semantic_compaction_launch_count": 1,
            "semantic_compaction_key_capacity": self.raw_capacity,
            "semantic_compaction_scratch_bytes": int(
                self.d_keys.nbytes + self.d_unique_rows.nbytes
                + self.d_max_key_seen.nbytes + self.d_unique_count.nbytes),
            "callback_status_kernel_launch_count": 0,
            "checked_product_kernel_launch_count": 0,
            "compact_control_finalizer_kernel_launch_count": 0,
            "total_auxiliary_cuda_kernel_launch_count": 1,
            "execution_parameter_h2d_bytes": (
                2 * int(self.b.PARAM_DTYPE.itemsize)),
            "execution_parameter_h2d_copy_call_count": 2,
            "stream_ordered_memset_call_count": 4,
            "status_d2h_copy_call_count": 1,
            "output_d2h_copy_call_count": 1,
            "required_sync_count": 2,
            "control_d2h_bytes": control_d2h_bytes,
            "output_d2h_bytes": output_d2h_bytes,
            "status_output_commit_blocking_boundary_count": 2,
        }

    def _execute_observed(self, *, reused: bool) -> dict[str, Any]:
        b = self.b
        before = dict(self.operation_counts)
        try:
            fast_result = self._execute_fast(reused=reused)
        except DeviceStatusFailure as failure:
            failure.evidence.update({
                "operation_order": list(self.launcher.execution_events),
                "prepare_operation_counts": dict(
                    self.prepare_operation_counts),
                "operation_ledger_scope": OPERATION_LEDGER_SCOPE,
                "execute_operation_counts": b.operation_count_delta(
                    self.operation_counts, before),
            })
            raise
        result = self._measurement_evidence(fast_result)
        if self.record_operation_evidence:
            result.update({
                "operation_order": list(self.launcher.execution_events),
                "prepare_operation_counts": dict(
                    self.prepare_operation_counts),
                "operation_ledger_scope": OPERATION_LEDGER_SCOPE,
                "execute_operation_counts": b.operation_count_delta(
                    self.operation_counts, before),
            })
            require_execution_contract(
                result,
                expected_counts=exact_counts(
                    b,
                    execute_async_h2d_call_count=2,
                    execute_async_d2h_call_count=2,
                    execute_device_zero_fill_call_count=4,
                    execute_explicit_stream_sync_call_count=2,
                    execute_launch_call_count=3,
                ),
                expected_order=[
                    "control_reset", "max_key_reset", "unique_count_reset",
                    "keys_fill_ff",
                    "params0_h2d", "launch0", "params1_h2d", "launch1",
                    "semantic_compaction", "unique_count_d2d",
                    "control_d2h", "status_ready_sync",
                    "unique_rows_d2h", "output_ready_sync",
                ],
            )
        return result

    def close(self) -> None:
        if self.closed:
            return
        self.launcher.close()
        self.closed = True


class ScalarTrianglePrepared:
    """Static triangle owner; query/weight input is first-execute materialized."""

    def __init__(self, baseline: Any, context: Any, pipeline: Any, sbt: Any,
                 task: dict[str, Any], *, pipeline_keepalive: Any,
                 sbt_keepalive: Any,
                 host_inputs: Any | None = None,
                 record_operation_evidence: bool = False):
        self.b = baseline
        self.context = context
        self.pipeline = pipeline
        self.sbt = sbt
        self.pipeline_keepalive = pipeline_keepalive
        self.sbt_keepalive = sbt_keepalive
        self.task = task
        self.record_operation_evidence = bool(record_operation_evidence)
        self.operation_counts = (
            baseline.new_operation_counts()
            if self.record_operation_evidence else None)
        self.closed = False
        b = baseline
        self.launcher = (
            _ObservedCompatiblePreparedLaunch(
                b, pipeline, sbt, kind="triangle",
                operation_counts=self.operation_counts)
            if self.record_operation_evidence
            else _ComparativePreparedLaunch(b, pipeline, sbt))
        if host_inputs is None:
            self.vertices = b.np.asarray(task["vertices"], dtype=b.np.float32)
            queries = task["queries"]
            rays = b.np.zeros(len(queries), dtype=b.RAY_DTYPE)
            for index, (origin, direction, _maximum) in enumerate(queries):
                rays[index] = tuple(
                    b.np.float32(value) for value in (*origin, *direction))
            maxima = {b.np.float32(row[2]).item() for row in queries}
            if len(maxima) != 1:
                raise RuntimeError(
                    "PyOptiX frozen device ABI accepts one common tmax")
            self.rays = rays
            self.weights = b.np.asarray(task["weights"], dtype=b.np.uint64)
            self.maximum = b.np.float32(next(iter(maxima)))
            self.goal5809_bulk_input_receipt = None
        else:
            if type(host_inputs) is not TriangleBulkHostInputs:
                raise TypeError("triangle bulk host input authority differs")
            self.vertices, self.rays, self.weights, self.maximum = \
                host_inputs.checked_arrays(b)
            self.goal5809_bulk_input_receipt = host_inputs.receipt()
        self.handle, self.gas = b.build_triangle_gas(
            context, self.vertices, operation_counts=self.operation_counts,
            stream=self.launcher.stream)
        self.d_rays = None
        self.d_weights = None
        self.d_per_ray = b.cp.zeros(len(self.rays), dtype=b.cp.uint64)
        self.d_weighted = b.cp.zeros(1, dtype=b.cp.uint64)
        self.d_status = b.cp.zeros(1, dtype=b.cp.uint32)
        if self.operation_counts is not None:
            self.operation_counts["prepare_device_allocation_call_count"] += 3
        self.params = self.launcher.pinned_array((1,), b.PARAM_DTYPE)
        self.h_status = self.launcher.pinned_array((1,), b.np.uint32)
        self.h_weighted = self.launcher.pinned_array((1,), b.np.uint64)
        self.h_dynamic_rays = self.launcher.pinned_array(
            self.rays.shape, self.rays.dtype)
        self.h_dynamic_weights = self.launcher.pinned_array(
            self.weights.shape, self.weights.dtype)
        self.dynamic_input_generation = 0
        self.prepare_operation_counts = (
            dict(self.operation_counts)
            if self.operation_counts is not None else None)
        expected_prepare = exact_counts(
            b,
            prepare_device_allocation_call_count=7,
            prepare_h2d_call_count=1,
            prepare_pinned_host_allocation_call_count=5,
            prepare_stream_creation_count=1,
        )
        if self.record_operation_evidence \
                and self.prepare_operation_counts != expected_prepare:
            raise RuntimeError({
                "triangle_scalar_prepare_operation_count_drift":
                    self.prepare_operation_counts,
                "expected": expected_prepare,
            })

    def _materialize_dynamic_input(
            self) -> tuple[bool, dict[str, Any] | None]:
        reused = self.d_rays is not None and self.d_weights is not None
        if reused:
            trace = (
                _dynamic_trace(
                    reused=True, generation=self.dynamic_input_generation)
                if self.record_operation_evidence else None)
            return True, trace
        trace = (
            _dynamic_trace(
                reused=False, generation=self.dynamic_input_generation)
            if self.record_operation_evidence else None)
        self.b.np.copyto(self.h_dynamic_rays, self.rays)
        self.b.np.copyto(self.h_dynamic_weights, self.weights)
        self.d_rays = _enqueue_pinned_dynamic_h2d(
            self.b, self.launcher, self.h_dynamic_rays, trace)
        self.d_weights = _enqueue_pinned_dynamic_h2d(
            self.b, self.launcher, self.h_dynamic_weights, trace)
        self.params[0] = (
            self.handle, 0, 0, 0, 0, 0, 0, len(self.rays), 0, 0,
            self.b.np.float32(0.0),
            self.b.np.float32(self.task.get("tmin", 0.0)),
            self.maximum, 0, self.d_rays.ptr,
            self.d_weights.ptr, self.d_per_ray.data.ptr,
            self.d_weighted.data.ptr, self.d_status.data.ptr,
        )
        self.dynamic_input_generation += 1
        if trace is not None:
            trace["dynamic_input_generation"] = self.dynamic_input_generation
            expected = {
                **_dynamic_trace(reused=False, generation=1),
                "dynamic_device_upload_call_count": 2,
                "dynamic_device_upload_bytes": int(
                    self.rays.nbytes + self.weights.nbytes),
            }
            if trace != expected:
                raise RuntimeError({
                    "triangle_dynamic_materialization_trace": trace,
                    "expected": expected,
                })
        return False, trace

    def execute(self) -> _TriangleFastResult:
        if self.record_operation_evidence:
            raise RuntimeError(
                "operation-evidence owner must use the untimed guard entrypoint")
        reused, _ = self._materialize_dynamic_input()
        return self._execute_fast(reused=reused)

    def execute_with_operation_guard(self) -> dict[str, Any]:
        """Untimed preworker KAT; never called by the comparative worker."""
        if not self.record_operation_evidence:
            raise RuntimeError("operation guard is disabled in comparative mode")
        reused, dynamic_receipt = self._materialize_dynamic_input()
        if dynamic_receipt is None:
            raise RuntimeError("triangle untimed dynamic trace is absent")
        try:
            with self.launcher.observe_execution() as observer:
                result = self._execute_observed(reused=reused)
        except BaseException as error:
            if hasattr(error, "evidence"):
                error.evidence["independent_execute_guard"] = observer.receipt
                error.evidence["dynamic_input_receipt"] = dynamic_receipt
            raise
        result["independent_execute_guard"] = observer.receipt
        result["dynamic_input_receipt"] = dynamic_receipt
        result["live_execute_guard_inside_timer"] = True
        return result

    def _execute_fast(self, *, reused: bool) -> _TriangleFastResult:
        """Comparative path with no measurement labels, counters, or lists."""

        if self.closed:
            raise RuntimeError("triangle scalar prepared owner is closed")
        self.launcher.zero_on_stream(
            self.d_per_ray, self.d_weighted, self.d_status)
        self.launcher.enqueue(self.params, len(self.rays))
        self.launcher.enqueue_d2h(
            self.d_status, self.h_status, int(self.d_status.nbytes))
        self.launcher.synchronize()
        status = int(self.h_status[0])
        if status:
            raise DeviceStatusFailure(
                f"triangle scalar device status failure: {status}",
                {
                    "device_status": status,
                    "application_output_exposed": False,
                    "application_output_d2h_call_count": 0,
                    "status_output_commit_blocking_boundary_count": 1,
                },
            )
        self.launcher.enqueue_d2h(
            self.d_weighted, self.h_weighted, int(self.d_weighted.nbytes))
        self.launcher.synchronize()
        reduced = int(self.h_weighted[0])
        if reduced != self.task["expected_reduced_u64"]:
            raise RuntimeError("triangle scalar route-independent-oracle mismatch")
        return _TriangleFastResult(
            reduced_u64=reduced,
            device_status=status,
            prepared_input_reused=reused,
            dynamic_input_generation=self.dynamic_input_generation,
        )

    def _measurement_evidence(
            self, result: _TriangleFastResult) -> dict[str, Any]:
        return {
            "device_status": result.device_status,
            "reduced_u64": result.reduced_u64,
            "launch_count": 1,
            "required_sync_count": 2,
            "status_d2h_bytes": int(self.d_status.nbytes),
            "scalar_d2h_bytes": int(self.d_weighted.nbytes),
            "total_success_d2h_bytes": (
                int(self.d_status.nbytes) + int(self.d_weighted.nbytes)),
            "compact_status_control_d2h_bytes": int(self.d_status.nbytes),
            "application_output_d2h_bytes": int(self.d_weighted.nbytes),
            "status_output_commit_blocking_boundary_count": 2,
            "per_ray_d2h_bytes": 0,
            "per_ray_host_materialized": False,
            "per_ray_device_intermediate_bytes": int(self.d_per_ray.nbytes),
            "device_reset_bytes": (
                int(self.d_per_ray.nbytes) + int(self.d_weighted.nbytes)
                + int(self.d_status.nbytes)),
            "h2d_launch_parameter_bytes": int(self.params.nbytes),
            "semantic_compaction_launch_count": 0,
            "semantic_compaction_key_capacity": 0,
            "semantic_compaction_scratch_bytes": 0,
            "callback_status_kernel_launch_count": 0,
            "checked_product_kernel_launch_count": 0,
            "compact_control_finalizer_kernel_launch_count": 0,
            "total_auxiliary_cuda_kernel_launch_count": 0,
            "execution_parameter_h2d_bytes": int(self.params.nbytes),
            "execution_parameter_h2d_copy_call_count": 1,
            "stream_ordered_memset_call_count": 3,
            "status_d2h_copy_call_count": 1,
            "output_d2h_copy_call_count": 1,
        }

    def _execute_observed(self, *, reused: bool) -> dict[str, Any]:
        b = self.b
        before = dict(self.operation_counts)
        try:
            fast_result = self._execute_fast(reused=reused)
        except DeviceStatusFailure as failure:
            failure.evidence.update({
                "operation_order": list(self.launcher.execution_events),
                "prepare_operation_counts": dict(
                    self.prepare_operation_counts),
                "operation_ledger_scope": OPERATION_LEDGER_SCOPE,
                "execute_operation_counts": b.operation_count_delta(
                    self.operation_counts, before),
            })
            raise
        result = self._measurement_evidence(fast_result)
        if self.record_operation_evidence:
            result.update({
                "operation_order": list(self.launcher.execution_events),
                "prepare_operation_counts": dict(
                    self.prepare_operation_counts),
                "operation_ledger_scope": OPERATION_LEDGER_SCOPE,
                "execute_operation_counts": b.operation_count_delta(
                    self.operation_counts, before),
            })
            require_execution_contract(
                result,
                expected_counts=exact_counts(
                    b,
                    execute_async_h2d_call_count=1,
                    execute_async_d2h_call_count=2,
                    execute_device_zero_fill_call_count=3,
                    execute_explicit_stream_sync_call_count=2,
                    execute_launch_call_count=1,
                ),
                expected_order=[
                    "per_ray_reset", "scalar_reset", "status_reset",
                    "params_h2d", "launch", "status_d2h",
                    "status_ready_sync", "scalar_d2h", "scalar_ready_sync",
                ],
            )
        return result

    def close(self) -> None:
        if self.closed:
            return
        self.launcher.close()
        self.closed = True


def _create_write_sealed_memfd(data: bytes) -> dict[str, Any]:
    """Create the sole immutable loader object for one retained cubin."""

    if os.name != "posix" or not hasattr(os, "memfd_create"):
        raise RuntimeError("Goal5807 sealed cubin loading requires Linux memfd")
    required = (
        "F_ADD_SEALS", "F_GET_SEALS", "F_SEAL_WRITE", "F_SEAL_GROW",
        "F_SEAL_SHRINK", "F_SEAL_SEAL",
    )
    if _fcntl is None:
        raise RuntimeError("Goal5807 sealed cubin loading requires fcntl")
    missing = [name for name in required if not hasattr(_fcntl, name)]
    if missing:
        raise RuntimeError({"goal5807_missing_memfd_seals": missing})
    flags = int(getattr(os, "MFD_CLOEXEC", 0x0001)) \
        | int(getattr(os, "MFD_ALLOW_SEALING", 0x0002))
    fd = os.memfd_create("goal5807_relation_compaction.cubin", flags)
    try:
        offset = 0
        while offset < len(data):
            written = os.write(fd, data[offset:])
            if written <= 0:
                raise RuntimeError("Goal5807 cubin memfd write made no progress")
            offset += written
        os.fsync(fd)
        readback = bytearray()
        offset = 0
        while offset < len(data):
            chunk = os.pread(fd, min(1024 * 1024, len(data) - offset), offset)
            if not chunk:
                raise RuntimeError("Goal5807 cubin memfd readback ended early")
            readback.extend(chunk)
            offset += len(chunk)
        expected_sha256 = hashlib.sha256(data).hexdigest()
        if bytes(readback) != data \
                or hashlib.sha256(readback).hexdigest() != expected_sha256:
            raise RuntimeError("Goal5807 cubin memfd readback identity differs")
        seal_mask = (
            int(_fcntl.F_SEAL_WRITE) | int(_fcntl.F_SEAL_GROW)
            | int(_fcntl.F_SEAL_SHRINK) | int(_fcntl.F_SEAL_SEAL))
        _fcntl.fcntl(fd, _fcntl.F_ADD_SEALS, seal_mask)
        observed_seals = int(_fcntl.fcntl(fd, _fcntl.F_GET_SEALS))
        if observed_seals & seal_mask != seal_mask:
            raise RuntimeError("Goal5807 cubin memfd is not write sealed")
        stat = os.fstat(fd)
        if stat.st_size != len(data):
            raise RuntimeError("Goal5807 cubin memfd size differs")
        proc_fd_path = f"/proc/self/fd/{fd}"
        proc_stat = os.stat(proc_fd_path)
        if (proc_stat.st_dev, proc_stat.st_ino, proc_stat.st_size) != (
                stat.st_dev, stat.st_ino, stat.st_size):
            raise RuntimeError("Goal5807 proc-fd cubin identity differs")
        return {
            "fd": fd,
            "proc_fd_path": proc_fd_path,
            "bytes": len(data),
            "sha256": expected_sha256,
            "seal_mask": seal_mask,
            "observed_seals": observed_seals,
            "stat_device": int(stat.st_dev),
            "stat_inode": int(stat.st_ino),
            "write_sealed": True,
        }
    except BaseException:
        os.close(fd)
        raise


def _validate_write_sealed_memfd(identity: dict[str, Any]) -> None:
    """Revalidate the held object without reopening the source pathname."""

    fd = identity.get("fd")
    if type(fd) is not int or fd < 0:
        raise RuntimeError("Goal5807 cubin memfd descriptor is invalid")
    stat = os.fstat(fd)
    if _fcntl is None:
        raise RuntimeError("Goal5807 sealed cubin validation requires fcntl")
    seals = int(_fcntl.fcntl(fd, _fcntl.F_GET_SEALS))
    if (stat.st_size, int(stat.st_dev), int(stat.st_ino)) != (
            identity["bytes"], identity["stat_device"], identity["stat_inode"]) \
            or seals & identity["seal_mask"] != identity["seal_mask"]:
        raise RuntimeError("Goal5807 held cubin memfd identity differs")
    proc_stat = os.stat(identity["proc_fd_path"])
    if (proc_stat.st_size, int(proc_stat.st_dev), int(proc_stat.st_ino)) != (
            identity["bytes"], identity["stat_device"], identity["stat_inode"]):
        raise RuntimeError("Goal5807 held cubin proc-fd identity differs")


class PyOptixScalarAdapter:
    """Use a pre-admitted runtime and create one persistent task owner."""

    def __init__(self, task: str, workload: dict[str, Any], *,
                 ptx_path: Path, compaction_cubin_path: Path | None,
                 record_operation_evidence: bool = False,
                 preloaded_runtime: Any | None = None,
                 runtime_preload_receipt: dict[str, Any] | None = None):
        if task not in {RELATION_TASK, TRIANGLE_TASK}:
            raise ValueError(f"unsupported Goal5802 task: {task}")
        self.task = task
        self.workload = workload
        self.ptx_path = ptx_path
        self.compaction_cubin_path = compaction_cubin_path
        if task == RELATION_TASK and compaction_cubin_path is None:
            raise ValueError("relation requires the semantic-compaction cubin")
        if task == TRIANGLE_TASK and compaction_cubin_path is not None:
            raise ValueError("triangle must not receive relation-only cubin")
        self.record_operation_evidence = bool(record_operation_evidence)
        if preloaded_runtime is None:
            preloaded_runtime, runtime_preload_receipt = \
                preload_pyoptix_runtime()
        if runtime_preload_receipt is None:
            raise RuntimeError("PyOptiX runtime preload receipt is absent")
        if preloaded_runtime.__name__ != PYOPTIX_BASELINE_MODULE:
            raise RuntimeError("PyOptiX preloaded runtime module differs")
        self.baseline: Any = preloaded_runtime
        self._runtime_preload_receipt = dict(runtime_preload_receipt)
        self._loaded = False
        self.ptx: bytes | None = None
        self.compaction_cubin: bytes | None = None
        self._compaction_cubin_source_path: str | None = None
        self._compaction_cubin_source_sha256: str | None = None
        self._compaction_cubin_memfd: dict[str, Any] | None = None
        self._compaction_cubin_memfd_closed = False
        self.compaction_module: Any | None = None
        self.compaction_kernel: Any | None = None
        self.context: Any | None = None
        self.logger: Any | None = None
        self.pipeline: Any | None = None
        self.pipeline_keepalive: Any | None = None
        self.sbt: Any | None = None
        self.sbt_keepalive: Any | None = None
        self.owner: Any | None = None
        self._measurement_execute: Any | None = None

    def load(self) -> None:
        if self._loaded:
            raise RuntimeError("PyOptiX adapter load called twice")
        self.ptx = self.ptx_path.read_bytes()
        if not self.ptx or b".version" not in self.ptx[:4096]:
            raise RuntimeError("Goal5802 matched prebuilt PTX is invalid")
        if self.task == RELATION_TASK:
            assert self.compaction_cubin_path is not None
            source = self.compaction_cubin_path.resolve(strict=True)
            self.compaction_cubin = source.read_bytes()
            if not self.compaction_cubin \
                    or self.compaction_cubin[:4] != b"\x7fELF":
                raise RuntimeError("Goal5802 target compaction cubin is invalid")
            self._compaction_cubin_source_path = str(source)
            self._compaction_cubin_source_sha256 = hashlib.sha256(
                self.compaction_cubin).hexdigest()
            self._compaction_cubin_memfd = _create_write_sealed_memfd(
                self.compaction_cubin)
            if self._compaction_cubin_memfd["sha256"] \
                    != self._compaction_cubin_source_sha256:
                raise RuntimeError("Goal5807 sealed cubin digest differs")
        self._loaded = True

    def prepare(self) -> None:
        if not self._loaded or self.ptx is None:
            raise RuntimeError("PyOptiX adapter prepare precedes load")
        if self.owner is not None:
            raise RuntimeError("PyOptiX adapter prepare called twice")
        b = self.baseline
        self.context, self.logger = _make_validation_off_context(b)
        set_cache_enabled = getattr(self.context, "setCacheEnabled", None)
        if not callable(set_cache_enabled):
            raise RuntimeError(
                "PyOptiX context does not expose disk-cache disable control")
        set_cache_enabled(False)
        task_kind = "relation" if self.task == RELATION_TASK else "triangle"
        self.pipeline, self.pipeline_keepalive, _logs = \
            _build_comparative_pipeline(
                b, self.context, self.ptx, task=task_kind)
        self.sbt, self.sbt_keepalive = b.make_sbt(self.pipeline_keepalive)
        if self.task == RELATION_TASK:
            if self.compaction_cubin is None \
                    or self._compaction_cubin_memfd is None:
                raise RuntimeError("relation compaction cubin was not loaded")
            _validate_write_sealed_memfd(self._compaction_cubin_memfd)
            self.compaction_module = b.cp.RawModule(
                path=self._compaction_cubin_memfd["proc_fd_path"])
            self.compaction_kernel = self.compaction_module.get_function(
                "goal5802_relation_unique_compact")
            fixture = {
                "indexed": self.workload["indexed"],
                "sources": self.workload["sources"],
                "minimum_overlap": self.workload["minimum_overlap_f32"],
                "capacity": self.workload["semantic_capacity"],
                "expected_rows": self.workload["expected_rows"],
            }
            self.owner = DeferredRelationPrepared(
                b, self.context, self.pipeline, self.sbt, fixture,
                pipeline_keepalive=self.pipeline_keepalive,
                sbt_keepalive=self.sbt_keepalive,
                compaction_kernel=self.compaction_kernel,
                record_operation_evidence=self.record_operation_evidence,
            )
        else:
            self.owner = ScalarTrianglePrepared(
                b, self.context, self.pipeline, self.sbt, self.workload,
                pipeline_keepalive=self.pipeline_keepalive,
                sbt_keepalive=self.sbt_keepalive,
                record_operation_evidence=self.record_operation_evidence,
            )
        owner = self.owner
        self._measurement_execute = lambda: owner.execute()

    def measurement_execution_callable(self) -> Any:
        """Return the matched zero-argument prepared execution boundary."""

        if self._measurement_execute is None:
            raise RuntimeError("PyOptiX measurement execution precedes prepare")
        return self._measurement_execute

    def execute(self) -> _RelationFastResult | _TriangleFastResult:
        if self._measurement_execute is None:
            raise RuntimeError("PyOptiX adapter execute precedes prepare")
        return self._measurement_execute()

    def measurement_lifecycle_receipt(
            self, raw_result: Any) -> dict[str, Any]:
        if self.owner is None:
            raise RuntimeError("PyOptiX lifecycle receipt precedes prepare")
        expected_type = (
            _RelationFastResult if self.task == RELATION_TASK
            else _TriangleFastResult)
        if not isinstance(raw_result, expected_type):
            raise RuntimeError("PyOptiX compact timed result type differs")
        receipt = _dynamic_trace(
            reused=raw_result.prepared_input_reused,
            generation=raw_result.dynamic_input_generation)
        if not raw_result.prepared_input_reused:
            receipt["dynamic_device_upload_call_count"] = 2
            if self.task == RELATION_TASK:
                receipt["dynamic_device_upload_bytes"] = int(
                    self.owner.h_dynamic_sources.nbytes
                    + self.owner.h_dynamic_aabbs.nbytes)
                receipt["dynamic_accel_build_count"] = 1
            else:
                receipt["dynamic_device_upload_bytes"] = int(
                    self.owner.rays.nbytes + self.owner.weights.nbytes)
        return receipt

    def finalize_measurement_evidence(
            self, raw_result: Any) -> dict[str, Any]:
        """Build measurement-only evidence after the primary clock stops."""

        if self.owner is None:
            raise RuntimeError("PyOptiX evidence finalization precedes prepare")
        if self.task == RELATION_TASK:
            if not isinstance(raw_result, _RelationFastResult):
                raise RuntimeError("PyOptiX relation compact result differs")
            result = self.owner._measurement_evidence(raw_result)
        else:
            if not isinstance(raw_result, _TriangleFastResult):
                raise RuntimeError("PyOptiX triangle compact result differs")
            result = self.owner._measurement_evidence(raw_result)
        result["optix_module_disk_cache_enabled"] = False
        result["optix_validation_mode"] = "OFF"
        result["optix_log_callback_mode"] = "OFF"
        result["module_optimization_level"] = "DEFAULT"
        result["module_debug_level"] = "NONE"
        result["operation_evidence_source"] = (
            "UNTIMED_PREWORKER_KAT_AND_EXACT_SOURCE_BOUNDARY")
        result["live_execute_guard_inside_timer"] = False
        if self.task == RELATION_TASK:
            return {
                **result,
                "compact_status_control_d2h_bytes": int(
                    result["control_d2h_bytes"]),
                "application_output_d2h_bytes": int(
                    result["output_d2h_bytes"]),
                "total_success_d2h_bytes": int(
                    result["control_d2h_bytes"]
                    + result["output_d2h_bytes"]),
                "status_output_commit_blocking_boundary_count": int(
                    result["status_output_commit_blocking_boundary_count"]),
                "per_ray_d2h_bytes": 0,
                "per_ray_host_materialized": False,
            }
        return result

    def execute_with_operation_guard(self) -> dict[str, Any]:
        if self.owner is None:
            raise RuntimeError("PyOptiX adapter guarded execute precedes prepare")
        if not self.record_operation_evidence:
            raise RuntimeError("PyOptiX operation KAT mode was not requested")
        return self.owner.execute_with_operation_guard()

    def close(self) -> None:
        owner_error: BaseException | None = None
        owner = self.owner
        if owner is not None:
            try:
                owner.close()
            except BaseException as error:
                owner_error = error
        if owner is not None and hasattr(owner, "compaction_kernel"):
            owner.compaction_kernel = None
        self.owner = None
        self._measurement_execute = None
        self.compaction_kernel = None
        self.compaction_module = None
        fd_error: BaseException | None = None
        if self._compaction_cubin_memfd is not None \
                and not self._compaction_cubin_memfd_closed:
            try:
                os.close(self._compaction_cubin_memfd["fd"])
                self._compaction_cubin_memfd_closed = True
            except BaseException as error:
                fd_error = error
        if owner_error is not None and fd_error is not None:
            raise RuntimeError({
                "pyoptix_owner_close_error": repr(owner_error),
                "sealed_cubin_fd_close_error": repr(fd_error),
            }) from owner_error
        if owner_error is not None:
            raise owner_error
        if fd_error is not None:
            raise fd_error

    def compaction_cubin_binding_identity(self) -> dict[str, Any] | None:
        """Return immutable Relation cubin binding evidence without reopening it."""

        if self.task != RELATION_TASK:
            return None
        if self._compaction_cubin_memfd is None \
                or self._compaction_cubin_source_path is None \
                or self._compaction_cubin_source_sha256 is None:
            raise RuntimeError("relation compaction identity unavailable")
        _validate_write_sealed_memfd(self._compaction_cubin_memfd)
        identity = {
            key: value for key, value in self._compaction_cubin_memfd.items()
            if key != "fd"
        }
        return {
            "source_path_observed_at_load": self._compaction_cubin_source_path,
            "source_sha256_observed_at_load": (
                self._compaction_cubin_source_sha256),
            "loader_object": identity,
            "prepare_loader_path": self._compaction_cubin_memfd["proc_fd_path"],
            "original_path_reopened_by_prepare": False,
            "closed": self._compaction_cubin_memfd_closed,
        }

    @property
    def compaction_cubin_loader_closed(self) -> bool | None:
        if self.task != RELATION_TASK:
            return None
        return self._compaction_cubin_memfd_closed

    def constructor_runtime_preload_receipt(self) -> dict[str, Any]:
        """Return already-materialized admission evidence outside the clock."""

        return dict(self._runtime_preload_receipt)

    def primary_timer_import_contract(self) -> dict[str, Any]:
        return {
            "required_preloaded_modules": list(
                PYOPTIX_REQUIRED_PRELOADED_MODULES),
            "forbidden_absent_modules": list(
                PRIMARY_TIMER_FORBIDDEN_ABSENT_MODULES),
        }

    def runtime_identity(self) -> dict[str, object]:
        if self.baseline is None:
            raise RuntimeError("PyOptiX runtime identity precedes load")
        initializer = Path(self.baseline.optix.__file__).resolve(strict=True)
        extension_module = __import__("sys").modules.get("optix._optix")
        extension_path = getattr(extension_module, "__file__", None)
        if not extension_path:
            raise RuntimeError("loaded PyOptiX extension identity unavailable")
        extension = Path(extension_path).resolve(strict=True)
        identity = {
            "distribution_version": importlib.metadata.version("pyoptix"),
            "initializer_path": str(initializer),
            "initializer_sha256": hashlib.sha256(
                initializer.read_bytes()).hexdigest(),
            "extension_path": str(extension),
            "extension_sha256": hashlib.sha256(
                extension.read_bytes()).hexdigest(),
            "optix_api_version": ".".join(
                map(str, self.baseline.optix.version())),
            "matched_ptx_path": str(self.ptx_path.resolve(strict=True)),
            "matched_ptx_sha256": hashlib.sha256(
                self.ptx_path.read_bytes()).hexdigest(),
            "retained_matched_ptx_sha256": hashlib.sha256(
                self.ptx).hexdigest(),
        }
        if self.task == RELATION_TASK:
            if self.compaction_cubin is None \
                    or self._compaction_cubin_source_path is None \
                    or self._compaction_cubin_source_sha256 is None:
                raise RuntimeError("relation compaction identity unavailable")
            binding = self.compaction_cubin_binding_identity()
            identity.update({
                "compaction_cubin_path": self._compaction_cubin_source_path,
                "compaction_cubin_sha256": (
                    self._compaction_cubin_source_sha256),
                "retained_compaction_cubin_sha256": hashlib.sha256(
                    self.compaction_cubin).hexdigest(),
                "sealed_compaction_cubin_binding": binding,
            })
        return identity


def plan() -> dict[str, object]:
    return {
        "schema": "rtdl.goal5802.pyoptix_scalar_arm.plan.v1",
        "status": "PASS__LOCAL_SOURCE_PLAN_ONLY__ZERO_TIMINGS",
        "arm": ARM,
        "lineage": LINEAGE,
        "goal5800_v7_arm": GOAL5800_V7_ARM,
        "output": {
            "device_status": "u32",
            "reduced_u64": "u64",
            "per_ray_host_output": False,
        },
        "comparative_load_uses_prebuilt_ptx": True,
        "comparative_load_invokes_nvrtc": False,
        "relation_cubin_loader": (
            "LOAD_ONCE_TO_WRITE_SEALED_MEMFD__RAW_MODULE_USES_PROC_SELF_FD"),
        "relation_cubin_prepare_reopens_original_path": False,
        "runtime_module_preloaded_before_primary_clock": True,
        "adapter_load_imports_runtime_module": False,
        "deployment_cold_estimator_scope": "WARM_PROCESS",
        "source_boundary": validate_scalar_execute_source(),
        "live_monkeypatch_or_forensic_guard_inside_comparative_timer": False,
        "untimed_preworker_operation_guard_kat_required": True,
        "registered_performance_timing_count": 0,
        "formal_execution_authorized": False,
    }


if __name__ == "__main__":
    print(json.dumps(plan(), sort_keys=True))
