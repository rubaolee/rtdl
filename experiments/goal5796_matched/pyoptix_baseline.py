#!/usr/bin/env python3
"""Current NVIDIA PyOptiX matched functional arm for Goal5796.

The host path follows the frozen otk-pyoptix 9.1 examples: Python owns the
OptiX objects and SBT, CUDA/C++ device source is compiled with NVRTC, and no
RTDL module is imported.  This program records no performance timing.
"""

from __future__ import annotations

import ctypes

import cupy as cp
import numpy as np
import optix


PYOPTIX_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
PYOPTIX_STOCK_OPTIX_API_VERSION = (9, 1, 0)


def check_nvrtc(result, program=None):
    # Compiler-only dependency: the deployed/prebuilt-PTX runtime must not
    # import cuda.bindings.nvrtc merely to construct an OptiX context.
    from cuda.bindings import nvrtc
    if result[0].value:
        log = ""
        if program is not None:
            status, size = nvrtc.nvrtcGetProgramLogSize(program)
            if not status.value:
                buffer = b" " * size
                nvrtc.nvrtcGetProgramLog(program, buffer)
                log = buffer.decode(errors="replace")
        raise RuntimeError(
            f"NVRTC {result[0].value}: {nvrtc.nvrtcGetErrorString(result[0])[1]}\n{log}")
    if len(result) == 1:
        return None
    if len(result) == 2:
        return result[1]
    return result[1:]


def compile_ptx(source_path: Path, optix_include: Path, cuda_include: Path) -> bytes:
    # Keep NVRTC outside the runtime-only import graph.  Goal5802 invokes this
    # builder only during untimed preparation or the separate BUILD_COLD
    # diagnostic, never from the comparative load/deploy path.
    from cuda.bindings import nvrtc
    source = source_path.read_bytes()
    program = check_nvrtc(nvrtc.nvrtcCreateProgram(
        source, source_path.name.encode(), 0, [], []))
    options = [
        b"--std=c++17", b"--device-as-default-execution-space", b"--relocatable-device-code=true",
        f"-I{optix_include}".encode(), f"-I{cuda_include}".encode(),
        f"-I{cuda_include / 'nv'}".encode(),
    ]
    check_nvrtc(nvrtc.nvrtcCompileProgram(program, len(options), options), program)
    size = check_nvrtc(nvrtc.nvrtcGetPTXSize(program))
    ptx = b" " * size
    check_nvrtc(nvrtc.nvrtcGetPTX(program, ptx))
    return ptx


def aligned_itemsize(formats, alignment: int) -> int:
    dtype = np.dtype({
        "names": [f"x{i}" for i in range(len(formats))],
        "formats": formats, "align": True,
    })
    size = dtype.itemsize
    return size if size % alignment == 0 else size + alignment - size % alignment


OPERATION_COUNT_KEYS = (
    "prepare_device_allocation_call_count",
    "prepare_h2d_call_count",
    "prepare_pinned_host_allocation_call_count",
    "prepare_stream_creation_count",
    "execute_device_allocation_call_count",
    "execute_pinned_host_allocation_call_count",
    "execute_async_h2d_call_count",
    "execute_async_d2h_call_count",
    "execute_blocking_d2h_call_count",
    "execute_device_zero_fill_call_count",
    "execute_explicit_stream_sync_call_count",
    "execute_launch_call_count",
    "execute_stream_creation_call_count",
    "execute_stream_destroy_call_count",
)


def new_operation_counts() -> dict[str, int]:
    return {key: 0 for key in OPERATION_COUNT_KEYS}


def _bump(operation_counts: dict[str, int] | None, key: str) -> None:
    if operation_counts is not None:
        operation_counts[key] = operation_counts.get(key, 0) + 1


def operation_count_delta(
        after: dict[str, int], before: dict[str, int]) -> dict[str, int]:
    return {
        key: int(after.get(key, 0)) - int(before.get(key, 0))
        for key in OPERATION_COUNT_KEYS
    }


