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


PACKET_VERSION = "rtdl.v3_0.archive_stage_c_examples.goal4609.v1"
OUT_JSON = Path("docs/reports/goal4609_v3_0_m210_archive_stage_c_examples_smoke_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4609_v3_0_m210_archive_stage_c_examples_smoke_2026-06-17.md")
MAKEFILE = Path("Makefile")
STAGING_CONTRACT = Path("docs/learn/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("examples/current/embedding/README.md")
ARCHITECTURE_DOC = Path("docs/learn/v3_0_embeddability_architecture_strategy.md")
BINDING_MATRIX = Path("docs/learn/v3_0_binding_and_device_interop_matrix.md")
BENCHMARK_INDEX = Path("docs/learn/benchmark_evidence_index.md")
STAGE_ARCHIVE_REPORT = Path("docs/reports/goal4587_v3_0_m188_c_abi_stage_archive_2026-06-17.json")
HOST_RUNTIME_REPORT = Path("docs/reports/goal4591_v3_0_m192_c_abi_host_external_runtime_gate_2026-06-17.json")
CUDA_METADATA_REPORT = Path("docs/reports/goal4592_v3_0_m193_c_abi_cuda_buffer_metadata_gate_2026-06-17.json")
ARCHIVE_CMAKE_REPORT = Path("docs/reports/goal4602_v3_0_m203_c_abi_archive_cmake_smoke_2026-06-17.json")
ARCHIVE_PYTHON_REPORT = Path("docs/reports/goal4608_v3_0_m209_archive_stage_python_ctypes_smoke_2026-06-17.json")
ARCHIVE = Path("build/rtdl-c-api-stage-0.1.3.tar.gz")
ARCHIVE_ROOT = "rtdl-c-api-stage-0.1.3"
C_EXAMPLES = (
    {
        "script": "c_api_direct_link_client.c",
        "mode": "pkg_config",
        "executable": "rtdl_c_api_direct_link_client_from_archive_all",
        "expected_stdout": "direct_link_ok 0.1.3 ok",
    },
    {
        "script": "c_api_host_runtime_client.c",
        "mode": "pkg_config",
        "executable": "rtdl_c_api_host_runtime_client_from_archive",
        "expected_contains": "validated_host_external_runtime_cases=3",
    },
    {
        "script": "c_api_cuda_buffer_metadata_client.c",
        "mode": "pkg_config",
        "executable": "rtdl_c_api_cuda_buffer_metadata_client_from_archive",
        "expected_contains": "validated_cuda_buffer_metadata_cases=4",
    },
    {
        "script": "c_api_last_error_client.c",
        "mode": "pkg_config",
        "executable": "rtdl_c_api_last_error_client_from_archive",
        "expected_contains": "validated_last_error_diagnostics_cases=7",
    },
    {
        "script": "c_api_aabb2_overlap_client.c",
        "mode": "dlopen",
        "executable": "rtdl_c_api_aabb2_overlap_client_from_archive",
        "expected_stdout": "hit_count=1 first_pair=(0,0)",
    },
)


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _exe_suffix() -> str:
    return ".exe" if os.name == "nt" else ""


def _shared_suffix() -> str:
    return ".dll" if os.name == "nt" else ".dylib" if os.uname().sysname == "Darwin" else ".so"


def _existing_command(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _library_env(shared_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    if os.name == "nt":
        env["PATH"] = str(shared_dir) + os.pathsep + env.get("PATH", "")
    elif os.uname().sysname == "Darwin":
        env["DYLD_LIBRARY_PATH"] = str(shared_dir) + os.pathsep + env.get("DYLD_LIBRARY_PATH", "")
    else:
        env["LD_LIBRARY_PATH"] = str(shared_dir) + os.pathsep + env.get("LD_LIBRARY_PATH", "")
    return env


def _load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


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


def _compile_command(cc: str, extracted: Path, example: dict[str, str], cflags: str, libs: str) -> list[str]:
    source = extracted / "examples" / example["script"]
    exe = extracted / "examples" / (example["executable"] + _exe_suffix())
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
        str(extracted / "include"),
        str(source),
        "-o",
        str(exe),
    ]
    if os.name != "nt" and os.uname().sysname != "Darwin":
        command.append("-ldl")
    return command


def _run_command(extracted: Path, example: dict[str, str]) -> list[str]:
    exe = extracted / "examples" / (example["executable"] + _exe_suffix())
    if example["mode"] == "dlopen":
        return [str(exe), str(extracted / "lib" / ("librtdl_c_api" + _shared_suffix()))]
    return [str(exe)]


def run_archive_stage_c_examples_smoke(root: Path) -> dict[str, Any]:
    make = shutil.which("make")
    pkg_config = shutil.which("pkg-config")
    cc = _existing_command(("cc", "gcc", "clang"))
    archive = root / ARCHIVE
    result: dict[str, Any] = {
        "make": make,
        "pkg_config": pkg_config,
        "cc": cc,
        "archive": archive.as_posix(),
        "make_result": None,
        "archive_exists": False,
        "archive_size_bytes": 0,
        "extract_dir": None,
        "cflags_result": None,
        "libs_result": None,
        "example_runs": [],
        "ok": False,
    }
    if make is None or pkg_config is None or cc is None:
        return result
    make_completed = subprocess.run(
        [make, "package-c-api-stage"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result["make_result"] = _command_result([make, "package-c-api-stage"], make_completed)
    result["archive_exists"] = archive.exists()
    result["archive_size_bytes"] = archive.stat().st_size if archive.exists() else 0
    if make_completed.returncode != 0 or not archive.exists():
        return result
    with tempfile.TemporaryDirectory(prefix="rtdl_c_api_archive_c_examples_") as tmp:
        tmpdir = Path(tmp)
        extract_root = tmpdir / "extracted"
        shutil.unpack_archive(str(archive), str(extract_root))
        extracted = extract_root / ARCHIVE_ROOT
        result["extract_dir"] = extracted.as_posix()
        pc_dir = extracted / "lib" / "pkgconfig"
        cflags = _pkg_config_args(pkg_config, "--cflags", root, pc_dir)
        libs = _pkg_config_args(pkg_config, "--libs", root, pc_dir)
        result["cflags_result"] = cflags
        result["libs_result"] = libs
        if not cflags["ok"] or not libs["ok"]:
            return result
        for example in C_EXAMPLES:
            compile_command = _compile_command(cc, extracted, example, cflags["stdout"], libs["stdout"])
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
                run_command = _run_command(extracted, example)
                run_completed = subprocess.run(
                    run_command,
                    cwd=root,
                    env=_library_env(extracted / "lib"),
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
        and result["archive_exists"]
        and result["archive_size_bytes"] > 0
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
    stage_archive = _load_json(root, STAGE_ARCHIVE_REPORT)
    host_runtime = _load_json(root, HOST_RUNTIME_REPORT)
    cuda_metadata = _load_json(root, CUDA_METADATA_REPORT)
    archive_cmake = _load_json(root, ARCHIVE_CMAKE_REPORT)
    archive_python = _load_json(root, ARCHIVE_PYTHON_REPORT)
    smoke = run_archive_stage_c_examples_smoke(root) if run_smoke else None
    checks = {
        "makefile_archive_carries_c_examples": "package-c-api-stage: stage-c-api" in makefile
        and all(example["script"] in makefile for example in C_EXAMPLES),
        "staging_contract_documents_archive_c_examples": (
            "The extracted source-tree archive carries runnable C examples too" in staging
            and "validated_cuda_buffer_metadata_cases=4" in staging
            and "validated_last_error_diagnostics_cases=7" in staging
        ),
        "embedding_readme_documents_archive_c_examples": (
            "The extracted archive also carries runnable C examples" in embedding
            and "validated_host_external_runtime_cases=3" in embedding
        ),
        "architecture_doc_names_archive_c_examples_smoke": "Current Implementation Progress" in architecture
        and "Archive-stage C examples smoke" in architecture,
        "binding_matrix_names_archive_c_surface": "C examples from archive stage" in binding,
        "benchmark_index_links_goal4609": "Goal4609 archive-stage C examples smoke" in index,
        "prior_stage_archive_smoke_ok": stage_archive["stage_archive_smoke"]["ok"],
        "prior_host_runtime_smoke_ok": host_runtime["checks"]["runtime_validated_all_cases"],
        "prior_cuda_metadata_smoke_ok": cuda_metadata["checks"]["runtime_validated_all_cases"],
        "prior_archive_cmake_smoke_ok": archive_cmake["archive_cmake_smoke"]["ok"],
        "prior_archive_python_smoke_ok": archive_python["archive_stage_python_smoke"]["ok"],
    }
    if smoke is not None:
        by_script = {row["script"]: row for row in smoke["example_runs"]}
        checks.update(
            {
                "make_package_stage_ok": bool(smoke["make_result"] and smoke["make_result"]["ok"]),
                "archive_exists_and_nonempty": bool(smoke["archive_exists"] and smoke["archive_size_bytes"] > 0),
                "pkg_config_cflags_ok": bool(smoke["cflags_result"] and smoke["cflags_result"]["ok"]),
                "pkg_config_libs_ok": bool(smoke["libs_result"] and smoke["libs_result"]["ok"]),
                "all_archive_c_examples_compile_and_run": bool(smoke["example_runs"])
                and all(row["ok"] for row in smoke["example_runs"]),
                "archive_direct_link_stdout_matches": by_script.get("c_api_direct_link_client.c", {}).get("ok")
                is True,
                "archive_host_runtime_stdout_matches": by_script.get("c_api_host_runtime_client.c", {}).get("ok")
                is True,
                "archive_cuda_metadata_stdout_matches": by_script.get(
                    "c_api_cuda_buffer_metadata_client.c", {}
                ).get("ok")
                is True,
                "archive_last_error_stdout_matches": by_script.get("c_api_last_error_client.c", {}).get("ok")
                is True,
                "archive_dlopen_aabb2_stdout_matches": by_script.get("c_api_aabb2_overlap_client.c", {}).get("ok")
                is True,
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4609 / V3 M210",
        "status": "archive_stage_c_examples_smoke_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "archive_stage_c_examples_smoke": smoke,
        "claim_boundary": {
            "archive_c_examples_stage_authorized": not failed,
            "system_install_authorized": False,
            "package_manager_artifact_authorized": False,
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "device_buffer_query_route_authorized": False,
            "release_authorized": False,
            "performance_wording_authorized": False,
        },
        "conclusion": (
            "Goal4609 validates that the movable source-tree C ABI archive can "
            "compile and run the staged C examples after extraction. The pod "
            "smoke builds `package-c-api-stage`, unpacks "
            "`rtdl-c-api-stage-0.1.3.tar.gz`, compiles direct-link, `dlopen` "
            "host AABB2, host-runtime metadata, CUDA descriptor metadata, and "
            "status/last-error diagnostics clients, then runs them against the "
            "extracted shared library. This "
            "authorizes extracted-archive C example smoke only; it is not a "
            "system install, package-manager artifact, packaged SDK, stable ABI, "
            "device-buffer query route, release, or performance claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["archive_stage_c_examples_smoke"] or {}
    lines = [
        "# Goal4609 / V3 M210 Archive-Stage C Examples Smoke",
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
        f"- Archive: `{smoke.get('archive')}`",
        f"- Extract dir: `{smoke.get('extract_dir')}`",
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
            "- This validates extracted source-tree archive C examples only.",
            "- It does not authorize a system install, package-manager artifact, packaged SDK, stable ABI, device-buffer query route, release, or performance claim.",
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
