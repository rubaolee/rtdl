# Codex Consensus: Phoenix V3 Spatial Default-Path Promotion

Date: 2026-06-22

Status: `claude_codex_consensus_accept_default_path_m7_row`

External review: `docs/reviews/claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md`

Reviewed packet: `docs/rebuild/v3/phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.md`

## Consensus

Codex accepts Claude's `accept_with_boundary` verdict.

The Phoenix V3 Spatial guarded squared-boundary route is now eligible as one row-scoped M7 release-surface capability for `point_location_topology_stream`.

This consensus authorizes:

- `m7_promotion_authorized: true`
- `m7_qualified_release_rows_added: 1`
- release-surface gate update to count one `point_location_topology_stream` row

This consensus does not authorize:

- V3 release authorization
- public speedup claims
- broad V3-over-V2 claims
- whole-app speedup claims
- `RTDL beats RayJoin` wording
- paper reproduction wording
- true zero-copy claims
- V4/embedding claims

## Why

The prior P1 blocker was that the performance evidence only existed behind default-off env flags. That is now fixed in source by `relation_status_corrected_default_enabled(...)`, and the POD evidence was rerun with both controls explicitly unset.

The default-path POD packet records:

- repeat50/sample7/warmup5
- median prepared query: `1.0805986821651459 ms`
- exact count: `47,262`
- raw candidates: `[47,570]`
- boundary candidates: `[47,550]`
- dropped candidates: `[308]`
- all samples clear the `1.865660 ms` author Query timer bar
- all release/public/broad/V4/zero-copy flags remain false

The disable-control packet records both controls set to `0`, restoring the old larger candidate volume:

- raw candidates: `[155,555]`
- dropped candidates: `[108,293]`
- exact count: `47,262`

This confirms the default path is actually active. The disable-control timing is only a directional control and must not be published as a precision ratio.

## Boundaries To Carry Forward

1. The POD source copy is not a git checkout. `git_commit: null` remains acceptable for this M7 row because the packet records local source SHA and built library SHA, but public release artifacts must be built from a versioned git-tracked source.

2. The RayJoin author Query timer did not print result count. It remains an internal performance bar only, not a broad parity or `RTDL beats RayJoin` claim.

3. The guarded predicate is accepted because the equivalence packet records zero guarded mismatches and documents pure-squared mismatch risk. Do not remove the guard fallback.

## Goal-Level Decision Audit

Decision: promote the default-path Spatial guarded squared-boundary candidate to one internal M7 release-surface row, while keeping all public and broad claims disabled.

1. Was I foolish? No. This decision waits for source default-on behavior, POD default-path evidence, disable-control evidence, Claude external review, and Codex consensus before counting the row.
2. If yes, what actions made the decision foolish? The foolish action would be to use this as public `RTDL beats RayJoin` or broad V3-over-V2 wording. This consensus explicitly forbids that.
3. Was there another path? Yes: keep Spatial blocked pending a git-checkout POD run. That is stricter provenance, but it would unnecessarily block an internal M7 row when source SHA, build SHA, correctness, and review evidence are already recorded.
4. Can I now try a different path that actually solves the problem? Yes. Update the candidate packet and release-surface gates to count one bounded `point_location_topology_stream` row, then continue Phoenix V3 breadth work without broad claims.