def to_device(
        array: np.ndarray,
        *,
        operation_counts: dict[str, int] | None = None,
):
    memory = cp.cuda.alloc(array.nbytes)
    _bump(operation_counts, "prepare_device_allocation_call_count")
    memory.copy_from(ctypes.c_void_p(array.ctypes.data), array.nbytes)
    _bump(operation_counts, "prepare_h2d_call_count")
    return memory


class Logger:
    def __init__(self):
        self.messages = []

    def __call__(self, level, tag, message):
        self.messages.append({"level": int(level), "tag": str(tag), "message": str(message)})


def make_context():
    cp.cuda.runtime.free(0)
    if hasattr(optix, "init"):
        optix.init()
    logger = Logger()
    options = optix.DeviceContextOptions(
        logCallbackFunction=logger, logCallbackLevel=4)
    if optix.version()[1] >= 2:
        options.validationMode = optix.DEVICE_CONTEXT_VALIDATION_MODE_ALL
    return optix.deviceContextCreate(0, options), logger


def pipeline_options(*, custom: bool):
    kwargs = dict(
        usesMotionBlur=False,
        traversableGraphFlags=int(optix.TRAVERSABLE_GRAPH_FLAG_ALLOW_SINGLE_GAS),
        numPayloadValues=2,
        numAttributeValues=1 if custom else 2,
        exceptionFlags=int(optix.EXCEPTION_FLAG_NONE),
        pipelineLaunchParamsVariableName="params",
    )
    if optix.version()[1] >= 2:
        kwargs["usesPrimitiveTypeFlags"] = (
            optix.PRIMITIVE_TYPE_FLAGS_CUSTOM if custom
            else optix.PRIMITIVE_TYPE_FLAGS_TRIANGLE)
    return optix.PipelineCompileOptions(**kwargs)


def build_pipeline(context, ptx: bytes, *, task: str):
    custom = task == "relation"
    options = pipeline_options(custom=custom)
    module_options = optix.ModuleCompileOptions(
        maxRegisterCount=optix.COMPILE_DEFAULT_MAX_REGISTER_COUNT,
        optLevel=optix.COMPILE_OPTIMIZATION_DEFAULT,
        debugLevel=optix.COMPILE_DEBUG_LEVEL_DEFAULT,
    )
    module, module_log = context.moduleCreate(module_options, options, ptx)

    raygen = optix.ProgramGroupDesc()
    raygen.raygenModule = module
    raygen.raygenEntryFunctionName = (
        "__raygen__goal5796_relation" if custom else "__raygen__goal5796_triangle")
    raygen_group, raygen_log = context.programGroupCreate([raygen])

    miss = optix.ProgramGroupDesc()
    miss.missModule = module
    miss.missEntryFunctionName = (
        "__miss__goal5796_relation" if custom else "__miss__goal5796_triangle")
    miss_group, miss_log = context.programGroupCreate([miss])

    hit = optix.ProgramGroupDesc()
    hit.hitgroupModuleAH = module
    hit.hitgroupEntryFunctionNameAH = (
        "__anyhit__goal5796_relation" if custom else "__anyhit__goal5796_triangle")
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


def make_sbt(groups):
    header = f"{optix.SBT_RECORD_HEADER_SIZE}B"
    size = aligned_itemsize([header], optix.SBT_RECORD_ALIGNMENT)
    dtype = np.dtype({
        "names": ["header"], "formats": [header],
        "itemsize": size, "align": True,
    })
    host_records = []
    device_records = []
    for group in groups:
        record = np.zeros(1, dtype=dtype)
        optix.sbtRecordPackHeader(group, record)
        host_records.append(record)
        device_records.append(to_device(record))
    raygen, miss, hit = device_records
    sbt = optix.ShaderBindingTable(
        raygenRecord=raygen.ptr,
        missRecordBase=miss.ptr,
        missRecordStrideInBytes=size,
        missRecordCount=1,
        hitgroupRecordBase=hit.ptr,
        hitgroupRecordStrideInBytes=size,
        hitgroupRecordCount=1,
    )
    return sbt, (host_records, device_records)


