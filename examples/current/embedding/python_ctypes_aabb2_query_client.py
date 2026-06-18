#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import os
from pathlib import Path
import sys


RTDL_STATUS_OK = 0
RTDL_BACKEND_CPU = 1
RTDL_DEVICE_HOST = 0
RTDL_DTYPE_F32 = 6
RTDL_DTYPE_U64 = 3
RTDL_PRIMITIVE_AABB2 = 1
RTDL_QUERY_AABB_OVERLAP = 1
RTDL_ABI_VERSION_MAJOR = 0
RTDL_ABI_VERSION_MINOR = 1


class RtdlExternalRuntime(ctypes.Structure):
    _fields_ = [
        ("device_type", ctypes.c_int),
        ("device_id", ctypes.c_int32),
        ("context", ctypes.c_void_p),
        ("stream", ctypes.c_void_p),
        ("user_data", ctypes.c_void_p),
    ]


class RtdlContextDesc(ctypes.Structure):
    _fields_ = [
        ("abi_version_major", ctypes.c_uint32),
        ("abi_version_minor", ctypes.c_uint32),
        ("backend", ctypes.c_int),
        ("external_runtime", RtdlExternalRuntime),
    ]


class RtdlBufferView(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.c_void_p),
        ("byte_count", ctypes.c_uint64),
        ("device_type", ctypes.c_int),
        ("device_id", ctypes.c_int32),
        ("dtype", ctypes.c_int),
        ("ndim", ctypes.c_uint32),
        ("shape", ctypes.c_int64 * 8),
        ("strides", ctypes.c_int64 * 8),
        ("release", ctypes.c_void_p),
        ("user_data", ctypes.c_void_p),
    ]


class RtdlIndexDesc(ctypes.Structure):
    _fields_ = [
        ("abi_version_major", ctypes.c_uint32),
        ("abi_version_minor", ctypes.c_uint32),
        ("primitive_kind", ctypes.c_int),
        ("primitives", ctypes.c_void_p),
        ("primitive_count", ctypes.c_uint64),
    ]


class RtdlQueryDesc(ctypes.Structure):
    _fields_ = [
        ("abi_version_major", ctypes.c_uint32),
        ("abi_version_minor", ctypes.c_uint32),
        ("query_kind", ctypes.c_int),
        ("inputs", ctypes.c_void_p),
        ("input_count", ctypes.c_uint64),
    ]


def _shared_library_name() -> str:
    if os.name == "nt":
        return "rtdl_c_api.dll"
    if sys.platform == "darwin":
        return "librtdl_c_api.dylib"
    return "librtdl_c_api.so"


def _default_library_candidates() -> tuple[Path, ...]:
    here = Path(__file__).resolve()
    return (
        here.parents[1] / "lib" / _shared_library_name(),
        Path("build") / "c_api_stage" / "lib" / _shared_library_name(),
        Path("build") / _shared_library_name(),
    )


def _resolve_library(path_arg: str | None) -> Path:
    if path_arg:
        return Path(path_arg)
    env_path = os.environ.get("RTDL_C_API_LIBRARY")
    if env_path:
        return Path(env_path)
    for candidate in _default_library_candidates():
        if candidate.exists():
            return candidate
    raise FileNotFoundError("pass a C ABI shared library path or set RTDL_C_API_LIBRARY")


def _configure(lib: ctypes.CDLL) -> None:
    lib.rtdl_status_string.argtypes = [ctypes.c_int]
    lib.rtdl_status_string.restype = ctypes.c_char_p
    lib.rtdl_context_last_error.argtypes = [ctypes.c_void_p]
    lib.rtdl_context_last_error.restype = ctypes.c_char_p
    lib.rtdl_context_create.argtypes = [ctypes.POINTER(RtdlContextDesc), ctypes.POINTER(ctypes.c_void_p)]
    lib.rtdl_context_create.restype = ctypes.c_int
    lib.rtdl_context_destroy.argtypes = [ctypes.c_void_p]
    lib.rtdl_context_destroy.restype = None
    lib.rtdl_buffer_import.argtypes = [ctypes.c_void_p, ctypes.POINTER(RtdlBufferView), ctypes.POINTER(ctypes.c_void_p)]
    lib.rtdl_buffer_import.restype = ctypes.c_int
    lib.rtdl_buffer_export.argtypes = [ctypes.c_void_p, ctypes.POINTER(RtdlBufferView)]
    lib.rtdl_buffer_export.restype = ctypes.c_int
    lib.rtdl_buffer_destroy.argtypes = [ctypes.c_void_p]
    lib.rtdl_buffer_destroy.restype = None
    lib.rtdl_index_build.argtypes = [ctypes.c_void_p, ctypes.POINTER(RtdlIndexDesc), ctypes.POINTER(ctypes.c_void_p)]
    lib.rtdl_index_build.restype = ctypes.c_int
    lib.rtdl_index_destroy.argtypes = [ctypes.c_void_p]
    lib.rtdl_index_destroy.restype = None
    lib.rtdl_query_execute.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(RtdlQueryDesc), ctypes.POINTER(ctypes.c_void_p)]
    lib.rtdl_query_execute.restype = ctypes.c_int


