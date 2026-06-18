from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


PACKET_VERSION = "rtdl.v3_0.embeddability_delivery_archive_cmake.goal4603.v1"
OUT_JSON = Path("docs/reports/goal4603_v3_0_m204_embeddability_delivery_archive_cmake_refresh_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4603_v3_0_m204_embeddability_delivery_archive_cmake_refresh_2026-06-17.md")
ARCHITECTURE_DOC = Path("docs/learn/v3_0_embeddability_architecture_strategy.md")
REPORTS = {
    "delivery_status": Path("docs/reports/goal4601_v3_0_m202_embeddability_delivery_status_refresh_2026-06-17.json"),
    "archive_cmake": Path("docs/reports/goal4602_v3_0_m203_c_abi_archive_cmake_smoke_2026-06-17.json"),
    "cmake_prefix": Path("docs/reports/goal4600_v3_0_m201_c_abi_cmake_prefix_stage_2026-06-17.json"),
    "layout_audit": Path("docs/reports/goal4599_v3_0_m200_python_ctypes_layout_audit_2026-06-17.json"),
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
    prior_matrix = reports["delivery_status"]["status_matrix"]
    status_matrix = dict(prior_matrix)
    status_matrix.update(
        {
            "archive_cmake_find_package": "validated_extracted_archive_imported_target",
            "source_tree_and_prefix_stage_handoff": "validated_pkg_config_and_cmake",
            "system_install": "blocked",
            "packaged_sdk": "blocked",
            "stable_abi": "blocked_until_1_0_gates",
            "release": "blocked",
        }
    )
    archive_smoke = reports["archive_cmake"]["archive_cmake_smoke"]
    checks = {
        "all_required_reports_accept": all(not tuple(report.get("failed_checks", ())) for report in reports.values()),
        "architecture_status_at_or_beyond_goal4602": progress_goal is not None
        and progress_goal >= 4602,
        "architecture_names_archive_cmake_proof": (
            "Extracted source-tree stage archive CMake consumer proof" in architecture
            and "rtdl-c-api-stage-0.1.3.tar.gz" in architecture
        ),
        "architecture_keeps_cmake_as_stage_not_sdk": (
            "staged-prefix/archive consumption proof" in architecture
            and "not an installed SDK\npromise" in architecture
        ),
        "archive_cmake_smoke_ok": archive_smoke["ok"]
        and archive_smoke["run_result"]["stdout"] == "cmake_archive_direct_link_ok 0.1.3 ok",
        "archive_cmake_authorizes_archive_stage_only": (
            reports["archive_cmake"]["claim_boundary"]["archive_cmake_stage_authorized"] is True
            and reports["archive_cmake"]["claim_boundary"]["system_install_authorized"] is False
            and reports["archive_cmake"]["claim_boundary"]["packaged_sdk_authorized"] is False
        ),
        "prefix_cmake_still_ok": reports["cmake_prefix"]["cmake_prefix_stage_smoke"]["ok"],
        "layout_audit_still_ok": reports["layout_audit"]["checks"]["c_layout_matches_python_ctypes_layout"],
        "prior_delivery_status_keeps_device_query_blocked": (
            reports["delivery_status"]["status_matrix"]["device_buffer_query_route"] == "blocked"
            and reports["delivery_status"]["claim_boundary"]["device_buffer_query_route_authorized"] is False
        ),
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4603 / V3 M204",
        "status": "embeddability_delivery_archive_cmake_refreshed",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "status_matrix": status_matrix,
        "reports": {name: path.as_posix() for name, path in REPORTS.items()},
        "claim_boundary": {
            "source_tree_stage_handoff_authorized": True,
            "prefix_stage_handoff_authorized": True,
            "archive_cmake_stage_authorized": True,
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
            "Goal4603 refreshes the embeddability delivery ledger after the archive "
            "CMake smoke. The current V3 source-tree handoff now has validated "
            "pkg-config and CMake consumption from both prefix-stage and extracted "
            "archive layouts, plus thin Python `ctypes` examples and C/Python layout "
            "drift checks. This remains an experimental source-tree/prefix/archive "
            "handoff slice, not a stable ABI, packaged SDK, system install, "
            "DLPack/true-zero-copy path, external CUDA stream contract, OptiX/Embree "
            "C ABI query surface, generated binding, release, or performance claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4603 / V3 M204 Embeddability Delivery Archive CMake Refresh",
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
            "- Authorized now: source-tree/prefix/archive handoff, staged CMake/pkg-config consumption, thin Python `ctypes` smoke, and layout-drift checking.",
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
