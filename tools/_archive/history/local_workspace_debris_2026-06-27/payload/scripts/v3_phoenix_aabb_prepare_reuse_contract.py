#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

OUT_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_aabb_prepare_reuse_contract_2026-06-21.json"
OUT_MD = OUT_JSON.with_suffix(".md")
AABB_M7 = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2026-06-21.json"
CONTACT_BOUNDARY = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_contact_manifold_broadphase_boundary_2026-06-21.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def build_payload() -> dict[str, Any]:
    from examples.current.research_benchmarks.contact_manifold import (
        rtdl_contact_manifold_benchmark_app as contact,
    )

    aabb_m7 = _read_json(AABB_M7)
    contact_boundary = _read_json(CONTACT_BOUNDARY)
    smoke = contact.aabb_broadphase_collect_k_payload(
        dataset="tiny",
        witness_capacity=3,
        discovery_backend="cpu",
        discovery_row_capacity=8,
    )
    metadata = smoke["prepared_session_residency"]
    contact_row = contact_boundary["candidate_row"]
    blockers = set(contact_boundary["m7_blockers"])

    checks = {
        "aabb_existing_m7_row_remains_one": aabb_m7.get("m7_qualified_release_rows") == 1,
        "contact_boundary_not_m7": contact_boundary.get("m7_promotion_authorized") is False,
        "contact_wall_is_slower": float(contact_row["wall_optix_over_embree"]) < 1.0,
        "contact_prepare_is_slower": float(contact_row["prepare_aabb_index_optix_over_embree"]) < 1.0,
        "prepare_cost_blocker_present": "optix_prepare_aabb_index_cost_offsets_hot_query_gain" in blockers,
        "smoke_metadata_present": metadata["cache_key"]["primitive"] == "aabb_index_query_2d",
        "smoke_metadata_for_generic_contract": metadata["cache_key"]["parameter_fingerprint"] != (),
        "smoke_blocks_public_speed": metadata["public_speedup_claim_authorized"] is False,
        "smoke_blocks_true_zero_copy": metadata["true_zero_copy_claim_authorized"] is False,
        "smoke_blocks_app_specific_native_logic": metadata["app_specific_native_engine_logic_allowed"] is False,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = "fail" if failed_checks else "aabb_prepare_reuse_contract_candidate_not_m7"

    return {
        "version": "phoenix_v3_aabb_prepare_reuse_contract_2026_06_21",
        "status": status,
        "generic_capability": "aabb_candidate_stream",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "current_packet_external_review_status": "claude_approve_with_amendments_p1_applied",
        "current_packet_2ai_consensus_status": "claude_codex_consensus_complete_queue_advancement_not_m7",
        "review_records": {
            "call_for_review": "docs/reviews/call_for_review_phoenix_v3_aabb_prepare_reuse_contract_2026-06-21.md",
            "claude_review": "docs/reviews/claude_phoenix_v3_aabb_prepare_reuse_contract_review_2026-06-21.md",
            "codex_consensus": "docs/reviews/codex_phoenix_v3_aabb_prepare_reuse_contract_2ai_consensus_2026-06-21.md",
        },
        "source_packets": {
            "aabb_count_only_m7": _rel(AABB_M7),
            "contact_broadphase_boundary": _rel(CONTACT_BOUNDARY),
        },
        "existing_m7_aabb_row": {
            "row_id": aabb_m7["candidate_row"]["candidate_row_id"],
            "scope": "native_float32_inclusive_count_only_32768",
            "remains_the_only_aabb_m7_row": True,
        },
        "current_contact_gap": {
            "row": "contact_manifold / generic_aabb_broadphase_collect_k",
            "query_optix_over_embree": float(contact_row["query_optix_over_embree"]),
            "collect_k_optix_over_embree": float(contact_row["collect_k_optix_over_embree"]),
            "prepare_aabb_index_optix_over_embree": float(contact_row["prepare_aabb_index_optix_over_embree"]),
            "wall_optix_over_embree": float(contact_row["wall_optix_over_embree"]),
            "reading": (
                "Hot query and bounded-row collection improve, but OptiX AABB-index "
                "preparation dominates enough that the current wall path is slower."
            ),
        },
        "new_runtime_contract_smoke": {
            "app": smoke["app"],
            "mode": smoke["mode"],
            "candidate_discovery_backend": smoke["candidate_discovery_backend"],
            "matches_cpu_reference": bool(smoke["matches_cpu_reference"]),
            "prepared_session_residency": metadata,
            "reading": (
                "The contact harness now emits the same generic prepared-session "
                "residency metadata family as other V3 prepared routes. This is "
                "contract visibility, not performance promotion."
            ),
        },
        "future_m7_candidate_requirements": [
            "Use the generic aabb_index_query_2d prepared-session contract, not contact-specific native logic.",
            "Use a serious fixture: at least 32,768 indexed AABBs and 32,768 query AABBs, or a reviewer-approved equivalent scale with a non-trivial prepare phase.",
            "Prepare indexed AABB scene once, then run repeated query/collect rows under an explicit user session.",
            "Report prepare/query/collect/wall phases separately and include cold-plus-repeat wall timing.",
            "Keep CPU-reference parity and fail-closed overflow behavior visible.",
            "Show material OptiX wall win after prepare reuse, not only hot-query win; 1.01x-style noise is not enough.",
            "Obtain fresh external review plus Codex consensus before any new M7 row.",
        ],
        "pod_runner": {
            "script": "scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py",
            "status": "runner_available_not_yet_rt_pod_evidence",
            "serious_default_command": (
                "PYTHONPATH=src:. python scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py "
                "--dataset jittered_grid --grid-count 32768 --warmup 3 --repeat 50 "
                "--backends embree,optix --require-rt-hardware "
                "--output-dir docs/rebuild/v3/evidence/phoenix_v3_aabb_prepare_reuse_YYYYMMDD"
            ),
            "local_smoke_command": (
                "py -3 scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py "
                "--dataset grid --grid-count 3 --backends cpu --warmup 0 --repeat 1 "
                "--witness-capacity 3 --discovery-row-capacity 8 "
                "--allow-non-serious-local-smoke --output-dir <tmp>"
            ),
            "m7_promotion_authorized_by_runner_alone": False,
        },
        "forbidden_shortcuts": [
            "Do not promote contact_manifold from this packet.",
            "Do not claim full contact solver or physics throughput.",
            "Do not claim device-buffer interop or automatic partner selection.",
            "Do not use the existing 1.235x query ratio as wall or end-to-end speedup.",
            "Do not claim a broad V3-over-V2 AABB/contact speedup.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": "Add generic AABB prepare-reuse contract visibility without promoting a new M7 row.",
            "was_i_foolish": "No. The current contact row is wall-slower, so the honest move is to expose the reusable prepared-session contract before rerunning performance.",
            "foolish_actions": (
                "It would be foolish to publish the 1.235x query or 2.759x collect-k ratios "
                "while ignoring the 0.803x wall ratio and 0.243x prepare ratio."
            ),
            "other_path": (
                "Directly rerun the pod. That may be needed next, but without a generic "
                "prepared-session contract the rerun would not prove a V3 engine capability."
            ),
            "different_path_now": (
                "Keep AABB in the engine queue as a prepare-reuse candidate and require "
                "a repeated-session POD row with wall win, parity, overflow behavior, and 2-AI review."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    gap = payload["current_contact_gap"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 AABB Prepare-Reuse Contract",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This packet advances the AABB queue item by making the reusable",
        "`aabb_index_query_2d` prepared-session contract visible in the contact",
        "broadphase harness. It does not promote a new M7 row.",
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}",
        f"M7 rows added by this packet: {payload['m7_qualified_release_rows_added']}",
        "```",
        "",
        "## Existing AABB M7 Row",
        "",
        f"- Row: `{payload['existing_m7_aabb_row']['row_id']}`",
        f"- Scope: `{payload['existing_m7_aabb_row']['scope']}`",
        "- This remains the only AABB M7 row.",
        "",
        "## Current Contact Gap",
        "",
        f"- Row: `{gap['row']}`",
        f"- Query OptiX/Embree: `{gap['query_optix_over_embree']:.3f}x`",
        f"- Collect-k OptiX/Embree: `{gap['collect_k_optix_over_embree']:.3f}x`",
        f"- Prepare AABB-index OptiX/Embree: `{gap['prepare_aabb_index_optix_over_embree']:.3f}x`",
        f"- Wall OptiX/Embree: `{gap['wall_optix_over_embree']:.3f}x`",
        "",
        gap["reading"],
        "",
        "## Runtime Contract Smoke",
        "",
        "- Primitive: `aabb_index_query_2d`",
        f"- Contract version: `{payload['new_runtime_contract_smoke']['prepared_session_residency']['policy']['contract_version']}`",
        "- Cold phase: `prepare_aabb_index_2d`",
        "- Hot phase: `emit_aabb_intersection_pair_rows_2d`",
        "- Explicit reuse helper: `get_or_prepare_explicit_session`",
        "- Public speedup, device-buffer interop, automatic partner selection, and app-specific native logic remain false.",
        "- This packet records contract visibility. It does not claim the current local smoke observed a prepared AABB execution path or a performance win.",
        "",
        "## POD Runner",
        "",
        f"- Script: `{payload['pod_runner']['script']}`",
        f"- Status: `{payload['pod_runner']['status']}`",
        "- Serious default command:",
        "",
        "```bash",
        payload["pod_runner"]["serious_default_command"],
        "```",
        "",
        "- The runner alone does not authorize M7 promotion; a successful RTX run still needs fresh external review plus Codex consensus.",
        "",
        "## Review Status",
        "",
        f"- External review: `{payload['current_packet_external_review_status']}`",
        f"- 2-AI consensus: `{payload['current_packet_2ai_consensus_status']}`",
        f"- Claude review: `{payload['review_records']['claude_review']}`",
        f"- Codex consensus: `{payload['review_records']['codex_consensus']}`",
        "",
        "## Future M7 Requirements",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["future_m7_candidate_requirements"])
    lines.extend(["", "## Forbidden Shortcuts", ""])
    lines.extend(f"- {item}" for item in payload["forbidden_shortcuts"])
    lines.extend(
        [
            "",
            "## Goal-Level Decision Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            "1. Was I foolish?",
            f"   {audit['was_i_foolish']}",
            "2. If yes, what actions made the decision foolish?",
            f"   {audit['foolish_actions']}",
            "3. Was there another path that would have avoided getting stuck on that idea?",
            f"   {audit['other_path']}",
            "4. Can I now try a different path that actually solves the problem?",
            f"   {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emit the Phoenix V3 AABB prepare-reuse contract packet.")
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "m7_qualified_release_rows_added": payload["m7_qualified_release_rows_added"],
                "wall_optix_over_embree": payload["current_contact_gap"]["wall_optix_over_embree"],
                "prepared_session_primitive": payload["new_runtime_contract_smoke"]["prepared_session_residency"]["cache_key"]["primitive"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    return 0 if payload["status"] == "aabb_prepare_reuse_contract_candidate_not_m7" else 2


if __name__ == "__main__":
    raise SystemExit(main())
