from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.embeddability_shipping_readiness_refresh.goal4589.v1"
OUT_JSON = Path("docs/reports/goal4589_v3_0_m190_embeddability_shipping_readiness_refresh_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4589_v3_0_m190_embeddability_shipping_readiness_refresh_2026-06-17.md")
REPORTS = {
    "readiness_refresh": Path("docs/reports/goal4583_v3_0_m184_embeddability_readiness_refresh_2026-06-17.json"),
    "staging_inventory": Path("docs/reports/goal4585_v3_0_m186_c_abi_staging_inventory_refresh_2026-06-17.json"),
    "relocatable_stage": Path("docs/reports/goal4586_v3_0_m187_c_abi_pkg_config_relocatable_stage_2026-06-17.json"),
    "stage_archive": Path("docs/reports/goal4587_v3_0_m188_c_abi_stage_archive_2026-06-17.json"),
    "doctor_archive": Path("docs/reports/goal4588_v3_0_m189_source_tree_doctor_stage_archive_2026-06-17.json"),
}


def _load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    reports = {name: _load_json(root, path) for name, path in REPORTS.items()}
    status_matrix = {
        "source_tree_staging_bundle": "validated",
        "staging_inventory_all_examples": "validated_four_examples",
        "relocatable_pkg_config_stage": "validated_after_directory_move",
        "source_tree_stage_archive": "validated_extract_compile_run",
        "source_tree_doctor_archive_target": "wired",
        "minimal_python_ctypes_binding_base": "validated_lifecycle_and_host_aabb2_query",
        "generated_language_bindings": "blocked",
        "packaged_sdk": "blocked",
        "system_install": "blocked",
        "stable_abi": "blocked_until_1_0_gates",
        "device_buffer_c_abi": "blocked",
        "optix_embree_c_abi_queries": "blocked",
    }
    checks = {
        "all_required_reports_accept": all(not tuple(report.get("failed_checks", ())) for report in reports.values()),
        "readiness_refresh_preserves_minimal_ctypes_base": (
            reports["readiness_refresh"]["status_matrix"]["language_binding_base"]
            == "minimal_ctypes_examples_validated_no_generated_binding"
        ),
        "staging_inventory_has_all_examples": reports["staging_inventory"]["stage_inventory"]["all_examples_staged"],
        "relocatable_stage_smoke_ok": reports["relocatable_stage"]["relocatable_stage_smoke"]["ok"],
        "stage_archive_extract_compile_run_ok": reports["stage_archive"]["stage_archive_smoke"]["ok"]
        and reports["stage_archive"]["stage_archive_smoke"]["run_result"]["stdout"] == "direct_link_ok 0.1.3 ok",
        "doctor_archive_target_wired": reports["doctor_archive"]["doctor_surface"]["status"] == "pass"
        and "package-c-api-stage" in reports["doctor_archive"]["doctor_surface"]["detail"],
        "stage_archive_does_not_authorize_sdk": not reports["stage_archive"]["claim_boundary"]["packaged_sdk_authorized"],
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4589 / V3 M190",
        "status": "embeddability_shipping_readiness_refresh_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "status_matrix": status_matrix,
        "reports": {name: path.as_posix() for name, path in REPORTS.items()},
        "claim_boundary": {
            "packaged_sdk_authorized": False,
            "system_install_authorized": False,
            "stable_abi_authorized": False,
            "generated_language_binding_authorized": False,
            "device_buffer_c_abi_authorized": False,
            "optix_embree_c_abi_query_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4589 refreshes the embeddability shipping ledger after the "
            "relocatable pkg-config and stage-archive proofs. The current V3 "
            "source tree can build a movable C ABI stage archive and that archive "
            "can be extracted, used through pkg-config, compiled, and run. This "
            "is a verified source-tree handoff artifact; it is still not a "
            "packaged SDK, system install, stable ABI, generated language binding, "
            "device-buffer C ABI, OptiX/Embree C ABI execution surface, or release "
            "claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4589 / V3 M190 Embeddability Shipping Readiness Refresh",
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
            "- The source-tree stage archive is a movable handoff artifact, not a packaged SDK.",
            "- Stable ABI, system install, generated bindings, device-buffer C ABI, OptiX/Embree C ABI execution, and release claims remain blocked.",
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