def build_custom_gas(
        context,
        boxes: np.ndarray,
        *,
        operation_counts: dict[str, int] | None = None,
        stream=None,
):
    aabbs = np.zeros((len(boxes), 6), dtype=np.float32)
    aabbs[:, 0:2] = np.stack((boxes["lower_x"], boxes["lower_y"]), axis=1)
    aabbs[:, 2] = np.float32(-0.001)
    aabbs[:, 3:5] = np.stack((boxes["upper_x"], boxes["upper_y"]), axis=1)
    aabbs[:, 5] = np.float32(0.001)
    if stream is None:
        d_aabbs = cp.asarray(aabbs.reshape(-1))
        d_aabbs_ptr = d_aabbs.data.ptr
        _bump(operation_counts, "prepare_device_allocation_call_count")
        _bump(operation_counts, "prepare_h2d_call_count")
    else:
        d_aabbs = to_device(
            aabbs.reshape(-1), operation_counts=operation_counts)
        d_aabbs_ptr = d_aabbs.ptr
    build_input = optix.BuildInputCustomPrimitiveArray(
        aabbBuffers=[d_aabbs_ptr], numPrimitives=len(boxes),
        flags=[optix.GEOMETRY_FLAG_NONE], numSbtRecords=1)
    options = optix.AccelBuildOptions(
        buildFlags=int(optix.BUILD_FLAG_NONE), operation=optix.BUILD_OPERATION_BUILD)
    sizes = context.accelComputeMemoryUsage([options], [build_input])
    temp = cp.cuda.alloc(sizes.tempSizeInBytes)
    output = cp.cuda.alloc(sizes.outputSizeInBytes)
    _bump(operation_counts, "prepare_device_allocation_call_count")
    _bump(operation_counts, "prepare_device_allocation_call_count")
    stream_ptr = 0 if stream is None else stream.ptr
    handle = context.accelBuild(
        stream_ptr, [options], [build_input], temp.ptr, sizes.tempSizeInBytes,
        output.ptr, sizes.outputSizeInBytes, [])
    return handle, (d_aabbs, temp, output)


def build_triangle_gas(
        context,
        vertices: np.ndarray,
        *,
        operation_counts: dict[str, int] | None = None,
        stream=None,
):
    host_vertices = vertices.reshape(-1).astype(np.float32)
    if stream is None:
        device_vertices = cp.asarray(host_vertices)
        device_vertices_ptr = device_vertices.data.ptr
        _bump(operation_counts, "prepare_device_allocation_call_count")
        _bump(operation_counts, "prepare_h2d_call_count")
    else:
        device_vertices = to_device(
            host_vertices, operation_counts=operation_counts)
        device_vertices_ptr = device_vertices.ptr
    build_input = optix.BuildInputTriangleArray()
    build_input.vertexFormat = optix.VERTEX_FORMAT_FLOAT3
    build_input.numVertices = len(vertices)
    build_input.vertexBuffers = [device_vertices_ptr]
    build_input.flags = [optix.GEOMETRY_FLAG_NONE]
    build_input.numSbtRecords = 1
    options = optix.AccelBuildOptions(
        buildFlags=int(optix.BUILD_FLAG_NONE), operation=optix.BUILD_OPERATION_BUILD)
    sizes = context.accelComputeMemoryUsage([options], [build_input])
    temp = cp.cuda.alloc(sizes.tempSizeInBytes)
    output = cp.cuda.alloc(sizes.outputSizeInBytes)
    _bump(operation_counts, "prepare_device_allocation_call_count")
    _bump(operation_counts, "prepare_device_allocation_call_count")
    stream_ptr = 0 if stream is None else stream.ptr
    handle = context.accelBuild(
        stream_ptr, [options], [build_input], temp.ptr, sizes.tempSizeInBytes,
        output.ptr, sizes.outputSizeInBytes, [])
    return handle, (device_vertices, temp, output)


