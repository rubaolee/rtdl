from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
from typing import Any


PACKET_VERSION = "rtdl.v3_0.prefix_stage_c_examples.goal4613.v1"
OUT_JSON = Path("docs/reports/goal4613_v3_0_m214_prefix_stage_c_examples_smoke_2026-06-18.json")
OUT_REPORT = Path("docs/reports/goal4613_v3_0_m214_prefix_stage_c_examples_smoke_2026-06-18.md")
MAKEFILE = Path("Makefile")
STAGING_CONTRACT = Path("docs/learn/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("examples/current/embedding/README.md")
ARCHITECTURE_DOC = Path("docs/learn/v3_0_embeddability_architecture_strategy.md")
BINDING_MATRIX = Path("docs/learn/v3_0_binding_and_device_interop_matrix.md")
BENCHMARK_INDEX = Path("docs/learn/benchmark_evidence_index.md")
DEFAULT_TEST_PREFIX = "/opt/rtdl"
C_EXAMPLES = (
    {
        "script": "c_api_direct_link_client.c",
        "mode": "pkg_config",
        "executable": "rtdl_c_api_direct_link_client_from_prefix_all",
        "expected_stdout": "direct_link_ok 0.1.3 ok",
    },
    {
        "script": "c_api_host_runtime_client.c",
        "mode": "pkg_config",
        "executable": "rtdl_c_api_host_runtime_client_from_prefix",
        "expected_contains": "validated_host_external_runtime_cases=3",
    },
    {
        "script": "c_api_cuda_buffer_metadata_client.c",
        "mode": "pkg_config",
        "executable": "rtdl_c_api_cuda_buffer_metadata_client_from_prefix",
        "expected_contains": "validated_cuda_buffer_metadata_cases=4",
    },
    {
        "script": "c_api_last_error_client.c",
        "mode": "pkg_config",
        "executable": "rtdl_c_api_last_error_client_from_prefix",
        "expected_contains": "validated_last_error_diagnostics_cases=7",
    },
    {
        "script": "c_api_aabb2_overlap_client.c",
        "mode": "dlopen",
        "executable": "rtdl_c_api_aabb2_overlap_client_from_prefix",
        "expected_stdout": "hit_count=1 first_pair=(0,0)",
    },
)


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _exe_suffix() -> str:
    return ".exe" if os.name == "nt" else ""


def _shared_suffix() -> str:
    return ".dll" if os.name == "nt" else ".dylib" if os.uname().sysname == "Darwin" else ".so"


def _library_env(shared_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    if os.name == "nt":
        env["PATH"] = str(shared_dir) + os.pathsep + env.get("PATH", "")
    elif os.uname().sysname == "Darwin":
        env["DYLD_LIBRARY_PATH"] = str(shared_dir) + os.pathsep + env.get("DYLD_LIBRARY_PATH", "")
    else:
        env["LD_LIBRARY_PATH"] = str(shared_dir) + os.pathsep + env.get("LD_LIBRARY_PATH", "")
    return env


def _existing_command(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _command_result(command: list[str], completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    return {
        "command": command,
        "returncode": completed.returncode,
        "ok": completed.returncode == 0,
        "stdout_tail": _tail(completed.stdout),
        "stderr_tail": _tail(completed.stderr),
    }


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


def _compile_command(cc: str, prefix_dir: Path, example: dict[str, str], cflags: str, libs: str) -> list[str]:
    source = prefix_dir / "share" / "rtdl" / "examples" / example["script"]
    exe = prefix_dir / "share" / "rtdl" / "examples" / (example["executable"] + _exe_suffix())
    if example["mode"] == "pkg_config":
        return [
            cc,
            "-std=c11",
            *shlex.split(cflags),
            str(source),
            "-o",
            str(exe),
            *shlex.split(libs),
        ]
    command = [
        cc,
        "-std=c11",
        "-I",
        str(prefix_dir / "include"),
        str(source),
        "-o",
        str(exe),
    ]
    if os.name != "nt" and os.uname().sysname != "Darwin":
        command.append("-ldl")
    return command


def _run_command(prefix_dir: Path, example: dict[str, str]) -> list[str]:
    exe = prefix_dir / "share" / "rtdl" / "examples" / (example["executable"] + _exe_suffix())
    if example["mode"] == "dlopen":
        return [str(exe), str(prefix_dir / "lib" / ("librtdl_c_api" + _shared_suffix()))]
    return [str(exe)]


def run_prefix_stage_c_examples_smoke(root: Path) -> dict[str, Any]:
    make = shutil.which("make")
    pkg_config = shutil.which("pkg-config")
    cc = _existing_command(("cc", "gcc", "clang"))
    result: dict[str, Any] = {
        "make": make,
        "pkg_config": pkg_config,
        "cc": cc,
        "prefix": DEFAULT_TEST_PREFIX,
        "stage_root": None,
        "prefix_dir": None,
        "make_result": None,
        "cflags_result": None,
        "libs_result": None,
        "example_runs": [],
        "ok": False,
    }
    if make is None or pkg_config is None or cc is None:
        return result

    with tempfile.TemporaryDirectory(prefix="rtdl_c_api_prefix_c_examples_") as tmp:
        stage_root = Path(tmp)
        prefix_dir = stage_root / DEFAULT_TEST_PREFIX.strip("/")
        result["stage_root"] = stage_root.as_posix()
        result["prefix_dir"] = prefix_dir.as_posix()
        make_command = [
            make,
            "stage-c-api-prefix",
            f"C_API_PREFIX_STAGE_ROOT={stage_root.as_posix()}",
            f"C_API_PREFIX={DEFAULT_TEST_PREFIX}",
        ]
        make_completed = subprocess.run(
            make_command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        result["make_result"] = _command_result(make_command, make_completed)
        if make_completed.returncode != 0:
            return result

        pc_dir = prefix_dir / "lib" / "pkgconfig"
        cflags = _pkg_config_args(pkg_config, "--cflags", root, pc_dir)
        libs = _pkg_config_args(pkg_config, "--libs", root, pc_dir)
        result["cflags_result"] = cflags
        result["libs_result"] = libs
        if not cflags["ok"] or not libs["ok"]:
            return result

        for example in C_EXAMPLES:
            compile_command = _compile_command(cc, prefix_dir, example, cflags["stdout"], libs["stdout"])
            compile_completed = subprocess.run(
                compile_command,
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            run_result = None
            stdout = ""
            ok = False
            if compile_completed.returncode == 0:
                run_command = _run_command(prefix_dir, example)
                run_completed = subprocess.run(
                    run_command,
                    cwd=root,
                    env=_library_env(prefix_dir / "lib"),
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                stdout = run_completed.stdout.strip()
                expected_stdout = example.get("expected_stdout")
                expected_contains = example.get("expected_contains")
                ok = run_completed.returncode == 0 and (
                    stdout == expected_stdout if expected_stdout is not None else expected_contains in stdout
                )
                run_result = {
                    "command": run_command,
                    "returncode": run_completed.returncode,
                    "ok": run_completed.returncode == 0,
                    "stdout": stdout,
                    "expected_stdout": expected_stdout,
                    "expected_contains": expected_contains,
                    "stderr_tail": _tail(run_completed.stderr),
                }
            result["example_runs"].append(
                {
                    "script": example["script"],
                    "mode": example["mode"],
                    "compile_result": _command_result(compile_command, compile_completed),
                    "run_result": run_result,
                    "ok": ok,
                }
            )
    result["ok"] = (
        bool(result["make_result"] and result["make_result"]["ok"])
        and bool(result["cflags_result"] and result["cflags_result"]["ok"])
        and bool(result["libs_result"] and result["libs_result"]["ok"])
        and bool(result["example_runs"])
        and all(row["ok"] for row in result["example_runs"])
    )
    return result


def build_packet(root: Path = Path("."), *, run_smoke: bool = False) -> dict[str, Any]:
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    staging = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    architecture = (root / ARCHITECTURE_DOC).read_text(encoding="utf-8")
    binding = (root / BINDING_MATRIX).read_text(encoding="utf-8")
    index = (root / BENCHMARK_INDEX).read_text(encoding="utf-8")
    smoke = run_prefix_stage_c_examples_smoke(root) if run_smoke else None
    checks = {
        "makefile_prefix_stage_carries_all_c_examples": "stage-c-api-prefix:" in makefile
        and all(example["script"] in makefile for example in C_EXAMPLES),
        "staging_contract_documents_prefix_c_examples": "share/rtdl/examples/*" in staging
        and "validated_last_error_diagnostics_cases=7" in staging,
        "embedding_readme_documents_prefix_c_examples": "same prefix-style stage also carries C examples" in embedding
        and "validated_last_error_diagnostics_cases=7" in embedding,
        "architecture_doc_names_prefix_c_examples_smoke": "Prefix-stage C examples smoke" in architecture,
        "binding_matrix_names_prefix_c_surface": "C examples from prefix stage" in binding,
        "benchmark_index_links_goal4613": "Goal4613 prefix-stage C examples smoke" in index,
    }
    if smoke is not None:
        by_script = {row["script"]: row for row in smoke["example_runs"]}
        checks.update(
            {
                "make_prefix_stage_ok": bool(smoke["make_result"] and smoke["make_result"]["ok"]),
                "pkg_config_available": bool(smoke["pkg_config"]),
                "cc_available": bool(smoke["cc"]),
                "prefix_pkg_config_cflags_ok": bool(smoke["cflags_result"] and smoke["cflags_result"]["ok"]),
                "prefix_pkg_config_libs_ok": bool(smoke["libs_result"] and smoke["libs_result"]["ok"]),
                "all_prefix_c_examples_compile_and_run": bool(smoke["example_runs"])
                and all(row["ok"] for row in smoke["example_runs"]),
                "prefix_direct_link_stdout_matches": by_script.get("c_api_direct_link_client.c", {}).get("ok")
                is True,
                "prefix_host_runtime_stdout_matches": by_script.get("c_api_host_runtime_client.c", {}).get("ok")
                is True,
                "prefix_cuda_metadata_stdout_matches": by_script.get(
                    "c_api_cuda_buffer_metadata_client.c", {}
                ).get("ok")
                is True,
                "prefix_last_error_stdout_matches": by_script.get("c_api_last_error_client.c", {}).get("ok")
                is True,
                "prefix_dlopen_aabb2_stdout_matches": by_script.get("c_api_aabb2_overlap_client.c", {}).get("ok")
                is True,
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4613 / V3 M214",
        "status": "prefix_stage_c_examples_smoke_checked",
        "date": "2026-06-18",
        "checks": checks,
        "failed_checks": failed,
        "prefix_stage_c_examples_smoke": smoke,
        "claim_boundary": {
            "prefix_c_examples_stage_authorized": not failed,
            "system_install_authorized": False,
            "package_manager_artifact_authorized": False,
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "release_authorized": False,
            "performance_wording_authorized": False,
        },
        "conclusion": (
            "Goal4613 validates that the DESTDIR/prefix-style C ABI stage can "
            "compile and run every staged C example. The pod smoke stages RTDL "
            "under a temporary `/opt/rtdl` prefix, compiles direct-link, `dlopen` "
            "host AABB2, host-runtime metadata, CUDA descriptor metadata, and "
            "status/last-error diagnostics clients, then runs them against the "
            "staged shared library. This authorizes prefix-stage C example smoke "
            "only; it is not a system install, package-manager artifact, packaged "
            "SDK, stable ABI, release, or performance claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["prefix_stage_c_examples_smoke"] or {}
    lines = [
        "# Goal4613 / V3 M214 Prefix-Stage C Examples Smoke",
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
        f"- Prefix dir: `{smoke.get('prefix_dir')}`",
        "",
        "| Example | Mode | OK | Stdout |",
        "| --- | --- | --- | --- |",
    ]
    for row in smoke.get("example_runs", ()):
        run_result = row.get("run_result") or {}
        lines.append(
            f"| `{row['script']}` | `{row['mode']}` | `{row['ok']}` | `{run_result.get('stdout', '')}` |"
        )
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
            "- This validates prefix-stage C examples only.",
            "- It does not authorize a system install, package-manager artifact, packaged SDK, stable ABI, release, or performance claim.",
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
