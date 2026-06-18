from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any

from scripts.goal4553_m154_v3_c_abi_c_client_smoke import (
    SOURCE,
    _c_compiler,
    _cxx_compiler,
    _exe_suffix,
    _run_compile,
    _shared_suffix,
    _stderr_tail,
)


PACKET_VERSION = "rtdl.v3_0.c_abi_backend_runtime_fail_closed.goal4573.v1"
OUT_JSON = Path("docs/reports/goal4573_v3_0_m174_c_abi_backend_runtime_fail_closed_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4573_v3_0_m174_c_abi_backend_runtime_fail_closed_2026-06-17.md")
C_ABI_DOC = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_draft.md")
HEADER = Path("include/rtdl/rtdl.h")
CASE_MARKERS = (
    "auto_backend_context_ok",
    "cpu_backend_context_ok",
    "optix_backend_rejected",
    "embree_backend_rejected",
    "external_runtime_rejected",
)


def _client_source() -> str:
    return r'''
#include "rtdl/rtdl.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#if defined(_WIN32)
#include <windows.h>
typedef HMODULE rtdl_test_library;
static rtdl_test_library rtdl_test_open(const char* path) { return LoadLibraryA(path); }
static void* rtdl_test_symbol(rtdl_test_library library, const char* name) {
  return (void*)GetProcAddress(library, name);
}
static void rtdl_test_close(rtdl_test_library library) { FreeLibrary(library); }
#else
#include <dlfcn.h>
typedef void* rtdl_test_library;
static rtdl_test_library rtdl_test_open(const char* path) { return dlopen(path, RTLD_NOW | RTLD_LOCAL); }
static void* rtdl_test_symbol(rtdl_test_library library, const char* name) {
  return dlsym(library, name);
}
static void rtdl_test_close(rtdl_test_library library) { dlclose(library); }
#endif

typedef const char* (*rtdl_context_last_error_fn)(const rtdl_context*);
typedef rtdl_status (*rtdl_context_create_fn)(const rtdl_context_desc*, rtdl_context**);
typedef void (*rtdl_context_destroy_fn)(rtdl_context*);
typedef rtdl_status (*rtdl_context_set_external_runtime_fn)(rtdl_context*, const rtdl_external_runtime*);

#define LOAD_SYMBOL(name, type) \
  type p_##name = (type)rtdl_test_symbol(library, #name); \
  if (p_##name == NULL) { \
    fprintf(stderr, "missing symbol: %s\n", #name); \
    rtdl_test_close(library); \
    return 20; \
  }

#define CASE_OK(name) printf("case %s: ok\n", name)

static rtdl_context_desc make_desc(rtdl_backend backend) {
  rtdl_context_desc desc;
  memset(&desc, 0, sizeof(desc));
  desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  desc.backend = backend;
  return desc;
}

static int require_context_status(
    const char* case_name,
    rtdl_context_create_fn create,
    rtdl_context_destroy_fn destroy,
    rtdl_backend backend,
    rtdl_status expected) {
  rtdl_context_desc desc = make_desc(backend);
  rtdl_context* context = NULL;
  rtdl_status observed = create(&desc, &context);
  if (observed != expected) {
    fprintf(stderr, "case %s failed: observed=%d expected=%d\n", case_name, observed, expected);
    if (context != NULL) {
      destroy(context);
    }
    return 1;
  }
  if (expected == RTDL_STATUS_OK && context == NULL) {
    fprintf(stderr, "case %s failed: expected context\n", case_name);
    return 1;
  }
  if (expected != RTDL_STATUS_OK && context != NULL) {
    fprintf(stderr, "case %s failed: rejected backend returned context\n", case_name);
    destroy(context);
    return 1;
  }
  if (context != NULL) {
    destroy(context);
  }
  CASE_OK(case_name);
  return 0;
}

int main(int argc, char** argv) {
  if (argc != 2) {
    fprintf(stderr, "usage: %s <rtdl shared library>\n", argv[0]);
    return 2;
  }
  rtdl_test_library library = rtdl_test_open(argv[1]);
  if (library == NULL) {
    fprintf(stderr, "could not open shared library\n");
    return 3;
  }

  LOAD_SYMBOL(rtdl_context_last_error, rtdl_context_last_error_fn);
  LOAD_SYMBOL(rtdl_context_create, rtdl_context_create_fn);
  LOAD_SYMBOL(rtdl_context_destroy, rtdl_context_destroy_fn);
  LOAD_SYMBOL(rtdl_context_set_external_runtime, rtdl_context_set_external_runtime_fn);

  if (require_context_status(
          "auto_backend_context_ok",
          p_rtdl_context_create,
          p_rtdl_context_destroy,
          RTDL_BACKEND_AUTO,
          RTDL_STATUS_OK)) {
    return 10;
  }
  if (require_context_status(
          "cpu_backend_context_ok",
          p_rtdl_context_create,
          p_rtdl_context_destroy,
          RTDL_BACKEND_CPU,
          RTDL_STATUS_OK)) {
    return 11;
  }
  if (require_context_status(
          "optix_backend_rejected",
          p_rtdl_context_create,
          p_rtdl_context_destroy,
          RTDL_BACKEND_OPTIX,
          RTDL_STATUS_ERROR_UNSUPPORTED)) {
    return 12;
  }
  if (require_context_status(
          "embree_backend_rejected",
          p_rtdl_context_create,
          p_rtdl_context_destroy,
          RTDL_BACKEND_EMBREE,
          RTDL_STATUS_ERROR_UNSUPPORTED)) {
    return 13;
  }

  rtdl_context_desc desc = make_desc(RTDL_BACKEND_CPU);
  rtdl_context* context = NULL;
  if (p_rtdl_context_create(&desc, &context) != RTDL_STATUS_OK || context == NULL) {
    return 14;
  }
  rtdl_external_runtime runtime;
  memset(&runtime, 0, sizeof(runtime));
  runtime.device_type = RTDL_DEVICE_CUDA;
  runtime.device_id = 0;
  runtime.context = (void*)0x1;
  runtime.stream = (void*)0x2;
  rtdl_status runtime_status = p_rtdl_context_set_external_runtime(context, &runtime);
  const char* error = p_rtdl_context_last_error(context);
  if (runtime_status != RTDL_STATUS_ERROR_UNSUPPORTED || error == NULL || error[0] == '\0') {
    p_rtdl_context_destroy(context);
    return 15;
  }
  CASE_OK("external_runtime_rejected");

  p_rtdl_context_destroy(context);
  rtdl_test_close(library);
  printf("validated_backend_runtime_cases=%d\n", 5);
  return 0;
}
'''


