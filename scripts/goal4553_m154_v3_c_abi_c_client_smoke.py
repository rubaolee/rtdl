from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_c_client_smoke.goal4553.v1"
OUT_JSON = Path("docs/reports/goal4553_v3_0_m154_c_abi_c_client_smoke_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4553_v3_0_m154_c_abi_c_client_smoke_2026-06-17.md")
HEADER = Path("include/rtdl/rtdl.h")
SOURCE = Path("src/native/rtdl_c_api.cpp")


def _existing_command(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _c_compiler() -> str | None:
    env = os.environ.get("CC")
    candidates = (env,) if env else ()
    if os.name == "nt":
        candidates += (r"C:\Program Files\LLVM\bin\clang.exe", "clang", "cc", "gcc")
    else:
        candidates += ("cc", "gcc", "clang")
    return _existing_command(tuple(candidate for candidate in candidates if candidate))


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
        return subprocess.run(
            ["cmd", "/c", str(script_path)],
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    finally:
        script_path.unlink(missing_ok=True)


def _run_compile(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    if os.name == "nt":
        return _run_windows_compile(command, cwd=cwd)
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _shared_suffix() -> str:
    if os.name == "nt":
        return ".dll"
    return ".dylib" if os.uname().sysname == "Darwin" else ".so"


def _exe_suffix() -> str:
    return ".exe" if os.name == "nt" else ""


def _stderr_tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _client_source() -> str:
    return "\n".join(
        [
            '#include "rtdl/rtdl.h"',
            "",
            "#include <stdint.h>",
            "#include <stdio.h>",
            "#include <string.h>",
            "",
            "#if defined(_WIN32)",
            "#include <windows.h>",
            "typedef HMODULE rtdl_test_library;",
            "static rtdl_test_library rtdl_test_open(const char* path) { return LoadLibraryA(path); }",
            "static void* rtdl_test_symbol(rtdl_test_library library, const char* name) {",
            "  return (void*)GetProcAddress(library, name);",
            "}",
            "static void rtdl_test_close(rtdl_test_library library) { FreeLibrary(library); }",
            "#else",
            "#include <dlfcn.h>",
            "typedef void* rtdl_test_library;",
            "static rtdl_test_library rtdl_test_open(const char* path) { return dlopen(path, RTLD_NOW | RTLD_LOCAL); }",
            "static void* rtdl_test_symbol(rtdl_test_library library, const char* name) {",
            "  return dlsym(library, name);",
            "}",
            "static void rtdl_test_close(rtdl_test_library library) { dlclose(library); }",
            "#endif",
            "",
            "typedef uint32_t (*rtdl_version_fn)(void);",
            "typedef const char* (*rtdl_status_string_fn)(rtdl_status);",
            "typedef rtdl_status (*rtdl_context_create_fn)(const rtdl_context_desc*, rtdl_context**);",
            "typedef void (*rtdl_context_destroy_fn)(rtdl_context*);",
            "typedef rtdl_status (*rtdl_buffer_import_fn)(rtdl_context*, const rtdl_buffer_view*, rtdl_buffer**);",
            "typedef rtdl_status (*rtdl_buffer_export_fn)(const rtdl_buffer*, rtdl_buffer_view*);",
            "typedef void (*rtdl_buffer_destroy_fn)(rtdl_buffer*);",
            "typedef rtdl_status (*rtdl_index_build_fn)(rtdl_context*, const rtdl_index_desc*, rtdl_index**);",
            "typedef rtdl_status (*rtdl_query_execute_fn)(rtdl_context*, const rtdl_index*, const rtdl_query_desc*, rtdl_buffer**);",
            "typedef void (*rtdl_index_destroy_fn)(rtdl_index*);",
            "",
            "#define LOAD_SYMBOL(name, type) \\",
            "  type name = (type)rtdl_test_symbol(library, #name); \\",
            "  if (name == NULL) { \\",
            "    fprintf(stderr, \"missing symbol: %s\\n\", #name); \\",
            "    rtdl_test_close(library); \\",
            "    return 20; \\",
            "  }",
            "",
            "int main(int argc, char** argv) {",
            "  if (argc != 2) {",
            "    fprintf(stderr, \"usage: %s <rtdl shared library>\\n\", argv[0]);",
            "    return 2;",
            "  }",
            "  rtdl_test_library library = rtdl_test_open(argv[1]);",
            "  if (library == NULL) {",
            "    fprintf(stderr, \"could not open shared library\\n\");",
            "    return 3;",
            "  }",
            "",
            "  LOAD_SYMBOL(rtdl_abi_version_major, rtdl_version_fn);",
            "  LOAD_SYMBOL(rtdl_abi_version_minor, rtdl_version_fn);",
            "  LOAD_SYMBOL(rtdl_status_string, rtdl_status_string_fn);",
            "  LOAD_SYMBOL(rtdl_context_create, rtdl_context_create_fn);",
            "  LOAD_SYMBOL(rtdl_context_destroy, rtdl_context_destroy_fn);",
            "  LOAD_SYMBOL(rtdl_buffer_import, rtdl_buffer_import_fn);",
            "  LOAD_SYMBOL(rtdl_buffer_export, rtdl_buffer_export_fn);",
            "  LOAD_SYMBOL(rtdl_buffer_destroy, rtdl_buffer_destroy_fn);",
            "  LOAD_SYMBOL(rtdl_index_build, rtdl_index_build_fn);",
            "  LOAD_SYMBOL(rtdl_query_execute, rtdl_query_execute_fn);",
            "  LOAD_SYMBOL(rtdl_index_destroy, rtdl_index_destroy_fn);",
            "",
            "  if (rtdl_abi_version_major() != 0 || rtdl_abi_version_minor() != 1) {",
            "    rtdl_test_close(library);",
            "    return 10;",
            "  }",
            "  if (strcmp(rtdl_status_string(RTDL_STATUS_OK), \"ok\") != 0) {",
            "    rtdl_test_close(library);",
            "    return 11;",
            "  }",
            "",
            "  rtdl_context_desc desc;",
            "  memset(&desc, 0, sizeof(desc));",
            "  desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;",
            "  desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;",
            "  desc.backend = RTDL_BACKEND_AUTO;",
            "  rtdl_context* context = NULL;",
            "  if (rtdl_context_create(&desc, &context) != RTDL_STATUS_OK || context == NULL) {",
            "    rtdl_test_close(library);",
            "    return 12;",
            "  }",
            "",
            "  uint32_t payload[4] = {1u, 2u, 3u, 4u};",
            "  rtdl_buffer_view view;",
            "  memset(&view, 0, sizeof(view));",
            "  view.data = payload;",
            "  view.byte_count = (uint64_t)sizeof(payload);",
            "  view.device_type = RTDL_DEVICE_HOST;",
            "  view.dtype = RTDL_DTYPE_U32;",
            "  view.ndim = 1u;",
            "  view.shape[0] = 4;",
            "  view.strides[0] = (int64_t)sizeof(uint32_t);",
            "  rtdl_buffer* buffer = NULL;",
            "  if (rtdl_buffer_import(context, &view, &buffer) != RTDL_STATUS_OK || buffer == NULL) {",
            "    rtdl_context_destroy(context);",
            "    rtdl_test_close(library);",
            "    return 13;",
            "  }",
            "  rtdl_buffer_view exported;",
            "  memset(&exported, 0, sizeof(exported));",
            "  if (rtdl_buffer_export(buffer, &exported) != RTDL_STATUS_OK) {",
            "    rtdl_buffer_destroy(buffer);",
            "    rtdl_context_destroy(context);",
            "    rtdl_test_close(library);",
            "    return 14;",
            "  }",
            "  if (exported.byte_count != (uint64_t)sizeof(payload) || exported.data != payload) {",
            "    rtdl_buffer_destroy(buffer);",
            "    rtdl_context_destroy(context);",
            "    rtdl_test_close(library);",
            "    return 15;",
            "  }",
            "  float primitive_payload[8] = {0.0f, 0.0f, 1.0f, 1.0f, 10.0f, 10.0f, 11.0f, 11.0f};",
            "  rtdl_buffer_view primitive_view;",
            "  memset(&primitive_view, 0, sizeof(primitive_view));",
            "  primitive_view.data = primitive_payload;",
            "  primitive_view.byte_count = (uint64_t)sizeof(primitive_payload);",
            "  primitive_view.device_type = RTDL_DEVICE_HOST;",
            "  primitive_view.dtype = RTDL_DTYPE_F32;",
            "  primitive_view.ndim = 2u;",
            "  primitive_view.shape[0] = 2;",
            "  primitive_view.shape[1] = 4;",
            "  primitive_view.strides[0] = (int64_t)(4 * sizeof(float));",
            "  primitive_view.strides[1] = (int64_t)sizeof(float);",
            "  rtdl_buffer* primitive_buffer = NULL;",
            "  if (rtdl_buffer_import(context, &primitive_view, &primitive_buffer) != RTDL_STATUS_OK || primitive_buffer == NULL) {",
            "    rtdl_buffer_destroy(buffer);",
            "    rtdl_context_destroy(context);",
            "    rtdl_test_close(library);",
            "    return 16;",
            "  }",
            "  float query_payload[4] = {0.25f, 0.25f, 0.75f, 0.75f};",
            "  rtdl_buffer_view query_view;",
            "  memset(&query_view, 0, sizeof(query_view));",
            "  query_view.data = query_payload;",
            "  query_view.byte_count = (uint64_t)sizeof(query_payload);",
            "  query_view.device_type = RTDL_DEVICE_HOST;",
            "  query_view.dtype = RTDL_DTYPE_F32;",
            "  query_view.ndim = 2u;",
            "  query_view.shape[0] = 1;",
            "  query_view.shape[1] = 4;",
            "  query_view.strides[0] = (int64_t)(4 * sizeof(float));",
            "  query_view.strides[1] = (int64_t)sizeof(float);",
            "  rtdl_buffer* query_buffer = NULL;",
            "  if (rtdl_buffer_import(context, &query_view, &query_buffer) != RTDL_STATUS_OK || query_buffer == NULL) {",
            "    rtdl_buffer_destroy(primitive_buffer);",
            "    rtdl_buffer_destroy(buffer);",
            "    rtdl_context_destroy(context);",
            "    rtdl_test_close(library);",
            "    return 17;",
            "  }",
            "  rtdl_index_desc index_desc;",
            "  memset(&index_desc, 0, sizeof(index_desc));",
            "  index_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;",
            "  index_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;",
            "  index_desc.primitive_kind = RTDL_PRIMITIVE_AABB2;",
            "  index_desc.primitives = primitive_buffer;",
            "  index_desc.primitive_count = 2u;",
            "  rtdl_index* index = NULL;",
            "  if (rtdl_index_build(context, &index_desc, &index) != RTDL_STATUS_OK || index == NULL) {",
            "    rtdl_buffer_destroy(query_buffer);",
            "    rtdl_buffer_destroy(primitive_buffer);",
            "    rtdl_buffer_destroy(buffer);",
            "    rtdl_context_destroy(context);",
            "    rtdl_test_close(library);",
            "    return 18;",
            "  }",
            "  rtdl_query_desc query_desc;",
            "  memset(&query_desc, 0, sizeof(query_desc));",
            "  query_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;",
            "  query_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;",
            "  query_desc.query_kind = RTDL_QUERY_AABB_OVERLAP;",
            "  query_desc.inputs = query_buffer;",
            "  query_desc.input_count = 1u;",
            "  rtdl_buffer* result_buffer = NULL;",
            "  if (rtdl_query_execute(context, index, &query_desc, &result_buffer) != RTDL_STATUS_OK || result_buffer == NULL) {",
            "    rtdl_index_destroy(index);",
            "    rtdl_buffer_destroy(query_buffer);",
            "    rtdl_buffer_destroy(primitive_buffer);",
            "    rtdl_buffer_destroy(buffer);",
            "    rtdl_context_destroy(context);",
            "    rtdl_test_close(library);",
            "    return 19;",
            "  }",
            "  rtdl_buffer_view result_view;",
            "  memset(&result_view, 0, sizeof(result_view));",
            "  if (rtdl_buffer_export(result_buffer, &result_view) != RTDL_STATUS_OK) {",
            "    rtdl_buffer_destroy(result_buffer);",
            "    rtdl_index_destroy(index);",
            "    rtdl_buffer_destroy(query_buffer);",
            "    rtdl_buffer_destroy(primitive_buffer);",
            "    rtdl_buffer_destroy(buffer);",
            "    rtdl_context_destroy(context);",
            "    rtdl_test_close(library);",
            "    return 20;",
            "  }",
            "  uint64_t* result_pairs = (uint64_t*)result_view.data;",
            "  if (result_view.dtype != RTDL_DTYPE_U64 || result_view.shape[0] != 1 || result_view.shape[1] != 2 ||",
            "      result_pairs == NULL || result_pairs[0] != 0u || result_pairs[1] != 0u) {",
            "    rtdl_buffer_destroy(result_buffer);",
            "    rtdl_index_destroy(index);",
            "    rtdl_buffer_destroy(query_buffer);",
            "    rtdl_buffer_destroy(primitive_buffer);",
            "    rtdl_buffer_destroy(buffer);",
            "    rtdl_context_destroy(context);",
            "    rtdl_test_close(library);",
            "    return 21;",
            "  }",
            "  rtdl_buffer_destroy(result_buffer);",
            "  rtdl_index_destroy(index);",
            "  rtdl_buffer_destroy(query_buffer);",
            "  rtdl_buffer_destroy(primitive_buffer);",
            "",
            "  rtdl_buffer_destroy(buffer);",
            "  rtdl_context_destroy(context);",
            "  rtdl_test_close(library);",
            "  return 0;",
            "}",
            "",
        ]
    )


def compile_and_run_c_client(root: Path) -> dict[str, Any]:
    c_compiler = _c_compiler()
    cxx_compiler = _cxx_compiler()
    result: dict[str, Any] = {
        "c_compiler": c_compiler,
        "cxx_compiler": cxx_compiler,
        "shared_library": None,
        "client_compile": None,
        "client_run": None,
        "ok": False,
    }
    if c_compiler is None or cxx_compiler is None:
        return result

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        tmpdir = Path(tmp)
        shared_library = tmpdir / ("rtdl_c_api_stub" + _shared_suffix())
        shared_command = [
            cxx_compiler,
            "-std=c++17",
            "-DRTDL_BUILD_SHARED",
            "-I",
            str(root / "include"),
            str(root / SOURCE),
            "-shared",
        ]
        if os.name != "nt":
            shared_command.append("-fPIC")
        shared_command.extend(["-o", str(shared_library)])
        shared_completed = _run_compile(shared_command, cwd=root)
        result["shared_library"] = {
            "command": shared_command,
            "returncode": shared_completed.returncode,
            "ok": shared_completed.returncode == 0,
            "stdout": shared_completed.stdout,
            "stderr_tail": _stderr_tail(shared_completed.stderr),
        }
        if shared_completed.returncode != 0:
            return result

        client_source = tmpdir / "rtdl_c_client_smoke.c"
        client_exe = tmpdir / ("rtdl_c_client_smoke" + _exe_suffix())
        client_source.write_text(_client_source(), encoding="utf-8")
        client_command = [
            c_compiler,
            "-std=c11",
            "-I",
            str(root / "include"),
            str(client_source),
            "-o",
            str(client_exe),
        ]
        if os.name != "nt":
            client_command.append("-ldl")
        client_completed = _run_compile(client_command, cwd=root)
        result["client_compile"] = {
            "command": client_command,
            "returncode": client_completed.returncode,
            "ok": client_completed.returncode == 0,
            "stdout": client_completed.stdout,
            "stderr_tail": _stderr_tail(client_completed.stderr),
        }
        if client_completed.returncode != 0:
            return result

        run_completed = subprocess.run(
            [str(client_exe), str(shared_library)],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        result["client_run"] = {
            "command": [str(client_exe), str(shared_library)],
            "returncode": run_completed.returncode,
            "ok": run_completed.returncode == 0,
            "stdout": run_completed.stdout,
            "stderr_tail": _stderr_tail(run_completed.stderr),
        }
        result["ok"] = run_completed.returncode == 0
    return result


def build_packet(root: Path = Path("."), *, run_compile: bool = False) -> dict[str, Any]:
    header_text = (root / HEADER).read_text(encoding="utf-8")
    source_text = (root / SOURCE).read_text(encoding="utf-8")
    client_result = compile_and_run_c_client(root) if run_compile else None
    checks = {
        "header_exists": (root / HEADER).exists(),
        "stub_source_exists": (root / SOURCE).exists(),
        "header_has_context_and_buffer_api": "rtdl_context_create" in header_text
        and "rtdl_buffer_import" in header_text,
        "stub_exports_context_and_buffer_api": "rtdl_context_create" in source_text
        and "rtdl_buffer_import" in source_text,
        "client_source_uses_c_header": '#include "rtdl/rtdl.h"' in _client_source(),
        "client_source_uses_dynamic_library_api": "dlopen" in _client_source()
        and "LoadLibraryA" in _client_source(),
    }
    if client_result is not None:
        checks.update(
            {
                "c_compiler_available": bool(client_result["c_compiler"]),
                "cxx_compiler_available": bool(client_result["cxx_compiler"]),
                "shared_library_build_ok": bool(
                    client_result["shared_library"] and client_result["shared_library"]["ok"]
                ),
                "c_client_compile_ok": bool(
                    client_result["client_compile"] and client_result["client_compile"]["ok"]
                ),
                "c_client_run_ok": bool(client_result["client_run"] and client_result["client_run"]["ok"]),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4553 / V3 M154",
        "status": "c_abi_c_client_smoke_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "client_result": client_result,
        "validated_capabilities": {
            "non_python_c11_dynamic_client_validated": bool(client_result and client_result["ok"]),
            "version_status_context_buffer_lifecycle_symbols_validated": bool(client_result and client_result["ok"]),
            "host_f32_aabb2_overlap_query_validated": bool(client_result and client_result["ok"]),
        },
        "claim_boundary": {
            "backend_query_implemented": False,
            "binary_compatibility_frozen": False,
            "dlpack_support_implemented": False,
            "external_stream_semantics_validated": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4553 validates the V3 C ABI stub from a real C11 client: the "
            "test builds the stub shared library, compiles a C client, dynamically "
            "loads the library, resolves the public symbols, and exercises version, "
            "status, context, neutral-buffer lifecycle, and a minimal host F32 "
            "AABB2 overlap query. It still makes no "
            "backend query, DLPack, external-stream, frozen-ABI, or release claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4553 / V3 M154 C ABI C Client Smoke",
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
            "- This validates a non-Python C11 dynamic-load client against the lifecycle stub.",
            "- No backend query, DLPack bridge, external stream semantics, frozen ABI, or release claim is authorized.",
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
