from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.embeddability_progress_gate.goal4569.v1"
OUT_JSON = Path("docs/reports/goal4569_v3_0_m170_embeddability_progress_gate_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4569_v3_0_m170_embeddability_progress_gate_2026-06-17.md")
STRATEGY = Path("docs/learn/v3_0_embeddability_architecture_strategy.md")
C_ABI_DRAFT = Path("docs/learn/v3_0_c_abi_draft.md")
STABILITY = Path("docs/learn/v3_0_c_abi_stability_policy.md")
SYMBOL_MANIFEST = Path("docs/learn/v3_0_c_abi_symbol_manifest_v0_1_3.json")
ZERO_COPY = Path("docs/learn/v3_0_zero_copy_interop_contract.md")
EMBEDDING_README = Path("examples/current/embedding/README.md")
MAKEFILE = Path("Makefile")
MATRIX = Path("scripts/run_test_matrix.py")
REPORTS = (
    Path("docs/reports/goal4553_v3_0_m154_c_abi_c_client_smoke_2026-06-17.json"),
    Path("docs/reports/goal4556_v3_0_m157_c_abi_exported_symbol_audit_2026-06-17.json"),
    Path("docs/reports/goal4558_v3_0_m159_c_abi_host_aabb2_query_proof_2026-06-17.json"),
    Path("docs/reports/goal4563_v3_0_m164_c_abi_aabb2_negative_runtime_2026-06-17.json"),
    Path("docs/reports/goal4567_v3_0_m168_c_abi_aabb2_layout_validation_2026-06-17.json"),
    Path("docs/reports/goal4568_v3_0_m169_zero_copy_interop_contract_2026-06-17.json"),
)


def _load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def _current_progress_goal_number(strategy: str) -> int | None:
    match = re.search(r"As of Goal(\d+)", strategy)
    return int(match.group(1)) if match else None


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    strategy = (root / STRATEGY).read_text(encoding="utf-8")
    c_abi = (root / C_ABI_DRAFT).read_text(encoding="utf-8")
    stability = (root / STABILITY).read_text(encoding="utf-8")
    zero_copy = (root / ZERO_COPY).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    matrix = (root / MATRIX).read_text(encoding="utf-8")
    manifest = _load_json(root, SYMBOL_MANIFEST)
    reports = {path.name: _load_json(root, path) for path in REPORTS}
    progress_goal = _current_progress_goal_number(strategy)
    checks = {
        "strategy_status_at_or_beyond_goal4576": progress_goal is not None
        and progress_goal >= 4576,
        "c_abi_draft_documents_host_aabb2_contract": "Current Host AABB2 Query Contract" in c_abi
        and "contiguous AABB2 rows" in c_abi,
        "c_abi_staging_surface_is_documented": "v3_0_c_abi_staging_contract.md" in c_abi
        and "make stage-c-api" in makefile
        and "make stage-c-api" in embedding,
        "stability_policy_blocks_stable_sdk": "never stable SDK" in stability
        and "not frozen" in stability,
        "symbol_manifest_is_draft_0_1_3": manifest["abi_version"] == "0.1.3"
        and manifest["stable"] is False
        and len(manifest["symbols"]) == 18,
        "embedding_readme_has_c_client_commands": "make build-c-api" in embedding
        and "c_api_aabb2_overlap_client.c" in embedding,
        "zero_copy_contract_blocks_c_abi_device_route": "does not make" in zero_copy
        and "C ABI accept device buffers" in zero_copy,
        "all_required_reports_accept": all(not tuple(report.get("failed_checks", ())) for report in reports.values()),
        "c_client_validates_real_query": reports[
            "goal4553_v3_0_m154_c_abi_c_client_smoke_2026-06-17.json"
        ]["validated_capabilities"]["host_f32_aabb2_overlap_query_validated"],
        "layout_validation_runtime_passed": reports[
            "goal4567_v3_0_m168_c_abi_aabb2_layout_validation_2026-06-17.json"
        ]["checks"]["runtime_validated_layout_cases"],
        "zero_copy_runtime_claims_blocked": reports[
            "goal4568_v3_0_m169_zero_copy_interop_contract_2026-06-17.json"
        ]["claim_boundary"]["public_true_zero_copy_claim_authorized"]
        is False,
        "v3_current_includes_progress_gate": "tests.goal4569_v3_0_m170_embeddability_progress_gate_test"
        in matrix,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    status_matrix = {
        "control_plane_host_aabb2_c_abi": "ready_source_tree_draft",
        "source_tree_c_api_stage_bundle": "validated_draft",
        "non_python_c_client": "validated",
        "exported_symbol_manifest": "draft_manifest_checked",
        "negative_and_layout_runtime": "validated",
        "source_tree_doctor_surface": "wired",
        "stable_abi": "blocked_until_1_0_gates",
        "packaged_sdk": "blocked",
        "c_abi_device_buffers": "blocked",
        "dlpack_cuda_array_interface_runtime": "readiness_contract_only",
        "optix_embree_c_abi_query": "blocked",
    }
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4569 / V3 M170",
        "status": "embeddability_progress_gate_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "status_matrix": status_matrix,
        "claim_boundary": {
            "stable_abi_authorized": False,
            "packaged_sdk_authorized": False,
            "c_abi_device_buffer_route_implemented": False,
            "optix_embree_c_abi_query_implemented": False,
            "public_zero_copy_claim_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4569 consolidates the V3 embeddability track: RTDL now has a "
            "source-tree draft C ABI with a real host AABB2 query, non-Python C "
            "client validation, symbol manifest, runtime negative/layout gates, "
            "doctor visibility, and a zero-copy interop readiness contract. "
            "Stable ABI, packaged SDK, device-buffer C ABI, OptiX/Embree C ABI "
            "queries, and public zero-copy wording remain blocked."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4569 / V3 M170 Embeddability Progress Gate",
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
            "- This is a progress gate, not a release gate.",
            "- Stable ABI, packaged SDK, device-buffer C ABI, OptiX/Embree C ABI query, and public zero-copy wording remain blocked.",
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
