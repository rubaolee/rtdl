# Call For Review: Phoenix V3 Goal4392 Alignment

Reviewer: Claude or Gemini.

Status: external review request, 2026-06-20.

Please perform an independent read-only review distinct from Codex.

## Files To Audit

Primary files:

```text
docs/rebuild/v3/phoenix_v3_goal4392_alignment_audit_2026-06-20.md
docs/rebuild/v3/phoenix_v3_high_performance_candidate_matrix_2026-06-20.md
```

Governing formal plan:

```text
docs/reports/goal4392_v3_0_overall_plan_2026-06-15.md
docs/reports/goal4392_3ai_consensus_v3_0_overall_plan_2026-06-15.md
```

Evidence boundaries:

```text
docs/rebuild/v3/v3_claim_grade_all_benchmark_results_2026-06-20.md
docs/rebuild/v3/v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md
docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md
```

## Context

Phoenix is the V3 rebuild line. Its purpose is not to polish old release
language. It must rebuild V3 from evidence after the failed V3/V4 posture.

The formal Goal4392 plan says V3 exists to solve V2.x's real limitations:

- repeated materialization;
- missing device-resident continuations;
- missing fused graph execution;
- missing stream/lifetime accounting;
- missing generic continuation primitives.

Goal4392 also says V3 must not become more benchmark-specific tuning. The V3
answer must be a generic execution-graph layer with benchmark apps as evidence.

Current paired evidence says:

```text
V3 is stronger on runability and route health.
V3 is not proven broadly faster than V2.14.
Same-row geomean V3 speedup vs V2.14: 1.012x.
Broad V3-over-V2 speedup wording remains unauthorized.
```

Current all-app OptiX-vs-Embree evidence says:

```text
10 promoted benchmark apps covered.
40 rows / 40 ok / 0 failed.
Strong route-scoped OptiX rows exist.
Release authorization remains false.
```

## Codex's Current Proposed Alignment

Codex amended Phoenix so Goal4392 controls the work:

1. Build a current M1-M7 compliance table from M0-M149 artifacts before
   promoting route rows.
2. Treat benchmark rows as evidence for generic V3 capabilities, not as the
   architecture itself.
3. Require each P0 route to map to generic capabilities:
   - grouped reduction;
   - compact positives / component union;
   - ranked summary;
   - point-location / topology streams;
   - frontier / node summary / vector accumulation;
   - prepared graph chunking.
4. Keep M150-M214 C ABI / embedding / SDK / external-runtime / true zero-copy
   product claims out of V3.
5. Keep all public speedup and release wording blocked until M7-quality harness
   and fresh external review.

## Review Questions

1. Does the Phoenix alignment correctly restore Goal4392 as the control plane?
2. Does the revised candidate matrix still over-focus on benchmark-specific
   tuning?
3. Are any V4/post-M150 ideas leaking into V3?
4. Are the P0 priorities correct after mapping to generic V3 capabilities?
5. What concrete amendments are required before the next pod/code work?

## Required Output

Write a concise markdown review with:

- `VERDICT: ACCEPT`, `VERDICT: ACCEPT_WITH_REQUIRED_AMENDMENTS`, or
  `VERDICT: REJECT`.
- `P0 Findings`
- `P1 Findings`
- `Required Amendments`
- `Final Consensus Statement`

Please be critical. Do not approve if Phoenix still reads like a benchmark
patch queue rather than the Goal4392 execution-graph language release.
