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


PACKET_VERSION = "rtdl.v3_0.c_abi_ownership_threading_contract.goal4570.v1"
OUT_JSON = Path("docs/reports/goal4570_v3_0_m171_c_abi_ownership_threading_contract_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4570_v3_0_m171_c_abi_ownership_threading_contract_2026-06-17.md")
CONTRACT = Path("docs/learn/v3_0_c_abi_ownership_threading_contract.md")
C_ABI_DOC = Path("docs/learn/v3_0_c_abi_draft.md")
STABILITY = Path("docs/learn/v3_0_c_abi_stability_policy.md")
EXAMPLE_README = Path("examples/current/embedding/README.md")
LEARN_README = Path("docs/learn/README.md")
HEADER = Path("include/rtdl/rtdl.h")

CASE_MARKERS = (
    "release_callback_called_once",
    "index_survives_primitive_buffer_destroy",
    "result_view_borrowed_until_destroy",
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

typedef rtdl_status (*rtdl_context_create_fn)(const rtdl_context_desc*, rtdl_context**);
typedef void (*rtdl_context_destroy_fn)(rtdl_context*);
typedef rtdl_status (*rtdl_buffer_import_fn)(rtdl_context*, const rtdl_buffer_view*, rtdl_buffer**);
typedef rtdl_status (*rtdl_buffer_export_fn)(const rtdl_buffer*, rtdl_buffer_view*);
typedef void (*rtdl_buffer_destroy_fn)(rtdl_buffer*);
typedef rtdl_status (*rtdl_index_build_fn)(rtdl_context*, const rtdl_index_desc*, rtdl_index**);
typedef rtdl_status (*rtdl_query_execute_fn)(rtdl_context*, const rtdl_index*, const rtdl_query_desc*, rtdl_buffer**);
typedef void (*rtdl_index_destroy_fn)(rtdl_index*);

#define LOAD_SYMBOL(name, type) \
  type p_##name = (type)rtdl_test_symbol(library, #name); \
  if (p_##name == NULL) { \
    fprintf(stderr, "missing symbol: %s\n", #name); \
    rtdl_test_close(library); \
    return 20; \
  }

#define CASE_OK(name) printf("case %s: ok\n", name)

static void count_release(void* data, void* user_data) {
  (void)data;
  int* counter = (int*)user_data;
  if (counter != NULL) {
    *counter += 1;
  }
}

static rtdl_buffer_view make_f32_aabb2_view(float* data, uint64_t count) {
  rtdl_buffer_view view;
  memset(&view, 0, sizeof(view));
  view.data = data;
  view.byte_count = count * 4u * (uint64_t)sizeof(float);
  view.device_type = RTDL_DEVICE_HOST;
  view.dtype = RTDL_DTYPE_F32;
  view.ndim = 2u;
  view.shape[0] = (int64_t)count;
  view.shape[1] = 4;
  view.strides[0] = (int64_t)(4 * sizeof(float));
  view.strides[1] = (int64_t)sizeof(float);
  return view;
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

  LOAD_SYMBOL(rtdl_context_create, rtdl_context_create_fn);
  LOAD_SYMBOL(rtdl_context_destroy, rtdl_context_destroy_fn);
  LOAD_SYMBOL(rtdl_buffer_import, rtdl_buffer_import_fn);
  LOAD_SYMBOL(rtdl_buffer_export, rtdl_buffer_export_fn);
  LOAD_SYMBOL(rtdl_buffer_destroy, rtdl_buffer_destroy_fn);
  LOAD_SYMBOL(rtdl_index_build, rtdl_index_build_fn);
  LOAD_SYMBOL(rtdl_query_execute, rtdl_query_execute_fn);
  LOAD_SYMBOL(rtdl_index_destroy, rtdl_index_destroy_fn);

  rtdl_context_desc desc;
  memset(&desc, 0, sizeof(desc));
  desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  desc.backend = RTDL_BACKEND_AUTO;
  rtdl_context* context = NULL;
  if (p_rtdl_context_create(&desc, &context) != RTDL_STATUS_OK || context == NULL) {
    rtdl_test_close(library);
    return 10;
  }

  int primitive_release_count = 0;
  float primitive_payload[8] = {0.0f, 0.0f, 1.0f, 1.0f, 10.0f, 10.0f, 11.0f, 11.0f};
  rtdl_buffer_view primitive_view = make_f32_aabb2_view(primitive_payload, 2u);
  primitive_view.release = count_release;
  primitive_view.user_data = &primitive_release_count;
  rtdl_buffer* primitive_buffer = NULL;
  if (p_rtdl_buffer_import(context, &primitive_view, &primitive_buffer) != RTDL_STATUS_OK ||
      primitive_buffer == NULL) {
    return 11;
  }

  rtdl_index_desc index_desc;
  memset(&index_desc, 0, sizeof(index_desc));
  index_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  index_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  index_desc.primitive_kind = RTDL_PRIMITIVE_AABB2;
  index_desc.primitives = primitive_buffer;
  index_desc.primitive_count = 2u;
  rtdl_index* index = NULL;
  if (p_rtdl_index_build(context, &index_desc, &index) != RTDL_STATUS_OK || index == NULL) {
    return 12;
  }

  p_rtdl_buffer_destroy(primitive_buffer);
  if (primitive_release_count != 1) {
    fprintf(stderr, "release callback count=%d\n", primitive_release_count);
    return 13;
  }
  CASE_OK("release_callback_called_once");

  primitive_payload[0] = 100.0f;
  primitive_payload[1] = 100.0f;
  primitive_payload[2] = 101.0f;
  primitive_payload[3] = 101.0f;

  int query_release_count = 0;
  float query_payload[4] = {0.25f, 0.25f, 0.75f, 0.75f};
  rtdl_buffer_view query_view = make_f32_aabb2_view(query_payload, 1u);
  query_view.release = count_release;
  query_view.user_data = &query_release_count;
  rtdl_buffer* query_buffer = NULL;
  if (p_rtdl_buffer_import(context, &query_view, &query_buffer) != RTDL_STATUS_OK ||
      query_buffer == NULL) {
    return 14;
  }

  rtdl_query_desc query_desc;
  memset(&query_desc, 0, sizeof(query_desc));
  query_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  query_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  query_desc.query_kind = RTDL_QUERY_AABB_OVERLAP;
  query_desc.inputs = query_buffer;
  query_desc.input_count = 1u;
  rtdl_buffer* result = NULL;
  if (p_rtdl_query_execute(context, index, &query_desc, &result) != RTDL_STATUS_OK || result == NULL) {
    return 15;
  }

  rtdl_buffer_view result_view;
  memset(&result_view, 0, sizeof(result_view));
  if (p_rtdl_buffer_export(result, &result_view) != RTDL_STATUS_OK) {
    return 16;
  }
  if (result_view.dtype != RTDL_DTYPE_U64 || result_view.shape[0] != 1 ||
      result_view.shape[1] != 2 || result_view.release == NULL) {
    return 17;
  }
  uint64_t* rows = (uint64_t*)result_view.data;
  if (rows == NULL || rows[0] != 0u || rows[1] != 0u) {
    return 18;
  }
  CASE_OK("index_survives_primitive_buffer_destroy");
  CASE_OK("result_view_borrowed_until_destroy");

  p_rtdl_buffer_destroy(result);
  p_rtdl_buffer_destroy(query_buffer);
  if (query_release_count != 1) {
    fprintf(stderr, "query release callback count=%d\n", query_release_count);
    return 19;
  }
  p_rtdl_index_destroy(index);
  p_rtdl_context_destroy(context);
  rtdl_test_close(library);
  printf("validated_ownership_cases=%d\n", 3);
  return 0;
}
'''


def compile_and_run_ownership_client(root: Path) -> dict[str, Any]:
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
        shared_library = tmpdir / ("rtdl_c_api_ownership" + _shared_suffix())
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

        client_source = tmpdir / "rtdl_c_api_ownership_client.c"
        client_exe = tmpdir / ("rtdl_c_api_ownership_client" + _exe_suffix())
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


def _compact(text: str) -> str:
    return " ".join(text.split())


def build_packet(root: Path = Path("."), *, run_compile: bool = False) -> dict[str, Any]:
    contract = (root / CONTRACT).read_text(encoding="utf-8")
    compact_contract = _compact(contract)
    c_abi_doc = (root / C_ABI_DOC).read_text(encoding="utf-8")
    stability = (root / STABILITY).read_text(encoding="utf-8")
    example_readme = (root / EXAMPLE_README).read_text(encoding="utf-8")
    learn_readme = (root / LEARN_README).read_text(encoding="utf-8")
    header = (root / HEADER).read_text(encoding="utf-8")
    source = (root / SOURCE).read_text(encoding="utf-8")
    client_result = compile_and_run_ownership_client(root) if run_compile else None
    stdout = ""
    if client_result and client_result["client_run"]:
        stdout = str(client_result["client_run"]["stdout"])
    runtime_cases = _runtime_cases(stdout)
    checks = {
        "contract_doc_exists": (root / CONTRACT).exists(),
        "contract_defines_release_null_caller_retained": "If `release == NULL`" in contract
        and "caller retains ownership" in contract,
        "contract_defines_release_callback_transfer": "If `release != NULL`" in contract
        and "calls that callback exactly once" in contract,
        "contract_defines_index_copy_lifetime": "copies primitive coordinates" in compact_contract
        and "primitive buffer handle may be destroyed" in compact_contract,
        "contract_defines_result_view_lifetime": (
            "valid only until the owning result buffer is destroyed" in compact_contract
        ),
        "contract_defines_last_error_lifetime": "valid only until the next C ABI call" in contract,
        "contract_defines_threading_boundary": "external synchronization" in contract
        and "not yet a release-grade thread-safety guarantee" in contract,
        "c_abi_doc_links_contract": "C ABI Ownership And Threading Contract" in c_abi_doc,
        "c_abi_doc_updates_imported_buffer_wording": "caller-retained when `release == NULL`" in c_abi_doc
        and "release != NULL" in c_abi_doc,
        "stability_policy_links_contract": "v3_0_c_abi_ownership_threading_contract.md" in stability,
        "example_readme_updates_imported_buffer_wording": "caller-retained when `release == NULL`" in example_readme
        and "release-callback-owned" in example_readme,
        "learn_readme_links_contract": "V3.0 C ABI Ownership And Threading Contract" in learn_readme,
        "header_documents_release_switch": "If release is NULL" in header
        and "calls it exactly once" in header,
        "source_calls_release_on_buffer_destroy": "buffer->view.release(buffer->view.data" in source,
        "source_copies_aabb2_into_index": "index->aabb2.assign" in source,
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
        "goal": "Goal4570 / V3 M171",
        "status": "c_abi_ownership_threading_contract_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "validated_cases": runtime_cases,
        "client_result": client_result,
        "claim_boundary": {
            "stable_thread_safety_guarantee": False,
            "packaged_sdk_released": False,
            "cross_version_compatibility_validated": False,
            "device_buffer_ownership_validated": False,
            "external_stream_semantics_validated": False,
            "public_performance_wording_authorized": False,
        },
        "conclusion": (
            "Goal4570 makes the V3 C ABI ownership and threading boundary "
            "explicit: imported buffers are caller-retained when `release` is "
            "NULL, release-callback-owned when `release` is provided, AABB2 "
            "index build copies primitive rows, result exports are borrowed "
            "until result destroy, and same-handle concurrency remains externally "
            "synchronized rather than a stable SDK promise."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4570 / V3 M171 C ABI Ownership And Threading Contract",
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
            "- This documents and validates current source-tree ownership behavior.",
            "- It does not create a stable thread-safety guarantee, packaged SDK, cross-version compatibility claim, device-buffer ownership route, external stream semantics, or performance wording.",
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
