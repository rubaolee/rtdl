from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_archive_cmake_smoke.goal4602.v1"
OUT_JSON = Path("docs/reports/goal4602_v3_0_m203_c_abi_archive_cmake_smoke_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4602_v3_0_m203_c_abi_archive_cmake_smoke_2026-06-17.md")
MAKEFILE = Path("Makefile")
STAGING_CONTRACT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("docs/history/v4_preparatory_embedding/examples/embedding/README.md")
STAGE_ARCHIVE_REPORT = Path("docs/reports/goal4587_v3_0_m188_c_abi_stage_archive_2026-06-17.json")
CMAKE_PREFIX_REPORT = Path("docs/reports/goal4600_v3_0_m201_c_abi_cmake_prefix_stage_2026-06-17.json")
ARCHIVE = Path("build/rtdl-c-api-stage-0.1.3.tar.gz")
ARCHIVE_ROOT = "rtdl-c-api-stage-0.1.3"


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
            "  printf(\"cmake_archive_direct_link_ok %u.%u.%u %s\\n\",",
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
            "project(rtdl_c_api_archive_cmake_consumer C)",
            "find_package(rtdl-c-api CONFIG REQUIRED)",
            "add_executable(rtdl_archive_cmake_consumer main.c)",
            "target_link_libraries(rtdl_archive_cmake_consumer PRIVATE rtdl::c_api)",
            "",
        ]
    )


