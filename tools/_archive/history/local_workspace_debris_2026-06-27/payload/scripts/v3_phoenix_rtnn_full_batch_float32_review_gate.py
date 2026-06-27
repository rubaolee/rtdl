from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

EVIDENCE = ROOT / "docs/rebuild/v3/phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.json"
CALL_FOR_REVIEW = (
    ROOT / "docs/reviews/call_for_review_phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.md"
)
EXTERNAL_BLOCKED = (
    ROOT
    / "docs/reviews/external_review_blocked_phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.md"
)
GEMINI_STDERR = (
    ROOT
    / "docs/reviews/gemini_phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_review_2026-06-21.stderr.txt"
)
CODEX_REVIEW = (
    ROOT / "docs/reviews/codex_phoenix_v3_rtnn_full_batch_float32_same_contract_blocking_review_2026-06-21.md"
)

OUT_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_rtnn_full_batch_float32_review_gate_2026-06-21.json"
OUT_MD = ROOT / "docs/rebuild/v3/phoenix_v3_rtnn_full_batch_float32_review_gate_2026-06-21.md"


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_packet() -> dict[str, Any]:
    evidence = _load_json(EVIDENCE)
    external_text = _read(EXTERNAL_BLOCKED)
    gemini_stderr = _read(GEMINI_STDERR)
    codex_text = _read(CODEX_REVIEW)
    row = evidence["main_row"]

    blockers = [
        "external_ai_review_missing",
        "codex_consensus_response_missing_after_external_review",
        "cold_plus_query_wall_regresses",
        "runner_wall_regresses",
        "prepared_hot_query_scope_not_reviewed",
        "float32_exact_false_boundary_requires_wording",
        "pack_prepare_amortization_not_solved",
        "public_wording_review_missing",
    ]

    checks = {
        "evidence_exists": EVIDENCE.exists(),
        "evidence_status_not_m7": evidence.get("status")
        == "rtnn_full_batch_float32_hot_query_candidate_pending_2ai_wall_blocked_not_m7",
        "evidence_m7_false": evidence.get("m7_promotion_authorized") is False,
        "evidence_release_false": evidence.get("release_authorized") is False,
        "hot_query_material": float(row["hot_speedup_optix_over_cupy_grid"]) > 7.0,
        "cold_plus_query_wall_regresses": float(row["cold_plus_query_speedup_optix_over_cupy_grid"]) < 1.0,
        "runner_wall_regresses": float(row["runner_wall_speedup_optix_over_cupy_grid"]) < 1.0,
        "same_contract_signature_match": evidence.get("parity", {}).get("same_contract_signature_match") is True,
        "call_for_review_exists": CALL_FOR_REVIEW.exists(),
        "external_blocked_exists": EXTERNAL_BLOCKED.exists()
        and "No 2-AI closure exists" in external_text,
        "gemini_stderr_records_auth_failure": GEMINI_STDERR.exists() and "IneligibleTierError" in gemini_stderr,
        "codex_blocking_review_exists": CODEX_REVIEW.exists()
        and "`approve-as-prepared-hot-query-intake`" in codex_text,
        "codex_review_blocks_m7": "must remain not-M7" in codex_text and "Wall and runner comparisons regress" in codex_text,
    }

    failed_checks = [name for name, passed in checks.items() if not passed]

    return {
        "tool": "v3_phoenix_rtnn_full_batch_float32_review_gate",
        "status": "rtnn_full_batch_float32_review_blocked_not_m7",
        "generic_capability": evidence["generic_capability"],
        "candidate_scope": evidence["candidate_scope"],
        "evidence_status": evidence["status"],
        "external_review_status": "blocked_no_external_ai_verdict",
        "codex_review_status": "approve_as_prepared_hot_query_intake_blocks_m7",
        "m7_candidate_reopen_authorized": False,
        "m7_promotion_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "universal_nearest_neighbor_claim_authorized": False,
        "prepared_hot_query_internal_signal": {
            "point_count": row["point_count"],
            "repeat": row["repeat"],
            "hot_speedup_optix_over_cupy_grid": row["hot_speedup_optix_over_cupy_grid"],
            "cold_plus_query_speedup_optix_over_cupy_grid": row[
                "cold_plus_query_speedup_optix_over_cupy_grid"
            ],
            "runner_wall_speedup_optix_over_cupy_grid": row["runner_wall_speedup_optix_over_cupy_grid"],
            "same_contract_signature_match": row["same_contract_signature_match"],
            "sum_distance_relative_error": row["sum_distance_relative_error"],
        },
        "required_blockers_before_m7": blockers,
        "review_records": {
            "call_for_review": _rel(CALL_FOR_REVIEW),
            "external_review_blocked": _rel(EXTERNAL_BLOCKED),
            "gemini_stderr": _rel(GEMINI_STDERR),
            "codex_blocking_review": _rel(CODEX_REVIEW),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "next_engine_action": (
            "Keep RTNN full-batch float32 behind a review gate. Future engine work must reduce pack/prepare "
            "or establish a stricter exact/tie-stable path before any prepared-hot-query M7 review."
        ),
        "goal_level_decision_audit": {
            "decision": "Gate the RTNN full-batch float32 hot-query result as review-blocked/not-M7.",
            "was_i_foolish": (
                "No. The hot-query signal is real, but wall regressions and missing external review block "
                "promotion."
            ),
            "foolish_actions": (
                "The foolish action would be to promote the 7.790x prepared-hot-query number while hiding "
                "the 0.393x cold-plus-query wall and 0.627x runner-wall regressions."
            ),
            "other_path": (
                "Rejecting RTNN entirely would avoid overclaim risk but would discard useful generic "
                "ranked_summary evidence."
            ),
            "different_path_now": (
                "Keep the row blocked, then work on pack/prepare amortization or exact/tie-stable parity."
            ),
        },
    }


def render_markdown(packet: dict[str, Any]) -> str:
    signal = packet["prepared_hot_query_internal_signal"]
    lines = [
        "# Phoenix V3 RTNN Full-Batch Float32 Review Gate",
        "",
        f"Status: `{packet['status']}`",
        "",
        "This packet blocks M7 promotion while preserving the useful prepared-hot-query",
        "signal. It is not release authorization and not an end-to-end RTNN speedup.",
        "",
        "## Current Verdict",
        "",
        f"- Evidence status: `{packet['evidence_status']}`",
        f"- External review status: `{packet['external_review_status']}`",
        f"- Codex review status: `{packet['codex_review_status']}`",
        "- M7 candidate reopen authorized: `false`",
        "- M7 promotion authorized: `false`",
        "- Release authorized: `false`",
        "",
        "## Internal Signal Preserved",
        "",
        f"- Point count: `{signal['point_count']}`",
        f"- Repeat: `{signal['repeat']}`",
        f"- Prepared hot-query OptiX/CuPy speedup: `{signal['hot_speedup_optix_over_cupy_grid']:.3f}x`",
        f"- Cold-plus-query wall speedup: `{signal['cold_plus_query_speedup_optix_over_cupy_grid']:.3f}x`",
        f"- Runner-wall speedup: `{signal['runner_wall_speedup_optix_over_cupy_grid']:.3f}x`",
        f"- Same-contract signature match: `{str(bool(signal['same_contract_signature_match'])).lower()}`",
        f"- Sum-distance relative error: `{signal['sum_distance_relative_error']:.3e}`",
        "",
        "The `7.790x` number is prepared-hot-query only. The `0.393x` and",
        "`0.627x` wall regressions block end-to-end wording.",
        "",
        "## Required Blockers Before M7",
        "",
    ]
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
