from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.embeddability_readiness_packet.goal4580.v1"
OUT_JSON = Path("docs/reports/goal4580_v3_0_m181_embeddability_readiness_packet_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4580_v3_0_m181_embeddability_readiness_packet_2026-06-17.md")
MANIFEST = Path("docs/learn/v3_0_c_abi_symbol_manifest_v0_1_3.json")
STABILITY = Path("docs/learn/v3_0_c_abi_stability_policy.md")
C_ABI_DRAFT = Path("docs/learn/v3_0_c_abi_draft.md")
STAGING = Path("docs/learn/v3_0_c_abi_staging_contract.md")
REPORTS = {
    "header_compile": Path("docs/reports/goal4551_v3_0_m152_c_abi_header_compile_smoke_2026-06-17.json"),
    "stub_library": Path("docs/reports/goal4552_v3_0_m153_c_abi_stub_library_2026-06-17.json"),
    "c_client": Path("docs/reports/goal4553_v3_0_m154_c_abi_c_client_smoke_2026-06-17.json"),
    "export_audit": Path("docs/reports/goal4556_v3_0_m157_c_abi_exported_symbol_audit_2026-06-17.json"),
    "host_aabb2": Path("docs/reports/goal4558_v3_0_m159_c_abi_host_aabb2_query_proof_2026-06-17.json"),
    "staging_bundle": Path("docs/reports/goal4576_v3_0_m177_c_abi_staging_bundle_2026-06-17.json"),
    "pkg_config": Path("docs/reports/goal4577_v3_0_m178_c_abi_pkg_config_stage_2026-06-17.json"),
    "capabilities": Path("docs/reports/goal4578_v3_0_m179_c_abi_capability_queries_2026-06-17.json"),
    "direct_link": Path("docs/reports/goal4579_v3_0_m180_c_abi_direct_link_example_2026-06-17.json"),
}


def _load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    manifest = _load_json(root, MANIFEST)
    reports = {name: _load_json(root, path) for name, path in REPORTS.items()}
    stability = (root / STABILITY).read_text(encoding="utf-8")
    c_abi = (root / C_ABI_DRAFT).read_text(encoding="utf-8")
    staging = (root / STAGING).read_text(encoding="utf-8")
    status_matrix = {
        "draft_c_header": "ready_source_tree_draft",
        "shared_library_build": "ready_source_tree_draft",
        "exported_symbol_manifest": "ready_draft_0_1_3",
        "host_aabb2_query": "validated_host_only",
        "c_dlopen_example": "validated",
        "staged_bundle": "validated_source_tree_stage",
        "staged_pkg_config": "validated_source_tree_stage",
        "direct_link_example": "validated",
        "capability_queries": "validated_current_surface",
        "stable_abi": "blocked_until_1_0_gates",
        "system_install_or_packaged_sdk": "blocked",
        "language_bindings": "not_generated",
        "device_buffer_c_abi": "blocked",
        "optix_embree_c_abi_queries": "blocked",
    }
    checks = {
        "manifest_is_current_0_1_3_with_18_symbols": manifest["abi_version"] == "0.1.3"
        and len(manifest["symbols"]) == 18,
        "all_required_reports_accept": all(not tuple(report.get("failed_checks", ())) for report in reports.values()),
        "staging_bundle_runtime_ok": reports["staging_bundle"]["stage_result"]["ok"],
        "pkg_config_direct_link_smoke_ok": reports["pkg_config"]["pkg_config_smoke"]["ok"],
        "direct_link_example_smoke_ok": reports["direct_link"]["direct_link_smoke"]["ok"],
        "capability_queries_runtime_ok": reports["capabilities"]["runtime_build"]["ok"],
        "stability_policy_blocks_stable_sdk": "not frozen" in stability
        and "not enough by itself to satisfy this 1.0 requirement" in stability,
        "draft_docs_name_current_capability_and_staging_surface": "Goal4578" in c_abi
        and "Goal4579" in c_abi
        and "make stage-c-api" in staging,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4580 / V3 M181",
        "status": "embeddability_readiness_packet_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "status_matrix": status_matrix,
        "reports": {name: path.as_posix() for name, path in REPORTS.items()},
        "claim_boundary": {
            "stable_abi_authorized": False,
            "packaged_sdk_authorized": False,
            "language_binding_ready": False,
            "device_buffer_c_abi_authorized": False,
            "optix_embree_c_abi_query_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4580 consolidates the V3 embeddability state after the C ABI, "
            "staging, pkg-config, capability-query, and direct-link example work. "
            "The source-tree draft is usable for host AABB2 C embedding experiments, "
            "but stable ABI, packaged SDK, language bindings, device-buffer routes, "
            "and OptiX/Embree C ABI query execution remain explicitly blocked."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4580 / V3 M181 Embeddability Readiness Packet",
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
            "- Ready means source-tree draft readiness only.",
            "- Stable ABI, packaged SDK, language bindings, device-buffer C ABI, OptiX/Embree C ABI query execution, and release claims remain blocked.",
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
