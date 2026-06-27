from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

EVIDENCE = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.json"
RAW_ORACLE_EVIDENCE = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_raw_oracle_evidence_2026-06-21.json"
STABILITY_EVIDENCE = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_stability_evidence_2026-06-21.json"
ROW_WORDING_GATE = (
    ROOT / "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_row_wording_gate_2026-06-21.json"
)
CALL_FOR_REVIEW = ROOT / "docs/reviews/call_for_review_phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.md"
FINAL_CALL_FOR_REVIEW = (
    ROOT / "docs/reviews/call_for_review_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md"
)
GEMINI_BLOCKED = ROOT / "docs/reviews/gemini_blocked_phoenix_v3_aabb_native_query_handle_evidence_review_2026-06-21.md"
GEMINI_STDERR = ROOT / "docs/reviews/gemini_phoenix_v3_aabb_native_query_handle_evidence_review_2026-06-21.stderr.txt"
EXTERNAL_BLOCKED = ROOT / "docs/reviews/external_ai_blocked_phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.md"
FINAL_EXTERNAL_BLOCKED = (
    ROOT / "docs/reviews/external_ai_blocked_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md"
)
CLAUDE_FINAL_REVIEW = (
    ROOT / "docs/reviews/claude_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md"
)
CLAUDE_FINAL_REVIEW_STREAM = (
    ROOT / "docs/reviews/claude_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.stream.jsonl"
)
CODEX_FINAL_CONSENSUS = (
    ROOT
    / "docs/reviews/codex_phoenix_v3_aabb_native_query_handle_final_m7_review_2ai_consensus_2026-06-21.md"
)
HUYGENS_REVIEW = ROOT / "docs/reviews/codex_subagent_huygens_phoenix_v3_aabb_native_query_handle_evidence_review_2026-06-21.md"
HUYGENS_FOLLOWUP_REVIEW = (
    ROOT / "docs/reviews/codex_subagent_huygens_phoenix_v3_aabb_native_query_handle_followup_review_2026-06-21.md"
)

OUT_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.json"
OUT_MD = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.md"


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_json_if_exists(path: Path) -> dict[str, Any] | None:
    return _load_json(path) if path.exists() else None


def _summary_git_heads(evidence: dict[str, Any]) -> list[str]:
    heads: list[str] = []
    for row in evidence.get("observed_rows", []):
        summary_path = row.get("summary_path")
        if not isinstance(summary_path, str):
            continue
        path = ROOT / summary_path
        if not path.exists():
            continue
        summary = _load_json(path)
        heads.append(str(summary.get("environment", {}).get("git_head", "")))
    return heads


def _has_stable_candidate_row_id(evidence: dict[str, Any]) -> bool:
    value = evidence.get("candidate_row_id") or evidence.get("promoted_candidate_row_id")
    return isinstance(value, str) and bool(value.strip())


def _approved_wording(row: dict[str, Any]) -> str:
    return (
        "On an NVIDIA RTX 4000 Ada Generation GPU, RTDL's OptiX native "
        "prepared-query-handle route for `AABB_INDEX_QUERY_2D range_intersection_rows` "
        f"was {float(row['optix_over_embree_cold_plus_collect_wall_speedup']):.3f}x faster "
        "than the RTDL Embree route on a jittered-grid workload with "
        f"{int(row['aabb_count']):,} AABBs and {int(row['box_query_count']):,} packed box "
        f"queries, measured as cold prepare plus collect wall time with warmup={row['warmup']} "
        f"and repeat={row['repeat']}. Query total was "
        f"{float(row['optix_over_embree_query_total_speedup']):.3f}x faster. OptiX prepare "
        "alone remains slower than Embree; the speedup applies to end-to-end prepared-session "
        "time. This result is row-scoped and does not claim Contact Manifold solver "
        "acceleration, broad AABB-index acceleration, or V3-over-V2 speedup."
    )


