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


PACKET_VERSION = "rtdl.v3_0.c_abi_aabb2_layout_validation.goal4567.v1"
OUT_JSON = Path("docs/reports/goal4567_v3_0_m168_c_abi_aabb2_layout_validation_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4567_v3_0_m168_c_abi_aabb2_layout_validation_2026-06-17.md")
HEADER = Path("include/rtdl/rtdl.h")
CASE_MARKERS = (
    "bad_index_shape_rejected",
    "bad_query_stride_rejected",
    "zero_count_empty_result_ok",
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

  float primitive_payload[8] = {0.0f, 0.0f, 1.0f, 1.0f, 10.0f, 10.0f, 11.0f, 11.0f};
  rtdl_buffer_view primitive_view = make_f32_aabb2_view(primitive_payload, 2u);
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

  rtdl_buffer_view bad_shape_view = primitive_view;
  bad_shape_view.shape[1] = 3;
  rtdl_buffer* bad_shape_buffer = NULL;
  if (p_rtdl_buffer_import(context, &bad_shape_view, &bad_shape_buffer) != RTDL_STATUS_OK ||
      bad_shape_buffer == NULL) {
    return 13;
  }
  rtdl_index_desc bad_shape_desc = index_desc;
  bad_shape_desc.primitives = bad_shape_buffer;
  rtdl_index* bad_index = NULL;
  if (require_status(
          "bad_index_shape_rejected",
          p_rtdl_index_build(context, &bad_shape_desc, &bad_index),
          RTDL_STATUS_ERROR_INVALID_ARGUMENT) ||
      bad_index != NULL) {
    return 14;
  }
  p_rtdl_buffer_destroy(bad_shape_buffer);

  float query_payload[4] = {0.25f, 0.25f, 0.75f, 0.75f};
  rtdl_buffer_view bad_stride_view = make_f32_aabb2_view(query_payload, 1u);
  bad_stride_view.strides[0] = (int64_t)(5 * sizeof(float));
  rtdl_buffer* bad_stride_buffer = NULL;
  if (p_rtdl_buffer_import(context, &bad_stride_view, &bad_stride_buffer) != RTDL_STATUS_OK ||
      bad_stride_buffer == NULL) {
    return 15;
  }
  rtdl_query_desc bad_stride_query;
  memset(&bad_stride_query, 0, sizeof(bad_stride_query));
  bad_stride_query.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  bad_stride_query.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  bad_stride_query.query_kind = RTDL_QUERY_AABB_OVERLAP;
  bad_stride_query.inputs = bad_stride_buffer;
  bad_stride_query.input_count = 1u;
  rtdl_buffer* bad_result = NULL;
  if (require_status(
          "bad_query_stride_rejected",
          p_rtdl_query_execute(context, index, &bad_stride_query, &bad_result),
          RTDL_STATUS_ERROR_INVALID_ARGUMENT) ||
      bad_result != NULL) {
    return 16;
  }
  p_rtdl_buffer_destroy(bad_stride_buffer);

  rtdl_buffer_view zero_view = make_f32_aabb2_view(NULL, 0u);
  rtdl_buffer* zero_primitives = NULL;
  rtdl_buffer* zero_queries = NULL;
  if (p_rtdl_buffer_import(context, &zero_view, &zero_primitives) != RTDL_STATUS_OK ||
      p_rtdl_buffer_import(context, &zero_view, &zero_queries) != RTDL_STATUS_OK) {
    return 17;
  }
  rtdl_index_desc zero_index_desc = index_desc;
  zero_index_desc.primitives = zero_primitives;
  zero_index_desc.primitive_count = 0u;
  rtdl_index* zero_index = NULL;
  if (p_rtdl_index_build(context, &zero_index_desc, &zero_index) != RTDL_STATUS_OK ||
      zero_index == NULL) {
    return 18;
  }
  rtdl_query_desc zero_query_desc;
  memset(&zero_query_desc, 0, sizeof(zero_query_desc));
  zero_query_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  zero_query_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  zero_query_desc.query_kind = RTDL_QUERY_AABB_OVERLAP;
  zero_query_desc.inputs = zero_queries;
  zero_query_desc.input_count = 0u;
  rtdl_buffer* zero_result = NULL;
  if (p_rtdl_query_execute(context, zero_index, &zero_query_desc, &zero_result) != RTDL_STATUS_OK ||
      zero_result == NULL) {
    return 19;
  }
  rtdl_buffer_view zero_result_view;
  memset(&zero_result_view, 0, sizeof(zero_result_view));
  if (p_rtdl_buffer_export(zero_result, &zero_result_view) != RTDL_STATUS_OK ||
      zero_result_view.dtype != RTDL_DTYPE_U64 || zero_result_view.shape[0] != 0 ||
      zero_result_view.shape[1] != 2 || zero_result_view.byte_count != 0u) {
    return 20;
  }
  CASE_OK("zero_count_empty_result_ok");

  p_rtdl_buffer_destroy(zero_result);
  p_rtdl_index_destroy(zero_index);
  p_rtdl_buffer_destroy(zero_queries);
  p_rtdl_buffer_destroy(zero_primitives);
  p_rtdl_index_destroy(index);
  p_rtdl_buffer_destroy(primitive_buffer);
  p_rtdl_context_destroy(context);
  rtdl_test_close(library);
  printf("validated_layout_cases=%d\n", 3);
  return 0;
}
'''


def compile_and_run_layout_client(root: Path) -> dict[str, Any]:
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
        shared_library = tmpdir / ("rtdl_c_api_layout" + _shared_suffix())
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

        client_source = tmpdir / "rtdl_c_abi_aabb2_layout_validation.c"
        client_exe = tmpdir / ("rtdl_c_abi_aabb2_layout_validation" + _exe_suffix())
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


def build_packet(root: Path = Path("."), *, run_compile: bool = False) -> dict[str, Any]:
    header = (root / HEADER).read_text(encoding="utf-8")
    source = (root / SOURCE).read_text(encoding="utf-8")
    client_source = _client_source()
    client_result = compile_and_run_layout_client(root) if run_compile else None
    stdout = ""
    if client_result and client_result.get("client_run"):
        stdout = str(client_result["client_run"].get("stdout") or "")
    validated_cases = {marker: marker in stdout for marker in CASE_MARKERS}
    checks = {
        "header_declares_buffer_shape_and_strides": "shape[8]" in header and "strides[8]" in header,
        "source_requires_two_dimensional_aabb2": "view.ndim == 2u" in source
        and "view.shape[1] == 4" in source,
        "source_requires_contiguous_f32_strides": "view.strides[0]" in source
        and "view.strides[1]" in source
        and "row_bytes" in source,
        "source_allows_zero_count_without_pointer_arithmetic": "desc->primitive_count != 0u" in source,
        "client_source_covers_layout_cases": all(marker in client_source for marker in CASE_MARKERS),
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
                "runtime_validated_layout_cases": all(validated_cases.values()),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4567 / V3 M168",
        "status": "c_abi_aabb2_layout_validation_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "case_markers": CASE_MARKERS,
        "validated_cases": validated_cases,
        "client_result": client_result,
        "claim_boundary": {
            "general_strided_buffer_support": False,
            "device_buffer_query_supported": False,
            "optix_embree_c_abi_query_supported": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4567 aligns the C ABI host AABB2 implementation with its "
            "documented contiguous `[count, 4]` contract: bad shape and stride "
            "metadata now fail closed, while zero-count inputs produce an empty "
            "host U64 pair buffer without pointer arithmetic on null data."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4567 / V3 M168 C ABI AABB2 Layout Validation",
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
            "- This validates only the host F32 AABB2 contiguous layout contract.",
            "- It does not add general strided-buffer, device-buffer, OptiX/Embree C ABI, or release support.",
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
