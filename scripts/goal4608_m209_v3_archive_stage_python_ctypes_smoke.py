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


PACKET_VERSION = "rtdl.v3_0.archive_stage_python_ctypes.goal4608.v1"
OUT_JSON = Path("docs/reports/goal4608_v3_0_m209_archive_stage_python_ctypes_smoke_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4608_v3_0_m209_archive_stage_python_ctypes_smoke_2026-06-17.md")
MAKEFILE = Path("Makefile")
STAGING_CONTRACT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("docs/history/v4_preparatory_embedding/examples/embedding/README.md")
ARCHITECTURE_DOC = Path("docs/history/v4_preparatory_embedding/v3_0_embeddability_architecture_strategy.md")
BINDING_MATRIX = Path("docs/history/v4_preparatory_embedding/v3_0_binding_and_device_interop_matrix.md")
BENCHMARK_INDEX = Path("docs/learn/benchmark_evidence_index.md")
STAGE_ARCHIVE_REPORT = Path("docs/reports/goal4587_v3_0_m188_c_abi_stage_archive_2026-06-17.json")
ARCHIVE_CMAKE_REPORT = Path("docs/reports/goal4602_v3_0_m203_c_abi_archive_cmake_smoke_2026-06-17.json")
PREFIX_PYTHON_REPORT = Path("docs/reports/goal4597_v3_0_m198_prefix_stage_python_ctypes_smoke_2026-06-17.json")
DLPACK_LIKE_REPORT = Path(
    "docs/reports/goal4607_v3_0_m208_python_ctypes_dlpack_like_metadata_bridge_2026-06-17.json"
)
ARCHIVE = Path("build/rtdl-c-api-stage-0.1.3.tar.gz")
ARCHIVE_ROOT = "rtdl-c-api-stage-0.1.3"
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
    (
        "python_ctypes_dlpack_like_metadata_client.py",
        "python_ctypes_dlpack_like_metadata_shape=(2,3) query_route_rejected=invalid argument",
    ),
)


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _shared_suffix() -> str:
    return ".dll" if os.name == "nt" else ".dylib" if os.uname().sysname == "Darwin" else ".so"