BOX_DTYPE = np.dtype([
    ("lower_x", "f4"), ("lower_y", "f4"), ("lower_z", "f4"),
    ("upper_x", "f4"), ("upper_y", "f4"), ("upper_z", "f4"),
    ("item_id", "u4"),
], align=True)
ROW_DTYPE = np.dtype([("source_id", "u4"), ("item_id", "u4")], align=True)
RAY_DTYPE = np.dtype([
    ("origin_x", "f4"), ("origin_y", "f4"), ("origin_z", "f4"),
    ("direction_x", "f4"), ("direction_y", "f4"), ("direction_z", "f4"),
], align=True)
PARAM_DTYPE = np.dtype({
    "names": [
        "traversable", "boxes", "queries", "rows", "row_count", "overflow",
        "box_count", "query_count", "raw_row_capacity", "reverse_orientation",
        "minimum_overlap", "tmin", "tmax", "reserved0",
        "rays", "weights", "per_ray", "weighted_sum", "status",
    ],
    "formats": [
        "u8", "u8", "u8", "u8", "u8", "u8",
        "u4", "u4", "u4", "u4", "f4", "f4", "f4", "u4",
        "u8", "u8", "u8", "u8", "u8",
    ],
    "align": True,
})
if BOX_DTYPE.itemsize != 28 or ROW_DTYPE.itemsize != 8 \
        or RAY_DTYPE.itemsize != 24 or PARAM_DTYPE.itemsize != 120:
    raise RuntimeError(
        "PyOptiX matched device ABI drift: "
        f"box={BOX_DTYPE.itemsize} row={ROW_DTYPE.itemsize} "
        f"ray={RAY_DTYPE.itemsize} params={PARAM_DTYPE.itemsize}")


class PreparedLaunch:
    """Own one persistent CUDA stream and one persistent launch-param buffer.

    Launch-parameter copies and launches are ordered on ``self.stream``.  A
    caller may enqueue several launches that reuse the parameter buffer: the
    later H2D cannot overwrite it until the earlier launch has completed on
    that same stream.  Host parameter arrays must remain alive until
    :meth:`synchronize`; the Goal5800 owners retain them for their lifetime.
    """

    def __init__(
            self,
            pipeline,
            sbt,
            *,
            operation_counts: dict[str, int],
    ):
        self.pipeline = pipeline
        self.sbt = sbt
        self.operation_counts = operation_counts
        self._raw_stream = cp.cuda.Stream(non_blocking=True)
        self._sync_authority = object()
        self._active_execution_guard = None
        self.stream = _ObservedPreparedStream(self, self._raw_stream)
        _bump(operation_counts, "prepare_stream_creation_count")
        self.device_params = cp.cuda.alloc(PARAM_DTYPE.itemsize)
        _bump(operation_counts, "prepare_device_allocation_call_count")
        self._pinned_keepalive = []
        self._pinned_by_array_id = {}
        self.execution_events: list[str] = []
        self._pending = False
        self._closed = False

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("prepared launch is closed")

    def zero_on_stream(self, *arrays, events: tuple[str, ...]) -> None:
        self._require_open()
        if len(arrays) != len(events):
            raise ValueError("prepared reset arrays/events length mismatch")
        with self.stream:
            for array, event in zip(arrays, events):
                cp.cuda.runtime.memsetAsync(
                    int(array.data.ptr), 0, int(array.nbytes),
                    int(self.stream.ptr),
                )
                _bump(
                    self.operation_counts,
                    "execute_device_zero_fill_call_count",
                )
                self.execution_events.append(event)

    def pinned_array(self, shape, dtype):
        self._require_open()
        dtype = np.dtype(dtype)
        item_count = int(np.prod(shape))
        pinned = cp.cuda.alloc_pinned_memory(item_count * dtype.itemsize)
        _bump(
            self.operation_counts,
            "prepare_pinned_host_allocation_call_count",
        )
        array = np.frombuffer(pinned, dtype=dtype, count=item_count).reshape(shape)
        array.fill(0)
        self._pinned_keepalive.append((pinned, array))
        self._pinned_by_array_id[id(array)] = pinned
        return array

    def begin_execution(self) -> None:
        self._require_open()
        if self._pending:
            raise RuntimeError("prior prepared execution is still pending")
        self.execution_events = []

    def observe_execution(self):
        """Guard the Python-visible execute boundary against hidden host work.

        The guard intercepts CuPy's active device allocator, public pinned-host
        allocation entrypoint, blocking ``cp.asnumpy`` and direct
        synchronization on the owned stream.
        H2D, D2H and OptiX launch calls remain source-observable wrapper events;
        the caller separately validates that execute bodies cannot call those
        APIs directly.  This is intentionally not a CUPTI/driver-wide trace.
        """
        return _PreparedExecutionGuard(self)

    def enqueue(
            self,
            params: np.ndarray,
            width: int,
            *,
            h2d_event: str,
            launch_event: str,
    ) -> None:
        self._require_open()
        if params.shape != (1,) or params.dtype != PARAM_DTYPE \
                or params.nbytes != PARAM_DTYPE.itemsize:
            raise ValueError("prepared launch parameter ABI mismatch")
        if not params.flags.c_contiguous:
            raise ValueError("prepared launch parameters must be contiguous")
        pinned = self._pinned_by_array_id.get(id(params))
        if pinned is None:
            raise ValueError("prepared launch parameters must use owned pinned host memory")
        self.device_params.copy_from_async(
            ctypes.c_void_p(pinned.ptr), params.nbytes, self._raw_stream)
        _bump(self.operation_counts, "execute_async_h2d_call_count")
        self.execution_events.append(h2d_event)
        optix.launch(
            self.pipeline, self.stream.ptr, self.device_params.ptr,
            params.dtype.itemsize, self.sbt, width, 1, 1)
        _bump(self.operation_counts, "execute_launch_call_count")
        self.execution_events.append(launch_event)
        self._pending = True

    def enqueue_d2h(
            self,
            device_array,
            host_array: np.ndarray,
            nbytes: int,
            *,
            event: str,
    ) -> None:
        self._require_open()
        nbytes = int(nbytes)
        if nbytes < 0 or nbytes > int(device_array.nbytes) \
                or nbytes > int(host_array.nbytes):
            raise ValueError("prepared D2H byte count is out of bounds")
        pinned = self._pinned_by_array_id.get(id(host_array))
        if pinned is None:
            raise ValueError("prepared D2H destination must be owned pinned memory")
        device_array.data.copy_to_host_async(
            ctypes.c_void_p(pinned.ptr), nbytes, self._raw_stream)
        _bump(self.operation_counts, "execute_async_d2h_call_count")
        self.execution_events.append(event)
        self._pending = True

    def synchronize(self, *, event: str) -> None:
        self._require_open()
        self.stream.synchronize(authorization=self._sync_authority)
        _bump(
            self.operation_counts,
            "execute_explicit_stream_sync_call_count",
        )
        self.execution_events.append(event)
        self._pending = False

    def close(self) -> None:
        if self._closed:
            return
        if self._pending:
            self.synchronize(event="close_sync")
        self._closed = True
        self.device_params = None
        self.stream = None
        self._pinned_by_array_id = {}
        self._pinned_keepalive = []


