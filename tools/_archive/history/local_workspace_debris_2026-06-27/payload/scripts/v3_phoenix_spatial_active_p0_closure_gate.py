from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

NEXT_QUEUE = ROOT / "docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.json"
REVIEW_GATE = (
    ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_review_gate_2026-06-21.json"
)
AUTHOR_BASIS = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.json"
CALL_FOR_REVIEW = (
    ROOT / "docs/reviews/call_for_review_phoenix_v3_spatial_active_p0_closure_2026-06-21.md"
)
GEMINI_REVIEW = (
    ROOT / "docs/reviews/gemini_phoenix_v3_spatial_active_p0_closure_review_2026-06-21.md"
)
GEMINI_STDERR = (
    ROOT / "docs/reviews/gemini_phoenix_v3_spatial_active_p0_closure_review_2026-06-21.stderr.txt"
)
CLAUDE_REVIEW = (
    ROOT / "docs/reviews/claude_phoenix_v3_spatial_active_p0_closure_review_2026-06-21.md"
)
CODEX_CONSENSUS = (
    ROOT / "docs/reviews/codex_phoenix_v3_spatial_active_p0_closure_2ai_consensus_2026-06-21.md"
)
EXTERNAL_BLOCKED = (
    ROOT / "docs/reviews/external_ai_blocked_phoenix_v3_spatial_active_p0_closure_2026-06-21.md"
)

OUT_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_active_p0_closure_gate_2026-06-21.json"
OUT_MD = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_active_p0_closure_gate_2026-06-21.md"


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-16")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _external_verdict(text: str) -> str | None:
    lowered = text.lower()
    for verdict in ("close-active-p0", "keep-active-p0", "reject-current-record"):
        if verdict in lowered:
            return verdict
    return None


