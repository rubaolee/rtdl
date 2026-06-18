from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from scripts import goal4576_m177_v3_c_abi_staging_bundle as staging


PACKET_VERSION = "rtdl.v3_0.c_abi_python_ctypes_example.goal4581.v1"
OUT_JSON = Path("docs/reports/goal4581_v3_0_m182_c_abi_python_ctypes_example_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4581_v3_0_m182_c_abi_python_ctypes_example_2026-06-17.md")
MAKEFILE = Path("Makefile")
EXAMPLE = Path("examples/current/embedding/python_ctypes_client.py")
STAGING_CONTRACT = Path("docs/learn/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("examples/current/embedding/README.md")
C_ABI_DRAFT = Path("docs/learn/v3_0_c_abi_draft.md")


def _shared_suffix() -> str:
    if os.name == "nt":
        return ".dll"
    return ".dylib" if os.uname().sysname == "Darwin" else ".so"


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def run_python_ctypes_example(root: Path) -> dict[str, Any]:
    stage_result = staging.run_stage(root)
    stage_dir = root / "build" / "c_api_stage"
    staged_example = stage_dir / "examples" / "python_ctypes_client.py"
    library = stage_dir / "lib" / ("librtdl_c_api" + _shared_suffix())
    env = os.environ.copy()
    library_path = str(library.parent)
    env["LD_LIBRARY_PATH"] = library_path + os.pathsep + env.get("LD_LIBRARY_PATH", "")
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
    result["ok"] = result["run_result"]["ok"] and result["run_result"]["stdout"] == "python_ctypes_ok 0.1.3 ok"
    return result


def build_packet(root: Path = Path("."), *, run_smoke: bool = False) -> dict[str, Any]:
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    example = (root / EXAMPLE).read_text(encoding="utf-8")
    staging_contract = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    c_abi = (root / C_ABI_DRAFT).read_text(encoding="utf-8")
    smoke = run_python_ctypes_example(root) if run_smoke else None
    checks = {
        "python_ctypes_example_exists": (root / EXAMPLE).exists(),
        "example_loads_shared_library_with_ctypes": "ctypes.CDLL" in example,
        "example_declares_context_desc_shape": "class RtdlContextDesc" in example
        and "class RtdlExternalRuntime" in example,
        "example_uses_public_version_capability_and_context_symbols": all(
            token in example
            for token in (
                "rtdl_abi_is_compatible",
                "rtdl_backend_is_supported",
                "rtdl_route_is_supported",
                "rtdl_context_create",
                "rtdl_context_destroy",
            )
        ),
        "makefile_stages_python_ctypes_example": "python_ctypes_client.py" in makefile,
        "staging_contract_documents_python_ctypes_example": "python_ctypes_client.py" in staging_contract
        and "python_ctypes_ok 0.1.3 ok" in staging_contract,
        "embedding_readme_documents_python_ctypes_example": "python_ctypes_client.py" in embedding
        and "python_ctypes_ok 0.1.3 ok" in embedding,
        "c_abi_draft_names_goal4581": "Goal4581" in c_abi and "python_ctypes_client.py" in c_abi,
    }
    if smoke is not None:
        checks.update(
            {
                "stage_bundle_smoke_ok": bool(smoke["stage_result"]["ok"]),
                "staged_python_ctypes_example_exists": (root / smoke["staged_example"]).exists(),
                "staged_library_exists": (root / smoke["library"]).exists(),
                "staged_python_ctypes_example_runs": bool(
                    smoke["run_result"]
                    and smoke["run_result"]["ok"]
                    and smoke["run_result"]["stdout"] == "python_ctypes_ok 0.1.3 ok"
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4581 / V3 M182",
        "status": "c_abi_python_ctypes_example_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "python_ctypes_smoke": smoke,
        "claim_boundary": {
            "general_language_binding_generated": False,
            "python_package_authorized": False,
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "device_buffer_language_binding_authorized": False,
            "optix_embree_c_abi_query_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4581 adds a staged Python ctypes client over the draft C ABI. "
            "The pod evidence runs the staged Python file against the staged "
            "shared library and validates version compatibility, capability "
            "queries, and CPU context create/destroy. This proves the C ABI can "
            "serve as a thin language-binding base, but it is not a generated "
            "Python package, stable ABI, device-buffer binding, or OptiX/Embree "
            "C ABI query surface."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["python_ctypes_smoke"] or {}
    run_result = smoke.get("run_result") or {}
    lines = [
        "# Goal4581 / V3 M182 C ABI Python ctypes Example",
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
            "- This validates a staged Python ctypes example over the draft C ABI only.",
            "- It does not authorize a generated language-binding package, stable ABI, packaged SDK, device-buffer binding, OptiX/Embree C ABI query execution, or release claim.",
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