class _ObservedPreparedStream:
    """Small stream proxy that distinguishes wrapper and direct sync calls."""

    def __init__(self, owner: PreparedLaunch, stream) -> None:
        self._owner = owner
        self._stream = stream

    @property
    def ptr(self):
        return self._stream.ptr

    def __enter__(self):
        self._stream.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self._stream.__exit__(exc_type, exc_value, traceback)

    def synchronize(self, *, authorization=None):
        guard = self._owner._active_execution_guard
        if guard is not None and authorization is not self._owner._sync_authority:
            guard.unauthorized_direct_stream_sync_count += 1
        return self._stream.synchronize()


class _PreparedExecutionGuard:
    """Observe operations that must be absent outside PreparedLaunch wrappers."""

    def __init__(self, launcher: PreparedLaunch) -> None:
        self.launcher = launcher
        self.unapproved_device_allocation_call_count = 0
        self.unapproved_pinned_host_allocation_call_count = 0
        self.unapproved_blocking_asnumpy_call_count = 0
        self.unauthorized_direct_stream_sync_count = 0
        self._original_allocator = None
        self._original_alloc_pinned_memory = None
        self._original_asnumpy = None
        self.receipt = None

    def __enter__(self):
        if self.launcher._active_execution_guard is not None:
            raise RuntimeError("nested prepared execution guard")
        self.launcher.begin_execution()
        self.launcher._active_execution_guard = self
        self._original_allocator = cp.cuda.get_allocator()
        self._original_alloc_pinned_memory = cp.cuda.alloc_pinned_memory
        self._original_asnumpy = cp.asnumpy

        def observed_allocator(size):
            self.unapproved_device_allocation_call_count += 1
            return self._original_allocator(size)

        def observed_pinned_allocator(size):
            self.unapproved_pinned_host_allocation_call_count += 1
            return self._original_alloc_pinned_memory(size)

        def observed_asnumpy(*args, **kwargs):
            self.unapproved_blocking_asnumpy_call_count += 1
            return self._original_asnumpy(*args, **kwargs)

        cp.cuda.set_allocator(observed_allocator)
        cp.cuda.alloc_pinned_memory = observed_pinned_allocator
        cp.asnumpy = observed_asnumpy
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        cp.asnumpy = self._original_asnumpy
        cp.cuda.alloc_pinned_memory = self._original_alloc_pinned_memory
        cp.cuda.set_allocator(self._original_allocator)
        self.launcher._active_execution_guard = None
        self.receipt = {
            "scope": (
                "PYTHON_VISIBLE_TASK_OWNER_EXECUTE__NOT_CUPTI_OR_DRIVER_WIDE"
            ),
            "unapproved_device_allocation_call_count":
                self.unapproved_device_allocation_call_count,
            "unapproved_pinned_host_allocation_call_count":
                self.unapproved_pinned_host_allocation_call_count,
            "unapproved_blocking_asnumpy_call_count":
                self.unapproved_blocking_asnumpy_call_count,
            "unauthorized_direct_stream_sync_count":
                self.unauthorized_direct_stream_sync_count,
            "complete_driver_operation_observation_claimed": False,
        }
        violations = sum(
            int(value) for key, value in self.receipt.items()
            if key.endswith("_count")
        )
        if exc_type is None and violations:
            raise RuntimeError({
                "unapproved_execute_operation_observed": self.receipt,
            })
        return False