def _status_text(lib: ctypes.CDLL, status: int) -> str:
    return lib.rtdl_status_string(status).decode("utf-8")


def _last_error(lib: ctypes.CDLL, context: ctypes.c_void_p) -> str:
    if not context.value:
        return "no context"
    return lib.rtdl_context_last_error(context).decode("utf-8")


def _check(lib: ctypes.CDLL, context: ctypes.c_void_p, status: int, label: str) -> None:
    if status != RTDL_STATUS_OK:
        raise RuntimeError(f"{label} failed: {_status_text(lib, status)}; {_last_error(lib, context)}")


def _host_f32_aabb2_view(array: ctypes.Array, count: int) -> RtdlBufferView:
    view = RtdlBufferView()
    view.data = ctypes.cast(array, ctypes.c_void_p)
    view.byte_count = ctypes.sizeof(array)
    view.device_type = RTDL_DEVICE_HOST
    view.device_id = 0
    view.dtype = RTDL_DTYPE_F32
    view.ndim = 2
    view.shape[0] = count
    view.shape[1] = 4
    view.strides[0] = 4 * ctypes.sizeof(ctypes.c_float)
    view.strides[1] = ctypes.sizeof(ctypes.c_float)
    view.release = None
    view.user_data = None
    return view


def run(library_path: Path) -> str:
    lib = ctypes.CDLL(str(library_path))
    _configure(lib)
    desc = RtdlContextDesc(
        abi_version_major=RTDL_ABI_VERSION_MAJOR,
        abi_version_minor=RTDL_ABI_VERSION_MINOR,
        backend=RTDL_BACKEND_CPU,
        external_runtime=RtdlExternalRuntime(),
    )
    context = ctypes.c_void_p()
    status = int(lib.rtdl_context_create(ctypes.byref(desc), ctypes.byref(context)))
    if status != RTDL_STATUS_OK or not context.value:
        raise RuntimeError(f"context_create failed: {_status_text(lib, status)}")

    primitive_buffer = ctypes.c_void_p()
    query_buffer = ctypes.c_void_p()
    index = ctypes.c_void_p()
    result_buffer = ctypes.c_void_p()
    try:
        primitive_values = (ctypes.c_float * 8)(0.0, 0.0, 1.0, 1.0, 10.0, 10.0, 11.0, 11.0)
        query_values = (ctypes.c_float * 4)(0.25, 0.25, 0.75, 0.75)
        primitive_view = _host_f32_aabb2_view(primitive_values, 2)
        query_view = _host_f32_aabb2_view(query_values, 1)

        status = int(lib.rtdl_buffer_import(context, ctypes.byref(primitive_view), ctypes.byref(primitive_buffer)))
        _check(lib, context, status, "primitive buffer import")
        status = int(lib.rtdl_buffer_import(context, ctypes.byref(query_view), ctypes.byref(query_buffer)))
        _check(lib, context, status, "query buffer import")

        index_desc = RtdlIndexDesc(
            abi_version_major=RTDL_ABI_VERSION_MAJOR,
            abi_version_minor=RTDL_ABI_VERSION_MINOR,
            primitive_kind=RTDL_PRIMITIVE_AABB2,
            primitives=primitive_buffer,
            primitive_count=2,
        )
        status = int(lib.rtdl_index_build(context, ctypes.byref(index_desc), ctypes.byref(index)))
        _check(lib, context, status, "index build")

        query_desc = RtdlQueryDesc(
            abi_version_major=RTDL_ABI_VERSION_MAJOR,
            abi_version_minor=RTDL_ABI_VERSION_MINOR,
            query_kind=RTDL_QUERY_AABB_OVERLAP,
            inputs=query_buffer,
            input_count=1,
        )
        status = int(lib.rtdl_query_execute(context, index, ctypes.byref(query_desc), ctypes.byref(result_buffer)))
        _check(lib, context, status, "query execute")

        result_view = RtdlBufferView()
        status = int(lib.rtdl_buffer_export(result_buffer, ctypes.byref(result_view)))
        _check(lib, context, status, "result buffer export")
        if result_view.dtype != RTDL_DTYPE_U64 or result_view.shape[0] != 1 or result_view.shape[1] != 2:
            raise RuntimeError("unexpected result buffer shape or dtype")
        rows = ctypes.cast(result_view.data, ctypes.POINTER(ctypes.c_uint64))
        if not rows or rows[0] != 0 or rows[1] != 0:
            raise RuntimeError("unexpected first result pair")
        return f"python_ctypes_hit_count={int(result_view.shape[0])} first_pair=({int(rows[0])},{int(rows[1])})"
    finally:
        if result_buffer.value:
            lib.rtdl_buffer_destroy(result_buffer)
        if index.value:
            lib.rtdl_index_destroy(index)
        if query_buffer.value:
            lib.rtdl_buffer_destroy(query_buffer)
        if primitive_buffer.value:
            lib.rtdl_buffer_destroy(primitive_buffer)
        lib.rtdl_context_destroy(context)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("library", nargs="?", help="Path to librtdl_c_api shared library")
    args = parser.parse_args(argv)
    try:
        print(run(_resolve_library(args.library)))
    except Exception as exc:
        print(f"python_ctypes_query_error {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
