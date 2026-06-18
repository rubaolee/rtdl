from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_cmake_prefix_stage.goal4600.v1"
OUT_JSON = Path("docs/reports/goal4600_v3_0_m201_c_abi_cmake_prefix_stage_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4600_v3_0_m201_c_abi_cmake_prefix_stage_2026-06-17.md")
MAKEFILE = Path("Makefile")
CMAKE_CONFIG = Path("packaging/rtdl-c-api-config.cmake")
STAGING_CONTRACT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("docs/history/v4_preparatory_embedding/examples/embedding/README.md")
DOCTOR = Path("scripts/rtdl_source_tree_doctor.py")
DOCTOR_DOC = Path("docs/learn/source_tree_doctor.md")
DEFAULT_TEST_PREFIX = "/opt/rtdl"


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _exe_suffix() -> str:
    return ".exe" if os.name == "nt" else ""


def _consumer_source() -> str:
    return "\n".join(
        [
            '#include "rtdl/rtdl.h"',
            "#include <stdio.h>",
            "",
            "int main(void) {",
            "  if (!rtdl_abi_is_compatible(",
            "          RTDL_ABI_VERSION_MAJOR,",
            "          RTDL_ABI_VERSION_MINOR,",
            "          RTDL_ABI_VERSION_PATCH)) {",
            "    return 2;",
            "  }",
            "  rtdl_context_desc desc = {0};",
            "  desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;",
            "  desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;",
            "  desc.backend = RTDL_BACKEND_CPU;",
            "  rtdl_context* context = 0;",
            "  rtdl_status status = rtdl_context_create(&desc, &context);",
            "  if (status != RTDL_STATUS_OK || context == 0) {",
            "    return 3;",
            "  }",
            "  printf(\"cmake_direct_link_ok %u.%u.%u %s\\n\",",
            "         rtdl_abi_version_major(),",
            "         rtdl_abi_version_minor(),",
            "         rtdl_abi_version_patch(),",
            "         rtdl_status_string(status));",
            "  rtdl_context_destroy(context);",
            "  return 0;",
            "}",
            "",
        ]
    )


def _consumer_cmakelists() -> str:
    return "\n".join(
        [
            "cmake_minimum_required(VERSION 3.16)",
            "project(rtdl_c_api_cmake_consumer C)",
            "find_package(rtdl-c-api CONFIG REQUIRED)",
            "add_executable(rtdl_cmake_consumer main.c)",
            "target_link_libraries(rtdl_cmake_consumer PRIVATE rtdl::c_api)",
            "",
        ]
    )


