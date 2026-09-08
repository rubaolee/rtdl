"""Small public-PyOptiX runtime helpers for the nine-app comparison.

This module deliberately imports neither RTDL nor CUDA packages at import time.
The experiment owners call :func:`load_runtime` only on a CUDA host.  All
device programs remain application-owned experiment sources.
"""

from __future__ import annotations

import ctypes
import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True, slots=True)
class PublicRuntime:
    cp: Any
    optix: Any


def load_runtime() -> PublicRuntime:
    return PublicRuntime(
        cp=importlib.import_module("cupy"),
        optix=importlib.import_module("optix"),
    )


def _nvrtc_options(
    *,
    optix_include: str | Path,
    cuda_include: str | Path,
    compute_capability: tuple[int, int],
) -> list[bytes]:
    if (
        len(compute_capability) != 2
        or any(type(value) is not int for value in compute_capability)
        or compute_capability[0] <= 0
        or not (0 <= compute_capability[1] <= 9)
    ):
        raise ValueError("NVRTC compute capability must be a major/minor pair")
    cuda = Path(cuda_include).resolve()
    return [
        b"--std=c++17",
        b"--device-as-default-execution-space",
        b"--relocatable-device-code=true",
        (
            f"--gpu-architecture=compute_{compute_capability[0]}{compute_capability[1]}"
        ).encode(),
        f"-I{Path(optix_include).resolve()}".encode(),
        f"-I{cuda}".encode(),
        f"-I{cuda / 'nv'}".encode(),
    ]


def compile_ptx(
    _runtime: PublicRuntime,
    source_path: str | Path,
    *,
    optix_include: str | Path,
    cuda_include: str | Path,
    compute_capability: tuple[int, int],
) -> bytes:
    """Compile one frozen CUDA source through CUDA Python's NVRTC binding."""

    from cuda.bindings import nvrtc

    def checked(result: Any, program: Any = None) -> Any:
        if result[0].value:
            log = ""
            if program is not None:
                status, size = nvrtc.nvrtcGetProgramLogSize(program)
                if not status.value:
                    buffer = b" " * size
                    nvrtc.nvrtcGetProgramLog(program, buffer)
                    log = buffer.decode(errors="replace")
            error = nvrtc.nvrtcGetErrorString(result[0])[1]
            raise RuntimeError(f"NVRTC {result[0].value}: {error}\n{log}")
        if len(result) == 1:
            return None
        return result[1] if len(result) == 2 else result[1:]

    source = Path(source_path).read_bytes()
    source_path = Path(source_path)
    program = checked(
        nvrtc.nvrtcCreateProgram(source, source_path.name.encode(), 0, [], [])
    )
    options = _nvrtc_options(
        optix_include=optix_include,
        cuda_include=cuda_include,
        compute_capability=compute_capability,
    )
    checked(nvrtc.nvrtcCompileProgram(program, len(options), options), program)
    size = checked(nvrtc.nvrtcGetPTXSize(program))
    ptx = b" " * size
    checked(nvrtc.nvrtcGetPTX(program, ptx))
    return _canonicalize_nvrtc_ptx(bytes(ptx))


def _canonicalize_nvrtc_ptx(raw: bytes) -> bytes:
    """Remove NVRTC's required terminator without hiding embedded NULs."""

    if not isinstance(raw, bytes) or not raw.endswith(b"\0"):
        raise RuntimeError("NVRTC PTX lacks its required trailing NUL")
    ptx = raw[:-1]
    if not ptx or b"\0" in ptx or b".version" not in ptx[:4096]:
        raise RuntimeError("NVRTC did not produce canonical PTX")
    return ptx


def make_context(runtime: PublicRuntime) -> Any:
    cp = runtime.cp
    optix = runtime.optix
    cp.cuda.runtime.free(0)
    if hasattr(optix, "init"):
        optix.init()
    options = optix.DeviceContextOptions()
    validation_off = getattr(optix, "DEVICE_CONTEXT_VALIDATION_MODE_OFF", None)
    if validation_off is None:
        raise RuntimeError("public PyOptiX does not expose validation-mode OFF")
    options.validationMode = validation_off
    context = optix.deviceContextCreate(0, options)
    set_cache_enabled = getattr(context, "setCacheEnabled", None)
    if not callable(set_cache_enabled):
        raise RuntimeError(  # noqa: TRY004 - deployed runtime capability failure
            "public PyOptiX does not expose disk-cache control"
        )
    set_cache_enabled(False)
    return context


def pipeline_options(runtime: PublicRuntime, *, custom_primitive: bool) -> Any:
    optix = runtime.optix
    kwargs = {
        "usesMotionBlur": False,
        "traversableGraphFlags": int(optix.TRAVERSABLE_GRAPH_FLAG_ALLOW_SINGLE_GAS),
        "numPayloadValues": 2,
        "numAttributeValues": 2 if not custom_primitive else 0,
        "exceptionFlags": int(optix.EXCEPTION_FLAG_NONE),
        "pipelineLaunchParamsVariableName": "params",
    }
    if tuple(optix.version()[:2]) >= (7, 2):
        kwargs["usesPrimitiveTypeFlags"] = (
            optix.PRIMITIVE_TYPE_FLAGS_CUSTOM
            if custom_primitive
            else optix.PRIMITIVE_TYPE_FLAGS_TRIANGLE
        )
    return optix.PipelineCompileOptions(**kwargs)


