from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

EVIDENCE = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.json"
RAW_ORACLE_EVIDENCE = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_raw_oracle_evidence_2026-06-21.json"
STABILITY_EVIDENCE = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_stability_evidence_2026-06-21.json"
REVIEW_GATE = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.json"
GEMINI_FINAL_ATTEMPT = (
    ROOT / "docs/reviews/gemini_phoenix_v3_aabb_native_query_handle_final_review_2026-06-21.md"
)
GEMINI_FINAL_STDERR = (
    ROOT / "docs/reviews/gemini_phoenix_v3_aabb_native_query_handle_final_review_2026-06-21.stderr.txt"
)
CLAUDE_FINAL_REVIEW = (
    ROOT / "docs/reviews/claude_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md"
)
CODEX_FINAL_CONSENSUS = (
    ROOT
    / "docs/reviews/codex_phoenix_v3_aabb_native_query_handle_final_m7_review_2ai_consensus_2026-06-21.md"
)

OUT_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_row_wording_gate_2026-06-21.json"
OUT_MD = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_row_wording_gate_2026-06-21.md"


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _candidate_row_id(grid_count: int) -> str:
    return f"aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_{grid_count}_repeat50"


def _row_wording(row: dict[str, Any]) -> str:
    grid_count = int(row["grid_count"])
    speedup = float(row["optix_over_embree_cold_plus_collect_wall_speedup"])
    query_speedup = float(row["optix_over_embree_query_total_speedup"])
    return (
        "Draft only, not publishable before external review: for a generic "
        "AABB_INDEX_QUERY_2D prepared-session range_intersection_rows workload "
        f"on an NVIDIA RTX 4000 Ada Generation pod, jittered_grid with {grid_count:,} "
        f"AABBs and {grid_count:,} packed box queries, warmup={row['warmup']} and "
        f"repeat={row['repeat']}, RTDL's OptiX native prepared-query-handle route "
        f"was {speedup:.3f}x faster than the RTDL Embree route for cold prepare plus "
        f"collect wall time, and {query_speedup:.3f}x faster for query_total. The "
        "row is candidate-only until external review and Codex consensus close; it "
        "does not claim full Contact Manifold solving, broad AABB-index acceleration, "
        "all-app speedup, release readiness, or V3-over-V2 speedup."
    )


def _approved_row_wording(row: dict[str, Any]) -> str:
    grid_count = int(row["grid_count"])
    speedup = float(row["optix_over_embree_cold_plus_collect_wall_speedup"])
    query_speedup = float(row["optix_over_embree_query_total_speedup"])
    return (
        "On an NVIDIA RTX 4000 Ada Generation GPU, RTDL's OptiX native "
        "prepared-query-handle route for `AABB_INDEX_QUERY_2D range_intersection_rows` "
        f"was {speedup:.3f}x faster than the RTDL Embree route on a jittered-grid "
        f"workload with {grid_count:,} AABBs and {grid_count:,} packed box queries, "
        f"measured as cold prepare plus collect wall time with warmup={row['warmup']} "
        f"and repeat={row['repeat']}. Query total was {query_speedup:.3f}x faster. "
        "OptiX prepare alone remains slower than Embree; the speedup applies to "
        "end-to-end prepared-session time. This result is row-scoped and does not "
        "claim Contact Manifold solver acceleration, broad AABB-index acceleration, "
        "or V3-over-V2 speedup."
    )


