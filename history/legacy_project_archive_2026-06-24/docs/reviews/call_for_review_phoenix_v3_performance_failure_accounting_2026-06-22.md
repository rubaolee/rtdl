# Call For Review: Phoenix V3 Performance Failure And Optimization Accounting

Date: 2026-06-22
Requester: Codex
Requested reviewer: Claude or equivalent external AI
Protocol intent: bounded technical review; no release authorization.

## Packet Under Review

Primary document:

```text
docs/reports/phoenix_v3_performance_failure_optimization_accounting_2026-06-22.md
```

Supporting documents:

```text
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/summary.json
docs/reports/phoenix_v3_optimization_effectiveness_and_remaining_plan_2026-06-22.md
docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_2_pod_ab_2026-06-22.md
docs/reviews/claude_phoenix_v3_external_review_2026-06-22.md
docs/reviews/phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md
docs/reviews/call_for_review_phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md
```

## Context

Phoenix V3 is currently not release-ready. The controlling same-RT-hardware
V2.14 vs Phoenix V3 all-app comparison reports:

```text
same_metric_comparison_count: 52
v3_geomean_speedup_vs_v2: 1.0117790403434224
v3_faster_count_gt_5pct: 12
v3_slower_count_gt_5pct: 5
similar_count_within_5pct: 35
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

The user requested a technical accounting document that states:

1. V3 currently has no release-level performance.
2. What optimizations were done.
3. Which did not produce performance.
4. Why they were originally expected to help.
5. Why they did not actually help enough.
6. What remaining optimizations should be implemented.
7. Why those remaining optimizations can still be expected to help.

## Questions For Reviewer

Please answer critically and directly.

1. Does the accounting document honestly state that Phoenix V3 currently lacks
   release-level performance?
2. Does it correctly distinguish regression repair, row-scoped wins, hot-query
   wins, runner parity recovery, and true productized-path performance?
3. Does it overclaim any current evidence?
4. Does it miss any major optimization already done in Phoenix V3 that should
   be included?
5. Are the proposed remaining optimizations genuinely language/runtime work,
   or do any smell like benchmark-app development?
6. Are the proposed remaining optimizations technically plausible paths to
   material V3 performance, or are they likely to asymptote to parity?
7. What changes should be made before this document is used as the handoff
   technical accounting for the next Phoenix V3 work?

## Required Verdict

Use one of:

```text
approve_accounting
approve_with_required_edits
reject_overclaims
reject_incomplete
```

This review cannot authorize a Phoenix V3 release, public speedup wording, or
broad V3-over-V2 claims.

## Explicit Non-Authorization

Regardless of verdict, this packet does not authorize:

- Phoenix V3 release;
- public performance claims;
- broad V3 faster than V2.x claims;
- true zero-copy claims;
- automatic backend/partner selection;
- V4, C ABI, embedding, SDK, or external host interop work.
