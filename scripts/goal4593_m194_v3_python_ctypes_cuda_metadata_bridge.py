from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from scripts import goal4576_m177_v3_c_abi_staging_bundle as staging


PACKET_VERSION = "rtdl.v3_0.python_ctypes_cuda_metadata_bridge.goal4593.v1"
OUT_JSON = Path("docs/reports/goal4593_v3_0_m194_python_ctypes_cuda_metadata_bridge_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4593_v3_0_m194_python_ctypes_cuda_metadata_bridge_2026-06-17.md")
MAKEFILE = Path("Makefile")
EXAMPLE = Path("docs/history/v4_preparatory_embedding/examples/embedding/python_ctypes_cuda_buffer_metadata_client.py")
STAGING_CONTRACT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("docs/history/v4_preparatory_embedding/examples/embedding/README.md")
C_ABI_DRAFT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_draft.md")
ZERO_COPY_DOC = Path("docs/history/v4_preparatory_embedding/v3_0_zero_copy_interop_contract.md")
EXPECTED_OUTPUT = "python_ctypes_cuda_metadata_shape=(3,4) query_route_rejected=invalid argument"


def _shared_suffix() -> str:
    if os.name == "nt":
        return ".dll"
    return ".dylib" if os.uname().sysname == "Darwin" else ".so"


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def run_python_ctypes_cuda_metadata(root: Path) -> dict[str, Any]:
    stage_result = staging.run_stage(root)
    stage_dir = root / "build" / "c_api_stage"
    staged_example = stage_dir / "examples" / "python_ctypes_cuda_buffer_metadata_client.py"
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
    zero_copy = (root / ZERO_COPY_DOC).read_text(encoding="utf-8")
    smoke = run_python_ctypes_cuda_metadata(root) if run_smoke else None
    checks = {
        "python_ctypes_cuda_metadata_example_exists": (root / EXAMPLE).exists(),
        "example_maps_cuda_array_interface_to_buffer_view": "__cuda_array_interface__" in example
        and "_cuda_array_interface_view" in example
        and "RTDL_DEVICE_CUDA" in example,
        "example_imports_exports_and_rejects_query_route": all(
            token in example
            for token in (
                "rtdl_buffer_import",
                "rtdl_buffer_export",
                "rtdl_index_build",
                "RTDL_STATUS_ERROR_INVALID_ARGUMENT",
            )
        ),
        "example_expected_output_is_documented": EXPECTED_OUTPUT in example,
        "makefile_stages_python_cuda_metadata_example": "python_ctypes_cuda_buffer_metadata_client.py"
        in makefile,
        "staging_contract_documents_python_cuda_metadata_example": "python_ctypes_cuda_buffer_metadata_client.py"
        in staging_contract
        and EXPECTED_OUTPUT in staging_contract,
        "embedding_readme_documents_python_cuda_metadata_example": "python_ctypes_cuda_buffer_metadata_client.py"
        in embedding
        and EXPECTED_OUTPUT in embedding,
        "c_abi_draft_names_goal4593": "Goal4593" in c_abi
        and "python_ctypes_cuda_buffer_metadata_client.py" in c_abi,
        "zero_copy_doc_keeps_public_claim_blocked": "public speedup and public true-zero-copy claims remain blocked"
        in zero_copy,
    }
    if smoke is not None:
        checks.update(
            {
                "stage_bundle_smoke_ok": bool(smoke["stage_result"]["ok"]),
                "staged_python_cuda_metadata_example_exists": (root / smoke["staged_example"]).exists(),
                "staged_library_exists": (root / smoke["library"]).exists(),
                "staged_python_cuda_metadata_example_runs": bool(
                    smoke["run_result"]
                    and smoke["run_result"]["ok"]
                    and smoke["run_result"]["stdout"] == EXPECTED_OUTPUT
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4593 / V3 M194",
        "status": "python_ctypes_cuda_metadata_bridge_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "python_ctypes_cuda_metadata_smoke": smoke,
        "support_matrix": {
            "cuda_array_interface_to_c_abi_descriptor": "validated_metadata_only",
            "python_ctypes_cuda_descriptor_import_export": "validated",
            "cuda_descriptor_host_aabb2_query_route": "rejected_invalid_argument",
            "cuda_pointer_ownership_validation": "blocked",
            "external_cuda_stream_ordering": "blocked",
            "public_true_zero_copy_claim": "blocked",
        },
        "claim_boundary": {
            "generated_python_package_authorized": False,
            "device_buffer_query_route_authorized": False,
            "cuda_pointer_ownership_validated": False,
            "external_cuda_stream_authorized": False,
            "public_true_zero_copy_claim_authorized": False,
            "performance_wording_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4593 validates a Python ctypes bridge from a "
            "`__cuda_array_interface__`-style object into the V3 C ABI neutral "
            "buffer descriptor path. The staged example imports and exports CUDA "
            "metadata through `librtdl_c_api` and proves the current host AABB2 "
            "query route still rejects the CUDA descriptor. This is a metadata "
            "bridge only, not a generated Python package, device-buffer query "
            "route, CUDA pointer ownership validation, stream-ordering proof, "
            "public true-zero-copy claim, performance claim, or release claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["python_ctypes_cuda_metadata_smoke"] or {}
    run_result = smoke.get("run_result") or {}
    lines = [
        "# Goal4593 / V3 M194 Python ctypes CUDA Metadata Bridge",
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
        "## Support Matrix",
        "",
        "| Surface | Status |",
        "| --- | --- |",
    ]
    for name, status in packet["support_matrix"].items():
        lines.append(f"| `{name}` | `{status}` |")
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
            "- This validates a staged Python ctypes CUDA metadata bridge over the draft C ABI only.",
            "- It does not authorize a generated Python package, device-buffer query route, CUDA pointer ownership validation, external stream ordering, public true-zero-copy wording, performance wording, or release claim.",
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
