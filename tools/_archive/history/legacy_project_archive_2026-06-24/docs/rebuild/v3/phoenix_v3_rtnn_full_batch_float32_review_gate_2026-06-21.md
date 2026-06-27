# Phoenix V3 RTNN Full-Batch Float32 Review Gate

Status: `rtnn_full_batch_float32_review_blocked_not_m7`

This packet blocks M7 promotion while preserving the useful prepared-hot-query
signal. It is not release authorization and not an end-to-end RTNN speedup.

## Current Verdict

- Evidence status: `rtnn_full_batch_float32_hot_query_candidate_pending_2ai_wall_blocked_not_m7`
- External review status: `blocked_no_external_ai_verdict`
- Codex review status: `approve_as_prepared_hot_query_intake_blocks_m7`
- M7 candidate reopen authorized: `false`
- M7 promotion authorized: `false`
- Release authorized: `false`

## Internal Signal Preserved

- Point count: `1048576`
- Repeat: `5`
- Prepared hot-query OptiX/CuPy speedup: `7.790x`
- Cold-plus-query wall speedup: `0.393x`
- Runner-wall speedup: `0.627x`
- Same-contract signature match: `true`
- Sum-distance relative error: `1.207e-10`

The `7.790x` number is prepared-hot-query only. The `0.393x` and
`0.627x` wall regressions block end-to-end wording.

## Required Blockers Before M7

- `external_ai_review_missing`
- `codex_consensus_response_missing_after_external_review`
- `cold_plus_query_wall_regresses`
- `runner_wall_regresses`
- `prepared_hot_query_scope_not_reviewed`
- `float32_exact_false_boundary_requires_wording`
- `pack_prepare_amortization_not_solved`
- `public_wording_review_missing`

## Review Records

- call_for_review: `docs/reviews/call_for_review_phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.md`
- external_review_blocked: `docs/reviews/external_review_blocked_phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.md`
- gemini_stderr: `docs/reviews/gemini_phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_review_2026-06-21.stderr.txt`
- codex_blocking_review: `docs/reviews/codex_phoenix_v3_rtnn_full_batch_float32_same_contract_blocking_review_2026-06-21.md`

## Checks

- `evidence_exists`: `true`
- `evidence_status_not_m7`: `true`
- `evidence_m7_false`: `true`
- `evidence_release_false`: `true`
- `hot_query_material`: `true`
- `cold_plus_query_wall_regresses`: `true`
- `runner_wall_regresses`: `true`
- `same_contract_signature_match`: `true`
- `call_for_review_exists`: `true`
- `external_blocked_exists`: `true`
- `gemini_stderr_records_auth_failure`: `true`
- `codex_blocking_review_exists`: `true`
- `codex_review_blocks_m7`: `true`

Failed checks: `[]`

## Goal-Level Decision Self-Audit

Decision: Gate the RTNN full-batch float32 hot-query result as review-blocked/not-M7.

1. Was I foolish? No. The hot-query signal is real, but wall regressions and missing external review block promotion.
2. If yes, what actions made the decision foolish? The foolish action would be to promote the 7.790x prepared-hot-query number while hiding the 0.393x cold-plus-query wall and 0.627x runner-wall regressions.
3. Was there another path? Rejecting RTNN entirely would avoid overclaim risk but would discard useful generic ranked_summary evidence.
4. Can I now try a different path? Keep the row blocked, then work on pack/prepare amortization or exact/tie-stable parity.