def _load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def run_archive_stage_python_smoke(root: Path) -> dict[str, Any]:
    make = shutil.which("make")
    archive = root / ARCHIVE
    result: dict[str, Any] = {
        "make": make,
        "python": sys.executable,
        "archive": archive.as_posix(),
        "make_result": None,
        "archive_exists": False,
        "archive_size_bytes": 0,
        "extract_dir": None,
        "example_runs": [],
        "ok": False,
    }
    if make is None:
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
    with tempfile.TemporaryDirectory(prefix="rtdl_c_api_archive_python_") as tmp:
        tmpdir = Path(tmp)
        extract_root = tmpdir / "extracted"
        shutil.unpack_archive(str(archive), str(extract_root))
        extracted = extract_root / ARCHIVE_ROOT
        examples_dir = extracted / "examples"
        lib_path = extracted / "lib" / ("librtdl_c_api" + _shared_suffix())
        result["extract_dir"] = extracted.as_posix()
        run_env = os.environ.copy()
        if os.name == "nt":
            run_env["PATH"] = str(extracted / "lib") + os.pathsep + run_env.get("PATH", "")
        elif os.uname().sysname == "Darwin":
            run_env["DYLD_LIBRARY_PATH"] = str(extracted / "lib") + os.pathsep + run_env.get("DYLD_LIBRARY_PATH", "")
        else:
            run_env["LD_LIBRARY_PATH"] = str(extracted / "lib") + os.pathsep + run_env.get("LD_LIBRARY_PATH", "")
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
    archive_cmake = _load_json(root, ARCHIVE_CMAKE_REPORT)
    prefix_python = _load_json(root, PREFIX_PYTHON_REPORT)
    dlpack_like = _load_json(root, DLPACK_LIKE_REPORT)
    smoke = run_archive_stage_python_smoke(root) if run_smoke else None
    checks = {
        "makefile_archive_carries_python_ctypes_examples": "package-c-api-stage: stage-c-api" in makefile
        and all(script_name in makefile for script_name, _ in PYTHON_EXAMPLES),
        "staging_contract_documents_archive_python_examples": (
            "The extracted source-tree archive also carries the Python `ctypes` examples" in staging
            and "python_ctypes_dlpack_like_metadata_shape=(2,3) query_route_rejected=invalid argument"
            in staging
        ),
        "embedding_readme_documents_archive_python_examples": (
            "The extracted archive also carries the same Python `ctypes` examples" in embedding
            and "python_ctypes_cuda_metadata_shape=(3,4) query_route_rejected=invalid argument" in embedding
        ),
        "architecture_doc_names_archive_python_smoke": "Current Implementation Progress" in architecture
        and "Archive-stage Python `ctypes` smoke" in architecture,
        "binding_matrix_names_archive_python_surface": "Python `ctypes` examples from archive stage" in binding,
        "benchmark_index_links_goal4608": "Goal4608 archive-stage Python ctypes smoke" in index,
        "prior_stage_archive_smoke_ok": stage_archive["stage_archive_smoke"]["ok"],
        "prior_archive_cmake_smoke_ok": archive_cmake["archive_cmake_smoke"]["ok"],
        "prior_prefix_python_smoke_ok": prefix_python["prefix_stage_python_smoke"]["ok"],
        "prior_dlpack_like_bridge_smoke_ok": dlpack_like["python_ctypes_dlpack_like_metadata_smoke"]["ok"],
    }
    if smoke is not None:
        checks.update(
            {
                "make_package_stage_ok": bool(smoke["make_result"] and smoke["make_result"]["ok"]),
                "archive_exists_and_nonempty": bool(smoke["archive_exists"] and smoke["archive_size_bytes"] > 0),
                "all_archive_python_examples_run": bool(smoke["example_runs"])
                and all(row["ok"] for row in smoke["example_runs"]),
                "archive_python_lifecycle_stdout_matches": any(
                    row["script"] == "python_ctypes_client.py" and row["ok"] for row in smoke["example_runs"]
                ),
                "archive_python_aabb2_stdout_matches": any(
                    row["script"] == "python_ctypes_aabb2_query_client.py" and row["ok"]
                    for row in smoke["example_runs"]
                ),
                "archive_python_cuda_metadata_stdout_matches": any(
                    row["script"] == "python_ctypes_cuda_buffer_metadata_client.py" and row["ok"]
                    for row in smoke["example_runs"]
                ),
                "archive_python_dlpack_like_metadata_stdout_matches": any(
                    row["script"] == "python_ctypes_dlpack_like_metadata_client.py" and row["ok"]
                    for row in smoke["example_runs"]
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4608 / V3 M209",
        "status": "archive_stage_python_ctypes_smoke_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "archive_stage_python_smoke": smoke,
        "claim_boundary": {
            "archive_python_ctypes_stage_authorized": not failed,
            "generated_python_package_authorized": False,
            "python_wheel_authorized": False,
            "system_install_authorized": False,
            "package_manager_artifact_authorized": False,
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "device_buffer_query_route_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4608 validates that the movable source-tree C ABI archive can "
            "run the staged Python `ctypes` examples after extraction. The pod "
            "smoke builds `package-c-api-stage`, unpacks "
            "`rtdl-c-api-stage-0.1.3.tar.gz`, and runs lifecycle, host AABB2, "
            "CUDA metadata, and DLPack-like metadata examples against the "
            "extracted shared library. This authorizes extracted-archive Python "
            "`ctypes` smoke only; it is not a generated Python package, wheel, "
            "system install, package-manager artifact, packaged SDK, stable ABI, "
            "device-buffer query route, release, or performance claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["archive_stage_python_smoke"] or {}
    lines = [
        "# Goal4608 / V3 M209 Archive-Stage Python Ctypes Smoke",
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
            "- This validates extracted source-tree archive Python `ctypes` examples only.",
            "- It does not authorize a generated Python package, wheel, system install, package-manager artifact, packaged SDK, stable ABI, device-buffer query route, release, or performance claim.",
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
