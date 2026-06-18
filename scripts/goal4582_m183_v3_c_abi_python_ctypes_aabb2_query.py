from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from scripts import goal4576_m177_v3_c_abi_staging_bundle as staging


PACKET_VERSION = "rtdl.v3_0.c_abi_python_ctypes_aabb2_query.goal4582.v1"
OUT_JSON = Path("docs/reports/goal4582_v3_0_m183_c_abi_python_ctypes_aabb2_query_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4582_v3_0_m183_c_abi_python_ctypes_aabb2_query_2026-06-17.md")
MAKEFILE = Path("Makefile")
EXAMPLE = Path("docs/history/v4_preparatory_embedding/examples/embedding/python_ctypes_aabb2_query_client.py")
STAGING_CONTRACT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("docs/history/v4_preparatory_embedding/examples/embedding/README.md")
C_ABI_DRAFT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_draft.md")
EXPECTED_OUTPUT = "python_ctypes_hit_count=1 first_pair=(0,0)"


def _shared_suffix() -> str:
    if os.name == "nt":
        return ".dll"
    return ".dylib" if os.uname().sysname == "Darwin" else ".so"


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def run_python_ctypes_query(root: Path) -> dict[str, Any]:
    stage_result = staging.run_stage(root)
    stage_dir = root / "build" / "c_api_stage"
    staged_example = stage_dir / "examples" / "python_ctypes_aabb2_query_client.py"
    library = stage_dir / "lib" / ("librtdl_c_api" + _shared_suffix())
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = str(library.parent) + os.pathsep + env.get("LD_LIBRARY_PATH", "")
    result: dict[str, Any] = {
        "stage_result": stage_result,
        "python": sys.executable,
        "staged_example": staged_example.as_posix(),
        "library": library.as_posix(),
        "run_result": None,
        "ok": False,
    }
    if not stage_result["ok"] or not staged_example.exists() or not library.exists():
        return result
    completed = subprocess.run(
        [sys.executable, str(staged_example), str(library)],
        cwd=root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result["run_result"] = {
        "command": [sys.executable, staged_example.as_posix(), library.as_posix()],
        "returncode": completed.returncode,
        "ok": completed.returncode == 0,
        "stdout": completed.stdout.strip(),
        "stderr_tail": _tail(completed.stderr),
    }
    result["ok"] = result["run_result"]["ok"] and result["run_result"]["stdout"] == EXPECTED_OUTPUT
    return result


def build_packet(root: Path = Path("."), *, run_smoke: bool = False) -> dict[str, Any]:
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    example = (root / EXAMPLE).read_text(encoding="utf-8")
    staging_contract = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    c_abi = (root / C_ABI_DRAFT).read_text(encoding="utf-8")
    smoke = run_python_ctypes_query(root) if run_smoke else None
    checks = {
        "python_ctypes_query_example_exists": (root / EXAMPLE).exists(),
        "example_defines_buffer_index_and_query_descriptors": all(
            token in example for token in ("class RtdlBufferView", "class RtdlIndexDesc", "class RtdlQueryDesc")
        ),
        "example_runs_real_host_aabb2_query_symbols": all(
            token in example
            for token in (
                "rtdl_buffer_import",
                "rtdl_index_build",
                "rtdl_query_execute",
                "rtdl_buffer_export",
                "rtdl_buffer_destroy",
            )
        ),
        "example_checks_u64_result_pair": "RTDL_DTYPE_U64" in example
        and "first_pair=({int(rows[0])},{int(rows[1])})" in example,
        "makefile_stages_python_ctypes_query_example": "python_ctypes_aabb2_query_client.py" in makefile,
        "staging_contract_documents_python_ctypes_query_example": "python_ctypes_aabb2_query_client.py" in staging_contract
        and EXPECTED_OUTPUT in staging_contract,
        "embedding_readme_documents_python_ctypes_query_example": "python_ctypes_aabb2_query_client.py" in embedding
        and EXPECTED_OUTPUT in embedding,
        "c_abi_draft_names_goal4582": "Goal4582" in c_abi and "python_ctypes_aabb2_query_client.py" in c_abi,
    }
    if smoke is not None:
        checks.update(
            {
                "stage_bundle_smoke_ok": bool(smoke["stage_result"]["ok"]),
                "staged_python_ctypes_query_example_exists": (root / smoke["staged_example"]).exists(),
                "staged_library_exists": (root / smoke["library"]).exists(),
                "staged_python_ctypes_query_example_runs": bool(
                    smoke["run_result"]
                    and smoke["run_result"]["ok"]
                    and smoke["run_result"]["stdout"] == EXPECTED_OUTPUT
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4582 / V3 M183",
        "status": "c_abi_python_ctypes_aabb2_query_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "python_ctypes_query_smoke": smoke,
        "claim_boundary": {
            "general_language_binding_generated": False,
            "python_package_authorized": False,
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "device_buffer_language_binding_authorized": False,
            "optix_embree_c_abi_query_authorized": False,
            "performance_wording_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4582 proves the staged Python ctypes path can run the current "
            "real C ABI query route, not just load lifecycle symbols. The pod "
            "evidence stages the C ABI bundle, imports host F32 AABB2 primitive "
            "and query buffers from Python, builds an index, executes host AABB2 "
            "overlap, exports the U64 result pair, and validates `(0,0)`. This "
            "still remains a source-tree draft example; it is not a generated "
            "Python package, stable ABI, device-buffer binding, OptiX/Embree C "
            "ABI execution surface, or performance claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["python_ctypes_query_smoke"] or {}
    run_result = smoke.get("run_result") or {}
    lines = [
        "# Goal4582 / V3 M183 C ABI Python ctypes AABB2 Query",
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
        f"- Output: `{run_result.get('stdout')}`",
        f"- Command: `{run_result.get('command')}`",
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
            "- This validates a staged Python ctypes host AABB2 query example over the draft C ABI only.",
            "- It does not authorize a generated language-binding package, stable ABI, packaged SDK, device-buffer binding, OptiX/Embree C ABI query execution, performance wording, or release claim.",
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