def build_packet() -> dict[str, Any]:
    evidence = _load_json(EVIDENCE)
    raw_oracle = _load_json(RAW_ORACLE_EVIDENCE)
    stability = _load_json(STABILITY_EVIDENCE)
    review_gate = _load_json(REVIEW_GATE)
    final_attempt_text = _read_if_exists(GEMINI_FINAL_ATTEMPT) + "\n" + _read_if_exists(GEMINI_FINAL_STDERR)
    claude_final_text = _read_if_exists(CLAUDE_FINAL_REVIEW)
    codex_final_text = _read_if_exists(CODEX_FINAL_CONSENSUS)

    claude_final_review_ok = (
        CLAUDE_FINAL_REVIEW.exists()
        and "Verdict: `approve-with-conditions`" in claude_final_text
        and "OptiX prepare alone remains slower than Embree" in claude_final_text
    )
    codex_final_consensus_ok = (
        CODEX_FINAL_CONSENSUS.exists()
        and "claude_codex_consensus_complete_approve_two_row_scoped_m7_rows" in codex_final_text
        and "OptiX prepare alone remains slower than Embree" in codex_final_text
    )
    review_gate_m7_qualified = (
        review_gate.get("status") == "aabb_native_query_handle_two_rows_m7_qualified_row_scoped"
        and review_gate.get("m7_promotion_authorized") is True
        and review_gate.get("m7_qualified_release_rows_added") == 2
    )
    post_review_closed = (claude_final_review_ok and codex_final_consensus_ok) or review_gate_m7_qualified

    observed_rows = evidence.get("observed_rows", [])
    candidate_rows: list[dict[str, Any]] = []
    for row in observed_rows:
        grid_count = int(row["grid_count"])
        candidate_rows.append(
            {
                "row_id": _candidate_row_id(grid_count),
                "app_id": "contact_manifold",
                "app_is_evidence_harness_only": True,
                "generic_capability": "aabb_candidate_stream",
                "generic_primitive": "AABB_INDEX_QUERY_2D",
                "operation": "range_intersection_rows",
                "primitive_contract": "generic_prepared_aabb_index_query_2d_native_query_handle",
                "dataset": row["dataset"],
                "aabb_count": grid_count,
                "box_query_count": grid_count,
                "warmup": row["warmup"],
                "repeat": row["repeat"],
                "matches_cpu_reference": row["matches_cpu_reference"],
                "complete_candidate_coverage": row["complete_candidate_coverage"],
                "native_query_handle_cache_observed": row["optix_native_cache_observed"],
                "embree_cold_plus_collect_wall_sec": row["embree_cold_plus_collect_wall_sec"],
                "optix_cold_plus_collect_wall_sec": row["optix_cold_plus_collect_wall_sec"],
                "optix_over_embree_cold_plus_collect_wall_speedup": row[
                    "optix_over_embree_cold_plus_collect_wall_speedup"
                ],
                "embree_query_total_sec": row["embree_query_total_sec"],
                "optix_query_total_sec": row["optix_query_total_sec"],
                "optix_over_embree_query_total_speedup": row["optix_over_embree_query_total_speedup"],
                "optix_prepare_sec": row["optix_prepare_sec"],
                "embree_prepare_sec": row["embree_prepare_sec"],
                "prepare_phase_note": (
                    "OptiX prepare remains slower than Embree on this row; the candidate wording "
                    "therefore uses cold-plus-collect wall and query_total, not prepare-only claims."
                ),
                "same_contract": True,
                "m7_promoted": post_review_closed,
                "row_scoped_public_speedup_claim_authorized": post_review_closed,
                "pre_review_draft_wording_superseded": post_review_closed,
                "approved_row_scoped_public_wording": _approved_row_wording(row)
                if post_review_closed
                else None,
                "draft_row_scoped_wording_not_publishable": None
                if post_review_closed
                else _row_wording(row),
            }
        )

    row_ids = [row["row_id"] for row in candidate_rows]
    floor = float(evidence.get("material_wall_speedup_floor", 1.2))
    checks = {
        "candidate_evidence_exists": EVIDENCE.exists(),
        "row_ids_defined": len(candidate_rows) == 2 and all(row_ids),
        "row_ids_are_unique": len(set(row_ids)) == len(row_ids),
        "row_ids_are_stable_native_query_handle_ids": all(
            row_id.startswith("aabb_candidate_stream_range_intersection_rows_native_query_handle_")
            for row_id in row_ids
        ),
        "all_rows_clear_material_floor": all(
            float(row["optix_over_embree_cold_plus_collect_wall_speedup"]) >= floor
            for row in candidate_rows
        ),
        "all_rows_match_cpu_reference": all(bool(row["matches_cpu_reference"]) for row in candidate_rows),
        "raw_oracle_closed": raw_oracle.get("raw_aabb_oracle_closes_correctness_blocker") is True,
        "stability_closed": stability.get("fresh_run_stability_closes_blocker") is True,
        "review_gate_or_final_reviews_close_public_wording": post_review_closed,
        "gemini_final_attempt_recorded_as_blocked": GEMINI_FINAL_ATTEMPT.exists()
        and "IneligibleTierError" in final_attempt_text,
        "source_evidence_flags_remain_false": (
            evidence.get("m7_promotion_authorized") is False
            and evidence.get("release_authorized") is False
            and evidence.get("public_speedup_claim_authorized") is False
            and evidence.get("broad_v3_faster_than_v2_claim_authorized") is False
        ),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]

    return {
        "tool": "v3_phoenix_aabb_native_query_handle_row_wording_gate",
        "status": (
            "aabb_native_query_handle_row_wording_gate_closed_after_claude_codex_m7_review"
            if post_review_closed
            else "aabb_native_query_handle_stable_row_wording_gate_ready_external_review_blocked_not_m7"
        ),
        "generic_capability": "aabb_candidate_stream",
        "candidate_scope": evidence["candidate_scope"],
        "candidate_row_ids": row_ids,
        "candidate_rows": candidate_rows,
        "stable_candidate_row_id_gate_closed": not failed_checks
        and checks["row_ids_defined"]
        and checks["row_ids_are_unique"],
        "candidate_wording_gate_present": True,
        "public_wording_review_closed": post_review_closed,
        "external_review_status": "claude_approve_with_conditions"
        if post_review_closed
        else "blocked_no_external_ai_verdict",
        "m7_promotion_authorized": post_review_closed,
        "m7_qualified_release_rows_added": len(row_ids) if post_review_closed else 0,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": post_review_closed,
        "whole_app_speedup_claim_authorized": False,
        "broad_aabb_index_acceleration_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "material_wall_speedup_floor": floor,
        "remaining_blockers_before_m7": []
        if post_review_closed
        else [
            "external_ai_review_missing",
            "codex_consensus_response_missing_after_external_review",
            "external_public_wording_review_missing",
        ],
        "forbidden_public_wording": [
            "V3-over-V2 speedup",
            "full Contact Manifold solver speedup",
            "broad AABB-index acceleration",
            "all benchmark apps are accelerated",
            "release-ready",
            "OptiX prepare phase is faster than Embree",
            "any AABB native-query-handle row outside the two exact stable row ids",
        ],
        "source_packets": [
            _rel(EVIDENCE),
            _rel(RAW_ORACLE_EVIDENCE),
            _rel(STABILITY_EVIDENCE),
            _rel(REVIEW_GATE),
            _rel(GEMINI_FINAL_ATTEMPT),
            _rel(CLAUDE_FINAL_REVIEW),
            _rel(CODEX_FINAL_CONSENSUS),
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Close AABB native-query-handle row wording after Claude external review and "
                "Codex consensus while keeping release and broad claims false."
            ),
            "was_i_foolish": (
                "No. The stable row IDs are now reviewed, the approved wording preserves the "
                "slower-prepare disclosure, and release/broad flags remain false."
            ),
            "foolish_actions": (
                "The foolish action would be to leave this gate in pre-review draft mode after "
                "real Claude/Codex review, or to generalize the two rows into a release claim."
            ),
            "other_path": (
                "Skip row materialization and move to RTNN. That is technically valid, but it "
                "leaves an already material AABB candidate with avoidable local blockers."
            ),
            "different_path_now": (
                "Use this wording closure as an exact-row input to the AABB review gate, then "
                "continue RTNN and Spatial without broad V3-over-V2 wording."
            ),
        },
    }


