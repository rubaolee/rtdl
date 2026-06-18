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


PACKET_VERSION = "rtdl.v3_0.c_abi_host_external_runtime.goal4591.v1"
OUT_JSON = Path("docs/reports/goal4591_v3_0_m192_c_abi_host_external_runtime_gate_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4591_v3_0_m192_c_abi_host_external_runtime_gate_2026-06-17.md")
HEADER = Path("docs/history/v4_preparatory_embedding/staging/include/rtdl/rtdl.h")
SOURCE_FILE = Path("src/native/rtdl_c_api.cpp")
C_ABI_DOC = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_draft.md")
OWNERSHIP_DOC = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_ownership_threading_contract.md")
STAGING_CONTRACT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("docs/history/v4_preparatory_embedding/examples/embedding/README.md")
MAKEFILE = Path("Makefile")
EXAMPLE = Path("docs/history/v4_preparatory_embedding/examples/embedding/c_api_host_runtime_client.c")
CASE_MARKERS = (
    "host_external_runtime_metadata_ok",
    "malformed_host_runtime_rejected",
    "cuda_runtime_rejected",
)


def _library_env(shared_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    if os.name == "nt":
        env["PATH"] = str(shared_dir) + os.pathsep + env.get("PATH", "")
    elif os.uname().sysname == "Darwin":
        env["DYLD_LIBRARY_PATH"] = str(shared_dir) + os.pathsep + env.get("DYLD_LIBRARY_PATH", "")
    else:
        env["LD_LIBRARY_PATH"] = str(shared_dir) + os.pathsep + env.get("LD_LIBRARY_PATH", "")
    return env


def compile_and_run_host_runtime_client(root: Path) -> dict[str, Any]:
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

        client_exe = tmpdir / ("rtdl_c_api_host_runtime_client" + _exe_suffix())
        client_command = [
            c_compiler,
            "-std=c11",
            "-I",
            str(root / "include"),
            str(root / EXAMPLE),
            "-L",
            str(tmpdir),
            "-lrtdl_c_api",
            "-o",
            str(client_exe),
        ]
        if os.name != "nt":
            client_command.insert(-2, f"-Wl,-rpath,{tmpdir}")
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
            "stdout": run_completed.stdout,
            "stderr_tail": _stderr_tail(run_completed.stderr),
        }
        result["ok"] = run_completed.returncode == 0
    return result


def _runtime_cases(stdout: str) -> dict[str, bool]:
    return {marker: f"case {marker}: ok" in stdout for marker in CASE_MARKERS}


def build_packet(root: Path = Path("."), *, run_compile: bool = False) -> dict[str, Any]:
    header = (root / HEADER).read_text(encoding="utf-8")
    source = (root / SOURCE_FILE).read_text(encoding="utf-8")
    c_abi = (root / C_ABI_DOC).read_text(encoding="utf-8")
    ownership = (root / OWNERSHIP_DOC).read_text(encoding="utf-8")
    staging = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    example = (root / EXAMPLE).read_text(encoding="utf-8")
    client_result = compile_and_run_host_runtime_client(root) if run_compile else None
    stdout = ""
    if client_result and client_result["client_run"]:
        stdout = str(client_result["client_run"]["stdout"])
    runtime_cases = _runtime_cases(stdout)
    checks = {
        "header_documents_host_only_external_runtime": "accepts host runtime metadata only" in header
        and "external stream semantics remain unsupported" in header,
        "source_accepts_host_runtime_metadata": "context->desc.external_runtime = *runtime" in source
        and "RTDL_DEVICE_HOST" in source,
        "source_rejects_non_host_runtime": "only host external runtime metadata is supported" in source,
        "source_rejects_malformed_host_runtime": "requires device_id 0 or -1 and null context/stream handles"
        in source,
        "c_abi_doc_names_goal4591_and_boundary": "Goal4591 adds" in c_abi
        and "CUDA/HIP/Metal/Vulkan runtime handles remain unsupported" in c_abi,
        "ownership_doc_names_no_runtime_ownership_transfer": "does not take ownership" in ownership
        and "host runtime metadata" in ownership,
        "example_validates_success_and_rejections": all(marker in example for marker in CASE_MARKERS)
        and "validated_host_external_runtime_cases=3" in example,
        "stage_target_copies_host_runtime_example": "c_api_host_runtime_client.c" in makefile,
        "staging_contract_lists_host_runtime_example": "examples/c_api_host_runtime_client.c" in staging,
        "embedding_readme_documents_host_runtime_example": "c_api_host_runtime_client.c" in embedding
        and "validated_host_external_runtime_cases=3" in embedding,
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
        "goal": "Goal4591 / V3 M192",
        "status": "c_abi_host_external_runtime_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "validated_cases": runtime_cases,
        "client_result": client_result,
        "support_matrix": {
            "host_external_runtime_metadata": "validated",
            "malformed_host_runtime": "rejected_invalid_argument",
            "cuda_external_runtime": "rejected_unsupported",
            "external_cuda_stream_semantics": "blocked",
            "optix_embree_c_abi_runtime": "blocked",
            "device_buffer_c_abi": "blocked",
        },
        "claim_boundary": {
            "external_cuda_stream_authorized": False,
            "optix_embree_c_abi_runtime_authorized": False,
            "device_buffer_c_abi_authorized": False,
            "stable_abi_authorized": False,
            "packaged_sdk_authorized": False,
            "performance_wording_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4591 turns `rtdl_context_set_external_runtime` from an all-"
            "unsupported placeholder into a narrow, validated host-runtime "
            "metadata path. The C ABI now accepts `RTDL_DEVICE_HOST` metadata "
            "with null context/stream handles, rejects malformed host metadata, "
            "and continues to reject CUDA runtime handles. This advances the "
            "control-plane embedding boundary without authorizing CUDA stream, "
            "OptiX/Embree runtime, device-buffer, stable ABI, SDK, release, or "
            "performance claims."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4591 / V3 M192 C ABI Host External Runtime Gate",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
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
            "- Host runtime metadata is validated for the current C ABI proof.",
            "- CUDA streams, OptiX/Embree C ABI runtime adoption, device-buffer routes, stable ABI, packaged SDK, release, and performance wording remain blocked.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-runtime", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_compile=not args.no_runtime)
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