def run_archive_cmake_smoke(root: Path) -> dict[str, Any]:
    make = shutil.which("make")
    cmake = shutil.which("cmake")
    archive = root / ARCHIVE
    result: dict[str, Any] = {
        "make": make,
        "cmake": cmake,
        "archive": archive.as_posix(),
        "make_result": None,
        "archive_exists": False,
        "archive_size_bytes": 0,
        "extract_dir": None,
        "cmake_config_exists": False,
        "configure_result": None,
        "build_result": None,
        "run_result": None,
        "ok": False,
    }
    if make is None or cmake is None:
        return result
    make_completed = subprocess.run(
        [make, "package-c-api-stage"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result["make_result"] = {
        "command": [make, "package-c-api-stage"],
        "returncode": make_completed.returncode,
        "ok": make_completed.returncode == 0,
        "stdout_tail": _tail(make_completed.stdout),
        "stderr_tail": _tail(make_completed.stderr),
    }
    result["archive_exists"] = archive.exists()
    result["archive_size_bytes"] = archive.stat().st_size if archive.exists() else 0
    if make_completed.returncode != 0 or not archive.exists():
        return result
    with tempfile.TemporaryDirectory(prefix="rtdl_c_api_archive_cmake_") as tmp:
        tmpdir = Path(tmp)
        extract_root = tmpdir / "extracted"
        project_dir = tmpdir / "consumer"
        build_dir = tmpdir / "build"
        shutil.unpack_archive(str(archive), str(extract_root))
        extracted = extract_root / ARCHIVE_ROOT
        result["extract_dir"] = extracted.as_posix()
        result["cmake_config_exists"] = (
            extracted / "lib" / "cmake" / "rtdl-c-api" / "rtdl-c-api-config.cmake"
        ).exists()
        project_dir.mkdir()
        (project_dir / "CMakeLists.txt").write_text(_consumer_cmakelists(), encoding="utf-8")
        (project_dir / "main.c").write_text(_consumer_source(), encoding="utf-8")
        configure_command = [
            cmake,
            "-S",
            str(project_dir),
            "-B",
            str(build_dir),
            f"-DCMAKE_PREFIX_PATH={extracted.as_posix()}",
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
        exe = build_dir / ("rtdl_archive_cmake_consumer" + _exe_suffix())
        run_env = os.environ.copy()
        if os.name == "nt":
            run_env["PATH"] = str(extracted / "lib") + os.pathsep + run_env.get("PATH", "")
        elif os.uname().sysname == "Darwin":
            run_env["DYLD_LIBRARY_PATH"] = str(extracted / "lib") + os.pathsep + run_env.get("DYLD_LIBRARY_PATH", "")
        else:
            run_env["LD_LIBRARY_PATH"] = str(extracted / "lib") + os.pathsep + run_env.get("LD_LIBRARY_PATH", "")
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
        and result["archive_exists"]
        and result["archive_size_bytes"] > 0
        and result["cmake_config_exists"]
        and result["configure_result"]["ok"]
        and result["build_result"]["ok"]
        and result["run_result"]["ok"]
        and result["run_result"]["stdout"] == "cmake_archive_direct_link_ok 0.1.3 ok"
    )
    return result


def _load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def build_packet(root: Path = Path("."), *, run_smoke: bool = False) -> dict[str, Any]:
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    staging = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    stage_archive = _load_json(root, STAGE_ARCHIVE_REPORT)
    cmake_prefix = _load_json(root, CMAKE_PREFIX_REPORT)
    smoke = run_archive_cmake_smoke(root) if run_smoke else None
    checks = {
        "makefile_archive_stages_cmake_config": "cp $(C_API_CMAKE_CONFIG) $(C_API_STAGE_DIR)/lib/cmake/rtdl-c-api" in makefile
        and "package-c-api-stage: stage-c-api" in makefile,
        "staging_contract_documents_archive_cmake_consumer": (
            "For a CMake consumer from the extracted source-tree archive" in staging
            and "rtdl-c-api-stage-0.1.3" in staging
        ),
        "embedding_readme_documents_archive_cmake_consumer": (
            "same CMake package config is present in the movable source-tree archive" in embedding
            and "rtdl-c-api-stage-0.1.3" in embedding
        ),
        "prior_archive_pkg_config_smoke_ok": stage_archive["stage_archive_smoke"]["ok"],
        "prior_prefix_cmake_smoke_ok": cmake_prefix["cmake_prefix_stage_smoke"]["ok"],
    }
    if smoke is not None:
        checks.update(
            {
                "make_package_stage_ok": bool(smoke["make_result"] and smoke["make_result"]["ok"]),
                "archive_exists_and_nonempty": bool(smoke["archive_exists"] and smoke["archive_size_bytes"] > 0),
                "archive_contains_cmake_config": smoke["cmake_config_exists"],
                "archive_cmake_configure_ok": bool(smoke["configure_result"] and smoke["configure_result"]["ok"]),
                "archive_cmake_build_ok": bool(smoke["build_result"] and smoke["build_result"]["ok"]),
                "archive_cmake_consumer_runs": bool(
                    smoke["run_result"]
                    and smoke["run_result"]["ok"]
                    and smoke["run_result"]["stdout"] == "cmake_archive_direct_link_ok 0.1.3 ok"
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4602 / V3 M203",
        "status": "c_abi_archive_cmake_smoke_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "archive_cmake_smoke": smoke,
        "claim_boundary": {
            "archive_cmake_stage_authorized": not failed,
            "system_install_authorized": False,
            "package_manager_artifact_authorized": False,
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4602 validates that the movable source-tree C ABI archive is "
            "consumable by an external CMake project after extraction. The smoke "
            "builds `package-c-api-stage`, unpacks `rtdl-c-api-stage-0.1.3.tar.gz`, "
            "configures an external consumer with `find_package(rtdl-c-api CONFIG "
            "REQUIRED)` via `CMAKE_PREFIX_PATH`, builds against `rtdl::c_api`, and "
            "runs against the extracted shared library. This authorizes archive "
            "CMake-stage consumption only; it is still not a system install, "
            "package-manager artifact, packaged SDK, stable ABI, or release claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["archive_cmake_smoke"] or {}
    lines = [
        "# Goal4602 / V3 M203 C ABI Archive CMake Smoke",
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
        f"- Extract dir: `{smoke.get('extract_dir')}`",
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
            "- This validates CMake consumption from the extracted source-tree stage archive only.",
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