def build_packet() -> dict[str, Any]:
    queue = _load_json(NEXT_QUEUE)
    review_gate = _load_json(REVIEW_GATE)
    author_basis = _load_json(AUTHOR_BASIS)
    gemini_text = _read(GEMINI_REVIEW)
    gemini_stderr = _read(GEMINI_STDERR)
    claude_text = _read(CLAUDE_REVIEW)
    codex_consensus_text = _read(CODEX_CONSENSUS)
    blocked_text = _read(EXTERNAL_BLOCKED)
    gemini_verdict = _external_verdict(gemini_text)
    claude_verdict = _external_verdict(claude_text)
    verdict = claude_verdict or gemini_verdict
    external_review_source = "claude" if claude_verdict else ("gemini" if gemini_verdict else None)

    active_ids = [item["id"] for item in queue.get("queue", [])]
    spatial_still_active = "spatial_rayjoin_topology_stream_author_gap" in active_ids
    gemini_blocked = "IneligibleTierError" in gemini_stderr
    blocked_record_ok = (
        EXTERNAL_BLOCKED.exists()
        and "external review blocked, not a review verdict" in blocked_text
        and "no 2-AI consensus exists" in blocked_text
    )
    codex_consensus_ok = (
        CODEX_CONSENSUS.exists()
        and "claude_codex_consensus_complete_close_active_p0_future_research"
        in codex_consensus_text
        and "spatial_rayjoin_topology_stream_author_gap" in codex_consensus_text
        and "below `1.865660 ms` with stable margin" in codex_consensus_text
    )
    close_allowed = (
        verdict == "close-active-p0"
        and external_review_source in {"claude", "gemini"}
        and codex_consensus_ok
        and review_gate.get("rtdl_beats_rayjoin_claim_authorized") is False
        and author_basis.get("m7_promotion_authorized") is False
    )

    checks = {
        "next_queue_exists": NEXT_QUEUE.exists(),
        "spatial_queue_state_valid_for_gate_phase": spatial_still_active or close_allowed,
        "review_gate_exists": REVIEW_GATE.exists(),
        "review_gate_blocks_m7": review_gate.get("status")
        == "spatial_rayjoin_relation_status_exact_f64_review_blocked_not_m7",
        "review_gate_failed_checks_empty": review_gate.get("failed_checks") == [],
        "author_basis_exists": AUTHOR_BASIS.exists(),
        "author_basis_records_author_query_faster": author_basis.get("comparison", {}).get(
            "rayjoin_author_query_speedup_vs_rtdl_exact_f64_prepared_query", 0.0
        )
        > 1.0,
        "call_for_review_exists": CALL_FOR_REVIEW.exists(),
        "claude_review_exists": CLAUDE_REVIEW.exists(),
        "claude_review_verdict_close_active_p0": claude_verdict == "close-active-p0",
        "codex_consensus_exists": CODEX_CONSENSUS.exists(),
        "codex_consensus_closes_active_p0_future_research": codex_consensus_ok,
        "gemini_attempt_stderr_exists": GEMINI_STDERR.exists(),
        "gemini_attempt_blocked": gemini_blocked,
        "external_blocked_record_exists": EXTERNAL_BLOCKED.exists(),
        "external_blocked_record_says_not_verdict": blocked_record_ok,
        "real_external_verdict_present": verdict in {
            "close-active-p0",
            "keep-active-p0",
            "reject-current-record",
        },
        "closure_authorized_only_after_external_and_codex_consensus": close_allowed
        == (verdict == "close-active-p0" and codex_consensus_ok),
        "gemini_tool_failure_does_not_override_claude_verdict": (
            gemini_blocked and external_review_source == "claude"
        ),
        "release_claims_remain_false": queue.get("release_authorized") is False
        and queue.get("public_speedup_claim_authorized") is False
        and queue.get("broad_v3_faster_than_v2_claim_authorized") is False,
    }
    failed_checks = [name for name, passed in checks.items() if not passed]

    if close_allowed and spatial_still_active:
        status = "spatial_active_p0_closure_authorized_pending_queue_update"
    elif close_allowed:
        status = "spatial_active_p0_closed_current_v3_future_research"
    elif verdict == "close-active-p0":
        status = "spatial_active_p0_external_review_recommends_close_pending_codex_consensus"
    else:
        status = "spatial_active_p0_closure_blocked_external_review_missing"
    return {
        "tool": "v3_phoenix_spatial_active_p0_closure_gate",
        "status": status,
        "generic_capability": "point_location_topology_stream",
        "spatial_queue_id": "spatial_rayjoin_topology_stream_author_gap",
        "external_review_verdict": verdict,
        "external_review_source": external_review_source,
        "external_review_status": (
            "blocked_no_external_ai_verdict" if verdict is None else "external_verdict_present"
        ),
        "active_p0_closure_authorized": close_allowed,
        "codex_consensus_required_after_external_review": not codex_consensus_ok,
        "codex_consensus_status": (
            "codex_consensus_complete_close_active_p0_future_research"
            if codex_consensus_ok
            else "codex_consensus_missing"
        ),
        "m7_promotion_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "evidence": {
            "closure_gate_markdown": _rel(OUT_MD),
            "closure_gate_json": _rel(OUT_JSON),
            "next_queue": _rel(NEXT_QUEUE),
            "review_gate": _rel(REVIEW_GATE),
            "author_basis": _rel(AUTHOR_BASIS),
            "call_for_review": _rel(CALL_FOR_REVIEW),
            "claude_review": _rel(CLAUDE_REVIEW),
            "codex_consensus": _rel(CODEX_CONSENSUS),
            "gemini_review": _rel(GEMINI_REVIEW),
            "gemini_stderr": _rel(GEMINI_STDERR),
            "external_blocked": _rel(EXTERNAL_BLOCKED),
            "same_dataset_author_query_ms": author_basis.get("author_run", {}).get("query_ms"),
            "rtdl_exact_f64_prepared_query_ms": author_basis.get("comparison", {}).get(
                "prepared_query_ms"
            )
            or author_basis.get("comparison", {}).get("rtdl_exact_f64_prepared_query_ms"),
            "rayjoin_author_query_speedup_vs_rtdl": author_basis.get("comparison", {}).get(
                "rayjoin_author_query_speedup_vs_rtdl_exact_f64_prepared_query"
            ),
        },
        "required_to_close_active_p0": [
            "real external AI verdict, not CLI stderr",
            "Codex consensus response after the external verdict",
            "machine update to next generic-engine queue",
            "release readiness gate rerun with generic queue changed",
            "public wording that keeps RTDL-beats-RayJoin and broad V3-over-V2 false",
        ],
        "reopen_conditions": [
            "fresh same-dataset br_county.cdb POD packet with RTDL prepared-query median below 1.865660 ms with stable margin",
            "stable exact count 47,262",
            "full M3 phase table",
            "same-packet author timing and count evidence",
            "or real external AI acceptance of a weaker scope plus Codex consensus",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": "Close Spatial active P0 for current Phoenix V3 only after Claude external review and Codex consensus.",
            "was_i_foolish": (
                "No. The gate now distinguishes a real Claude verdict from Gemini CLI stderr and requires Codex consensus before queue closure."
            ),
            "foolish_actions": (
                "The foolish action would be to treat the RTDL-vs-RTDL 3.680x repair as an RTDL-beats-RayJoin win, "
                "or to close Spatial without recording the 3.382x author gap and numeric reopen bar."
            ),
            "other_path": (
                "Keep Spatial active and continue optimizing the exact/topology predicate. That path is possible, "
                "but it keeps the current release track blocked without evidence that RTDL can beat the author timer."
            ),
            "different_path_now": (
                "Move Spatial to future research, preserve all no-claim boundaries, and reopen only on the recorded "
                "same-dataset performance/count/M3 evidence bar or a new external scoped acceptance."
            ),
        },
    }