def boxes_array(rows) -> np.ndarray:
    result = np.zeros(len(rows), dtype=BOX_DTYPE)
    for i, row in enumerate(rows):
        result[i] = (
            np.float32(row[0]), np.float32(row[1]), np.float32(0.0),
            np.float32(row[2]), np.float32(row[3]), np.float32(0.0),
            np.uint32(row[4]),
        )
    return result


def launch(pipeline, sbt, params: np.ndarray, width: int):
    device_params = to_device(params)
    stream = cp.cuda.Stream()
    optix.launch(
        pipeline, stream.ptr, device_params.ptr, params.dtype.itemsize,
        sbt, width, 1, 1)
    stream.synchronize()
    return device_params


def run_relation_fixture(context, pipeline, sbt, fixture):
    indexed = boxes_array(fixture["indexed"])
    sources = boxes_array(fixture["sources"])
    # CuPy numeric arrays own the AABBs used by OptiX, but current CuPy does
    # not promise NumPy structured-dtype support.  Preserve the exact C ABI by
    # copying the structured Box bytes into raw device allocations instead.
    d_indexed = to_device(indexed)
    d_sources = to_device(sources)
    raw_capacity = max(1, 2 * len(indexed) * len(sources))
    d_rows = cp.zeros(raw_capacity * 2, dtype=np.uint32)
    d_count = cp.zeros(1, dtype=np.uint32)
    d_overflow = cp.zeros(1, dtype=np.uint32)
    d_status = cp.zeros(1, dtype=np.uint32)
    keepalive = [d_indexed, d_sources, d_rows, d_count, d_overflow, d_status]

    for reverse, primitive_host, query_host, d_primitive, d_query in (
        (0, indexed, sources, d_indexed, d_sources),
        (1, sources, indexed, d_sources, d_indexed),
    ):
        handle, gas_keepalive = build_custom_gas(context, primitive_host)
        keepalive.extend(gas_keepalive)
        params = np.zeros(1, dtype=PARAM_DTYPE)
        params[0] = (
            handle, d_primitive.ptr, d_query.ptr, d_rows.data.ptr,
            d_count.data.ptr, d_overflow.data.ptr,
            len(primitive_host), len(query_host), raw_capacity, reverse,
            np.float32(fixture["minimum_overlap"]), np.float32(0.0), np.float32(1.0), 0,
            0, 0, 0, 0, d_status.data.ptr,
        )
        keepalive.append(launch(pipeline, sbt, params, len(query_host)))

    raw_count = int(cp.asnumpy(d_count)[0])
    overflow = int(cp.asnumpy(d_overflow)[0])
    status = int(cp.asnumpy(d_status)[0])
    if overflow or raw_count > raw_capacity or status:
        raise RuntimeError(
            f"relation device status failure: count={raw_count} overflow={overflow} status={status}")
    raw = cp.asnumpy(d_rows[:raw_count * 2]).reshape((-1, 2))
    rows = sorted({(int(row[0]), int(row[1])) for row in raw})
    if len(rows) > int(fixture["capacity"]):
        raise RuntimeError("relation capacity exceeded; partial rows withheld")
    return [list(row) for row in rows], {
        "raw_event_count": raw_count, "duplicate_count": raw_count - len(rows),
        "device_status": status, "device_overflow": overflow,
    }


