from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


PACKET_VERSION = "rtdl.v3_0.embeddability_delivery_status.goal4601.v1"
OUT_JSON = Path("docs/reports/goal4601_v3_0_m202_embeddability_delivery_status_refresh_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4601_v3_0_m202_embeddability_delivery_status_refresh_2026-06-17.md")
ARCHITECTURE_DOC = Path("docs/history/v4_preparatory_embedding/v3_0_embeddability_architecture_strategy.md")
REPORTS = {
    "metadata_readiness": Path("docs/reports/goal4594_v3_0_m195_embeddability_metadata_readiness_refresh_2026-06-17.json"),
    "prefix_python_ctypes": Path("docs/reports/goal4597_v3_0_m198_prefix_stage_python_ctypes_smoke_2026-06-17.json"),
    "layout_audit": Path("docs/reports/goal4599_v3_0_m200_python_ctypes_layout_audit_2026-06-17.json"),
    "cmake_prefix": Path("docs/reports/goal4600_v3_0_m201_c_abi_cmake_prefix_stage_2026-06-17.json"),
}


def _load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def _current_progress_goal_number(doc: str) -> int | None:
    match = re.search(r"As of Goal(\d+)", doc)
    return int(match.group(1)) if match else None


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    architecture = (root / ARCHITECTURE_DOC).read_text(encoding="utf-8")
    progress_goal = _current_progress_goal_number(architecture)
    reports = {name: _load_json(root, path) for name, path in REPORTS.items()}
    metadata = reports["metadata_readiness"]["status_matrix"]
    prefix_python = reports["prefix_python_ctypes"]
    layout = reports["layout_audit"]
    cmake = reports["cmake_prefix"]
    status_matrix = {
        "source_tree_stage_archive": metadata["source_tree_stage_archive"],
        "prefix_layout_stage": "validated",
        "prefix_pkg_config": "validated",
        "prefix_cmake_find_package": "validated_imported_target",
        "python_ctypes_prefix_examples": "validated_lifecycle_host_aabb2_cuda_metadata",
        "python_ctypes_c_layout_audit": "validated_sizeof_offsetof_matches",
        "host_aabb2_c_abi_query": "validated_host_f32_to_host_u64_pairs",
        "host_external_runtime_metadata": metadata["host_external_runtime_metadata"],
        "cuda_buffer_descriptor_import_export": metadata["cuda_buffer_descriptor_import_export"],
        "device_buffer_query_route": "blocked",
        "external_cuda_stream_ordering": "blocked",
        "dlpack_zero_copy": "blocked",
        "generated_language_bindings": "blocked",
        "packaged_sdk": "blocked",
        "system_install": "blocked",
        "stable_abi": "blocked_until_1_0_gates",
        "release": "blocked",
    }
    checks = {
        "all_required_reports_accept": all(not tuple(report.get("failed_checks", ())) for report in reports.values()),
        "architecture_status_at_or_beyond_goal4600": progress_goal is not None
        and progress_goal >= 4600,
        "architecture_names_cmake_prefix_consumer": (
            "find_package(rtdl-c-api CONFIG REQUIRED)" in architecture and "`rtdl::c_api`" in architecture
        ),
        "architecture_names_python_ctypes_layout_audit": (
            "C/Python `ctypes` layout audit" in architecture
            and "compiler-observed `sizeof`/`offsetof` evidence" in architecture
        ),
        "architecture_preserves_no_sdk_or_release_boundary": (
            "not an installed SDK" in architecture and "or V3 release wording" in architecture
        ),
        "cmake_prefix_stage_smoke_ok": (
            cmake["cmake_prefix_stage_smoke"]["ok"]
            and cmake["cmake_prefix_stage_smoke"]["run_result"]["stdout"] == "cmake_direct_link_ok 0.1.3 ok"
        ),
        "cmake_authorizes_prefix_stage_only": (
            cmake["claim_boundary"]["cmake_prefix_stage_authorized"] is True
            and cmake["claim_boundary"]["system_install_authorized"] is False
            and cmake["claim_boundary"]["packaged_sdk_authorized"] is False
        ),
        "prefix_python_ctypes_examples_run": prefix_python["prefix_stage_python_smoke"]["ok"]
        and prefix_python["claim_boundary"]["prefix_python_ctypes_stage_authorized"] is True,
        "layout_audit_matches_python_ctypes": layout["checks"]["c_layout_matches_python_ctypes_layout"]
        and layout["c_layout_probe"]["ok"],
        "metadata_keeps_device_query_blocked": metadata["device_buffer_query_route"] == "blocked"
        and reports["metadata_readiness"]["claim_boundary"]["device_buffer_query_route_authorized"] is False,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4601 / V3 M202",
        "status": "embeddability_delivery_status_refreshed",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "status_matrix": status_matrix,
        "reports": {name: path.as_posix() for name, path in REPORTS.items()},
        "claim_boundary": {
            "source_tree_and_prefix_stage_handoff_authorized": True,
            "cmake_prefix_stage_consumption_authorized": True,
            "python_ctypes_smoke_authorized": True,
            "python_ctypes_layout_drift_check_authorized": True,
            "system_install_authorized": False,
            "package_manager_artifact_authorized": False,
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "dlpack_zero_copy_authorized": False,
            "device_buffer_query_route_authorized": False,
            "external_cuda_stream_authorized": False,
            "optix_embree_c_abi_query_authorized": False,
            "generated_language_binding_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4601 refreshes the V3 embeddability delivery ledger after the "
            "prefix-stage Python `ctypes`, layout-audit, and CMake-consumer work. "
            "The current source tree can hand off a movable C ABI stage, a "
            "prefix-style stage consumable by pkg-config and CMake, and thin "
            "Python `ctypes` examples whose descriptor layouts are checked against "
            "compiler-observed C layout. This is now a validated experimental "
            "source-tree/prefix-stage embedding slice. It is still not a stable ABI, "
            "packaged SDK, system install, DLPack/true-zero-copy path, external "
            "CUDA stream contract, OptiX/Embree C ABI query surface, generated "
            "binding, release, or performance claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4601 / V3 M202 Embeddability Delivery Status Refresh",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Status Matrix",
        "",
        "| Surface | Status |",
        "| --- | --- |",
    ]
    for name, status in packet["status_matrix"].items():
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
            "- Authorized now: source-tree/prefix-stage handoff, staged CMake/pkg-config consumption, thin Python `ctypes` smoke, and layout-drift checking.",
            "- Still blocked: stable ABI, packaged SDK, system install, package-manager artifact, DLPack/true-zero-copy wording, device-buffer query route, external CUDA stream, OptiX/Embree C ABI query execution, generated bindings, release, and performance claims.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet()
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
