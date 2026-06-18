from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_example_client.goal4559.v1"
OUT_JSON = Path("docs/reports/goal4559_v3_0_m160_c_abi_example_client_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4559_v3_0_m160_c_abi_example_client_2026-06-17.md")
EXAMPLE = Path("examples/current/embedding/c_api_aabb2_overlap_client.c")


def _shared_suffix() -> str:
    if os.name == "nt":
        return ".dll"
    return ".dylib" if os.uname().sysname == "Darwin" else ".so"


def _exe_suffix() -> str:
    return ".exe" if os.name == "nt" else ""


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def run_example(root: Path) -> dict[str, Any]:
    make = shutil.which("make")
    cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    artifact = root / "build" / ("librtdl_c_api" + _shared_suffix())
    exe = root / "build" / ("rtdl_c_api_aabb2_overlap_client" + _exe_suffix())
    result: dict[str, Any] = {
        "make": make,
        "cc": cc,
        "artifact": artifact.as_posix(),
        "exe": exe.as_posix(),
        "make_result": None,
        "compile_result": None,
        "run_result": None,
        "ok": False,
    }
    if make is None or cc is None:
        return result
    make_completed = subprocess.run(
        [make, "build-c-api"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result["make_result"] = {
        "command": [make, "build-c-api"],
        "returncode": make_completed.returncode,
        "ok": make_completed.returncode == 0 and artifact.exists(),
        "stdout_tail": _tail(make_completed.stdout),
        "stderr_tail": _tail(make_completed.stderr),
    }
    if make_completed.returncode != 0 or not artifact.exists():
        return result
    command = [cc, "-std=c11", "-I", str(root / "include"), str(root / EXAMPLE), "-o", str(exe)]
    if os.name != "nt":
        command.append("-ldl")
    compile_completed = subprocess.run(
        command,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result["compile_result"] = {
        "command": command,
        "returncode": compile_completed.returncode,
        "ok": compile_completed.returncode == 0 and exe.exists(),
        "stdout_tail": _tail(compile_completed.stdout),
        "stderr_tail": _tail(compile_completed.stderr),
    }
    if compile_completed.returncode != 0 or not exe.exists():
        return result
    run_completed = subprocess.run(
        [str(exe), str(artifact)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result["run_result"] = {
        "command": [str(exe), str(artifact)],
        "returncode": run_completed.returncode,
        "ok": run_completed.returncode == 0 and "hit_count=1" in run_completed.stdout,
        "stdout": run_completed.stdout,
        "stderr_tail": _tail(run_completed.stderr),
    }
    result["ok"] = bool(result["run_result"]["ok"])
    return result


def build_packet(root: Path = Path("."), *, run_build: bool = False) -> dict[str, Any]:
    example = (root / EXAMPLE).read_text(encoding="utf-8")
    run_result = run_example(root) if run_build else None
    checks = {
        "example_exists": (root / EXAMPLE).exists(),
        "example_includes_public_header": '#include "rtdl/rtdl.h"' in example,
        "example_uses_dynamic_library_loading": "dlopen" in example and "LoadLibraryA" in example,
        "example_builds_aabb2_index": "RTDL_PRIMITIVE_AABB2" in example and "index_build" in example,
        "example_executes_overlap_query": "RTDL_QUERY_AABB_OVERLAP" in example and "query_execute" in example,
        "example_checks_expected_pair": "rows[0] != 0u" in example and "rows[1] != 0u" in example,
    }
    if run_result is not None:
        checks.update(
            {
                "make_available": bool(run_result["make"]),
                "cc_available": bool(run_result["cc"]),
                "make_build_ok": bool(run_result["make_result"] and run_result["make_result"]["ok"]),
                "example_compile_ok": bool(run_result["compile_result"] and run_result["compile_result"]["ok"]),
                "example_run_ok": bool(run_result["run_result"] and run_result["run_result"]["ok"]),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4559 / V3 M160",
        "status": "c_abi_example_client_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "run_result": run_result,
        "claim_boundary": {
            "packaged_sdk_released": False,
            "optix_backend_query_implemented": False,
            "embree_backend_query_implemented": False,
            "device_buffer_query_validated": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4559 promotes the C ABI host AABB2 overlap proof into a readable "
            "example client under `examples/current/embedding/`. Pod evidence builds "
            "`librtdl_c_api`, compiles the C example, runs it, and observes the "
            "expected single overlap pair. This is still a source-tree example, not "
            "a packaged SDK or OptiX/Embree/device-buffer claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    run_result = packet["run_result"] or {}
    lines = [
        "# Goal4559 / V3 M160 C ABI Example Client",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Run Result",
        "",
        f"- OK: `{run_result.get('ok')}`",
        f"- Executable: `{run_result.get('exe')}`",
        f"- Artifact: `{run_result.get('artifact')}`",
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
            "- This is a source-tree C client example for host AABB2 overlap only.",
            "- No packaged SDK, OptiX, Embree, device-buffer query, frozen ABI, or release claim is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-build", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_build=not args.no_build)
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