def run_cmake_prefix_stage_smoke(root: Path) -> dict[str, Any]:
    make = shutil.which("make")
    cmake = shutil.which("cmake")
    result: dict[str, Any] = {
        "make": make,
        "cmake": cmake,
        "stage_root": None,
        "prefix": DEFAULT_TEST_PREFIX,
        "prefix_dir": None,
        "make_result": None,
        "configure_result": None,
        "build_result": None,
        "run_result": None,
        "ok": False,
    }
    if make is None or cmake is None:
        return result
    with tempfile.TemporaryDirectory(prefix="rtdl_c_api_cmake_prefix_") as tmp:
        tmpdir = Path(tmp)
        stage_root = tmpdir / "stage"
        project_dir = tmpdir / "consumer"
        build_dir = tmpdir / "build"
        prefix_dir = stage_root / DEFAULT_TEST_PREFIX.strip("/")
        result["stage_root"] = stage_root.as_posix()
        result["prefix_dir"] = prefix_dir.as_posix()
        make_completed = subprocess.run(
            [
                make,
                "stage-c-api-prefix",
                f"C_API_PREFIX_STAGE_ROOT={stage_root.as_posix()}",
                f"C_API_PREFIX={DEFAULT_TEST_PREFIX}",
            ],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        result["make_result"] = {
            "command": [
                make,
                "stage-c-api-prefix",
                f"C_API_PREFIX_STAGE_ROOT={stage_root.as_posix()}",
                f"C_API_PREFIX={DEFAULT_TEST_PREFIX}",
            ],
            "returncode": make_completed.returncode,
            "ok": make_completed.returncode == 0,
            "stdout_tail": _tail(make_completed.stdout),
            "stderr_tail": _tail(make_completed.stderr),
        }
        if make_completed.returncode != 0:
            return result
        project_dir.mkdir()
        (project_dir / "CMakeLists.txt").write_text(_consumer_cmakelists(), encoding="utf-8")
        (project_dir / "main.c").write_text(_consumer_source(), encoding="utf-8")
        configure_command = [
            cmake,
            "-S",
            str(project_dir),
            "-B",
            str(build_dir),
            f"-DCMAKE_PREFIX_PATH={prefix_dir.as_posix()}",
        ]
        configure_completed = subprocess.run(
            configure_command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        result["configure_result"] = {
            "command": configure_command,
            "returncode": configure_completed.returncode,
            "ok": configure_completed.returncode == 0,
            "stdout_tail": _tail(configure_completed.stdout),
            "stderr_tail": _tail(configure_completed.stderr),
        }
        if configure_completed.returncode != 0:
            return result
        build_command = [cmake, "--build", str(build_dir)]
        build_completed = subprocess.run(
            build_command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        result["build_result"] = {
            "command": build_command,
            "returncode": build_completed.returncode,
            "ok": build_completed.returncode == 0,
            "stdout_tail": _tail(build_completed.stdout),
            "stderr_tail": _tail(build_completed.stderr),
        }
        if build_completed.returncode != 0:
            return result
        exe = build_dir / ("rtdl_cmake_consumer" + _exe_suffix())
        run_env = os.environ.copy()
        if os.name == "nt":
            run_env["PATH"] = str(prefix_dir / "lib") + os.pathsep + run_env.get("PATH", "")
        elif os.uname().sysname == "Darwin":
            run_env["DYLD_LIBRARY_PATH"] = str(prefix_dir / "lib") + os.pathsep + run_env.get("DYLD_LIBRARY_PATH", "")
        else:
            run_env["LD_LIBRARY_PATH"] = str(prefix_dir / "lib") + os.pathsep + run_env.get("LD_LIBRARY_PATH", "")
        run_completed = subprocess.run(
            [str(exe)],
            cwd=root,
            env=run_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        result["run_result"] = {
            "command": [exe.as_posix()],
            "returncode": run_completed.returncode,
            "ok": run_completed.returncode == 0,
            "stdout": run_completed.stdout.strip(),
            "stderr_tail": _tail(run_completed.stderr),
        }
    result["ok"] = (
        result["make_result"]["ok"]
        and result["configure_result"]["ok"]
        and result["build_result"]["ok"]
        and result["run_result"]["ok"]
        and result["run_result"]["stdout"] == "cmake_direct_link_ok 0.1.3 ok"
    )
    return result


def build_packet(root: Path = Path("."), *, run_smoke: bool = False) -> dict[str, Any]:
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    cmake_config = (root / CMAKE_CONFIG).read_text(encoding="utf-8")
    staging = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    doctor = (root / DOCTOR).read_text(encoding="utf-8")
    doctor_doc = (root / DOCTOR_DOC).read_text(encoding="utf-8")
    smoke = run_cmake_prefix_stage_smoke(root) if run_smoke else None
    checks = {
        "cmake_config_is_relocatable": "CMAKE_CURRENT_LIST_DIR" in cmake_config
        and "_RTDL_C_API_PREFIX" in cmake_config,
        "cmake_config_exports_imported_target": "add_library(rtdl::c_api SHARED IMPORTED)" in cmake_config
        and "INTERFACE_INCLUDE_DIRECTORIES" in cmake_config,
        "makefile_stages_cmake_config": "lib/cmake/rtdl-c-api" in makefile
        and "$(C_API_CMAKE_CONFIG)" in makefile,
        "staging_contract_documents_cmake_config": "find_package(rtdl-c-api CONFIG REQUIRED)" in staging
        and "CMAKE_PREFIX_PATH" in staging,
        "embedding_readme_documents_cmake_config": "CMake package config" in embedding
        and "target_link_libraries(consumer PRIVATE rtdl::c_api)" in embedding,
        "doctor_checks_cmake_metadata_presence": "rtdl-c-api-config.cmake" in doctor
        and "pkg-config and CMake metadata" in doctor,
        "doctor_doc_names_cmake_metadata_boundary": "pkg-config and CMake\n  metadata" in doctor_doc
        and "it does not run\n  CMake" in doctor_doc,
    }
    if smoke is not None:
        checks.update(
            {
                "make_prefix_stage_ok": bool(smoke["make_result"] and smoke["make_result"]["ok"]),
                "cmake_available": bool(smoke["cmake"]),
                "cmake_configure_ok": bool(smoke["configure_result"] and smoke["configure_result"]["ok"]),
                "cmake_build_ok": bool(smoke["build_result"] and smoke["build_result"]["ok"]),
                "cmake_consumer_runs": bool(
                    smoke["run_result"]
                    and smoke["run_result"]["ok"]
                    and smoke["run_result"]["stdout"] == "cmake_direct_link_ok 0.1.3 ok"
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4600 / V3 M201",
        "status": "c_abi_cmake_prefix_stage_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "cmake_prefix_stage_smoke": smoke,
        "claim_boundary": {
            "cmake_prefix_stage_authorized": not failed,
            "system_install_authorized": False,
            "package_manager_artifact_authorized": False,
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4600 adds relocatable CMake package metadata to the C ABI "
            "stage and prefix-stage layouts. The pod evidence stages RTDL under "
            "a temporary `/opt/rtdl` prefix, configures an external CMake "
            "consumer with `find_package(rtdl-c-api CONFIG REQUIRED)`, builds it "
            "against the imported `rtdl::c_api` target, and runs it against the "
            "staged shared library. This authorizes CMake prefix-stage consumption "
            "only, not a system install, package-manager artifact, packaged SDK, "
            "stable ABI, or release claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["cmake_prefix_stage_smoke"] or {}
    lines = [
        "# Goal4600 / V3 M201 C ABI CMake Prefix Stage",
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
        f"- CMake: `{smoke.get('cmake')}`",
        f"- Prefix dir: `{smoke.get('prefix_dir')}`",
        f"- Output: `{(smoke.get('run_result') or {}).get('stdout')}`",
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
            "- This validates CMake prefix-stage consumption only.",
            "- It does not authorize a system install, package-manager artifact, packaged SDK, stable ABI, or release claim.",
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
