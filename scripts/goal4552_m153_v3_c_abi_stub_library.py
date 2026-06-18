from __future__ import annotations

import argparse
import ctypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_stub_library.goal4552.v1"
OUT_JSON = Path("docs/reports/goal4552_v3_0_m153_c_abi_stub_library_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4552_v3_0_m153_c_abi_stub_library_2026-06-17.md")
SOURCE = Path("src/native/rtdl_c_api.cpp")
HEADER = Path("include/rtdl/rtdl.h")


def _existing_command(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _cxx_compiler() -> str | None:
    env = os.environ.get("CXX")
    candidates = (env,) if env else ()
    if os.name == "nt":
        candidates += (r"C:\Program Files\LLVM\bin\clang++.exe", "clang++", "c++", "g++")
    else:
        candidates += ("c++", "g++", "clang++")
    return _existing_command(tuple(candidate for candidate in candidates if candidate))


def _run_windows_compile(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    vcvars = Path(
        os.environ.get(
            "RTDL_VCVARS64",
            r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
        )
    )
    script = "\r\n".join(
        (
            "@echo off",
            f'call "{vcvars}" >nul 2>&1',
            "if errorlevel 1 exit /b %errorlevel%",
            subprocess.list2cmdline(command),
        )
    )
    with tempfile.NamedTemporaryFile("w", suffix=".bat", delete=False, encoding="utf-8", newline="") as handle:
        handle.write(script)
        script_path = Path(handle.name)
    try:
        return subprocess.run(["cmd", "/c", str(script_path)], cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    finally:
        script_path.unlink(missing_ok=True)


def build_shared_library(root: Path) -> dict[str, Any]:
    compiler = _cxx_compiler()
    if compiler is None:
        return {"compiler": None, "ok": False, "returncode": None, "command": (), "stderr_tail": ("no C++ compiler found",)}
    suffix = ".dll" if os.name == "nt" else ".dylib" if os.uname().sysname == "Darwin" else ".so"
    # Windows keeps a ctypes-loaded DLL mapped until process teardown, so the
    # temporary directory must tolerate cleanup deferral after a successful smoke.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        out = Path(tmp) / ("rtdl_c_api_stub" + suffix)
        command = [
            compiler,
            "-std=c++17",
            "-DRTDL_BUILD_SHARED",
            "-I",
            str(root / "include"),
            str(root / SOURCE),
            "-shared",
        ]
        if os.name != "nt":
            command.append("-fPIC")
        command.extend(["-o", str(out)])
        completed = _run_windows_compile(command, cwd=root) if os.name == "nt" else subprocess.run(
            command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        smoke = None
        if completed.returncode == 0:
            smoke = ctypes_smoke(out)
        return {
            "compiler": compiler,
            "command": command,
            "returncode": completed.returncode,
            "ok": completed.returncode == 0 and bool(smoke and smoke["ok"]),
            "stdout": completed.stdout,
            "stderr_tail": tuple(completed.stderr.splitlines()[-12:]),
            "ctypes_smoke": smoke,
        }


class ExternalRuntime(ctypes.Structure):
    _fields_ = [
        ("device_type", ctypes.c_int),
        ("device_id", ctypes.c_int32),
        ("context", ctypes.c_void_p),
        ("stream", ctypes.c_void_p),
        ("user_data", ctypes.c_void_p),
    ]


class ContextDesc(ctypes.Structure):
    _fields_ = [
        ("abi_version_major", ctypes.c_uint32),
        ("abi_version_minor", ctypes.c_uint32),
        ("backend", ctypes.c_int),
        ("external_runtime", ExternalRuntime),
    ]


class BufferView(ctypes.Structure):
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


def ctypes_smoke(shared_library: Path) -> dict[str, Any]:
    lib = ctypes.CDLL(str(shared_library))
    lib.rtdl_abi_version_major.restype = ctypes.c_uint32
    lib.rtdl_abi_version_minor.restype = ctypes.c_uint32
    lib.rtdl_status_string.argtypes = [ctypes.c_int]
    lib.rtdl_status_string.restype = ctypes.c_char_p
    lib.rtdl_context_create.argtypes = [ctypes.POINTER(ContextDesc), ctypes.POINTER(ctypes.c_void_p)]
    lib.rtdl_context_create.restype = ctypes.c_int
    lib.rtdl_context_destroy.argtypes = [ctypes.c_void_p]
    lib.rtdl_context_destroy.restype = None
    lib.rtdl_buffer_import.argtypes = [ctypes.c_void_p, ctypes.POINTER(BufferView), ctypes.POINTER(ctypes.c_void_p)]
    lib.rtdl_buffer_import.restype = ctypes.c_int
    lib.rtdl_buffer_export.argtypes = [ctypes.c_void_p, ctypes.POINTER(BufferView)]
    lib.rtdl_buffer_export.restype = ctypes.c_int
    lib.rtdl_buffer_destroy.argtypes = [ctypes.c_void_p]
    lib.rtdl_buffer_destroy.restype = None

    desc = ContextDesc(0, 1, 0, ExternalRuntime(0, 0, None, None, None))
    context = ctypes.c_void_p()
    status = lib.rtdl_context_create(ctypes.byref(desc), ctypes.byref(context))
    data = (ctypes.c_uint32 * 4)(1, 2, 3, 4)
    view = BufferView(
        ctypes.cast(data, ctypes.c_void_p),
        ctypes.sizeof(data),
        0,
        0,
        2,
        1,
        (ctypes.c_int64 * 8)(4, 0, 0, 0, 0, 0, 0, 0),
        (ctypes.c_int64 * 8)(4, 0, 0, 0, 0, 0, 0, 0),
        None,
        None,
    )
    buffer = ctypes.c_void_p()
    buffer_status = lib.rtdl_buffer_import(context, ctypes.byref(view), ctypes.byref(buffer))
    exported = BufferView()
    export_status = lib.rtdl_buffer_export(buffer, ctypes.byref(exported))
    if buffer:
        lib.rtdl_buffer_destroy(buffer)
    if context:
        lib.rtdl_context_destroy(context)
    checks = {
        "major_is_zero": lib.rtdl_abi_version_major() == 0,
        "minor_is_one": lib.rtdl_abi_version_minor() == 1,
        "status_string_ok": lib.rtdl_status_string(0) == b"ok",
        "context_created": status == 0 and bool(context.value),
        "buffer_imported": buffer_status == 0 and bool(buffer.value),
        "buffer_exported": export_status == 0 and exported.byte_count == ctypes.sizeof(data),
    }
    return {"ok": all(checks.values()), "checks": checks}


def build_packet(root: Path = Path("."), *, run_compile: bool = False) -> dict[str, Any]:
    source_text = (root / SOURCE).read_text(encoding="utf-8")
    header_text = (root / HEADER).read_text(encoding="utf-8")
    build_result = build_shared_library(root) if run_compile else None
    checks = {
        "source_exists": (root / SOURCE).exists(),
        "header_exists": (root / HEADER).exists(),
        "source_includes_public_header": '#include "rtdl/rtdl.h"' in source_text,
        "version_functions_implemented": "rtdl_abi_version_major" in source_text
        and "rtdl_abi_version_minor" in source_text,
        "context_lifecycle_implemented": "rtdl_context_create" in source_text
        and "rtdl_context_destroy" in source_text,
        "buffer_lifecycle_implemented": "rtdl_buffer_import" in source_text
        and "rtdl_buffer_destroy" in source_text,
        "header_marks_draft_stub_boundary": "minimal lifecycle stub implementation" in header_text
        and "not" in header_text
        and "frozen or backend-capable shared-library contract" in header_text,
    }
    if build_result is not None:
        checks.update(
            {
                "compiler_available": bool(build_result["compiler"]),
                "shared_library_build_ok": bool(build_result["ok"]),
                "ctypes_smoke_ok": bool(build_result["ctypes_smoke"] and build_result["ctypes_smoke"]["ok"]),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4552 / V3 M153",
        "status": "c_abi_stub_library_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "build_result": build_result,
        "claim_boundary": {
            "optix_backend_query_implemented": False,
            "embree_backend_query_implemented": False,
            "broad_backend_query_implemented": False,
            "binary_compatibility_frozen": False,
            "non_python_client_validated": False,
            "dlpack_support_implemented": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4552 adds a minimal V3 C ABI stub implementation for version, "
            "status, context lifecycle, and neutral buffer lifecycle symbols. "
            "A temporary shared-library build and ctypes smoke prove the symbols "
            "load. Later goals add a narrow host AABB2 query proof, but this goal "
            "still makes no OptiX, Embree, broad backend query, DLPack bridge, or "
            "frozen compatibility claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4552 / V3 M153 C ABI Stub Library",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- The stub covers lifecycle and neutral buffer mechanics only.",
            "- No OptiX, Embree, broad backend query, DLPack, release, or performance claim is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_compile=True)
    if not args.no_write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_report(packet, OUT_REPORT)
    print(
        json.dumps(
            {
                "failed_checks": packet["failed_checks"],
                "status": "accept" if not packet["failed_checks"] else "reject",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
