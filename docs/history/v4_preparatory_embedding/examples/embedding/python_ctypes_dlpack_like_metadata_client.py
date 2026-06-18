#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import math
import os
from pathlib import Path
import sys


RTDL_STATUS_OK = 0
RTDL_STATUS_ERROR_INVALID_ARGUMENT = 1
RTDL_BACKEND_CPU = 1
RTDL_DEVICE_HOST = 0
RTDL_DEVICE_CUDA = 1
RTDL_DTYPE_F32 = 6
RTDL_PRIMITIVE_AABB2 = 1
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


class FakeDLPackLikeArray:
    dtype = "float32"
    shape = (2, 3)
    strides = None

    def __dlpack__(self) -> object:
        return object()

    def __dlpack_device__(self) -> tuple[int, int]:
        return (2, 0)

    def data_ptr(self) -> int:
        return 0x2000


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


def _status_text(lib: ctypes.CDLL, status: int) -> str:
    return lib.rtdl_status_string(status).decode("utf-8")


def _dtype_and_itemsize(dtype: str) -> tuple[int, int]:
    if dtype in ("float32", "f4"):
        return RTDL_DTYPE_F32, 4
    raise ValueError(f"unsupported fake DLPack-like dtype {dtype!r}")


def _device_type(device: tuple[int, int]) -> tuple[int, int]:
    raw_type, device_id = device
    if int(raw_type) == 1:
        return RTDL_DEVICE_HOST, int(device_id)
    if int(raw_type) == 2:
        return RTDL_DEVICE_CUDA, int(device_id)
    raise ValueError(f"unsupported fake DLPack-like device {device!r}")


def _contiguous_strides(shape: tuple[int, ...], itemsize: int) -> tuple[int, ...]:
    strides = []
    stride = itemsize
    for extent in reversed(shape):
        strides.append(stride)
        stride *= extent
    return tuple(reversed(strides))


def _dlpack_like_view(obj: object) -> RtdlBufferView:
    if not callable(getattr(obj, "__dlpack__", None)) or not callable(getattr(obj, "__dlpack_device__", None)):
        raise TypeError("object must expose __dlpack__ and __dlpack_device__")
    shape = tuple(int(value) for value in getattr(obj, "shape"))
    dtype, itemsize = _dtype_and_itemsize(str(getattr(obj, "dtype")))
    device_type, device_id = _device_type(obj.__dlpack_device__())
    pointer = int(obj.data_ptr())
    strides = getattr(obj, "strides", None) or _contiguous_strides(shape, itemsize)
    if len(shape) > 8:
        raise ValueError("RTDL C ABI buffer views support at most 8 dimensions")

    view = RtdlBufferView()
    view.data = ctypes.c_void_p(pointer)
    view.byte_count = int(math.prod(shape) * itemsize)
    view.device_type = device_type
    view.device_id = device_id
    view.dtype = dtype
    view.ndim = len(shape)
    for index, value in enumerate(shape):
        view.shape[index] = value
    for index, value in enumerate(strides):
        view.strides[index] = int(value)
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
        external_runtime=RtdlExternalRuntime(RTDL_DEVICE_HOST, 0, None, None, None),
    )
    context = ctypes.c_void_p()
    status = int(lib.rtdl_context_create(ctypes.byref(desc), ctypes.byref(context)))
    if status != RTDL_STATUS_OK or not context.value:
        raise RuntimeError(f"context_create failed: {_status_text(lib, status)}")

    buffer = ctypes.c_void_p()
    index = ctypes.c_void_p()
    try:
        view = _dlpack_like_view(FakeDLPackLikeArray())
        status = int(lib.rtdl_buffer_import(context, ctypes.byref(view), ctypes.byref(buffer)))
        if status != RTDL_STATUS_OK or not buffer.value:
            raise RuntimeError(f"dlpack-like metadata import failed: {_status_text(lib, status)}")

        exported = RtdlBufferView()
        status = int(lib.rtdl_buffer_export(buffer, ctypes.byref(exported)))
        if status != RTDL_STATUS_OK:
            raise RuntimeError(f"dlpack-like metadata export failed: {_status_text(lib, status)}")
        if (
            exported.data != view.data
            or exported.byte_count != view.byte_count
            or exported.device_type != RTDL_DEVICE_CUDA
            or exported.device_id != 0
            or exported.dtype != RTDL_DTYPE_F32
            or exported.ndim != 2
            or tuple(exported.shape[:2]) != (2, 3)
            or tuple(exported.strides[:2]) != (12, 4)
        ):
            raise RuntimeError("dlpack-like metadata export mismatch")

        index_desc = RtdlIndexDesc(
            abi_version_major=RTDL_ABI_VERSION_MAJOR,
            abi_version_minor=RTDL_ABI_VERSION_MINOR,
            primitive_kind=RTDL_PRIMITIVE_AABB2,
            primitives=buffer,
            primitive_count=2,
        )
        status = int(lib.rtdl_index_build(context, ctypes.byref(index_desc), ctypes.byref(index)))
        if status != RTDL_STATUS_ERROR_INVALID_ARGUMENT or index.value:
            raise RuntimeError("DLPack-like metadata unexpectedly entered host AABB2 query route")
        return "python_ctypes_dlpack_like_metadata_shape=(2,3) query_route_rejected=invalid argument"
    finally:
        if index.value:
            lib.rtdl_index_destroy(index)
        if buffer.value:
            lib.rtdl_buffer_destroy(buffer)
        lib.rtdl_context_destroy(context)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("library", nargs="?", help="Path to librtdl_c_api shared library")
    args = parser.parse_args(argv)
    try:
        print(run(_resolve_library(args.library)))
    except Exception as exc:
        print(f"python_ctypes_dlpack_like_metadata_error {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
