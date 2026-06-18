from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_last_error_staged_example.goal4612.v1"
OUT_JSON = Path("docs/reports/goal4612_v3_0_m213_c_abi_last_error_staged_example_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4612_v3_0_m213_c_abi_last_error_staged_example_2026-06-17.md")
EXAMPLE = Path("docs/history/v4_preparatory_embedding/examples/embedding/c_api_last_error_client.c")
MAKEFILE = Path("Makefile")
STAGING_CONTRACT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("docs/history/v4_preparatory_embedding/examples/embedding/README.md")
BINDING_MATRIX = Path("docs/history/v4_preparatory_embedding/v3_0_binding_and_device_interop_matrix.md")
ARCHITECTURE_DOC = Path("docs/history/v4_preparatory_embedding/v3_0_embeddability_architecture_strategy.md")
BENCHMARK_INDEX = Path("docs/learn/benchmark_evidence_index.md")
STAGING_INVENTORY_SCRIPT = Path("scripts/goal4585_m186_v3_c_abi_staging_inventory_refresh.py")
ARCHIVE_C_EXAMPLE_SCRIPT = Path("scripts/goal4609_m210_v3_archive_stage_c_examples_smoke.py")
EXPECTED_MARKER = "validated_last_error_diagnostics_cases=7"


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _exe_suffix() -> str:
    return ".exe" if os.name == "nt" else ""