def render_markdown(packet: dict[str, Any]) -> str:
    evidence = packet["evidence"]
    lines = [
        "# Phoenix V3 Spatial Active-P0 Closure Gate",
        "",
        f"Status: `{packet['status']}`",
        "",
        "This gate does not authorize release, M7 promotion, RTDL-beats-RayJoin wording, or broad V3-over-V2 wording.",
        "",
        "## Verdict",
        "",
        f"- External review verdict: `{packet['external_review_verdict']}`",
        f"- External review source: `{packet['external_review_source']}`",
        f"- External review status: `{packet['external_review_status']}`",
        f"- Active P0 closure authorized: `{str(packet['active_p0_closure_authorized']).lower()}`",
        f"- Codex consensus required after external review: `{str(packet['codex_consensus_required_after_external_review']).lower()}`",
        f"- Codex consensus status: `{packet['codex_consensus_status']}`",
        "",
        "## Evidence",
        "",
        f"- Closure gate markdown: `{evidence['closure_gate_markdown']}`",
        f"- Closure gate JSON: `{evidence['closure_gate_json']}`",
        f"- Current queue: `{evidence['next_queue']}`",
        f"- Exact-f64 review gate: `{evidence['review_gate']}`",
        f"- Same-dataset author timing: `{evidence['author_basis']}`",
        f"- Closure review request: `{evidence['call_for_review']}`",
        f"- Claude review: `{evidence['claude_review']}`",
        f"- Codex consensus: `{evidence['codex_consensus']}`",
        f"- Gemini review output: `{evidence['gemini_review']}`",
        f"- Gemini stderr: `{evidence['gemini_stderr']}`",
        f"- External blocked record: `{evidence['external_blocked']}`",
        "",
        "## Current Timing Boundary",
        "",
        f"- Same-dataset author Query timer: `{evidence['same_dataset_author_query_ms']:.6f} ms`",
        f"- RTDL exact-f64 prepared-query median: `{evidence['rtdl_exact_f64_prepared_query_ms']:.6f} ms`",
        f"- RayJoin author Query speedup vs RTDL: `{evidence['rayjoin_author_query_speedup_vs_rtdl']:.3f}x`",
        "",
        "## Required To Close Active P0",
        "",
    ]
    lines.extend(f"- `{item}`" for item in packet["required_to_close_active_p0"])
    lines.extend(
        [
            "",
            "## Reopen Conditions",
            "",
        ]
    )
    lines.extend(f"- `{item}`" for item in packet["reopen_conditions"])
    lines.extend(
        [
            "",
            "## Checks",
            "",
        ]
    )
    lines.extend(f"- `{name}`: `{str(value).lower()}`" for name, value in packet["checks"].items())
    lines.extend(
        [
            "",
            f"Failed checks: `{packet['failed_checks']}`",
            "",
            "## Goal-Level Decision Self-Audit",
            "",
            f"Decision: {packet['goal_level_decision_audit']['decision']}",
            "",
            f"1. Was I foolish? {packet['goal_level_decision_audit']['was_i_foolish']}",
            f"2. If yes, what actions made the decision foolish? {packet['goal_level_decision_audit']['foolish_actions']}",
            f"3. Was there another path? {packet['goal_level_decision_audit']['other_path']}",
            f"4. Can I now try a different path? {packet['goal_level_decision_audit']['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    packet = build_packet()
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(packet), encoding="utf-8")
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0 if not packet["failed_checks"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
