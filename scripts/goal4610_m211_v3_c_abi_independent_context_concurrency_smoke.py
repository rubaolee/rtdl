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
    _cxx_compiler,
    _exe_suffix,
    _run_compile,
    _shared_suffix,
    _stderr_tail,
)


PACKET_VERSION = "rtdl.v3_0.c_abi_independent_context_concurrency.goal4610.v1"
OUT_JSON = Path(
    "docs/reports/goal4610_v3_0_m211_c_abi_independent_context_concurrency_smoke_2026-06-17.json"
)
OUT_REPORT = Path(
    "docs/reports/goal4610_v3_0_m211_c_abi_independent_context_concurrency_smoke_2026-06-17.md"
)
HEADER = Path("include/rtdl/rtdl.h")
SOURCE_FILE = Path("src/native/rtdl_c_api.cpp")
OWNERSHIP_DOC = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_ownership_threading_contract.md")
ARCHITECTURE_DOC = Path("docs/history/v4_preparatory_embedding/v3_0_embeddability_architecture_strategy.md")
BINDING_MATRIX = Path("docs/history/v4_preparatory_embedding/v3_0_binding_and_device_interop_matrix.md")
BENCHMARK_INDEX = Path("docs/learn/benchmark_evidence_index.md")
THREAD_COUNT = 8
ITERATIONS_PER_THREAD = 64


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _library_env(shared_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    if os.name == "nt":
        env["PATH"] = str(shared_dir) + os.pathsep + env.get("PATH", "")
    elif os.uname().sysname == "Darwin":
        env["DYLD_LIBRARY_PATH"] = str(shared_dir) + os.pathsep + env.get("DYLD_LIBRARY_PATH", "")
    else:
        env["LD_LIBRARY_PATH"] = str(shared_dir) + os.pathsep + env.get("LD_LIBRARY_PATH", "")
    return env


def _client_source(thread_count: int = THREAD_COUNT, iterations: int = ITERATIONS_PER_THREAD) -> str:
    return f"""
#include "rtdl/rtdl.h"

#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <thread>
#include <vector>

static rtdl_buffer_view host_f32_aabb2_view(float* data, uint64_t count) {{
  rtdl_buffer_view view;
  std::memset(&view, 0, sizeof(view));
  view.data = data;
  view.byte_count = count * 4u * sizeof(float);
  view.device_type = RTDL_DEVICE_HOST;
  view.dtype = RTDL_DTYPE_F32;
  view.ndim = 2u;
  view.shape[0] = static_cast<int64_t>(count);
  view.shape[1] = 4;
  view.strides[0] = static_cast<int64_t>(4u * sizeof(float));
  view.strides[1] = static_cast<int64_t>(sizeof(float));
  return view;
}}

static bool run_one_query(int worker_id, int iteration) {{
  rtdl_context_desc context_desc;
  std::memset(&context_desc, 0, sizeof(context_desc));
  context_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
  context_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
  context_desc.backend = RTDL_BACKEND_CPU;

  rtdl_context* context = nullptr;
  rtdl_buffer* primitive_buffer = nullptr;
  rtdl_buffer* query_buffer = nullptr;
  rtdl_index* index = nullptr;
  rtdl_buffer* result_buffer = nullptr;

  bool ok = rtdl_context_create(&context_desc, &context) == RTDL_STATUS_OK && context != nullptr;
  float shift = static_cast<float>(worker_id * 1000 + iteration);
  float primitives[8] = {{shift, shift, shift + 1.0f, shift + 1.0f,
                         shift + 10.0f, shift + 10.0f, shift + 11.0f, shift + 11.0f}};
  float queries[4] = {{shift + 0.25f, shift + 0.25f, shift + 0.75f, shift + 0.75f}};

  if (ok) {{
    rtdl_buffer_view primitive_view = host_f32_aabb2_view(primitives, 2);
    rtdl_buffer_view query_view = host_f32_aabb2_view(queries, 1);
    ok = rtdl_buffer_import(context, &primitive_view, &primitive_buffer) == RTDL_STATUS_OK &&
         rtdl_buffer_import(context, &query_view, &query_buffer) == RTDL_STATUS_OK;
  }}
  if (ok) {{
    rtdl_index_desc index_desc;
    std::memset(&index_desc, 0, sizeof(index_desc));
    index_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
    index_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
    index_desc.primitive_kind = RTDL_PRIMITIVE_AABB2;
    index_desc.primitives = primitive_buffer;
    index_desc.primitive_count = 2;
    ok = rtdl_index_build(context, &index_desc, &index) == RTDL_STATUS_OK && index != nullptr;
  }}
  if (primitive_buffer != nullptr) {{
    rtdl_buffer_destroy(primitive_buffer);
    primitive_buffer = nullptr;
  }}
  if (ok) {{
    rtdl_query_desc query_desc;
    std::memset(&query_desc, 0, sizeof(query_desc));
    query_desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
    query_desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
    query_desc.query_kind = RTDL_QUERY_AABB_OVERLAP;
    query_desc.inputs = query_buffer;
    query_desc.input_count = 1;
    ok = rtdl_query_execute(context, index, &query_desc, &result_buffer) == RTDL_STATUS_OK &&
         result_buffer != nullptr;
  }}
  if (ok) {{
    rtdl_buffer_view result_view;
    std::memset(&result_view, 0, sizeof(result_view));
    ok = rtdl_buffer_export(result_buffer, &result_view) == RTDL_STATUS_OK &&
         result_view.shape[0] == 1 && result_view.shape[1] == 2 && result_view.data != nullptr;
    uint64_t* rows = static_cast<uint64_t*>(result_view.data);
    ok = ok && rows[0] == 0u && rows[1] == 0u;
  }}

  rtdl_buffer_destroy(result_buffer);
  rtdl_index_destroy(index);
  rtdl_buffer_destroy(query_buffer);
  rtdl_context_destroy(context);
  return ok;
}}

int main() {{
  std::atomic<int> failures{{0}};
  std::vector<std::thread> workers;
  workers.reserve({thread_count});
  for (int worker = 0; worker < {thread_count}; ++worker) {{
    workers.emplace_back([worker, &failures]() {{
      for (int iteration = 0; iteration < {iterations}; ++iteration) {{
        if (!run_one_query(worker, iteration)) {{
          failures.fetch_add(1);
        }}
      }}
    }});
  }}
  for (std::thread& worker : workers) {{
    worker.join();
  }}
  if (failures.load() != 0) {{
    std::fprintf(stderr, "independent context concurrency failures=%d\\n", failures.load());
    return 1;
  }}
  std::printf("validated_independent_context_threads={thread_count} iterations={iterations}\\n");
  return 0;
}}
"""


def compile_and_run_concurrency_smoke(root: Path) -> dict[str, Any]:
    cxx_compiler = _cxx_compiler()
    result: dict[str, Any] = {
        "cxx_compiler": cxx_compiler,
        "shared_library": None,
        "client_compile": None,
        "client_run": None,
        "ok": False,
    }
    if cxx_compiler is None:
        return result

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        tmpdir = Path(tmp)
        shared_library = tmpdir / ("librtdl_c_api" + _shared_suffix())
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

        source = tmpdir / "rtdl_c_api_independent_context_concurrency_smoke.cpp"
        source.write_text(_client_source(), encoding="utf-8")
        client_exe = tmpdir / ("rtdl_c_api_independent_context_concurrency_smoke" + _exe_suffix())
        client_command = [
            cxx_compiler,
            "-std=c++17",
            "-I",
            str(root / "include"),
            str(source),
            "-L",
            str(tmpdir),
            "-lrtdl_c_api",
            "-o",
            str(client_exe),
        ]
        if os.name != "nt":
            client_command.insert(-2, f"-Wl,-rpath,{tmpdir}")
            client_command.append("-pthread")
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
            [str(client_exe)],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=_library_env(tmpdir),
        )
        result["client_run"] = {
            "command": [str(client_exe)],
            "returncode": run_completed.returncode,
            "ok": run_completed.returncode == 0,
            "stdout": run_completed.stdout.strip(),
            "stderr_tail": _tail(run_completed.stderr),
        }
        result["ok"] = (
            run_completed.returncode == 0
            and run_completed.stdout.strip()
            == f"validated_independent_context_threads={THREAD_COUNT} iterations={ITERATIONS_PER_THREAD}"
        )
    return result