def _library_env(shared_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    if os.name == "nt":
        env["PATH"] = str(shared_dir) + os.pathsep + env.get("PATH", "")
    elif os.uname().sysname == "Darwin":
        env["DYLD_LIBRARY_PATH"] = str(shared_dir) + os.pathsep + env.get("DYLD_LIBRARY_PATH", "")
    else:
        env["LD_LIBRARY_PATH"] = str(shared_dir) + os.pathsep + env.get("LD_LIBRARY_PATH", "")
    return env


def _pkg_config_args(pkg_config: str, flag: str, root: Path, pc_dir: Path) -> dict[str, Any]:
    env = os.environ.copy()
    env["PKG_CONFIG_PATH"] = str(pc_dir)
    command = [pkg_config, flag, "rtdl-c-api"]
    completed = subprocess.run(
        command,
        cwd=root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "ok": completed.returncode == 0,
        "stdout": completed.stdout.strip(),
        "stderr_tail": _tail(completed.stderr),
    }


def run_staged_last_error_example(root: Path) -> dict[str, Any]:
    make = shutil.which("make")
    pkg_config = shutil.which("pkg-config")
    cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    stage = root / "build" / "c_api_stage"
    result: dict[str, Any] = {
        "make": make,
        "pkg_config": pkg_config,
        "cc": cc,
        "stage_dir": stage.as_posix(),
        "make_result": None,
        "cflags_result": None,
        "libs_result": None,
        "compile_result": None,
        "run_result": None,
        "ok": False,
    }
    if make is None or pkg_config is None or cc is None:
        return result

    make_completed = subprocess.run(
        [make, "stage-c-api"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result["make_result"] = {
        "command": [make, "stage-c-api"],
        "returncode": make_completed.returncode,
        "ok": make_completed.returncode == 0,
        "stdout_tail": _tail(make_completed.stdout),
        "stderr_tail": _tail(make_completed.stderr),
    }
    if make_completed.returncode != 0:
        return result

    pc_dir = stage / "lib" / "pkgconfig"
    cflags = _pkg_config_args(pkg_config, "--cflags", root, pc_dir)
    libs = _pkg_config_args(pkg_config, "--libs", root, pc_dir)
    result["cflags_result"] = cflags
    result["libs_result"] = libs
    if not cflags["ok"] or not libs["ok"]:
        return result

    source = stage / "examples" / "c_api_last_error_client.c"
    exe = stage / "examples" / ("rtdl_c_api_last_error_client" + _exe_suffix())
    compile_command = [
        cc,
        "-std=c11",
        *shlex.split(cflags["stdout"]),
        str(source),
        "-o",
        str(exe),
        *shlex.split(libs["stdout"]),
    ]
    compile_completed = subprocess.run(
        compile_command,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result["compile_result"] = {
        "command": compile_command,
        "returncode": compile_completed.returncode,
        "ok": compile_completed.returncode == 0,
        "stdout_tail": _tail(compile_completed.stdout),
        "stderr_tail": _tail(compile_completed.stderr),
    }
    if compile_completed.returncode != 0:
        return result

    run_completed = subprocess.run(
        [str(exe)],
        cwd=root,
        env=_library_env(stage / "lib"),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    stdout = run_completed.stdout.strip()
    result["run_result"] = {
        "command": [str(exe)],
        "returncode": run_completed.returncode,
        "ok": run_completed.returncode == 0,
        "stdout": stdout,
        "stderr_tail": _tail(run_completed.stderr),
    }
    result["ok"] = run_completed.returncode == 0 and EXPECTED_MARKER in stdout
    return result


def build_packet(root: Path = Path("."), *, run_smoke: bool = False) -> dict[str, Any]:
    example = (root / EXAMPLE).read_text(encoding="utf-8")
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    staging = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    binding = (root / BINDING_MATRIX).read_text(encoding="utf-8")
    architecture = (root / ARCHITECTURE_DOC).read_text(encoding="utf-8")
    index = (root / BENCHMARK_INDEX).read_text(encoding="utf-8")
    inventory_script = (root / STAGING_INVENTORY_SCRIPT).read_text(encoding="utf-8")
    archive_script = (root / ARCHIVE_C_EXAMPLE_SCRIPT).read_text(encoding="utf-8")
    smoke = run_staged_last_error_example(root) if run_smoke else None
    checks = {
        "example_source_exists_and_uses_diagnostic_api": "rtdl_context_last_error" in example
        and "rtdl_status_string" in example
        and EXPECTED_MARKER in example,
        "makefile_stages_example_in_source_and_prefix_stages": makefile.count("c_api_last_error_client.c") >= 2,
        "staging_contract_lists_and_documents_example": "examples/c_api_last_error_client.c" in staging
        and EXPECTED_MARKER in staging,
        "embedding_readme_documents_example_command_and_boundary": "c_api_last_error_client.c" in embedding
        and EXPECTED_MARKER in embedding
        and "callers must still branch on `rtdl_status`" in embedding,
        "staging_inventory_requires_example": "c_api_last_error_client.c" in inventory_script,
        "archive_c_examples_smoke_requires_example": "c_api_last_error_client.c" in archive_script
        and EXPECTED_MARKER in archive_script,
        "binding_matrix_names_staged_example": "staged `c_api_last_error_client.c` example" in binding,
        "architecture_doc_current_to_goal4612": "As of Goal4612" in architecture
        and "c_api_last_error_client.c" in architecture,
        "benchmark_index_links_goal4612": "Goal4612 C ABI last-error staged example" in index,
    }
    if smoke is not None:
        checks.update(
            {
                "make_available": bool(smoke["make"]),
                "pkg_config_available": bool(smoke["pkg_config"]),
                "cc_available": bool(smoke["cc"]),
                "stage_make_ok": bool(smoke["make_result"] and smoke["make_result"]["ok"]),
                "pkg_config_cflags_ok": bool(smoke["cflags_result"] and smoke["cflags_result"]["ok"]),
                "pkg_config_libs_ok": bool(smoke["libs_result"] and smoke["libs_result"]["ok"]),
                "staged_example_compiles": bool(smoke["compile_result"] and smoke["compile_result"]["ok"]),
                "staged_example_runs_expected_marker": bool(smoke["ok"]),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4612 / V3 M213",
        "status": "c_abi_last_error_staged_example_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "staged_example_smoke": smoke,
        "claim_boundary": {
            "last_error_staged_example_authorized": not failed,
            "stable_error_text_authorized": False,
            "stable_abi_authorized": False,
            "packaged_sdk_authorized": False,
            "system_install_authorized": False,
            "release_authorized": False,
            "performance_wording_authorized": False,
        },
        "conclusion": (
            "Goal4612 promotes the C ABI status/last-error diagnostic pattern "
            "from an internal smoke into the user-facing embedding bundle. The "
            "new `c_api_last_error_client.c` example is staged, prefix-staged, "
            "archived, compiled through staged `pkg-config` flags, and run "
            "against the staged shared library. This authorizes the staged "
            "diagnostic example only; error text remains diagnostic and callers "
            "must branch on `rtdl_status`."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["staged_example_smoke"] or {}
    run = smoke.get("run_result") or {}
    lines = [
        "# Goal4612 / V3 M213 C ABI Last-Error Staged Example",
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
        f"- Stage dir: `{smoke.get('stage_dir')}`",
        f"- Output: `{run.get('stdout')}`",
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
            "- This validates the staged C status/last-error diagnostics example only.",
            "- Error text remains diagnostic; callers branch on `rtdl_status`.",
            "- No stable error-text, stable ABI, packaged SDK, system install, release, or performance claim is authorized.",
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