def build_packet() -> dict[str, Any]:
    evidence = _load_json(EVIDENCE)
    raw_oracle = _load_json_if_exists(RAW_ORACLE_EVIDENCE)
    stability = _load_json_if_exists(STABILITY_EVIDENCE)
    row_wording_gate = _load_json_if_exists(ROW_WORDING_GATE)
    call_text = _read(CALL_FOR_REVIEW)
    final_call_text = _read(FINAL_CALL_FOR_REVIEW)
    gemini_blocked_text = _read(GEMINI_BLOCKED)
    gemini_stderr_text = _read(GEMINI_STDERR)
    external_text = _read(EXTERNAL_BLOCKED)
    final_external_text = _read(FINAL_EXTERNAL_BLOCKED)
    claude_final_text = _read(CLAUDE_FINAL_REVIEW)
    codex_final_consensus_text = _read(CODEX_FINAL_CONSENSUS)
    huygens_text = _read(HUYGENS_REVIEW)
    huygens_followup_text = _read(HUYGENS_FOLLOWUP_REVIEW)
    git_heads = _summary_git_heads(evidence)

    observed_rows = evidence.get("observed_rows", [])
    speedups = [
        float(row.get("optix_over_embree_cold_plus_collect_wall_speedup", 0.0))
        for row in observed_rows
    ]
    floor = float(evidence.get("material_wall_speedup_floor", 1.2))
    raw_oracle_ok = bool(
        raw_oracle
        and raw_oracle.get("status") == "aabb_raw_oracle_pass_not_m7"
        and raw_oracle.get("raw_aabb_oracle_closes_correctness_blocker") is True
        and raw_oracle.get("checks", {}).get("all_rows_match_independent_cpu_oracle") is True
        and raw_oracle.get("checks", {}).get("optix_capacity_pressure_fail_closed_if_requested") is True
    )
    source_manifest_sha256 = str(raw_oracle.get("source_manifest_sha256", "")) if raw_oracle else ""
    source_manifest_ok = len(source_manifest_sha256) == 64
    stability_ok = bool(
        stability
        and stability.get("status") == "aabb_native_query_handle_stability_pass_not_m7"
        and stability.get("fresh_run_stability_closes_blocker") is True
    )
    row_wording_gate_closes_stable_id = bool(
        row_wording_gate
        and row_wording_gate.get("status")
        in {
            "aabb_native_query_handle_stable_row_wording_gate_ready_external_review_blocked_not_m7",
            "aabb_native_query_handle_row_wording_gate_closed_after_claude_codex_m7_review",
        }
        and row_wording_gate.get("failed_checks") == []
        and row_wording_gate.get("stable_candidate_row_id_gate_closed") is True
        and row_wording_gate.get("release_authorized") is False
    )
    has_stable_candidate_row_id = _has_stable_candidate_row_id(evidence) or row_wording_gate_closes_stable_id
    stable_candidate_row_ids = row_wording_gate.get("candidate_row_ids", []) if row_wording_gate else []
    claude_final_review_ok = bool(
        CLAUDE_FINAL_REVIEW.exists()
        and "Verdict: `approve-with-conditions`" in claude_final_text
        and "This review closes `external_ai_review_missing` and `external_public_wording_review_missing`"
        in claude_final_text
        and "codex_consensus_response_missing_after_external_review" in claude_final_text
        and "OptiX prepare alone remains slower than Embree" in claude_final_text
        and all(row_id in claude_final_text for row_id in stable_candidate_row_ids)
    )
    codex_final_consensus_ok = bool(
        CODEX_FINAL_CONSENSUS.exists()
        and "claude_codex_consensus_complete_approve_two_row_scoped_m7_rows"
        in codex_final_consensus_text
        and "OptiX prepare alone remains slower than Embree" in codex_final_consensus_text
        and source_manifest_sha256
        and source_manifest_sha256 in codex_final_consensus_text
        and all(row_id in codex_final_consensus_text for row_id in stable_candidate_row_ids)
    )
    p1_conditions_applied = bool(
        claude_final_review_ok
        and codex_final_consensus_ok
        and source_manifest_ok
        and row_wording_gate_closes_stable_id
    )

    blockers = []
    if not claude_final_review_ok:
        blockers.append("external_ai_review_missing")
    if not codex_final_consensus_ok:
        blockers.append("codex_consensus_response_missing_after_external_review")
    if not claude_final_review_ok:
        blockers.append("external_public_wording_review_missing")
    if not raw_oracle_ok:
        blockers.append("raw_aabb_oracle_missing")
    if not source_manifest_ok:
        blockers.append("remote_provenance_missing_or_weak")
    if not stability_ok:
        blockers.append("fresh_run_stability_missing")
    if not has_stable_candidate_row_id:
        blockers.append("stable_candidate_row_id_missing")
    if not p1_conditions_applied:
        blockers.append("claude_p1_conditions_not_applied")

    checks = {
        "evidence_exists": EVIDENCE.exists(),
        "evidence_status_is_candidate": evidence.get("status")
        == "aabb_native_query_handle_m7_candidate_pending_external_review",
        "evidence_m7_false": evidence.get("m7_promotion_authorized") is False,
        "evidence_release_false": evidence.get("release_authorized") is False,
        "evidence_public_speedup_false": evidence.get("public_speedup_claim_authorized") is False,
        "material_signal_preserved": bool(speedups) and min(speedups) >= floor,
        "call_for_review_exists": CALL_FOR_REVIEW.exists()
        and "Should Phoenix V3 promote a new row-scoped M7 claim" in call_text,
        "final_call_for_review_exists": FINAL_CALL_FOR_REVIEW.exists()
        and "Phoenix V3 AABB Native Query-Handle Final M7 Review" in final_call_text
        and "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50"
        in final_call_text
        and "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50"
        in final_call_text,
        "gemini_blocked_record_exists": GEMINI_BLOCKED.exists()
        and "not an external review verdict" in gemini_blocked_text,
        "gemini_stderr_records_ineligible_tier": GEMINI_STDERR.exists()
        and "IneligibleTierError" in gemini_stderr_text,
        "external_blocked_record_exists": EXTERNAL_BLOCKED.exists()
        and "external_review_blocked_no_2ai_consensus" in external_text,
        "final_external_blocked_record_exists": FINAL_EXTERNAL_BLOCKED.exists()
        and "external_review_blocked_no_2ai_consensus" in final_external_text
        and "claude.exe" in final_external_text
        and "UNSUPPORTED_CLIENT" in final_external_text
        and "Codex Chrome Extension" in final_external_text,
        "claude_final_review_exists_and_approves_with_conditions": claude_final_review_ok,
        "claude_stream_log_exists": CLAUDE_FINAL_REVIEW_STREAM.exists()
        and CLAUDE_FINAL_REVIEW_STREAM.stat().st_size > 0,
        "codex_final_consensus_closes_p0": codex_final_consensus_ok,
        "claude_p1_conditions_applied": p1_conditions_applied,
        "huygens_review_blocks_promotion": HUYGENS_REVIEW.exists()
        and "Status: `blocked_as_is`" in huygens_text
        and "Raw Embree/OptiX `range_intersection_rows` match an independent CPU AABB oracle" in huygens_text,
        "huygens_followup_review_records_closed_and_remaining_blockers": HUYGENS_FOLLOWUP_REVIEW.exists()
        and "Status: `block_m7_promotion_raw_oracle_and_stability_closed`" in huygens_followup_text
        and "Raw AABB oracle is adequately closed" in huygens_followup_text
        and "Fresh-run stability is adequately closed" in huygens_followup_text
        and "External/2-AI review is still missing" in huygens_followup_text
        and "No public speedup wording is allowed yet" in huygens_followup_text,
        "raw_oracle_gate_closed_or_blocker_recorded": raw_oracle_ok
        or "raw_aabb_oracle_missing" in blockers,
        "source_manifest_provenance_gate_closed_or_blocker_recorded": source_manifest_ok
        or "remote_provenance_missing_or_weak" in blockers,
        "fresh_run_stability_gate_closed_or_blocker_recorded": stability_ok
        or "fresh_run_stability_missing" in blockers,
        "row_wording_gate_exists": ROW_WORDING_GATE.exists(),
        "row_wording_gate_defines_stable_ids_and_preserves_release_boundary": row_wording_gate_closes_stable_id,
        "stable_candidate_row_id_gate_closed_or_blocker_recorded": has_stable_candidate_row_id
        or (
            evidence.get("m7_qualified_release_rows_added") == 0
            and "stable_candidate_row_id_missing" in blockers
        ),
        "all_promotion_blockers_closed": blockers == [],
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    promotion_authorized = not failed_checks and blockers == []
    candidate_rows = []
    for row in row_wording_gate.get("candidate_rows", []) if row_wording_gate else []:
        candidate = dict(row)
        candidate["m7_promoted"] = promotion_authorized
        candidate["row_scoped_public_speedup_claim_authorized"] = promotion_authorized
        candidate["approved_row_scoped_public_wording"] = _approved_wording(candidate)
        candidate_rows.append(candidate)

    return {
        "tool": "v3_phoenix_aabb_native_query_handle_review_gate",
        "status": (
            "aabb_native_query_handle_two_rows_m7_qualified_row_scoped"
            if promotion_authorized
            else "aabb_native_query_handle_review_blocked_not_m7"
        ),
        "generic_capability": evidence.get("generic_capability"),
        "candidate_scope": evidence.get("candidate_scope"),
        "evidence_status": evidence.get("status"),
        "external_review_status": (
            "claude_approve_with_conditions"
            if claude_final_review_ok
            else "blocked_no_external_ai_verdict"
        ),
        "subagent_review_status": "huygens_followup_local_blockers_closed_external_review_supersedes",
        "m7_candidate_reopen_authorized": promotion_authorized,
        "m7_promotion_authorized": promotion_authorized,
        "m7_qualified_release_rows_added": len(stable_candidate_row_ids) if promotion_authorized else 0,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": promotion_authorized,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "full_contact_solver_speedup_claim_authorized": False,
        "broad_aabb_index_acceleration_claim_authorized": False,
        "material_signal_preserved": {
            "material_wall_speedup_floor": floor,
            "best_cold_plus_collect_wall_speedup": max(speedups) if speedups else None,
            "weakest_cold_plus_collect_wall_speedup": min(speedups) if speedups else None,
            "grid_counts": [row.get("grid_count") for row in observed_rows],
        },
        "required_blockers_before_m7": blockers,
        "review_records": {
            "candidate_evidence": _rel(EVIDENCE),
            "call_for_review": _rel(CALL_FOR_REVIEW),
            "final_call_for_review": _rel(FINAL_CALL_FOR_REVIEW),
            "row_wording_gate": _rel(ROW_WORDING_GATE),
            "gemini_blocked": _rel(GEMINI_BLOCKED),
            "gemini_stderr": _rel(GEMINI_STDERR),
            "external_ai_blocked": _rel(EXTERNAL_BLOCKED),
            "final_external_ai_blocked": _rel(FINAL_EXTERNAL_BLOCKED),
            "claude_final_review": _rel(CLAUDE_FINAL_REVIEW),
            "claude_final_review_stream": _rel(CLAUDE_FINAL_REVIEW_STREAM),
            "codex_final_consensus": _rel(CODEX_FINAL_CONSENSUS),
            "huygens_review": _rel(HUYGENS_REVIEW),
            "huygens_followup_review": _rel(HUYGENS_FOLLOWUP_REVIEW),
            "raw_oracle_expected": _rel(RAW_ORACLE_EVIDENCE),
            "stability_expected": _rel(STABILITY_EVIDENCE),
        },
        "remote_git_heads_observed": git_heads,
        "raw_oracle_status": raw_oracle.get("status") if raw_oracle else "missing",
        "raw_oracle_closes_correctness_blocker": raw_oracle_ok,
        "source_manifest_provenance_sha256": source_manifest_sha256 or None,
        "source_manifest_provenance_closes_blocker": source_manifest_ok,
        "fresh_run_stability_status": stability.get("status") if stability else "missing",
        "fresh_run_stability_closes_blocker": stability_ok,
        "stable_candidate_row_id_gate_closed": has_stable_candidate_row_id,
        "stable_candidate_row_ids": stable_candidate_row_ids,
        "candidate_rows": candidate_rows,
        "row_wording_gate_status": row_wording_gate.get("status") if row_wording_gate else "missing",
        "candidate_wording_gate_present": bool(
            row_wording_gate and row_wording_gate.get("candidate_wording_gate_present") is True
        ),
        "public_wording_review_closed": claude_final_review_ok,
        "codex_consensus_response_closed": codex_final_consensus_ok,
        "claude_p1_conditions_applied": p1_conditions_applied,
        "approved_row_scoped_public_wording": [
            row["approved_row_scoped_public_wording"] for row in candidate_rows
        ],
        "forbidden_public_wording": [
            "V3 is faster than V2",
            "Phoenix V3 is release-ready",
            "Contact Manifold solver acceleration",
            "broad AABB-index acceleration",
            "OptiX prepare is faster than Embree prepare",
            "any AABB row outside the two exact stable candidate row ids",
        ],
        "p1_promotion_record_requirements": [
            "Record that the POD source directory had no git_head and provenance rests on SHA-256 source manifest.",
            "Preserve the disclosure that OptiX prepare alone remains slower than Embree.",
        ],
        "huygens_required_gates": [
            "raw Embree/OptiX range_intersection_rows must match an independent CPU AABB oracle",
            "remote git_head or source/build digest must be present",
            "external review/consensus must be recorded",
            "stable candidate row id must exist",
            "broad/public flags must stay false except explicit row-scoped wording",
            "cold-plus-collect wall must remain above the material floor across repeated fresh runs",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "next_engine_action": (
            "Promote exactly the two AABB native-query-handle stable row IDs as row-scoped M7 "
            "evidence while keeping aggregate release, whole-app, broad AABB, and V3-over-V2 "
            "claims false."
            if promotion_authorized
            else (
                "Do not promote the AABB native-query-handle candidate until the remaining "
                "review/consensus/P1 gates close."
            )
        ),
        "goal_level_decision_audit": {
            "decision": (
                "Accept the Claude external AABB final review plus Codex consensus and promote "
                "exactly two row-scoped native-query-handle rows while keeping release and broad "
                "claims false."
            ),
            "was_i_foolish": (
                "No. The previous local blockers are closed, the external review is now real, "
                "and the remaining P1 conditions are recorded as hard checks."
            ),
            "foolish_actions": (
                "The foolish action would be to omit the slower-prepare disclosure, hide the "
                "source-manifest-only provenance, or generalize the two rows into Contact "
                "Manifold or broad V3 claims."
            ),
            "other_path": (
                "I could skip AABB and move to RTNN or Spatial. That avoids this blocker but leaves "
                "a now externally reviewed generic AABB candidate unresolved."
            ),
            "different_path_now": (
                "Regenerate the AABB gate, update the global M7 classification to count only these "
                "two scoped rows, and keep Phoenix V3 release blocked until the broader blockers close."
            ),
        },
    }


def render_markdown(packet: dict[str, Any]) -> str:
    signal = packet["material_signal_preserved"]
    lines = [
        "# Phoenix V3 AABB Native Query-Handle Review Gate",
        "",
        f"Status: `{packet['status']}`",
        "",
        (
            "This packet promotes exactly two AABB native-query-handle rows to "
            "row-scoped M7 status after Claude external review and Codex consensus."
            if packet["m7_promotion_authorized"]
            else "This packet blocks M7 promotion for the AABB native-query-handle candidate."
        ),
        "The candidate is not release evidence, not a Contact Manifold solver",
        "speedup, and not a broad V3-over-V2 claim.",
        "",
        "## Current Verdict",
        "",
        f"- Evidence status: `{packet['evidence_status']}`",
        f"- External review status: `{packet['external_review_status']}`",
        f"- Subagent review status: `{packet['subagent_review_status']}`",
        f"- M7 candidate reopen authorized: `{str(packet['m7_candidate_reopen_authorized']).lower()}`",
        f"- M7 promotion authorized: `{str(packet['m7_promotion_authorized']).lower()}`",
        f"- M7 rows added: `{packet['m7_qualified_release_rows_added']}`",
        "- Release authorized: `false`",
        "",
        "## Material Signal Preserved",
        "",
        f"- Material wall-speedup floor: `{signal['material_wall_speedup_floor']:.2f}x`",
        f"- Best cold-plus-collect wall speedup: `{signal['best_cold_plus_collect_wall_speedup']:.3f}x`",
        f"- Weakest cold-plus-collect wall speedup: `{signal['weakest_cold_plus_collect_wall_speedup']:.3f}x`",
        f"- Grid counts: `{signal['grid_counts']}`",
        "",
        (
            "These numbers are authorized only as exact row-scoped M7 evidence."
            if packet["m7_promotion_authorized"]
            else "These numbers remain candidate evidence only. Promotion is blocked by the review gates below."
        ),
        "",
        "## Required Blockers Before M7",
        "",
    ]
    if packet["required_blockers_before_m7"]:
        for blocker in packet["required_blockers_before_m7"]:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Stable Candidate Rows", ""])
    for row in packet["candidate_rows"]:
        lines.extend(
            [
                f"### {row['row_id']}",
                "",
                f"- AABBs / box queries: `{row['aabb_count']}` / `{row['box_query_count']}`",
                f"- Cold-plus-collect wall speedup: `{row['optix_over_embree_cold_plus_collect_wall_speedup']:.3f}x`",
                f"- Query-total speedup: `{row['optix_over_embree_query_total_speedup']:.3f}x`",
                "- Prepare disclosure: OptiX prepare alone remains slower than Embree.",
                "",
            ]
        )
    lines.extend(["", "## P1 Promotion Record Requirements", ""])
    for item in packet["p1_promotion_record_requirements"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Huygens Required Gates", ""])
    for gate in packet["huygens_required_gates"]:
        lines.append(f"- {gate}")
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