def build_packet(root: Path = Path("."), *, run_smoke: bool = False) -> dict[str, Any]:
    header = (root / HEADER).read_text(encoding="utf-8")
    source = (root / SOURCE_FILE).read_text(encoding="utf-8")
    ownership = (root / OWNERSHIP_DOC).read_text(encoding="utf-8")
    architecture = (root / ARCHITECTURE_DOC).read_text(encoding="utf-8")
    binding = (root / BINDING_MATRIX).read_text(encoding="utf-8")
    index = (root / BENCHMARK_INDEX).read_text(encoding="utf-8")
    smoke = compile_and_run_concurrency_smoke(root) if run_smoke else None
    checks = {
        "header_points_to_ownership_threading_contract": "Current ownership and threading rules are documented" in header,
        "source_context_and_buffer_handles_are_instance_owned": "struct rtdl_context" in source
        and "struct rtdl_buffer" in source
        and "rtdl_context* context" in source,
        "ownership_doc_names_goal4610_independent_context_smoke": "Goal4610" in ownership
        and "Independent contexts with no shared imported buffers" in ownership,
        "ownership_doc_keeps_stable_thread_safety_blocked": "Stable thread-safety wording remains blocked" in ownership
        and "shared-handle misuse" in ownership,
        "architecture_doc_current_to_goal4610": "As of Goal4610" in architecture
        and "Independent-context concurrency smoke" in architecture,
        "binding_matrix_names_independent_context_concurrency": "Independent-context host-route concurrency" in binding,
        "benchmark_index_links_goal4610": "Goal4610 C ABI independent-context concurrency smoke" in index,
    }
    if smoke is not None:
        checks.update(
            {
                "cxx_compiler_available": bool(smoke["cxx_compiler"]),
                "shared_library_build_ok": bool(smoke["shared_library"] and smoke["shared_library"]["ok"]),
                "client_compile_ok": bool(smoke["client_compile"] and smoke["client_compile"]["ok"]),
                "client_run_ok": bool(smoke["client_run"] and smoke["client_run"]["ok"]),
                "independent_context_concurrency_stdout_matches": smoke["ok"],
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4610 / V3 M211",
        "status": "c_abi_independent_context_concurrency_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "concurrency_smoke": smoke,
        "support_matrix": {
            "independent_context_host_aabb2_concurrency": "validated_source_tree_smoke",
            "same_context_concurrent_mutation": "requires_external_synchronization",
            "shared_handle_destroy_while_in_use": "blocked_requires_external_synchronization",
            "backend_concurrency_matrix": "blocked_until_each_backend_route_is_tested",
            "stable_thread_safety_wording": "blocked",
        },
        "claim_boundary": {
            "independent_context_host_route_concurrency_authorized": not failed,
            "same_context_concurrent_mutation_authorized": False,
            "shared_handle_concurrency_authorized": False,
            "backend_concurrency_matrix_authorized": False,
            "stable_thread_safety_authorized": False,
            "release_authorized": False,
            "performance_wording_authorized": False,
        },
        "conclusion": (
            "Goal4610 validates a narrow independent-context concurrency smoke "
            "for the current host AABB2 C ABI route. The generated C++ client "
            "starts multiple host threads, each with its own context, buffers, "
            "index, query, and teardown loop, and checks deterministic result "
            "rows. This authorizes independent-context host-route smoke only; "
            "same-handle concurrent mutation, destroy-while-in-use, backend-wide "
            "thread-safety, stable thread-safety wording, release, and "
            "performance claims remain blocked."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["concurrency_smoke"] or {}
    run_result = smoke.get("client_run") or {}
    lines = [
        "# Goal4610 / V3 M211 C ABI Independent-Context Concurrency Smoke",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Smoke",
        "",
        f"- OK: `{smoke.get('ok')}`",
        f"- CXX: `{smoke.get('cxx_compiler')}`",
        f"- Output: `{run_result.get('stdout')}`",
        "",
        "## Support Matrix",
        "",
        "| Surface | Status |",
        "| --- | --- |",
    ]
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
            "- Independent contexts with no shared handles are validated for the current host AABB2 route only.",
            "- Same-context concurrent mutation, shared-handle concurrency, backend-wide concurrency, stable thread-safety wording, release, and performance claims remain blocked.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-smoke", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_smoke=not args.no_smoke)
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
