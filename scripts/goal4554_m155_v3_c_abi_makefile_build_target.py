from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_makefile_build_target.goal4554.v1"
OUT_JSON = Path("docs/reports/goal4554_v3_0_m155_c_abi_makefile_build_target_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4554_v3_0_m155_c_abi_makefile_build_target_2026-06-17.md")
MAKEFILE = Path("Makefile")
SOURCE = Path("src/native/rtdl_c_api.cpp")


def _shared_suffix() -> str:
    if os.name == "nt":
        return ".dll"
    return ".dylib" if os.uname().sysname == "Darwin" else ".so"


def _artifact_path(root: Path) -> Path:
    return root / "build" / ("librtdl_c_api" + _shared_suffix())


def run_make_build(root: Path) -> dict[str, Any]:
    make = shutil.which("make")
    artifact = _artifact_path(root)
    result: dict[str, Any] = {
        "make": make,
        "command": None,
        "returncode": None,
        "ok": False,
        "stdout_tail": (),
        "stderr_tail": (),
        "artifact": artifact.as_posix(),
        "artifact_exists": False,
        "artifact_size_bytes": 0,
    }
    if make is None:
        result["stderr_tail"] = ("make not found",)
        return result
    completed = subprocess.run(
        [make, "build-c-api"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result.update(
        {
            "command": [make, "build-c-api"],
            "returncode": completed.returncode,
            "stdout_tail": tuple(completed.stdout.splitlines()[-12:]),
            "stderr_tail": tuple(completed.stderr.splitlines()[-12:]),
            "artifact_exists": artifact.exists(),
            "artifact_size_bytes": artifact.stat().st_size if artifact.exists() else 0,
        }
    )
    result["ok"] = completed.returncode == 0 and result["artifact_exists"] and result["artifact_size_bytes"] > 0
    return result


def build_packet(root: Path = Path("."), *, run_make: bool = False) -> dict[str, Any]:
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    source_text = (root / SOURCE).read_text(encoding="utf-8")
    make_result = run_make_build(root) if run_make else None
    checks = {
        "makefile_exists": (root / MAKEFILE).exists(),
        "c_api_source_exists": (root / SOURCE).exists(),
        "c_api_lib_name_declared": "C_API_LIB_NAME" in makefile,
        "build_c_api_target_declared": "\nbuild-c-api:" in makefile,
        "build_c_api_is_phony": "build-c-api" in makefile.split(".PHONY:", 1)[-1],
        "target_uses_public_header_include": "-Iinclude" in makefile,
        "target_exports_shared_symbols": "-DRTDL_BUILD_SHARED" in makefile,
        "target_builds_c_api_source": "src/native/rtdl_c_api.cpp" in makefile,
        "help_mentions_build_c_api": "build-c-api" in makefile and "V3 C ABI" in makefile,
        "source_uses_public_header": '#include "rtdl/rtdl.h"' in source_text,
    }
    if make_result is not None:
        checks.update(
            {
                "make_available": bool(make_result["make"]),
                "make_build_c_api_ok": bool(make_result["ok"]),
                "make_artifact_exists": bool(make_result["artifact_exists"]),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4554 / V3 M155",
        "status": "c_abi_makefile_build_target_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "make_result": make_result,
        "claim_boundary": {
            "backend_query_implemented": False,
            "binary_compatibility_frozen": False,
            "install_package_target_implemented": False,
            "dlpack_support_implemented": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4554 wires the V3 C ABI lifecycle stub into the normal Makefile "
            "front door via `make build-c-api`. The target builds a shared library "
            "from the app-agnostic `src/native/rtdl_c_api.cpp` source and public "
            "`include/rtdl/rtdl.h` header. This is a source-tree build target only; "
            "it does not implement backend query execution, package installation, "
            "DLPack, frozen compatibility, or release wording."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    make_result = packet["make_result"] or {}
    lines = [
        "# Goal4554 / V3 M155 C ABI Makefile Build Target",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Make Result",
        "",
        f"- Command: `{make_result.get('command')}`",
        f"- OK: `{make_result.get('ok')}`",
        f"- Artifact: `{make_result.get('artifact')}`",
        f"- Artifact bytes: `{make_result.get('artifact_size_bytes')}`",
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
            "- This is a source-tree Makefile build target for the lifecycle stub.",
            "- No backend query, install/package target, DLPack bridge, frozen ABI, or release claim is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-make", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_make=not args.no_make)
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
