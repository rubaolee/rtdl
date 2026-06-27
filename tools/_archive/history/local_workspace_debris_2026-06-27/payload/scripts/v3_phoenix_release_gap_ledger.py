#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import v3_phoenix_external_verdict_intake
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_phoenix_external_verdict_intake

try:
    import v3_phoenix_objective_conformance_gate
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_phoenix_objective_conformance_gate

try:
    import v3_phoenix_release_readiness_gate
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_phoenix_release_readiness_gate

try:
    import v3_phoenix_major_performance_mandate_gate
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_phoenix_major_performance_mandate_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_release_gap_ledger_2026-06-22.json"


def _gate_path(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _done_item(item_id: str, evidence: str, note: str) -> dict[str, str]:
    return {"id": item_id, "state": "done", "evidence": evidence, "note": note}


def _remaining_item(item_id: str, severity: str, evidence: str, required_action: str) -> dict[str, str]:
    return {
        "id": item_id,
        "state": "remaining",
        "severity": severity,
        "evidence": evidence,
        "required_action": required_action,
    }


def build_payload() -> dict[str, Any]:
    readiness = v3_phoenix_release_readiness_gate.build_payload()
    objective = v3_phoenix_objective_conformance_gate.build_payload()
    external = v3_phoenix_external_verdict_intake.build_payload()
    major = v3_phoenix_major_performance_mandate_gate.build_payload()

    readiness_evidence = readiness.get("evidence", {})
    objective_evidence = objective.get("evidence", {})

    done = [
        _done_item(
            "current_surface_width",
            "docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json",
            "13 current M7/supplemental rows across 9 capability families.",
        ),
        _done_item(
            "objective_capability_mapping",
            "docs/rebuild/v3/phoenix_v3_objective_conformance_gate_2026-06-22.json",
            "RayDB, RTDBSCAN, Spatial RayJoin, Triangle, and RTNN objectives map to reusable capability rows.",
        ),
        _done_item(
            "unsupported_claim_boundaries",
            "scripts/v3_release_wording_gate.py",
            "Release, broad V3-over-V2, package-install, hardware portability, V4/C ABI, and embedding claims remain blocked.",
        ),
        _done_item(
            "source_tree_pod_gated_scope",
            "docs/rebuild/v3/phoenix_v3_install_reproducibility_gate_2026-06-21.json",
            "Scoped source-tree/pod-gated thirteen-row installer blocker is closed, but general package install is not claimed.",
        ),
        _done_item(
            "single_rtx_hardware_scope",
            "docs/rebuild/v3/phoenix_v3_secondary_platform_gate_2026-06-21.json",
            "Secondary-platform blocker is closed only by a reviewed single-RTX hardware waiver.",
        ),
        _done_item(
            "local_validation",
            "docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_aabb_runner_m2_20260622.json",
            "Full v3_rebuild matrix is green: 111 modules / 557 tests OK.",
        ),
        _done_item(
            "external_scoped_packet_verdict",
            "docs/reviews/claude_phoenix_v3_aggregate_release_readiness_13_row_after_dossier_review_2026-06-22.md",
            "Claude external aggregate review returned release_ready for the exact source_tree_pod_gated_thirteen_row scope; this is scoped evidence, not V3 major release authorization.",
        ),
        _done_item(
            "current_core_gap_external_redirect",
            "docs/rebuild/v3/phoenix_v3_core_gaps_external_verdict_status_2026-06-22.md",
            "Claude core-gap review is recorded as approve_blocked_not_release; continue non-release engineering, redirect effort to Gap 1, and do not authorize public speedup claims.",
        ),
    ]

    remaining: list[dict[str, str]] = [
        _remaining_item(
            "major_runtime_performance_mandate",
            "P0",
            "docs/rebuild/v3/phoenix_v3_redo_mandate_major_version_performance_2026-06-22.md",
            "Prove broad V2.x performance superiority across serious benchmark-app stress tests and express wins as reusable RTRDL runtime capabilities.",
        )
    ]

    boundaries = [
        "Do not claim V3 broadly beats V2.x.",
        "Do not claim package install or SDK readiness.",
        "Do not claim multi-GPU or broad hardware portability.",
        "Do not claim public Spatial speedup, RTDL-beats-RayJoin, or paper reproduction.",
        "Do not claim true zero-copy, V4 C ABI, embedding, or multi-language host support.",
        "Do not turn app-specific native engines into the V3 release surface.",
    ]

    checks = {
        "readiness_redo_required": readiness.get("status") == "redo_required",
        "readiness_release_false": readiness.get("release_authorized") is False,
        "major_performance_redo_required": major.get("status") == "redo_required",
        "objective_conformance_passed_not_release": (
            objective.get("status") == "objective_conformance_passed_not_release"
        ),
        "objective_coverage_5_of_5": (
            objective_evidence.get("objective_required_capability_coverage_count")
            == objective_evidence.get("objective_required_capability_count")
            == 5
        ),
        "external_verdict_obtained": external.get("status") == "external_verdict_obtained",
        "external_verdict_release_false": external.get("release_authorized") is False,
        "external_verdict_scoped_packet_true": external.get("scoped_packet_authorized") is True,
        "current_core_gap_external_verdict_blocks_release": (
            readiness_evidence.get("core_gaps_external_verdict") == "approve_blocked_not_release"
            and readiness_evidence.get("core_gaps_external_release_authorized") is False
        ),
        "set_a_set_b_proposal_only_not_authorization": (
            readiness_evidence.get("set_a_set_b_release_bar_proposal_status")
            == "proposal_only_not_authorization"
        ),
        "remaining_gap_count_is_one": len(remaining) == 1,
        "done_item_count_is_eight": len(done) == 8,
        "claim_boundaries_present": len(boundaries) == 6,
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    status = "redo_required_major_performance_p0_open" if not failed_checks else "fail"

    return {
        "tool": "v3_phoenix_release_gap_ledger",
        "status": status,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "failed_checks": failed_checks,
        "checks": checks,
        "done": done,
        "remaining": remaining,
        "claim_boundaries": boundaries,
        "evidence": {
            "readiness_status": readiness.get("status"),
            "readiness_blocking_reasons": readiness.get("blocking_reasons", []),
            "readiness_path": _gate_path(
                ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_release_readiness_gate_2026-06-21.json"
            ),
            "objective_conformance_status": objective.get("status"),
            "objective_conformance_path": _gate_path(
                ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_objective_conformance_gate_2026-06-22.json"
            ),
            "objective_capabilities_covered": objective_evidence.get(
                "objective_required_capabilities_covered", []
            ),
            "external_verdict_intake_status": external.get("status"),
            "external_verdict_intake_path": _gate_path(
                ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_external_verdict_intake_2026-06-22.json"
            ),
            "valid_external_verdict_obtained": external.get("valid_external_verdict_obtained"),
            "accepted_external_verdict": external.get("accepted_verdict"),
            "scoped_packet_authorized": external.get("scoped_packet_authorized"),
            "current_core_gap_external_verdict": readiness_evidence.get("core_gaps_external_verdict"),
            "current_core_gap_external_status_line": readiness_evidence.get("core_gaps_external_status_line"),
            "current_core_gap_external_release_authorized": readiness_evidence.get(
                "core_gaps_external_release_authorized"
            ),
            "current_core_gap_external_review_path": readiness_evidence.get("core_gaps_external_review_path"),
            "current_core_gap_external_status_path": readiness_evidence.get("core_gaps_external_status_path"),
            "set_a_set_b_release_bar_proposal_status": readiness_evidence.get(
                "set_a_set_b_release_bar_proposal_status"
            ),
            "set_a_set_b_release_bar_proposal_path": readiness_evidence.get(
                "set_a_set_b_release_bar_proposal_path"
            ),
            "set_a_set_b_release_bar_proposal_precondition": readiness_evidence.get(
                "set_a_set_b_release_bar_proposal_precondition"
            ),
            "major_performance_mandate_status": major.get("status"),
            "major_performance_mandate_blocking_reasons": major.get("blocking_reasons", []),
            "reference_file_count": readiness_evidence.get("aggregate_13_row_review_packet_reference_file_count"),
        },
        "next_action_policy": {
            "if_external_verdict_release_ready": "treat it as scoped packet evidence unless the major performance mandate also passes",
            "if_external_verdict_blocked": "fix the named P0/P1 blockers, rerun gates, and request a new bounded review",
            "if_external_tool_no_output": (
                "record the no-output attempt and continue non-release V3 cleanup without changing release flags"
            ),
        },
        "decision_audit": _decision_audit(),
    }


def _decision_audit() -> dict[str, str]:
    return {
        "decision": "Record that Phoenix V3 still has a P0 major runtime-performance gap even after the scoped Claude verdict.",
        "was_i_foolish": "Yes. I previously treated scoped release authorization as if it closed the V3 major-version gap.",
        "foolish_actions": "The foolish action was letting row-scoped evidence and a scoped verdict replace broad V2.x runtime-performance proof.",
        "other_path": "Keep the no-remaining-P0 ledger. That would mislead the next worker and the user.",
        "different_path_now": "Keep the P0 gap machine-readable: V3 needs serious all-app runtime stress-test wins before release.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phoenix V3 release gap ledger.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 2 if payload["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
