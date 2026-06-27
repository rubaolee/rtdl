# Claude Review: Phoenix V3 Final Public-Surface Wording Gate Upgrade

Reviewer: Claude Sonnet 4.6 via local Claude Code
Date: 2026-06-21
Call for review:
`docs/reviews/call_for_review_phoenix_v3_final_public_surface_wording_gate_upgrade_2026-06-21.md`

Verdict: `approve-with-amendments`

## Findings

### P0 Findings

None.

### P1 Findings

#### P1-1: `v3_current_status_2026-06-20.md` current blocker section is stale

The short-answer section correctly says eleven M7-qualified rows. A later
"Current Blocker" section still reads "Six exact rows are now row-scoped
M7-qualified" and lists only the original six, omitting the five supplemental
rows added since. This is not a gate failure because the scanned surface also
contains the current eleven-row state, but it is an inconsistent status note.

#### P1-2: `v3_release_authorization_blockers_2026-06-20.md` stale ten-row summary

The M7 classification summary paragraph records "Phoenix M7-qualified release
rows: 10" and omits
`rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`.
The P0 blocker row correctly says eleven, so the file is internally
inconsistent.

## Review Answers

1. The upgrade closes the old first-pass wording-scanner ambiguity as a final
   public-surface claim-boundary gate. The gate now reports
   `gate_level: final_public_surface_claim_boundary_gate`,
   `final_public_surface_gate: true`, and verifies all eleven expected row ids.
2. The release non-authorization boundary is preserved. `release_authorized:
   false` and `public_speedup_claim_authorized: false` remain hardcoded in the
   wording and release-readiness gates.
3. The regex checks are mostly well-calibrated. The `embedding` pattern is the
   broadest, but context-window allowance plus current zero violations make it
   acceptable for this surface.
4. The release-readiness gate correctly consumes the stronger wording gate
   through `wording_gate_final_public_surface`,
   `wording_gate_level_is_final_public_surface`, and
   `wording_gate_has_all_expected_m7_row_ids`.
5. No P0 fixes are required. Fix the two P1 stale row-count references before
   Codex consensus.

## Recommendation

The gate upgrade logic is correct and the non-authorization boundary is
structurally sound. Correct the stale documentation counts, then record Codex
consensus. No gate-code changes are required.

