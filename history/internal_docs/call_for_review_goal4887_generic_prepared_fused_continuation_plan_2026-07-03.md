# Call For Review: Goal4887 Generic Prepared Session + Fused Continuation Plan

Please review:

```text
history/internal_docs/goal4887_generic_prepared_fused_continuation_plan_2026-07-03.md
history/internal_docs/goal4886_authorpatch_vs_rtdl_performance_boundary_2026-07-03.md
history/internal_docs/goal4886_rayjoin_numba_partner_acceleration_report_2026-07-03.md
history/internal_docs/antigravity_goal4886_final_v2_review_2026-07-03.md
```

## Requested Verdict

Preferred labels:

- `approve_goal4887_generic_engine_plan_start_implementation`
- `approve_with_required_amendments`
- `block_as_rayjoin_specific_or_underdesigned`

## Review Context

We are not asking whether RTDL should optimize RayJoin with a private helper.
That is forbidden.

We are asking whether the next implementation goal correctly turns the RayJoin
performance lesson into generic RTDL engine work:

```text
prepared planar-map session
+ stable row buffers
+ formal Numba partner continuation
+ materialization-aware pipeline
```

The plan explicitly says:

- no new `rayjoin_*` public APIs;
- no private `rtdsl.rayjoin_overlay` route;
- no AuthorOfficial comparator logic in core;
- no claim that Numba accelerated LSI/PIP;
- no broad RayJoin speedup claim.

## Facts To Check

Current Australia representative evidence:

```text
RTDL+Numba v2 one-shot end-to-end: 103.786 s
RTDL+Numba v2 query+output:        20.920 s
RTDL+Numba v2 core compute:        18.880 s
AuthorPatch query+output:           0.844 s
AuthorPatch core compute:           0.0421 s
```

This means RTDL+Numba can win cold one-shot, but still loses the hot RayJoin
path by a large margin.

Goal4887 proposes to attack the true hot-path causes:

- repeated load/pack work;
- separated primitive boundaries;
- Python orchestration;
- row materialization;
- lack of formal partner continuation.

## Review Questions

1. Is Goal4887 truly generic engine work rather than RayJoin-specific work?
2. Are the forbidden actions complete enough to stop hidden RayJoin shortcuts?
3. Are `prepared session`, `row-buffer ABI`, `formal Numba continuation`, and
   `pipeline execution graph` the right architectural pieces?
4. Are the performance targets realistic:
   - cold one-shot `75-95 s`;
   - prepared hot query+output `3-8 s`;
   - stretch `<= 1.5 s`;
   - no promise to beat AuthorPatch core `0.0421 s`?
5. Are the acceptance criteria concrete enough to avoid V3/V4-style overclaim?
6. Should implementation start, or must the goal be amended first?

## Non-Authorization

This review does not authorize:

- implementation before approval;
- public release wording;
- broad RayJoin speedup claims;
- full hidden-input Section 5.7 claims;
- app-specific native kernels;
- private helper laundering;
- changing the comparator boundary;
- claiming hot-path parity with AuthorPatch.
