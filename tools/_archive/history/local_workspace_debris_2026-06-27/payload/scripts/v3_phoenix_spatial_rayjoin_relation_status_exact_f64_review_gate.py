from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

INTAKE_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.json"
EXACT_EXECUTOR_INTAKE_JSON = (
    ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_exact_executor_intake_2026-06-21.json"
)
M5_AUTHOR_SUMMARY_JSON = (
    ROOT
    / "docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620"
    / "m5_pip_point_location_parity_filtered_100k"
    / "summary.json"
)
AUTHOR_BASIS_JSON = (
    ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.json"
)
ADVERSE_SUBSET_JSON = (
    ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_adverse_subset_2026-06-21.json"
)
CALL_FOR_REVIEW = ROOT / "docs/reviews/call_for_review_phoenix_v3_spatial_relation_status_exact_f64_intake_2026-06-21.md"
CLAUDE_UNAVAILABLE = ROOT / "docs/reviews/claude_unavailable_phoenix_v3_spatial_relation_status_exact_f64_intake_2026-06-21.md"
GEMINI_ATTEMPT = ROOT / "docs/reviews/gemini_phoenix_v3_spatial_relation_status_exact_f64_intake_review_2026-06-21.md"
EXTERNAL_BLOCKED = ROOT / "docs/reviews/external_ai_blocked_phoenix_v3_spatial_relation_status_exact_f64_intake_2026-06-21.md"
CODEX_REVIEW = ROOT / "docs/reviews/codex_phoenix_v3_spatial_relation_status_exact_f64_intake_blocking_review_2026-06-21.md"