def run_triangle(context, pipeline, sbt, task):
    vertices = np.asarray(task["vertices"], dtype=np.float32)
    handle, gas_keepalive = build_triangle_gas(context, vertices)
    rays = np.zeros(len(task["rays"]), dtype=RAY_DTYPE)
    for i, (origin, direction) in enumerate(task["rays"]):
        rays[i] = tuple(np.float32(v) for v in (*origin, *direction))
    weights = np.asarray(task["weights"], dtype=np.uint64)
    d_rays = to_device(rays)
    d_weights = cp.asarray(weights)
    d_per_ray = cp.zeros(len(rays), dtype=np.uint64)
    d_weighted = cp.zeros(1, dtype=np.uint64)
    d_status = cp.zeros(1, dtype=np.uint32)
    params = np.zeros(1, dtype=PARAM_DTYPE)
    params[0] = (
        handle, 0, 0, 0, 0, 0, 0, len(rays), 0, 0,
        np.float32(0.0), np.float32(task["tmin"]), np.float32(task["tmax"]), 0,
        d_rays.ptr, d_weights.data.ptr, d_per_ray.data.ptr,
        d_weighted.data.ptr, d_status.data.ptr,
    )
    device_params = launch(pipeline, sbt, params, len(rays))
    keepalive = [*gas_keepalive, d_rays, d_weights, d_per_ray, d_weighted, d_status, device_params]
    status = int(cp.asnumpy(d_status)[0])
    if status:
        raise RuntimeError(f"triangle device status failure: {status}")
    return [int(v) for v in cp.asnumpy(d_per_ray)], int(cp.asnumpy(d_weighted)[0])


def machine_record():
    # CLI-only provenance dependencies stay outside the deployed runtime graph.
    import platform
    import subprocess

    line = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,driver_version,uuid,compute_cap", "--format=csv,noheader"],
        check=True, text=True, capture_output=True).stdout.strip()
    return {"hostname": platform.node(), "nvidia_smi": line}


