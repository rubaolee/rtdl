from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


PACKET_VERSION = "rtdl.v3_0.prefix_stage_python_ctypes.goal4597.v1"
OUT_JSON = Path("docs/reports/goal4597_v3_0_m198_prefix_stage_python_ctypes_smoke_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4597_v3_0_m198_prefix_stage_python_ctypes_smoke_2026-06-17.md")
MAKEFILE = Path("Makefile")
STAGING_CONTRACT = Path("docs/learn/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("examples/current/embedding/README.md")
PREFIX_STAGE_REPORT = Path("docs/reports/goal4595_v3_0_m196_c_abi_prefix_stage_2026-06-17.json")
DEFAULT_TEST_PREFIX = "/opt/rtdl"
PYTHON_EXAMPLES = (
    (
        "python_ctypes_client.py",
        "python_ctypes_ok 0.1.3 ok",
    ),
    (
        "python_ctypes_aabb2_query_client.py",
        "python_ctypes_hit_count=1 first_pair=(0,0)",
    ),
    (
        "python_ctypes_cuda_buffer_metadata_client.py",
        "python_ctypes_cuda_metadata_shape=(3,4) query_route_rejected=invalid argument",
    ),
)


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _shared_suffix() -> str:
    if os.name == "nt":
        return ".dll"
    return ".dylib" if os.uname().sysname == "Darwin" else ".so"


def run_prefix_stage_python_smoke(root: Path) -> dict[str, Any]:
    make = shutil.which("make")
    result: dict[str, Any] = {
        "make": make,
        "python": sys.executable,
        "stage_root": None,
        "prefix": DEFAULT_TEST_PREFIX,
        "prefix_dir": None,
        "make_result": None,
        "example_runs": [],
        "ok": False,
    }
    if make is None:
        return result
    with tempfile.TemporaryDirectory(prefix="rtdl_c_api_prefix_python_") as tmp:
        stage_root = Path(tmp)
        prefix_dir = stage_root / DEFAULT_TEST_PREFIX.strip("/")
        lib_path = prefix_dir / "lib" / ("librtdl_c_api" + _shared_suffix())
        examples_dir = prefix_dir / "share" / "rtdl" / "examples"
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
        run_env = os.environ.copy()
        if os.name == "nt":
            run_env["PATH"] = str(prefix_dir / "lib") + os.pathsep + run_env.get("PATH", "")
        elif os.uname().sysname == "Darwin":
            run_env["DYLD_LIBRARY_PATH"] = str(prefix_dir / "lib") + os.pathsep + run_env.get("DYLD_LIBRARY_PATH", "")
        else:
            run_env["LD_LIBRARY_PATH"] = str(prefix_dir / "lib") + os.pathsep + run_env.get("LD_LIBRARY_PATH", "")
        for script_name, expected_stdout in PYTHON_EXAMPLES:
            script_path = examples_dir / script_name
            completed = subprocess.run(
                [sys.executable, str(script_path), str(lib_path)],
                cwd=root,
                env=run_env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            result["example_runs"].append(
                {
                    "script": script_name,
                    "command": [sys.executable, script_path.as_posix(), lib_path.as_posix()],
                    "returncode": completed.returncode,
                    "ok": completed.returncode == 0 and completed.stdout.strip() == expected_stdout,
                    "stdout": completed.stdout.strip(),
                    "expected_stdout": expected_stdout,
                    "stderr_tail": _tail(completed.stderr),
                }
            )
    result["ok"] = bool(result["make_result"] and result["make_result"]["ok"]) and all(
        row["ok"] for row in result["example_runs"]
    )
    return result


def build_packet(root: Path = Path("."), *, run_smoke: bool = False) -> dict[str, Any]:
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    staging = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    prefix_packet = json.loads((root / PREFIX_STAGE_REPORT).read_text(encoding="utf-8"))
    smoke = run_prefix_stage_python_smoke(root) if run_smoke else None
    checks = {
        "prefix_stage_target_exists": "stage-c-api-prefix:" in makefile,
        "prefix_stage_copies_python_ctypes_examples": "python_ctypes_client.py" in makefile
        and "python_ctypes_aabb2_query_client.py" in makefile
        and "python_ctypes_cuda_buffer_metadata_client.py" in makefile
        and "/share/rtdl/examples" in makefile,
        "staging_contract_documents_prefix_python_examples": "python3 build/c_api_prefix_stage/usr/local/share/rtdl/examples/python_ctypes_client.py"
        in staging
        and "python_ctypes_cuda_metadata_shape=(3,4) query_route_rejected=invalid argument" in staging,
        "embedding_readme_documents_prefix_python_examples": "without using\nsource-tree relative paths" in embedding
        and "python_ctypes_hit_count=1 first_pair=(0,0)" in embedding,
        "prefix_stage_report_accepts": not tuple(prefix_packet.get("failed_checks", ())),
        "prefix_stage_report_keeps_system_install_false": prefix_packet["claim_boundary"][
            "system_install_authorized"
        ]
        is False,
    }
    if smoke is not None:
        checks.update(
            {
                "prefix_stage_make_ok": bool(smoke["make_result"] and smoke["make_result"]["ok"]),
                "all_prefix_python_examples_run": bool(smoke["example_runs"])
                and all(row["ok"] for row in smoke["example_runs"]),
                "python_ctypes_lifecycle_stdout_matches": any(
                    row["script"] == "python_ctypes_client.py" and row["ok"] for row in smoke["example_runs"]
                ),
                "python_ctypes_aabb2_stdout_matches": any(
                    row["script"] == "python_ctypes_aabb2_query_client.py" and row["ok"]
                    for row in smoke["example_runs"]
                ),
                "python_ctypes_cuda_metadata_stdout_matches": any(
                    row["script"] == "python_ctypes_cuda_buffer_metadata_client.py" and row["ok"]
                    for row in smoke["example_runs"]
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4597 / V3 M198",
        "status": "prefix_stage_python_ctypes_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "prefix_stage_python_smoke": smoke,
        "claim_boundary": {
            "prefix_python_ctypes_stage_authorized": not failed,
            "generated_python_package_authorized": False,
            "system_install_authorized": False,
            "package_manager_artifact_authorized": False,
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4597 validates that the prefix-style C ABI stage is usable from "
            "the staged Python `ctypes` examples, not only from a direct-link C "
            "client. The pod evidence builds a temporary `/opt/rtdl` prefix "
            "stage and runs the lifecycle, host AABB2 query, and CUDA metadata "
            "bridge examples against the staged shared library. This authorizes "
            "a prefix-stage Python `ctypes` smoke only; it is not a generated "
            "Python package, system install, packaged SDK, stable ABI, or "
            "release claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["prefix_stage_python_smoke"] or {}
    lines = [
        "# Goal4597 / V3 M198 Prefix-Stage Python Ctypes Smoke",
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
        f"- Prefix: `{smoke.get('prefix')}`",
        f"- Prefix dir: `{smoke.get('prefix_dir')}`",
        "",
        "| Script | OK | Stdout |",
        "| --- | --- | --- |",
    ]
    for row in smoke.get("example_runs", ()):
        lines.append(f"| `{row['script']}` | `{row['ok']}` | `{row['stdout']}` |")
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
            "- This validates prefix-stage Python `ctypes` examples only.",
            "- It does not authorize a generated Python package, system install, package-manager artifact, packaged SDK, stable ABI, or release claim.",
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
