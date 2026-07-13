# Call For Review: Goal4888 Core Phase Decomposition Gate

Please review:

```text
history/internal_docs/goal4888_core_phase_decomposition_gate_2026-07-03.md
history/internal_docs/goal4887_generic_prepared_fused_continuation_plan_2026-07-03.md
history/internal_docs/claude_review_goal4887_fused_continuation_plan_2026-07-03.md
history/internal_docs/goal4886_pod_numba_au_skip_v2_summary.json
history/internal_docs/goal4886_authorpatch_vs_rtdl_performance_boundary_2026-07-03.md
```

## Requested Verdict

Preferred labels:

- `approve_goal4888_measurement_only_core_decomposition`
- `approve_with_required_amendments`
- `block_goal4888_as_still_underdesigned`

## Context

Goal4887 was blocked because it targeted `3-8 s` prepared hot query+output
without first proving that the current `18.880 s` RTDL core compute bucket is
removable by prepared/fused continuation.

Goal4888 is the correction:

```text
measure first -> classify bottleneck -> rewrite implementation goal
```

It does not authorize any engine implementation.

## Review Questions

1. Does Goal4888 correctly accept the Goal4887 block?
2. Is the scope truly measurement-only?
3. Does the required decomposition focus on the right unknown: whether
   `18.880 s` is native traversal, host materialization, Python orchestration,
   or mixed?
4. Is it correct to use existing Goal4886 summaries first before rerunning?
5. Are the decision gates sharp enough to prevent another V3-style
   implementation-before-source mistake?
6. Does the goal properly forbid RTDL core/native edits and RayJoin-specific
   shortcuts?
7. Should Goal4888 begin?

## Non-Authorization

This review does not authorize:

- Goal4887 implementation;
- prepared session implementation;
- row-buffer ABI implementation;
- Numba partner API implementation;
- native kernel changes;
- public performance claims;
- RayJoin-specific shortcuts.
