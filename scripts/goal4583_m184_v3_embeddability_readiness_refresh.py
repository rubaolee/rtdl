from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.embeddability_readiness_refresh.goal4583.v1"
OUT_JSON = Path("docs/reports/goal4583_v3_0_m184_embeddability_readiness_refresh_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4583_v3_0_m184_embeddability_readiness_refresh_2026-06-17.md")
MANIFEST = Path("docs/learn/v3_0_c_abi_symbol_manifest_v0_1_3.json")
STABILITY = Path("docs/learn/v3_0_c_abi_stability_policy.md")
C_ABI_DRAFT = Path("docs/learn/v3_0_c_abi_draft.md")
STAGING = Path("docs/learn/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("examples/current/embedding/README.md")
REPORTS = {
    "m181_readiness": Path("docs/reports/goal4580_v3_0_m181_embeddability_readiness_packet_2026-06-17.json"),
    "python_ctypes_lifecycle": Path("docs/reports/goal4581_v3_0_m182_c_abi_python_ctypes_example_2026-06-17.json"),
    "python_ctypes_aabb2_query": Path("docs/reports/goal4582_v3_0_m183_c_abi_python_ctypes_aabb2_query_2026-06-17.json"),
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
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
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
        "python_ctypes_lifecycle_example": "validated_source_tree_stage",
        "python_ctypes_host_aabb2_query_example": "validated_source_tree_stage",
        "language_binding_base": "minimal_ctypes_examples_validated_no_generated_binding",
        "generated_language_bindings": "blocked",
        "stable_abi": "blocked_until_1_0_gates",
        "system_install_or_packaged_sdk": "blocked",
        "device_buffer_c_abi": "blocked",
        "optix_embree_c_abi_queries": "blocked",
    }
    checks = {
        "manifest_is_current_0_1_3_with_18_symbols": manifest["abi_version"] == "0.1.3"
        and len(manifest["symbols"]) == 18,
        "all_required_reports_accept": all(not tuple(report.get("failed_checks", ())) for report in reports.values()),
        "m181_recorded_language_binding_gap_before_refresh": (
            reports["m181_readiness"]["status_matrix"]["language_bindings"] == "not_generated"
        ),
        "python_ctypes_lifecycle_smoke_ok": reports["python_ctypes_lifecycle"]["python_ctypes_smoke"]["ok"]
        and reports["python_ctypes_lifecycle"]["python_ctypes_smoke"]["run_result"]["stdout"]
        == "python_ctypes_ok 0.1.3 ok",
        "python_ctypes_aabb2_query_smoke_ok": reports["python_ctypes_aabb2_query"]["python_ctypes_query_smoke"]["ok"]
        and reports["python_ctypes_aabb2_query"]["python_ctypes_query_smoke"]["run_result"]["stdout"]
        == "python_ctypes_hit_count=1 first_pair=(0,0)",
        "staged_bundle_and_pkg_config_remain_ok": reports["staging_bundle"]["stage_result"]["ok"]
        and reports["pkg_config"]["pkg_config_smoke"]["ok"],
        "direct_link_and_capability_queries_remain_ok": reports["direct_link"]["direct_link_smoke"]["ok"]
        and reports["capabilities"]["runtime_build"]["ok"],
        "docs_name_current_python_ctypes_surface": "Goal4581" in c_abi
        and "Goal4582" in c_abi
        and "python_ctypes_client.py" in staging
        and "python_ctypes_aabb2_query_client.py" in embedding,
        "stability_policy_still_blocks_stable_sdk": "not frozen" in stability
        and "not enough by itself to satisfy this 1.0 requirement" in stability,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4583 / V3 M184",
        "status": "embeddability_readiness_refresh_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "status_matrix": status_matrix,
        "reports": {name: path.as_posix() for name, path in REPORTS.items()},
        "claim_boundary": {
            "stable_abi_authorized": False,
            "packaged_sdk_authorized": False,
            "generated_language_binding_ready": False,
            "device_buffer_c_abi_authorized": False,
            "optix_embree_c_abi_query_authorized": False,
            "performance_wording_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4583 refreshes the embeddability readiness ledger after the "
            "Python ctypes lifecycle and host AABB2 query examples. The current "
            "source-tree draft now has C dlopen, C direct-link, pkg-config, "
            "capability-query, staged bundle, and Python ctypes host-query "
            "proofs. That upgrades the language-binding status from `not "
            "generated` to a validated minimal ctypes base, while generated "
            "bindings, stable ABI, packaged SDK, device-buffer C ABI, OptiX/Embree "
            "C ABI execution, and performance wording remain blocked."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4583 / V3 M184 Embeddability Readiness Refresh",
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
            "- The Python ctypes examples prove a minimal binding base, not a generated or packaged binding.",
            "- Stable ABI, packaged SDK, device-buffer C ABI, OptiX/Embree C ABI query execution, performance wording, and release claims remain blocked.",
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