def build_pipeline(
    runtime: PublicRuntime,
    context: Any,
    ptx: bytes,
    *,
    raygen_entry: str,
    miss_entry: str,
    any_hit_entry: str | None = None,
    closest_hit_entry: str | None = None,
    intersection_entry: str | None = None,
    custom_primitive: bool,
) -> tuple[Any, tuple[Any, Any, Any], Any, dict[str, str]]:
    """Build one single-GAS pipeline using only public PyOptiX objects."""

    optix = runtime.optix
    options = pipeline_options(runtime, custom_primitive=custom_primitive)
    module_options = optix.ModuleCompileOptions(
        maxRegisterCount=optix.COMPILE_DEFAULT_MAX_REGISTER_COUNT,
        optLevel=optix.COMPILE_OPTIMIZATION_DEFAULT,
        debugLevel=optix.COMPILE_DEBUG_LEVEL_NONE,
    )
    module, module_log = context.moduleCreate(module_options, options, ptx)

    raygen = optix.ProgramGroupDesc()
    raygen.raygenModule = module
    raygen.raygenEntryFunctionName = raygen_entry
    raygen_group, raygen_log = context.programGroupCreate([raygen])

    miss = optix.ProgramGroupDesc()
    miss.missModule = module
    miss.missEntryFunctionName = miss_entry
    miss_group, miss_log = context.programGroupCreate([miss])

    hit = optix.ProgramGroupDesc()
    if any_hit_entry is not None:
        hit.hitgroupModuleAH = module
        hit.hitgroupEntryFunctionNameAH = any_hit_entry
    if closest_hit_entry is not None:
        hit.hitgroupModuleCH = module
        hit.hitgroupEntryFunctionNameCH = closest_hit_entry
    if intersection_entry is not None:
        hit.hitgroupModuleIS = module
        hit.hitgroupEntryFunctionNameIS = intersection_entry
    hit_group, hit_log = context.programGroupCreate([hit])
    groups = (raygen_group[0], miss_group[0], hit_group[0])

    link = optix.PipelineLinkOptions()
    link.maxTraceDepth = 1
    pipeline = context.pipelineCreate(options, link, list(groups), "")
    stack = optix.StackSizes()
    for group in groups:
        if optix.version()[:2] >= (7, 7):
            optix.util.accumulateStackSizes(group, stack, pipeline)
        else:
            optix.util.accumulateStackSizes(group, stack)
    dc_trav, dc_state, continuation = optix.util.computeStackSizes(stack, 1, 0, 0)
    pipeline.setStackSize(dc_trav, dc_state, continuation, 1)
    return (
        pipeline,
        groups,
        module,
        {
            "module": str(module_log),
            "raygen": str(raygen_log),
            "miss": str(miss_log),
            "hitgroup": str(hit_log),
        },
    )


def _aligned_itemsize(formats: list[str], alignment: int) -> int:
    dtype = np.dtype(
        {
            "names": [f"x{index}" for index in range(len(formats))],
            "formats": formats,
            "align": True,
        }
    )
    remainder = dtype.itemsize % alignment
    return dtype.itemsize if remainder == 0 else dtype.itemsize + alignment - remainder


def host_to_raw_device(runtime: PublicRuntime, value: np.ndarray) -> Any:
    if not value.flags.c_contiguous:
        raise ValueError("host-to-device source must be C-contiguous")
    device = runtime.cp.cuda.alloc(int(value.nbytes))
    device.copy_from(ctypes.c_void_p(int(value.ctypes.data)), int(value.nbytes))
    return device


def pinned_array(
    runtime: PublicRuntime, shape: tuple[int, ...], dtype: np.dtype
) -> tuple[np.ndarray, Any]:
    dtype = np.dtype(dtype)
    count = int(np.prod(shape))
    storage = runtime.cp.cuda.alloc_pinned_memory(count * dtype.itemsize)
    value = np.frombuffer(storage, dtype=dtype, count=count).reshape(shape)
    value.fill(0)
    return value, storage


def make_sbt(
    runtime: PublicRuntime, groups: tuple[Any, Any, Any]
) -> tuple[Any, tuple[Any, ...]]:
    optix = runtime.optix
    header = f"{optix.SBT_RECORD_HEADER_SIZE}B"
    size = _aligned_itemsize([header], optix.SBT_RECORD_ALIGNMENT)
    dtype = np.dtype(
        {
            "names": ["header"],
            "formats": [header],
            "itemsize": size,
            "align": True,
        }
    )
    host_records = []
    device_records = []
    for group in groups:
        record = np.zeros(1, dtype=dtype)
        optix.sbtRecordPackHeader(group, record)
        host_records.append(record)
        device_records.append(host_to_raw_device(runtime, record))
    raygen, miss, hit = device_records
    sbt = optix.ShaderBindingTable(
        raygenRecord=int(raygen.ptr),
        missRecordBase=int(miss.ptr),
        missRecordStrideInBytes=size,
        missRecordCount=1,
        hitgroupRecordBase=int(hit.ptr),
        hitgroupRecordStrideInBytes=size,
        hitgroupRecordCount=1,
    )
    return sbt, (tuple(host_records), tuple(device_records))


def copy_params_and_launch(
    runtime: PublicRuntime,
    *,
    pipeline: Any,
    sbt: Any,
    stream: Any,
    params: np.ndarray,
    device_params: Any,
    width: int,
) -> None:
    if params.shape != (1,) or not params.flags.c_contiguous:
        raise ValueError("launch parameters must be one contiguous record")
    device_params.copy_from_async(
        ctypes.c_void_p(int(params.ctypes.data)),
        int(params.nbytes),
        stream,
    )
    runtime.optix.launch(
        pipeline,
        int(stream.ptr),
        int(device_params.ptr),
        int(params.nbytes),
        sbt,
        int(width),
        1,
        1,
    )


__all__ = [
    "PublicRuntime",
    "build_pipeline",
    "compile_ptx",
    "copy_params_and_launch",
    "host_to_raw_device",
    "load_runtime",
    "make_context",
    "make_sbt",
    "pinned_array",
    "pipeline_options",
]
