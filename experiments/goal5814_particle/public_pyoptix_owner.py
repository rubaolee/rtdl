#!/usr/bin/env python3
"""Real public-PyOptiX owner for Goal5814 Particle strict-interior tracing.

The owner consumes prebuilt PTX and uses only public CuPy and PyOptiX host
interfaces.  It does not import RTDL, call an RTDL native lifecycle ABI, load a
private RTDL library, compile device source, record time, hash data, serialize
JSON, or build forensic diagnostics in the complete-execute boundary.

The parameterized shape is for CPU/mock contract tests.  The only formal
constructor in this module fixes the frozen 314587/3392530/5000 shape.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass, replace
import importlib
from pathlib import Path
import re
import threading
from typing import Any
import weakref

import numpy as np


RAYGEN_ENTRY = "__raygen__rtdl_particle_strict_interior"
CLOSEST_HIT_ENTRY = "__closesthit__rtdl_particle_strict_interior"
MISS_ENTRY = "__miss__rtdl_particle_strict_interior"
FORBIDDEN_ANY_HIT_ENTRY = "__anyhit__rtdl_particle_strict_interior"

UINT32_MAX = np.uint32(0xFFFFFFFF)
CONTROL_DTYPE = np.dtype([
    ("validated_row_count", "u4"),
    ("first_error", "u4"),
    ("error_code", "u4"),
    ("status", "u4"),
], align=True)
PARTICLE_PARAM_DTYPE = np.dtype({
    "names": [
        "traversable",
        "query_ox", "query_oy", "query_oz",
        "query_dx", "query_dy", "query_dz", "query_tmax",
        "front_values", "back_values",
        "primitive_count", "query_count",
        "output_selected", "output_neighbor", "output_face", "control",
    ],
    "formats": [
        "u8",
        "u8", "u8", "u8",
        "u8", "u8", "u8", "u8",
        "u8", "u8",
        "u4", "u4",
        "u8", "u8", "u8", "u8",
    ],
    "align": True,
})
if CONTROL_DTYPE.itemsize != 16 or PARTICLE_PARAM_DTYPE.itemsize != 120:
    raise RuntimeError(
        "Goal5814 Particle public-PyOptiX ABI drift: "
        f"control={CONTROL_DTYPE.itemsize} params={PARTICLE_PARAM_DTYPE.itemsize}")


@dataclass(frozen=True)
class ParticleProblemShape:
    vertex_count: int
    triangle_count: int
    query_count: int

    def __post_init__(self) -> None:
        for name in ("vertex_count", "triangle_count", "query_count"):
            value = getattr(self, name)
            if type(value) is not int or value <= 0 or value > 0xFFFFFFFF:
                raise ValueError(f"Particle {name} is outside nonzero U32")


FORMAL_PARTICLE_SHAPE = ParticleProblemShape(
    vertex_count=314_587,
    triangle_count=3_392_530,
    query_count=5_000,
)


@dataclass(frozen=True)
class PublicPyOptixRuntime:
    """Injectable public runtime namespace used by real and mock owners."""

    cp: Any
    optix: Any

    @classmethod
    def load(cls) -> "PublicPyOptixRuntime":
        """Import the deployed runtime; deliberately do not import NVRTC."""

        return cls(
            cp=importlib.import_module("cupy"),
            optix=importlib.import_module("optix"),
        )


@dataclass
class ParticleExecutionCounters:
    """Source-level operation ledger, split by prepare or one execute call."""

    raw_device_allocation_call_count: int = 0
    raw_device_allocation_bytes: int = 0
    pinned_host_allocation_call_count: int = 0
    pinned_host_allocation_bytes: int = 0
    h2d_copy_call_count: int = 0
    h2d_copy_bytes: int = 0
    query_h2d_copy_call_count: int = 0
    query_h2d_bytes: int = 0
    control_reset_h2d_copy_call_count: int = 0
    control_reset_h2d_bytes: int = 0
    parameter_h2d_copy_call_count: int = 0
    parameter_h2d_bytes: int = 0
    device_memset_call_count: int = 0
    device_memset_bytes: int = 0
    optix_launch_call_count: int = 0
    raygen_invocation_count: int = 0
    explicit_stream_sync_call_count: int = 0
    d2h_copy_call_count: int = 0
    d2h_copy_bytes: int = 0
    control_d2h_copy_call_count: int = 0
    control_d2h_bytes: int = 0
    output_d2h_copy_call_count: int = 0
    output_d2h_bytes: int = 0
    status_before_output: bool = False
    output_d2h_after_status_failure: int = 0
    stream_creation_call_count: int = 0
    context_creation_call_count: int = 0
    module_creation_call_count: int = 0
    program_group_creation_call_count: int = 0
    pipeline_creation_call_count: int = 0
    accel_build_call_count: int = 0

    def frozen_copy(self) -> "ParticleExecutionCounters":
        return replace(self)


@dataclass(frozen=True)
class ParticleExecutionResult:
    """Complete exact result; ``output`` is borrowed until the next execute."""

    output: np.ndarray
    control: tuple[int, int, int, int]
    operation_counts: ParticleExecutionCounters


class PrevalidatedParticleExecutionInput:
    """Read-only formal SoA/oracle admission completed before any clock."""

    __slots__ = (
        "__columns", "__expected", "__query_count", "__pointers",
        "__object_ids", "__sealed", "__weakref__",
    )

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        raise TypeError(
            "PrevalidatedParticleExecutionInput requires public admission")

    @property
    def columns(self) -> tuple[np.ndarray, ...]:
        return self.__columns

    @property
    def expected(self) -> np.ndarray:
        return self.__expected

    @property
    def query_count(self) -> int:
        return self.__query_count

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_PrevalidatedParticleExecutionInput__sealed", False):
            raise AttributeError("prevalidated Particle input is immutable")
        object.__setattr__(self, name, value)


_PREVALIDATED_INPUTS: weakref.WeakSet[PrevalidatedParticleExecutionInput] = \
    weakref.WeakSet()
_PREVALIDATED_INPUT_STORAGE: weakref.WeakKeyDictionary[
    PrevalidatedParticleExecutionInput,
    tuple[tuple[np.ndarray, ...], np.ndarray, tuple[int, ...], tuple[int, ...]],
] = weakref.WeakKeyDictionary()


def _new_prevalidated_input(
        columns: tuple[np.ndarray, ...], expected: np.ndarray,
        ) -> PrevalidatedParticleExecutionInput:
    value = object.__new__(PrevalidatedParticleExecutionInput)
    object.__setattr__(
        value, "_PrevalidatedParticleExecutionInput__columns", columns)
    object.__setattr__(
        value, "_PrevalidatedParticleExecutionInput__expected", expected)
    object.__setattr__(
        value, "_PrevalidatedParticleExecutionInput__query_count",
        int(expected.shape[0]))
    arrays = (*columns, expected)
    object.__setattr__(
        value, "_PrevalidatedParticleExecutionInput__pointers",
        tuple(int(item.ctypes.data) for item in arrays))
    object.__setattr__(
        value, "_PrevalidatedParticleExecutionInput__object_ids",
        tuple(id(item) for item in arrays))
    object.__setattr__(
        value, "_PrevalidatedParticleExecutionInput__sealed", True)
    _PREVALIDATED_INPUTS.add(value)
    _PREVALIDATED_INPUT_STORAGE[value] = (
        columns, expected,
        value._PrevalidatedParticleExecutionInput__pointers,
        value._PrevalidatedParticleExecutionInput__object_ids,
    )
    return value


class ParticleExactCoreCompletion:
    """Opaque owner-created token crossing the exact-core caller boundary."""

    __slots__ = ("__weakref__",)

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        raise TypeError("ParticleExactCoreCompletion is owner-created")


@dataclass(frozen=True)
class _ParticleExactCoreState:
    owner: Any
    generation: int
    output: np.ndarray
    expected: np.ndarray
    control: tuple[int, int, int, int]
    operation_counts: ParticleExecutionCounters
    output_snapshot: tuple[Any, ...]
    expected_snapshot: tuple[Any, ...]
    operation_counts_snapshot: tuple[tuple[str, Any], ...]


_PARTICLE_EXACT_CORE_COMPLETIONS: weakref.WeakKeyDictionary[
    ParticleExactCoreCompletion, _ParticleExactCoreState,
] = weakref.WeakKeyDictionary()


def _array_storage_snapshot(value: np.ndarray) -> tuple[Any, ...]:
    return (
        id(value), int(value.ctypes.data), value.dtype.str,
        tuple(value.shape), tuple(value.strides),
        bool(value.flags.c_contiguous), bool(value.flags.f_contiguous),
        bool(value.flags.writeable), id(value.base),
    )


def _counter_snapshot(
        value: ParticleExecutionCounters) -> tuple[tuple[str, Any], ...]:
    return tuple(
        (name, getattr(value, name))
        for name in ParticleExecutionCounters.__dataclass_fields__)


def _new_particle_exact_core_completion(
        *, owner: Any, generation: int, output: np.ndarray,
        expected: np.ndarray, control: tuple[int, int, int, int],
        operation_counts: ParticleExecutionCounters,
        ) -> ParticleExactCoreCompletion:
    completion = object.__new__(ParticleExactCoreCompletion)
    _PARTICLE_EXACT_CORE_COMPLETIONS[completion] = _ParticleExactCoreState(
        owner=owner,
        generation=generation,
        output=output,
        expected=expected,
        control=control,
        operation_counts=operation_counts,
        output_snapshot=_array_storage_snapshot(output),
        expected_snapshot=_array_storage_snapshot(expected),
        operation_counts_snapshot=_counter_snapshot(operation_counts),
    )
    return completion


class ParticleDeviceStatusError(RuntimeError):
    """Device status failed before any application-output D2H copy."""

    def __init__(
            self,
            control: tuple[int, int, int, int],
            operation_counts: ParticleExecutionCounters,
            ) -> None:
        super().__init__(f"Goal5814 Particle device status failure: {control}")
        self.control = control
        self.operation_counts = operation_counts.frozen_copy()
        self.application_output_exposed = False


class ParticleOracleMismatch(RuntimeError):
    """The completed U32x3 device output differed from the supplied oracle."""

    def __init__(self, operation_counts: ParticleExecutionCounters) -> None:
        super().__init__("Goal5814 Particle exact NumPy oracle mismatch")
        self.operation_counts = operation_counts.frozen_copy()


def _require_exact_array(
        name: str, value: Any, *, dtype: np.dtype, shape: tuple[int, ...],
        ) -> np.ndarray:
    if not isinstance(value, np.ndarray):
        raise TypeError(f"{name} must be a NumPy ndarray")
    if value.dtype != np.dtype(dtype):
        raise TypeError(f"{name} dtype must be exactly {np.dtype(dtype)}")
    if value.shape != shape:
        raise ValueError(f"{name} shape must be exactly {shape}")
    if not value.flags.c_contiguous:
        raise ValueError(f"{name} must be C contiguous")
    return value


def _prevalidate_particle_execution_input(
        query_ox: np.ndarray,
        query_oy: np.ndarray,
        query_oz: np.ndarray,
        query_dx: np.ndarray,
        query_dy: np.ndarray,
        query_dz: np.ndarray,
        query_tmax: np.ndarray,
        expected: np.ndarray,
        *,
        query_count: int,
        ) -> PrevalidatedParticleExecutionInput:
    """Validate and seal one exact-cardinality dynamic input."""
    columns = (
        query_ox, query_oy, query_oz,
        query_dx, query_dy, query_dz, query_tmax,
    )
    names = (
        "query_ox", "query_oy", "query_oz", "query_dx",
        "query_dy", "query_dz", "query_tmax",
    )
    for name, column in zip(names, columns):
        _require_exact_array(
            name, column, dtype=np.float32, shape=(query_count,))
        if column.flags.writeable:
            raise ValueError(
                f"{name} formal admission requires read-only storage")
    _require_exact_array(
        "expected", expected, dtype=np.uint32, shape=(query_count, 3))
    if expected.flags.writeable:
        raise ValueError(
            "expected formal admission requires read-only storage")
    if not all(bool(np.isfinite(column).all()) for column in columns):
        raise ValueError("queries contain a nonfinite value")
    if bool((query_tmax <= np.float32(0.0)).any()):
        raise ValueError("queries contain a nonpositive tmax")
    if bool(((query_dx == np.float32(0.0))
             & (query_dy == np.float32(0.0))
             & (query_dz == np.float32(0.0))).any()):
        raise ValueError("queries contain a zero direction")
    # The admitted views are backed by immutable bytes, not merely by an
    # ndarray whose writeable flag a caller could later re-enable.  B and D
    # therefore consume the same stable bytes for every measured repetition.
    admitted_columns = tuple(
        np.frombuffer(column.tobytes(order="C"), dtype=np.float32)
        for column in columns)
    admitted_expected = np.ndarray(
        shape=(query_count, 3), dtype=np.uint32,
        buffer=expected.tobytes(order="C"), order="C")
    return _new_prevalidated_input(admitted_columns, admitted_expected)


def prevalidate_formal_particle_execution_input(
        query_ox: np.ndarray,
        query_oy: np.ndarray,
        query_oz: np.ndarray,
        query_dx: np.ndarray,
        query_dy: np.ndarray,
        query_dz: np.ndarray,
        query_tmax: np.ndarray,
        expected: np.ndarray,
        ) -> PrevalidatedParticleExecutionInput:
    """Validate immutable formal SoA/oracle bytes once before all clocks."""

    return _prevalidate_particle_execution_input(
        query_ox, query_oy, query_oz,
        query_dx, query_dy, query_dz, query_tmax, expected,
        query_count=FORMAL_PARTICLE_SHAPE.query_count,
    )


def _validate_static_arrays(
        vertices: np.ndarray,
        triangles: np.ndarray,
        front_values: np.ndarray,
        back_values: np.ndarray,
        shape: ParticleProblemShape,
        ) -> None:
    _require_exact_array(
        "vertices", vertices, dtype=np.float32,
        shape=(shape.vertex_count, 3))
    _require_exact_array(
        "triangles", triangles, dtype=np.uint32,
        shape=(shape.triangle_count, 3))
    _require_exact_array(
        "front_values", front_values, dtype=np.uint32,
        shape=(shape.triangle_count,))
    _require_exact_array(
        "back_values", back_values, dtype=np.uint32,
        shape=(shape.triangle_count,))
    if not bool(np.isfinite(vertices).all()):
        raise ValueError("vertices contain a nonfinite value")
    if int(triangles.max()) >= shape.vertex_count:
        raise ValueError("triangles contain an out-of-range vertex index")
    if bool(((triangles[:, 0] == triangles[:, 1])
             | (triangles[:, 0] == triangles[:, 2])
             | (triangles[:, 1] == triangles[:, 2])).any()):
        raise ValueError("triangles contain a repeated vertex index")
    both_boundary = (front_values == UINT32_MAX) & (back_values == UINT32_MAX)
    duplicate_owner = (front_values != UINT32_MAX) \
        & (back_values != UINT32_MAX) & (front_values == back_values)
    if bool((both_boundary | duplicate_owner).any()):
        raise ValueError("front/back face ownership metadata is invalid")


def _validate_prebuilt_ptx(ptx: Any) -> bytes:
    if isinstance(ptx, memoryview):
        ptx = ptx.tobytes()
    elif isinstance(ptx, bytearray):
        ptx = bytes(ptx)
    if not isinstance(ptx, bytes) or not ptx:
        raise TypeError("prebuilt_ptx must be nonempty bytes")
    # OptiX/PyOptiX ultimately consumes PTX as a C string.  Accepting an
    # embedded NUL would let the identity cover bytes that the device-module
    # parser never sees, splitting the frozen artifact from the executable.
    if b"\0" in ptx:
        raise ValueError("prebuilt PTX must not contain an embedded NUL")
    if b".version" not in ptx[:4096]:
        raise ValueError("Goal5814 owner accepts prebuilt PTX, not CUDA source")
    # Match declarations, not comments or string-like substrings.  This
    # specialization's complete executable entry set is exactly three roles.
    declared_entries = {
        name.decode("ascii")
        for name in re.findall(
            rb"(?m)^\s*(?:\.visible\s+)?\.entry\s+"
            rb"([A-Za-z_.$][A-Za-z0-9_.$]*)\s*\(", ptx)
    }
    required_entries = {RAYGEN_ENTRY, CLOSEST_HIT_ENTRY, MISS_ENTRY}
    if declared_entries != required_entries:
        raise ValueError(
            "strict-interior PTX entrypoint set differs: "
            f"expected={sorted(required_entries)}, "
            f"observed={sorted(declared_entries)}")
    return ptx


def _aligned_itemsize(formats: list[str], alignment: int) -> int:
    dtype = np.dtype({
        "names": [f"x{index}" for index in range(len(formats))],
        "formats": formats,
        "align": True,
    })
    remainder = dtype.itemsize % alignment
    return dtype.itemsize if remainder == 0 else dtype.itemsize + alignment - remainder


class PublicPyOptixParticleOwner:
    """Persistent public-PyOptiX Particle geometry and execution owner."""

    def __init__(
            self,
            *,
            runtime: PublicPyOptixRuntime,
            shape: ParticleProblemShape,
            context: Any,
            module: Any,
            pipeline: Any,
            program_groups: tuple[Any, Any, Any],
            sbt: Any,
            sbt_keepalive: Any,
            traversable: int,
            gas_keepalive: Any,
            front_values_device: Any,
            back_values_device: Any,
            query_columns_device: Any,
            output_columns_device: Any,
            control_device: Any,
            params_device: Any,
            stream: Any,
            host_queries: np.ndarray,
            host_output: np.ndarray,
            host_output_rows: np.ndarray,
            host_control: np.ndarray,
            host_params: np.ndarray,
            pinned_keepalive: list[Any],
            prepare_counts: ParticleExecutionCounters,
            ) -> None:
        self.runtime = runtime
        self.shape = shape
        self.context = context
        self.module = module
        self.pipeline = pipeline
        self.program_groups = program_groups
        self.sbt = sbt
        self.sbt_keepalive = sbt_keepalive
        self.traversable = int(traversable)
        self.gas_keepalive = gas_keepalive
        self.front_values_device = front_values_device
        self.back_values_device = back_values_device
        self.query_columns_device = query_columns_device
        self.output_columns_device = output_columns_device
        self.control_device = control_device
        self.params_device = params_device
        self.stream = stream
        self.host_queries = host_queries
        self.host_output = host_output
        self.host_output_rows = host_output_rows
        self.host_control = host_control
        self.host_params = host_params
        self.pinned_keepalive = pinned_keepalive
        self.prepare_operation_counts = prepare_counts.frozen_copy()
        self.last_execute_operation_counts: ParticleExecutionCounters | None = None
        self._execution_lock = threading.Lock()
        self._execution_generation = 0
        self._closed = False

    @classmethod
    def prepare(
            cls,
            *,
            prebuilt_ptx: bytes,
            vertices: np.ndarray,
            triangles: np.ndarray,
            front_values: np.ndarray,
            back_values: np.ndarray,
            shape: ParticleProblemShape = FORMAL_PARTICLE_SHAPE,
            runtime: PublicPyOptixRuntime | None = None,
            ) -> "PublicPyOptixParticleOwner":
        """Prepare one persistent owner using public PyOptiX orchestration."""

        ptx = _validate_prebuilt_ptx(prebuilt_ptx)
        _validate_static_arrays(
            vertices, triangles, front_values, back_values, shape)
        runtime = PublicPyOptixRuntime.load() if runtime is None else runtime
        cp = runtime.cp
        optix = runtime.optix
        counts = ParticleExecutionCounters()

        cp.cuda.runtime.free(0)
        if hasattr(optix, "init"):
            optix.init()
        context_options = optix.DeviceContextOptions()
        validation_off = getattr(optix, "DEVICE_CONTEXT_VALIDATION_MODE_OFF", None)
        if validation_off is None:
            raise RuntimeError("public PyOptiX lacks validation-mode OFF")
        context_options.validationMode = validation_off
        context = optix.deviceContextCreate(0, context_options)
        counts.context_creation_call_count += 1
        set_cache_enabled = getattr(context, "setCacheEnabled", None)
        if not callable(set_cache_enabled):
            raise RuntimeError("public PyOptiX lacks disk-cache control")
        set_cache_enabled(False)

        pipeline_options = cls._pipeline_options(optix)
        module_options = optix.ModuleCompileOptions(
            maxRegisterCount=optix.COMPILE_DEFAULT_MAX_REGISTER_COUNT,
            optLevel=optix.COMPILE_OPTIMIZATION_DEFAULT,
            debugLevel=optix.COMPILE_DEBUG_LEVEL_NONE,
        )
        module, _module_log = context.moduleCreate(
            module_options, pipeline_options, ptx)
        counts.module_creation_call_count += 1
        pipeline, groups = cls._build_pipeline(
            optix, context, module, pipeline_options, counts)
        sbt, sbt_keepalive = cls._make_sbt(runtime, groups, counts)

        stream = cp.cuda.Stream(non_blocking=True)
        counts.stream_creation_call_count += 1
        traversable, gas_keepalive = cls._build_indexed_triangle_gas(
            runtime, context, stream, vertices, triangles, counts)

        front_device = cls._static_to_device(runtime, front_values, counts)
        back_device = cls._static_to_device(runtime, back_values, counts)
        query_bytes = shape.query_count * 7 * np.dtype(np.float32).itemsize
        output_bytes = shape.query_count * 3 * np.dtype(np.uint32).itemsize
        query_device = cls._allocate_device(runtime, query_bytes, counts)
        output_device = cls._allocate_device(runtime, output_bytes, counts)
        control_device = cls._allocate_device(
            runtime, CONTROL_DTYPE.itemsize, counts)
        params_device = cls._allocate_device(
            runtime, PARTICLE_PARAM_DTYPE.itemsize, counts)

        pinned_keepalive: list[Any] = []
        host_queries = cls._pinned_array(
            runtime, (7, shape.query_count), np.float32,
            pinned_keepalive, counts)
        host_output = cls._pinned_array(
            runtime, (3, shape.query_count), np.uint32,
            pinned_keepalive, counts)
        host_output_rows = np.ndarray(
            shape=(shape.query_count, 3), dtype=np.uint32,
            buffer=host_output,
            strides=(np.dtype(np.uint32).itemsize,
                     shape.query_count * np.dtype(np.uint32).itemsize),
        )
        host_output_rows.setflags(write=False)
        host_control = cls._pinned_array(
            runtime, (1,), CONTROL_DTYPE, pinned_keepalive, counts)
        host_params = cls._pinned_array(
            runtime, (1,), PARTICLE_PARAM_DTYPE, pinned_keepalive, counts)

        query_stride = shape.query_count * np.dtype(np.float32).itemsize
        output_stride = shape.query_count * np.dtype(np.uint32).itemsize
        query_base = int(query_device.ptr)
        output_base = int(output_device.ptr)
        params = host_params[0]
        params["traversable"] = np.uint64(traversable)
        for column, name in enumerate((
                "query_ox", "query_oy", "query_oz", "query_dx",
                "query_dy", "query_dz", "query_tmax")):
            params[name] = np.uint64(query_base + column * query_stride)
        params["front_values"] = np.uint64(front_device.ptr)
        params["back_values"] = np.uint64(back_device.ptr)
        params["primitive_count"] = np.uint32(shape.triangle_count)
        params["query_count"] = np.uint32(shape.query_count)
        params["output_selected"] = np.uint64(output_base)
        params["output_neighbor"] = np.uint64(output_base + output_stride)
        params["output_face"] = np.uint64(output_base + 2 * output_stride)
        params["control"] = np.uint64(control_device.ptr)

        # accelBuild and static copies may be asynchronous with respect to the
        # owner stream.  Preparation closes that boundary before returning.
        stream.synchronize()
        counts.explicit_stream_sync_call_count += 1
        return cls(
            runtime=runtime, shape=shape, context=context, module=module,
            pipeline=pipeline, program_groups=groups, sbt=sbt,
            sbt_keepalive=sbt_keepalive, traversable=traversable,
            gas_keepalive=gas_keepalive,
            front_values_device=front_device,
            back_values_device=back_device,
            query_columns_device=query_device,
            output_columns_device=output_device,
            control_device=control_device, params_device=params_device,
            stream=stream, host_queries=host_queries,
            host_output=host_output, host_output_rows=host_output_rows,
            host_control=host_control,
            host_params=host_params, pinned_keepalive=pinned_keepalive,
            prepare_counts=counts,
        )

    @staticmethod
    def _pipeline_options(optix: Any) -> Any:
        kwargs = dict(
            usesMotionBlur=False,
            traversableGraphFlags=int(
                optix.TRAVERSABLE_GRAPH_FLAG_ALLOW_SINGLE_GAS),
            numPayloadValues=2,
            numAttributeValues=2,
            exceptionFlags=int(optix.EXCEPTION_FLAG_NONE),
            pipelineLaunchParamsVariableName="params",
        )
        if optix.version()[1] >= 2:
            kwargs["usesPrimitiveTypeFlags"] = optix.PRIMITIVE_TYPE_FLAGS_TRIANGLE
        return optix.PipelineCompileOptions(**kwargs)

    @classmethod
    def _build_pipeline(
            cls, optix: Any, context: Any, module: Any,
            pipeline_options: Any, counts: ParticleExecutionCounters,
            ) -> tuple[Any, tuple[Any, Any, Any]]:
        raygen = optix.ProgramGroupDesc()
        raygen.raygenModule = module
        raygen.raygenEntryFunctionName = RAYGEN_ENTRY
        raygen_group, _raygen_log = context.programGroupCreate([raygen])
        counts.program_group_creation_call_count += 1

        miss = optix.ProgramGroupDesc()
        miss.missModule = module
        miss.missEntryFunctionName = MISS_ENTRY
        miss_group, _miss_log = context.programGroupCreate([miss])
        counts.program_group_creation_call_count += 1

        hit = optix.ProgramGroupDesc()
        hit.hitgroupModuleCH = module
        hit.hitgroupEntryFunctionNameCH = CLOSEST_HIT_ENTRY
        hit_group, _hit_log = context.programGroupCreate([hit])
        counts.program_group_creation_call_count += 1
        groups = (raygen_group[0], miss_group[0], hit_group[0])

        link_options = optix.PipelineLinkOptions()
        link_options.maxTraceDepth = 1
        pipeline = context.pipelineCreate(
            pipeline_options, link_options, list(groups), "")
        counts.pipeline_creation_call_count += 1
        stack_sizes = optix.StackSizes()
        for group in groups:
            if optix.version()[:2] >= (7, 7):
                optix.util.accumulateStackSizes(group, stack_sizes, pipeline)
            else:
                optix.util.accumulateStackSizes(group, stack_sizes)
        direct_traversal, direct_state, continuation = \
            optix.util.computeStackSizes(stack_sizes, 1, 0, 0)
        pipeline.setStackSize(
            direct_traversal, direct_state, continuation, 1)
        return pipeline, groups

    @classmethod
    def _make_sbt(
            cls, runtime: PublicPyOptixRuntime, groups: tuple[Any, Any, Any],
            counts: ParticleExecutionCounters,
            ) -> tuple[Any, tuple[Any, ...]]:
        optix = runtime.optix
        header_format = f"{optix.SBT_RECORD_HEADER_SIZE}B"
        itemsize = _aligned_itemsize(
            [header_format], optix.SBT_RECORD_ALIGNMENT)
        dtype = np.dtype({
            "names": ["header"], "formats": [header_format],
            "itemsize": itemsize, "align": True,
        })
        host_records: list[np.ndarray] = []
        device_records: list[Any] = []
        for group in groups:
            record = np.zeros(1, dtype=dtype)
            optix.sbtRecordPackHeader(group, record)
            host_records.append(record)
            device_records.append(cls._static_to_device(runtime, record, counts))
        raygen_record, miss_record, hit_record = device_records
        sbt = optix.ShaderBindingTable(
            raygenRecord=int(raygen_record.ptr),
            missRecordBase=int(miss_record.ptr),
            missRecordStrideInBytes=itemsize,
            missRecordCount=1,
            hitgroupRecordBase=int(hit_record.ptr),
            hitgroupRecordStrideInBytes=itemsize,
            hitgroupRecordCount=1,
        )
        return sbt, (tuple(host_records), tuple(device_records))

    @classmethod
    def _build_indexed_triangle_gas(
            cls,
            runtime: PublicPyOptixRuntime,
            context: Any,
            stream: Any,
            vertices: np.ndarray,
            triangles: np.ndarray,
            counts: ParticleExecutionCounters,
            ) -> tuple[int, tuple[Any, ...]]:
        optix = runtime.optix
        device_vertices = cls._static_to_device(runtime, vertices, counts)
        device_triangles = cls._static_to_device(runtime, triangles, counts)
        build_input = optix.BuildInputTriangleArray()
        build_input.vertexFormat = optix.VERTEX_FORMAT_FLOAT3
        build_input.vertexStrideInBytes = 12
        build_input.numVertices = len(vertices)
        build_input.vertexBuffers = [int(device_vertices.ptr)]
        build_input.indexFormat = optix.INDICES_FORMAT_UNSIGNED_INT3
        build_input.indexStrideInBytes = 12
        build_input.numIndexTriplets = len(triangles)
        build_input.indexBuffer = int(device_triangles.ptr)
        build_input.flags = [optix.GEOMETRY_FLAG_DISABLE_ANYHIT]
        build_input.numSbtRecords = 1
        accel_options = optix.AccelBuildOptions(
            buildFlags=int(optix.BUILD_FLAG_PREFER_FAST_TRACE),
            operation=optix.BUILD_OPERATION_BUILD,
        )
        sizes = context.accelComputeMemoryUsage(
            [accel_options], [build_input])
        temporary = cls._allocate_device(
            runtime, int(sizes.tempSizeInBytes), counts)
        output = cls._allocate_device(
            runtime, int(sizes.outputSizeInBytes), counts)
        handle = context.accelBuild(
            int(stream.ptr), [accel_options], [build_input],
            int(temporary.ptr), int(sizes.tempSizeInBytes),
            int(output.ptr), int(sizes.outputSizeInBytes), [])
        counts.accel_build_call_count += 1
        return int(handle), (
            device_vertices, device_triangles, temporary, output, build_input)

    @staticmethod
    def _allocate_device(
            runtime: PublicPyOptixRuntime,
            nbytes: int,
            counts: ParticleExecutionCounters,
            ) -> Any:
        nbytes = int(nbytes)
        if nbytes <= 0:
            raise ValueError("raw device allocation must be nonempty")
        allocation = runtime.cp.cuda.alloc(nbytes)
        counts.raw_device_allocation_call_count += 1
        counts.raw_device_allocation_bytes += nbytes
        return allocation

    @classmethod
    def _static_to_device(
            cls,
            runtime: PublicPyOptixRuntime,
            host_array: np.ndarray,
            counts: ParticleExecutionCounters,
            ) -> Any:
        if not host_array.flags.c_contiguous:
            raise ValueError("static H2D source is not contiguous")
        device = cls._allocate_device(runtime, int(host_array.nbytes), counts)
        device.copy_from(
            ctypes.c_void_p(int(host_array.ctypes.data)), int(host_array.nbytes))
        counts.h2d_copy_call_count += 1
        counts.h2d_copy_bytes += int(host_array.nbytes)
        return device

    @staticmethod
    def _pinned_array(
            runtime: PublicPyOptixRuntime,
            shape: tuple[int, ...],
            dtype: np.dtype,
            keepalive: list[Any],
            counts: ParticleExecutionCounters,
            ) -> np.ndarray:
        dtype = np.dtype(dtype)
        element_count = int(np.prod(shape))
        nbytes = element_count * dtype.itemsize
        pinned = runtime.cp.cuda.alloc_pinned_memory(nbytes)
        array = np.frombuffer(
            pinned, dtype=dtype, count=element_count).reshape(shape)
        array.fill(0)
        keepalive.append((pinned, array))
        counts.pinned_host_allocation_call_count += 1
        counts.pinned_host_allocation_bytes += nbytes
        return array

    @staticmethod
    def _host_pointer(array: np.ndarray) -> int:
        return int(array.ctypes.data)

    def _enqueue_h2d(
            self,
            destination: int,
            source: np.ndarray,
            nbytes: int,
            counts: ParticleExecutionCounters,
            *,
            kind: str,
            ) -> None:
        cuda = self.runtime.cp.cuda.runtime
        cuda.memcpyAsync(
            int(destination), self._host_pointer(source), int(nbytes),
            int(cuda.memcpyHostToDevice), int(self.stream.ptr))
        counts.h2d_copy_call_count += 1
        counts.h2d_copy_bytes += int(nbytes)
        if kind == "query":
            counts.query_h2d_copy_call_count += 1
            counts.query_h2d_bytes += int(nbytes)
        elif kind == "control":
            counts.control_reset_h2d_copy_call_count += 1
            counts.control_reset_h2d_bytes += int(nbytes)
        elif kind == "parameter":
            counts.parameter_h2d_copy_call_count += 1
            counts.parameter_h2d_bytes += int(nbytes)
        else:
            raise AssertionError("unknown H2D operation kind")

    def _enqueue_d2h(
            self,
            destination: np.ndarray,
            source: int,
            nbytes: int,
            counts: ParticleExecutionCounters,
            *,
            output: bool,
            ) -> None:
        cuda = self.runtime.cp.cuda.runtime
        cuda.memcpyAsync(
            self._host_pointer(destination), int(source), int(nbytes),
            int(cuda.memcpyDeviceToHost), int(self.stream.ptr))
        counts.d2h_copy_call_count += 1
        counts.d2h_copy_bytes += int(nbytes)
        if output:
            counts.output_d2h_copy_call_count += 1
            counts.output_d2h_bytes += int(nbytes)
        else:
            counts.control_d2h_copy_call_count += 1
            counts.control_d2h_bytes += int(nbytes)

    def _validate_complete_input(
            self,
            query_ox: np.ndarray,
            query_oy: np.ndarray,
            query_oz: np.ndarray,
            query_dx: np.ndarray,
            query_dy: np.ndarray,
            query_dz: np.ndarray,
            query_tmax: np.ndarray,
            expected: np.ndarray,
            ) -> tuple[tuple[np.ndarray, ...], np.ndarray]:
        query_count = self.shape.query_count
        query_columns = (
            query_ox, query_oy, query_oz, query_dx,
            query_dy, query_dz, query_tmax,
        )
        query_names = (
            "query_ox", "query_oy", "query_oz", "query_dx",
            "query_dy", "query_dz", "query_tmax",
        )
        for name, column in zip(query_names, query_columns):
            _require_exact_array(
                name, column, dtype=np.float32, shape=(query_count,))
        _require_exact_array(
            "expected", expected, dtype=np.uint32,
            shape=(query_count, 3))
        if not all(bool(np.isfinite(column).all())
                   for column in query_columns):
            raise ValueError("queries contain a nonfinite value")
        if bool((query_tmax <= np.float32(0.0)).any()):
            raise ValueError("queries contain a nonpositive tmax")
        if bool(((query_dx == np.float32(0.0))
                 & (query_dy == np.float32(0.0))
                 & (query_dz == np.float32(0.0))).any()):
            raise ValueError("queries contain a zero direction")
        return query_columns, expected

    def _require_prevalidated_input(
            self, value: PrevalidatedParticleExecutionInput,
            ) -> tuple[tuple[np.ndarray, ...], np.ndarray]:
        registered = _PREVALIDATED_INPUT_STORAGE.get(value) \
            if type(value) is PrevalidatedParticleExecutionInput else None
        if type(value) is not PrevalidatedParticleExecutionInput \
                or value not in _PREVALIDATED_INPUTS \
                or registered is None \
                or value.query_count != self.shape.query_count:
            raise TypeError("prevalidated Particle input differs")
        arrays = (*value.columns, value.expected)
        if len(value.columns) != 7 \
                or registered[0] is not value.columns \
                or registered[1] is not value.expected \
                or registered[2] \
                != value._PrevalidatedParticleExecutionInput__pointers \
                or registered[3] \
                != value._PrevalidatedParticleExecutionInput__object_ids \
                or tuple(int(item.ctypes.data) for item in arrays) \
                != value._PrevalidatedParticleExecutionInput__pointers \
                or tuple(id(item) for item in arrays) \
                != value._PrevalidatedParticleExecutionInput__object_ids \
                or any(item.flags.writeable for item in arrays) \
                or any(not item.flags.c_contiguous for item in arrays) \
                or any(not isinstance(item.base, bytes) for item in arrays) \
                or any(item.dtype != np.dtype(np.float32)
                       or item.shape != (value.query_count,)
                       or item.strides != (np.dtype(np.float32).itemsize,)
                       for item in value.columns) \
                or value.expected.dtype != np.dtype(np.uint32) \
                or value.expected.shape != (value.query_count, 3) \
                or value.expected.strides != (
                    3 * np.dtype(np.uint32).itemsize,
                    np.dtype(np.uint32).itemsize):
            raise ValueError("formal prevalidated Particle storage drifted")
        return value.columns, value.expected

    def _execute_exact_core_locked(
            self, query_columns: tuple[np.ndarray, ...],
            expected: np.ndarray) -> ParticleExactCoreCompletion:
        if self._closed:
            raise RuntimeError("Goal5814 Particle owner is closed")
        query_count = self.shape.query_count
        # Every execute attempt ends the lifetime of an earlier borrowed
        # completion, including a later attempt that terminates on status.
        self._execution_generation += 1
        counts = ParticleExecutionCounters()
        query_stride = query_count * np.dtype(np.float32).itemsize
        for column_index, column in enumerate(query_columns):
            np.copyto(self.host_queries[column_index], column, casting="no")
            self._enqueue_h2d(
                int(self.query_columns_device.ptr) + column_index * query_stride,
                self.host_queries[column_index], query_stride, counts,
                kind="query")

        self.host_control[0] = (
            np.uint32(0), UINT32_MAX, np.uint32(0), np.uint32(0))
        self._enqueue_h2d(
            int(self.control_device.ptr), self.host_control,
            CONTROL_DTYPE.itemsize, counts, kind="control")
        self._enqueue_h2d(
            int(self.params_device.ptr), self.host_params,
            PARTICLE_PARAM_DTYPE.itemsize, counts, kind="parameter")
        self.runtime.optix.launch(
            self.pipeline, int(self.stream.ptr),
            int(self.params_device.ptr), PARTICLE_PARAM_DTYPE.itemsize,
            self.sbt, query_count, 1, 1)
        counts.optix_launch_call_count += 1
        counts.raygen_invocation_count += query_count

        self._enqueue_d2h(
            self.host_control, int(self.control_device.ptr),
            CONTROL_DTYPE.itemsize, counts, output=False)
        self.stream.synchronize()
        counts.explicit_stream_sync_call_count += 1
        counts.status_before_output = True
        control = (
            int(self.host_control["validated_row_count"][0]),
            int(self.host_control["first_error"][0]),
            int(self.host_control["error_code"][0]),
            int(self.host_control["status"][0]),
        )
        if control != (query_count, 0xFFFFFFFF, 0, 0):
            self.last_execute_operation_counts = counts.frozen_copy()
            raise ParticleDeviceStatusError(control, counts)

        output_bytes = query_count * 3 * np.dtype(np.uint32).itemsize
        self._enqueue_d2h(
            self.host_output, int(self.output_columns_device.ptr),
            output_bytes, counts, output=True)
        self.stream.synchronize()
        counts.explicit_stream_sync_call_count += 1
        output = self.host_output_rows
        completion = _new_particle_exact_core_completion(
            owner=self, generation=self._execution_generation,
            output=output, expected=expected, control=control,
            operation_counts=counts)
        if np.shares_memory(output, expected):
            self.last_execute_operation_counts = counts.frozen_copy()
            raise ValueError(
                "Goal5814 Particle output and oracle must not share memory")
        if not np.array_equal(output, expected):
            self.last_execute_operation_counts = counts.frozen_copy()
            raise ParticleOracleMismatch(counts)
        return completion

    def _materialize_exact_core_locked(
            self, completion: ParticleExactCoreCompletion,
            ) -> ParticleExecutionResult:
        state = _PARTICLE_EXACT_CORE_COMPLETIONS.get(completion) \
            if type(completion) is ParticleExactCoreCompletion else None
        if state is None \
                or state.owner is not self \
                or state.generation != self._execution_generation \
                or self._closed:
            raise ValueError("Particle exact-core completion is stale or foreign")
        if _array_storage_snapshot(state.output) != state.output_snapshot \
                or _array_storage_snapshot(state.expected) \
                != state.expected_snapshot \
                or _counter_snapshot(state.operation_counts) \
                != state.operation_counts_snapshot \
                or np.shares_memory(state.output, state.expected) \
                or not np.array_equal(state.output, state.expected):
            raise ValueError("Particle exact-core completion mutated after return")
        counts = state.operation_counts.frozen_copy()
        self.last_execute_operation_counts = counts
        return ParticleExecutionResult(
            output=state.output,
            control=state.control,
            operation_counts=counts,
        )

    def execute_exact_core_prevalidated(
            self, value: PrevalidatedParticleExecutionInput,
            ) -> ParticleExactCoreCompletion:
        """Measured core; successful return immediately follows array_equal."""

        with self._execution_lock:
            columns, expected = self._require_prevalidated_input(value)
            return self._execute_exact_core_locked(columns, expected)

    def materialize_exact_core_completion(
            self, completion: ParticleExactCoreCompletion,
            ) -> ParticleExecutionResult:
        """Freeze counters after the caller has recorded its end clock."""

        with self._execution_lock:
            return self._materialize_exact_core_locked(completion)

    def execute_complete_soa(
            self,
            query_ox: np.ndarray,
            query_oy: np.ndarray,
            query_oz: np.ndarray,
            query_dx: np.ndarray,
            query_dy: np.ndarray,
            query_dz: np.ndarray,
            query_tmax: np.ndarray,
            expected: np.ndarray,
            ) -> ParticleExecutionResult:
        """Checked compatibility API for arbitrary caller-owned SoA input."""

        with self._execution_lock:
            columns, oracle = self._validate_complete_input(
                query_ox, query_oy, query_oz, query_dx,
                query_dy, query_dz, query_tmax, expected)
            completion = self._execute_exact_core_locked(columns, oracle)
            return self._materialize_exact_core_locked(completion)

    def execute_complete_matrix_convenience(
            self,
            queries: np.ndarray,
            expected: np.ndarray,
            ) -> ParticleExecutionResult:
        """Nonformal convenience for callers that own an Nx7 matrix.

        This explicit adapter performs seven column materializations and must
        never be used as the formal or measured execution callable.
        """

        query_count = self.shape.query_count
        _require_exact_array(
            "queries", queries, dtype=np.float32,
            shape=(query_count, 7))
        columns = tuple(
            np.ascontiguousarray(queries[:, column]) for column in range(7))
        return self.execute_complete_soa(*columns, expected)

    def close(self) -> None:
        with self._execution_lock:
            if self._closed:
                return
            self._closed = True
            self.stream = None
            self.params_device = None
            self.control_device = None
            self.output_columns_device = None
            self.query_columns_device = None
            self.back_values_device = None
            self.front_values_device = None
            self.gas_keepalive = None
            self.sbt_keepalive = None
            self.sbt = None
            self.program_groups = ()
            self.pipeline = None
            self.module = None
            self.context = None

    def __enter__(self) -> "PublicPyOptixParticleOwner":
        if self._closed:
            raise RuntimeError("Goal5814 Particle owner is closed")
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()


class FormalPublicPyOptixParticleOwner:
    """Formal façade exposing only the seven-column execute contract."""

    __slots__ = ("__owner",)

    def __init__(self, owner: PublicPyOptixParticleOwner) -> None:
        if owner.shape != FORMAL_PARTICLE_SHAPE:
            raise ValueError("formal Particle owner shape is not frozen")
        self.__owner = owner

    @property
    def prepare_operation_counts(self) -> ParticleExecutionCounters:
        return self.__owner.prepare_operation_counts.frozen_copy()

    @property
    def last_execute_operation_counts(
            self) -> ParticleExecutionCounters | None:
        counts = self.__owner.last_execute_operation_counts
        return None if counts is None else counts.frozen_copy()

    def execute_complete(
            self,
            query_ox: np.ndarray,
            query_oy: np.ndarray,
            query_oz: np.ndarray,
            query_dx: np.ndarray,
            query_dy: np.ndarray,
            query_dz: np.ndarray,
            query_tmax: np.ndarray,
            expected: np.ndarray,
            ) -> ParticleExecutionResult:
        return self.__owner.execute_complete_soa(
            query_ox, query_oy, query_oz,
            query_dx, query_dy, query_dz, query_tmax,
            expected,
        )

    def execute_exact_core_prevalidated(
            self, value: PrevalidatedParticleExecutionInput,
            ) -> ParticleExactCoreCompletion:
        """Run the frozen exact core; successful return follows its oracle."""

        if value.query_count != FORMAL_PARTICLE_SHAPE.query_count:
            raise TypeError("formal prevalidated Particle input differs")
        return self.__owner.execute_exact_core_prevalidated(value)

    def materialize_exact_core_completion(
            self, completion: ParticleExactCoreCompletion,
            ) -> ParticleExecutionResult:
        """Freeze public counters after the caller records its end clock."""

        return self.__owner.materialize_exact_core_completion(completion)

    def close(self) -> None:
        self.__owner.close()

    def __enter__(self) -> "FormalPublicPyOptixParticleOwner":
        self.__owner.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()


def prepare_formal_particle_owner(
        *,
        prebuilt_ptx: bytes,
        vertices: np.ndarray,
        triangles: np.ndarray,
        front_values: np.ndarray,
        back_values: np.ndarray,
        runtime: PublicPyOptixRuntime | None = None,
        ) -> FormalPublicPyOptixParticleOwner:
    """The formal-facing wrapper: query cardinality is unconditionally 5000."""

    return FormalPublicPyOptixParticleOwner(
        PublicPyOptixParticleOwner.prepare(
            prebuilt_ptx=prebuilt_ptx,
            vertices=vertices,
            triangles=triangles,
            front_values=front_values,
            back_values=back_values,
            shape=FORMAL_PARTICLE_SHAPE,
            runtime=runtime,
        )
    )


def read_prebuilt_ptx(path: str | Path) -> bytes:
    """Load prebuilt PTX bytes without invoking a compiler or native loader."""

    return _validate_prebuilt_ptx(Path(path).read_bytes())
