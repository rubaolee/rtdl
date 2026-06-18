from __future__ import annotations

import argparse
import json
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


PACKET_VERSION = "rtdl.v3_0.c_abi_last_error_diagnostics.goal4611.v1"
OUT_JSON = Path("docs/reports/goal4611_v3_0_m212_c_abi_last_error_diagnostics_smoke_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4611_v3_0_m212_c_abi_last_error_diagnostics_smoke_2026-06-17.md")
HEADER = Path("include/rtdl/rtdl.h")
SOURCE_FILE = Path("src/native/rtdl_c_api.cpp")
OWNERSHIP_DOC = Path("docs/learn/v3_0_c_abi_ownership_threading_contract.md")
ARCHITECTURE_DOC = Path("docs/learn/v3_0_embeddability_architecture_strategy.md")
BINDING_MATRIX = Path("docs/learn/v3_0_binding_and_device_interop_matrix.md")
BENCHMARK_INDEX = Path("docs/learn/benchmark_evidence_index.md")
CASE_MARKERS = (
    "status_strings_stable",
    "null_context_last_error_stable",
    "initial_last_error_empty",
    "invalid_buffer_import_sets_message",
    "successful_buffer_import_clears_error",
    "cuda_runtime_sets_message",
    "host_runtime_clears_error",
    "index_abi_mismatch_sets_message",
    "successful_index_build_clears_error",
    "unsupported_query_sets_message",
    "successful_query_clears_error",
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

typedef const char* (*rtdl_status_string_fn)(rtdl_status);
typedef const char* (*rtdl_context_last_error_fn)(const rtdl_context*);
typedef rtdl_status (*rtdl_context_create_fn)(const rtdl_context_desc*, rtdl_context**);
typedef void (*rtdl_context_destroy_fn)(rtdl_context*);
typedef rtdl_status (*rtdl_context_set_external_runtime_fn)(rtdl_context*, const rtdl_external_runtime*);
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

static int require_status(const char* case_name, rtdl_status observed, rtdl_status expected) {
  if (observed != expected) {
    fprintf(stderr, "case %s failed: observed=%d expected=%d\n", case_name, observed, expected);
    return 1;
  }
  return 0;
}

static int require_error_empty(
    const char* case_name,
    rtdl_context* context,
    rtdl_context_last_error_fn p_rtdl_context_last_error) {
  const char* message = p_rtdl_context_last_error(context);
  if (message == NULL || message[0] != '\0') {
    fprintf(stderr, "case %s failed: expected empty last_error, got '%s'\n",
            case_name, message == NULL ? "<null>" : message);
    return 1;
  }
  CASE_OK(case_name);
  return 0;
}

static int require_error_contains(
    const char* case_name,
    rtdl_context* context,
    const char* needle,
    rtdl_context_last_error_fn p_rtdl_context_last_error) {
  const char* message = p_rtdl_context_last_error(context);
  if (message == NULL || strstr(message, needle) == NULL) {
    fprintf(stderr, "case %s failed: expected last_error containing '%s', got '%s'\n",
            case_name, needle, message == NULL ? "<null>" : message);
    return 1;
  }
  CASE_OK(case_name);
  return 0;
}

static int require_status_string(
    const char* case_name,
    rtdl_status status,
    const char* expected,
    rtdl_status_string_fn p_rtdl_status_string) {
  const char* observed = p_rtdl_status_string(status);
  if (observed == NULL || strcmp(observed, expected) != 0) {
    fprintf(stderr, "case %s failed: status string for %d was '%s', expected '%s'\n",
            case_name, status, observed == NULL ? "<null>" : observed, expected);
    return 1;
  }
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

  LOAD_SYMBOL(rtdl_status_string, rtdl_status_string_fn);
  LOAD_SYMBOL(rtdl_context_last_error, rtdl_context_last_error_fn);
  LOAD_SYMBOL(rtdl_context_create, rtdl_context_create_fn);
  LOAD_SYMBOL(rtdl_context_destroy, rtdl_context_destroy_fn);
  LOAD_SYMBOL(rtdl_context_set_external_runtime, rtdl_context_set_external_runtime_fn);
  LOAD_SYMBOL(rtdl_buffer_import, rtdl_buffer_import_fn);
  LOAD_SYMBOL(rtdl_buffer_export, rtdl_buffer_export_fn);
  LOAD_SYMBOL(rtdl_buffer_destroy, rtdl_buffer_destroy_fn);
  LOAD_SYMBOL(rtdl_index_build, rtdl_index_build_fn);
  LOAD_SYMBOL(rtdl_query_execute, rtdl_query_execute_fn);
  LOAD_SYMBOL(rtdl_index_destroy, rtdl_index_destroy_fn);

  if (require_status_string("status_ok", RTDL_STATUS_OK, "ok", p_rtdl_status_string) ||
      require_status_string(
          "status_invalid", RTDL_STATUS_ERROR_INVALID_ARGUMENT, "invalid argument", p_rtdl_status_string) ||
      require_status_string(
          "status_unsupported", RTDL_STATUS_ERROR_UNSUPPORTED, "unsupported", p_rtdl_status_string) ||
      require_status_string(
          "status_backend", RTDL_STATUS_ERROR_BACKEND, "backend error", p_rtdl_status_string) ||
      require_status_string(
          "status_internal", RTDL_STATUS_ERROR_INTERNAL, "internal error", p_rtdl_status_string) ||
      require_status_string("status_unknown", (rtdl_status)9999, "unknown status", p_rtdl_status_string)) {
    rtdl_test_close(library);
    return 30;
  }
  CASE_OK("status_strings_stable");

  const char* null_error = p_rtdl_context_last_error(NULL);
  if (null_error == NULL || strcmp(null_error, "context is null") != 0) {
    fprintf(stderr, "case null_context_last_error_stable failed: '%s'\n",
            null_error == NULL ? "<null>" : null_error);
    rtdl_test_close(library);
    return 31;
  }
  CASE_OK("null_context_last_error_stable");

  rtdl_context_desc context_desc;
  memset(&context_desc, 0, sizeof(context_desc));
  context_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  context_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  context_desc.backend = RTDL_BACKEND_CPU;
  rtdl_context* context = NULL;
  if (p_rtdl_context_create(&context_desc, &context) != RTDL_STATUS_OK || context == NULL) {
    rtdl_test_close(library);
    return 32;
  }
  if (require_error_empty("initial_last_error_empty", context, p_rtdl_context_last_error)) {
    return 33;
  }

  float primitive_payload[8] = {0.0f, 0.0f, 1.0f, 1.0f, 10.0f, 10.0f, 11.0f, 11.0f};
  rtdl_buffer_view primitive_view = make_f32_aabb2_view(primitive_payload, 2u);
  rtdl_buffer_view bad_buffer_view = primitive_view;
  bad_buffer_view.ndim = 9u;
  rtdl_buffer* bad_buffer = NULL;
  if (require_status(
          "invalid_buffer_import_sets_message",
          p_rtdl_buffer_import(context, &bad_buffer_view, &bad_buffer),
          RTDL_STATUS_ERROR_INVALID_ARGUMENT) ||
      bad_buffer != NULL ||
      require_error_contains(
          "invalid_buffer_import_sets_message",
          context,
          "buffer import requires known device/dtype metadata",
          p_rtdl_context_last_error)) {
    return 34;
  }

  rtdl_buffer* primitive_buffer = NULL;
  if (p_rtdl_buffer_import(context, &primitive_view, &primitive_buffer) != RTDL_STATUS_OK ||
      primitive_buffer == NULL ||
      require_error_empty("successful_buffer_import_clears_error", context, p_rtdl_context_last_error)) {
    return 35;
  }

  rtdl_external_runtime cuda_runtime;
  memset(&cuda_runtime, 0, sizeof(cuda_runtime));
  cuda_runtime.device_type = RTDL_DEVICE_CUDA;
  cuda_runtime.device_id = 0;
  if (require_status(
          "cuda_runtime_sets_message",
          p_rtdl_context_set_external_runtime(context, &cuda_runtime),
          RTDL_STATUS_ERROR_UNSUPPORTED) ||
      require_error_contains(
          "cuda_runtime_sets_message",
          context,
          "only host external runtime metadata",
          p_rtdl_context_last_error)) {
    return 36;
  }

  rtdl_external_runtime host_runtime;
  memset(&host_runtime, 0, sizeof(host_runtime));
  host_runtime.device_type = RTDL_DEVICE_HOST;
  host_runtime.device_id = -1;
  host_runtime.user_data = &host_runtime;
  if (p_rtdl_context_set_external_runtime(context, &host_runtime) != RTDL_STATUS_OK ||
      require_error_empty("host_runtime_clears_error", context, p_rtdl_context_last_error)) {
    return 37;
  }

  rtdl_index_desc index_desc;
  memset(&index_desc, 0, sizeof(index_desc));
  index_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  index_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  index_desc.primitive_kind = RTDL_PRIMITIVE_AABB2;
  index_desc.primitives = primitive_buffer;
  index_desc.primitive_count = 2u;

  rtdl_index_desc bad_index_desc = index_desc;
  bad_index_desc.abi_version_major = 99u;
  rtdl_index* bad_index = NULL;
  if (require_status(
          "index_abi_mismatch_sets_message",
          p_rtdl_index_build(context, &bad_index_desc, &bad_index),
          RTDL_STATUS_ERROR_UNSUPPORTED) ||
      bad_index != NULL ||
      require_error_contains(
          "index_abi_mismatch_sets_message",
          context,
          "index descriptor ABI version is unsupported",
          p_rtdl_context_last_error)) {
    return 38;
  }

  rtdl_index* index = NULL;
  if (p_rtdl_index_build(context, &index_desc, &index) != RTDL_STATUS_OK ||
      index == NULL ||
      require_error_empty("successful_index_build_clears_error", context, p_rtdl_context_last_error)) {
    return 39;
  }

  float query_payload[4] = {0.25f, 0.25f, 0.75f, 0.75f};
  rtdl_buffer_view query_view = make_f32_aabb2_view(query_payload, 1u);
  rtdl_buffer* query_buffer = NULL;
  if (p_rtdl_buffer_import(context, &query_view, &query_buffer) != RTDL_STATUS_OK ||
      query_buffer == NULL) {
    return 40;
  }

  rtdl_query_desc query_desc;
  memset(&query_desc, 0, sizeof(query_desc));
  query_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  query_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  query_desc.query_kind = RTDL_QUERY_AABB_OVERLAP;
  query_desc.inputs = query_buffer;
  query_desc.input_count = 1u;

  rtdl_query_desc bad_query_desc = query_desc;
  bad_query_desc.query_kind = RTDL_QUERY_NEAREST;
  rtdl_buffer* bad_result = NULL;
  if (require_status(
          "unsupported_query_sets_message",
          p_rtdl_query_execute(context, index, &bad_query_desc, &bad_result),
          RTDL_STATUS_ERROR_UNSUPPORTED) ||
      bad_result != NULL ||
      require_error_contains(
          "unsupported_query_sets_message",
          context,
          "only host F32 AABB2 overlap query",
          p_rtdl_context_last_error)) {
    return 41;
  }

  rtdl_buffer* result = NULL;
  if (p_rtdl_query_execute(context, index, &query_desc, &result) != RTDL_STATUS_OK ||
      result == NULL ||
      require_error_empty("successful_query_clears_error", context, p_rtdl_context_last_error)) {
    return 42;
  }
  rtdl_buffer_view result_view;
  memset(&result_view, 0, sizeof(result_view));
  if (p_rtdl_buffer_export(result, &result_view) != RTDL_STATUS_OK ||
      result_view.dtype != RTDL_DTYPE_U64 ||
      result_view.ndim != 2u ||
      result_view.shape[0] != 1 ||
      result_view.shape[1] != 2) {
    fprintf(stderr, "result contract mismatch\n");
    return 43;
  }

  p_rtdl_buffer_destroy(result);
  p_rtdl_buffer_destroy(query_buffer);
  p_rtdl_index_destroy(index);
  p_rtdl_buffer_destroy(primitive_buffer);
  p_rtdl_context_destroy(context);
  rtdl_test_close(library);
  printf("validated_last_error_lifecycle_cases=11\n");
  return 0;
}
'''


def compile_and_run_diagnostics_client(root: Path) -> dict[str, Any]:
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
        shared_library = tmpdir / ("rtdl_c_api_last_error" + _shared_suffix())
        shared_command = [
            cxx_compiler,
            "-std=c++17",
            "-DRTDL_BUILD_SHARED",
            "-I",
            str(root / "include"),
            str(root / SOURCE),
            "-shared",
        ]
        if shared_library.suffix != ".dll":
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

        client_source = tmpdir / "rtdl_c_abi_last_error_diagnostics.c"
        client_exe = tmpdir / ("rtdl_c_abi_last_error_diagnostics" + _exe_suffix())
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
        if client_exe.suffix != ".exe":
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


def build_packet(root: Path = Path("."), *, run_client: bool = False) -> dict[str, Any]:
    header = (root / HEADER).read_text(encoding="utf-8")
    source = (root / SOURCE_FILE).read_text(encoding="utf-8")
    ownership = (root / OWNERSHIP_DOC).read_text(encoding="utf-8")
    architecture = (root / ARCHITECTURE_DOC).read_text(encoding="utf-8")
    binding = (root / BINDING_MATRIX).read_text(encoding="utf-8")
    index = (root / BENCHMARK_INDEX).read_text(encoding="utf-8")
    client_source = _client_source()
    client_result = compile_and_run_diagnostics_client(root) if run_client else None
    stdout = ""
    if client_result and client_result.get("client_run"):
        stdout = str(client_result["client_run"].get("stdout") or "")
    validated_cases = {marker: marker in stdout for marker in CASE_MARKERS}
    checks = {
        "header_declares_status_string_and_last_error": "rtdl_status_string" in header
        and "rtdl_context_last_error" in header,
        "source_has_status_string_and_null_context_diagnostic": "unknown status" in source
        and "context is null" in source,
        "source_clears_context_errors_after_successful_mutations": "clear_error(context);" in source
        and "rtdl_buffer_import" in source
        and "rtdl_index_build" in source
        and "rtdl_query_execute" in source,
        "client_source_covers_all_lifecycle_markers": all(marker in client_source for marker in CASE_MARKERS),
        "ownership_doc_defines_last_error_clear_rule": "Successful C ABI calls that mutate a context clear" in ownership,
        "ownership_doc_keeps_error_text_non_machine_contract": "must not parse it as a stable" in ownership
        and "machine contract" in ownership,
        "architecture_doc_current_to_goal4611": "As of Goal4611" in architecture
        and "Last-error/status diagnostic lifecycle smoke" in architecture,
        "binding_matrix_names_last_error_diagnostics": "C ABI status/last-error diagnostics" in binding,
        "benchmark_index_links_goal4611": "Goal4611 C ABI last-error diagnostics smoke" in index,
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
                "runtime_validated_all_lifecycle_cases": all(validated_cases.values())
                and "validated_last_error_lifecycle_cases=11" in stdout,
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4611 / V3 M212",
        "status": "c_abi_last_error_diagnostics_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "case_markers": CASE_MARKERS,
        "validated_cases": validated_cases,
        "client_result": client_result,
        "support_matrix": {
            "status_string_diagnostics": "validated_source_tree_smoke",
            "null_context_last_error": "validated_source_tree_smoke",
            "last_error_set_on_selected_failures": "validated_source_tree_smoke",
            "last_error_cleared_after_successful_context_mutations": "validated_source_tree_smoke",
            "last_error_text_as_machine_contract": "blocked_use_status_codes",
        },
        "claim_boundary": {
            "diagnostic_lifecycle_authorized": not failed,
            "stable_error_text_authorized": False,
            "all_failure_paths_exhaustively_validated": False,
            "thread_safe_last_error_reads_authorized": False,
            "release_authorized": False,
            "performance_wording_authorized": False,
        },
        "conclusion": (
            "Goal4611 adds a C dynamic-load smoke for the C ABI diagnostic "
            "surface: status strings, null-context last-error behavior, selected "
            "failure messages, and clearing of last_error after successful "
            "context-mutating calls. This makes the embedding boundary easier to "
            "debug from Python/Rust/Julia-style bindings while keeping status "
            "codes as the only branching contract. It does not freeze exact error "
            "text, exhaustively validate every failure path, authorize concurrent "
            "last-error reads, or authorize release/performance wording."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    client = packet["client_result"] or {}
    run_result = client.get("client_run") or {}
    lines = [
        "# Goal4611 / V3 M212 C ABI Last-Error Diagnostics Smoke",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Runtime Cases",
        "",
        "| Case | Validated |",
        "| --- | --- |",
    ]
    for name, passed in packet["validated_cases"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Smoke",
            "",
            f"- OK: `{client.get('ok')}`",
            f"- C compiler: `{client.get('c_compiler')}`",
            f"- C++ compiler: `{client.get('cxx_compiler')}`",
            f"- Output marker: `{str(run_result.get('stdout') or '').strip()}`",
            "",
            "## Support Matrix",
            "",
            "| Surface | Status |",
            "| --- | --- |",
        ]
    )
    for name, status in packet["support_matrix"].items():
        lines.append(f"| `{name}` | `{status}` |")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Status codes remain the machine-readable branching contract.",
            "- Last-error text is diagnostic and may change while the ABI is still draft.",
            "- This is not exhaustive failure-path coverage, thread-safe last-error authorization, release evidence, or performance evidence.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-client", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_client=not args.no_client)
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