def compile_and_run_backend_runtime_client(root: Path) -> dict[str, Any]:
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
        shared_library = tmpdir / ("rtdl_c_api_backend_runtime" + _shared_suffix())
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

        client_source = tmpdir / "rtdl_c_api_backend_runtime_client.c"
        client_exe = tmpdir / ("rtdl_c_api_backend_runtime_client" + _exe_suffix())
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


def _runtime_cases(stdout: str) -> dict[str, bool]:
    return {marker: f"case {marker}: ok" in stdout for marker in CASE_MARKERS}


def build_packet(root: Path = Path("."), *, run_compile: bool = False) -> dict[str, Any]:
    header = (root / HEADER).read_text(encoding="utf-8")
    doc = (root / C_ABI_DOC).read_text(encoding="utf-8")
    source = (root / SOURCE).read_text(encoding="utf-8")
    client_result = compile_and_run_backend_runtime_client(root) if run_compile else None
    stdout = ""
    if client_result and client_result["client_run"]:
        stdout = str(client_result["client_run"]["stdout"])
    runtime_cases = _runtime_cases(stdout)
    checks = {
        "doc_limits_context_to_auto_cpu": "RTDL_BACKEND_CPU` or `RTDL_BACKEND_AUTO" in doc
        and "Other backend requests" in doc,
        "doc_blocks_non_host_external_runtime_handles": "non-host runtime" in doc
        and "fail-closed" in doc,
        "header_marks_device_runtime_unsupported": "runtime handles and external stream semantics remain unsupported"
        in header,
        "source_rejects_unsupported_backend": "backend_is_supported_by_host_proof" in source
        and "RTDL_STATUS_ERROR_UNSUPPORTED" in source,
        "source_rejects_non_host_external_runtime": "only host external runtime metadata is supported" in source,
        "client_source_checks_backend_and_runtime": "optix_backend_rejected" in _client_source()
        and "external_runtime_rejected" in _client_source(),
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
                "runtime_validated_all_cases": all(runtime_cases.values()),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4573 / V3 M174",
        "status": "c_abi_backend_runtime_fail_closed_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "validated_cases": runtime_cases,
        "client_result": client_result,
        "claim_boundary": {
            "optix_c_abi_backend_supported": False,
            "embree_c_abi_backend_supported": False,
            "external_runtime_supported": False,
            "device_buffer_route_supported": False,
            "stable_abi_authorized": False,
            "performance_wording_authorized": False,
        },
        "conclusion": (
            "Goal4573 hardens the draft C ABI context layer so unsupported backend "
            "and non-host external-runtime hints fail closed. Goal4591 later accepts "
            "host runtime metadata only; the current C ABI proof still accepts only "
            "AUTO/CPU contexts, and OptiX, Embree, CUDA runtime handles, external "
            "streams, and device buffers remain explicit future work rather than "
            "silently accepted no-ops."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4573 / V3 M174 C ABI Backend Runtime Fail-Closed",
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
            "## Runtime Cases",
            "",
            "| Case | Passed |",
            "| --- | --- |",
        ]
    )
    for name, passed in packet["validated_cases"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This validates fail-closed context/backend/runtime behavior for the current C ABI proof.",
            "- It does not implement OptiX, Embree, external runtime handles, device buffers, a stable ABI, or performance wording.",
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
                "validated_cases": packet["validated_cases"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
