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
RTDL_PRIMITIVE_AABB2 = 1
RTDL_QUERY_AABB_OVERLAP = 1
RTDL_ABI_VERSION_MAJOR = 0
RTDL_ABI_VERSION_MINOR = 1
RTDL_ABI_VERSION_PATCH = 3


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
    lib.rtdl_abi_version_major.argtypes = []
    lib.rtdl_abi_version_major.restype = ctypes.c_uint32
    lib.rtdl_abi_version_minor.argtypes = []
    lib.rtdl_abi_version_minor.restype = ctypes.c_uint32
    lib.rtdl_abi_version_patch.argtypes = []
    lib.rtdl_abi_version_patch.restype = ctypes.c_uint32
    lib.rtdl_abi_is_compatible.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    lib.rtdl_abi_is_compatible.restype = ctypes.c_uint32
    lib.rtdl_backend_is_supported.argtypes = [ctypes.c_int]
    lib.rtdl_backend_is_supported.restype = ctypes.c_uint32
    lib.rtdl_route_is_supported.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    lib.rtdl_route_is_supported.restype = ctypes.c_uint32
    lib.rtdl_status_string.argtypes = [ctypes.c_int]
    lib.rtdl_status_string.restype = ctypes.c_char_p
    lib.rtdl_context_create.argtypes = [ctypes.POINTER(RtdlContextDesc), ctypes.POINTER(ctypes.c_void_p)]
    lib.rtdl_context_create.restype = ctypes.c_int
    lib.rtdl_context_destroy.argtypes = [ctypes.c_void_p]
    lib.rtdl_context_destroy.restype = None


def run(library_path: Path) -> str:
    lib = ctypes.CDLL(str(library_path))
    _configure(lib)
    major = int(lib.rtdl_abi_version_major())
    minor = int(lib.rtdl_abi_version_minor())
    patch = int(lib.rtdl_abi_version_patch())
    if not lib.rtdl_abi_is_compatible(RTDL_ABI_VERSION_MAJOR, RTDL_ABI_VERSION_MINOR, RTDL_ABI_VERSION_PATCH):
        raise RuntimeError("ABI version is not compatible")
    if (major, minor, patch) != (RTDL_ABI_VERSION_MAJOR, RTDL_ABI_VERSION_MINOR, RTDL_ABI_VERSION_PATCH):
        raise RuntimeError(f"unexpected ABI version {major}.{minor}.{patch}")
    if not lib.rtdl_backend_is_supported(RTDL_BACKEND_CPU):
        raise RuntimeError("CPU backend is not supported by the current C ABI library")
    if not lib.rtdl_route_is_supported(RTDL_PRIMITIVE_AABB2, RTDL_QUERY_AABB_OVERLAP, RTDL_DEVICE_HOST):
        raise RuntimeError("host AABB2 overlap route is not supported by the current C ABI library")

    desc = RtdlContextDesc(
        abi_version_major=RTDL_ABI_VERSION_MAJOR,
        abi_version_minor=RTDL_ABI_VERSION_MINOR,
        backend=RTDL_BACKEND_CPU,
        external_runtime=RtdlExternalRuntime(),
    )
    context = ctypes.c_void_p()
    status = int(lib.rtdl_context_create(ctypes.byref(desc), ctypes.byref(context)))
    if status != RTDL_STATUS_OK or not context.value:
        raise RuntimeError(f"rtdl_context_create failed with status {status}")
    try:
        status_text = lib.rtdl_status_string(status).decode("utf-8")
        return f"python_ctypes_ok {major}.{minor}.{patch} {status_text}"
    finally:
        lib.rtdl_context_destroy(context)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("library", nargs="?", help="Path to librtdl_c_api shared library")
    args = parser.parse_args(argv)
    try:
        print(run(_resolve_library(args.library)))
    except Exception as exc:
        print(f"python_ctypes_error {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
