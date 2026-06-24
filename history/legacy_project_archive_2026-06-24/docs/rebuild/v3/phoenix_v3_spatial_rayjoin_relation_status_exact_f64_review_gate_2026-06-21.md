# Phoenix V3 Spatial Relation-Status Exact-F64 Review Gate

Status: `spatial_rayjoin_relation_status_exact_f64_review_blocked_not_m7`

This packet intentionally blocks M7 promotion. The exact-f64 repair is
material generic-engine evidence, but external review and author-basis
requirements are still missing.

## Current Verdict

- Intake status: `spatial_rayjoin_relation_status_exact_f64_device_scalar_count_intake_not_m7`
- External review status: `blocked_no_external_ai_verdict`
- Codex review status: `approve_as_intake_blocks_m7`
- M7 candidate reopen authorized: `false`
- M7 promotion authorized: `false`
- Release authorized: `false`

## Internal Delta Preserved

- Prepared-query speedup versus prior RTDL exact executor: `3.680x`
- Runner-wall speedup versus prior RTDL exact executor: `1.465x`

These are internal RTDL-vs-RTDL comparisons, not RayJoin author, paper,
whole-app, broad V3-over-V2, or release claims.

## Author Timing Basis

- Status: `present_but_not_m7_author_query_faster_count_not_printed`
- Same-dataset author timing present: `true`
- Current candidate dataset: `data/rayjoin_public_cdb/br_county.cdb`
- Current candidate exact count: `47262`
- Current comparison basis: `RTDL exact-f64 native scalar-count versus prior RTDL exact executor`
- Same-dataset author evidence source: `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.json`
- Same-dataset author Query timer: `1.865660 ms`
- Same-dataset author query points: `342738`
- Same-dataset author result count printed: `false`
- RayJoin author Query speedup vs RTDL exact-f64 prepared query: `3.382x`
- Prior author evidence source: `docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620/m5_pip_point_location_parity_filtered_100k/summary.json`
- Prior author evidence scope: `prior_100k_same_stream_author_comparison_not_direct_public_county_packet`
- Prior author query count: `100000`
- Prior author direct-current comparison authorized: `false`

A same-dataset RayJoin author timing basis now exists for br_county.cdb/br_county.cdb, but it does not promote the Spatial row: RayJoin author Query is faster than the current RTDL exact-f64 prepared-query path, query_exec does not print a result count in this run, and external/public wording review is still missing.

Required before M7:

- External AI review with an actual approve/block verdict
- Codex consensus response after external review
- Public scope review for the fact that RayJoin author Query is faster on this same-dataset timing basis
- An author result-count/parity basis, or explicit wording that refuses count-equivalence claims
- exact row-count/parity evidence for the same dataset and predicate
- external public wording review that keeps RTDL-beats-RayJoin false unless the same-dataset basis proves it

## Adverse-Subset Parity

- Closed: `true`
- Packet: `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_adverse_subset_2026-06-21.json`
- This closes only the adverse-subset parity blocker; it does not
  authorize M7, release, or public speedup wording.

## Required Blockers Before M7

- `external_ai_review_missing`
- `codex_consensus_response_missing_after_external_review`
- `rayjoin_author_result_count_not_printed_or_public_scope_review_missing`
- `rayjoin_author_query_faster_than_rtdl_exact_f64_query`
- `route_name_semantically_stale_relation_status_corrected`
- `public_wording_review_missing`

## Review Records

- call_for_review: `docs/reviews/call_for_review_phoenix_v3_spatial_relation_status_exact_f64_intake_2026-06-21.md`
- claude_unavailable: `docs/reviews/claude_unavailable_phoenix_v3_spatial_relation_status_exact_f64_intake_2026-06-21.md`
- gemini_attempt: `docs/reviews/gemini_phoenix_v3_spatial_relation_status_exact_f64_intake_review_2026-06-21.md`
- external_ai_blocked: `docs/reviews/external_ai_blocked_phoenix_v3_spatial_relation_status_exact_f64_intake_2026-06-21.md`
- codex_blocking_review: `docs/reviews/codex_phoenix_v3_spatial_relation_status_exact_f64_intake_blocking_review_2026-06-21.md`

## Checks

- `intake_exists`: `true`
- `intake_status_not_m7`: `true`
- `intake_m7_promotion_false`: `true`
- `intake_release_false`: `true`
- `intake_rtdl_beats_rayjoin_false`: `true`
- `intake_exact_count_47262`: `true`
- `intake_material_internal_delta`: `true`
- `call_for_review_exists`: `true`
- `claude_unavailable_record_exists`: `true`
- `gemini_attempt_record_exists`: `true`
- `external_blocked_record_exists`: `true`
- `codex_blocking_review_exists`: `true`
- `codex_review_blocks_m7`: `true`
- `adverse_subset_packet_exists`: `true`
- `adverse_subset_status_pass_not_m7`: `true`
- `adverse_subset_closes_only_parity_blocker`: `true`
- `adverse_subset_failed_checks_empty`: `true`
- `adverse_subset_row_count_six_consistent`: `true`
- `exact_executor_intake_exists`: `true`
- `exact_executor_prior_author_gap_not_direct`: `true`
- `m5_author_summary_exists`: `true`
- `m5_author_query_count_is_prior_100k`: `true`
- `m5_author_scope_is_different_from_current_exact_f64`: `true`
- `author_basis_packet_exists`: `true`
- `author_basis_status_present_not_m7`: `true`
- `author_basis_same_dataset_timing_present`: `true`
- `author_basis_result_count_not_printed`: `true`
- `author_basis_keeps_claims_false`: `true`
- `author_basis_records_author_query_faster`: `true`
- `author_timing_basis_marks_present`: `true`
- `author_timing_basis_status_present_not_m7`: `true`
- `author_timing_same_dataset_evidence_not_m7`: `true`
- `author_timing_prior_evidence_still_not_direct_current_packet`: `true`
- `author_timing_requires_public_wording_review`: `true`

Failed checks: `[]`

## Goal-Level Decision Self-Audit

Decision: Gate the Spatial exact-f64 repair as review-blocked/not-M7 despite material internal speedup.

1. Was I foolish? No. The exact-f64 route is promising, but review, author-basis, and adverse-subset gates are still missing.
2. If yes, what actions made the decision foolish? The foolish action would be to turn a 3.680x internal comparison into M7 or release wording without external review and author-basis evidence.
3. Was there another path? I could have kept optimizing Spatial immediately. That risks single-route fixation and does not close the review discipline gap.
4. Can I now try a different path? Preserve Spatial as a blocked intake, then proceed to the next generic engine route while leaving this review gate as the condition for future M7 discussion.
