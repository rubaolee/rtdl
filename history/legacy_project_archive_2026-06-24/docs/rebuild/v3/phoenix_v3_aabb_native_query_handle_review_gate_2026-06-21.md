# Phoenix V3 AABB Native Query-Handle Review Gate

Status: `aabb_native_query_handle_two_rows_m7_qualified_row_scoped`

This packet promotes exactly two AABB native-query-handle rows to row-scoped M7 status after Claude external review and Codex consensus.
The candidate is not release evidence, not a Contact Manifold solver
speedup, and not a broad V3-over-V2 claim.

## Current Verdict

- Evidence status: `aabb_native_query_handle_m7_candidate_pending_external_review`
- External review status: `claude_approve_with_conditions`
- Subagent review status: `huygens_followup_local_blockers_closed_external_review_supersedes`
- M7 candidate reopen authorized: `true`
- M7 promotion authorized: `true`
- M7 rows added: `2`
- Release authorized: `false`

## Material Signal Preserved

- Material wall-speedup floor: `1.20x`
- Best cold-plus-collect wall speedup: `1.719x`
- Weakest cold-plus-collect wall speedup: `1.637x`
- Grid counts: `[32768, 65536]`

These numbers are authorized only as exact row-scoped M7 evidence.

## Required Blockers Before M7

- none

## Stable Candidate Rows

### aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50

- AABBs / box queries: `32768` / `32768`
- Cold-plus-collect wall speedup: `1.719x`
- Query-total speedup: `1.867x`
- Prepare disclosure: OptiX prepare alone remains slower than Embree.

### aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50

- AABBs / box queries: `65536` / `65536`
- Cold-plus-collect wall speedup: `1.637x`
- Query-total speedup: `1.743x`
- Prepare disclosure: OptiX prepare alone remains slower than Embree.


## P1 Promotion Record Requirements

- Record that the POD source directory had no git_head and provenance rests on SHA-256 source manifest.
- Preserve the disclosure that OptiX prepare alone remains slower than Embree.

## Huygens Required Gates

- raw Embree/OptiX range_intersection_rows must match an independent CPU AABB oracle
- remote git_head or source/build digest must be present
- external review/consensus must be recorded
- stable candidate row id must exist
- broad/public flags must stay false except explicit row-scoped wording
- cold-plus-collect wall must remain above the material floor across repeated fresh runs

## Review Records

- candidate_evidence: `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.json`
- call_for_review: `docs/reviews/call_for_review_phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.md`
- final_call_for_review: `docs/reviews/call_for_review_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md`
- row_wording_gate: `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_row_wording_gate_2026-06-21.json`
- gemini_blocked: `docs/reviews/gemini_blocked_phoenix_v3_aabb_native_query_handle_evidence_review_2026-06-21.md`
- gemini_stderr: `docs/reviews/gemini_phoenix_v3_aabb_native_query_handle_evidence_review_2026-06-21.stderr.txt`
- external_ai_blocked: `docs/reviews/external_ai_blocked_phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.md`
- final_external_ai_blocked: `docs/reviews/external_ai_blocked_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md`
- claude_final_review: `docs/reviews/claude_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md`
- claude_final_review_stream: `docs/reviews/claude_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.stream.jsonl`
- codex_final_consensus: `docs/reviews/codex_phoenix_v3_aabb_native_query_handle_final_m7_review_2ai_consensus_2026-06-21.md`
- huygens_review: `docs/reviews/codex_subagent_huygens_phoenix_v3_aabb_native_query_handle_evidence_review_2026-06-21.md`
- huygens_followup_review: `docs/reviews/codex_subagent_huygens_phoenix_v3_aabb_native_query_handle_followup_review_2026-06-21.md`
- raw_oracle_expected: `docs/rebuild/v3/phoenix_v3_aabb_raw_oracle_evidence_2026-06-21.json`
- stability_expected: `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_stability_evidence_2026-06-21.json`

## Checks

- `evidence_exists`: `true`
- `evidence_status_is_candidate`: `true`
- `evidence_m7_false`: `true`
- `evidence_release_false`: `true`
- `evidence_public_speedup_false`: `true`
- `material_signal_preserved`: `true`
- `call_for_review_exists`: `true`
- `final_call_for_review_exists`: `true`
- `gemini_blocked_record_exists`: `true`
- `gemini_stderr_records_ineligible_tier`: `true`
- `external_blocked_record_exists`: `true`
- `final_external_blocked_record_exists`: `true`
- `claude_final_review_exists_and_approves_with_conditions`: `true`
- `claude_stream_log_exists`: `true`
- `codex_final_consensus_closes_p0`: `true`
- `claude_p1_conditions_applied`: `true`
- `huygens_review_blocks_promotion`: `true`
- `huygens_followup_review_records_closed_and_remaining_blockers`: `true`
- `raw_oracle_gate_closed_or_blocker_recorded`: `true`
- `source_manifest_provenance_gate_closed_or_blocker_recorded`: `true`
- `fresh_run_stability_gate_closed_or_blocker_recorded`: `true`
- `row_wording_gate_exists`: `true`
- `row_wording_gate_defines_stable_ids_and_preserves_release_boundary`: `true`
- `stable_candidate_row_id_gate_closed_or_blocker_recorded`: `true`
- `all_promotion_blockers_closed`: `true`

Failed checks: `[]`

## Goal-Level Decision Self-Audit

Decision: Accept the Claude external AABB final review plus Codex consensus and promote exactly two row-scoped native-query-handle rows while keeping release and broad claims false.

1. Was I foolish? No. The previous local blockers are closed, the external review is now real, and the remaining P1 conditions are recorded as hard checks.
2. If yes, what actions made the decision foolish? The foolish action would be to omit the slower-prepare disclosure, hide the source-manifest-only provenance, or generalize the two rows into Contact Manifold or broad V3 claims.
3. Was there another path? I could skip AABB and move to RTNN or Spatial. That avoids this blocker but leaves a now externally reviewed generic AABB candidate unresolved.
4. Can I now try a different path? Regenerate the AABB gate, update the global M7 classification to count only these two scoped rows, and keep Phoenix V3 release blocked until the broader blockers close.
