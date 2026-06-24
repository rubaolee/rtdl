# Call For Review: Phoenix V3 AABB Runner Route M2.1 POD A/B

Date: 2026-06-22
Status: `review_request_not_release_authorization`
Scope: Phoenix V3 only. V4, C ABI, embedding, SDK, and multi-language host work are out of scope.

## Why This Review Exists

Claude's core-gap review is recorded as:

```text
review: docs/reviews/claude_phoenix_v3_external_review_2026-06-22.md
verdict: approve_blocked_not_release
status_line: external_verdict_obtained_claude_approve_blocked_not_release
release_authorized: false
direction: continue with redirect to Gap 1
```

The highest-priority redirect was to stop treating cache hygiene as V3 progress
and make the productized execution path actually execute on Set-A probes.

This packet asks for a bounded external review of the first positive focused
post-redirect result: the AABB native query-handle route now goes through the
shared `prepared_execution_session_runner` and has same-pod evidence.

## Files To Inspect

- `src/rtdsl/prepared_execution.py`
- `src/rtdsl/__init__.py`
- `examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py`
- `scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py`
- `tests/v3_phoenix_aabb_prepare_reuse_pod_runner_test.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
- `tests/v3_phoenix_aabb_prepared_query_cache_test.py`
- `docs/reports/phoenix_v3_aabb_native_query_handle_runner_route_m2_2026-06-22.md`
- `docs/reports/phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md`
- `docs/rebuild/v3/evidence/phoenix_v3_aabb_runner_m2_1_pod_ab_20260622_180241/summary.json`
- `docs/rebuild/v3/phoenix_v3_next_dominant_engine_hotpath_selection_2026-06-22.json`
- `docs/rebuild/v3/phoenix_v3_next_dominant_engine_hotpath_selection_2026-06-22.md`

## Current Result

Evidence:

```text
local evidence dir: docs/rebuild/v3/evidence/phoenix_v3_aabb_runner_m2_1_pod_ab_20260622_180241
remote evidence dir: /root/rtdl_v3_rebuild_20260620/phoenix_v3_aabb_runner_m2_1_pod_ab_20260622_180241
hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.05, compute capability 8.9
fixture: jittered_grid
indexed_aabb_count: 32768
query_aabb_count: 32768
warmup: 3
repeat: 50
backends: embree,optix
```

Both Embree and OptiX payloads report:

```text
productized_execution_path: prepared_execution_session_runner
prepared_execution_session_runner_used: true
runtime_executed_count: 50
cache_hit_count: 49
matches_cpu_reference: true
complete_candidate_coverage: true
```

Main comparisons:

```text
OptiX / Embree prepare speedup: 0.700x
OptiX / Embree query median speedup: 1.921x
OptiX / Embree query total speedup: 1.738x
OptiX / Embree broadphase wall speedup: 1.348x
OptiX / Embree cold-plus-collect wall speedup: 1.346x
OptiX / Embree runner wall speedup: 1.337x
```

Interpretation proposed for review:

```text
status: m2_1_aabb_runner_route_pod_ab_pending_2ai_not_m7
productized_runner_visible_for_prepared_backends: true
material_optix_wall_win_after_prepare_reuse: true
m7_reopen_candidate_pending_2ai_review: true
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
full_all_app_rerun_authorized_by_this_packet: false
```

## Review Questions

Please use the bounded protocol in:

`docs/rebuild/v3/phoenix_v3_bounded_external_review_protocol_2026-06-22.md`

Return exactly one verdict label:

- `release_ready`
- `approve_blocked_not_release`
- `block_p0`
- `block_p1`

For this scoped packet, `release_ready` should only mean the AABB M2.1 evidence
is internally coherent enough to proceed to local M7-row consideration. It must
not mean Phoenix V3 release readiness.

Please answer:

1. Does the route actually prove a productized execution path, or is it still a
   route-specific cache dressed up as runtime work?
2. Are the timings measured on a fair basis for the proposed claim, including
   prepare cost and collect cost?
3. Is it acceptable that OptiX prepare is slower than Embree while repeated
   query, runner wall, and cold-plus-collect are materially faster?
4. Is the 32,768/32,768 warmup-3 repeat-50 same-pod fixture serious enough for
   a focused Set-A candidate, or should scale/repeat be strengthened?
5. Should this evidence reopen an AABB M7 candidate pending Codex consensus, or
   should it remain only diagnostic?
6. What exact wording boundary would be safe if the row is later accepted?
7. Does this evidence satisfy one of the "at least two Set-A probes" required
   before any future all-app pod run, or should it be excluded from that count?

## Explicit Non-Authorization

This packet does not authorize:

- Phoenix V3 release;
- public speedup wording;
- broad V3-over-V2 wording;
- true-zero-copy wording;
- automatic backend or partner selection wording;
- whole Contact Manifold solver speedup;
- broad AABB acceleration;
- another all-app paired pod run by itself;
- M7 promotion without external review intake plus Codex consensus.

## Goal-Level Decision Audit

Decision: request bounded external review of the M2.1 AABB runner-backed pod
A/B before any M7 reclassification.

1. Was I foolish?
   No for this decision.
2. If yes, what actions made the decision foolish?
   The foolish action would be to treat this positive focused row as V3 release
   proof, or to hide that OptiX prepare is slower while only quoting query
   speedup.
3. Was there another path?
   Yes. I could either skip review and promote the row, or ignore the positive
   pod result because V3 is still blocked. Both would lose important truth.
4. Can I now try a different path?
   Yes. Keep release blocked, send this focused evidence through bounded review,
   and require a second material Set-A probe before any all-app rerun planning.