def main() -> None:
    # Goal5802 imports the reusable runtime helpers but consumes prebuilt PTX;
    # these functional-CLI dependencies must not enter that deployment graph.
    import argparse
    import hashlib
    import importlib.metadata
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--expected-optix-api-version", default="9.1.0")
    parser.add_argument("--compatibility-authority", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    version = tuple(int(v) for v in optix.version())
    expected_version = tuple(
        int(value) for value in args.expected_optix_api_version.split("."))
    if len(expected_version) != 3 or version != expected_version:
        raise RuntimeError(
            f"expected OptiX API {expected_version}, observed {version}")
    distribution_version = importlib.metadata.version("pyoptix")
    compatibility_authority_sha256 = None
    if expected_version != PYOPTIX_STOCK_OPTIX_API_VERSION:
        if args.compatibility_authority is None or not args.compatibility_authority.is_file():
            raise RuntimeError(
                "non-stock OptiX API requires a compatibility authority")
        compatibility_authority_sha256 = hashlib.sha256(
            args.compatibility_authority.read_bytes()).hexdigest()
    elif args.compatibility_authority is not None:
        raise RuntimeError(
            "stock OptiX API must not carry a compatibility authority")
    spec_bytes = args.spec.read_bytes()
    device_bytes = args.device_source.read_bytes()
    spec = json.loads(spec_bytes)
    ptx = compile_ptx(args.device_source, args.optix_include, args.cuda_include)
    context, logger = make_context()
    relation_pipeline, relation_groups, relation_logs = build_pipeline(
        context, ptx, task="relation")
    triangle_pipeline, triangle_groups, triangle_logs = build_pipeline(
        context, ptx, task="triangle")
    relation_sbt, relation_sbt_keepalive = make_sbt(relation_groups)
    triangle_sbt, triangle_sbt_keepalive = make_sbt(triangle_groups)
    relation_task = spec["tasks"]["CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"]
    relation_outputs = {}
    diagnostics = {}
    for fixture in relation_task["fixtures"]:
        output, diagnostic = run_relation_fixture(
            context, relation_pipeline, relation_sbt, fixture)
        relation_outputs[fixture["id"]] = output
        diagnostics[fixture["id"]] = diagnostic
    overflow_fixture = dict(next(
        row for row in relation_task["fixtures"]
        if row["id"] == relation_task["overflow_witness"]["base_fixture_id"]))
    overflow_fixture["capacity"] = int(relation_task["overflow_witness"]["capacity"])
    try:
        run_relation_fixture(context, relation_pipeline, relation_sbt, overflow_fixture)
    except RuntimeError as error:
        if str(error) != "relation capacity exceeded; partial rows withheld":
            raise
        overflow_probe = {
            "status": "FAIL_CLOSED", "application_result_exposed": False,
            "exception": str(error), "capacity": overflow_fixture["capacity"],
            "expected_unique_row_count": relation_task["overflow_witness"]
                ["expected_unique_row_count"],
        }
    else:
        raise RuntimeError("PyOptiX relation overflow witness was accepted")
    triangle_task = spec["tasks"]["BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1"]
    per_ray, weighted = run_triangle(
        context, triangle_pipeline, triangle_sbt, triangle_task)
    outputs = {
        "bounded_relation": relation_outputs,
        "triangle": {"per_ray": per_ray, "weighted_sum": weighted},
    }
    expected = {
        "bounded_relation": {
            fixture["id"]: fixture["expected_rows"]
            for fixture in relation_task["fixtures"]
        },
        "triangle": {
            "per_ray": triangle_task["expected_per_ray"],
            "weighted_sum": triangle_task["expected_weighted_sum"],
        },
    }
    if outputs != expected:
        raise RuntimeError(f"PyOptiX result mismatch: {outputs!r} != {expected!r}")
    result = {
        "schema": "rtdl.goal5796.pyoptix_matched_functional.v2",
        "status": "PASS",
        "arm": (
            "B_CURRENT_NVIDIA_PYOPTIX"
            if expected_version == PYOPTIX_STOCK_OPTIX_API_VERSION
            else "B_CURRENT_PYOPTIX_SOURCE_OPTIX90_COMPATIBILITY"
        ),
        "pyoptix_repository_commit": PYOPTIX_COMMIT,
        "pyoptix_distribution_version": distribution_version,
        "optix_api_version": ".".join(map(str, version)),
        "stock_current_pyoptix_9_1_claimed": (
            expected_version == PYOPTIX_STOCK_OPTIX_API_VERSION),
        "compatibility_authority_sha256": compatibility_authority_sha256,
        "device_authoring_path": "CUDA_CPP_NVRTC_FROM_PYTHON_HOST",
        "spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
        "device_source_sha256": hashlib.sha256(device_bytes).hexdigest(),
        "ptx_sha256": hashlib.sha256(ptx).hexdigest(),
        "outputs": outputs, "diagnostics": diagnostics,
        "capacity_overflow_witness": overflow_probe,
        "machine": machine_record(),
        "validation_log_message_count": len(logger.messages),
        "pipeline_logs": {"relation": relation_logs, "triangle": triangle_logs},
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(
        result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
