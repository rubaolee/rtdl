from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


PACKET_VERSION = "rtdl.v3_0.embeddability_architecture_prefix_status.goal4598.v1"
OUT_JSON = Path("docs/reports/goal4598_v3_0_m199_embeddability_architecture_prefix_status_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4598_v3_0_m199_embeddability_architecture_prefix_status_2026-06-17.md")
ARCHITECTURE_DOC = Path("docs/history/v4_preparatory_embedding/v3_0_embeddability_architecture_strategy.md")
REPORTS = {
    "metadata_readiness": Path("docs/reports/goal4594_v3_0_m195_embeddability_metadata_readiness_refresh_2026-06-17.json"),
    "prefix_stage": Path("docs/reports/goal4595_v3_0_m196_c_abi_prefix_stage_2026-06-17.json"),
    "doctor_prefix_stage": Path("docs/reports/goal4596_v3_0_m197_source_tree_doctor_prefix_stage_2026-06-17.json"),
    "prefix_python_ctypes": Path("docs/reports/goal4597_v3_0_m198_prefix_stage_python_ctypes_smoke_2026-06-17.json"),
}


def _load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def _current_progress_goal_number(doc: str) -> int | None:
    match = re.search(r"As of Goal(\d+)", doc)
    return int(match.group(1)) if match else None


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    architecture = (root / ARCHITECTURE_DOC).read_text(encoding="utf-8")
    reports = {name: _load_json(root, path) for name, path in REPORTS.items()}
    progress_goal = _current_progress_goal_number(architecture)
    status_matrix = {
        "source_tree_stage_archive": reports["metadata_readiness"]["status_matrix"]["source_tree_stage_archive"],
        "prefix_layout_stage": "validated"
        if reports["prefix_stage"]["claim_boundary"]["prefix_layout_stage_authorized"]
        else "blocked",
        "source_tree_doctor_prefix_stage": reports["doctor_prefix_stage"]["status"],
        "prefix_python_ctypes_examples": "validated"
        if reports["prefix_python_ctypes"]["claim_boundary"]["prefix_python_ctypes_stage_authorized"]
        else "blocked",
        "host_external_runtime_metadata": reports["metadata_readiness"]["status_matrix"][
            "host_external_runtime_metadata"
        ],
        "cuda_buffer_descriptor_import_export": reports["metadata_readiness"]["status_matrix"][
            "cuda_buffer_descriptor_import_export"
        ],
        "device_buffer_query_route": "blocked",
        "external_cuda_stream_ordering": "blocked",
        "generated_language_bindings": "blocked",
        "packaged_sdk": "blocked",
        "stable_abi": "blocked_until_1_0_gates",
        "release": "blocked",
    }
    checks = {
        "all_required_reports_accept": all(not tuple(report.get("failed_checks", ())) for report in reports.values()),
        "architecture_status_at_or_beyond_goal4597": progress_goal is not None
        and progress_goal >= 4597,
        "architecture_names_prefix_stage_target": "make stage-c-api-prefix" in architecture,
        "architecture_names_prefix_pkg_config_proof": "Prefix-layout `pkg-config` proof" in architecture,
        "architecture_names_doctor_prefix_stage": "Source-tree doctor coverage for the prefix-stage target"
        in architecture,
        "architecture_names_prefix_python_ctypes_smoke": "Prefix-stage Python `ctypes` smoke" in architecture,
        "architecture_preserves_no_sdk_install_release_boundary": "packaged SDK wording" in architecture
        and "system install or package-manager wording" in architecture
        and "or V3 release wording" in architecture,
        "prefix_stage_authorized_but_not_system_install": reports["prefix_stage"]["claim_boundary"][
            "prefix_layout_stage_authorized"
        ]
        is True
        and reports["prefix_stage"]["claim_boundary"]["system_install_authorized"] is False,
        "prefix_python_ctypes_authorized_but_not_generated_package": reports["prefix_python_ctypes"][
            "claim_boundary"
        ]["prefix_python_ctypes_stage_authorized"]
        is True
        and reports["prefix_python_ctypes"]["claim_boundary"]["generated_python_package_authorized"] is False,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4598 / V3 M199",
        "status": "embeddability_architecture_prefix_status_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "status_matrix": status_matrix,
        "reports": {name: path.as_posix() for name, path in REPORTS.items()},
        "claim_boundary": {
            "system_install_authorized": False,
            "package_manager_artifact_authorized": False,
            "packaged_sdk_authorized": False,
            "generated_python_package_authorized": False,
            "stable_abi_authorized": False,
            "device_buffer_query_route_authorized": False,
            "external_cuda_stream_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4598 refreshes the embeddability architecture status after the "
            "prefix-stage work. The architecture document now reflects the "
            "`stage-c-api-prefix` layout proof, source-tree doctor coverage, and "
            "prefix-stage Python `ctypes` smoke while preserving the boundary: "
            "no system install, package-manager artifact, packaged SDK, "
            "generated package, stable ABI, device-buffer query route, external "
            "CUDA stream, or release wording is authorized."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4598 / V3 M199 Embeddability Architecture Prefix Status",
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
            "- Prefix-layout stage and prefix-stage Python `ctypes` smoke are now documented and validated.",
            "- System install, package-manager artifact, packaged SDK, generated package, stable ABI, device-buffer query route, external CUDA stream, and release wording remain blocked.",
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