OUT_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_review_gate_2026-06-21.json"
OUT_MD = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_review_gate_2026-06-21.md"


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_packet() -> dict[str, Any]:
    intake = _load_json(INTAKE_JSON)
    exact_executor_intake = _load_json(EXACT_EXECUTOR_INTAKE_JSON)
    m5_author = _load_json(M5_AUTHOR_SUMMARY_JSON)
    author_basis = _load_json(AUTHOR_BASIS_JSON)
    adverse_subset = _load_json(ADVERSE_SUBSET_JSON)
    claude_text = _read(CLAUDE_UNAVAILABLE)
    gemini_text = _read(GEMINI_ATTEMPT)
    external_text = _read(EXTERNAL_BLOCKED)
    codex_text = _read(CODEX_REVIEW)

    checks = {
        "intake_exists": INTAKE_JSON.exists(),
        "intake_status_not_m7": intake.get("status")
        == "spatial_rayjoin_relation_status_exact_f64_device_scalar_count_intake_not_m7",
        "intake_m7_promotion_false": intake.get("m7_promotion_authorized") is False,
        "intake_release_false": intake.get("release_authorized") is False,
        "intake_rtdl_beats_rayjoin_false": intake.get("rtdl_beats_rayjoin_claim_authorized") is False,
        "intake_exact_count_47262": int(intake.get("current_exact_count", -1)) == 47262,
        "intake_material_internal_delta": float(
            intake["comparison_vs_exact_executor"]["prepared_query_speedup_vs_exact_executor"]
        )
        > 3.6,
        "call_for_review_exists": CALL_FOR_REVIEW.exists(),
        "claude_unavailable_record_exists": CLAUDE_UNAVAILABLE.exists()
        and "No Claude review verdict is claimed" in claude_text,
        "gemini_attempt_record_exists": GEMINI_ATTEMPT.exists()
        and "IneligibleTierError" in gemini_text,
        "external_blocked_record_exists": EXTERNAL_BLOCKED.exists()
        and "external_ai_review_blocked_not_2ai_consensus" in external_text,
        "codex_blocking_review_exists": CODEX_REVIEW.exists()
        and "`approve-as-intake`" in codex_text,
        "codex_review_blocks_m7": "not-M7" in codex_text and "M7 promotion" in codex_text,
        "adverse_subset_packet_exists": ADVERSE_SUBSET_JSON.exists(),
        "adverse_subset_status_pass_not_m7": adverse_subset.get("status")
        == "spatial_rayjoin_relation_status_exact_f64_adverse_subset_parity_pass_not_m7",
        "adverse_subset_closes_only_parity_blocker": (
            adverse_subset.get("adverse_subset_parity_closes_blocker") is True
            and adverse_subset.get("m7_qualified_release_rows_added") == 0
            and adverse_subset.get("m7_promotion_authorized") is False
            and adverse_subset.get("release_authorized") is False
            and adverse_subset.get("public_speedup_claim_authorized") is False
            and adverse_subset.get("rtdl_beats_rayjoin_claim_authorized") is False
            and adverse_subset.get("true_zero_copy_claim_authorized") is False
        ),
        "adverse_subset_failed_checks_empty": adverse_subset.get("failed_checks") == [],
        "adverse_subset_row_count_six_consistent": (
            adverse_subset.get("row_count") == 6 and adverse_subset.get("row_count_consistent") is True
        ),
        "exact_executor_intake_exists": EXACT_EXECUTOR_INTAKE_JSON.exists(),
        "exact_executor_prior_author_gap_not_direct": exact_executor_intake["prior_author_gap"][
            "direct_current_packet_comparison_authorized"
        ]
        is False,
        "m5_author_summary_exists": M5_AUTHOR_SUMMARY_JSON.exists(),
        "m5_author_query_count_is_prior_100k": int(m5_author["protocol"]["point_count"]) == 100000,
        "m5_author_scope_is_different_from_current_exact_f64": (
            m5_author["protocol"]["query_generation"] == "backend_parity_filtered_random_bbox"
            and intake["count_mode"] == "relation_status_corrected_executor_validated"
            and intake["current_exact_count"] == 47262
        ),
        "author_basis_packet_exists": AUTHOR_BASIS_JSON.exists(),
        "author_basis_status_present_not_m7": author_basis.get("status")
        == "spatial_rayjoin_same_county_author_timing_present_not_m7",
        "author_basis_same_dataset_timing_present": author_basis.get(
            "same_dataset_author_timing_basis_present"
        )
        is True,
        "author_basis_result_count_not_printed": author_basis.get("author_result_count_printed") is False
        and author_basis.get("author_result_count_parity_verified") is False,
        "author_basis_keeps_claims_false": author_basis.get("m7_promotion_authorized") is False
        and author_basis.get("release_authorized") is False
        and author_basis.get("rtdl_beats_rayjoin_claim_authorized") is False,
        "author_basis_records_author_query_faster": author_basis.get("comparison", {}).get(
            "rayjoin_author_query_speedup_vs_rtdl_exact_f64_prepared_query", 0.0
        )
        > 1.0,
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    adverse_subset_parity_closed = all(
        checks[name]
        for name in (
            "adverse_subset_packet_exists",
            "adverse_subset_status_pass_not_m7",
            "adverse_subset_closes_only_parity_blocker",
            "adverse_subset_failed_checks_empty",
            "adverse_subset_row_count_six_consistent",
        )
    )

    blockers = [
        "external_ai_review_missing",
        "codex_consensus_response_missing_after_external_review",
        "rayjoin_author_result_count_not_printed_or_public_scope_review_missing",
        "rayjoin_author_query_faster_than_rtdl_exact_f64_query",
        "route_name_semantically_stale_relation_status_corrected",
        "public_wording_review_missing",
    ]
    if not adverse_subset_parity_closed:
        blockers.insert(3, "adverse_subset_parity_missing")

    author_timing_basis = {
        "status": "present_but_not_m7_author_query_faster_count_not_printed",
        "same_dataset_author_timing_basis_present": True,
        "current_candidate": {
            "dataset": intake["dataset"],
            "count_mode": intake["count_mode"],
            "exact_count": intake["current_exact_count"],
            "comparison_basis": "RTDL exact-f64 native scalar-count versus prior RTDL exact executor",
            "prepared_query_speedup_vs_prior_rtdl_exact_executor": intake["comparison_vs_exact_executor"][
                "prepared_query_speedup_vs_exact_executor"
            ],
            "runner_wall_speedup_vs_prior_rtdl_exact_executor": intake["comparison_vs_exact_executor"][
                "runner_wall_speedup_vs_exact_executor"
            ],
        },
        "same_dataset_author_evidence": {
            "source": _rel(AUTHOR_BASIS_JSON),
            "status": author_basis["status"],
            "author_query_ms": author_basis["author_run"]["query_ms"],
            "author_query_point_count": author_basis["author_run"][
                "query_point_count_from_optix_launch_width"
            ],
            "author_result_count_printed": author_basis["author_result_count_printed"],
            "author_result_count_parity_verified": author_basis["author_result_count_parity_verified"],
            "rayjoin_author_query_speedup_vs_rtdl_exact_f64_prepared_query": author_basis[
                "comparison"
            ]["rayjoin_author_query_speedup_vs_rtdl_exact_f64_prepared_query"],
        },
        "prior_author_evidence": {
            "source": _rel(M5_AUTHOR_SUMMARY_JSON),
            "scope": exact_executor_intake["prior_author_gap"]["scope"],
            "direct_current_packet_comparison_authorized": exact_executor_intake["prior_author_gap"][
                "direct_current_packet_comparison_authorized"
            ],
            "base_cdb": m5_author["protocol"]["base_cdb"],
            "query_cdb": m5_author["protocol"]["query_cdb"],
            "query_generation": m5_author["protocol"]["query_generation"],
            "query_count": m5_author["protocol"]["point_count"],
            "rayjoin_timer": m5_author["comparison_methodology"]["rayjoin_timer"],
            "rtdl_total_timer": m5_author["comparison_methodology"]["rtdl_total_timer"],
            "rtdl_native_timer": m5_author["comparison_methodology"]["rtdl_native_timer"],
            "timing_basis_note": m5_author["comparison_methodology"]["timing_basis_note"],
            "rayjoin_rt_speedup_vs_rtdl_optix": m5_author["comparison"][
                "rayjoin_rt_speedup_vs_rtdl_optix"
            ],
            "rayjoin_rt_speedup_vs_rtdl_optix_native_traversal": m5_author["comparison"][
                "rayjoin_rt_speedup_vs_rtdl_optix_native_traversal"
            ],
        },
        "why_not_m7": (
            "A same-dataset RayJoin author timing basis now exists for br_county.cdb/br_county.cdb, "
            "but it does not promote the Spatial row: RayJoin author Query is faster than the current "
            "RTDL exact-f64 prepared-query path, query_exec does not print a result count in this run, "
            "and external/public wording review is still missing."
        ),
        "required_evidence_before_m7": (
            "External AI review with an actual approve/block verdict",
            "Codex consensus response after external review",
            "Public scope review for the fact that RayJoin author Query is faster on this same-dataset timing basis",
            "An author result-count/parity basis, or explicit wording that refuses count-equivalence claims",
            "exact row-count/parity evidence for the same dataset and predicate",
            "external public wording review that keeps RTDL-beats-RayJoin false unless the same-dataset basis proves it",
        ),
    }
    checks.update(
        {
            "author_timing_basis_marks_present": author_timing_basis[
                "same_dataset_author_timing_basis_present"
            ]
            is True,
            "author_timing_basis_status_present_not_m7": author_timing_basis["status"]
            == "present_but_not_m7_author_query_faster_count_not_printed",
            "author_timing_same_dataset_evidence_not_m7": author_timing_basis[
                "same_dataset_author_evidence"
            ]["author_result_count_printed"]
            is False
            and author_timing_basis["same_dataset_author_evidence"][
                "rayjoin_author_query_speedup_vs_rtdl_exact_f64_prepared_query"
            ]
            > 1.0,
            "author_timing_prior_evidence_still_not_direct_current_packet": author_timing_basis[
                "prior_author_evidence"
            ]["direct_current_packet_comparison_authorized"]
            is False,
            "author_timing_requires_public_wording_review": any(
                "external public wording review" in item
                for item in author_timing_basis["required_evidence_before_m7"]
            ),
        }
    )
    failed_checks = [name for name, passed in checks.items() if not passed]

    return {
        "tool": "v3_phoenix_spatial_rayjoin_relation_status_exact_f64_review_gate",
        "status": "spatial_rayjoin_relation_status_exact_f64_review_blocked_not_m7",
        "generic_capability": intake["generic_capability"],
        "intake_status": intake["status"],
        "external_review_status": "blocked_no_external_ai_verdict",
        "codex_review_status": "approve_as_intake_blocks_m7",
        "m7_candidate_reopen_authorized": False,
        "m7_promotion_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "internal_material_delta_vs_exact_executor": {
            "prepared_query_speedup": intake["comparison_vs_exact_executor"][
                "prepared_query_speedup_vs_exact_executor"
            ],
            "runner_wall_speedup": intake["comparison_vs_exact_executor"]["runner_wall_speedup_vs_exact_executor"],
        },
        "author_timing_basis": author_timing_basis,
        "required_blockers_before_m7": blockers,
        "adverse_subset_parity_closed": adverse_subset_parity_closed,
        "adverse_subset_packet": _rel(ADVERSE_SUBSET_JSON),
        "review_records": {
            "call_for_review": _rel(CALL_FOR_REVIEW),
            "claude_unavailable": _rel(CLAUDE_UNAVAILABLE),
            "gemini_attempt": _rel(GEMINI_ATTEMPT),
            "external_ai_blocked": _rel(EXTERNAL_BLOCKED),
            "codex_blocking_review": _rel(CODEX_REVIEW),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "next_engine_action": (
            "Keep Spatial exact-f64 as intake evidence only. Retry external AI review when a working channel "
            "is available; otherwise continue Phoenix on another reusable generic engine route without "
            "promoting Spatial."
        ),
        "goal_level_decision_audit": {
            "decision": "Gate the Spatial exact-f64 repair as review-blocked/not-M7 despite material internal speedup.",
            "was_i_foolish": (
                "No. The exact-f64 route is promising, but review, author-basis, and adverse-subset gates are "
                "still missing."
            ),
            "foolish_actions": (
                "The foolish action would be to turn a 3.680x internal comparison into M7 or release wording "
                "without external review and author-basis evidence."
            ),
            "other_path": (
                "I could have kept optimizing Spatial immediately. That risks single-route fixation and does "
                "not close the review discipline gap."
            ),
            "different_path_now": (
                "Preserve Spatial as a blocked intake, then proceed to the next generic engine route while "
                "leaving this review gate as the condition for future M7 discussion."
            ),
        },
    }


def render_markdown(packet: dict[str, Any]) -> str:
    delta = packet["internal_material_delta_vs_exact_executor"]
    author = packet["author_timing_basis"]
    prior = author["prior_author_evidence"]
    lines = [
        "# Phoenix V3 Spatial Relation-Status Exact-F64 Review Gate",
        "",
        f"Status: `{packet['status']}`",
        "",
        "This packet intentionally blocks M7 promotion. The exact-f64 repair is",
        "material generic-engine evidence, but external review and author-basis",
        "requirements are still missing.",
        "",
        "## Current Verdict",
        "",
        f"- Intake status: `{packet['intake_status']}`",
        f"- External review status: `{packet['external_review_status']}`",
        f"- Codex review status: `{packet['codex_review_status']}`",
        "- M7 candidate reopen authorized: `false`",
        "- M7 promotion authorized: `false`",
        "- Release authorized: `false`",
        "",
        "## Internal Delta Preserved",
        "",
        f"- Prepared-query speedup versus prior RTDL exact executor: `{delta['prepared_query_speedup']:.3f}x`",
        f"- Runner-wall speedup versus prior RTDL exact executor: `{delta['runner_wall_speedup']:.3f}x`",
        "",
        "These are internal RTDL-vs-RTDL comparisons, not RayJoin author, paper,",
        "whole-app, broad V3-over-V2, or release claims.",
        "",
        "## Author Timing Basis",
        "",
        f"- Status: `{author['status']}`",
        f"- Same-dataset author timing present: `{str(author['same_dataset_author_timing_basis_present']).lower()}`",
        f"- Current candidate dataset: `{author['current_candidate']['dataset']}`",
        f"- Current candidate exact count: `{author['current_candidate']['exact_count']}`",
        f"- Current comparison basis: `{author['current_candidate']['comparison_basis']}`",
        f"- Same-dataset author evidence source: `{author['same_dataset_author_evidence']['source']}`",
        f"- Same-dataset author Query timer: `{author['same_dataset_author_evidence']['author_query_ms']:.6f} ms`",
        f"- Same-dataset author query points: `{author['same_dataset_author_evidence']['author_query_point_count']}`",
        f"- Same-dataset author result count printed: `{str(author['same_dataset_author_evidence']['author_result_count_printed']).lower()}`",
        f"- RayJoin author Query speedup vs RTDL exact-f64 prepared query: `{author['same_dataset_author_evidence']['rayjoin_author_query_speedup_vs_rtdl_exact_f64_prepared_query']:.3f}x`",
        f"- Prior author evidence source: `{prior['source']}`",
        f"- Prior author evidence scope: `{prior['scope']}`",
        f"- Prior author query count: `{prior['query_count']}`",
        f"- Prior author direct-current comparison authorized: `{str(prior['direct_current_packet_comparison_authorized']).lower()}`",
        "",
        author["why_not_m7"],
        "",
        "Required before M7:",
        "",
    ]
    for item in author["required_evidence_before_m7"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Adverse-Subset Parity",
            "",
            f"- Closed: `{str(packet['adverse_subset_parity_closed']).lower()}`",
            f"- Packet: `{packet['adverse_subset_packet']}`",
            "- This closes only the adverse-subset parity blocker; it does not",
            "  authorize M7, release, or public speedup wording.",
            "",
            "## Required Blockers Before M7",
            "",
        ]
    )
    for blocker in packet["required_blockers_before_m7"]:
        lines.append(f"- `{blocker}`")
    lines.extend(["", "## Review Records", ""])
    for label, path in packet["review_records"].items():
        lines.append(f"- {label}: `{path}`")
    lines.extend(["", "## Checks", ""])
    for name, passed in packet["checks"].items():
        lines.append(f"- `{name}`: `{str(bool(passed)).lower()}`")
    audit = packet["goal_level_decision_audit"]
    lines.extend(
        [
            "",
            f"Failed checks: `{packet['failed_checks']}`",
            "",
            "## Goal-Level Decision Self-Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            f"1. Was I foolish? {audit['was_i_foolish']}",
            f"2. If yes, what actions made the decision foolish? {audit['foolish_actions']}",
            f"3. Was there another path? {audit['other_path']}",
            f"4. Can I now try a different path? {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    packet = build_packet()
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(packet), encoding="utf-8")
    print(json.dumps({"status": packet["status"], "failed_checks": packet["failed_checks"]}, indent=2))


if __name__ == "__main__":
    main()
