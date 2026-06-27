# Phoenix V3 Current Status After Post-P1 Consensus

Date: 2026-06-21.

This is the current Phoenix V3 status. V4, C ABI, embedding, and external
zero-copy interop are out of scope.

## Current Verdict

```text
status: blocked_not_release
m7_qualified_release_rows: 12
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
twelve_row_release_readiness_consensus_blocks_release
```

V3 has real row-scoped M7 evidence, but it is still not a responsible major
release.

## Claude And 2-AI Review

Verified Claude CLI:

```text
C:\Users\Lestat\.local\bin\claude.exe
2.1.170 (Claude Code)
```

Saved review trail:

- Call packet:
  `docs/reviews/call_for_review_phoenix_v3_twelve_row_release_readiness_after_p1_fixes_compact_2026-06-21.md`
- Claude review:
  `docs/reviews/claude_phoenix_v3_twelve_row_release_readiness_after_p1_fixes_compact_review_2026-06-21.md`
- Codex 2-AI consensus:
  `docs/reviews/codex_phoenix_v3_twelve_row_release_readiness_after_p1_fixes_2ai_consensus_2026-06-21.md`

Claude verdict: `approve-blocked-not-release`.

Codex consensus status: `twelve_row_release_readiness_consensus_blocks_release`.

## What Changed In This Pass

- Repaired stale current docs from eleven-row to twelve-row status.
- Added/verified `source_tree_pod_gated_twelve_row` installer scope.
- Added/verified the `13.591x` Barnes-Hut overclaim scanner.
- Recorded the Barnes-Hut fused-partner row as generic Numba CUDA partner
  evidence, not RT-core evidence.
- Replaced the temporary blocker
  `twelve_row_release_readiness_consensus_missing` with
  `twelve_row_release_readiness_consensus_blocks_release`.
- Added the Spatial relation-status zero-prefilter experiment: the best legal
  RTDL public-county route improved from `5.406518 ms` to `1.903493 ms`
  (`2.840x`) with exact count `47,262`, but RayJoin author Query is still
  faster at `1.865660 ms`; therefore it remains a near-miss, not M7.
- Closed the Spatial count-only/no-diagnostics follow-up as no-go: it preserved
  exact count `47,262`, but was slower than the diagnostic prefilter-zero route
  (`1.903873 ms` versus `1.897592 ms`, delta `+0.006281 ms`), so the tested
  flag is not retained in source and adds no M7 row.
- Regenerated current release-readiness, aggregate alias, release-surface, and
  next-engine queue artifacts.

## Current Blockers

```text
release_authorization_false
twelve_row_surface_still_too_narrow_for_major_release
missing_point_location_topology_stream_m7_capability_family
twelve_row_release_readiness_consensus_blocks_release
```

The key technical gap is `point_location_topology_stream`: current coverage is
8 of 9 capability families, and this family has zero M7 rows.

Latest Spatial note:

```text
docs/rebuild/v3/phoenix_v3_spatial_relation_status_prefilter_zero_experiment_2026-06-21.md
status: spatial_relation_status_prefilter_zero_near_miss_not_m7
best RTDL prepared query: 1.903493 ms
RayJoin author Query bar: 1.865660 ms
remaining author gap: 0.037833 ms
M7 rows added: 0
```

Latest Spatial no-go follow-up:

```text
docs/rebuild/v3/phoenix_v3_spatial_relation_status_count_only_no_diagnostics_no_go_2026-06-21.md
status: spatial_relation_status_count_only_no_diagnostics_no_go_not_m7
count-only prepared query: 1.903873 ms
diagnostic prefilter-zero prepared query: 1.897592 ms
delta: +0.006281 ms
source retained: false
M7 rows added: 0
```

External AI review for this new near-miss is blocked, not complete:

```text
docs/reviews/call_for_review_phoenix_v3_spatial_prefilter_zero_near_miss_2026-06-21.md
docs/reviews/external_ai_blocked_phoenix_v3_spatial_prefilter_zero_near_miss_2026-06-21.md
status: external_ai_review_blocked_not_2ai_consensus
```

The active generic-engine queue is closed:

```text
generic_engine_work_queue_closed_not_release
existing_evidence_promotable_now: false
```

That means old evidence should not be mined for another promotion. A new M7 row
needs fresh evidence, correctness, phase/wall accounting, source provenance, and
2-AI review.

## Verification

Latest local verification:

```text
py -3 scripts\v3_release_wording_gate.py --pretty
status: pass

py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty
status: blocked_not_release
failed_checks: []

py -3 scripts\v3_phoenix_release_surface_breadth_gate.py --pretty
status: surface_breadth_blocked_not_release
failed_checks: []

py -3 scripts\v3_phoenix_next_engine_work_queue.py --pretty
status: generic_engine_work_queue_closed_not_release
failed_checks: []

py -3 -m unittest tests.v3_phoenix_spatial_active_p0_closure_gate_test tests.v3_phoenix_spatial_relation_status_prefilter_zero_experiment_test tests.v3_phoenix_next_engine_work_queue_test tests.v3_phoenix_release_readiness_gate_test tests.v3_release_wording_gate_test
24 tests OK

py -3 scripts\run_test_matrix.py --group v3_rebuild
96 modules / 463 tests OK
```

## Next Major Steps

1. Resolve `point_location_topology_stream`: either produce a reviewed M7 row
   for the family or make an explicit product-scope decision that V3 is a
   narrower row-scoped evidence release.
2. If pursuing the Spatial path, the current reopen bar is a fresh
   `br_county.cdb` POD packet with RTDL prepared-query median below
   `1.865660 ms` with stable margin, stable exact `47,262` count, full M3
   phase table, and same-packet author timing/count evidence, or a weaker scope
   accepted by external AI plus Codex consensus.
3. Get release-facing P1 reviews: app catalog, backend maturity, performance
   model, tutorial 07-15 coherence, and negative-row wording placement.
4. Do not publish broad V3-over-V2 speedup wording unless a later evidence
   packet and 2-AI review explicitly authorize it.

## Goal-Level Decision Self-Audit

Decision: record the post-P1 twelve-row consensus as the current V3
release-readiness authority.

1. Was I foolish? Not in the final decision. I corrected the earlier overbroad
   Claude prompt by using a compact review packet and then wrote a proper 2-AI
   consensus.
2. If yes, what actions made it foolish? The foolish part was starting with a
   Claude prompt that asked it to inspect too many files, causing a long run with
   no artifact. That was terminated and recorded.
3. Was there another path? Yes: give Claude a compact fact packet from the
   verified gates first.
4. Can I now try a different path? Yes. Keep V3 work focused on the remaining
   capability-family gap and release-facing review blockers, not V4 or broad
   performance claims.
