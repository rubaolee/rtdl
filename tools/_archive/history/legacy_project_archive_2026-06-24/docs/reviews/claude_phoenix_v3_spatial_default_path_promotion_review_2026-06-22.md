# Claude Review: Phoenix V3 Spatial Default-Path Promotion

Reviewer: Claude (Sonnet 4.6 external AI review)

Date: 2026-06-22

Verdict: `accept_with_boundary`

## Bottom Line

The previous P1 default-path blocker is resolved. The default-path POD evidence is internally consistent, correctness-preserving, and sufficient for row-scoped M7 eligibility after Codex consensus.

No P0 or P1 blockers remain.

## Findings

### Default Path

Claude confirmed that `relation_status_corrected_default_enabled(...)` makes both controls default-enabled when unset or empty:

- `RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO`
- `RTDL_OPTIX_RELATION_STATUS_CORRECTED_EXACT_F64_SQUARED_BOUNDARY`

The POD command explicitly used `env -u` for both variables, so the measured optimized route is not a hidden env-gated route.

### Evidence Quality

Default-path POD evidence:

- repeat50/sample7/warmup5
- median prepared query: `1.0805986821651459 ms`
- every sample clears the `1.865660 ms` author Query timer bar
- row count is stable at `47,262`
- raw/boundary/dropped/emitted counts match the prior guarded-squared candidate
- median RT traversal time confirms the speedup is in the expected any-hit predicate site

Disable-control evidence:

- both controls set to `0`
- row count remains `47,262`
- raw candidates return to `[155,555]`
- dropped candidates return to `[108,293]`
- prepared query is much slower, confirming the default optimization is actually active

Claude accepted the disable-control evidence as a smoke/control, not as a precise public ratio.

### Equivalence And Cleanup

The guarded predicate has zero mismatches in the saved equivalence packet. The pure-squared mismatch risk remains documented and guarded. Claude also confirmed the old dead helper `exact_boundary_contact_f64` is gone and the source/test checks now enforce that.

## Boundary Conditions

1. Source provenance gap carries forward. The POD evidence has `git_commit: null` because the remote source is a non-git checkout. This is acceptable for M7 row eligibility because the packet records source SHA and built library SHA. It is not acceptable for a future public release artifact, which must come from a versioned git-tagged build.

2. Disable-control speedup is directional only. The `5.37x` figure comes from a single sample and must not be used in public-facing performance wording. It may be described only as evidence that the default optimization is active.

## Required Codex Follow-Up

If Codex accepts this review:

- update `external_review_status` to `claude_accept_with_boundary_default_path`
- run/save Codex second consensus
- then update `codex_consensus_status` to `claude_codex_consensus_accept_default_path_m7_row`
- set `m7_promotion_authorized: true`
- set `m7_qualified_release_rows_added: 1`
- add `point_location_topology_stream` as an M7 row in the V3 capability/release-surface gate

The following must remain false:

- `release_authorized`
- `public_speedup_claim_authorized`
- `rtdl_beats_rayjoin_claim_authorized`
- `paper_reproduction_claim_authorized`
- `true_zero_copy_claim_authorized`
- `v4_embedding_claim_authorized`

Claude additionally warned that the author Query timer is only a performance bar because the author run did not print result count. It must not be turned into broad `RTDL beats RayJoin` wording.