def render_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 AABB Native Query-Handle Row Wording Gate",
        "",
        f"Status: `{packet['status']}`",
        "",
        (
            "This packet records approved row-scoped wording for the AABB native "
            "prepared-query-handle evidence after Claude external review and Codex consensus."
            if packet["m7_promotion_authorized"]
            else "This packet defines stable candidate row IDs and draft row-scoped wording"
        ),
        (
            "It promotes only the two exact native-query-handle rows and does not authorize release, whole-app, broad AABB, or V3-over-V2 wording."
            if packet["m7_promotion_authorized"]
            else "for the AABB native prepared-query-handle evidence. It does not promote the rows and it does not authorize public speedup wording."
        ),
        "",
        "## Candidate Rows",
        "",
    ]
    for row in packet["candidate_rows"]:
        lines.extend(
            [
                f"### {row['row_id']}",
                "",
                f"- Generic capability: `{row['generic_capability']}`",
                f"- Primitive contract: `{row['primitive_contract']}`",
                f"- Dataset: `{row['dataset']}`",
                f"- AABBs / box queries: `{row['aabb_count']}` / `{row['box_query_count']}`",
                f"- Warmup / repeat: `{row['warmup']}` / `{row['repeat']}`",
                f"- Cold-plus-collect wall speedup: `{row['optix_over_embree_cold_plus_collect_wall_speedup']:.3f}x`",
                f"- Query-total speedup: `{row['optix_over_embree_query_total_speedup']:.3f}x`",
                f"- Matches CPU reference: `{str(bool(row['matches_cpu_reference'])).lower()}`",
                f"- Native query-handle cache observed: `{str(bool(row['native_query_handle_cache_observed'])).lower()}`",
                f"- Prepare note: {row['prepare_phase_note']}",
                (
                    f"- Approved row-scoped wording: {row['approved_row_scoped_public_wording']}"
                    if row.get("approved_row_scoped_public_wording")
                    else f"- Draft wording: {row['draft_row_scoped_wording_not_publishable']}"
                ),
                "",
            ]
        )
    lines.extend(
        [
            "## Remaining Blockers Before M7",
            "",
        ]
    )
    if packet["remaining_blockers_before_m7"]:
        for blocker in packet["remaining_blockers_before_m7"]:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Forbidden Public Wording", ""])
    for wording in packet["forbidden_public_wording"]:
        lines.append(f"- {wording}")
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
