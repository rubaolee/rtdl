# Codex Consensus: Phoenix V3 Core Gaps Status And Next Work After Claude

Date: 2026-06-22
Consensus pair: Claude + Codex
Status: 2-AI consensus recorded; V3 remains blocked from release.

## Inputs

- `docs/reviews/claude_phoenix_v3_core_gaps_status_and_next_work_after_claude_review_2026-06-22.md`
- `docs/reviews/claude_phoenix_v3_core_gaps_status_and_next_work_after_claude_review_2026-06-22.raw.md`
- `docs/reviews/claude_phoenix_v3_external_review_2026-06-22.md`
- `docs/reviews/phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md`
- `docs/reviews/call_for_review_phoenix_v3_core_gaps_status_and_next_work_after_claude_2026-06-22.md`
- `docs/reports/phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md`
- `docs/rebuild/v3/evidence/phoenix_v3_aabb_runner_m2_1_pod_ab_20260622_180241/summary.json`

## Consensus Verdict

```text
verdict: approve_blocked_not_release
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_wording_authorized: false
all_app_rerun_authorized: false
```

Codex accepts Claude's verdict. Phoenix V3 engineering may continue, but the
current evidence does not authorize a release, broad V3-over-V2 wording, true
zero-copy wording, or all-app pod reruns.

## Accepted Findings

1. Gap 1 remains the parent blocker: V3 must show that the productized execution
   path executes real work and creates material wins, not just caches away V3
   overhead.
2. AABB M2.1 is valid Set-A productized-path evidence because it uses
   `prepared_execution_session_runner`, records `runtime_executed_count: 50`,
   records `cache_hit_count: 49`, preserves CPU reference correctness, and
   reports wall wins.
3. AABB M2.1 may proceed toward M7 review only with the full phase table and
   the slower OptiX prepare phase disclosed. It must not imply cold-start or
   prepare-phase speedup.
4. The Set-A / Set-B proposal is accepted as the working bar, but not frozen as
   the official bar. A row-by-row classification record must be committed before
   any formal all-app run.
5. The next engineering priority is RTDBSCAN / grouped-reduction /
   component-union continuation through the productized runner. Another
   app-specific route or another cache-only cleanup is not enough.
6. Misleading current-status labels must be cleaned up so scoped row evidence is
   not mistaken for release authorization.

## Required Next Actions

| Priority | Action |
| --- | --- |
| P1 | Produce a second material Set-A runner-backed focused pod result, with `runtime_executed: true` and at least `1.15x` wall speedup from the productized path. |
| P1 | Freeze Set-A / Set-B membership before any all-app paired pod run. |
| P2 | Rename current grouped-reduction row status text away from `m7_qualified_row_scoped_after_claude_codex_consensus` on user-facing/current packets. |
| P2 | Qualify the older aggregate `release_ready` field as scoped dossier evidence, not aggregate release authorization. |
| P2 | Keep AABB M2.1 claim wording tied to the full phase table, including OptiX prepare `0.700x` versus Embree. |

## Goal-Level Decision Audit

Decision: accept Claude's blocked-not-release verdict and redirect Phoenix V3
work toward a second Set-A productized-runner proof before any all-app run.

1. Was I foolish?
   Yes, earlier work let "many reviewed rows" and "green gates" look too close
   to release progress while the central runtime path was still under-proven.
2. What actions made that decision foolish?
   I let scoped evidence labels, aggregate row counts, and documentation gates
   stay prominent even when the serious same-hardware V3-vs-V2 result was only
   near parity and the productized path lacked breadth.
3. Was there another path that avoided being trapped in that idea?
   Yes. The better path is to treat unit tests and row packets only as
   spend-pod-time filters, then require focused runner-backed Set-A evidence
   before spending all-app pod time or using any public wording.
4. Can I now try a different path that truly solves the problem?
   Yes. The active path is to keep current release status blocked, fix
   misleading labels, freeze the scorecard basis, and implement/measure the
   second generic Set-A runner route through RTDBSCAN/component-union.

## Current Gate Reading

```text
phoenix_v3_gate: redo_required
current_work_allowed: focused_non_release_engineering
next_engineering_spine: rtdbscan_grouped_reduction_component_union_runner_route
```

